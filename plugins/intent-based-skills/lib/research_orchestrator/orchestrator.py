"""Main Research Orchestrator - coordinates all phases."""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

from .models import (
    OrchestratorConfig,
    ResearchDepth,
    ExecutionMode,
    Stage,
    StageResult,
    StageStatus,
    Decomposition,
    ValidationResult,
    ExecutionStats,
    ResearchResult,
)
from .errors import (
    OrchestratorError,
    DecompositionError,
    ExecutionError,
    ValidationError,
    SynthesisError,
    TotalTimeoutError,
    GuardrailViolationError,
)
from .guardrails import Guardrails

from .agents.decomposer import DecomposerAgent
from .agents.scientist import ScientistAgent, ScientistAgentFactory
from .agents.validator import ValidatorAgent
from .agents.synthesizer import SynthesizerAgent

from .utils.file_manager import FileManager
from .utils.task_manager import TaskManager, AgentStatus as TaskAgentStatus
from .utils.checkpoint import CheckpointManager, Phase


class ResearchOrchestrator:
    """연구 오케스트레이터 - 4단계 워크플로우 조정.

    Phases:
        1. Decomposition: 연구 목표를 Stage로 분해
        2. Execution: 병렬 Scientist 에이전트로 각 Stage 실행
        3. Verification: 결과 교차 검증
        4. Synthesis: 최종 리포트 생성
    """

    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self.output_dir = config.output_dir

        # Managers
        self.file_manager = FileManager(self.output_dir)
        self.task_manager = TaskManager(
            self.output_dir,
            max_parallel=config.max_parallel_agents,
        )
        self.checkpoint_manager = CheckpointManager(self.output_dir)
        self.guardrails = Guardrails(config)

        # State
        self.decomposition: Optional[Decomposition] = None
        self.stage_results: list[StageResult] = []
        self.validation_result: Optional[ValidationResult] = None
        self.execution_stats = ExecutionStats()

        # Callbacks
        self.on_phase_start: Optional[Callable[[str], None]] = None
        self.on_phase_complete: Optional[Callable[[str, dict], None]] = None
        self.on_stage_complete: Optional[Callable[[int, StageResult], None]] = None

    def run(self) -> ResearchResult:
        """전체 연구 워크플로우 실행.

        Returns:
            ResearchResult: 실행 결과
        """
        try:
            # 초기화
            self.file_manager.setup_directories()
            self.guardrails.start()
            self.execution_stats.start_time = datetime.now()

            # Phase 1: Decomposition
            self._notify_phase_start("decomposition")
            self.decomposition = self._phase_1_decompose()
            self._notify_phase_complete("decomposition", {
                "stages": len(self.decomposition.stages),
            })

            if self._is_interactive():
                self._checkpoint("after_decomposition")

            # Phase 2: Execution
            self._notify_phase_start("execution")
            self.stage_results = self._phase_2_execute()
            self._notify_phase_complete("execution", {
                "completed": len([r for r in self.stage_results if r.status == StageStatus.COMPLETED]),
                "failed": len([r for r in self.stage_results if r.status == StageStatus.FAILED]),
            })

            if self._is_interactive():
                self._checkpoint("after_execution")

            # Phase 3: Verification
            self._notify_phase_start("verification")
            self.validation_result = self._phase_3_verify()
            self._notify_phase_complete("verification", {
                "consistency_score": self.validation_result.consistency_score,
            })

            if self._is_interactive():
                self._checkpoint("after_verification")

            # Phase 4: Synthesis
            self._notify_phase_start("synthesis")
            report_path, data_path = self._phase_4_synthesize()
            self._notify_phase_complete("synthesis", {
                "report_path": str(report_path),
            })

            # 완료
            self.execution_stats.end_time = datetime.now()
            self._update_execution_stats()

            return ResearchResult(
                success=True,
                report_path=report_path,
                data_path=data_path,
                validation_result=self.validation_result,
                execution_stats=self.execution_stats,
            )

        except TotalTimeoutError as e:
            return ResearchResult(
                success=False,
                error_message=str(e),
                execution_stats=self.execution_stats,
            )

        except GuardrailViolationError as e:
            return ResearchResult(
                success=False,
                error_message=str(e),
                execution_stats=self.execution_stats,
            )

        except OrchestratorError as e:
            return ResearchResult(
                success=False,
                error_message=str(e),
                execution_stats=self.execution_stats,
            )

    def _phase_1_decompose(self) -> Decomposition:
        """Phase 1: 연구 목표 분해."""
        # 기존 체크포인트 확인
        if self.checkpoint_manager.should_skip_decomposition():
            existing = self.file_manager.load_decomposition()
            if existing:
                return existing

        agent = DecomposerAgent(
            prompts_dir=self.prompts_dir,
            output_dir=self.output_dir,
            config=self.config,
        )

        prompt = agent.get_prompt()

        # 프롬프트를 실행 대기 상태로 저장
        self._save_pending_prompt("decomposer", prompt)

        # 결과 로드 시도 (이미 실행된 경우)
        decomposition = self.file_manager.load_decomposition()
        if decomposition:
            # 검증
            self.guardrails.check_stage_count(len(decomposition.stages))
            return decomposition

        raise DecompositionError(
            "Decomposition not completed. Please run the decomposer agent with the provided prompt.",
        )

    def _phase_2_execute(self) -> list[StageResult]:
        """Phase 2: Stage 병렬 실행."""
        if not self.decomposition:
            raise ExecutionError(
                "Decomposition required before execution",
                stage_id=0,
                error_code=ExecutionError.DEPENDENCY_FAILED,
            )

        # 체크포인트에서 미완료 Stage 확인
        pending_stages = self.checkpoint_manager.get_pending_stages(
            len(self.decomposition.stages)
        )

        results = []
        factory = ScientistAgentFactory(
            prompts_dir=self.prompts_dir,
            output_dir=self.output_dir,
            config=self.config,
        )

        # execution_order에 따라 배치 실행
        for group in self.decomposition.execution_order:
            # 그룹 내에서 미완료 Stage만 필터
            group_pending = [sid for sid in group if sid in pending_stages]

            if not group_pending:
                # 이미 완료된 Stage 결과 로드
                for stage_id in group:
                    result = self.file_manager.load_stage_result(stage_id)
                    if result:
                        results.append(result)
                continue

            # Guardrail 확인
            self.guardrails.check_total_timeout()

            # 배치 크기 제한
            batch_size = self.guardrails.get_batch_size(len(group_pending))
            batches = [group_pending[i:i+batch_size] for i in range(0, len(group_pending), batch_size)]

            for batch in batches:
                batch_results = self._execute_batch(factory, batch)
                results.extend(batch_results)

                # 체크포인트 업데이트
                for result in batch_results:
                    self.checkpoint_manager.update_stage_progress(
                        result.stage_id,
                        result.status == StageStatus.COMPLETED,
                    )

                    if self.on_stage_complete:
                        self.on_stage_complete(result.stage_id, result)

        return results

    def _execute_batch(
        self,
        factory: ScientistAgentFactory,
        stage_ids: list[int],
    ) -> list[StageResult]:
        """Stage 배치 실행."""
        results = []
        prompts = []

        # 프롬프트 생성
        for stage_id in stage_ids:
            stage = self._get_stage_by_id(stage_id)
            if not stage:
                continue

            agent = factory.create(stage)
            prompt = agent.get_prompt()
            prompts.append((prompt, stage_id))

            # 프롬프트 저장
            self._save_pending_prompt(f"scientist_stage_{stage_id}", prompt)

        # 결과 수집 (이미 실행된 경우)
        for stage_id in stage_ids:
            result = self.file_manager.load_stage_result(stage_id)
            if result:
                results.append(result)
            else:
                # 미완료 Stage
                results.append(StageResult(
                    stage_id=stage_id,
                    status=StageStatus.PENDING,
                ))

        return results

    def _phase_3_verify(self) -> ValidationResult:
        """Phase 3: 교차 검증."""
        stage_data_files = self.file_manager.get_stage_data_files()

        if not stage_data_files:
            raise ValidationError(
                "No stage results to validate",
                consistency_score=0,
            )

        agent = ValidatorAgent(
            prompts_dir=self.prompts_dir,
            output_dir=self.output_dir,
            config=self.config,
            stage_data_files=stage_data_files,
        )

        prompt = agent.get_prompt()
        self._save_pending_prompt("validator", prompt)

        # 결과 로드 시도
        validation = self.file_manager.load_validation_result()
        if validation:
            return validation

        # 기본 검증 결과 반환
        return ValidationResult(
            consistency_score=0.0,
            gaps=["Validation not completed"],
        )

    def _phase_4_synthesize(self) -> tuple[Path, Path]:
        """Phase 4: 결과 통합."""
        stage_data_files = self.file_manager.get_stage_data_files()

        agent = SynthesizerAgent(
            prompts_dir=self.prompts_dir,
            output_dir=self.output_dir,
            config=self.config,
            stage_data_files=stage_data_files,
            validation_result=self.validation_result,
            execution_stats=self.execution_stats,
        )

        prompt = agent.get_prompt()
        self._save_pending_prompt("synthesizer", prompt)

        # 결과 경로 반환
        report_path = self.output_dir / "RESEARCH-REPORT.md"
        data_path = self.output_dir / "research-data.json"

        return report_path, data_path

    def _get_stage_by_id(self, stage_id: int) -> Optional[Stage]:
        """Stage ID로 Stage 조회."""
        if not self.decomposition:
            return None

        for stage in self.decomposition.stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def _checkpoint(self, name: str) -> None:
        """Interactive 모드 체크포인트."""
        if not self._is_interactive():
            return

        phase_map = {
            "after_decomposition": Phase.DECOMPOSITION,
            "after_execution": Phase.EXECUTION,
            "after_verification": Phase.VERIFICATION,
        }

        phase = phase_map.get(name, Phase.INIT)
        completed = [r.stage_id for r in self.stage_results if r.status == StageStatus.COMPLETED]
        failed = [r.stage_id for r in self.stage_results if r.status == StageStatus.FAILED]

        self.checkpoint_manager.save(
            phase=phase,
            completed_stages=completed,
            failed_stages=failed,
        )

    def _is_interactive(self) -> bool:
        """Interactive 모드 여부."""
        return self.config.mode == ExecutionMode.INTERACTIVE

    def _save_pending_prompt(self, name: str, prompt: str) -> Path:
        """대기 중인 프롬프트 저장."""
        prompts_output_dir = self.output_dir / ".prompts"
        prompts_output_dir.mkdir(exist_ok=True)

        path = prompts_output_dir / f"{name}.prompt.md"
        path.write_text(prompt, encoding="utf-8")
        return path

    def _update_execution_stats(self) -> None:
        """실행 통계 업데이트."""
        if self.decomposition:
            self.execution_stats.total_stages = len(self.decomposition.stages)

        self.execution_stats.completed_stages = len([
            r for r in self.stage_results if r.status == StageStatus.COMPLETED
        ])
        self.execution_stats.failed_stages = len([
            r for r in self.stage_results if r.status == StageStatus.FAILED
        ])
        self.execution_stats.skipped_stages = len([
            r for r in self.stage_results if r.status == StageStatus.SKIPPED
        ])

        # Finding 수 계산
        all_findings = self.file_manager.merge_findings(self.stage_results)
        self.execution_stats.total_findings = len(all_findings)

        # 출처 수 계산
        all_sources = self.file_manager.get_all_sources(self.stage_results)
        self.execution_stats.total_sources = len(all_sources)

        # 총 실행 시간
        if self.execution_stats.start_time and self.execution_stats.end_time:
            delta = self.execution_stats.end_time - self.execution_stats.start_time
            self.execution_stats.total_execution_time = int(delta.total_seconds())

    def _notify_phase_start(self, phase: str) -> None:
        """Phase 시작 알림."""
        if self.on_phase_start:
            self.on_phase_start(phase)

    def _notify_phase_complete(self, phase: str, data: dict) -> None:
        """Phase 완료 알림."""
        if self.on_phase_complete:
            self.on_phase_complete(phase, data)

    def get_status(self) -> dict:
        """현재 상태 반환."""
        checkpoint = self.checkpoint_manager.load()

        return {
            "config": self.config.to_dict(),
            "guardrails": self.guardrails.get_status(),
            "checkpoint": checkpoint.to_dict() if checkpoint else None,
            "decomposition": self.decomposition.to_dict() if self.decomposition else None,
            "stage_results_count": len(self.stage_results),
            "validation": self.validation_result.to_dict() if self.validation_result else None,
            "stats": self.execution_stats.to_dict(),
        }

    def get_pending_prompts(self) -> list[Path]:
        """대기 중인 프롬프트 파일 목록."""
        prompts_dir = self.output_dir / ".prompts"
        if not prompts_dir.exists():
            return []
        return list(prompts_dir.glob("*.prompt.md"))

    def resume(self) -> ResearchResult:
        """중단된 실행 재개."""
        checkpoint = self.checkpoint_manager.load()
        if not checkpoint:
            return self.run()

        # 체크포인트에서 상태 복구
        self.decomposition = self.file_manager.load_decomposition()
        self.stage_results = self.file_manager.collect_stage_results()
        self.validation_result = self.file_manager.load_validation_result()

        # 해당 Phase부터 재개
        return self.run()
