# Week 5 — Tools, MCP & Interoperability

[![CI](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week05-mcp-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week05-mcp-tools/actions/workflows/ci.yml)

> **Standalone lab** from the *Agentic AI on Azure — Enterprise Master Class* (12 weeks).
> Each lab is an independent, runnable FastAPI starter. Part of the
> [course series](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure).

---

## 🎯 Learning goal
Connect agents to tools via REST APIs, OpenAPI, Functions, Logic Apps, and a custom MCP server.

## 🏢 Enterprise use case — "Procurement Operations Agent" (Manufacturing / Retail)
The agent checks inventory (REST), creates a purchase order (Logic App), gets supplier pricing (OpenAPI tool), and logs to the ERP — all via standardized tool contracts so tools are reusable across agents.

---

## 🧪 What you'll build (lab)
1. Register an **OpenAPI** tool and an **Azure Function** tool.
2. Build a **custom MCP server** exposing internal APIs as MCP tools.
3. Front the MCP server / tools with FastAPI + **API Management** as the secure gateway.
4. Add idempotency keys for write tools (PO creation).

> This starter ships with a **runnable mock** of the endpoint so you can run and test
> immediately, then progressively replace the mock with the real Azure implementation.

## 🏗️ Architect's lens
- MCP as the *interoperability contract* — decouple tools from agents so they're portable.
- Tool governance: who can call what, schemas as the trust boundary, idempotency for write tools.
- Gateway pattern: rate limits, auth, and observability centralized at APIM.

## 🧰 Tech stack
MCP (Model Context Protocol) server, OpenAPI, Azure Functions, Azure Logic Apps, Azure API Management, FastAPI, Pydantic tool schemas.

---

## 🚀 Quick start

```bash
# 1. Create & activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) copy the env template — runs in MOCK mode without it
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux

# 4. Run the API
uvicorn app.main:app --reload
```

Open the interactive docs at **http://127.0.0.1:8000/docs**.

### Try the endpoint
```bash
curl -X POST http://127.0.0.1:8000/api/v1/procure \
  -H "Content-Type: application/json" \
  -d '{"request": "Order 500 units of part SKU-9981 from our preferred supplier."}'
```

### Run the tests
```bash
pytest -q
```

### Run with Docker
```bash
docker build -t agentic-ai-azure-week05-mcp-tools .
docker run -p 8000:8000 agentic-ai-azure-week05-mcp-tools
```

---

## 📁 Project structure
```
agentic-ai-azure-week05-mcp-tools/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI app + the /api/v1/procure endpoint
├── tests/
│   └── test_smoke.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

---

## 🗺️ Where this fits
This repo covers **Week 5 — Tools, MCP & Interoperability**. The full 12-week path and reference architecture
live in the master-class companion repo:
**[azure-agentic-ai-masterclass](https://github.com/satyajeetaiml-hue/azure-agentic-ai-masterclass)**.

## 📄 License
MIT — see [`LICENSE`](LICENSE).
