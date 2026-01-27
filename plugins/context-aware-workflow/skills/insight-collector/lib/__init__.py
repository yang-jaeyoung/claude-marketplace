"""Insight Collector Integration Library."""
from .common import (
    get_project_dir,
    get_caw_dir,
    ensure_dir,
    SYSTEM_DIRS,
)
from .integration import (
    list_insights,
    search_insights,
    get_relevant_insights,
    list_instincts,
    get_evolution_candidates,
    get_metrics,
)
from .evolution import (
    get_evolved_dir,
    ensure_evolved_dirs,
    slugify,
    classify_instinct,
    extract_steps_from_action,
    generate_command_scaffold,
    generate_skill_scaffold,
    generate_agent_scaffold,
    create_evolution,
    track_evolution,
    get_evolution_candidates_list,
    EVOLUTION_TYPES,
    MIN_CONFIDENCE,
)
from .types import (
    Observation,
    Instinct,
    InstinctSummary,
    InstinctIndex,
    Insight,
    PatternCandidate,
    EvolutionCandidates,
    Metrics,
)

__all__ = [
    # Common utilities
    'get_project_dir',
    'get_caw_dir',
    'ensure_dir',
    'SYSTEM_DIRS',
    # Integration functions
    'list_insights',
    'search_insights',
    'get_relevant_insights',
    'list_instincts',
    'get_evolution_candidates',
    'get_metrics',
    # Evolution functions
    'get_evolved_dir',
    'ensure_evolved_dirs',
    'slugify',
    'classify_instinct',
    'extract_steps_from_action',
    'generate_command_scaffold',
    'generate_skill_scaffold',
    'generate_agent_scaffold',
    'create_evolution',
    'track_evolution',
    'get_evolution_candidates_list',
    # Constants
    'EVOLUTION_TYPES',
    'MIN_CONFIDENCE',
    # Types
    'Observation',
    'Instinct',
    'InstinctSummary',
    'InstinctIndex',
    'Insight',
    'PatternCandidate',
    'EvolutionCandidates',
    'Metrics',
]
