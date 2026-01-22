"""Checkpoint management for resumable execution."""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Phase(Enum):
    """실행 단계."""
    INIT = "init"
    DECOMPOSITION = "decomposition"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    SYNTHESIS = "synthesis"
    COMPLETED = "completed"


@dataclass
class Checkpoint:
    """체크포인트 데이터."""
    phase: Phase
    timestamp: str
    completed_stages: list[int]
    failed_stages: list[int]
    current_stage: Optional[int] = None
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "phase": self.phase.value,
            "timestamp": self.timestamp,
            "completed_stages": self.completed_stages,
            "failed_stages": self.failed_stages,
            "current_stage": self.current_stage,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Checkpoint":
        return cls(
            phase=Phase(data["phase"]),
            timestamp=data["timestamp"],
            completed_stages=data["completed_stages"],
            failed_stages=data["failed_stages"],
            current_stage=data.get("current_stage"),
            metadata=data.get("metadata"),
        )


class CheckpointManager:
    """체크포인트 관리 - 실행 상태 저장 및 복구."""

    CHECKPOINT_FILE = ".checkpoint.json"

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.checkpoint_path = self.output_dir / self.CHECKPOINT_FILE

    def save(
        self,
        phase: Phase,
        completed_stages: list[int],
        failed_stages: list[int],
        current_stage: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """체크포인트 저장."""
        checkpoint = Checkpoint(
            phase=phase,
            timestamp=datetime.now().isoformat(),
            completed_stages=completed_stages,
            failed_stages=failed_stages,
            current_stage=current_stage,
            metadata=metadata,
        )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path.write_text(
            json.dumps(checkpoint.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self) -> Optional[Checkpoint]:
        """체크포인트 로드."""
        if not self.checkpoint_path.exists():
            return None

        try:
            data = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
            return Checkpoint.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def clear(self) -> None:
        """체크포인트 삭제."""
        if self.checkpoint_path.exists():
            self.checkpoint_path.unlink()

    def exists(self) -> bool:
        """체크포인트 존재 여부."""
        return self.checkpoint_path.exists()

    def get_resumable_phase(self) -> Optional[Phase]:
        """재개 가능한 단계 반환."""
        checkpoint = self.load()
        if not checkpoint:
            return None

        return checkpoint.phase

    def get_pending_stages(self, total_stages: int) -> list[int]:
        """미완료 Stage 목록 반환."""
        checkpoint = self.load()
        if not checkpoint:
            return list(range(1, total_stages + 1))

        all_stages = set(range(1, total_stages + 1))
        completed = set(checkpoint.completed_stages)
        failed = set(checkpoint.failed_stages)

        # 실패한 Stage도 재시도 대상에 포함
        return sorted(all_stages - completed)

    def should_skip_decomposition(self) -> bool:
        """Decomposition 단계 스킵 여부."""
        checkpoint = self.load()
        if not checkpoint:
            return False

        return checkpoint.phase.value in [
            Phase.EXECUTION.value,
            Phase.VERIFICATION.value,
            Phase.SYNTHESIS.value,
            Phase.COMPLETED.value,
        ]

    def should_skip_execution(self) -> bool:
        """Execution 단계 스킵 여부."""
        checkpoint = self.load()
        if not checkpoint:
            return False

        return checkpoint.phase.value in [
            Phase.VERIFICATION.value,
            Phase.SYNTHESIS.value,
            Phase.COMPLETED.value,
        ]

    def update_stage_progress(
        self,
        stage_id: int,
        success: bool,
    ) -> None:
        """Stage 진행 상황 업데이트."""
        checkpoint = self.load()
        if not checkpoint:
            checkpoint = Checkpoint(
                phase=Phase.EXECUTION,
                timestamp=datetime.now().isoformat(),
                completed_stages=[],
                failed_stages=[],
            )

        if success:
            if stage_id not in checkpoint.completed_stages:
                checkpoint.completed_stages.append(stage_id)
            if stage_id in checkpoint.failed_stages:
                checkpoint.failed_stages.remove(stage_id)
        else:
            if stage_id not in checkpoint.failed_stages:
                checkpoint.failed_stages.append(stage_id)

        checkpoint.timestamp = datetime.now().isoformat()

        self.checkpoint_path.write_text(
            json.dumps(checkpoint.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_summary(self) -> str:
        """체크포인트 상태 요약."""
        checkpoint = self.load()
        if not checkpoint:
            return "No checkpoint found"

        lines = [
            f"Phase: {checkpoint.phase.value}",
            f"Timestamp: {checkpoint.timestamp}",
            f"Completed: {checkpoint.completed_stages}",
            f"Failed: {checkpoint.failed_stages}",
        ]

        if checkpoint.current_stage:
            lines.append(f"Current: {checkpoint.current_stage}")

        return "\n".join(lines)
