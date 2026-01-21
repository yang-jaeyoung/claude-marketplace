#!/usr/bin/env python3
"""Cross-platform circular dependency checker for Vue projects.

Usage: python check_circular.py /path/to/vue-project
"""
import os
import sys
import subprocess
from pathlib import Path

# Windows UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def get_icons():
    """Return platform-appropriate icons."""
    if sys.platform == 'win32' and not os.environ.get('WT_SESSION'):
        return {
            'circular': '[CIRCULAR]',
            'check': '[OK]',
            'error': '[ERROR]',
            'info': '[INFO]',
            'graph': '[GRAPH]'
        }
    return {
        'circular': '🔄',
        'check': '✅',
        'error': '❌',
        'info': '📊',
        'graph': '📈'
    }


def check_npx_available():
    """Check if npx is available."""
    try:
        result = subprocess.run(
            ['npx', '--version'],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_madge_available(project_path: Path):
    """Check if madge is available, install if needed."""
    try:
        result = subprocess.run(
            ['npx', 'madge', '--version'],
            capture_output=True,
            timeout=30,
            cwd=project_path
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_circular_check(project_path: Path, src_path: Path):
    """Run madge circular dependency check."""
    icons = get_icons()

    try:
        result = subprocess.run(
            ['npx', 'madge', '--circular', '--extensions', 'ts,js,vue', str(src_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=project_path
        )

        output = result.stdout.strip()

        if result.returncode == 0 and not output:
            print(f"\n{icons['check']} 순환 의존성이 발견되지 않았습니다.")
            return True
        elif output:
            print(output)
            return False
        else:
            if result.stderr:
                print(f"{icons['error']} 오류: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"{icons['error']} 타임아웃: madge 실행이 너무 오래 걸립니다.")
        return False
    except Exception as e:
        print(f"{icons['error']} 오류: {e}")
        return False


def main():
    icons = get_icons()

    # Get project path from argument or use current directory
    project_path = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
    src_path = project_path / 'src'

    print(f"{icons['circular']} 순환 의존성 체크")
    print("=" * 32)
    print()

    # Check npx availability
    if not check_npx_available():
        print(f"{icons['error']} npx가 설치되어 있지 않습니다.")
        print("   Node.js를 설치하세요: https://nodejs.org/")
        sys.exit(1)

    # Check if src directory exists
    if not src_path.exists():
        print(f"{icons['error']} src 폴더를 찾을 수 없습니다: {src_path}")
        sys.exit(1)

    # Check madge availability
    print("madge 실행 중...")
    if not check_madge_available(project_path):
        print("madge 설치 중...")
        subprocess.run(
            ['npm', 'install', 'madge', '--save-dev'],
            cwd=project_path,
            capture_output=True
        )

    print()
    print(f"{icons['info']} 순환 의존성 결과:")
    print("-" * 19)

    success = run_circular_check(project_path, src_path)

    print()
    print(f"{icons['graph']} 의존성 그래프 생성 (선택사항):")
    print("   npx madge --image graph.svg src/")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
