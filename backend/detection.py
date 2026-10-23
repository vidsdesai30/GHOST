from dataclasses import dataclass

from .models import (
    DetectionResult,
    GraphEdge,
    GraphNode,
    Prediction,
    Scenario,
    SecurityEvent,
)


@dataclass(frozen=True)
class ScenarioRule:
    scenario_id: str
    name: str
    description: str
    stages: tuple[str, ...]
    action_weights: tuple[tuple[str, float], ...]


RULES = {
    "scenario-office-macro": ScenarioRule(
        scenario_id="scenario-office-macro",
        name="Office macro to credential access",
        description="Synthetic chain from document execution through a credential access attempt.",
        stages=(
            "process_start",
            "network_connection",
            "script_execution",
            "credential_access_attempt",
            "credential_dump",
        ),
        action_weights=(
            ("credential_dump", 0.90),
            ("persistence_setup", 0.38),
        ),
    )
}


def available_scenarios() -> list[Scenario]:
    return [
        Scenario(
            scenario_id=rule.scenario_id,
            name=rule.name,
            description=rule.description,
            status="synthetic_demo",
            event_count=4,
        )
        for rule in RULES.values()
    ]


def _normalize(events: list[SecurityEvent]) -> tuple[list[SecurityEvent], list[str], list[str], bool]:
    unique: dict[str, SecurityEvent] = {}
    duplicate_ids: list[str] = []
    delayed_ids: list[str] = []
    previous_received = None
    previous_timestamp = None
    out_of_order = False
    for event in events:
        if event.event_id in unique:
            duplicate_ids.append(event.event_id)
            continue
        unique[event.event_id] = event
        received = event.ingestion.received_at
        if previous_received and received < previous_received:
            out_of_order = True
        if previous_timestamp and event.timestamp < previous_timestamp:
            out_of_order = True
        if received > event.timestamp:
            delayed_ids.append(event.event_id)
        previous_received = received
        previous_timestamp = event.timestamp
    ordered = sorted(unique.values(), key=lambda event: (event.timestamp, event.event_id))
    return ordered, sorted(set(duplicate_ids)), sorted(set(delayed_ids)), out_of_order


def _prediction(rule: ScenarioRule, observed: list[str], event_ids: list[str]) -> list[Prediction]:
    missing = [stage for stage in rule.stages if stage not in observed]
    if len(observed) < 2 or not missing:
        return []
    next_stage = next((stage for stage in rule.stages if stage not in observed), None)
    if next_stage is None:
        return []
    observed_count = len(observed)
    predictions: list[Prediction] = []
    for action, weight in rule.action_weights:
        confidence = min(0.99, round(weight * (0.55 + (observed_count / len(rule.stages)) * 0.45), 3))
        predictions.append(
            Prediction(
                scenario_id=rule.scenario_id,
                predicted_action=action,
                confidence=confidence,
                supporting_event_ids=event_ids,
                observed_stages=observed,
                missing_expected_stages=missing,
                alternative_explanations=[
                    "The sequence may be benign administrative activity with similar telemetry.",
                    "A missing event may have occurred outside the synthetic sensor coverage.",
                ],
                reasoning=f"Observed {observed_count} of {len(rule.stages)} ordered stages; the next unmatched stage is {next_stage}.",
            )
        )
    return sorted(predictions, key=lambda prediction: (-prediction.confidence, prediction.predicted_action))


def detect(scenario_id: str, events: list[SecurityEvent]) -> DetectionResult:
    rule = RULES.get(scenario_id)
    if rule is None:
        raise ValueError("unknown scenario")
    normalized, duplicate_ids, delayed_ids, out_of_order = _normalize(events)
    stage_to_event: dict[str, SecurityEvent] = {}
    for event in normalized:
        if event.scenario_id != scenario_id:
            continue
        if event.event_type in rule.stages and event.event_type not in stage_to_event:
            stage_to_event[event.event_type] = event
    observed = [stage for stage in rule.stages if stage in stage_to_event]
    missing = [stage for stage in rule.stages if stage not in stage_to_event]
    event_ids = [stage_to_event[stage].event_id for stage in observed]

    nodes = [
        GraphNode(node_id=f"event:{event.event_id}", node_type="observed_event", label=event.event_type, event_id=event.event_id)
        for event in normalized
        if event.scenario_id == scenario_id
    ]
    edges = [
        GraphEdge(
            edge_id=f"edge:{left.event_id}:{right.event_id}",
            source=f"event:{left.event_id}",
            target=f"event:{right.event_id}",
            relation="ordered_sequence",
            supporting_event_ids=[left.event_id, right.event_id],
        )
        for left, right in zip([stage_to_event[stage] for stage in observed], [stage_to_event[stage] for stage in observed][1:])
    ]
    predictions = _prediction(rule, observed, event_ids)
    for prediction in predictions:
        node_id = f"prediction:{prediction.predicted_action}"
        nodes.append(GraphNode(node_id=node_id, node_type="predicted_action", label=prediction.predicted_action, predicted_action=prediction.predicted_action))
        if event_ids:
            edges.append(GraphEdge(edge_id=f"edge:{event_ids[-1]}:{node_id}", source=f"event:{event_ids[-1]}", target=node_id, relation="supports_prediction", supporting_event_ids=event_ids))
    return DetectionResult(
        scenario_id=scenario_id,
        complete=not missing,
        insufficient_evidence=len(observed) < 2,
        duplicate_event_ids=duplicate_ids,
        delayed_event_ids=delayed_ids,
        out_of_order=out_of_order,
        observed_stages=observed,
        missing_expected_stages=missing,
        predictions=predictions,
        graph_nodes=nodes,
        graph_edges=edges,
    )