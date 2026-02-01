"""Type definitions for Insight Collector."""

from typing import List, Optional, TypedDict, NotRequired


class Observation(TypedDict):
    """Raw tool usage observation."""
    timestamp: str
    session_id: str
    event_type: str  # 'pre' | 'post'
    tool_name: str
    tool_input: NotRequired[dict]
    tool_output: NotRequired[str]
    success: NotRequired[bool]
    duration_ms: NotRequired[int]
    project_dir: str


class InstinctSummary(TypedDict):
    """Instinct summary stored in index.json."""
    id: str
    trigger: str
    confidence: float
    evidence_count: int
    domain: str


class Instinct(TypedDict, total=False):
    """Full instinct data."""
    id: str
    trigger: str
    action: str
    confidence: float
    evidence_count: int
    domain: str
    source: str
    last_observed: str
    created_at: str
    title: str
    notes: str
    body: str  # Markdown body content


class InstinctIndex(TypedDict):
    """Instinct index file structure."""
    instincts: List[InstinctSummary]
    last_updated: Optional[str]


class Insight(TypedDict, total=False):
    """Parsed insight data."""
    file: str
    filename: str
    title: str
    content: str
    tags: List[str]
    captured: str
    context: str


class PatternCandidate(TypedDict):
    """Pattern detection candidate."""
    type: str  # 'workflow' | 'error-recovery' | 'preference'
    trigger: str
    action: str
    evidence_count: int
    domain: str
    pattern: NotRequired[tuple]


class EvolutionCandidates(TypedDict):
    """Categorized evolution candidates."""
    commands: List[InstinctSummary]
    skills: List[InstinctSummary]
    agents: List[InstinctSummary]


class Metrics(TypedDict):
    """Session metrics."""
    insights_captured: int
    instincts_generated: int
    observations_recorded: int
