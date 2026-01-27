"""Common utilities for insight-collector skill."""

import os
from pathlib import Path
from typing import Optional

# System directories to refuse (path sanitization)
SYSTEM_DIRS = frozenset([
    '/etc', '/usr', '/bin', '/sbin', '/var', '/root', '/boot', '/sys', '/proc',
    'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)', 'C:\\System32'
])

def get_project_dir() -> Path:
    """Get project directory from environment or current directory.

    Raises:
        ValueError: If the resolved path is a sensitive system directory.
    """
    project_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())).resolve()

    # Path sanitization: refuse system directories
    project_dir_str = str(project_dir)
    for sys_dir in SYSTEM_DIRS:
        # Check if project_dir is exactly a system dir or a subdirectory of it
        if project_dir_str == sys_dir or project_dir_str.startswith(sys_dir + os.sep):
            raise ValueError(f"Refusing to operate in system directory: {sys_dir}")

    return project_dir


def get_caw_dir() -> Path:
    """Get .caw directory path."""
    return get_project_dir() / '.caw'


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists and return path."""
    path.mkdir(parents=True, exist_ok=True)
    return path
