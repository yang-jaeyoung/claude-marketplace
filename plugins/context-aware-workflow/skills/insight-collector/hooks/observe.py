#!/usr/bin/env python3
"""
Observation Hook for Insight Collector

Captures PreToolUse and PostToolUse events to build a behavioral profile
for automatic instinct generation.

Cross-platform compatible (macOS, Linux, Windows).

Usage:
    # In hooks.json:
    "PreToolUse": [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/hooks/observe.py\" pre"}]
    }],
    "PostToolUse": [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/hooks/observe.py\" post"}]
    }]
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import common utilities
try:
    from lib.common import get_project_dir, get_caw_dir, ensure_dir, SYSTEM_DIRS
except ImportError:
    # Fallback for standalone usage
    SYSTEM_DIRS = frozenset([
        '/etc', '/usr', '/bin', '/sbin', '/var', '/root', '/boot', '/sys', '/proc',
        'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)', 'C:\\System32'
    ])

    def get_project_dir() -> Path:
        project_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())).resolve()
        project_dir_str = str(project_dir)
        for sys_dir in SYSTEM_DIRS:
            if project_dir_str == sys_dir or project_dir_str.startswith(sys_dir + os.sep):
                raise ValueError(f"Refusing to operate in system directory: {sys_dir}")
        return project_dir

    def get_caw_dir() -> Path:
        return get_project_dir() / '.caw'

    def ensure_dir(path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path

# Type definitions (optional - for IDE support)
try:
    from lib.types import Observation
except ImportError:
    pass

# Cross-platform file locking
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

# Truncation constants
MAX_STRING_LENGTH = 1000
MAX_LIST_ITEMS = 20
TRUNCATION_SUFFIX = '... [truncated]'

# Sensitive keys frozenset for O(1) lookup
SENSITIVE_KEYS = frozenset([
    'password',
    'api_key',
    'apikey',
    'token',
    'secret',
    'credential',
    'auth',
    'bearer',
    'private_key',
    'privatekey',
    'access_key',
    'accesskey',
])

# Skip tools frozenset for O(1) lookup
SKIP_TOOLS = frozenset([
    'TaskCreate',
    'TaskUpdate',
    'TaskList',
    'TaskGet',
    # Keep most tools for pattern detection
])

def ensure_observations_dir() -> Path:
    """Ensure observations directory exists and return path."""
    obs_dir = get_caw_dir() / 'observations'
    return ensure_dir(obs_dir)


def get_observations_file() -> Path:
    """Get path to observations JSONL file."""
    return ensure_observations_dir() / 'observations.jsonl'


def read_stdin_json() -> Optional[Dict[str, Any]]:
    """
    Read JSON from stdin (hook input).

    Claude Code hooks receive tool call information via stdin.
    """
    try:
        if sys.stdin.isatty():
            return None
        # Limit stdin read to 1MB to prevent memory exhaustion
        MAX_INPUT_SIZE = 1024 * 1024  # 1MB
        raw = sys.stdin.read(MAX_INPUT_SIZE).strip()
        if not raw:
            return None
        return json.loads(raw)
    except json.JSONDecodeError:
        return None
    except IOError:
        return None


def rotate_if_needed(file_path: Path, max_size: int = 5 * 1024 * 1024, max_backups: int = 5) -> None:
    """Rotate log file if it exceeds max_size."""
    if not file_path.exists() or file_path.stat().st_size < max_size:
        return

    # Rotate backups: .5 -> delete, .4 -> .5, .3 -> .4, etc.
    for i in range(max_backups - 1, 0, -1):
        old_backup = file_path.with_suffix(f'.jsonl.{i}')
        new_backup = file_path.with_suffix(f'.jsonl.{i + 1}')
        if old_backup.exists():
            if new_backup.exists():
                new_backup.unlink()
            old_backup.rename(new_backup)

    # Move current file to .1
    backup = file_path.with_suffix('.jsonl.1')
    if backup.exists():
        backup.unlink()
    file_path.rename(backup)


def append_observation(observation: Dict[str, Any]) -> bool:
    """Append observation to JSONL file with file locking and rotation."""
    try:
        obs_file = get_observations_file()

        # Rotate if needed before appending
        rotate_if_needed(obs_file)

        # Ensure parent directory exists
        obs_file.parent.mkdir(parents=True, exist_ok=True)

        # Direct append with file locking
        with open(obs_file, 'a', encoding='utf-8') as f:
            # Lock the file (cross-platform)
            if HAS_FCNTL:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            elif HAS_MSVCRT:
                # Windows locking - lock first byte
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

            try:
                f.write(json.dumps(observation) + '\n')
                f.flush()
                os.fsync(f.fileno())
            finally:
                # Unlock
                if HAS_FCNTL:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                elif HAS_MSVCRT:
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)

        return True
    except IOError as e:
        print(f"Failed to write observation: {e}", file=sys.stderr)
        return False


def get_session_id() -> str:
    """Get or generate session ID for grouping observations."""
    session_file = get_caw_dir() / 'observations' / '.session_id'

    if session_file.exists():
        try:
            return session_file.read_text(encoding='utf-8').strip()
        except IOError:
            pass

    # Generate new session ID with microseconds to reduce collision
    session_id = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')

    try:
        session_file.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write with tempfile + rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=session_file.parent,
            prefix='.session_id_',
            suffix='.tmp',
            text=True
        )

        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_f:
                temp_f.write(session_id)
                temp_f.flush()
                os.fsync(temp_f.fileno())

            # Atomic rename
            os.replace(temp_path, session_file)

        except Exception:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    except IOError:
        pass

    return session_id


def create_observation(
    event_type: str,
    tool_name: str,
    tool_input: Optional[Dict[str, Any]] = None,
    tool_output: Optional[str] = None,
    success: Optional[bool] = None,
    duration_ms: Optional[int] = None
) -> Dict[str, Any]:
    """Create an observation record."""
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'session_id': get_session_id(),
        'event_type': event_type,  # 'pre' or 'post'
        'tool_name': tool_name,
        'tool_input': tool_input,
        'tool_output': tool_output,
        'success': success,
        'duration_ms': duration_ms,
        'project_dir': str(get_project_dir()),
    }


def extract_tool_info(hook_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract tool information from hook input.

    Hook input structure varies by event type:
    - PreToolUse: { tool_name, tool_input }
    - PostToolUse: { tool_name, tool_input, tool_output, success, duration_ms }
    """
    try:
        tool_name = hook_input.get('tool_name', hook_input.get('toolName', 'unknown'))
        tool_input = hook_input.get('tool_input', hook_input.get('toolInput'))
        tool_output = hook_input.get('tool_output', hook_input.get('toolOutput'))
        success = hook_input.get('success')
        duration_ms = hook_input.get('duration_ms', hook_input.get('durationMs'))

        return {
            'tool_name': tool_name,
            'tool_input': tool_input,
            'tool_output': tool_output,
            'success': success,
            'duration_ms': duration_ms,
        }
    except (KeyError, AttributeError) as e:
        print(f"Failed to extract tool info - {type(e).__name__}: {e}", file=sys.stderr)
        return {
            'tool_name': 'unknown',
            'tool_input': None,
            'tool_output': None,
            'success': None,
            'duration_ms': None,
        }
    except Exception as e:
        import traceback
        print(f"Unexpected error in extract_tool_info - {type(e).__name__}: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return {
            'tool_name': 'unknown',
            'tool_input': None,
            'tool_output': None,
            'success': None,
            'duration_ms': None,
        }


