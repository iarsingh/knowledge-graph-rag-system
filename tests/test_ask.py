from fastapi.testclient import TestClient
from kgrag.main import app

client = TestClient(app)


def test_answers_and_refuses():
    hit = client.post("/ask", json={"question": 'Which GKE cluster runs in europe-west1?'}).json()
    assert hit["answered"] is True
    assert hit["citation"] == "gke.md"
    miss = client.post("/ask", json={"question": 'football scores'}).json()
    assert miss["answered"] is False


def test_empty_is_refused():
    assert client.post("/ask", json={"question": " "}).status_code == 422
