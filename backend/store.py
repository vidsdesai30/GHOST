import sqlite3
import json
from datetime import datetime

from .models import SecurityEvent


class EventStore:
    def __init__(self, database_path: str = "ghost.db") -> None:
        self.database_path = database_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    host TEXT NOT NULL,
                    process TEXT NOT NULL,
                    user_account TEXT NOT NULL,
                    source TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    attributes_json TEXT NOT NULL,
                    scenario_id TEXT NOT NULL,
                    ingestion_json TEXT NOT NULL
                )
                """
            )

    def upsert(self, event: SecurityEvent) -> bool:
        payload = event.model_dump_json()
        ingestion = event.ingestion.model_copy(update={"is_duplicate": False})
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT 1 FROM security_events WHERE event_id = ?", (event.event_id,)
            ).fetchone()
            if existing:
                return False
            connection.execute(
                """INSERT INTO security_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.event_id,
                    event.timestamp.isoformat(),
                    event.event_type,
                    event.host,
                    event.process,
                    event.user_account,
                    event.source,
                    event.destination,
                    event.model_dump_json(include={"attributes"}),
                    event.scenario_id,
                    ingestion.model_dump_json(),
                ),
            )
        return True

    def count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM security_events").fetchone()[0])

    def list(self, scenario_id: str | None = None) -> list[SecurityEvent]:
        query = "SELECT * FROM security_events"
        parameters: tuple[str, ...] = ()
        if scenario_id:
            query += " WHERE scenario_id = ?"
            parameters = (scenario_id,)
        query += " ORDER BY timestamp, event_id"
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [
            SecurityEvent(
                event_id=row["event_id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                event_type=row["event_type"],
                host=row["host"],
                process=row["process"],
                user_account=row["user_account"],
                source=row["source"],
                destination=row["destination"],
                attributes=json.loads(row["attributes_json"]).get("attributes", {}),
                scenario_id=row["scenario_id"],
                ingestion=json.loads(row["ingestion_json"]),
            )
            for row in rows
        ]
