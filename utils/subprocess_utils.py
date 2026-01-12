"""
Subprocess utilities for PDF tools.
Handles running external tools without showing console windows.
"""

import os
import subprocess
from typing import Dict, List, Optional


def subprocess_no_window_kwargs() -> Dict[str, any]:
    """Suppress console windows for subprocesses on Windows GUI builds."""
    if os.name != "nt":
        return {}

    kwargs = {}

    # Prevent a console window from being created (most reliable).
    kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    # Extra safety: explicitly hide any window that might be shown.
    if hasattr(subprocess, "STARTUPINFO") and hasattr(
        subprocess, "STARTF_USESHOWWINDOW"
    ):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = getattr(subprocess, "SW_HIDE", 0)
        kwargs["startupinfo"] = startupinfo

    return kwargs


def run_command(
    cmd: List[str], capture_output: bool = True, check: bool = False, text: bool = True
) -> subprocess.CompletedProcess:
    """Run a command with window suppression."""
    kwargs = subprocess_no_window_kwargs()
    if capture_output:
        kwargs["capture_output"] = True
    if text:
        kwargs["text"] = True

    return subprocess.run(cmd, check=check, **kwargs)


def check_command(cmd: List[str]) -> str:
    """Run a command and return stdout, raising CalledProcessError on failure."""
    kwargs = subprocess_no_window_kwargs()
    return subprocess.check_output(cmd, **kwargs).decode()


def verify_tool(tool_path: str) -> bool:
    """Verify that a tool can run by checking its version."""
    try:
        result = run_command([tool_path, "--version"], check=False)
        return result.returncode == 0
    except Exception:
        return False
