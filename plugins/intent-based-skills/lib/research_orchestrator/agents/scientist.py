"""Scientist Agent - Phase 2: Stage Execution."""

from pathlib import Path
from typing import Optional

from .base import BaseAgent, AgentResult, AgentStatus
from ..models import Stage, OrchestratorConfig


class ScientistAgent(BaseAgent):
    """개별 Stage를 실행하는 연구 에이전트."""

    PROMPT_TEMPLATE_FILE = "scientist.prompt.md"

    def __init__(
        self,
        prompts_dir: Path,
        output_dir: Path,
        config: OrchestratorConfig,
        stage: Stage,
    ):
        super().__init__(prompts_dir, output_dir)
        self.config = config
        self.stage = stage

    def build_context(self, **kwargs) -> dict:
        """Scientist 컨텍스트 구성."""
        questions = "\n".join(f"- {q}" for q in self.stage.questions)

        return {
            "RESEARCH_GOAL": self.config.research_goal,
            "STAGE_ID": self.stage.stage_id,
            "STAGE_NAME": self.stage.name,
            "STAGE_OBJECTIVE": self.stage.objective,
            "QUESTIONS": questions,
            "LANGUAGE": self.config.language,
        }

    def get_expected_outputs(self) -> list[str]:
        """예상 출력 파일."""
        stage_id = self.stage.stage_id
        stage_name = self.sanitize_name(self.stage.name)

        return [
            f"stages/stage-{stage_id}-data.json",
            f"stages/stage-{stage_id}-{stage_name}.md",
        ]

    def get_prompt(self, **kwargs) -> str:
        """실행 가능한 프롬프트 생성."""
        context = self.build_context(**kwargs)
        prompt = self.render_prompt(context)

        stage_id = self.stage.stage_id
        stage_name = self.sanitize_name(self.stage.name)

        # 출력 디렉토리 정보 추가
        output_instructions = f"""

## 출력 위치

모든 파일은 다음 디렉토리에 저장하세요:
- 데이터 JSON: `{self.output_dir}/stages/stage-{stage_id}-data.json`
- 상세 리포트: `{self.output_dir}/stages/stage-{stage_id}-{stage_name}.md`

**중요**: JSON 파일의 `status` 필드를 반드시 "completed"로 설정하세요.
"""
        return prompt + output_instructions

    def validate_result(self, data: dict) -> tuple[bool, list[str]]:
        """Stage 결과 검증."""
        errors = []
        stage_id = self.stage.stage_id

        # 필수 필드 확인
        required = ["stage_id", "status", "findings"]
        for field in required:
            if field not in data:
                errors.append(f"Stage {stage_id}: missing {field}")

        if data.get("stage_id") != stage_id:
            errors.append(f"Stage ID mismatch: expected {stage_id}, got {data.get('stage_id')}")

        if data.get("status") != "completed":
            errors.append(f"Stage {stage_id}: status is not 'completed'")

        # Findings 검증
        findings = data.get("findings", [])
        if len(findings) < 3:
            errors.append(f"Stage {stage_id}: at least 3 findings required, got {len(findings)}")

        for i, finding in enumerate(findings):
            finding_errors = self._validate_finding(finding, stage_id, i)
            errors.extend(finding_errors)

        return len(errors) == 0, errors

    def _validate_finding(
        self,
        finding: dict,
        stage_id: int,
        index: int
    ) -> list[str]:
        """단일 Finding 검증."""
        errors = []
        finding_id = finding.get("id", f"F{stage_id}-{index+1:03d}")

        required = ["id", "topic", "summary", "confidence", "evidence"]
        for field in required:
            if field not in finding:
                errors.append(f"Finding {finding_id}: missing {field}")

        # confidence 범위 확인
        confidence = finding.get("confidence", 0)
        if not (0 <= confidence <= 1):
            errors.append(f"Finding {finding_id}: confidence must be 0-1, got {confidence}")

        # evidence 확인
        evidence = finding.get("evidence", [])
        if not evidence:
            errors.append(f"Finding {finding_id}: at least 1 evidence required")

        # sources 확인 (권장)
        sources = finding.get("sources", [])
        if not sources and confidence >= 0.7:
            errors.append(f"Finding {finding_id}: sources recommended for confidence >= 0.7")

        return errors


class ScientistAgentFactory:
    """Scientist 에이전트 팩토리."""

    def __init__(
        self,
        prompts_dir: Path,
        output_dir: Path,
        config: OrchestratorConfig,
    ):
        self.prompts_dir = prompts_dir
        self.output_dir = output_dir
        self.config = config

    def create(self, stage: Stage) -> ScientistAgent:
        """Stage에 대한 Scientist 에이전트 생성."""
        return ScientistAgent(
            prompts_dir=self.prompts_dir,
            output_dir=self.output_dir,
            config=self.config,
            stage=stage,
        )

    def create_batch(self, stages: list[Stage]) -> list[ScientistAgent]:
        """여러 Stage에 대한 에이전트 일괄 생성."""
        return [self.create(stage) for stage in stages]
