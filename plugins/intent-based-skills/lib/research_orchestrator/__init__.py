"""Research Orchestrator - Multi-agent research system."""

from .orchestrator import ResearchOrchestrator
from .config import load_config
from .models import (
    ResearchDepth,
    ExecutionMode,
    OrchestratorConfig,
    ResearchResult,
)

__version__ = "1.0.0"

__all__ = [
    "ResearchOrchestrator",
    "load_config",
    "ResearchDepth",
    "ExecutionMode",
    "OrchestratorConfig",
    "ResearchResult",
]
