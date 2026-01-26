"""Extract skill generation context from research results."""

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class VerificationItem:
    """검증 항목."""
    id: str
    name: str
    priority: str  # must, should, could
    validation_type: str  # auto, manual
    description: str = ""
    script: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "type": self.validation_type,
            "description": self.description,
            "script": self.script,
        }


@dataclass
class SuggestedPhase:
    """제안된 실행 단계."""
    name: str
    objective: str
    tools: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    duration_hint: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "objective": self.objective,
            "tools": self.tools,
            "outputs": self.outputs,
            "duration_hint": self.duration_hint,
        }


@dataclass
class SkillGenerationContext:
    """스킬 생성을 위한 추출된 컨텍스트."""
    skill_name: str
    domain: str
    research_hash: str
    research_date: str

    # 추출된 정보
    inferred_triggers: list[str] = field(default_factory=list)
    technical_constraints: list[str] = field(default_factory=list)
    verification_items: list[VerificationItem] = field(default_factory=list)
    suggested_phases: list[SuggestedPhase] = field(default_factory=list)
    best_practices: list[str] = field(default_factory=list)
    reference_standards: list[str] = field(default_factory=list)

    # 원본 리서치 경로
    research_report_path: Optional[Path] = None
    research_data_path: Optional[Path] = None

    def to_dict(self) -> dict:
        """JSON 직렬화를 위한 딕셔너리 변환."""
        return {
            "meta": {
                "skill_name": self.skill_name,
                "domain": self.domain,
                "research_hash": self.research_hash,
                "research_date": self.research_date,
            },
            "skill_generation_context": {
                "inferred_triggers": self.inferred_triggers,
                "technical_constraints": self.technical_constraints,
                "verification_items": [v.to_dict() for v in self.verification_items],
                "suggested_phases": [p.to_dict() for p in self.suggested_phases],
                "best_practices": self.best_practices,
                "reference_standards": self.reference_standards,
            },
            "source_paths": {
                "research_report": str(self.research_report_path) if self.research_report_path else None,
                "research_data": str(self.research_data_path) if self.research_data_path else None,
            },
        }

    def save(self, output_path: Path) -> None:
        """key-insights.json으로 저장."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path) -> "SkillGenerationContext":
        """key-insights.json에서 로드."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data["meta"]
        ctx = data["skill_generation_context"]

        return cls(
            skill_name=meta["skill_name"],
            domain=meta["domain"],
            research_hash=meta["research_hash"],
            research_date=meta["research_date"],
            inferred_triggers=ctx.get("inferred_triggers", []),
            technical_constraints=ctx.get("technical_constraints", []),
            verification_items=[
                VerificationItem(
                    id=v["id"],
                    name=v["name"],
                    priority=v["priority"],
                    validation_type=v["type"],
                    description=v.get("description", ""),
                    script=v.get("script", ""),
                )
                for v in ctx.get("verification_items", [])
            ],
            suggested_phases=[
                SuggestedPhase(
                    name=p["name"],
                    objective=p["objective"],
                    tools=p.get("tools", []),
                    outputs=p.get("outputs", []),
                    duration_hint=p.get("duration_hint", ""),
                )
                for p in ctx.get("suggested_phases", [])
            ],
            best_practices=ctx.get("best_practices", []),
            reference_standards=ctx.get("reference_standards", []),
            research_report_path=Path(data["source_paths"]["research_report"])
            if data["source_paths"].get("research_report")
            else None,
            research_data_path=Path(data["source_paths"]["research_data"])
            if data["source_paths"].get("research_data")
            else None,
        )


