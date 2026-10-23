from datetime import datetime, timezone

from .models import SecurityEvent


RECEIVED_AT = datetime(2026, 1, 15, 12, 5, tzinfo=timezone.utc)


def deterministic_events() -> list[SecurityEvent]:
    return [
        SecurityEvent(
            event_id="evt-001",
            timestamp=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
            event_type="process_start",
            host="workstation-07",
            process="winword.exe",
            user_account="lab\\analyst",
            source="workstation-07",
            destination="-",
            attributes={"parent_process": "explorer.exe", "integrity": "medium"},
            scenario_id="scenario-office-macro",
            ingestion={"received_at": RECEIVED_AT, "source_batch": "fixture-a", "sequence_number": 1},
        ),
        SecurityEvent(
            event_id="evt-002",
            timestamp=datetime(2026, 1, 15, 12, 1, tzinfo=timezone.utc),
            event_type="network_connection",
            host="workstation-07",
            process="winword.exe",
            user_account="lab\\analyst",
            source="workstation-07",
            destination="198.51.100.24:443",
            attributes={"protocol": "https", "bytes_out": 1842},
            scenario_id="scenario-office-macro",
            ingestion={"received_at": RECEIVED_AT, "source_batch": "fixture-a", "sequence_number": 2},
        ),
        SecurityEvent(
            event_id="evt-003",
            timestamp=datetime(2026, 1, 15, 12, 3, tzinfo=timezone.utc),
            event_type="script_execution",
            host="workstation-07",
            process="powershell.exe",
            user_account="lab\\analyst",
            source="workstation-07",
            destination="-",
            attributes={"engine": "powershell", "command_summary": "encoded payload (synthetic)"},
            scenario_id="scenario-office-macro",
            ingestion={"received_at": RECEIVED_AT, "source_batch": "fixture-a", "sequence_number": 3},
        ),
        SecurityEvent(
            event_id="evt-004",
            timestamp=datetime(2026, 1, 15, 12, 4, tzinfo=timezone.utc),
            event_type="credential_access_attempt",
            host="workstation-07",
            process="powershell.exe",
            user_account="lab\\analyst",
            source="workstation-07",
            destination="lsass.exe",
            attributes={"result": "blocked", "sensor": "synthetic-edr"},
            scenario_id="scenario-office-macro",
            ingestion={"received_at": RECEIVED_AT, "source_batch": "fixture-a", "sequence_number": 4},
        ),
    ]
