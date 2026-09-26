"""Build structured JSON and human-readable diagnostic reports."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def build_report(
    system_info: Optional[Dict[str, Any]] = None,
    events_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system_info": system_info,
        "events_analysis": events_analysis,
    }


def to_json(report: Dict[str, Any], indent: int = 2) -> str:
    return json.dumps(report, indent=indent, default=str)


def _fmt_tool(tool: Dict[str, Any]) -> str:
    status = "OK " if tool["found"] else "MISSING"
    version = f" ({tool['version']})" if tool.get("version") else ""
    return f"    [{status}] {tool['name']}{version}"


def to_human_readable(report: Dict[str, Any]) -> str:
    lines = [
        "RabTech Diagnostics Report",
        "=" * 30,
        f"Generated at: {report.get('generated_at')}",
        "",
    ]

    sysinfo = report.get("system_info")
    if sysinfo:
        lines.append("System Info")
        lines.append("-" * 30)
        lines.append(f"  Python version : {sysinfo.get('python_version')}")
        lines.append(f"  Platform       : {sysinfo.get('platform')}")
        disk = sysinfo.get("disk_space", {})
        lines.append(
            f"  Disk ({disk.get('path')}): {disk.get('used_gb')}GB used / "
            f"{disk.get('total_gb')}GB total ({disk.get('percent_used')}%)"
        )
        lines.append("  Environment variables:")
        for key, val in sysinfo.get("env_vars", {}).items():
            shown = val if val is None or len(str(val)) < 60 else str(val)[:57] + "..."
            lines.append(f"    {key} = {shown}")
        lines.append("  Developer tools:")
        for tool in sysinfo.get("dev_tools", []):
            lines.append(_fmt_tool(tool))
        lines.append("")

    events = report.get("events_analysis")
    if events:
        lines.append("Event Log Analysis")
        lines.append("-" * 30)
        lines.append(f"  Source           : {events.get('generated_for')}")
        lines.append(f"  Total events     : {events.get('total_events')}")
        lines.append(f"  Errors / Warnings: {events.get('error_count')} / {events.get('warn_count')}")
        lines.append(f"  Avg latency (ms) : {events.get('avg_latency_ms')}")
        lines.append(f"  By service       : {events.get('by_service')}")
        lines.append(f"  By status code   : {events.get('by_status_code')}")
        if events.get("malformed_entry_count"):
            lines.append(
                f"  Malformed entries: {events.get('malformed_entry_count')} (see JSON output for details)"
            )
        lines.append("")

    return "\n".join(lines)
