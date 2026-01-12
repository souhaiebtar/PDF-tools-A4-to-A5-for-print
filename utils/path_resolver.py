"""
Path resolution utilities for PDF tools.
Handles finding bundled dependencies and system tools.
"""

import os
import shutil
import sys
from typing import List, Optional


def _candidate_base_dirs() -> List[str]:
    """Where to look for bundled dependencies (dev + PyInstaller)."""
    dirs = []

    # PyInstaller: prefer folder next to the exe (where users can ship dependencies/)
    if getattr(sys, "frozen", False):
        dirs.append(os.path.dirname(sys.executable))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            dirs.append(meipass)

    # Dev: folder containing main.py
    dirs.append(os.path.dirname(os.path.abspath(__file__)))

    # De-duplicate while preserving order
    unique_dirs = []
    for d in dirs:
        if d and d not in unique_dirs:
            unique_dirs.append(d)
    return unique_dirs


def resolve_tool_path(
    tool_name: str, env_var: Optional[str] = None, subfolder: Optional[str] = None
) -> Optional[str]:
    """Generic tool path resolver."""
    # Check environment variable first
    if env_var:
        env_path = os.environ.get(env_var)
        if env_path and os.path.exists(env_path):
            return env_path

    # Construct executable name for platform
    exe_name = f"{tool_name}.exe" if os.name == "nt" else tool_name

    # Search in bundled dependencies
    for base in _candidate_base_dirs():
        if subfolder:
            candidate = os.path.join(base, "dependencies", subfolder, exe_name)
        else:
            candidate = os.path.join(base, "dependencies", exe_name)
        if os.path.exists(candidate):
            return candidate

    # Fall back to system PATH
    return shutil.which(tool_name)


def resolve_pdfcpu_path() -> Optional[str]:
    """Resolve pdfcpu executable path."""
    return resolve_tool_path("pdfcpu", "PDFCPU_PATH")


def resolve_qpdf_path() -> Optional[str]:
    """Resolve qpdf executable path."""
    return resolve_tool_path("qpdf", "QPDF_PATH", "qpdf")


def resolve_app_icon_path() -> Optional[str]:
    """Return path to an app icon file (prefers .ico, falls back to .png)."""
    rel_candidates = [
        os.path.join("dependencies", "app.ico"),
        os.path.join("dependencies", "app.png"),
        "app.ico",
        "app.png",
    ]

    for base in _candidate_base_dirs():
        for rel in rel_candidates:
            candidate = os.path.join(base, rel)
            if os.path.exists(candidate):
                return candidate

    return None
