"""Data models for Research Orchestrator."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from pathlib import Path
from datetime import datetime


class ResearchDepth(Enum):
    """연구 깊이 레벨."""
    QUICK = "quick"      # 2-3 stages, 빠른 개요
    STANDARD = "standard"  # 4-6 stages, 균형잡힌 분석
    DEEP = "deep"        # 7-10 stages, 심층 연구

    @property
    def stage_range(self) -> tuple[int, int]:
        """해당 깊이의 stage 수 범위."""
        ranges = {
            ResearchDepth.QUICK: (2, 3),
            ResearchDepth.STANDARD: (4, 6),
            ResearchDepth.DEEP: (7, 10),
        }
        return ranges[self]


class ExecutionMode(Enum):
    """실행 모드."""
    INTERACTIVE = "interactive"  # 단계별 확인
    AUTO = "auto"               # 자동 실행


class StageStatus(Enum):
    """Stage 실행 상태."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Stage:
    """연구 단계."""
    stage_id: int
    name: str
    objective: str
    questions: list[str]
    dependencies: list[int] = field(default_factory=list)
    skippable: bool = False
    estimated_time: int = 10  # minutes

    def to_dict(self) -> dict:
        return {
            "stage_id": self.stage_id,
            "name": self.name,
            "objective": self.objective,
            "questions": self.questions,
            "dependencies": self.dependencies,
            "skippable": self.skippable,
            "estimated_time": self.estimated_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Stage":
        return cls(
            stage_id=data["stage_id"],
            name=data["name"],
            objective=data["objective"],
            questions=data["questions"],
            dependencies=data.get("dependencies", []),
            skippable=data.get("skippable", False),
            estimated_time=data.get("estimated_time", 10),
        )


@dataclass
class Finding:
    """연구 발견."""
    id: str  # F{stage_id}-{seq}, e.g., F1-001
    topic: str
    summary: str
    confidence: float  # 0.0 ~ 1.0
    evidence: list[str]
    sources: list[str] = field(default_factory=list)
    stage_id: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "summary": self.summary,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "sources": self.sources,
            "stage_id": self.stage_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Finding":
        return cls(
            id=data["id"],
            topic=data["topic"],
            summary=data["summary"],
            confidence=data["confidence"],
            evidence=data["evidence"],
            sources=data.get("sources", []),
            stage_id=data.get("stage_id", 0),
        )


@dataclass
class StageResult:
    """Stage 실행 결과."""
    stage_id: int
    status: StageStatus
    findings: list[Finding] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    error_message: Optional[str] = None
    execution_time: int = 0  # seconds
    retry_count: int = 0

    def to_dict(self) -> dict:
        return {
            "stage_id": self.stage_id,
            "status": self.status.value,
            "findings": [f.to_dict() for f in self.findings],
            "sources": self.sources,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StageResult":
        return cls(
            stage_id=data["stage_id"],
            status=StageStatus(data["status"]),
            findings=[Finding.from_dict(f) for f in data.get("findings", [])],
            sources=data.get("sources", []),
            error_message=data.get("error_message"),
            execution_time=data.get("execution_time", 0),
            retry_count=data.get("retry_count", 0),
        )


@dataclass
class Contradiction:
    """발견 간 모순."""
    finding_a: str  # Finding ID
    finding_b: str
    description: str
    severity: str  # minor, major, critical


@dataclass
class ValidationResult:
    """검증 결과."""
    consistency_score: float  # 0.0 ~ 1.0
    contradictions: list[Contradiction] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    cross_references: dict = field(default_factory=dict)  # finding_id -> supporting_ids

    def to_dict(self) -> dict:
        return {
            "consistency_score": self.consistency_score,
            "contradictions": [
                {
                    "finding_a": c.finding_a,
                    "finding_b": c.finding_b,
                    "description": c.description,
                    "severity": c.severity,
                }
                for c in self.contradictions
            ],
            "gaps": self.gaps,
            "recommendations": self.recommendations,
            "cross_references": self.cross_references,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ValidationResult":
        return cls(
            consistency_score=data["consistency_score"],
            contradictions=[
                Contradiction(**c) for c in data.get("contradictions", [])
            ],
            gaps=data.get("gaps", []),
            recommendations=data.get("recommendations", []),
            cross_references=data.get("cross_references", {}),
        )


@dataclass
class Decomposition:
    """연구 분해 결과."""
    research_goal: str
    stages: list[Stage]
    execution_order: list[list[int]]  # 병렬 그룹 [[1,2], [3,4], [5]]
    total_estimated_time: int  # minutes

    def to_dict(self) -> dict:
        return {
            "research_goal": self.research_goal,
            "stages": [s.to_dict() for s in self.stages],
            "execution_order": self.execution_order,
            "total_estimated_time": self.total_estimated_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Decomposition":
        return cls(
            research_goal=data["research_goal"],
            stages=[Stage.from_dict(s) for s in data["stages"]],
            execution_order=data["execution_order"],
            total_estimated_time=data["total_estimated_time"],
        )


@dataclass
class OrchestratorConfig:
    """오케스트레이터 설정."""
    research_goal: str
    depth: ResearchDepth = ResearchDepth.STANDARD
    mode: ExecutionMode = ExecutionMode.INTERACTIVE
    research_type: str = "technical"  # technical, academic, market, comparative
    language: str = "ko"
    output_dir: Path = field(default_factory=lambda: Path("./research-output"))

    # Guardrails
    max_stages: int = 10
    max_parallel_agents: int = 5
    timeout_per_stage: int = 30  # minutes
    total_timeout: int = 120  # minutes
    max_retries: int = 2

    def to_dict(self) -> dict:
        return {
            "research_goal": self.research_goal,
            "depth": self.depth.value,
            "mode": self.mode.value,
            "research_type": self.research_type,
            "language": self.language,
            "output_dir": str(self.output_dir),
            "max_stages": self.max_stages,
            "max_parallel_agents": self.max_parallel_agents,
            "timeout_per_stage": self.timeout_per_stage,
            "total_timeout": self.total_timeout,
            "max_retries": self.max_retries,
        }


@dataclass
class ExecutionStats:
    """실행 통계."""
    total_stages: int = 0
    completed_stages: int = 0
    failed_stages: int = 0
    skipped_stages: int = 0
    total_findings: int = 0
    total_sources: int = 0
    total_execution_time: int = 0  # seconds
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "total_stages": self.total_stages,
            "completed_stages": self.completed_stages,
            "failed_stages": self.failed_stages,
            "skipped_stages": self.skipped_stages,
            "total_findings": self.total_findings,
            "total_sources": self.total_sources,
            "total_execution_time": self.total_execution_time,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


@dataclass
class ResearchResult:
    """최종 연구 결과."""
    success: bool
    report_path: Optional[Path] = None
    data_path: Optional[Path] = None
    validation_result: Optional[ValidationResult] = None
    execution_stats: Optional[ExecutionStats] = None
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "report_path": str(self.report_path) if self.report_path else None,
            "data_path": str(self.data_path) if self.data_path else None,
            "validation_result": self.validation_result.to_dict() if self.validation_result else None,
            "execution_stats": self.execution_stats.to_dict() if self.execution_stats else None,
            "error_message": self.error_message,
        }
