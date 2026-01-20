#!/usr/bin/env python3
"""
Feedback Loop - Event Collector CLI
스킬 실행 이벤트를 JSONL 형식으로 수집

Usage:
    python feedback_collector.py <command> <skill> [args...]

Commands:
    start <skill> [version] [input]
        실행 시작 - session_id 출력

    complete <skill> <session> <duration> <total> <pass> <fail> <warn>
        실행 완료

    failure <skill> <session> <check_id> <check_name> <priority> [error]
        검증 실패 기록

    correction <skill> <session> <file> <action> [section] [+lines] [-lines]
        사용자 수정 기록
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path


# Windows UTF-8 지원
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


class FeedbackCollector:
    """스킬 실행 피드백 수집기"""

    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        self.feedback_dir = Path(os.environ.get(
            "FEEDBACK_DIR",
            Path.home() / ".claude" / "feedback"
        ))
        self.logs_dir = self.feedback_dir / "logs" / skill_name
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_file(self) -> Path:
        """오늘 날짜의 로그 파일 경로 반환"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.logs_dir / f"{today}.jsonl"

    def _write_event(self, event: dict) -> None:
        """이벤트를 JSONL 파일에 추가"""
        event["timestamp"] = datetime.now().isoformat()
        event["skill_name"] = self.skill_name

        log_file = self._get_log_file()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def start(self, version: str = "1.0.0", input_summary: str = "") -> str:
        """실행 시작 기록, session_id 반환"""
        session_id = str(uuid.uuid4())[:8]

        self._write_event({
            "event_type": "execution_start",
            "session_id": session_id,
            "version": version,
            "input_summary": input_summary
        })

        return session_id

    def complete(
        self,
        session_id: str,
        duration: int,
        total: int,
        passed: int,
        failed: int,
        warnings: int
    ) -> None:
        """실행 완료 기록"""
        self._write_event({
            "event_type": "execution_complete",
            "session_id": session_id,
            "duration_seconds": duration,
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": failed,
            "warning_checks": warnings
        })

    def failure(
        self,
        session_id: str,
        check_id: str,
        check_name: str,
        priority: str,
        error_message: str = ""
    ) -> None:
        """검증 실패 기록"""
        self._write_event({
            "event_type": "verification_failure",
            "session_id": session_id,
            "check_id": check_id,
            "check_name": check_name,
            "priority": priority,
            "error_message": error_message
        })

    def correction(
        self,
        session_id: str,
        file_path: str,
        action: str,
        section: str = "",
        lines_added: int = 0,
        lines_removed: int = 0
    ) -> None:
        """사용자 수정 기록"""
        self._write_event({
            "event_type": "user_correction",
            "session_id": session_id,
            "file_path": file_path,
            "action": action,
            "section": section,
            "lines_added": lines_added,
            "lines_removed": lines_removed
        })


def cmd_start(args):
    """실행 시작 명령"""
    collector = FeedbackCollector(args.skill)
    session_id = collector.start(
        version=args.version,
        input_summary=args.input or ""
    )
    print(session_id)


def cmd_complete(args):
    """실행 완료 명령"""
    collector = FeedbackCollector(args.skill)
    collector.complete(
        session_id=args.session,
        duration=args.duration,
        total=args.total,
        passed=args.passed,
        failed=args.failed,
        warnings=args.warnings
    )


def cmd_failure(args):
    """검증 실패 명령"""
    collector = FeedbackCollector(args.skill)
    collector.failure(
        session_id=args.session,
        check_id=args.check_id,
        check_name=args.check_name,
        priority=args.priority,
        error_message=args.error or ""
    )


def cmd_correction(args):
    """사용자 수정 명령"""
    collector = FeedbackCollector(args.skill)
    collector.correction(
        session_id=args.session,
        file_path=args.file,
        action=args.action,
        section=args.section or "",
        lines_added=args.added or 0,
        lines_removed=args.removed or 0
    )


def main():
    parser = argparse.ArgumentParser(
        description="스킬 실행 이벤트를 JSONL 형식으로 수집",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start my-skill 1.0.0 "test input"
  %(prog)s complete my-skill abc-123 30 10 9 1 0
  %(prog)s failure my-skill abc-123 FILE-001 "파일 검증" must "파일 없음"
  %(prog)s correction my-skill abc-123 SKILL.md modify overview 5 2
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='서브 명령어')

    # start 명령
    start_parser = subparsers.add_parser('start', help='실행 시작')
    start_parser.add_argument('skill', help='스킬 이름')
    start_parser.add_argument('version', nargs='?', default='1.0.0', help='스킬 버전')
    start_parser.add_argument('input', nargs='?', default='', help='입력 요약')
    start_parser.set_defaults(func=cmd_start)

    # complete 명령
    complete_parser = subparsers.add_parser('complete', help='실행 완료')
    complete_parser.add_argument('skill', help='스킬 이름')
    complete_parser.add_argument('session', help='세션 ID')
    complete_parser.add_argument('duration', type=int, help='실행 시간 (초)')
    complete_parser.add_argument('total', type=int, help='전체 검증 항목 수')
    complete_parser.add_argument('passed', type=int, help='통과 항목 수')
    complete_parser.add_argument('failed', type=int, help='실패 항목 수')
    complete_parser.add_argument('warnings', type=int, help='경고 항목 수')
    complete_parser.set_defaults(func=cmd_complete)

    # failure 명령
    failure_parser = subparsers.add_parser('failure', help='검증 실패')
    failure_parser.add_argument('skill', help='스킬 이름')
    failure_parser.add_argument('session', help='세션 ID')
    failure_parser.add_argument('check_id', help='검증 ID (예: FILE-001)')
    failure_parser.add_argument('check_name', help='검증 이름')
    failure_parser.add_argument('priority', choices=['must', 'should', 'could'], help='우선순위')
    failure_parser.add_argument('error', nargs='?', default='', help='에러 메시지')
    failure_parser.set_defaults(func=cmd_failure)

    # correction 명령
    correction_parser = subparsers.add_parser('correction', help='사용자 수정')
    correction_parser.add_argument('skill', help='스킬 이름')
    correction_parser.add_argument('session', help='세션 ID')
    correction_parser.add_argument('file', help='수정된 파일')
    correction_parser.add_argument('action', choices=['modify', 'add', 'delete'], help='수정 행위')
    correction_parser.add_argument('section', nargs='?', default='', help='수정된 섹션')
    correction_parser.add_argument('added', nargs='?', type=int, default=0, help='추가된 줄 수')
    correction_parser.add_argument('removed', nargs='?', type=int, default=0, help='삭제된 줄 수')
    correction_parser.set_defaults(func=cmd_correction)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
