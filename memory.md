# GHOST Project Memory

## Current status

Prompt 4 final validation is complete. The project is a runnable local research prototype using React/Vite/TypeScript, FastAPI/Pydantic, SQLite, and pytest.

## Decisions

- Synthetic deterministic events only; no credentials or live telemetry.
- Event identity is the SQLite primary key, making ingestion idempotent for duplicates.
- Event time and ingestion time are separate to support delayed and out-of-order events.
- Prediction is an explicit placeholder until evidence-backed detection is implemented.
- UI uses a fixed sidebar, graphite palette, restrained green accents, and a graph-first workspace.

## Important locations

- `backend/models.py`: normalized event plus scenario/investigation/prediction/evidence contracts.
- `backend/app.py`: FastAPI app, health/status/events routes, size limit and CORS.
- `backend/sample_data.py`: deterministic synthetic fixture sequence.
- `backend/store.py`: SQLite initialization, idempotent event persistence, and normalized event retrieval.
- `backend/detection.py`: deterministic scenario rules, normalization, prediction ranking, and evidence graph generation.
- `backend/test_app.py`: focused backend checks.
- `backend/test_detection.py`: detection, prediction, graph, and API coverage.
- `frontend/src/api.ts`: shared TypeScript API contracts and sanitized request helper.
- `frontend/src/Dashboard.tsx`: functional graph-first dashboard views and shared scenario state.
- `frontend/src/App.tsx`: dashboard entrypoint.
- `SecurityChecklist.md`, `Architecture.md`: security and architecture records.

## Commands

- Backend: `cd backend; python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1; pip install -r requirements.txt; cd ..; python -m uvicorn backend.app:app --reload --port 8000`
- Frontend: `cd frontend; npm install; npm run dev`
- Tests: `py -m pytest backend/test_app.py backend/test_detection.py -q`
- Build: `cd frontend; npm run build`

## Final validation checks

- Frontend: `npm install` and `npm run build` passed; Vite produced `frontend/dist` successfully.
- Editor diagnostics: no errors reported for backend or frontend.
- Backend: `py -m pytest backend/test_app.py backend/test_detection.py -q` passed: 10 passed, 33 deprecation warnings.
- Final regression: `py -m pytest -q` passed: 10 passed, 33 deprecation warnings; `py -m compileall backend -q` passed.
- Frontend final regression: `cd frontend; npm run build` passed; Vite emitted production assets successfully.
- Backend final regression: `py -m pytest -q` passed: 10 passed, 33 deprecation warnings.
- Live API: health 200; one scenario; four events; two predictions; six graph nodes; five graph edges.
- CORS diagnosis/fix: browser at `127.0.0.1:5173` initially received 400 preflight responses because only `localhost:5173` was allowed. FastAPI now allows both local origins by default; preflight and browser loading were verified.
- Live browser validation: overview, graph/node selection, timeline, predictions, investigations, scenarios/tests, and security/audit views rendered successfully. No automated frontend test suite exists.

## Research evaluation

- Prediction opportunities supported by withheld synthetic future stages: 1.
- Correct top prediction: 1 (`credential_dump`).
- Incorrect top predictions: 0 observed in the supported evaluation.
- Abstentions: 2 test conditions (complete sequence and insufficient evidence).
- Conditional top-1 accuracy: 100% (1/1 predicted opportunity).
- Coverage across the three evaluated conditions: 33.3% (1/3).
- This is not a meaningful benchmark: there is one scenario, one withheld future stage, deterministic rules, and no noisy production distribution.
- Python 3.14 note: Pydantic 2.10.4 attempted a source build without `link.exe`; `backend/requirements.txt` now pins Pydantic 2.12.5, which installed from a compatible wheel.

## Known issues

- No authentication, authorization, tenant isolation, durable migrations, rate limiting, encryption, or production deployment hardening.
- Frontend does not fabricate fixture success when the API is unavailable; it shows an explicit unavailable/error state.
- SQLite event row storage is foundation-level; graph output is computed in memory and not persisted.
- The Security & Audit view is a client-side presentation of documented controls and local signals, not an audit-log endpoint.

## Final state and unresolved issues

1. Investigations and detection results are not persisted; investigation view is client-side inspection of the current prediction.
2. Security & Audit is a documented posture view, not a server-side audit event stream.
3. Add automated browser tests and more synthetic scenarios if the prototype continues.
4. Revisit authentication, authorization, rate limiting, and tenant isolation only if the prototype moves beyond local synthetic use.
