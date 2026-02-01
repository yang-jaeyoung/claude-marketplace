#!/usr/bin/env python3
"""
Rate Limit Wait Utility for CAW workflow.

Automatically detects rate limit errors and provides wait-and-resume
functionality for long-running deepwork/ultrawork sessions.

Activation:
    export CAW_RATE_LIMIT_HANDLER=enabled

Features:
    - Detects Claude API rate limit responses
    - Calculates wait time from headers/response
    - Saves resume state for continuation
    - Notifies user of wait status

Environment variables:
    CAW_RATE_LIMIT_HANDLER: enabled|disabled (default: enabled)
    CAW_RATE_LIMIT_MAX_WAIT: maximum wait time in seconds (default: 300)
    CAW_RATE_LIMIT_RESUME: enabled|disabled - auto-resume after wait (default: enabled)
"""

import json
import os
import sys
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

# Windows UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


# Default configuration
DEFAULT_MAX_WAIT = 300  # 5 minutes
DEFAULT_RETRY_BACKOFF = [5, 10, 30, 60, 120]  # Progressive backoff


def find_caw_root() -> Optional[Path]:
    """Find .caw directory starting from current working directory."""
    cwd = Path.cwd()
    for path in [cwd, *cwd.parents]:
        caw_dir = path / ".caw"
        if caw_dir.is_dir():
            return caw_dir
    return None


def debug_log(message: str) -> None:
    """Log debug message to stderr if debug is enabled."""
    if os.environ.get("CAW_DEBUG", "").lower() in ("enabled", "true", "1"):
        print(f"[RateLimit Debug] {message}", file=sys.stderr)


def is_handler_enabled() -> bool:
    """Check if rate limit handler is enabled."""
    value = os.environ.get("CAW_RATE_LIMIT_HANDLER", "enabled").lower()
    return value in ("enabled", "true", "1")


def get_max_wait() -> int:
    """Get maximum wait time in seconds."""
    try:
        return int(os.environ.get("CAW_RATE_LIMIT_MAX_WAIT", DEFAULT_MAX_WAIT))
    except ValueError:
        return DEFAULT_MAX_WAIT


def is_auto_resume_enabled() -> bool:
    """Check if auto-resume is enabled."""
    value = os.environ.get("CAW_RATE_LIMIT_RESUME", "enabled").lower()
    return value in ("enabled", "true", "1")


def load_json_safe(path: Path) -> dict:
    """Load JSON file safely, returning empty dict on failure."""
    try:
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def save_json_safe(path: Path, data: dict) -> bool:
    """Save JSON file safely."""
    try:
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        return True
    except OSError as e:
        debug_log(f"Failed to save {path}: {e}")
        return False


def detect_rate_limit(error_message: str) -> Tuple[bool, int]:
    """
    Detect rate limit error and extract wait time.

    Returns:
        (is_rate_limited, wait_seconds)
    """
    if not error_message:
        return False, 0

    error_lower = error_message.lower()

    # Common rate limit indicators
    rate_limit_patterns = [
        r"rate.?limit",
        r"too.?many.?requests",
        r"429",
        r"quota.?exceeded",
        r"throttl",
        r"retry.?after",
    ]

    is_rate_limited = any(
        re.search(pattern, error_lower)
        for pattern in rate_limit_patterns
    )

    if not is_rate_limited:
        return False, 0

    # Try to extract wait time
    wait_seconds = 60  # Default wait

    # Pattern: "retry after X seconds"
    retry_match = re.search(r"retry.?after[:\s]+(\d+)\s*(?:seconds?|s)?", error_lower)
    if retry_match:
        wait_seconds = int(retry_match.group(1))

    # Pattern: "wait X seconds"
    wait_match = re.search(r"wait[:\s]+(\d+)\s*(?:seconds?|s)?", error_lower)
    if wait_match:
        wait_seconds = int(wait_match.group(1))

    # Pattern: "try again in X minutes"
    minutes_match = re.search(r"try.?again.?in[:\s]+(\d+)\s*(?:minutes?|m)", error_lower)
    if minutes_match:
        wait_seconds = int(minutes_match.group(1)) * 60

    return True, wait_seconds


def save_resume_state(caw_root: Path, wait_until: datetime, context: dict) -> None:
    """Save state for resuming after rate limit wait."""
    resume_state = {
        "rate_limited_at": datetime.utcnow().isoformat() + "Z",
        "resume_at": wait_until.isoformat() + "Z",
        "wait_seconds": int((wait_until - datetime.utcnow()).total_seconds()),
        "context": context,
        "retry_count": context.get("retry_count", 0) + 1
    }

    rate_limit_file = caw_root / "rate_limit_state.json"
    save_json_safe(rate_limit_file, resume_state)
    debug_log(f"Saved resume state: {resume_state}")


def load_resume_state(caw_root: Path) -> Optional[dict]:
    """Load saved resume state if available."""
    rate_limit_file = caw_root / "rate_limit_state.json"
    return load_json_safe(rate_limit_file) or None


def clear_resume_state(caw_root: Path) -> None:
    """Clear resume state after successful resume."""
    rate_limit_file = caw_root / "rate_limit_state.json"
    try:
        if rate_limit_file.exists():
            rate_limit_file.unlink()
            debug_log("Cleared resume state")
    except OSError:
        pass


