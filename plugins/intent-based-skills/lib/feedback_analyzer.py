#!/usr/bin/env python3
"""
Feedback Loop - Analyzer
스킬 실행 로그를 분석하여 패턴을 감지하고 개선 제안을 생성
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional

# Windows UTF-8 지원
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# 크로스 플랫폼 아이콘
def get_icons():
    """플랫폼에 따른 아이콘 반환"""
    if sys.platform == 'win32' and not os.environ.get('WT_SESSION'):
        return {
            'check': '[OK]',
            'warn': '[WARN]',
            'high': '[HIGH]',
            'medium': '[MED]',
        }
    return {
        'check': '✅',
        'warn': '⚠️',
        'high': '🔴',
        'medium': '🟡',
    }

ICONS = get_icons()

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

FEEDBACK_DIR = Path(os.environ.get("FEEDBACK_DIR", Path.home() / ".claude" / "feedback"))
LOGS_DIR = FEEDBACK_DIR / "logs"
PLUGIN_DIR = Path(__file__).parent.parent  # plugin root


class FeedbackAnalyzer:
    def __init__(self, skill_name: str, period_days: int = 7):
        self.skill_name = skill_name
        self.period_days = period_days
        self.events: List[Dict[str, Any]] = []
        self._skill_info: Optional[Dict[str, Any]] = None

    def _get_project_root(self) -> Optional[Path]:
        """프레임워크 루트 디렉토리 탐색"""
        # plugin root -> project root (one level up from plugin)
        candidate = PLUGIN_DIR.parent
        if (candidate / "index.yaml").exists():
            return candidate
        # 환경 변수로 지정된 경우
        env_root = os.environ.get("SKILL_FRAMEWORK_ROOT")
        if env_root:
            return Path(env_root)
        return None

    def verify_skill_exists(self) -> Dict[str, Any]:
        """스킬 존재 여부 및 정보 확인"""
        result = {
            "exists": False,
            "skill_name": self.skill_name,
            "path": None,
            "type": None,
            "version": None,
            "message": ""
        }

        project_root = self._get_project_root()
        if not project_root:
            result["message"] = "프레임워크 루트를 찾을 수 없습니다."
            return result

        index_file = project_root / "index.yaml"
        if not index_file.exists():
            result["message"] = "index.yaml을 찾을 수 없습니다."
            return result

        if not HAS_YAML:
            content = index_file.read_text(encoding='utf-8')
            if f"name: {self.skill_name}" in content:
                result["exists"] = True
                result["message"] = f"스킬 '{self.skill_name}'이(가) index.yaml에 존재합니다."
            else:
                result["message"] = f"스킬 '{self.skill_name}'이(가) index.yaml에 없습니다."
            return result

        try:
            with open(index_file, encoding='utf-8') as f:
                index_data = yaml.safe_load(f)

            skills = index_data.get("skills", [])
            for skill in skills:
                if skill.get("name") == self.skill_name:
                    result["exists"] = True
                    result["path"] = skill.get("path")
                    result["type"] = skill.get("type")
                    result["version"] = skill.get("version")
                    result["message"] = f"스킬 '{self.skill_name}'이(가) 존재합니다."
                    self._skill_info = skill

                    skill_path = project_root / result["path"] if result["path"] else None
                    if skill_path and not skill_path.exists():
                        result["exists"] = False
                        result["message"] = f"스킬이 index.yaml에 등록되어 있으나 경로가 존재하지 않습니다: {result['path']}"
                    return result

            result["message"] = f"스킬 '{self.skill_name}'이(가) index.yaml에 등록되어 있지 않습니다."

        except Exception as e:
            result["message"] = f"index.yaml 파싱 오류: {e}"

        return result

    def load_events(self) -> None:
        """지정 기간의 이벤트 로드"""
        skill_dir = LOGS_DIR / self.skill_name
        if not skill_dir.exists():
            return

        cutoff = datetime.now() - timedelta(days=self.period_days)

        for log_file in skill_dir.glob("*.jsonl"):
            try:
                file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
                if file_date >= cutoff:
                    with open(log_file, encoding='utf-8') as f:
                        line_num = 0
                        for line in f:
                            line_num += 1
                            if line.strip():
                                try:
                                    self.events.append(json.loads(line))
                                except json.JSONDecodeError as e:
                                    logger.warning(f"Invalid JSON in {log_file}:{line_num}: {e}")
                                    continue
            except ValueError as e:
                logger.warning(f"Invalid date format in filename {log_file}: {e}")
                continue
            except IOError as e:
                logger.warning(f"Cannot read file {log_file}: {e}")
                continue

    def analyze_failures(self) -> Dict[str, Dict]:
        """반복 실패 패턴 분석"""
        failures = defaultdict(lambda: {"count": 0, "name": "", "priority": ""})

        for event in self.events:
            if event.get("event_type") == "verification_failure":
                check_id = event.get("check_id", "")
                failures[check_id]["count"] += 1
                failures[check_id]["name"] = event.get("check_name", "")
                failures[check_id]["priority"] = event.get("priority", "")

        return {k: v for k, v in failures.items() if v["count"] >= 3}

    def analyze_corrections(self) -> Dict[str, Dict]:
        """반복 수정 패턴 분석"""
        corrections = defaultdict(lambda: {"count": 0, "files": set()})

        for event in self.events:
            if event.get("event_type") == "user_correction":
                section = event.get("section", "unknown")
                corrections[section]["count"] += 1
                corrections[section]["files"].add(event.get("file_path", ""))

        result = {}
        for k, v in corrections.items():
            if v["count"] >= 3:
                result[k] = {"count": v["count"], "files": list(v["files"])}
        return result

    def analyze_performance(self) -> Dict[str, Any]:
        """성능 이상 분석"""
        durations = []

        for event in self.events:
            if event.get("event_type") == "execution_complete":
                dur = event.get("duration_seconds", 0)
                if dur > 0:
                    durations.append(dur)

        if len(durations) < 3:
            return {"anomalies": [], "avg": 0, "std": 0}

        avg = sum(durations) / len(durations)
        variance = sum((d - avg) ** 2 for d in durations) / len(durations)
        std = variance ** 0.5
        threshold = avg + 2 * std

        anomalies = [d for d in durations if d > threshold]

        return {"anomalies": anomalies, "avg": round(avg, 2), "std": round(std, 2)}

    def generate_suggestions(self) -> List[Dict[str, Any]]:
        """개선 제안 생성"""
        suggestions = []
        skill_status = self.verify_skill_exists()

        failures = self.analyze_failures()
        for check_id, data in failures.items():
            suggestion = {
                "type": "repeated_failure",
                "priority": "high" if data["priority"] == "must" else "medium",
                "target": check_id,
                "message": f"'{data['name']}' 검증이 {data['count']}회 실패. 검증 로직 또는 가이드 수정 필요.",
                "count": data["count"],
                "applicable_actions": []
            }

            if skill_status["exists"]:
                suggestion["applicable_actions"] = [
                    f"verification/checklist.yaml의 {check_id} 항목 검토",
                    f"SKILL.md의 관련 가이드 개선"
                ]
            else:
                suggestion["applicable_actions"] = [
                    f"스킬 '{self.skill_name}'이(가) 존재하지 않아 직접 적용 불가",
                    f"스킬 생성 또는 피드백 데이터 정리 필요"
                ]

            suggestions.append(suggestion)

        corrections = self.analyze_corrections()
        for section, data in corrections.items():
            suggestion = {
                "type": "repeated_correction",
                "priority": "medium",
                "target": section,
                "message": f"'{section}' 섹션이 {data['count']}회 수정됨. 생성 가이드 개선 필요.",
                "count": data["count"],
                "files": data["files"],
                "applicable_actions": []
            }

            if skill_status["exists"]:
                suggestion["applicable_actions"] = [
                    f"SKILL.md의 '{section}' 관련 Phase 가이드 보강",
                    f"출력 예시 추가 고려"
                ]
            else:
                suggestion["applicable_actions"] = [
                    f"스킬 '{self.skill_name}'이(가) 존재하지 않아 직접 적용 불가"
                ]

            suggestions.append(suggestion)

        return sorted(suggestions, key=lambda x: (0 if x["priority"] == "high" else 1, -x["count"]))

    def generate_application_guide(self) -> Dict[str, Any]:
        """개선 제안 적용 가이드 생성"""
        skill_status = self.verify_skill_exists()
        suggestions = self.generate_suggestions()

        guide = {
            "skill_name": self.skill_name,
            "skill_exists": skill_status["exists"],
            "skill_info": {
                "path": skill_status.get("path"),
                "type": skill_status.get("type"),
                "version": skill_status.get("version")
            },
            "total_suggestions": len(suggestions),
            "applicable": skill_status["exists"],
            "actions": [],
            "message": ""
        }

        if not skill_status["exists"]:
            guide["message"] = skill_status["message"]
            guide["actions"] = [
                {
                    "type": "create_skill",
                    "description": f"intent-skill-creator를 사용하여 '{self.skill_name}' 스킬 생성",
                    "command": f"# intent-skill-creator로 새 스킬 생성"
                },
                {
                    "type": "cleanup_data",
                    "description": "해당 스킬의 피드백 데이터 정리 (선택)",
                    "command": f"rm -rf ~/.claude/feedback/logs/{self.skill_name}"
                }
            ]
            return guide

        project_root = self._get_project_root()
        high_priority = [s for s in suggestions if s["priority"] == "high"]
        medium_priority = [s for s in suggestions if s["priority"] == "medium"]

        guide["message"] = f"{len(suggestions)}건의 개선 제안 (HIGH: {len(high_priority)}, MEDIUM: {len(medium_priority)})"

        for s in high_priority:
            if s["type"] == "repeated_failure":
                guide["actions"].append({
                    "type": "update_checklist",
                    "priority": "high",
                    "target": s["target"],
                    "description": f"검증 항목 '{s['target']}' 수정 - {s['count']}회 반복 실패",
                    "files": [
                        f"{skill_status['path']}/verification/checklist.yaml",
                        f"{skill_status['path']}/SKILL.md"
                    ]
                })

        for s in medium_priority:
            if s["type"] == "repeated_correction":
                guide["actions"].append({
                    "type": "update_guide",
                    "priority": "medium",
                    "target": s["target"],
                    "description": f"'{s['target']}' 섹션 가이드 개선 - {s['count']}회 반복 수정",
                    "files": [
                        f"{skill_status['path']}/SKILL.md"
                    ]
                })

        return guide

    def generate_report(self, format: str = "md") -> str:
        """분석 리포트 생성"""
        self.load_events()

        skill_status = self.verify_skill_exists()
        failures = self.analyze_failures()
        corrections = self.analyze_corrections()
        performance = self.analyze_performance()
        suggestions = self.generate_suggestions()

        total_executions = sum(1 for e in self.events if e.get("event_type") == "execution_start")

        if format == "json":
            return json.dumps({
                "skill": self.skill_name,
                "period_days": self.period_days,
                "total_executions": total_executions,
                "skill_status": skill_status,
                "failures": failures,
                "corrections": corrections,
                "performance": performance,
                "suggestions": suggestions
            }, indent=2, ensure_ascii=False)

        # Markdown 리포트
        skill_status_icon = ICONS['check'] if skill_status["exists"] else ICONS['warn']
        skill_status_text = skill_status["message"]

        report = f"""# {self.skill_name} 피드백 분석 리포트

