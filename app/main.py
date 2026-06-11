"""Week 5 — Tools, MCP & Interoperability — starter FastAPI service.

Use case: Procurement Operations Agent (Manufacturing / Retail).
See README.md for the full lab brief. Run:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Week 5 — Tools, MCP & Interoperability", version="0.1.0")


class LabRequest(BaseModel):
    request: str = Field(..., min_length=1, description="A procurement request in natural language.")


@app.get("/health")
def health():
    return {"status": "ok", "week": "5", "use_case": "Procurement Operations Agent"}


@app.get("/")
def root():
    return {
        "service": "agentic-ai-azure-week05-mcp-tools",
        "week": "5",
        "endpoint": "/api/v1/procure",
        "docs": "/docs",
    }


@app.post("/api/v1/procure")
def handler(payload: LabRequest):
    """Mock handler for the Procurement Operations Agent.

    TODO (lab): replace this stub with the real implementation described in
    README.md (the Azure services for this week are listed in the Tech Stack).
    """
    return {
        "week": "5",
        "use_case": "Procurement Operations Agent",
        "received": payload.request,
        "status": "accepted",
        "note": "Mock response — implement the real agent per README.md.",
    }
