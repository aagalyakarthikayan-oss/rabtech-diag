"""Command-line entry point for rabtech-diag."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import events, report, system_info

EXIT_OK = 0
EXIT_MISSING_DEPENDENCY = 1
EXIT_INVALID_INPUT = 2
EXIT_UNEXPECTED_ERROR = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rabtech-diag", description="Machine + diagnostic-event inspection CLI."
    )
    parser.add_argument(
        "--events-file", "-e", default=None, help="Path to a diagnostic events JSON file to analyze."
    )
    parser.add_argument(
        "--require-tool",
        "-r",
        action="append",
        default=[],
        help="A developer tool that MUST be present (repeatable). Missing -> exit code 1.",
    )
    parser.add_argument(
        "--tools",
        nargs="*",
        default=None,
        help="Developer tools to check for (default: git, pip, python3, docker).",
    )
    parser.add_argument("--disk-path", default=".", help="Path to check disk usage for (default: cwd).")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON instead of text.")
    parser.add_argument("--output", "-o", default=None, help="Write the report to a file instead of stdout.")
    parser.add_argument("--skip-system", action="store_true", help="Skip machine inspection.")
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    sys_info = None
    events_analysis = None

    try:
        if not args.skip_system:
            sys_info = system_info.gather_system_info(disk_path=args.disk_path, tools=args.tools)

        if args.events_file:
            try:
                data = events.load_events_file(args.events_file)
            except FileNotFoundError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return EXIT_INVALID_INPUT
            except events.MalformedEventDataError as exc:
                print(f"error: malformed event data: {exc}", file=sys.stderr)
                return EXIT_INVALID_INPUT
            events_analysis = events.analyze_events(data)

    except Exception as exc:
        print(f"unexpected error: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED_ERROR

    if args.require_tool and sys_info:
        found_names = {t["name"] for t in sys_info["dev_tools"] if t["found"]}
        missing = [t for t in args.require_tool if t not in found_names]
        if missing:
            print(f"error: required developer tool(s) missing: {missing}", file=sys.stderr)
            return EXIT_MISSING_DEPENDENCY

    final_report = report.build_report(sys_info, events_analysis)
    output_text = report.to_json(final_report) if args.json else report.to_human_readable(final_report)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output_text)
    else:
        print(output_text)

    return EXIT_OK


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
