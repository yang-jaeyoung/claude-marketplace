#!/usr/bin/env python3
"""
Research Orchestrator - 검증 스크립트
연구 결과가 스키마와 품질 기준을 충족하는지 검증

Usage:
    python verifier.py --output-dir <research_output_directory>

Example:
    python verifier.py --output-dir ./research-output
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# 상위 lib 모듈 임포트
from ..colors import Colors
from ..verifier_base import BaseVerifier, Priority


class ResearchVerifier(BaseVerifier):
    """연구 오케스트레이터 결과 검증기"""

    # 연구 깊이별 단계 수 기준
    DEPTH_STAGE_COUNTS = {
        "quick": (2, 3),
        "standard": (4, 6),
        "deep": (7, 10)
    }

    def __init__(self, output_dir: Path, verbose: bool = False):
        super().__init__(verbose)
        self.output_dir = output_dir
        self.research_data: Optional[Dict[str, Any]] = None

    def get_skill_name(self) -> str:
        return "Research Orchestrator"

    def run_checks(self) -> None:
        """모든 검증 실행"""
        self._load_research_data()
        self._verify_file_existence()
        self._verify_schema()
        self._verify_content()
        self._verify_quality()
        self._verify_diagrams()

    def _load_research_data(self) -> None:
        """research-data.json 로드"""
        data_file = self.output_dir / "research-data.json"
        if data_file.exists():
            try:
                with open(data_file, encoding='utf-8') as f:
                    self.research_data = json.load(f)
            except Exception:
                self.research_data = None

    def _verify_file_existence(self) -> None:
        """파일 존재 검증"""
        self.section("파일 존재 검증")

        # FILE-001: RESEARCH-REPORT.md
        self.check_file_exists(
            "FILE-001", "RESEARCH-REPORT.md 존재", Priority.MUST,
            self.output_dir / "RESEARCH-REPORT.md"
        )

        # FILE-002: research-data.json
        self.check_file_exists(
            "FILE-002", "research-data.json 존재", Priority.MUST,
            self.output_dir / "research-data.json"
        )

        # FILE-003: stages/ 디렉토리
        self.check_dir_exists(
            "FILE-003", "stages/ 디렉토리 존재", Priority.MUST,
            self.output_dir / "stages"
        )

        # FILE-004: diagrams/ 디렉토리
        self.check_dir_exists(
            "FILE-004", "diagrams/ 디렉토리 존재", Priority.SHOULD,
            self.output_dir / "diagrams"
        )

        # FILE-005: 단계별 리포트 존재
        stages_dir = self.output_dir / "stages"
        if stages_dir.is_dir():
            stage_files = list(stages_dir.glob("stage-*.md"))
            self.run_check(
                "FILE-005", "단계별 리포트 존재", Priority.MUST,
                lambda: len(stage_files) >= 1,
                f"발견: {len(stage_files)}개 (최소 1개 필요)"
            )

    def _verify_schema(self) -> None:
        """스키마 검증"""
        self.section("스키마 검증")

        data_file = self.output_dir / "research-data.json"

        # SCHEMA-001: JSON 유효성
        self.check_json_valid(
            "SCHEMA-001", "research-data.json JSON 유효성", Priority.MUST,
            data_file
        )

        # SCHEMA-002: 필수 섹션 존재
        required_keys = ["meta", "stages", "validation", "synthesis"]
        for key in required_keys:
            self.check_json_has_key(
                f"SCHEMA-00{required_keys.index(key) + 2}",
                f"'{key}' 섹션 존재", Priority.MUST,
                data_file, key
            )

        # SCHEMA-006: meta 필수 필드
        if self.research_data:
            meta_fields = ["generated_at", "skill_version", "research_goal", "research_depth"]
            for field in meta_fields:
                key_path = f"meta.{field}"
                self.check_json_has_key(
                    f"SCHEMA-META-{meta_fields.index(field) + 1}",
                    f"meta.{field} 존재", Priority.MUST,
                    data_file, key_path
                )

    def _verify_content(self) -> None:
        """내용 검증"""
        self.section("내용 검증")

        report_file = self.output_dir / "RESEARCH-REPORT.md"
        data_file = self.output_dir / "research-data.json"

        # CONTENT-001: Executive Summary
        self.check_file_contains(
            "CONTENT-001", "Executive Summary 섹션 존재", Priority.MUST,
            report_file, r"(Executive Summary|요약)", use_regex=True
        )

        # CONTENT-002: Methodology
        self.check_file_contains(
            "CONTENT-002", "Methodology 섹션 존재", Priority.MUST,
            report_file, r"(Methodology|방법론)", use_regex=True
        )

        # CONTENT-003: Conclusions
        self.check_file_contains(
            "CONTENT-003", "Conclusions 섹션 존재", Priority.MUST,
            report_file, r"(Conclusions|결론)", use_regex=True
        )

        # CONTENT-004: 교차 검증 수행됨
        def check_validation_performed():
            if not self.research_data:
                return False
            validation = self.research_data.get("validation", {})
            return validation.get("performed", False) is True

        self.run_check(
            "CONTENT-004", "교차 검증 수행됨", Priority.MUST,
            check_validation_performed,
            "validation.performed가 true여야 합니다"
        )

        # CONTENT-005: 핵심 발견 존재
        self.check_json_array_not_empty(
            "CONTENT-005", "핵심 발견 존재", Priority.MUST,
            data_file, "synthesis.key_findings"
        )

        # CONTENT-006: 결론 존재
        self.check_json_array_not_empty(
            "CONTENT-006", "결론 존재", Priority.MUST,
            data_file, "synthesis.conclusions"
        )

    def _verify_quality(self) -> None:
        """품질 검증"""
        self.section("품질 검증")

        # QUALITY-001: 단계 커버리지
        def check_stage_coverage():
            if not self.research_data:
                return False

            meta = self.research_data.get("meta", {})
            depth = meta.get("research_depth", "standard")
            stages = self.research_data.get("stages", [])

            min_count, max_count = self.DEPTH_STAGE_COUNTS.get(depth, (4, 6))
            return min_count <= len(stages) <= max_count

        if self.research_data:
            meta = self.research_data.get("meta", {})
            depth = meta.get("research_depth", "standard")
            stages = self.research_data.get("stages", [])
            min_count, max_count = self.DEPTH_STAGE_COUNTS.get(depth, (4, 6))

            self.run_check(
                "QUALITY-001", "단계 커버리지", Priority.SHOULD,
                check_stage_coverage,
                f"depth={depth}, 실제={len(stages)}, 기대={min_count}-{max_count}"
            )

        # QUALITY-002: 일관성 점수
        def check_consistency_score():
            if not self.research_data:
                return False
            validation = self.research_data.get("validation", {})
            score = validation.get("consistency_score", 0)
            return score >= 0.7

        if self.research_data:
            validation = self.research_data.get("validation", {})
            score = validation.get("consistency_score", 0)

            self.run_check(
                "QUALITY-002", "일관성 점수 >= 0.7", Priority.SHOULD,
                check_consistency_score,
                f"실제 점수: {score:.2f}"
            )

        # QUALITY-003: 모순 해결
        def check_contradictions_resolved():
            if not self.research_data:
                return True  # 데이터 없으면 통과

            validation = self.research_data.get("validation", {})
            contradictions = validation.get("contradictions", [])

            if not contradictions:
                return True

            return all(c.get("resolved", False) for c in contradictions)

        self.run_check(
            "QUALITY-003", "모든 모순 해결됨", Priority.SHOULD,
            check_contradictions_resolved,
            "해결되지 않은 모순이 있습니다"
        )

        # QUALITY-004: 모든 단계 완료
        def check_all_stages_completed():
            if not self.research_data:
                return False

            stages = self.research_data.get("stages", [])
            if not stages:
                return False

            return all(
                s.get("status") in ["completed", "partial"]
                for s in stages
            )

        self.run_check(
            "QUALITY-004", "모든 단계 완료됨", Priority.MUST,
            check_all_stages_completed,
            "실패하거나 스킵된 단계가 있습니다"
        )

    def _verify_diagrams(self) -> None:
        """다이어그램 검증"""
        self.section("다이어그램 검증")

        diagrams_dir = self.output_dir / "diagrams"

        if not diagrams_dir.is_dir():
            self.run_check(
                "DIAGRAM-000", "다이어그램 디렉토리 존재", Priority.SHOULD,
                lambda: False,
                "diagrams/ 디렉토리가 없습니다"
            )
            return

        # DIAGRAM-001: research-decomposition.mmd
        decomp_file = diagrams_dir / "research-decomposition.mmd"
        if decomp_file.exists():
            self.check_mermaid_valid(
                "DIAGRAM-001", "research-decomposition.mmd Mermaid 유효성",
                Priority.SHOULD, decomp_file
            )
        else:
            self.run_check(
                "DIAGRAM-001", "research-decomposition.mmd 존재", Priority.SHOULD,
                lambda: False, "파일이 없습니다"
            )

        # DIAGRAM-002: validation-matrix.mmd
        matrix_file = diagrams_dir / "validation-matrix.mmd"
        if matrix_file.exists():
            self.check_mermaid_valid(
                "DIAGRAM-002", "validation-matrix.mmd Mermaid 유효성",
                Priority.SHOULD, matrix_file
            )
        else:
            self.run_check(
                "DIAGRAM-002", "validation-matrix.mmd 존재", Priority.SHOULD,
                lambda: False, "파일이 없습니다"
            )

        # DIAGRAM-003: findings-synthesis.mmd (선택)
        synthesis_file = diagrams_dir / "findings-synthesis.mmd"
        if synthesis_file.exists():
            self.check_mermaid_valid(
                "DIAGRAM-003", "findings-synthesis.mmd Mermaid 유효성",
                Priority.COULD, synthesis_file
            )

    def print_header(self) -> None:
        """헤더 출력 오버라이드"""
        print()
        print(Colors.blue("=" * 60))
        print(Colors.blue("  Research Orchestrator - Verification Report"))
        print(Colors.blue("=" * 60))
        print()
        print(f"  Output Directory: {self.output_dir}")

        if self.research_data:
            meta = self.research_data.get("meta", {})
            print(f"  Research Goal: {meta.get('research_goal', 'N/A')[:50]}...")
            print(f"  Research Depth: {meta.get('research_depth', 'N/A')}")
            print(f"  Generated At: {meta.get('generated_at', 'N/A')}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="연구 오케스트레이터 결과 검증"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="연구 결과가 저장된 디렉토리 경로"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="상세 출력"
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    if not output_dir.is_dir():
        print(Colors.red(f"ERROR: 디렉토리를 찾을 수 없음: {output_dir}"))
        sys.exit(1)

    verifier = ResearchVerifier(output_dir, verbose=args.verbose)
    exit_code = verifier.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
