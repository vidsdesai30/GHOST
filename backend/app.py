import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .detection import RULES, available_scenarios, detect
from .models import DetectionRequest, DetectionResult, Prediction, Scenario, SecurityEvent
from .sample_data import deterministic_events
from .store import EventStore

logging.basicConfig(level=os.getenv("GHOST_LOG_LEVEL", "INFO"))
logger = logging.getLogger("ghost")
store = EventStore(os.getenv("GHOST_DATABASE_PATH", "ghost.db"))
configured_origins = os.getenv("GHOST_FRONTEND_ORIGINS") or os.getenv("GHOST_FRONTEND_ORIGIN") or "http://localhost:5173,http://127.0.0.1:5173"
frontend_origins = [
    origin.strip()
    for origin in configured_origins.split(",")
    if origin.strip()
]


def seed_demo_events() -> None:
    for event in deterministic_events():
        store.upsert(event)


seed_demo_events()


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_demo_events()
    yield


app = FastAPI(
    title="GHOST - Almost-Completed Attack Detector",
    version="0.1.0",
    description="Synthetic research prototype for incomplete attack-sequence analysis.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def request_size_limit(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 1_000_000:
        raise HTTPException(status_code=413, detail="request too large")
    return await call_next(request)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ghost-api"}


@app.get("/api/status")
def status() -> dict[str, int | str]:
    return {"status": "research_prototype", "stored_events": store.count(), "database": "sqlite"}


@app.get("/api/events", response_model=list[SecurityEvent])
def events(scenario_id: str | None = None) -> list[SecurityEvent]:
    return store.list(scenario_id)


@app.get("/api/scenarios", response_model=list[Scenario])
def scenarios() -> list[Scenario]:
    return available_scenarios()


@app.get("/api/scenarios/{scenario_id}/demo-events", response_model=list[SecurityEvent])
def demo_events(scenario_id: str) -> list[SecurityEvent]:
    if scenario_id not in RULES:
        raise HTTPException(status_code=404, detail="scenario not found")
    return [event for event in deterministic_events() if event.scenario_id == scenario_id]


@app.post("/api/events", response_model=dict[str, bool], status_code=201)
def ingest_event(event: SecurityEvent) -> dict[str, bool]:
    inserted = store.upsert(event)
    return {"accepted": True, "duplicate": not inserted}


@app.post("/api/detection", response_model=DetectionResult)
def run_detection(request: DetectionRequest) -> DetectionResult:
    if request.scenario_id not in RULES:
        raise HTTPException(status_code=404, detail="scenario not found")
    return detect(request.scenario_id, request.events)


def _demo_detection(scenario_id: str) -> DetectionResult:
    if scenario_id not in RULES:
        raise HTTPException(status_code=404, detail="scenario not found")
    return detect(scenario_id, demo_events(scenario_id))


@app.get("/api/predictions/next-action", response_model=list[Prediction])
def prediction_compatibility_route() -> list[Prediction]:
    return predictions("scenario-office-macro")


@app.get("/api/predictions/{scenario_id}", response_model=list[Prediction])
def predictions(scenario_id: str) -> list[Prediction]:
    return _demo_detection(scenario_id).predictions


@app.get("/api/graph/{scenario_id}", response_model=DetectionResult)
def graph(scenario_id: str) -> DetectionResult:
    return _demo_detection(scenario_id)
