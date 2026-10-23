# GHOST Architecture

## Status

Prompt 4 final validation. This document describes the runnable research prototype, not a production security service.

## Components and flow

The React/Vite frontend presents a graph-first investigation workspace with live API state, overview, graph, timeline, predictions, investigations, scenarios/tests, and security/audit views. The FastAPI backend validates normalized events with Pydantic, persists event IDs and metadata in SQLite, serves deterministic synthetic fixtures, and runs a pure sequence detector that produces predictions and evidence graphs.

`fixture or POST /api/events -> Pydantic validation -> idempotent SQLite insert -> detection rules -> predictions/evidence graph -> API`

## Data model

`SecurityEvent` contains `event_id`, `timestamp`, `event_type`, `host`, `process`, `user_account`, `source`, `destination`, arbitrary structured `attributes`, `scenario_id`, and `ingestion` metadata (`received_at`, source batch, optional sequence number, duplicate/delayed flags). Scenario, investigation, prediction, and evidence Pydantic models establish contracts for subsequent prompts. SQLite currently stores normalized event rows and JSON for structured fields.

Duplicate events are rejected by the event ID primary key and reported as idempotent duplicates. The detector also deduplicates request batches before matching. Timestamp and ingestion time are separate: arrival after event time is marked delayed, and arrival order that conflicts with event timestamps is marked out of order. Matching uses event timestamps and deterministic event-ID tie breaks.

## Detection and prediction boundary

The current rule `scenario-office-macro` expects `process_start -> network_connection -> script_execution -> credential_access_attempt -> credential_dump`. It reports observed and missing stages, but missing telemetry is not treated as proof that an action did not occur. Fewer than two observed stages yields `insufficient_evidence` and no prediction. Deterministic weights rank `credential_dump` at `0.90` and `persistence_setup` at `0.38`; confidence is a transparent heuristic, not a calibrated probability.

Observed event nodes are created only from supplied events. Inferred ordered-sequence edges reference supporting event IDs. Predicted actions use separate `predicted_action` nodes and `supports_prediction` edges; they are never serialized as observed activity.

## API contracts

- `GET /api/health`: liveness response.
- `GET /api/status`: prototype status, SQLite backend, stored event count.
- `GET /api/events?scenario_id=...`: normalized synthetic events.
- `GET /api/scenarios`: available synthetic scenario definitions.
- `GET /api/scenarios/{scenario_id}/demo-events`: deterministic demo events.
- `POST /api/events`: validates and idempotently stores one event; returns `accepted` and `duplicate`.
- `POST /api/detection`: validates an event batch and returns detection, predictions, and graph data.
- `GET /api/predictions/{scenario_id}`: returns ranked demo predictions.
- `GET /api/graph/{scenario_id}`: returns the demo detection graph response.
- `GET /api/predictions/next-action`: compatibility route for the office-macro demo.

The frontend uses typed contracts in `frontend/src/api.ts`. Scenario loading calls demo-events and graph endpoints together; the Scenarios view calls `POST /api/detection` explicitly. Loading, empty, error, and success states are represented in the dashboard. Backend failures are shown as unavailable; the UI does not fabricate successful results.

The frontend defaults to `http://localhost:8000`. FastAPI defaults to allowing both `http://localhost:5173` and `http://127.0.0.1:5173` through `GHOST_FRONTEND_ORIGINS`, because both are common local Vite URLs. The verified backend command is `py -m uvicorn backend.app:app --host 127.0.0.1 --port 8000` from the repository root.

## Trust boundaries and security decisions

The browser-to-local-API boundary is CORS-limited to the configured local frontend origin. No authentication is present because this is a single-user local prototype; that is a documented gap, not an implemented control. Inputs use typed validation, request bodies are capped at 1 MB, dynamic command execution is absent, CORS does not allow arbitrary origins, and error responses avoid diagnostic internals. Only synthetic data belongs in this project. SQLite files and `.env` files are ignored.

## Limitations and future production architecture

There is no authentication, authorization, tenant isolation, retention policy, durable migration system, rate limiting, event signature verification, encryption at rest, structured audit log, or production observability. A production architecture would place an authenticated ingestion gateway in front of a durable event bus, schema registry, tenant-aware storage, immutable evidence store, detection workers, model registry, human review workflow, and centralized monitoring. Prediction would require offline evaluation, confidence calibration, adversarial testing, and explicit analyst approval.

Final validation used the live browser at `http://127.0.0.1:5173`: overview data loaded from the API; graph node selection exposed prediction boundaries and supporting IDs; timeline showed event and ingestion order; predictions showed confidence, stages, missing stages, and alternatives; investigations showed linked evidence; Scenarios & Tests ran detection; Security & Audit disclosed missing controls. Browser automation is not part of the repository test suite.
