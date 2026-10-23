# GHOST

GHOST (The Almost-Completed Attack Detector) is a local research prototype for identifying incomplete attack sequences from synthetic security events. It is not production-hardened and must not be connected to live sensitive telemetry.

## Run locally

Backend (Python 3.14 verified; Python 3.11+ intended):

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
cd ..
py -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Frontend (Node.js 20+):

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. API health: `http://localhost:8000/api/health`.

Checks:

```powershell
py -m pytest -q
cd ..\frontend
npm run build
```
