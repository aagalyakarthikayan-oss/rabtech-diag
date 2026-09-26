import json

from rabtech_diag import cli

SAMPLE = {
    "generated_for": "RabTech Python Software Engineering internship",
    "events": [
        {"timestamp": "2026-08-01T09:00:00Z", "service": "billing-api", "level": "INFO", "latency_ms": 148, "status_code": 200},
        {"timestamp": "2026-08-01T09:04:00Z", "service": "billing-api", "level": "ERROR", "latency_ms": None, "status_code": 500},
    ],
}


def test_cli_success_json(tmp_path, capsys):
    events_path = tmp_path / "events.json"
    events_path.write_text(json.dumps(SAMPLE), encoding="utf-8")

    exit_code = cli.run(["--events-file", str(events_path), "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == cli.EXIT_OK
    assert payload["events_analysis"]["total_events"] == 2
    assert payload["system_info"]["python_version"]


def test_cli_missing_dependency(capsys):
    exit_code = cli.run(["--require-tool", "definitely_not_a_real_tool_xyz"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_MISSING_DEPENDENCY
    assert "missing" in captured.err


def test_cli_malformed_configuration(tmp_path, capsys):
    bad_path = tmp_path / "bad.json"
    bad_path.write_text("{not valid json", encoding="utf-8")

    exit_code = cli.run(["--events-file", str(bad_path)])
    captured = capsys.readouterr()

    assert exit_code == cli.EXIT_INVALID_INPUT
    assert "malformed" in captured.err.lower()


def test_cli_missing_events_file(tmp_path, capsys):
    missing_path = tmp_path / "nope.json"
    exit_code = cli.run(["--events-file", str(missing_path)])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_INVALID_INPUT
    assert "not found" in captured.err.lower()
