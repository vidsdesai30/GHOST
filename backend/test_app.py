from fastapi.testclient import TestClient

from .app import app

client = TestClient(app)


def test_health_and_status() -> None:
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/status").json()["database"] == "sqlite"


def test_deterministic_events_are_available() -> None:
    response = client.get("/api/events")
    assert response.status_code == 200
    assert [event["event_id"] for event in response.json()] == ["evt-001", "evt-002", "evt-003", "evt-004"]


def test_duplicate_event_is_idempotent() -> None:
    event = client.get("/api/events").json()[0]
    response = client.post("/api/events", json=event)
    assert response.status_code == 201
    assert response.json() == {"accepted": True, "duplicate": True}
