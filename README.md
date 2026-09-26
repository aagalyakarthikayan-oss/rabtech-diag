# rabtech-diag

A Python CLI that inspects a machine (Python version, disk space, environment variables, developer tools) and analyzes diagnostic event log JSON files, producing JSON + human-readable reports.

## Usage

    rabtech-diag
    rabtech-diag --events-file samples/diagnostic-events.json --json

## Exit codes

- 0 = Success
- 1 = Required developer tool missing
- 2 = Malformed or missing input
- 3 = Unexpected error

## Running tests

    pip install -e ".[dev]"
    pytest -v