**분석 기간**: 최근 {self.period_days}일
**총 실행**: {total_executions}회
**스킬 상태**: {skill_status_icon} {skill_status_text}

## 반복 실패 패턴

| Check ID | 이름 | 실패 횟수 | 우선순위 |
|----------|------|----------|----------|
"""
        for check_id, data in failures.items():
            report += f"| {check_id} | {data['name']} | {data['count']}회 | {data['priority'].upper()} |\n"

        if not failures:
            report += "| - | 반복 실패 없음 | - | - |\n"

        report += """
## 반복 수정 패턴

| 섹션 | 수정 횟수 | 관련 파일 |
|------|----------|----------|
"""
        for section, data in corrections.items():
            files = ", ".join(data["files"][:2])
            report += f"| {section} | {data['count']}회 | {files} |\n"

        if not corrections:
            report += "| - | 반복 수정 없음 | - |\n"

        report += f"""
## 성능 분석

- 평균 실행 시간: {performance['avg']}초
- 표준 편차: {performance['std']}초
- 이상 감지: {len(performance['anomalies'])}건

## 개선 제안

"""
        for i, s in enumerate(suggestions, 1):
            priority_icon = ICONS['high'] if s["priority"] == "high" else ICONS['medium']
            report += f"{i}. {priority_icon} **[{s['priority'].upper()}]** {s['message']}\n"
            if s.get("applicable_actions"):
                for action in s["applicable_actions"]:
                    report += f"   - {action}\n"

        if not suggestions:
            report += "현재 개선 제안 없음\n"

        return report


if __name__ == "__main__":
    def print_usage():
        print("""Usage: feedback_analyzer.py <command> [options]

