"""Synthesizer Agent - Phase 4: Result Synthesis."""

from pathlib import Path
from typing import Optional
from datetime import datetime

from .base import BaseAgent, AgentResult, AgentStatus
from ..models import OrchestratorConfig, ValidationResult, ExecutionStats


class SynthesizerAgent(BaseAgent):
    """연구 결과를 통합하여 최종 리포트를 생성하는 에이전트."""

    PROMPT_TEMPLATE_FILE = "synthesizer.prompt.md"

    def __init__(
        self,
        prompts_dir: Path,
        output_dir: Path,
        config: OrchestratorConfig,
        stage_data_files: list[Path],
        validation_result: Optional[ValidationResult] = None,
        execution_stats: Optional[ExecutionStats] = None,
    ):
        super().__init__(prompts_dir, output_dir)
        self.config = config
        self.stage_data_files = stage_data_files
        self.validation_result = validation_result
        self.execution_stats = execution_stats

    def build_context(self, **kwargs) -> dict:
        """Synthesizer 컨텍스트 구성."""
        files_list = "\n".join(f"- `{f}`" for f in self.stage_data_files)

        # 통계 계산
        total_stages = len(self.stage_data_files)
        completed_stages = self.execution_stats.completed_stages if self.execution_stats else total_stages
        failed_stages = self.execution_stats.failed_stages if self.execution_stats else 0
        total_findings = self.execution_stats.total_findings if self.execution_stats else 0
        execution_time = self.execution_stats.total_execution_time if self.execution_stats else 0

        consistency_score = 0.0
        if self.validation_result:
            consistency_score = self.validation_result.consistency_score

        return {
            "RESEARCH_GOAL": self.config.research_goal,
            "RESEARCH_TYPE": self.config.research_type,
            "DEPTH": self.config.depth.value,
            "LANGUAGE": self.config.language,
            "STAGE_DATA_FILES": files_list,
            "DATE": datetime.now().strftime("%Y-%m-%d"),
            "TIMESTAMP": datetime.now().isoformat(),
            "TOTAL_STAGES": total_stages,
            "COMPLETED_STAGES": completed_stages,
            "FAILED_STAGES": failed_stages,
            "TOTAL_FINDINGS": total_findings,
            "CONSISTENCY_SCORE": f"{consistency_score:.2f}",
            "EXECUTION_TIME": execution_time,
        }

    def get_expected_outputs(self) -> list[str]:
        """예상 출력 파일."""
        return [
            "RESEARCH-REPORT.md",
            "research-data.json",
        ]

    def get_prompt(self, **kwargs) -> str:
        """실행 가능한 프롬프트 생성."""
        context = self.build_context(**kwargs)
        prompt = self.render_prompt(context)

        # 출력 디렉토리 정보 추가
        output_instructions = f"""

## 출력 위치

모든 파일은 다음 디렉토리에 저장하세요:
- 최종 리포트: `{self.output_dir}/RESEARCH-REPORT.md`
- 연구 데이터: `{self.output_dir}/research-data.json`

**중요**: 
- 리포트에 Executive Summary 섹션이 반드시 포함되어야 합니다
- 모든 Finding에 출처 참조가 있어야 합니다
- JSON의 execution_stats 필드를 포함하세요
"""
        return prompt + output_instructions

    def validate_result(self, data: dict) -> tuple[bool, list[str]]:
        """최종 결과 검증."""
        errors = []

        # 필수 필드 확인
        required = ["meta", "summary", "findings", "conclusions"]
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # meta 검증
        meta = data.get("meta", {})
        meta_required = ["research_goal", "research_type", "depth"]
        for field in meta_required:
            if field not in meta:
                errors.append(f"meta: missing {field}")

        # summary 검증
        summary = data.get("summary", {})
        if "key_insights" not in summary:
            errors.append("summary: missing key_insights")
        elif len(summary.get("key_insights", [])) < 2:
            errors.append("summary: at least 2 key_insights required")

        # findings 검증
        findings = data.get("findings", [])
        if len(findings) < 3:
            errors.append(f"At least 3 findings required, got {len(findings)}")

        for finding in findings:
            if not finding.get("sources"):
                errors.append(f"Finding {finding.get('id')}: missing sources")

        # conclusions 검증
        conclusions = data.get("conclusions", [])
        if not conclusions:
            errors.append("At least 1 conclusion required")

        return len(errors) == 0, errors

    def validate_report(self, report_content: str) -> tuple[bool, list[str]]:
        """Markdown 리포트 검증."""
        errors = []

        # 필수 섹션 확인
        required_sections = [
            "Executive Summary",
            "연구 배경",
            "주요 발견",
            "결론",
            "참고 자료",
        ]

        for section in required_sections:
            if section.lower() not in report_content.lower():
                # 영문/한글 모두 확인
                alt_names = {
                    "executive summary": ["요약", "개요"],
                    "연구 배경": ["research background", "background"],
                    "주요 발견": ["key findings", "findings"],
                    "결론": ["conclusion", "conclusions"],
                    "참고 자료": ["references", "sources", "참고문헌"],
                }

                found = False
                for alt in alt_names.get(section.lower(), []):
                    if alt in report_content.lower():
                        found = True
                        break

                if not found:
                    errors.append(f"Missing required section: {section}")

        return len(errors) == 0, errors
