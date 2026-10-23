# GHOST Project Memory

## Current status

GHOST is a frontend-only React/Vite/TypeScript research demonstration named TRACE LAB. It runs two deterministic synthetic attack-sequence fixtures entirely in the browser. The repository no longer requires FastAPI, Python, SQLite, localhost API calls, or external inference.

## Decisions

- Keep all fixtures synthetic and documentation-safe.
- Preserve separate observed, inferred, and predicted categories.
- Treat confidence as a transparent heuristic, not a probability.
- Use deterministic normalization and ranking so replay is repeatable.
- Keep investigations in frontend session state and state that they are not persisted.
- Keep production controls out of scope and disclose that frontend code cannot provide server security.

## Important locations

- `frontend/src/api.ts`: typed contracts, two synthetic scenario fixtures, normalization, detection, ranking, and graph construction.
- `frontend/src/Dashboard.tsx`: shared scenario state and seven functional views.
- `frontend/src/styles.css`: TRACE LAB visual system and responsive/accessibility rules.
- `Architecture.md`: frontend architecture and evidence boundary.
- `SecurityChecklist.md`: current safeguards and deployment gaps.

## Commands

From `frontend/`:

```powershell
npm install
npm run dev
npm run build
```

Open the Vite URL shown in the terminal, normally `http://localhost:5173`.

## Validation record

- `npm run build` passed after the frontend-only conversion.
- The build runs `tsc -b` followed by `vite build`.
- No automated frontend or browser test suite exists.
- Browser validation remains to be performed after the redesign.

## Remaining work

- Add automated component/browser tests.
- Capture the seven requested documentation screenshots from the running frontend.
- Expand the synthetic corpus and create reproducible evaluation fixtures.
- Improve temporal and graph-based reasoning and uncertainty calibration.
- Add production controls only in a separately designed service.
