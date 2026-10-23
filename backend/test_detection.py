from datetime import timedelta

from fastapi.testclient import TestClient

from .app import app
from .detection import detect
from .models import SecurityEvent
from .sample_data import deterministic_events


def complete_events() -> list[SecurityEvent]:
    events = deterministic_events()
    events.append(
        events[-1].model_copy(
            update={
                "event_id": "evt-005",
                "timestamp": events[-1].timestamp + timedelta(minutes=1),
                "event_type": "credential_dump",
                "destination": "-",
            }
        )
    )
    return events


def test_interrupted_sequence_predicts_ranked_next_actions_and_graph_separates_prediction() -> None:
    result = detect("scenario-office-macro", deterministic_events())
    withheld_future_stage = complete_events()[-1].event_type
    assert result.complete is False
    assert result.missing_expected_stages == ["credential_dump"]
    assert result.predictions[0].predicted_action == withheld_future_stage
    assert result.predictions[0].supporting_event_ids == ["evt-001", "evt-002", "evt-003", "evt-004"]
    assert any(node.node_type == "predicted_action" for node in result.graph_nodes)
    assert not any(node.node_type == "observed_event" and node.predicted_action for node in result.graph_nodes)


def test_complete_sequence_has_no_missing_stage_or_prediction() -> None:
    result = detect("scenario-office-macro", complete_events())
    assert result.complete is True
    assert result.missing_expected_stages == []
    assert result.predictions == []


def test_duplicate_out_of_order_and_delayed_events_are_metadata_not_new_activity() -> None:
    events = deterministic_events()
    duplicate = events[1].model_copy()
    result = detect("scenario-office-macro", [events[0], events[2], duplicate, events[1], events[3]])
    assert result.duplicate_event_ids == ["evt-002"]
    assert result.out_of_order is True
    assert result.delayed_event_ids == ["evt-001", "evt-002", "evt-003", "evt-004"]
    assert [node.event_id for node in result.graph_nodes if node.node_type == "observed_event"] == ["evt-001", "evt-002", "evt-003", "evt-004"]


def test_insufficient_evidence_does_not_claim_an_absent_action() -> None:
    result = detect("scenario-office-macro", deterministic_events()[:1])
    assert result.insufficient_evidence is True
    assert result.predictions == []
    assert "network_connection" in result.missing_expected_stages


def test_missing_optional_fields_are_accepted() -> None:
    event = deterministic_events()[0].model_copy(update={"process": None, "destination": None})
    result = detect("scenario-office-macro", [event, deterministic_events()[1]])
    assert result.observed_stages == ["process_start", "network_connection"]


def test_api_detection_scenarios_predictions_and_invalid_input() -> None:
    client = TestClient(app)
    assert client.get("/api/scenarios").status_code == 200
    assert client.get("/api/scenarios/scenario-office-macro/demo-events").status_code == 200
    response = client.post(
        "/api/detection",
        json={"scenario_id": "scenario-office-macro", "events": [event.model_dump(mode="json") for event in deterministic_events()]},
    )
    assert response.status_code == 200
    assert response.json()["predictions"][0]["predicted_action"] == "credential_dump"
    assert client.get("/api/predictions/next-action").status_code == 200
    assert client.get("/api/graph/scenario-office-macro").status_code == 200
    invalid = client.post("/api/detection", json={"scenario_id": "", "events": []})
    assert invalid.status_code == 422


def test_detection_is_repeatable_and_unknown_scenario_is_rejected() -> None:
    first = detect("scenario-office-macro", deterministic_events()).model_dump()
    second = detect("scenario-office-macro", deterministic_events()).model_dump()
    assert first == second
    client = TestClient(app)
    assert client.get("/api/predictions/unknown").status_code == 404