Commands:
  analyze <skill> [--period=7] [--format=md]    분석 리포트 생성
  verify-skill <skill>                           스킬 존재 여부 확인
  apply <skill> [--dry-run]                      적용 가이드 생성
  report <skill> [--format=md|json]             리포트 생성

Examples:
  feedback_analyzer.py analyze my-skill --period=14 --format=json
  feedback_analyzer.py verify-skill my-skill
  feedback_analyzer.py apply my-skill --dry-run
""")
        sys.exit(1)

    if len(sys.argv) < 2:
        print_usage()

    command = sys.argv[1]

    # verify-skill 명령
    if command == "verify-skill":
        if len(sys.argv) < 3:
            print("Usage: feedback_analyzer.py verify-skill <skill>")
            sys.exit(1)
        skill = sys.argv[2]
        analyzer = FeedbackAnalyzer(skill)
        result = analyzer.verify_skill_exists()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["exists"] else 1)

    # apply 명령
    if command == "apply":
        if len(sys.argv) < 3:
            print("Usage: feedback_analyzer.py apply <skill> [--dry-run]")
            sys.exit(1)
        skill = sys.argv[2]
        dry_run = "--dry-run" in sys.argv

        analyzer = FeedbackAnalyzer(skill)
        analyzer.load_events()
        guide = analyzer.generate_application_guide()

        if dry_run:
            print("=== DRY RUN: 적용 가이드 미리보기 ===\n")

        print(json.dumps(guide, indent=2, ensure_ascii=False))
        sys.exit(0 if guide["applicable"] else 1)

    # analyze 또는 report 명령
    if command in ["analyze", "report"]:
        if len(sys.argv) < 3:
            print(f"Usage: feedback_analyzer.py {command} <skill> [options]")
            sys.exit(1)
        skill = sys.argv[2]
    else:
        # 기본: 스킬 이름으로 리포트 생성
        skill = command

    period = 7
    fmt = "md"

    for arg in sys.argv[2:]:
        if arg.startswith("--period="):
            period = int(arg.split("=")[1])
        elif arg.startswith("--format="):
            fmt = arg.split("=")[1]

    analyzer = FeedbackAnalyzer(skill, period)
    print(analyzer.generate_report(fmt))
