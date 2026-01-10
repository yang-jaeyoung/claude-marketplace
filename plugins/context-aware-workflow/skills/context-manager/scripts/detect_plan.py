#!/usr/bin/env python3
"""
Plan detection utilities for the context-aware-workflow plugin.

Provides functions to analyze plan files, extract metadata, and calculate
completion status.
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List


def extract_title(content: str) -> str:
    """
    Extract title from plan content.

    Priority:
    1. H1 header (# Title)
    2. H2 header (## Title)
    3. First non-empty line (truncated to 50 chars)
    4. "Unknown Plan" if content is empty
    """
    if not content or not content.strip():
        return "Unknown Plan"

    lines = content.strip().split("\n")

    # Look for H1 header
    for line in lines:
        line = line.strip()
        if line.startswith("# ") and not line.startswith("## "):
            return line[2:].strip()

    # Look for H2 header
    for line in lines:
        line = line.strip()
        if line.startswith("## "):
            return line[3:].strip()

    # Fall back to first non-empty line
    for line in lines:
        line = line.strip()
        if line:
            if len(line) > 50:
                return line[:47] + "..."
            return line

    return "Unknown Plan"


def calculate_completion(content: str) -> float:
    """
    Calculate completion rate based on checkbox items.

    Returns a float between 0.0 and 1.0.
    Returns 0.0 if no checkboxes are present.
    """
    # Match completed: [x] or [X]
    completed = len(re.findall(r"\[(?:x|X)\]", content))
    # Match pending: [ ]
    pending = len(re.findall(r"\[ \]", content))

    total = completed + pending
    if total == 0:
        return 0.0

    return completed / total


def extract_files_mentioned(content: str) -> List[str]:
    """
    Extract file paths mentioned in backticks from content.

    Filters out non-file content (commands, short strings).
    Returns sorted list of unique file paths.
    """
    # Extract all backtick content
    backtick_pattern = re.compile(r"`([^`]+)`")
    matches = backtick_pattern.findall(content)

    # File extensions to include
    file_extensions = {
        ".ts", ".tsx", ".js", ".jsx", ".py", ".rs", ".go", ".java",
        ".json", ".yaml", ".yml", ".toml", ".md", ".html", ".css",
        ".scss", ".sql", ".sh", ".bash", ".zsh", ".fish", ".vue",
        ".svelte", ".astro", ".config", ".env", ".gitignore"
    }

    files = []
    for match in matches:
        match = match.strip()

        # Skip if it looks like a command (contains spaces but no path separators)
        if " " in match and "/" not in match and "\\" not in match:
            continue

        # Skip very short strings that are likely code snippets
        if len(match) < 3:
            continue

        # Include if it has a file extension
        for ext in file_extensions:
            if match.endswith(ext):
                files.append(match)
                break
        else:
            # Include if it has a path separator
            if "/" in match or "\\" in match:
                # Check for common file-like patterns
                if re.search(r"\.\w{1,10}$", match):
                    files.append(match)

    # Return sorted unique files
    return sorted(set(files))


def count_steps(content: str) -> Dict[str, int]:
    """
    Count completed, pending, and total steps in content.

    Returns dict with keys: completed, pending, total
    """
    completed = len(re.findall(r"\[(?:x|X)\]", content))
    pending = len(re.findall(r"\[ \]", content))

    return {
        "completed": completed,
        "pending": pending,
        "total": completed + pending
    }


def format_time_ago(dt: datetime) -> str:
    """
    Format a datetime as a human-readable "time ago" string.

    Examples:
    - "just now" (< 1 minute)
    - "5 minutes ago"
    - "1 hour ago"
    - "3 days ago"
    """
    now = datetime.now()
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"

    minutes = seconds // 60
    if minutes < 60:
        unit = "minute" if minutes == 1 else "minutes"
        return f"{minutes} {unit} ago"

    hours = minutes // 60
    if hours < 24:
        unit = "hour" if hours == 1 else "hours"
        return f"{hours} {unit} ago"

    days = hours // 24
    unit = "day" if days == 1 else "days"
    return f"{days} {unit} ago"


def is_recent(plan_info: Dict[str, Any], max_age_hours: int = 24) -> bool:
    """
    Check if a plan is recent (within max_age_hours).

    Args:
        plan_info: Dict with 'modified' key containing ISO format datetime
        max_age_hours: Maximum age in hours to be considered recent

    Returns:
        True if plan was modified within max_age_hours, False otherwise
    """
    modified_str = plan_info.get("modified")
    if not modified_str:
        return False

    try:
        modified = datetime.fromisoformat(modified_str)
        now = datetime.now()
        age = now - modified
        return age < timedelta(hours=max_age_hours)
    except (ValueError, TypeError):
        return False


if __name__ == "__main__":
    # Example usage
    sample_content = """
# Authentication Implementation Plan

## Completed
- [x] Create JWT utility
- [x] Add login endpoint

## In Progress
- [ ] Add refresh token logic
- [ ] Implement logout

## Files
- `src/auth/jwt.ts`
- `src/api/login.ts`
"""

    print("Title:", extract_title(sample_content))
    print("Completion:", f"{calculate_completion(sample_content) * 100:.0f}%")
    print("Files:", extract_files_mentioned(sample_content))
    print("Steps:", count_steps(sample_content))
