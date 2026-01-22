"""Validator Agent - Phase 3: Cross-Verification."""

from pathlib import Path
from typing import Optional

from .base import BaseAgent, AgentResult, AgentStatus
from ..models import OrchestratorConfig


class ValidatorAgent(BaseAgent):
    """Stage 결과를 교차 검증하는 에이전트."""

    PROMPT_TEMPLATE_FILE = "validator.prompt.md"

    def __init__(
        self,
        prompts_dir: Path,
        output_dir: Path,
        config: OrchestratorConfig,
        stage_data_files: list[Path],
    ):
        super().__init__(prompts_dir, output_dir)
        self.config = config
        self.stage_data_files = stage_data_files

    def build_context(self, **kwargs) -> dict:
        """Validator 컨텍스트 구성."""
        files_list = "\n".join(f"- `{f}`" for f in self.stage_data_files)

        return {
            "RESEARCH_GOAL": self.config.research_goal,
            "TOTAL_STAGES": len(self.stage_data_files),
            "STAGE_DATA_FILES": files_list,
        }

    def get_expected_outputs(self) -> list[str]:
        """예상 출력 파일."""
        return [
            "validation/validation-result.json",
            "diagrams/validation-matrix.mmd",
            "validation/validation-report.md",
        ]

    def get_prompt(self, **kwargs) -> str:
        """실행 가능한 프롬프트 생성."""
        context = self.build_context(**kwargs)
        prompt = self.render_prompt(context)

        # 출력 디렉토리 정보 추가
        output_instructions = f"""

## 출력 위치

모든 파일은 다음 디렉토리에 저장하세요:
- 검증 결과 JSON: `{self.output_dir}/validation/validation-result.json`
- 검증 매트릭스: `{self.output_dir}/diagrams/validation-matrix.mmd`
- 검증 리포트: `{self.output_dir}/validation/validation-report.md`

**중요**: 일관성 점수(consistency_score)가 0.7 미만이면 경고를 표시하세요.
"""
        return prompt + output_instructions

    def validate_result(self, data: dict) -> tuple[bool, list[str]]:
        """검증 결과 검증."""
        errors = []

        # 필수 필드 확인
        required = ["consistency_score", "contradictions", "gaps"]
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # consistency_score 범위 확인
        score = data.get("consistency_score", 0)
        if not (0 <= score <= 1):
            errors.append(f"consistency_score must be 0-1, got {score}")

        # contradictions 검증
        contradictions = data.get("contradictions", [])
        for i, c in enumerate(contradictions):
            c_errors = self._validate_contradiction(c, i)
            errors.extend(c_errors)

        return len(errors) == 0, errors

    def _validate_contradiction(self, contradiction: dict, index: int) -> list[str]:
        """모순 항목 검증."""
        errors = []

        required = ["finding_a", "finding_b", "description", "severity"]
        for field in required:
            if field not in contradiction:
                errors.append(f"Contradiction {index}: missing {field}")

        severity = contradiction.get("severity", "")
        valid_severities = ["minor", "major", "critical"]
        if severity not in valid_severities:
            errors.append(f"Contradiction {index}: invalid severity '{severity}'")

        return errors

    def check_threshold(self, data: dict, threshold: float = 0.7) -> bool:
        """일관성 점수가 임계값 이상인지 확인."""
        return data.get("consistency_score", 0) >= threshold

    def get_critical_issues(self, data: dict) -> list[str]:
        """심각한 이슈 추출."""
        issues = []

        # Critical 모순 확인
        for c in data.get("contradictions", []):
            if c.get("severity") == "critical":
                issues.append(
                    f"Critical contradiction: {c.get('finding_a')} vs {c.get('finding_b')}"
                )

        # 주요 갭 확인
        for gap in data.get("gaps", [])[:3]:  # 상위 3개
            issues.append(f"Gap: {gap}")

        return issues
