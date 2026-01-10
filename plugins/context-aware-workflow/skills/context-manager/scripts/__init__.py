# Context Manager Scripts
# Python utilities for the context-aware-workflow plugin

from .detect_plan import (
    extract_title,
    calculate_completion,
    extract_files_mentioned,
    count_steps,
    format_time_ago,
    is_recent,
)

from .pack_context import (
    extract_typescript_interfaces,
    extract_python_interfaces,
    format_markdown,
)

from .prune_context import (
    is_referenced_in_plan,
    calculate_staleness,
    analyze_files,
    get_recommendations_summary,
)

__all__ = [
    # detect_plan
    "extract_title",
    "calculate_completion",
    "extract_files_mentioned",
    "count_steps",
    "format_time_ago",
    "is_recent",
    # pack_context
    "extract_typescript_interfaces",
    "extract_python_interfaces",
    "format_markdown",
    # prune_context
    "is_referenced_in_plan",
    "calculate_staleness",
    "analyze_files",
    "get_recommendations_summary",
]