def should_skip_tool(tool_name: str) -> bool:
    """Check if this tool should be skipped from observation."""
    return tool_name in SKIP_TOOLS


def mask_sensitive_data(data: Any) -> Any:
    """
    Mask sensitive data recursively.

    Recursively processes data structures and replaces values for keys
    matching sensitive patterns (password, api_key, token, secret, etc.)
    with "[MASKED]". Only primitive values (strings, numbers) are masked;
    nested dicts and lists are processed recursively.

    Args:
        data: Any data structure (dict, list, string, etc.)

    Returns:
        Data structure with sensitive values masked.
    """
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            # Case-insensitive key check
            if key.lower() in SENSITIVE_KEYS:
                # Only mask if value is not a dict or list (to allow nested processing)
                if isinstance(value, (dict, list)):
                    masked[key] = mask_sensitive_data(value)
                else:
                    masked[key] = '[MASKED]'
            else:
                masked[key] = mask_sensitive_data(value)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    else:
        return data


def truncate_for_storage(data: Any, max_length: int = MAX_STRING_LENGTH) -> Any:
    """
    Truncate large data for storage efficiency and mask sensitive data.

    Combines truncation and sensitive data masking into a single pass.
    Masking is applied first, then truncation.

    Args:
        data: Any data structure to process
        max_length: Maximum string length before truncation

    Returns:
        Processed data with sensitive values masked and large strings truncated.
    """
    # First, mask sensitive data
    data = mask_sensitive_data(data)

    # Then, truncate large strings
    if isinstance(data, str):
        if len(data) > max_length:
            return data[:max_length] + TRUNCATION_SUFFIX
        return data
    elif isinstance(data, dict):
        return {k: truncate_for_storage(v, max_length) for k, v in data.items()}
    elif isinstance(data, list):
        return [truncate_for_storage(item, max_length) for item in data[:MAX_LIST_ITEMS]]
    return data


def observe_pre(hook_input: Dict[str, Any]) -> None:
    """Handle PreToolUse observation."""
    info = extract_tool_info(hook_input)

    if should_skip_tool(info['tool_name']):
        return

    observation = create_observation(
        event_type='pre',
        tool_name=info['tool_name'],
        tool_input=truncate_for_storage(info['tool_input']),
    )

    append_observation(observation)


def observe_post(hook_input: Dict[str, Any]) -> None:
    """Handle PostToolUse observation."""
    info = extract_tool_info(hook_input)

    if should_skip_tool(info['tool_name']):
        return

    observation = create_observation(
        event_type='post',
        tool_name=info['tool_name'],
        tool_input=truncate_for_storage(info['tool_input']),
        tool_output=truncate_for_storage(info['tool_output']),
        success=info['success'],
        duration_ms=info['duration_ms'],
    )

    append_observation(observation)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: observe.py <pre|post>", file=sys.stderr)
        sys.exit(1)

    event_type = sys.argv[1].lower()

    if event_type not in ('pre', 'post'):
        print(f"Unknown event type: {event_type}", file=sys.stderr)
        sys.exit(1)

    # Read hook input from stdin
    hook_input = read_stdin_json()

    if not hook_input:
        # No input - might be running without proper hook context
        # Just exit silently
        sys.exit(0)

    try:
        if event_type == 'pre':
            observe_pre(hook_input)
        else:
            observe_post(hook_input)
    except Exception as e:
        # Don't block the tool call on observation errors
        print(f"Observation error: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == '__main__':
    main()
