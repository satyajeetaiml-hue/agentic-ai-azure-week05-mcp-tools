"""Week 5 — Tools, MCP & Interoperability: Procurement Operations Agent.

Demonstrates tool contracts and interoperability: a small **tool registry**
(inventory check, supplier pricing, PO creation) with JSON-schema definitions, an
**idempotency** guard on the write tool, and an MCP-style **tool discovery** endpoint.

Two backends: ``MockProcurementBackend`` (offline, tested) and
``FoundryProcurementBackend`` (azure-ai-projects v2 Responses API with the tools
registered as function tools, lazy-imported).
"""

from __future__ import annotations

import json
import re
import uuid
from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ── settings ────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    foundry_project_endpoint: str = ""
    foundry_model_name: str = "gpt-4o"

    @property
    def use_foundry(self) -> bool:
        return bool(self.foundry_project_endpoint)


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ── schemas ─────────────────────────────────────────────────────────────
class ProcureRequest(BaseModel):
    request: str = Field(..., min_length=1, description="Procurement request in natural language.")
    idempotency_key: str | None = Field(default=None, description="Dedupe key for PO creation.")


class ProcureResponse(BaseModel):
    order_id: str | None
    status: str
    sku: str | None
    quantity: int | None
    unit_price: float | None
    total: float | None
    steps: list[str]
    mode: str


# ── tools (with JSON schemas for MCP / function-calling) ────────────────
_INVENTORY = {"SKU-9981": 1200, "SKU-1001": 0, "SKU-5500": 350}
_PRICING = {"SKU-9981": 4.25, "SKU-1001": 19.99, "SKU-5500": 8.10}
_PO_STORE: dict[str, dict] = {}  # idempotency_key -> order


def check_inventory(sku: str) -> dict[str, Any]:
    qty = _INVENTORY.get(sku.upper())
    return {"sku": sku, "known": qty is not None, "in_stock": (qty or 0) > 0, "available": qty or 0}


def get_supplier_pricing(sku: str) -> dict[str, Any]:
    price = _PRICING.get(sku.upper())
    return {"sku": sku, "unit_price": price, "currency": "USD", "found": price is not None}


def create_purchase_order(sku: str, quantity: int, idempotency_key: str | None = None) -> dict[str, Any]:
    if idempotency_key and idempotency_key in _PO_STORE:
        return {**_PO_STORE[idempotency_key], "idempotent_replay": True}
    order = {"order_id": f"PO-{uuid.uuid4().hex[:8].upper()}", "sku": sku, "quantity": quantity, "status": "created"}
    if idempotency_key:
        _PO_STORE[idempotency_key] = order
    return {**order, "idempotent_replay": False}


TOOL_REGISTRY: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "check_inventory",
        "description": "Check current inventory level for a SKU.",
        "parameters": {
            "type": "object",
            "properties": {"sku": {"type": "string"}},
            "required": ["sku"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_supplier_pricing",
        "description": "Get the supplier unit price for a SKU.",
        "parameters": {
            "type": "object",
            "properties": {"sku": {"type": "string"}},
            "required": ["sku"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "create_purchase_order",
        "description": "Create a purchase order for a SKU and quantity (idempotent).",
        "parameters": {
            "type": "object",
            "properties": {
                "sku": {"type": "string"},
                "quantity": {"type": "integer"},
                "idempotency_key": {"type": "string"},
            },
            "required": ["sku", "quantity"],
            "additionalProperties": False,
        },
    },
]
_TOOL_FUNCS = {
    "check_inventory": check_inventory,
    "get_supplier_pricing": get_supplier_pricing,
    "create_purchase_order": create_purchase_order,
}

_SKU_RE = re.compile(r"\bSKU-\d{3,6}\b", re.IGNORECASE)
_QTY_RE = re.compile(r"\b(\d{1,6})\b")

SYSTEM_INSTRUCTIONS = (
    "You are a procurement operations agent. Given a request, determine the SKU and quantity, "
    "check inventory, get supplier pricing, and create a purchase order using the tools. "
    "Always check inventory and pricing before creating a PO."
)


# ── backends ────────────────────────────────────────────────────────────
class MockProcurementBackend:
    mode = "mock"

    def procure(self, req: ProcureRequest) -> ProcureResponse:
        steps: list[str] = []
        sku_m = _SKU_RE.search(req.request)
        sku = sku_m.group(0).upper() if sku_m else None
        qty_m = _QTY_RE.search(req.request)
        qty = int(qty_m.group(1)) if qty_m else None
        steps.append(f"Parsed sku={sku}, quantity={qty}.")

        if not sku or not qty:
            return ProcureResponse(
                order_id=None, status="needs_clarification", sku=sku, quantity=qty,
                unit_price=None, total=None, mode=self.mode,
                steps=steps + ["Could not determine SKU and/or quantity."],
            )

        inv = check_inventory(sku)
        steps.append(f"check_inventory -> available={inv['available']}.")
        pricing = get_supplier_pricing(sku)
        steps.append(f"get_supplier_pricing -> unit_price={pricing['unit_price']}.")

        if not pricing["found"]:
            return ProcureResponse(
                order_id=None, status="rejected", sku=sku, quantity=qty,
                unit_price=None, total=None, mode=self.mode,
                steps=steps + ["No supplier price; cannot order."],
            )

        order = create_purchase_order(sku, qty, req.idempotency_key)
        steps.append(f"create_purchase_order -> {order['order_id']} (replay={order['idempotent_replay']}).")
        total = round(pricing["unit_price"] * qty, 2)
        return ProcureResponse(
            order_id=order["order_id"], status=order["status"], sku=sku, quantity=qty,
            unit_price=pricing["unit_price"], total=total, steps=steps, mode=self.mode,
        )


class FoundryProcurementBackend:
    mode = "foundry"

    def procure(self, req: ProcureRequest) -> ProcureResponse:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential

        steps: list[str] = []
        s = get_settings()
        with (
            DefaultAzureCredential() as cred,
            AIProjectClient(endpoint=s.foundry_project_endpoint, credential=cred) as proj,
        ):
            client = proj.get_openai_client()
            response = client.responses.create(
                model=s.foundry_model_name,
                input=[
                    {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                    {"role": "user", "content": req.request},
                ],
                tools=TOOL_REGISTRY,
            )
            for _ in range(6):
                calls = [it for it in response.output if getattr(it, "type", None) == "function_call"]
                if not calls:
                    break
                outputs = []
                for call in calls:
                    args = json.loads(call.arguments or "{}")
                    if call.name == "create_purchase_order" and req.idempotency_key:
                        args.setdefault("idempotency_key", req.idempotency_key)
                    result = _TOOL_FUNCS[call.name](**args)
                    steps.append(f"Model called {call.name} -> {result}.")
                    outputs.append(
                        {"type": "function_call_output", "call_id": call.call_id, "output": json.dumps(result)}
                    )
                response = client.responses.create(
                    model=s.foundry_model_name, previous_response_id=response.id,
                    input=outputs, tools=TOOL_REGISTRY,
                )

        # Re-derive a structured summary from the mock store / tools deterministically.
        mock = MockProcurementBackend().procure(req)
        mock.steps = steps + ["Finalized via deterministic re-validation."]
        mock.mode = self.mode
        return mock


def get_backend():
    return FoundryProcurementBackend() if get_settings().use_foundry else MockProcurementBackend()
