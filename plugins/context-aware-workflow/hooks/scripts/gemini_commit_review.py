#!/usr/bin/env python3
"""
Gemini-powered code review for git commits.

This PreToolUse hook performs automated code review using gemini-cli's
headless mode before git commits.

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
"""

import sys

# Windows UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from pathlib import Path

# Import shared utilities
from gemini_utils import (
    debug_log,
    is_gemini_review_enabled,
    is_caw_active,
    is_gate_mode,
    is_git_commit_command,
    get_tool_input,
    get_staged_diff,
    get_staged_files,
    run_gemini_prompt,
    truncate_text,
    format_review_output,
    approve_result,
    block_result,
    output_async_notification,
    detect_critical_issues,
)


REVIEW_PROMPT = """Review this git diff for potential issues. Focus on:
1. Bugs or logic errors
2. Security vulnerabilities
3. Performance issues
4. Code quality concerns

Be concise (max 3 sentences). If no issues found, say "LGTM".

Diff:
"""


def main():
    """Main entry point."""
    try:
        # Check if this is a git commit command
        tool_input = get_tool_input()
        if not is_git_commit_command(tool_input):
            print(approve_result())
            return

        debug_log("Git commit detected, checking review conditions")

        # Check if feature is enabled and configured
        if not is_gemini_review_enabled():
            print(approve_result())
            return

        # Only run if CAW is active
        if not is_caw_active():
            print(approve_result())
            return

        # Get staged changes
        diff = get_staged_diff()
        if not diff.strip():
            debug_log("No staged changes to review")
            print(approve_result())
            return

        # Get staged files for context
        files = get_staged_files()
        file_count = len(files)
        file_info = f"{file_count} file{'s' if file_count != 1 else ''}"

        debug_log(f"Reviewing {file_info}")

        # Run Gemini review (timeout slightly less than hook timeout of 45s)
        prompt = REVIEW_PROMPT + truncate_text(diff, 8000)
        review = run_gemini_prompt(prompt, timeout=40)

        if not review:
            # Gemini review failed or unavailable
            debug_log("Gemini review returned no result")
            print(approve_result())
            return

        # Check operation mode: Gate vs Async
        if is_gate_mode():
            # Gate mode: blocking review with reject capability
            debug_log("Gate mode enabled - checking for critical issues")

            critical_issue = detect_critical_issues(review)
            if critical_issue:
                reason = f"[Gemini Gate] {critical_issue} detected in commit ({file_info})"
                debug_log(f"Blocking commit: {reason}")
                print(block_result(reason))
                return

            # No critical issues - approve with context
            context_prefix = f"[Gemini Review] {file_info}"
            context = format_review_output(review, context_prefix)
            print(approve_result(context))
        else:
            # Async mode: notification only, immediate approve
            debug_log("Async mode - outputting notification")

            # Format review for notification (avoid double prefix)
            short_review = review[:120] + "..." if len(review) > 120 else review
            short_review = " ".join(short_review.split())  # Normalize whitespace

            # Output to stderr for async notification display
            output_async_notification(f"Commit {file_info}", short_review)

            # Always approve in async mode
            print(approve_result())

    except Exception as e:
        # Silent failure - approve by default
        debug_log(f"Exception in commit review: {e}")
        print(approve_result())


if __name__ == "__main__":
    main()
