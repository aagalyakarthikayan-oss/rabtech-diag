"""Load and analyze diagnostic event logs (e.g. samples/diagnostic-events.json)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Union

REQUIRED_FIELDS = ("timestamp", "service", "level", "status_code")


class MalformedEventDataError(ValueError):
    """Raised when the event log's top-level structure is invalid (bad JSON or schema)."""


def load_events_file(path: Union[str, Path]) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Event file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise MalformedEventDataError(f"Invalid JSON in {path}: {exc}") from exc
    return validate_structure(data)


def validate_structure(data: Any) -> dict:
    if not isinstance(data, dict):
        raise MalformedEventDataError("Top-level JSON must be an object.")
    events = data.get("events")
    if not isinstance(events, list):
        raise MalformedEventDataError("'events' key must be a list.")
    return data


def analyze_events(data: dict) -> Dict[str, Any]:
    events: List[dict] = data.get("events", [])

    by_level: Dict[str, int] = {}
    by_service: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    latencies: List[float] = []
    malformed_entries: List[Dict[str, Any]] = []

    for idx, event in enumerate(events):
        missing = [f for f in REQUIRED_FIELDS if f not in event]
        if missing:
            malformed_entries.append(
                {"index": idx, "reason": f"missing fields: {missing}", "event": event}
            )
            continue

        level = event.get("level", "UNKNOWN")
        service = event.get("service", "unknown")
        status = str(event.get("status_code", "unknown"))
        by_level[level] = by_level.get(level, 0) + 1
        by_service[service] = by_service.get(service, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1

        latency = event.get("latency_ms")
        if isinstance(latency, (int, float)):
            latencies.append(latency)
        else:
            malformed_entries.append(
                {"index": idx, "reason": "latency_ms missing or null", "event": event}
            )

    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None

    return {
        "generated_for": data.get("generated_for"),
        "total_events": len(events),
        "by_level": by_level,
        "by_service": by_service,
        "by_status_code": by_status,
        "avg_latency_ms": avg_latency,
        "max_latency_ms": max(latencies) if latencies else None,
        "malformed_entry_count": len(malformed_entries),
        "malformed_entries": malformed_entries,
        "error_count": by_level.get("ERROR", 0),
        "warn_count": by_level.get("WARN", 0),
    }
