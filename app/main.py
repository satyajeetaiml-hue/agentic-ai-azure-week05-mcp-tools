"""Week 5 — Tools, MCP & Interoperability.

Procurement Operations Agent with a tool registry, idempotency, and MCP-style
tool discovery. Runs in MOCK mode out of the box. Run:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.service import (
    TOOL_REGISTRY,
    ProcureRequest,
    ProcureResponse,
    get_backend,
    get_settings,
)

settings = get_settings()
app = FastAPI(title="Week 5 — MCP & Tools (Procurement)", version="0.2.0")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "week": "5", "backend": "foundry" if settings.use_foundry else "mock"}


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "service": "agentic-ai-azure-week05-mcp-tools",
        "endpoint": "/api/v1/procure",
        "backend": "foundry" if settings.use_foundry else "mock",
        "docs": "/docs",
    }


@app.get("/api/v1/tools", tags=["week05"])
def list_tools() -> dict[str, list]:
    """MCP-style tool discovery: advertise the callable tool contracts."""
    return {"tools": [{"name": t["name"], "description": t["description"]} for t in TOOL_REGISTRY]}


@app.post("/api/v1/procure", response_model=ProcureResponse, tags=["week05"])
def procure(payload: ProcureRequest) -> ProcureResponse:
    return get_backend().procure(payload)
