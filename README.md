# Week 5 — Tools, MCP & Interoperability

[![CI](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week05-mcp-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week05-mcp-tools/actions/workflows/ci.yml)

> ▶️ **Run in VS Code — no Azure needed.** `pip install -r requirements.txt`, then `uvicorn app.main:app --reload` and open http://127.0.0.1:8000/docs. Runs in **mock mode** by default — no `az login`, keys, or `.env` required. Wiring real Azure (below) is optional.

> **Standalone lab** from the *Agentic AI on Azure — Enterprise Master Class*.
> Course hub: [azure-agentic-ai-masterclass](https://github.com/satyajeetaiml-hue/azure-agentic-ai-masterclass).

---

## 🎯 Learning goal
Connect an agent to tools via standardized contracts (REST/OpenAPI/Functions/MCP) so tools are reusable.

## 🏢 Enterprise use case — "Procurement Operations Agent" (Manufacturing / Retail)
The agent checks **inventory**, gets **supplier pricing**, and creates a **purchase order** — each a tool
with a JSON-schema contract, with **idempotency** on the write tool.

## ✅ What this repo implements
- A **tool registry** (`check_inventory`, `get_supplier_pricing`, `create_purchase_order`) with
  JSON-schema definitions — the contract shared by MCP and OpenAI function-calling.
- **MCP-style discovery** at `GET /api/v1/tools`.
- **Idempotency** guard so retrying a PO with the same `idempotency_key` returns the same order.
- **Mock backend** (offline, tested) and **Foundry backend** (Responses API tool-calling loop).

## 🚀 Quick start
```bash
python -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
```bash
curl http://127.0.0.1:8000/api/v1/tools
curl -X POST http://127.0.0.1:8000/api/v1/procure \
  -H "Content-Type: application/json" \
  -d '{"request": "Order 500 units of SKU-9981", "idempotency_key": "po-001"}'
```
Run tests: `pytest -q`. Known SKUs: `SKU-9981`, `SKU-1001`, `SKU-5500`.

## ☁️ Foundry mode
`az login`, then set `FOUNDRY_PROJECT_ENDPOINT` + `FOUNDRY_MODEL_NAME`. The model calls the registry
tools during the run; the result is re-validated deterministically.

## 🏗️ Architect's lens
- **MCP as the interoperability contract** — decouple tools from agents so they're portable.
- Tool governance: schemas as the trust boundary, **idempotency** for write tools.
- Gateway pattern: centralize auth/rate-limits/observability at **API Management**.

## 🧰 Tech stack
MCP, OpenAPI, Azure Functions, Logic Apps, API Management, FastAPI, azure-ai-projects v2.

## 📁 Structure
```
app/service.py   # settings, schemas, tool registry + funcs, backends
app/main.py      # POST /api/v1/procure, GET /api/v1/tools
tests/test_app.py
```

## 🗺️ Series
Prev: [Weeks 3-4](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week03-04-agent-framework) ·
Next: [Weeks 6-7 — Multi-agent](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week06-07-multi-agent) ·
[All labs](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure)

## 📄 License
MIT — see [`LICENSE`](LICENSE).

## 📊 Teaching slides

Download the **7-slide deck** for classroom use: [`agentic-ai-azure-week05-mcp-tools.pptx`](slides/agentic-ai-azure-week05-mcp-tools.pptx)

> Slides: Title · Learning goal · Enterprise use case · Architecture/flow · Key concepts · Run it · Architect's takeaways.

