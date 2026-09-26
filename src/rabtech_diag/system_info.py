"""Inspect the local machine: Python version, disk space, env vars, dev tools."""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional

DEFAULT_ENV_VARS = ["PATH", "HOME", "VIRTUAL_ENV", "PYTHONPATH"]
DEFAULT_DEV_TOOLS = ["git", "pip", "python3", "docker"]


@dataclass
class ToolStatus:
    name: str
    found: bool
    path: Optional[str] = None
    version: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "found": self.found,
            "path": self.path,
            "version": self.version,
        }


def get_python_version() -> str:
    return platform.python_version()


def get_disk_space(path: str = ".") -> Dict[str, float]:
    total, used, free = shutil.disk_usage(path)
    percent_used = round((used / total) * 100, 2) if total else 0.0
    return {
        "path": os.path.abspath(path),
        "total_gb": round(total / (1024 ** 3), 2),
        "used_gb": round(used / (1024 ** 3), 2),
        "free_gb": round(free / (1024 ** 3), 2),
        "percent_used": percent_used,
    }


def get_env_vars(keys: Optional[List[str]] = None) -> Dict[str, Optional[str]]:
    keys = keys or DEFAULT_ENV_VARS
    return {key: os.environ.get(key) for key in keys}


def _tool_version(tool_path: str) -> Optional[str]:
    try:
        result = subprocess.run(
            [tool_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        output = (result.stdout or result.stderr or "").strip()
        return output.splitlines()[0] if output else None
    except Exception:
        return None


def check_dev_tools(tools: Optional[List[str]] = None) -> List[ToolStatus]:
    tools = tools or DEFAULT_DEV_TOOLS
    statuses = []
    for tool in tools:
        found_path = shutil.which(tool)
        version = _tool_version(found_path) if found_path else None
        statuses.append(
            ToolStatus(name=tool, found=bool(found_path), path=found_path, version=version)
        )
    return statuses


def gather_system_info(
    disk_path: str = ".",
    env_keys: Optional[List[str]] = None,
    tools: Optional[List[str]] = None,
) -> dict:
    return {
        "python_version": get_python_version(),
        "platform": platform.platform(),
        "disk_space": get_disk_space(disk_path),
        "env_vars": get_env_vars(env_keys),
        "dev_tools": [t.to_dict() for t in check_dev_tools(tools)],
    }