class ContextExtractor:
    """리서치 결과에서 스킬 생성 컨텍스트를 추출하는 클래스."""

    def __init__(self, skill_name: str, domain: str):
        self.skill_name = skill_name
        self.domain = domain
        self.research_hash = self._compute_domain_hash(domain)

    @staticmethod
    def _compute_domain_hash(domain: str) -> str:
        """도메인 문자열의 해시 생성."""
        return hashlib.sha256(domain.encode()).hexdigest()[:12]

    def extract(self, research_data_path: Path) -> SkillGenerationContext:
        """research-data.json에서 스킬 생성 컨텍스트 추출."""
        with open(research_data_path, "r", encoding="utf-8") as f:
            research_data = json.load(f)

        context = SkillGenerationContext(
            skill_name=self.skill_name,
            domain=self.domain,
            research_hash=self.research_hash,
            research_date=datetime.now().strftime("%Y-%m-%d"),
            research_data_path=research_data_path,
            research_report_path=research_data_path.parent / "RESEARCH-REPORT.md",
        )

        # 각 추출 메서드 호출
        context.inferred_triggers = self._extract_triggers(research_data)
        context.technical_constraints = self._extract_constraints(research_data)
        context.verification_items = self._extract_verification_items(research_data)
        context.suggested_phases = self._extract_phases(research_data)
        context.best_practices = self._extract_best_practices(research_data)
        context.reference_standards = self._extract_standards(research_data)

        return context

    def _extract_triggers(self, data: dict) -> list[str]:
        """사용 시나리오에서 트리거 추출."""
        triggers = []

        # synthesis.key_findings에서 추출
        synthesis = data.get("synthesis", {})
        for finding in synthesis.get("key_findings", []):
            # finding이 dict인 경우와 string인 경우 모두 처리
            if isinstance(finding, dict):
                topic = finding.get("topic", "")
                if topic:
                    triggers.append(f"{topic} 분석")
                    triggers.append(f"{topic} 검토")
            elif isinstance(finding, str):
                triggers.append(finding)

        # stages에서 추가 추출
        for stage in data.get("stages", []):
            stage_name = stage.get("name", "")
            if stage_name:
                triggers.append(stage_name)

        # 중복 제거 및 상위 5개
        seen = set()
        unique_triggers = []
        for t in triggers:
            if t and t not in seen:
                seen.add(t)
                unique_triggers.append(t)
            if len(unique_triggers) >= 5:
                break

        return unique_triggers

    def _extract_constraints(self, data: dict) -> list[str]:
        """기술적 제약사항 추출."""
        constraints = []

        # synthesis.limitations에서 추출
        synthesis = data.get("synthesis", {})
        for limitation in synthesis.get("limitations", []):
            if isinstance(limitation, str):
                constraints.append(limitation)
            elif isinstance(limitation, dict):
                desc = limitation.get("description", limitation.get("name", ""))
                if desc:
                    constraints.append(desc)

        # validation.gaps에서 추출
        validation = data.get("validation", {})
        for gap in validation.get("gaps", []):
            if isinstance(gap, str) and "필요" in gap:
                constraints.append(gap)

        return constraints[:5]

    def _extract_verification_items(self, data: dict) -> list[VerificationItem]:
        """검증 항목 추출."""
        items = []
        item_id = 1

        # synthesis.recommendations에서 검증 가능한 항목 추출
        synthesis = data.get("synthesis", {})
        for rec in synthesis.get("recommendations", []):
            if isinstance(rec, str):
                items.append(
                    VerificationItem(
                        id=f"VER-{item_id:03d}",
                        name=rec[:50],  # 50자 제한
                        priority="should",
                        validation_type="manual",
                        description=rec,
                    )
                )
                item_id += 1

        # key_findings에서 검증 항목 추출
        for finding in synthesis.get("key_findings", []):
            if isinstance(finding, dict):
                confidence = finding.get("confidence", 0)
                priority = "must" if confidence >= 0.8 else "should"
                items.append(
                    VerificationItem(
                        id=f"VER-{item_id:03d}",
                        name=finding.get("topic", "")[:50],
                        priority=priority,
                        validation_type="auto" if confidence >= 0.9 else "manual",
                        description=finding.get("summary", ""),
                    )
                )
                item_id += 1

        return items[:10]

    def _extract_phases(self, data: dict) -> list[SuggestedPhase]:
        """실행 단계 제안 추출."""
        phases = []

        # stages를 기반으로 phase 생성
        for i, stage in enumerate(data.get("stages", []), 1):
            phases.append(
                SuggestedPhase(
                    name=f"Phase {i}: {stage.get('name', 'Unknown')}",
                    objective=stage.get("objective", ""),
                    tools=self._infer_tools(stage),
                    outputs=stage.get("expected_outputs", []),
                )
            )

        # 최소 4개, 최대 6개 phase
        if len(phases) < 4:
            # 기본 phase 추가
            default_phases = [
                SuggestedPhase(name="Phase 1: 환경 확인", objective="실행 환경 및 전제조건 확인"),
                SuggestedPhase(name="Phase 2: 데이터 수집", objective="분석 대상 데이터 수집"),
                SuggestedPhase(name="Phase 3: 분석 실행", objective="핵심 분석 로직 실행"),
                SuggestedPhase(name="Phase 4: 결과 생성", objective="분석 결과 문서화"),
            ]
            phases = default_phases[:4]

        return phases[:6]

    def _extract_best_practices(self, data: dict) -> list[str]:
        """Best practices 추출."""
        practices = []

        # synthesis.conclusions에서 추출
        synthesis = data.get("synthesis", {})
        for conclusion in synthesis.get("conclusions", []):
            if isinstance(conclusion, str):
                practices.append(conclusion)
            elif isinstance(conclusion, dict):
                desc = conclusion.get("description", conclusion.get("summary", ""))
                if desc:
                    practices.append(desc)

        # patterns에서 추출
        for pattern in synthesis.get("patterns", []):
            if isinstance(pattern, str):
                practices.append(pattern)

        return practices[:5]

    def _extract_standards(self, data: dict) -> list[str]:
        """참조 표준 추출."""
        standards = []

        # 모든 sources 수집
        all_sources = []

        # stages의 sources
        for stage in data.get("stages", []):
            all_sources.extend(stage.get("sources", []))

        # synthesis의 sources
        synthesis = data.get("synthesis", {})
        all_sources.extend(synthesis.get("sources", []))

        # 표준/가이드라인 키워드 필터링
        standard_keywords = [
            "standard", "benchmark", "guide", "specification", "rfc",
            "iso", "nist", "owasp", "cis", "표준", "가이드", "규격",
        ]

        for source in all_sources:
            source_lower = source.lower() if isinstance(source, str) else ""
            if any(kw in source_lower for kw in standard_keywords):
                standards.append(source)

        return list(set(standards))[:5]

    def _infer_tools(self, stage: dict) -> list[str]:
        """Stage 정보에서 필요한 도구 추론."""
        tools = []
        stage_text = json.dumps(stage, ensure_ascii=False).lower()

        tool_keywords = {
            "Read": ["read", "파일", "file", "config", "설정"],
            "Glob": ["glob", "패턴", "pattern", "find", "찾기"],
            "Grep": ["grep", "search", "검색", "찾기"],
            "Bash": ["bash", "shell", "command", "명령", "실행"],
            "Write": ["write", "생성", "create", "output", "출력"],
            "WebSearch": ["web", "search", "검색", "조사"],
        }

        for tool, keywords in tool_keywords.items():
            if any(kw in stage_text for kw in keywords):
                tools.append(tool)

        return tools if tools else ["Read", "Glob", "Grep"]
