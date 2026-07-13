from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.ingest import router


app = FastAPI()

app.include_router(router)

client = TestClient(app)


def test_ingest():

    response = client.post(
        "/ingest",
        files={
            "file": (
                "sample.pdf",
                b"Hello",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "queued"


def test_status():

    response = client.get(
        "/documents/123"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "queued"