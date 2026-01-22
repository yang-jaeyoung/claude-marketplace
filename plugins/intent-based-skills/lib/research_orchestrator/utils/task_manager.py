"""Task tool wrapper for agent management."""

import time
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum


class AgentStatus(Enum):
    """에이전트 상태."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class AgentResult:
    """에이전트 실행 결과."""
    agent_id: str
    status: AgentStatus
    output_file: Optional[Path] = None
    result_data: Optional[dict] = None
    error_message: Optional[str] = None
    execution_time: int = 0  # seconds


@dataclass
class SpawnedAgent:
    """스폰된 에이전트 정보."""
    agent_id: str
    prompt: str
    output_file: Optional[Path]
    stage_id: Optional[int]
    start_time: float


class TaskManager:
    """Task 도구 래퍼 - Claude Code의 Task 도구와 연동.

    NOTE: 이 클래스는 Claude Code 환경에서 실행될 때
    실제 Task 도구 호출로 대체됩니다.
    스탠드얼론 실행 시에는 시뮬레이션 모드로 동작합니다.
    """

    def __init__(
        self,
        output_dir: Path,
        max_parallel: int = 5,
        poll_interval: int = 30,
    ):
        self.output_dir = Path(output_dir)
        self.max_parallel = max_parallel
        self.poll_interval = poll_interval
        self.spawned_agents: dict[str, SpawnedAgent] = {}
        self._agent_counter = 0

    def spawn_agent(
        self,
        prompt: str,
        agent_type: str = "general-purpose",
        stage_id: Optional[int] = None,
        run_in_background: bool = True,
    ) -> str:
        """에이전트 스폰.

        Args:
            prompt: 에이전트 프롬프트
            agent_type: 에이전트 유형
            stage_id: 관련 Stage ID (있는 경우)
            run_in_background: 백그라운드 실행 여부

        Returns:
            agent_id: 생성된 에이전트 ID

        NOTE: 실제 Claude Code 환경에서는 Task 도구를 호출합니다.
        이 구현은 오케스트레이터가 에이전트 관리를 추적하기 위한 것입니다.
        """
        self._agent_counter += 1
        agent_id = f"agent-{self._agent_counter:03d}"

        output_file = None
        if stage_id is not None:
            output_file = self.output_dir / "stages" / f"stage-{stage_id}-data.json"

        self.spawned_agents[agent_id] = SpawnedAgent(
            agent_id=agent_id,
            prompt=prompt,
            output_file=output_file,
            stage_id=stage_id,
            start_time=time.time(),
        )

        return agent_id

    def spawn_batch(
        self,
        prompts: list[tuple[str, int]],  # (prompt, stage_id)
        agent_type: str = "general-purpose",
    ) -> list[str]:
        """배치로 에이전트 스폰 (max_parallel 제한 적용).

        Args:
            prompts: (prompt, stage_id) 튜플 리스트
            agent_type: 에이전트 유형

        Returns:
            agent_ids: 생성된 에이전트 ID 리스트
        """
        agent_ids = []
        for prompt, stage_id in prompts[:self.max_parallel]:
            agent_id = self.spawn_agent(
                prompt=prompt,
                agent_type=agent_type,
                stage_id=stage_id,
                run_in_background=True,
            )
            agent_ids.append(agent_id)

        return agent_ids

    def wait_for_completion(
        self,
        agent_ids: list[str],
        timeout_minutes: int = 30,
        on_progress: Optional[Callable[[str, AgentStatus], None]] = None,
    ) -> list[AgentResult]:
        """에이전트 완료 대기.

        Args:
            agent_ids: 대기할 에이전트 ID 리스트
            timeout_minutes: 타임아웃 (분)
            on_progress: 진행 콜백 (agent_id, status)

        Returns:
            results: 에이전트 결과 리스트
        """
        results = []
        timeout_seconds = timeout_minutes * 60
        start_time = time.time()

        for agent_id in agent_ids:
            agent = self.spawned_agents.get(agent_id)
            if not agent:
                results.append(AgentResult(
                    agent_id=agent_id,
                    status=AgentStatus.FAILED,
                    error_message="Agent not found",
                ))
                continue

            # 출력 파일 존재 확인으로 완료 감지
            result = self._wait_for_agent(
                agent,
                timeout_seconds - (time.time() - start_time),
                on_progress,
            )
            results.append(result)

        return results

    def _wait_for_agent(
        self,
        agent: SpawnedAgent,
        remaining_timeout: float,
        on_progress: Optional[Callable],
    ) -> AgentResult:
        """단일 에이전트 완료 대기."""
        start_time = time.time()

        while time.time() - start_time < remaining_timeout:
            # 출력 파일 확인
            if agent.output_file and agent.output_file.exists():
                execution_time = int(time.time() - agent.start_time)

                if on_progress:
                    on_progress(agent.agent_id, AgentStatus.COMPLETED)

                return AgentResult(
                    agent_id=agent.agent_id,
                    status=AgentStatus.COMPLETED,
                    output_file=agent.output_file,
                    execution_time=execution_time,
                )

            if on_progress:
                on_progress(agent.agent_id, AgentStatus.RUNNING)

            time.sleep(self.poll_interval)

        # 타임아웃
        return AgentResult(
            agent_id=agent.agent_id,
            status=AgentStatus.TIMEOUT,
            error_message=f"Timeout after {remaining_timeout/60:.1f} minutes",
            execution_time=int(time.time() - agent.start_time),
        )

    def poll_output_files(
        self,
        pattern: str = "stage-*-data.json",
    ) -> list[Path]:
        """출력 파일 폴링."""
        stages_dir = self.output_dir / "stages"
        return list(stages_dir.glob(pattern))

    def get_agent_status(self, agent_id: str) -> AgentStatus:
        """에이전트 상태 조회."""
        agent = self.spawned_agents.get(agent_id)
        if not agent:
            return AgentStatus.FAILED

        if agent.output_file and agent.output_file.exists():
            return AgentStatus.COMPLETED

        return AgentStatus.RUNNING

    def cancel_agent(self, agent_id: str) -> bool:
        """에이전트 취소 (가능한 경우)."""
        if agent_id in self.spawned_agents:
            del self.spawned_agents[agent_id]
            return True
        return False

    def get_running_count(self) -> int:
        """실행 중인 에이전트 수."""
        return sum(
            1 for agent in self.spawned_agents.values()
            if not agent.output_file or not agent.output_file.exists()
        )

    def can_spawn_more(self) -> bool:
        """추가 스폰 가능 여부."""
        return self.get_running_count() < self.max_parallel