def format_wait_time(seconds: int) -> str:
    """Format wait time for display."""
    if seconds >= 60:
        minutes = seconds // 60
        secs = seconds % 60
        if secs > 0:
            return f"{minutes}m {secs}s"
        return f"{minutes}m"
    return f"{seconds}s"


def notify_rate_limit(wait_seconds: int, resume_at: datetime) -> None:
    """Notify user about rate limit and wait time."""
    wait_display = format_wait_time(wait_seconds)
    resume_time = resume_at.strftime("%H:%M:%S")

    message = f"""
[Rate Limit Detected]
Waiting {wait_display} before retrying...
Resume at: {resume_time}

The workflow will automatically continue after the wait period.
To cancel, press Ctrl+C.
"""
    print(message, file=sys.stderr)


def wait_with_countdown(wait_seconds: int) -> bool:
    """
    Wait with countdown display.

    Returns True if wait completed, False if interrupted.
    """
    start_time = time.time()
    end_time = start_time + wait_seconds

    try:
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            if remaining <= 0:
                break

            # Update countdown every 10 seconds or for last 10 seconds
            if remaining <= 10 or remaining % 10 == 0:
                print(f"\r[Rate Limit] Resuming in {format_wait_time(remaining)}...  ",
                      end="", file=sys.stderr)

            time.sleep(1)

        print("\r[Rate Limit] Wait complete. Resuming...              ", file=sys.stderr)
        return True

    except KeyboardInterrupt:
        print("\n[Rate Limit] Wait cancelled by user.", file=sys.stderr)
        return False


def get_backoff_time(retry_count: int) -> int:
    """Get progressive backoff time based on retry count."""
    if retry_count < len(DEFAULT_RETRY_BACKOFF):
        return DEFAULT_RETRY_BACKOFF[retry_count]
    return DEFAULT_RETRY_BACKOFF[-1]


def handle_rate_limit(error_message: str, context: Optional[dict] = None) -> dict:
    """
    Main handler for rate limit errors.

    Args:
        error_message: The error message to check
        context: Optional context to save for resume

    Returns:
        Result dict with action to take
    """
    if not is_handler_enabled():
        return {"action": "passthrough", "handled": False}

    caw_root = find_caw_root()
    if not caw_root:
        return {"action": "passthrough", "handled": False}

    # Detect rate limit
    is_limited, wait_seconds = detect_rate_limit(error_message)

    if not is_limited:
        # Check if we're resuming from a previous rate limit
        resume_state = load_resume_state(caw_root)
        if resume_state:
            clear_resume_state(caw_root)
            return {
                "action": "resumed",
                "handled": True,
                "context": resume_state.get("context", {})
            }
        return {"action": "passthrough", "handled": False}

    # Apply maximum wait limit
    max_wait = get_max_wait()
    wait_seconds = min(wait_seconds, max_wait)

    # Get retry count for progressive backoff
    resume_state = load_resume_state(caw_root) or {}
    retry_count = resume_state.get("retry_count", 0)

    # Apply progressive backoff if this is a retry
    if retry_count > 0:
        backoff = get_backoff_time(retry_count)
        wait_seconds = max(wait_seconds, backoff)
        debug_log(f"Applied backoff: retry #{retry_count}, wait {wait_seconds}s")

    # Calculate resume time
    resume_at = datetime.utcnow() + timedelta(seconds=wait_seconds)

    # Save resume state
    save_resume_state(caw_root, resume_at, context or {})

    # Notify user
    notify_rate_limit(wait_seconds, resume_at)

    # Wait if auto-resume is enabled
    if is_auto_resume_enabled():
        wait_completed = wait_with_countdown(wait_seconds)

        if wait_completed:
            clear_resume_state(caw_root)
            return {
                "action": "retry",
                "handled": True,
                "wait_seconds": wait_seconds,
                "retry_count": retry_count + 1
            }
        else:
            return {
                "action": "cancelled",
                "handled": True,
                "resume_state_saved": True
            }

    # Manual resume mode
    return {
        "action": "wait_manual",
        "handled": True,
        "wait_seconds": wait_seconds,
        "resume_at": resume_at.isoformat() + "Z"
    }


def approve_result(additional_context: Optional[str] = None) -> str:
    """Return JSON approve result."""
    output = {"result": "approve"}
    if additional_context:
        output["additionalContext"] = additional_context
    return json.dumps(output)


def main():
    """Main entry point for hook usage."""
    if not is_handler_enabled():
        print(approve_result())
        return

    caw_root = find_caw_root()
    if not caw_root:
        print(approve_result())
        return

    # Check for pending resume
    resume_state = load_resume_state(caw_root)
    if resume_state:
        resume_at_str = resume_state.get("resume_at", "")
        try:
            resume_at = datetime.fromisoformat(resume_at_str.replace("Z", "+00:00"))
            now = datetime.utcnow().replace(tzinfo=resume_at.tzinfo)

            if now >= resume_at:
                # Ready to resume
                clear_resume_state(caw_root)
                print(approve_result("[Rate Limit] Resumed after wait"))
                return
            else:
                # Still waiting
                remaining = int((resume_at - now).total_seconds())
                print(approve_result(f"[Rate Limit] Waiting {format_wait_time(remaining)}"))
                return
        except (ValueError, TypeError):
            clear_resume_state(caw_root)

    print(approve_result())


if __name__ == "__main__":
    main()
