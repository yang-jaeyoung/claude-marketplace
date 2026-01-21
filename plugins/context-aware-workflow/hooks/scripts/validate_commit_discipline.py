#!/usr/bin/env python3
"""
Validate commit discipline following Tidy First methodology.

This PreToolUse hook checks that git commits follow Tidy First principles:
- Structural (tidy) and behavioral (build) changes should not be mixed
- Provides context about the change type and suggested commit prefix

Output format:
{
  "result": "approve",
  "additionalContext": "[Tidy First] Change type: structural | Prefix: [tidy]"
}
"""

import json
import sys

# Windows UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def find_caw_root() -> Optional[Path]:
    """Find .caw directory starting from current working directory."""
    cwd = Path.cwd()

    for path in [cwd, *cwd.parents]:
        caw_dir = path / ".caw"
        if caw_dir.is_dir():
            return caw_dir

    return None


def get_staged_diff() -> str:
    """Get the staged git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged", "--no-color"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout
    except Exception:
        return ""


def get_staged_stat() -> str:
    """Get staged diff statistics."""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged", "--stat", "--no-color"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout
    except Exception:
        return ""


def classify_change(diff: str, stat: str) -> Tuple[str, float]:
    """
    Classify the change as structural, behavioral, or mixed.

    Returns: (change_type, confidence)
    """
    if not diff.strip():
        return ("empty", 1.0)

    structural_indicators = 0
    behavioral_indicators = 0

    # Structural indicators
    # - Rename operations
    if re.search(r"rename (from|to)", diff, re.IGNORECASE):
        structural_indicators += 3

    # - Similar line counts (additions ≈ deletions)
    additions = len(re.findall(r"^\+[^+]", diff, re.MULTILINE))
    deletions = len(re.findall(r"^-[^-]", diff, re.MULTILINE))

    if additions > 0 and deletions > 0:
        ratio = min(additions, deletions) / max(additions, deletions)
        if ratio > 0.8:  # Within 20%
            structural_indicators += 2

    # - Only whitespace/formatting changes
    whitespace_only = True
    for line in diff.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:].strip()
            if content and not re.match(r"^[\s,;{}()\[\]]*$", content):
                whitespace_only = False
                break
        if line.startswith("-") and not line.startswith("---"):
            content = line[1:].strip()
            if content and not re.match(r"^[\s,;{}()\[\]]*$", content):
                whitespace_only = False
                break

    if whitespace_only and additions > 0:
        structural_indicators += 2

    # Behavioral indicators
    # - New function/method definitions
    new_function_patterns = [
        r"^\+\s*(async\s+)?function\s+\w+",  # JS/TS function
        r"^\+\s*(export\s+)?(const|let|var)\s+\w+\s*=\s*(async\s+)?\(",  # Arrow function
        r"^\+\s*(public|private|protected)?\s*(async\s+)?\w+\s*\([^)]*\)\s*[:{]",  # Method
        r"^\+\s*def\s+\w+",  # Python function
        r"^\+\s*fn\s+\w+",  # Rust function
        r"^\+\s*func\s+\w+",  # Go function
    ]

    for pattern in new_function_patterns:
        if re.search(pattern, diff, re.MULTILINE):
            behavioral_indicators += 2

    # - New control flow (if, for, while, try)
    control_flow_patterns = [
        r"^\+\s*(if|else|elif|else if)\s*[\(:]",
        r"^\+\s*(for|while)\s*[\(:]",
        r"^\+\s*(try|catch|except|finally)\s*[\(:{]",
        r"^\+\s*(switch|case)\s*[\(:]",
    ]

    for pattern in control_flow_patterns:
        if re.search(pattern, diff, re.MULTILINE):
            behavioral_indicators += 1

    # - New exports
    if re.search(r"^\+\s*export\s+(default\s+)?", diff, re.MULTILINE):
        behavioral_indicators += 1

    # - New test files or test cases
    if re.search(r"^\+\+\+.*\.(test|spec)\.(ts|tsx|js|jsx|py)", diff):
        behavioral_indicators += 2
    if re.search(r"^\+\s*(it|test|describe)\s*\(", diff, re.MULTILINE):
        behavioral_indicators += 2

    # - Package.json changes (new dependencies)
    if "package.json" in stat:
        if re.search(r'^\+\s*"[^"]+"\s*:\s*"[\^~]?\d', diff, re.MULTILINE):
            behavioral_indicators += 2

    # Classify based on indicators
    total = structural_indicators + behavioral_indicators

    if total == 0:
        return ("neutral", 0.5)

    if structural_indicators > 0 and behavioral_indicators == 0:
        confidence = min(structural_indicators / 5, 1.0)
        return ("structural", confidence)

    if behavioral_indicators > 0 and structural_indicators == 0:
        confidence = min(behavioral_indicators / 5, 1.0)
        return ("behavioral", confidence)

    # Mixed - both indicators present
    return ("mixed", 0.8)


def get_suggested_prefix(change_type: str) -> str:
    """Get suggested commit message prefix based on change type."""
    prefixes = {
        "structural": "[tidy]",
        "behavioral": "[feat]/[fix]",
        "mixed": "Split into [tidy] + [feat]",
        "neutral": "[docs]/[chore]",
        "empty": ""
    }
    return prefixes.get(change_type, "")


def main():
    """Main entry point."""
    try:
        # Only run if CAW is active
        caw_root = find_caw_root()
        if not caw_root:
            print(json.dumps({"result": "approve"}))
            return

        # Get staged changes
        diff = get_staged_diff()
        stat = get_staged_stat()

        if not diff.strip():
            print(json.dumps({"result": "approve"}))
            return

        # Classify change
        change_type, confidence = classify_change(diff, stat)
        prefix = get_suggested_prefix(change_type)

        # Build additionalContext
        type_display = {
            "structural": "structural (tidy)",
            "behavioral": "behavioral (build)",
            "mixed": "MIXED - needs split",
            "neutral": "neutral (docs/chore)",
            "empty": "no changes"
        }

        context_parts = ["[Tidy First]"]
        context_parts.append(f"Change: {type_display.get(change_type, change_type)}")

        if prefix:
            context_parts.append(f"Prefix: {prefix}")

        if change_type == "mixed":
            context_parts.append("Consider splitting structural & behavioral changes")

        context = " | ".join(context_parts)

        # Truncate if needed
        if len(context) > 200:
            context = context[:197] + "..."

        output = {
            "result": "approve",
            "additionalContext": context
        }

        print(json.dumps(output))

    except Exception:
        # Silent failure - approve by default
        print(json.dumps({"result": "approve"}))


if __name__ == "__main__":
    main()
