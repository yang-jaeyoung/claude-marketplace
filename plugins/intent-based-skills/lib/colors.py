#!/usr/bin/env python3
"""
크로스 플랫폼 색상 출력 유틸리티
Windows/Linux/macOS에서 ANSI 색상 코드 지원
"""

import os
import sys
from typing import Optional


class Colors:
    """ANSI 색상 코드 관리 클래스"""

    # 색상 비활성화 조건:
    # 1. NO_COLOR 환경변수 설정
    # 2. 표준 출력이 터미널이 아님 (파이프 등)
    # 3. Windows에서 ANSICON 없이 실행 (Windows 10 이상은 지원)

    _enabled: Optional[bool] = None

    @classmethod
    def is_enabled(cls) -> bool:
        """색상 출력 가능 여부 확인"""
        if cls._enabled is not None:
            return cls._enabled

        # NO_COLOR 환경변수 체크 (https://no-color.org/)
        if os.environ.get('NO_COLOR'):
            cls._enabled = False
            return False

        # 터미널 여부 체크
        if not sys.stdout.isatty():
            cls._enabled = False
            return False

        # Windows 체크
        if sys.platform == 'win32':
            # Windows 10 이상은 기본 지원
            # ANSICON, ConEmu, Windows Terminal 등 지원 확인
            if os.environ.get('ANSICON') or os.environ.get('WT_SESSION'):
                cls._enabled = True
            else:
                # Windows 10 1511 이상에서 VT100 지원 활성화 시도
                try:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    # STD_OUTPUT_HANDLE = -11
                    # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                    handle = kernel32.GetStdHandle(-11)
                    mode = ctypes.c_ulong()
                    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                    kernel32.SetConsoleMode(handle, mode.value | 0x0004)
                    cls._enabled = True
                except Exception:
                    cls._enabled = False
        else:
            cls._enabled = True

        return cls._enabled

    @classmethod
    def disable(cls) -> None:
        """색상 출력 비활성화"""
        cls._enabled = False

    @classmethod
    def enable(cls) -> None:
        """색상 출력 강제 활성화"""
        cls._enabled = True

    # ANSI 색상 코드
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color (Reset)

    # 볼드
    BOLD = '\033[1m'

    @classmethod
    def red(cls, text: str) -> str:
        """빨간색 텍스트"""
        if cls.is_enabled():
            return f"{cls.RED}{text}{cls.NC}"
        return text

    @classmethod
    def green(cls, text: str) -> str:
        """초록색 텍스트"""
        if cls.is_enabled():
            return f"{cls.GREEN}{text}{cls.NC}"
        return text

    @classmethod
    def yellow(cls, text: str) -> str:
        """노란색 텍스트"""
        if cls.is_enabled():
            return f"{cls.YELLOW}{text}{cls.NC}"
        return text

    @classmethod
    def blue(cls, text: str) -> str:
        """파란색 텍스트"""
        if cls.is_enabled():
            return f"{cls.BLUE}{text}{cls.NC}"
        return text

    @classmethod
    def cyan(cls, text: str) -> str:
        """시안색 텍스트"""
        if cls.is_enabled():
            return f"{cls.CYAN}{text}{cls.NC}"
        return text

    @classmethod
    def bold(cls, text: str) -> str:
        """볼드 텍스트"""
        if cls.is_enabled():
            return f"{cls.BOLD}{text}{cls.NC}"
        return text


def print_colored(text: str, color: str = '', end: str = '\n') -> None:
    """색상이 적용된 텍스트 출력

    Args:
        text: 출력할 텍스트
        color: 색상 코드 (Colors.RED 등)
        end: 줄 끝 문자
    """
    if Colors.is_enabled() and color:
        print(f"{color}{text}{Colors.NC}", end=end)
    else:
        print(text, end=end)


# 테스트 실행
if __name__ == '__main__':
    # Windows에서 UTF-8 출력 설정
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass  # Python 3.6 이하

    print("색상 출력 테스트:")
    print(f"  색상 활성화: {Colors.is_enabled()}")
    print(f"  플랫폼: {sys.platform}")
    print()
    print(f"  {Colors.red('빨간색 텍스트')}")
    print(f"  {Colors.green('초록색 텍스트')}")
    print(f"  {Colors.yellow('노란색 텍스트')}")
    print(f"  {Colors.blue('파란색 텍스트')}")
    print(f"  {Colors.cyan('시안색 텍스트')}")
    print(f"  {Colors.bold('볼드 텍스트')}")
    print()
    print("  아이콘 테스트:")
    # Windows 호환 아이콘 사용
    check_mark = "[OK]" if sys.platform == 'win32' else "V"
    cross_mark = "[FAIL]" if sys.platform == 'win32' else "X"
    warn_mark = "[WARN]" if sys.platform == 'win32' else "!"
    info_mark = "[INFO]" if sys.platform == 'win32' else "i"
    print(f"    {Colors.green(check_mark)} 통과")
    print(f"    {Colors.red(cross_mark)} 실패")
    print(f"    {Colors.yellow(warn_mark)} 경고")
    print(f"    {Colors.blue(info_mark)} 정보")
