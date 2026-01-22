"""Guardrails for AUTO mode safety."""

from datetime import datetime, timedelta
from typing import Optional

from .models import OrchestratorConfig, ExecutionMode
from .errors import GuardrailViolationError, TotalTimeoutError


class Guardrails:
    """AUTO 모드 가드레일 관리."""

    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.start_time: Optional[datetime] = None
        self.stage_count = 0
        self.parallel_agents = 0

    def start(self) -> None:
        """가드레일 타이머 시작."""
        self.start_time = datetime.now()

    def check_stage_count(self, count: int) -> None:
        """Stage 수 검증.

        Raises:
            GuardrailViolationError: max_stages 초과 시
        """
        if count > self.config.max_stages:
            raise GuardrailViolationError(
                guardrail_name="max_stages",
                current_value=count,
                limit=self.config.max_stages,
            )

    def check_parallel_agents(self, count: int) -> None:
        """병렬 에이전트 수 검증.

        Returns:
            count > max_parallel_agents면 max_parallel_agents 반환
        """
        if count > self.config.max_parallel_agents:
            raise GuardrailViolationError(
                guardrail_name="max_parallel_agents",
                current_value=count,
                limit=self.config.max_parallel_agents,
            )

    def get_batch_size(self, requested: int) -> int:
        """배치 크기 계산 (max_parallel_agents 이하로 제한)."""
        return min(requested, self.config.max_parallel_agents)

    def check_total_timeout(self) -> None:
        """전체 시간 초과 검증.

        Raises:
            TotalTimeoutError: total_timeout 초과 시
        """
        if not self.start_time:
            return

        elapsed = datetime.now() - self.start_time
        elapsed_minutes = int(elapsed.total_seconds() / 60)

        if elapsed_minutes > self.config.total_timeout:
            raise TotalTimeoutError(
                elapsed_minutes=elapsed_minutes,
                limit_minutes=self.config.total_timeout,
            )

    def get_remaining_time(self) -> int:
        """남은 시간 (분) 반환."""
        if not self.start_time:
            return self.config.total_timeout

        elapsed = datetime.now() - self.start_time
        elapsed_minutes = int(elapsed.total_seconds() / 60)
        return max(0, self.config.total_timeout - elapsed_minutes)

    def get_stage_timeout(self) -> int:
        """Stage별 타임아웃 (분) 반환."""
        remaining = self.get_remaining_time()
        return min(self.config.timeout_per_stage, remaining)

    def should_skip_optional(self) -> bool:
        """선택적 Stage 스킵 여부.

        남은 시간이 20% 미만이면 선택적 Stage 스킵 권장.
        """
        remaining = self.get_remaining_time()
        threshold = self.config.total_timeout * 0.2
        return remaining < threshold

    def is_auto_mode(self) -> bool:
        """AUTO 모드 여부."""
        return self.config.mode == ExecutionMode.AUTO

    def get_status(self) -> dict:
        """현재 가드레일 상태."""
        remaining = self.get_remaining_time()
        return {
            "mode": self.config.mode.value,
            "elapsed_minutes": self.config.total_timeout - remaining,
            "remaining_minutes": remaining,
            "max_stages": self.config.max_stages,
            "max_parallel_agents": self.config.max_parallel_agents,
            "should_skip_optional": self.should_skip_optional(),
        }
