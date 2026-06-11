"""Hermetic tests for the Week 5 procurement agent (mock backend)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_mock():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["backend"] == "mock"


def test_tool_discovery():
    r = client.get("/api/v1/tools")
    assert r.status_code == 200
    names = {t["name"] for t in r.json()["tools"]}
    assert {"check_inventory", "get_supplier_pricing", "create_purchase_order"} <= names


def test_procure_creates_order():
    r = client.post("/api/v1/procure", json={"request": "Order 500 units of SKU-9981"})
    assert r.status_code == 200
    body = r.json()
    assert body["sku"] == "SKU-9981"
    assert body["quantity"] == 500
    assert body["unit_price"] == 4.25
    assert body["total"] == 2125.0
    assert body["status"] == "created"
    assert body["order_id"].startswith("PO-")


def test_idempotency_returns_same_order():
    payload = {"request": "Order 10 units of SKU-5500", "idempotency_key": "abc-123"}
    first = client.post("/api/v1/procure", json=payload).json()
    second = client.post("/api/v1/procure", json=payload).json()
    assert first["order_id"] == second["order_id"]


def test_missing_sku_needs_clarification():
    r = client.post("/api/v1/procure", json={"request": "Please order some widgets"})
    assert r.status_code == 200
    assert r.json()["status"] == "needs_clarification"


def test_validation_rejects_empty():
    r = client.post("/api/v1/procure", json={"request": ""})
    assert r.status_code == 422
