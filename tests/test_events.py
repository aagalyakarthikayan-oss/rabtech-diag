import json

import pytest

from rabtech_diag import events

SAMPLE = {
    "generated_for": "RabTech Python Software Engineering internship",
    "events": [
        {"timestamp": "2026-08-01T09:00:00Z", "service": "billing-api", "level": "INFO", "latency_ms": 148, "status_code": 200},
        {"timestamp": "2026-08-01T09:01:00Z", "service": "billing-api", "level": "WARN", "latency_ms": 920, "status_code": 200},
        {"timestamp": "2026-08-01T09:02:00Z", "service": "profile-api", "level": "ERROR", "latency_ms": 1210, "status_code": 503},
        {"timestamp": "2026-08-01T09:03:00Z", "service": "profile-api", "level": "INFO", "latency_ms": 205, "status_code": 200},
        {"timestamp": "2026-08-01T09:04:00Z", "service": "billing-api", "level": "ERROR", "latency_ms": None, "status_code": 500},
    ],
}


def test_analyze_events_success():
    result = events.analyze_events(SAMPLE)
    assert result["total_events"] == 5
    assert result["error_count"] == 2
    assert result["warn_count"] == 1
    assert result["malformed_entry_count"] == 1
    assert result["by_service"]["billing-api"] == 3
    assert result["avg_latency_ms"] == pytest.approx((148 + 920 + 1210 + 205) / 4, rel=1e-3)


def test_load_events_file_success(tmp_path):
    path = tmp_path / "events.json"
    path.write_text(json.dumps(SAMPLE), encoding="utf-8")
    data = events.load_events_file(path)
    assert data["generated_for"] == SAMPLE["generated_for"]


def test_load_events_file_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        events.load_events_file(tmp_path / "missing.json")


def test_load_events_file_malformed_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(events.MalformedEventDataError):
        events.load_events_file(path)


def test_load_events_file_malformed_structure(tmp_path):
    path = tmp_path / "bad_structure.json"
    path.write_text(json.dumps({"generated_for": "x", "events": "oops-not-a-list"}), encoding="utf-8")
    with pytest.raises(events.MalformedEventDataError):
        events.load_events_file(path)
