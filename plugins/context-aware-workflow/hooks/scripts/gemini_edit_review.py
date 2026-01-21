#!/usr/bin/env python3
"""
Gemini-powered code review for Edit/Write operations.

This PreToolUse hook performs automated code review using gemini-cli's
headless mode before file modifications.

Activation:
    export CAW_GEMINI_REVIEW=enabled

Authentication (one of):
    - gemini auth login (Google account)
    - export GEMINI_API_KEY=your_api_key

Debug mode:
    export CAW_GEMINI_DEBUG=enabled

Output format:
{
  "result": "approve",
  "additionalContext": "[Gemini Review] ..."
}

Environment variables read by Claude Code:
- CLAUDE_TOOL_INPUT: JSON containing the tool input parameters
"""

from pathlib import Path
from typing import Optional

# Import shared utilities
from gemini_utils import (
    debug_log,
    is_gemini_review_enabled,
    is_caw_active,
    get_tool_input,
    run_gemini_prompt,
    truncate_text,
    format_review_output,
    approve_result,
)


# File extensions to skip review
SKIP_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".lock"}


REVIEW_PROMPT = """Review this code change for potential issues. Focus on:
1. Bugs or logic errors
2. Security vulnerabilities (injection, XSS, etc.)
3. Breaking changes
4. Missing error handling

Be concise (max 2 sentences). If no issues found, say "LGTM".

Change:
"""


def read_file_content(file_path: str) -> Optional[str]:
    """Read the current content of a file with path validation."""
    try:
        path = Path(file_path).resolve()
        
        # Basic path validation - ensure it's a file path
        if not path.suffix:
            debug_log(f"Skipping path without extension: {file_path}")
            return None
            
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
        return None
    except Exception as e:
        debug_log(f"Failed to read file {file_path}: {e}")
        return None


def create_diff_context(tool_input: dict) -> Optional[str]:
    """
    Create a diff-like context from tool input.

    For Edit tool: shows old_string -> new_string replacement
    For Write tool: shows the new content being written
    """
    if not tool_input:
        return None

    file_path = tool_input.get("file_path", "")
    file_name = Path(file_path).name if file_path else "unknown"

    # Check if it's an Edit operation
    old_string = tool_input.get("old_string")
    new_string = tool_input.get("new_string")

    if old_string is not None and new_string is not None:
        # Edit operation - create pseudo-diff
        diff = f"File: {file_name}\n\n"
        diff += "--- Before\n+++ After\n\n"

        old_lines = old_string.split("\n")
        new_lines = new_string.split("\n")

        for line in old_lines:
            diff += f"- {line}\n"
        for line in new_lines:
            diff += f"+ {line}\n"

        return diff

    # Check if it's a Write operation
    content = tool_input.get("content")
    if content is not None:
        # For Write, show what's being written
        current = read_file_content(file_path)

        if current:
            # File exists - show it's being overwritten
            return f"File: {file_name} (OVERWRITE)\n\nNew content:\n{content[:2000]}"
        else:
            # New file
            return f"File: {file_name} (NEW FILE)\n\nContent:\n{content[:2000]}"

    return None


def should_skip_file(file_path: str) -> bool:
    """Check if file should be skipped based on extension."""
    if not file_path:
        return True
    return any(file_path.endswith(ext) for ext in SKIP_EXTENSIONS)


def main():
    """Main entry point."""
    try:
        # Check if feature is enabled and configured
        if not is_gemini_review_enabled():
            print(approve_result())
            return

        # Only run if CAW is active
        if not is_caw_active():
            print(approve_result())
            return

        # Parse tool input
        tool_input = get_tool_input()
        if not tool_input:
            print(approve_result())
            return

        file_path = tool_input.get("file_path", "")

        # Skip review for certain file types
        if should_skip_file(file_path):
            debug_log(f"Skipping review for {file_path}")
            print(approve_result())
            return

        # Create diff context
        context = create_diff_context(tool_input)
        if not context:
            print(approve_result())
            return

        file_name = Path(file_path).name if file_path else "file"
        debug_log(f"Reviewing edit to {file_name}")

        # Run Gemini review
        prompt = REVIEW_PROMPT + truncate_text(context, 6000)
        review = run_gemini_prompt(prompt)

        if review:
            context_prefix = f"[Gemini Review] {file_name}"
            formatted = format_review_output(review, context_prefix)
            print(approve_result(formatted))
        else:
            # Gemini review failed or unavailable
            debug_log("Gemini review returned no result")
            print(approve_result())

    except Exception as e:
        # Silent failure - approve by default
        debug_log(f"Exception in edit review: {e}")
        print(approve_result())


if __name__ == "__main__":
    main()
