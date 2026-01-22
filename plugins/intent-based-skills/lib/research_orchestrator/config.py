"""Configuration management for Research Orchestrator."""

from pathlib import Path
from typing import Optional
import json
import yaml

from .models import OrchestratorConfig, ResearchDepth, ExecutionMode


# Default configuration values
DEFAULT_CONFIG = {
    "depth": "standard",
    "mode": "interactive",
    "research_type": "technical",
    "language": "ko",
    "output_dir": "./research-output",
    "guardrails": {
        "max_stages": 10,
        "max_parallel_agents": 5,
        "timeout_per_stage": 30,  # minutes
        "total_timeout": 120,  # minutes
        "max_retries": 2,
    },
}

# Depth-specific configurations
DEPTH_CONFIG = {
    "quick": {
        "stage_range": (2, 3),
        "timeout_per_stage": 15,
        "total_timeout": 45,
    },
    "standard": {
        "stage_range": (4, 6),
        "timeout_per_stage": 30,
        "total_timeout": 120,
    },
    "deep": {
        "stage_range": (7, 10),
        "timeout_per_stage": 45,
        "total_timeout": 180,
    },
}

# Research type configurations
RESEARCH_TYPE_CONFIG = {
    "technical": {
        "focus_areas": ["architecture", "implementation", "performance", "trade-offs"],
        "source_priority": ["documentation", "github", "technical blogs", "papers"],
    },
    "academic": {
        "focus_areas": ["theory", "methodology", "citations", "peer-review"],
        "source_priority": ["arxiv", "papers", "journals", "conferences"],
    },
    "market": {
        "focus_areas": ["trends", "competition", "pricing", "adoption"],
        "source_priority": ["reports", "news", "company sites", "reviews"],
    },
    "comparative": {
        "focus_areas": ["features", "pros/cons", "use-cases", "recommendations"],
        "source_priority": ["benchmarks", "comparisons", "user reviews", "docs"],
    },
}


def load_config(
    research_goal: str,
    depth: str = "standard",
    mode: str = "interactive",
    research_type: str = "technical",
    language: str = "ko",
    output_dir: Optional[str] = None,
    config_file: Optional[Path] = None,
    **overrides,
) -> OrchestratorConfig:
    """설정 로드 및 OrchestratorConfig 생성.

    Args:
        research_goal: 연구 목표
        depth: quick, standard, deep
        mode: interactive, auto
        research_type: technical, academic, market, comparative
        language: ko, en
        output_dir: 출력 디렉토리
        config_file: 추가 설정 파일 경로
        **overrides: 추가 오버라이드

    Returns:
        OrchestratorConfig 인스턴스
    """
    # Start with defaults
    config = DEFAULT_CONFIG.copy()

    # Load from config file if provided
    if config_file and config_file.exists():
        file_config = _load_config_file(config_file)
        config.update(file_config)

    # Apply depth-specific settings
    depth_settings = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["standard"])

    # Build final config
    guardrails = config.get("guardrails", DEFAULT_CONFIG["guardrails"])
    guardrails["timeout_per_stage"] = depth_settings["timeout_per_stage"]
    guardrails["total_timeout"] = depth_settings["total_timeout"]

    # Apply overrides
    for key, value in overrides.items():
        if key in guardrails:
            guardrails[key] = value

    return OrchestratorConfig(
        research_goal=research_goal,
        depth=ResearchDepth(depth),
        mode=ExecutionMode(mode),
        research_type=research_type,
        language=language,
        output_dir=Path(output_dir or config.get("output_dir", "./research-output")),
        max_stages=guardrails["max_stages"],
        max_parallel_agents=guardrails["max_parallel_agents"],
        timeout_per_stage=guardrails["timeout_per_stage"],
        total_timeout=guardrails["total_timeout"],
        max_retries=guardrails["max_retries"],
    )


def _load_config_file(path: Path) -> dict:
    """설정 파일 로드 (JSON 또는 YAML)."""
    content = path.read_text(encoding="utf-8")

    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(content) or {}
    elif path.suffix == ".json":
        return json.loads(content)
    else:
        raise ValueError(f"Unsupported config file format: {path.suffix}")


def get_research_type_config(research_type: str) -> dict:
    """연구 유형별 설정 반환."""
    return RESEARCH_TYPE_CONFIG.get(research_type, RESEARCH_TYPE_CONFIG["technical"])


def get_depth_config(depth: str) -> dict:
    """깊이별 설정 반환."""
    return DEPTH_CONFIG.get(depth, DEPTH_CONFIG["standard"])
