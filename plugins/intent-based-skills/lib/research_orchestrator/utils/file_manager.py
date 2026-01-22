"""File management utilities for Research Orchestrator."""

import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..models import (
    Stage,
    Finding,
    StageResult,
    Decomposition,
    ValidationResult,
    StageStatus,
)


class FileManager:
    """연구 출력 파일 관리."""

    # 디렉토리 구조
    DIRECTORIES = [
        "stages",
        "diagrams",
        "validation",
    ]

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)

    def setup_directories(self) -> None:
        """출력 디렉토리 구조 생성."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for subdir in self.DIRECTORIES:
            (self.output_dir / subdir).mkdir(exist_ok=True)

    def save_decomposition(self, decomposition: Decomposition) -> Path:
        """분해 결과 저장."""
        path = self.output_dir / "stages" / "decomposition.json"
        path.write_text(
            json.dumps(decomposition.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def load_decomposition(self) -> Optional[Decomposition]:
        """분해 결과 로드."""
        path = self.output_dir / "stages" / "decomposition.json"
        if not path.exists():
            return None

        data = json.loads(path.read_text(encoding="utf-8"))
        return Decomposition.from_dict(data)

    def save_stage_result(self, result: StageResult, stage_name: str = "") -> Path:
        """Stage 결과 저장."""
        filename = f"stage-{result.stage_id}-data.json"
        path = self.output_dir / "stages" / filename

        path.write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def load_stage_result(self, stage_id: int) -> Optional[StageResult]:
        """Stage 결과 로드."""
        path = self.output_dir / "stages" / f"stage-{stage_id}-data.json"
        if not path.exists():
            return None

        data = json.loads(path.read_text(encoding="utf-8"))
        return StageResult.from_dict(data)

    def collect_stage_results(self) -> list[StageResult]:
        """모든 Stage 결과 수집."""
        results = []
        stages_dir = self.output_dir / "stages"

        for path in sorted(stages_dir.glob("stage-*-data.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                results.append(StageResult.from_dict(data))
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to load {path}: {e}")

        return results

    def merge_findings(self, results: list[StageResult]) -> list[Finding]:
        """모든 Finding 병합."""
        findings = []
        for result in results:
            findings.extend(result.findings)
        return findings

    def get_all_sources(self, results: list[StageResult]) -> list[str]:
        """모든 출처 수집 (중복 제거)."""
        sources = set()
        for result in results:
            sources.update(result.sources)
            for finding in result.findings:
                sources.update(finding.sources)
        return sorted(sources)

    def save_validation_result(self, validation: ValidationResult) -> Path:
        """검증 결과 저장."""
        path = self.output_dir / "validation" / "validation-result.json"
        path.write_text(
            json.dumps(validation.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def load_validation_result(self) -> Optional[ValidationResult]:
        """검증 결과 로드."""
        path = self.output_dir / "validation" / "validation-result.json"
        if not path.exists():
            return None

        data = json.loads(path.read_text(encoding="utf-8"))
        return ValidationResult.from_dict(data)

    def save_diagram(self, name: str, content: str) -> Path:
        """다이어그램 저장."""
        path = self.output_dir / "diagrams" / f"{name}.mmd"
        path.write_text(content, encoding="utf-8")
        return path

    def save_report(self, content: str) -> Path:
        """최종 리포트 저장."""
        path = self.output_dir / "RESEARCH-REPORT.md"
        path.write_text(content, encoding="utf-8")
        return path

    def save_research_data(self, data: dict) -> Path:
        """연구 데이터 JSON 저장."""
        path = self.output_dir / "research-data.json"
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def load_research_data(self) -> Optional[dict]:
        """연구 데이터 로드."""
        path = self.output_dir / "research-data.json"
        if not path.exists():
            return None

        return json.loads(path.read_text(encoding="utf-8"))

    def validate_against_schema(self, data: dict, schema_path: Path) -> tuple[bool, list[str]]:
        """JSON Schema 검증."""
        try:
            import jsonschema

            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            jsonschema.validate(data, schema)
            return True, []

        except ImportError:
            return True, ["jsonschema not installed, skipping validation"]

        except jsonschema.ValidationError as e:
            return False, [str(e.message)]

        except Exception as e:
            return False, [str(e)]

    def get_stage_data_files(self) -> list[Path]:
        """Stage 데이터 파일 목록 반환."""
        stages_dir = self.output_dir / "stages"
        return sorted(stages_dir.glob("stage-*-data.json"))

    def check_stage_completed(self, stage_id: int) -> bool:
        """Stage 완료 여부 확인."""
        result = self.load_stage_result(stage_id)
        return result is not None and result.status == StageStatus.COMPLETED

    def get_completion_status(self, total_stages: int) -> dict:
        """전체 완료 상태 반환."""
        completed = []
        pending = []
        failed = []

        for stage_id in range(1, total_stages + 1):
            result = self.load_stage_result(stage_id)
            if result is None:
                pending.append(stage_id)
            elif result.status == StageStatus.COMPLETED:
                completed.append(stage_id)
            elif result.status == StageStatus.FAILED:
                failed.append(stage_id)
            else:
                pending.append(stage_id)

        return {
            "completed": completed,
            "pending": pending,
            "failed": failed,
            "total": total_stages,
            "progress": len(completed) / total_stages if total_stages > 0 else 0,
        }

    def cleanup_partial_results(self) -> None:
        """부분 결과 정리 (실패한 실행 후)."""
        # 불완전한 파일 삭제 로직
        # 주의: 이 메서드는 신중하게 사용해야 함
        pass

    def export_summary(self) -> str:
        """현재 상태 요약 문자열 반환."""
        decomposition = self.load_decomposition()
        validation = self.load_validation_result()

        lines = ["=== Research Output Summary ==="]

        if decomposition:
            lines.append(f"Goal: {decomposition.research_goal}")
            lines.append(f"Stages: {len(decomposition.stages)}")

            status = self.get_completion_status(len(decomposition.stages))
            lines.append(f"Progress: {status['progress']*100:.0f}%")
            lines.append(f"Completed: {status['completed']}")
            lines.append(f"Failed: {status['failed']}")

        if validation:
            lines.append(f"Consistency Score: {validation.consistency_score:.2f}")
            lines.append(f"Contradictions: {len(validation.contradictions)}")
            lines.append(f"Gaps: {len(validation.gaps)}")

        report_path = self.output_dir / "RESEARCH-REPORT.md"
        if report_path.exists():
            lines.append(f"Report: {report_path}")

        return "\n".join(lines)
