# GHOST Architecture

## Status

GHOST is a frontend-only, local research demonstration. The browser runs deterministic synthetic fixtures and detection logic without FastAPI, Python, SQLite, network requests, or hosted inference.

## Components and state flow

```text
scenario fixtures -> localResearch.events()
                  -> deterministic normalization
                  -> stage comparison and ranking
                  -> DetectionResult
                  -> shared React state
                  -> graph / timeline / predictions / investigation views
```

The React/Vite/TypeScript application keeps the active scenario, event list, latest detection result, selected graph node, selected prediction, and timeline filter in `Dashboard.tsx`. Scenario changes reset the relevant state and recompute the same result from the selected fixture.

## Frontend modules

- `frontend/src/api.ts` contains the typed event, scenario, graph, prediction, and detection contracts; deterministic fixtures; and the `localResearch` engine.
- `frontend/src/Dashboard.tsx` renders the seven investigation views and shared controls.
- `frontend/src/styles.css` provides the TRACE LAB visual system, graph treatments, responsive layout, focus states, and reduced-motion behavior.
- `frontend/src/App.tsx` exposes the dashboard entry point.

## Synthetic fixtures

Two deterministic scenarios are included:

- `scenario-office-macro`: `process_start -> network_connection -> script_execution -> credential_access_attempt -> credential_dump`, with four supplied events and a missing final stage.
- `scenario-build-runner`: `process_start -> script_execution -> network_connection -> persistence_setup`, with three supplied events and a missing final stage.

Fixtures use documentation-safe values such as synthetic hostnames, reserved IP ranges, and synthetic process metadata. They do not collect credentials, execute attacks, or ingest real telemetry.

## Detection and evidence boundary

The engine:

1. Deduplicates event IDs for matching and records duplicate IDs.
2. Detects timestamp order conflicts and delayed arrivals by comparing event and ingestion times.
3. Orders unique events by event timestamp and event ID.
4. Matches known event types against the selected scenario stages.
5. Abstains when fewer than two stages are observed or when the sequence is complete.
6. Ranks missing next-action candidates with transparent deterministic weights.
7. Builds observed-event nodes, inferred ordered-sequence edges, predicted-action nodes, and evidence-linked prediction edges.

Observed nodes represent supplied fixture events. Inferred edges represent relationships derived from their order. Predicted nodes represent possible next actions only; missing telemetry is not proof that the action occurred. Confidence is a heuristic score, not a calibrated probability.

## Visualization components

- **Overview:** active fixture metrics, sequence status, graph preview, top hypothesis, and timeline.
- **Attack Graph:** selectable observed and predicted nodes, inferred directional edges, legend, and node inspector.
- **Event Timeline:** event time versus ingestion time with all/delayed filters.
- **Predictions:** ranked hypotheses, heuristic confidence, reasoning, supporting IDs, stages, and alternatives.
- **Investigations:** session-only evidence inspection for the selected hypothesis.
- **Scenarios & Tests:** deterministic replay and reset controls.
- **Security & Audit:** explicit frontend security posture and missing production controls.

No view claims server-side persistence. Browser state is the only investigation state.

## Design and trust boundaries

The interface uses a near-black charcoal palette, green observed evidence, cyan inferred relationships, amber predicted hypotheses, technical labels, and responsive accessible controls. The visual language is explanatory rather than an assertion of live monitoring.

Because the application is frontend-only, it provides no authentication, authorization, tenant isolation, secure ingestion boundary, audit log, encrypted storage, or production telemetry protection. It must remain a synthetic-data demonstration unless a separately designed service supplies those controls.
