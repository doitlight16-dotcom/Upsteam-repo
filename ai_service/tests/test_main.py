import pytest
from fastapi.testclient import TestClient
from app.main import app, get_tenant_id
from app.db import vector_store

client = TestClient(app)

def test_missing_tenant_id_returns_401():
    app.dependency_overrides.clear()
    response = client.post("/api/v1/ai/ask", json={"prompt": "Where is KMG stand?"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Corporate identity (tenant_id) missing or unverified."

def test_vector_store_tenant_isolation():
    results = vector_store.query_tenant_context(
        prompt="Where is KMG pavilion?",
        tenant_id="KMG"
    )
    assert len(results) > 0
    assert "Hall 4, Stand #4150" in results[0]

def test_authenticated_tenant_request():
    # Inject mock tenant identity via FastAPI dependency overrides
    app.dependency_overrides[get_tenant_id] = lambda: "KMG"

    response = client.post("/api/v1/ai/ask", json={"prompt": "Where is KMG pavilion?"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["tenant_id"] == "KMG"
    assert "Hall 4, Stand #4150" in data["context_retrieved"]
    assert "STRICT OPERATIONAL DIRECTIVES" in data["system_prompt_prepared"]

    # Clean up overrides after test completion
    app.dependency_overrides.clear()