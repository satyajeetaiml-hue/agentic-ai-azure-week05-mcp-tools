"""Smoke tests for Week 5 — Tools, MCP & Interoperability."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_endpoint_accepts_input():
    r = client.post("/api/v1/procure", json={"request": "Order 500 units of part SKU-9981 from our preferred supplier."})
    assert r.status_code == 200


def test_endpoint_rejects_empty():
    r = client.post("/api/v1/procure", json={"request": ""})
    assert r.status_code == 422
