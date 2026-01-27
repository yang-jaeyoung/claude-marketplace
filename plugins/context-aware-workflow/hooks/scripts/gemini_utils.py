#!/usr/bin/env python3
"""
Common utilities for Gemini CLI integration in CAW hooks.

Shared functions for:
- CAW environment detection
- Gemini CLI availability checking
- Feature flag management
- Debug logging

Activation:
    export CAW_GEMINI_REVIEW=enabled

Debug mode:
    export CAW_GEMINI_DEBUG=enabled
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Windows UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
from typing import Optional, List

# Cache for gemini CLI availability check
_gemini_available: Optional[bool] = None


def debug_log(message: str) -> None:
    """Log debug message to stderr if CAW_GEMINI_DEBUG is enabled."""
    if os.environ.get("CAW_GEMINI_DEBUG", "").lower() in ("enabled", "true", "1"):
        print(f"[Gemini Debug] {message}", file=sys.stderr)


def find_caw_root() -> Optional[Path]:
    """Find .caw directory starting from current working directory."""
    cwd = Path.cwd()

    for path in [cwd, *cwd.parents]:
        caw_dir = path / ".caw"
        if caw_dir.is_dir():
            return caw_dir

    return None


def is_gemini_cli_available() -> bool:
    """Check if gemini CLI is installed (cached)."""
    global _gemini_available
    if _gemini_available is not None:
        return _gemini_available

    try:
        result = subprocess.run(
            ["gemini", "--version"],
            capture_output=True,
            timeout=5
        )
        _gemini_available = result.returncode == 0
        debug_log(f"Gemini CLI available: {_gemini_available}")
    except FileNotFoundError:
        debug_log("Gemini CLI not found")
        _gemini_available = False
    except subprocess.TimeoutExpired:
        debug_log("Gemini CLI check timed out")
        _gemini_available = False

    return _gemini_available


def is_gemini_review_enabled() -> bool:
    """Check if Gemini review is enabled and properly configured."""
    # Check feature flag
    flag_value = os.environ.get("CAW_GEMINI_REVIEW", "")
    if flag_value.lower() not in ("enabled", "true", "1"):
        debug_log(f"Gemini review disabled (CAW_GEMINI_REVIEW={flag_value})")
        return False

    # Check CLI availability
    if not is_gemini_cli_available():
        return False

    return True


def is_caw_active() -> bool:
    """Check if CAW workflow is active (has .caw directory)."""
    caw_root = find_caw_root()
    if not caw_root:
        debug_log("CAW not active (no .caw directory found)")
        return False
    return True


def run_gemini_prompt(prompt: str, timeout: int = 30) -> Optional[str]:
    """
    Run Gemini CLI in headless mode with the given prompt.

    Args:
        prompt: The prompt to send to Gemini
        timeout: Timeout in seconds (default: 30)

    Returns:
        The response text or None on failure
    """
    try:
        debug_log(f"Running Gemini with prompt length: {len(prompt)}")

        result = subprocess.run(
            ["gemini", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0 and result.stdout.strip():
            debug_log("Gemini response received")
            return result.stdout.strip()

        debug_log(f"Gemini returned code {result.returncode}")
        return None

    except subprocess.TimeoutExpired:
        debug_log(f"Gemini timed out after {timeout}s")
        return None
    except Exception as e:
        debug_log(f"Gemini error: {e}")
        return None


def truncate_text(text: str, max_chars: int) -> str:
    """Truncate text to max_chars with truncation indicator."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n... [truncated]"


def format_review_output(review: str, context_prefix: str, max_len: int = 200) -> str:
    """
    Format review output for additionalContext.

    Args:
        review: The raw review text from Gemini
        context_prefix: Prefix like "[Gemini Review] file.py"
        max_len: Maximum total length (default: 200)

    Returns:
        Formatted context string
    """
    # Calculate available space for review text
    prefix_len = len(context_prefix) + 3  # " | " separator
    max_review_len = max_len - prefix_len

    if max_review_len < 20:
        max_review_len = 20

    # Clean and truncate review
    review = " ".join(review.split())  # Normalize whitespace

    if len(review) > max_review_len:
        review = review[:max_review_len - 3] + "..."

    context = f"{context_prefix} | {review}"

    # Final safety truncation
    if len(context) > max_len:
        context = context[:max_len - 3] + "..."

    return context


def approve_result(additional_context: Optional[str] = None) -> str:
    """Return JSON approve result."""
    output = {"result": "approve"}
    if additional_context:
        output["additionalContext"] = additional_context
    return json.dumps(output)


def get_staged_diff() -> str:
    """Get the staged git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged", "--no-color"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except Exception as e:
        debug_log(f"Failed to get staged diff: {e}")
        return ""


def get_staged_files() -> List[str]:
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception as e:
        debug_log(f"Failed to get staged files: {e}")
        return []


def get_tool_input() -> Optional[dict]:
    """Parse tool input from CLAUDE_TOOL_INPUT environment variable."""
    try:
        tool_input_raw = os.environ.get("CLAUDE_TOOL_INPUT", "{}")
        return json.loads(tool_input_raw)
    except json.JSONDecodeError as e:
        debug_log(f"Failed to parse CLAUDE_TOOL_INPUT: {e}")
        return None


def is_git_commit_command(tool_input: Optional[dict]) -> bool:
    """Check if the tool input is a git commit command."""
    if not tool_input:
        return False

    command = tool_input.get("command", "")
    return "git commit" in command


def is_gate_mode() -> bool:
    """
    Check if Gate mode is enabled (CAW_REVIEW_GATE=1).

    Gate mode enables blocking reviews that can reject dangerous changes.
    When disabled (default), reviews run in async notification-only mode.
    """
    return os.environ.get("CAW_REVIEW_GATE", "") == "1"


def output_async_notification(source: str, message: str) -> None:
    """
    Output notification to stderr for async mode.

    In async mode, stderr output is displayed to the user as a notification.
    The message is truncated to prevent excessive output.

    Args:
        source: The notification source (e.g., "Gemini Review")
        message: The notification message
    """
    # Truncate long messages
    max_len = 150
    truncated = message[:max_len] + "..." if len(message) > max_len else message
    print(f"[{source}] {truncated}", file=sys.stderr)


def block_result(reason: str) -> str:
    """Return JSON block result for Gate mode rejection."""
    return json.dumps({
        "decision": "block",
        "reason": reason
    })


def detect_critical_issues(review: str) -> Optional[str]:
    """
    Detect critical security issues in Gemini review response.

    Returns the issue description if critical, None otherwise.
    """
    # Keywords indicating critical security issues
    critical_patterns = [
        (r"\b(sql\s*injection|sqli)\b", "SQL injection vulnerability"),
        (r"\b(xss|cross.?site.?scripting)\b", "XSS vulnerability"),
        (r"\b(command\s*injection|shell\s*injection)\b", "Command injection"),
        (r"\b(path\s*traversal|directory\s*traversal)\b", "Path traversal"),
        (r"\b(hardcoded\s*(secret|password|key|credential|token))\b", "Hardcoded credentials"),
        (r"\b(exposed\s*(secret|password|key|api.?key|credential))\b", "Exposed credentials"),
        (r"\b(remote\s*code\s*execution|rce)\b", "Remote code execution"),
        (r"\b(insecure\s*deserialization)\b", "Insecure deserialization"),
    ]

    review_lower = review.lower()

    for pattern, issue_name in critical_patterns:
        if re.search(pattern, review_lower, re.IGNORECASE):
            return issue_name

    return None
