from __future__ import annotations

import os
import stat
import sys
from pathlib import Path


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent.parent


def resource_path(relative_path: str) -> str:
    return str(project_root() / relative_path)


def ensure_executable(path: str) -> str:
    executable_path = Path(path)
    if executable_path.exists():
        current_mode = executable_path.stat().st_mode
        executable_bits = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        if not current_mode & executable_bits:
            os.chmod(executable_path, current_mode | executable_bits)
    return str(executable_path)

