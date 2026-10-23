from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class IngestionMetadata(BaseModel):
    received_at: datetime
    source_batch: str = Field(min_length=1, max_length=100)
    sequence_number: int | None = Field(default=None, ge=0)
    is_duplicate: bool = False
    is_delayed: bool = False


class SecurityEvent(BaseModel):
    event_id: str = Field(min_length=1, max_length=120)
    timestamp: datetime
    event_type: str = Field(min_length=1, max_length=100)
    host: str = Field(min_length=1, max_length=255)
    process: str | None = Field(default=None, max_length=255)
    user_account: str | None = Field(default=None, max_length=255)
    source: str | None = Field(default=None, max_length=255)
    destination: str | None = Field(default=None, max_length=255)
    attributes: dict[str, Any] = Field(default_factory=dict)
    scenario_id: str = Field(min_length=1, max_length=100)
    ingestion: IngestionMetadata

    @field_validator("event_id", "scenario_id", "host", "process", "user_account", "source", "destination")
    @classmethod
    def reject_control_characters(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if any(ord(character) < 32 for character in value):
            raise ValueError("control characters are not allowed")
        return value


class Scenario(BaseModel):
    scenario_id: str
    name: str
    description: str
    status: str
    event_count: int


class Investigation(BaseModel):
    investigation_id: str
    scenario_id: str
    state: str
    created_at: datetime
    analyst_note: str | None = None


class Prediction(BaseModel):
    scenario_id: str
    predicted_action: str
    confidence: float = Field(ge=0, le=1)
    supporting_event_ids: list[str]
    observed_stages: list[str]
    missing_expected_stages: list[str]
    alternative_explanations: list[str]
    reasoning: str


class GraphNode(BaseModel):
    node_id: str
    node_type: str
    label: str
    event_id: str | None = None
    predicted_action: str | None = None


class GraphEdge(BaseModel):
    edge_id: str
    source: str
    target: str
    relation: str
    inferred: bool = True
    supporting_event_ids: list[str] = Field(default_factory=list)


class DetectionRequest(BaseModel):
    scenario_id: str = Field(min_length=1, max_length=100)
    events: list[SecurityEvent] = Field(min_length=1, max_length=500)


class DetectionResult(BaseModel):
    scenario_id: str
    complete: bool
    insufficient_evidence: bool
    duplicate_event_ids: list[str]
    delayed_event_ids: list[str]
    out_of_order: bool
    observed_stages: list[str]
    missing_expected_stages: list[str]
    predictions: list[Prediction]
    graph_nodes: list[GraphNode]
    graph_edges: list[GraphEdge]


class Evidence(BaseModel):
    evidence_id: str
    event_id: str
    relation: str
    confidence: float = Field(ge=0, le=1)
