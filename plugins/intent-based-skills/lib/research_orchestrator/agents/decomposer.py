"""Decomposer Agent - Phase 1: Research Decomposition."""

from pathlib import Path
from typing import Optional

from .base import BaseAgent, AgentResult, AgentStatus
from ..models import ResearchDepth, OrchestratorConfig
from ..config import DEPTH_CONFIG, RESEARCH_TYPE_CONFIG


class DecomposerAgent(BaseAgent):
    """연구 목표를 Stage로 분해하는 에이전트."""

    PROMPT_TEMPLATE_FILE = "decomposer.prompt.md"

    def __init__(
        self,
        prompts_dir: Path,
        output_dir: Path,
        config: OrchestratorConfig,
    ):
        super().__init__(prompts_dir, output_dir)
        self.config = config

    def build_context(self, **kwargs) -> dict:
        """Decomposer 컨텍스트 구성."""
        depth_config = DEPTH_CONFIG.get(
            self.config.depth.value,
            DEPTH_CONFIG["standard"]
        )
        min_stages, max_stages = depth_config["stage_range"]

        return {
            "RESEARCH_GOAL": self.config.research_goal,
            "RESEARCH_TYPE": self.config.research_type,
            "DEPTH": self.config.depth.value,
            "MIN_STAGES": min_stages,
            "MAX_STAGES": max_stages,
            "LANGUAGE": self.config.language,
        }

    def get_expected_outputs(self) -> list[str]:
        """예상 출력 파일."""
        return [
            "stages/decomposition.json",
            "diagrams/research-decomposition.mmd",
        ]

    def get_prompt(self, **kwargs) -> str:
        """실행 가능한 프롬프트 생성."""
        context = self.build_context(**kwargs)
        prompt = self.render_prompt(context)

        # 출력 디렉토리 정보 추가
        output_instructions = f"""

## 출력 위치

모든 파일은 다음 디렉토리에 저장하세요:
- 분해 결과: `{self.output_dir}/stages/decomposition.json`
- 다이어그램: `{self.output_dir}/diagrams/research-decomposition.mmd`

작업 완료 후 위 파일들이 생성되었는지 확인하세요.
"""
        return prompt + output_instructions

    def validate_decomposition(self, data: dict) -> tuple[bool, list[str]]:
        """분해 결과 검증."""
        errors = []

        # 필수 필드 확인
        required_fields = ["research_goal", "stages", "execution_order"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        if "stages" not in data:
            return False, errors

        stages = data["stages"]

        # Stage 수 확인
        depth_config = DEPTH_CONFIG.get(
            self.config.depth.value,
            DEPTH_CONFIG["standard"]
        )
        min_stages, max_stages = depth_config["stage_range"]

        if len(stages) < min_stages:
            errors.append(f"Too few stages: {len(stages)} < {min_stages}")
        if len(stages) > max_stages:
            errors.append(f"Too many stages: {len(stages)} > {max_stages}")

        # 각 Stage 검증
        for stage in stages:
            stage_errors = self._validate_stage(stage)
            errors.extend(stage_errors)

        # execution_order 검증
        if "execution_order" in data:
            order_errors = self._validate_execution_order(
                data["execution_order"],
                [s["stage_id"] for s in stages]
            )
            errors.extend(order_errors)

        return len(errors) == 0, errors

    def _validate_stage(self, stage: dict) -> list[str]:
        """단일 Stage 검증."""
        errors = []
        stage_id = stage.get("stage_id", "unknown")

        required = ["stage_id", "name", "objective", "questions"]
        for field in required:
            if field not in stage:
                errors.append(f"Stage {stage_id}: missing {field}")

        if "questions" in stage:
            if not isinstance(stage["questions"], list):
                errors.append(f"Stage {stage_id}: questions must be a list")
            elif len(stage["questions"]) < 2:
                errors.append(f"Stage {stage_id}: at least 2 questions required")
            elif len(stage["questions"]) > 5:
                errors.append(f"Stage {stage_id}: at most 5 questions allowed")

        return errors

    def _validate_execution_order(
        self,
        order: list[list[int]],
        stage_ids: list[int]
    ) -> list[str]:
        """실행 순서 검증."""
        errors = []

        # 모든 Stage가 포함되어 있는지 확인
        all_in_order = set()
        for group in order:
            all_in_order.update(group)

        missing = set(stage_ids) - all_in_order
        extra = all_in_order - set(stage_ids)

        if missing:
            errors.append(f"Stages missing in execution_order: {missing}")
        if extra:
            errors.append(f"Unknown stages in execution_order: {extra}")

        return errors
