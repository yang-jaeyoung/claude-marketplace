#!/usr/bin/env python3
"""
Context pruning utilities for the context-aware-workflow plugin.

Provides functions to analyze file staleness and determine which files
should be kept, packed, or pruned from context.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union


def is_referenced_in_plan(file_path: str, plan_content: Optional[str]) -> bool:
    """
    Check if a file is referenced in the current plan.

    Matches either:
    - Full path (src/auth/jwt.ts)
    - Filename only (jwt.ts)

    Args:
        file_path: Path to check
        plan_content: Content of the current plan

    Returns:
        True if file is mentioned in plan, False otherwise
    """
    if not plan_content:
        return False

    # Check for full path
    if file_path in plan_content:
        return True

    # Check for filename only
    filename = os.path.basename(file_path)
    if filename in plan_content:
        return True

    return False


def calculate_staleness(file_info: Dict[str, Any], now: datetime) -> int:
    """
    Calculate how many hours since a file was last accessed.

    Uses 'last_accessed' timestamp if available, falls back to 'added'.
    Returns 0 if no timestamp is available or if timestamp is invalid.

    Args:
        file_info: Dict with 'last_accessed' or 'added' key (ISO format)
        now: Current datetime for comparison

    Returns:
        Hours since last access (integer)
    """
    timestamp_str = file_info.get("last_accessed") or file_info.get("added")
    if not timestamp_str:
        return 0

    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        diff = now - timestamp
        return int(diff.total_seconds() // 3600)
    except (ValueError, TypeError):
        return 0


def analyze_files(
    manifest: Dict[str, Any],
    plan_content: str,
    threshold_hours: int = 24
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Analyze files and categorize them for context management.

    Categories:
    - keep: Files to keep in full context
    - pack: Files to compress to interface-only
    - prune: Files to remove from context

    Decision logic:
    1. Files referenced in plan: KEEP (regardless of staleness)
    2. Recent files (< threshold/2 hours): KEEP
    3. Moderately stale files (threshold/2 to threshold): PACK
    4. Very stale files (> threshold hours): PRUNE

    Args:
        manifest: Context manifest with files.active list
        plan_content: Current plan content
        threshold_hours: Hours after which files are considered stale

    Returns:
        Dict with 'keep', 'pack', 'prune' lists
    """
    result = {
        "keep": [],
        "pack": [],
        "prune": []
    }

    # Get active files from manifest
    files = manifest.get("files", {}).get("active", [])
    if not files:
        return result

    now = datetime.now()
    half_threshold = threshold_hours / 2

    for file_info in files:
        path = file_info.get("path", "")
        staleness = calculate_staleness(file_info, now)

        entry = {
            "path": path,
            "staleness_hours": staleness,
            "recommendation": ""
        }

        # Check if referenced in plan - always keep
        if is_referenced_in_plan(path, plan_content):
            entry["recommendation"] = "Keep - referenced in task plan"
            result["keep"].append(entry)
            continue

        # Check staleness
        if staleness < half_threshold:
            entry["recommendation"] = "Keep - recently accessed"
            result["keep"].append(entry)
        elif staleness < threshold_hours:
            entry["recommendation"] = f"Pack - moderately stale ({staleness}h)"
            result["pack"].append(entry)
        else:
            entry["recommendation"] = f"Prune - very stale ({staleness}h)"
            result["prune"].append(entry)

    return result


def get_recommendations_summary(analysis: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Generate a human-readable summary of analysis recommendations.

    Args:
        analysis: Result from analyze_files()

    Returns:
        Markdown-formatted summary string
    """
    lines = ["# Context Analysis Summary\n"]

    keep_count = len(analysis.get("keep", []))
    pack_count = len(analysis.get("pack", []))
    prune_count = len(analysis.get("prune", []))
    total = keep_count + pack_count + prune_count

    lines.append(f"**Total files analyzed**: {total}\n")
    lines.append(f"- 🟢 Keep: {keep_count}")
    lines.append(f"- 🟡 Pack: {pack_count}")
    lines.append(f"- 🔴 Prune: {prune_count}")
    lines.append("")

    if analysis.get("prune"):
        lines.append("## Files to Prune\n")
        for entry in analysis["prune"]:
            lines.append(f"- `{entry['path']}` ({entry['staleness_hours']}h stale)")
        lines.append("")

    if analysis.get("pack"):
        lines.append("## Files to Pack\n")
        for entry in analysis["pack"]:
            lines.append(f"- `{entry['path']}` ({entry['staleness_hours']}h stale)")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    manifest = {
        "files": {
            "active": [
                {
                    "path": "src/auth/jwt.ts",
                    "last_accessed": (datetime.now() - timedelta(hours=2)).isoformat()
                },
                {
                    "path": "src/old/deprecated.ts",
                    "last_accessed": (datetime.now() - timedelta(hours=100)).isoformat()
                },
                {
                    "path": "src/utils/helpers.ts",
                    "last_accessed": (datetime.now() - timedelta(hours=8)).isoformat()
                },
            ]
        }
    }

    plan = "Edit src/auth/jwt.ts for token validation"

    analysis = analyze_files(manifest, plan, threshold_hours=12)
    print(get_recommendations_summary(analysis))
