#!/usr/bin/env python3
"""
검증 스크립트 기본 클래스
모든 스킬의 verifier.py에서 상속받아 사용
"""

import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Windows에서 UTF-8 출력 설정
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass  # Python 3.6 이하

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from .colors import Colors


# Windows 호환 아이콘
def get_icons():
    """플랫폼에 따른 아이콘 반환"""
    if sys.platform == 'win32':
        return {
            'check': '[OK]',
            'cross': '[FAIL]',
            'warn': '[WARN]',
            'info': '[INFO]',
        }
    return {
        'check': 'V',
        'cross': 'X',
        'warn': '!',
        'info': 'i',
    }


ICONS = get_icons()


class Priority(Enum):
    """검증 항목 우선순위"""
    MUST = "must"      # 필수 - 실패 시 전체 실패
    SHOULD = "should"  # 권장 - 실패 시 경고
    COULD = "could"    # 선택 - 실패 시 정보


@dataclass
class CheckResult:
    """단일 검증 결과"""
    check_id: str
    name: str
    priority: Priority
    passed: bool
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class BaseVerifier(ABC):
    """검증 스크립트 기본 클래스

    하위 클래스에서 구현해야 할 메서드:
    - get_skill_name(): 스킬 이름 반환
    - run_checks(): 검증 로직 실행
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[CheckResult] = []
        self._current_section: str = ""

    @abstractmethod
    def get_skill_name(self) -> str:
        """스킬 이름 반환"""
        pass

    @abstractmethod
    def run_checks(self) -> None:
        """검증 로직 실행 - 하위 클래스에서 구현"""
        pass

    def section(self, name: str) -> None:
        """검증 섹션 시작"""
        self._current_section = name
        print()
        print(f"{Colors.blue(f'=== {name} ===')}")
        print()

    def run_check(
        self,
        check_id: str,
        name: str,
        priority: Priority,
        check_func: Callable[[], bool],
        error_msg: str = ""
    ) -> CheckResult:
        """단일 검증 항목 실행

        Args:
            check_id: 검증 ID (예: FILE-001)
            name: 검증 이름
            priority: 우선순위 (MUST, SHOULD, COULD)
            check_func: 검증 함수 (True 반환 시 통과)
            error_msg: 실패 시 메시지

        Returns:
            CheckResult 객체
        """
        if self.verbose:
            print(f"{Colors.blue(f'[{check_id}]')} {name}...")

        try:
            passed = check_func()
            message = "" if passed else error_msg
        except Exception as e:
            passed = False
            message = f"Exception: {e}"

        result = CheckResult(
            check_id=check_id,
            name=name,
            priority=priority,
            passed=passed,
            message=message
        )
        self.results.append(result)

        # 결과 출력
        if passed:
            print(f"  {Colors.green(ICONS['check'])} [{check_id}] {name}")
        else:
            if priority == Priority.MUST:
                print(f"  {Colors.red(ICONS['cross'])} [{check_id}] {name}")
                if message:
                    print(f"    {Colors.red(message)}")
            else:
                print(f"  {Colors.yellow(ICONS['warn'])} [{check_id}] {name}")
                if message:
                    print(f"    {Colors.yellow(message)}")

        return result

    # ============================================================
    # 공통 검증 헬퍼 메서드
    # ============================================================

    def check_file_exists(
        self,
        check_id: str,
        name: str,
        priority: Priority,
        file_path: Path,
        check_not_empty: bool = False
    ) -> CheckResult:
        """파일 존재 검증

        Args:
            check_id: 검증 ID
            name: 검증 이름
            priority: 우선순위
            file_path: 검증할 파일 경로
            check_not_empty: True면 파일이 비어있지 않은지도 확인
        """
        def check():
            if not file_path.exists():
                return False
            if check_not_empty and file_path.stat().st_size == 0:
                return False
            return True

        return self.run_check(
            check_id, name, priority, check,
            f"파일 없음: {file_path}"
        )

    def check_dir_exists(
        self,
        check_id: str,
        name: str,
        priority: Priority,
        dir_path: Path
    ) -> CheckResult:
        """디렉토리 존재 검증"""
        return self.run_check(
            check_id, name, priority,
            lambda: dir_path.is_dir(),
            f"디렉토리 없음: {dir_path}"
        )

    def check_json_valid(
        self,
        check_id: str,
        name: str,
        priority: Priority,
        file_path: Path
    ) -> CheckResult:
        """JSON 파일 유효성 검증"""
        def check():
            if not file_path.exists():
                return False
            try:
                with open(file_path, encoding='utf-8') as f:
                    json.load(f)
                return True
            except (json.JSONDecodeError, IOError):
                return False

        return self.run_check(
            check_id, name, priority, check,
            f"유효하지 않은 JSON: {file_path}"
        )

    def check_yaml_valid(
        self,
        check_id: str,
        name: str,
        priority: Priority,
        file_path: Path
    ) -> CheckResult:
        """YAML 파일 유효성 검증"""
        def check():
            if not file_path.exists():
                return False
            if not HAS_YAML:
                # PyYAML 없으면 기본적인 문법 검사만
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # 최소한의 YAML 문법 검사
                    return ':' in content
                except IOError:
                    return False
            try:
                with open(file_path, encoding='utf-8') as f:
                    yaml.safe_load(f)
                return True
            except Exception:
                return False

        return self.run_check(
            check_id, name, priority, check,
            f"유효하지 않은 YAML: {file_path}"
        )

    def check_file_contains(
        self,
        check_id: str,
        name: str,
        priority: Priority,
        file_path: Path,
        pattern: str,
        use_regex: bool = False
    ) -> CheckResult:
        """파일 내용 패턴 검증

        Args:
            check_id: 검증 ID
            name: 검증 이름
            priority: 우선순위
            file_path: 검증할 파일 경로
            pattern: 검색할 패턴 (문자열 또는 정규식)
            use_regex: True면 정규식으로 검색
        """
        def check():
            if not file_path.exists():
                return False
            try:
                content = file_path.read_text(encoding='utf-8')
                if use_regex:
                    import re
                    return bool(re.search(pattern, content, re.MULTILINE))
                return pattern in content
            except IOError:
                return False

        return self.run_check(
            check_id, name, priority, check,
            f"패턴 미발견: {pattern}"
        )

    def check_json_has_key(
        self,
        check_id: str,
        name: str,
        priority: Priority,
        file_path: Path,
        key_path: str
    ) -> CheckResult:
        """JSON 파일 키 존재 검증

        Args:
            key_path: 점으로 구분된 키 경로 (예: "meta.generated_at")
        """
        def check():
            if not file_path.exists():
                return False
            try:
                with open(file_path, encoding='utf-8') as f:
                    data = json.load(f)

                keys = key_path.split('.')
                current = data
                for key in keys:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return False
                return True
            except Exception:
                return False

        return self.run_check(
            check_id, name, priority, check,
            f"키 없음: {key_path}"
        )

    def check_json_array_not_empty(
        self,
        check_id: str,
        name: str,
        priority: Priority,
        file_path: Path,
        key_path: str
    ) -> CheckResult:
        """JSON 배열이 비어있지 않은지 검증"""
        def check():
            if not file_path.exists():
                return False
            try:
                with open(file_path, encoding='utf-8') as f:
                    data = json.load(f)

                keys = key_path.split('.')
                current = data
                for key in keys:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return False

                return isinstance(current, list) and len(current) > 0
            except Exception:
                return False

        return self.run_check(
            check_id, name, priority, check,
            f"빈 배열 또는 키 없음: {key_path}"
        )

    def check_mermaid_valid(
        self,
        check_id: str,
        name: str,
        priority: Priority,
        file_path: Path
    ) -> CheckResult:
        """Mermaid 파일 기본 문법 검증"""
        def check():
            if not file_path.exists():
                return False
            try:
                content = file_path.read_text(encoding='utf-8')
                # 첫 몇 줄에서 mermaid 다이어그램 타입 확인
                first_lines = '\n'.join(content.split('\n')[:5])
                valid_starts = ['flowchart', 'graph', 'sequenceDiagram',
                               'classDiagram', 'stateDiagram', 'gantt',
                               'pie', 'erDiagram', '%%']
                return any(first_lines.strip().startswith(s) for s in valid_starts)
            except IOError:
                return False

        return self.run_check(
            check_id, name, priority, check,
            f"유효하지 않은 Mermaid 문법: {file_path}"
        )

    # ============================================================
    # 결과 출력 및 종료
    # ============================================================

    def print_header(self) -> None:
        """검증 시작 헤더 출력"""
        skill_name = self.get_skill_name()
        print()
        print(Colors.blue("=" * 60))
        print(Colors.blue(f"  {skill_name} - Verification"))
        print(Colors.blue("=" * 60))
        print()

    def print_summary(self) -> None:
        """검증 결과 요약 출력"""
        passed = sum(1 for r in self.results if r.passed)
        failed_must = sum(1 for r in self.results
                         if not r.passed and r.priority == Priority.MUST)
        failed_should = sum(1 for r in self.results
                           if not r.passed and r.priority == Priority.SHOULD)
        failed_could = sum(1 for r in self.results
                          if not r.passed and r.priority == Priority.COULD)

        print()
        print(Colors.blue("=" * 60))
        print(Colors.blue("  검증 결과 요약"))
        print(Colors.blue("=" * 60))
        print()
        print(f"  {Colors.green('통과')}: {passed}")
        print(f"  {Colors.red('실패 (MUST)')}: {failed_must}")
        print(f"  {Colors.yellow('경고 (SHOULD)')}: {failed_should}")
        print(f"  {Colors.cyan('정보 (COULD)')}: {failed_could}")
        print()

        total = passed + failed_must
        if total > 0:
            rate = passed * 100 // total
            print(f"  통과율: {rate}%")
            print()

        if failed_must == 0:
            print(Colors.green(f"  {ICONS['check']} 전체 상태: PASS"))
        else:
            print(Colors.red(f"  {ICONS['cross']} 전체 상태: FAIL ({failed_must}개 필수 항목 실패)"))

    def get_exit_code(self) -> int:
        """종료 코드 반환 (MUST 실패 시 1, 아니면 0)"""
        failed_must = sum(1 for r in self.results
                         if not r.passed and r.priority == Priority.MUST)
        return 1 if failed_must > 0 else 0

    def run(self) -> int:
        """전체 검증 실행

        Returns:
            종료 코드 (0: 성공, 1: 실패)
        """
        self.print_header()
        self.run_checks()
        self.print_summary()
        return self.get_exit_code()
