from fastapi.testclient import TestClient

from backend.main import app


def test_root_api():

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "NeuroFlow API running"


def test_query_endpoint_exists():

    with TestClient(app) as client:
        response = client.post(
            "/query",
            json={
                "question": "What is NeuroFlow?"
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "sources" in data