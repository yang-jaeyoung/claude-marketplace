#!/usr/bin/env python3
"""Cross-platform unused Vue component detector.

Usage: python find_unused.py /path/to/vue-project
"""
import os
import sys
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
            'search': '[SEARCH]',
            'warn': '[WARN]',
            'error': '[ERROR]',
            'note': '[NOTE]'
        }
    return {
        'search': '🔍',
        'warn': '⚠️',
        'error': '❌',
        'note': '⚠️'
    }


def find_unused_components(src_path: Path) -> list:
    """Find potentially unused Vue components."""
    components_path = src_path / 'components'

    if not components_path.exists():
        return None

    # Get all Vue component files
    vue_files = list(components_path.rglob('*.vue'))

    if not vue_files:
        return []

    # Get all source files to search in
    all_src_files = (
        list(src_path.rglob('*.vue')) +
        list(src_path.rglob('*.ts')) +
        list(src_path.rglob('*.js')) +
        list(src_path.rglob('*.tsx')) +
        list(src_path.rglob('*.jsx'))
    )

    unused = []

    for component in vue_files:
        filename = component.stem  # filename without .vue extension
        import_count = 0

        for src_file in all_src_files:
            # Skip self
            if src_file == component:
                continue

            try:
                content = src_file.read_text(encoding='utf-8', errors='ignore')
                if filename in content:
                    import_count += 1
                    break  # Found at least one reference
            except Exception:
                continue

        if import_count == 0:
            unused.append(component)

    return unused


def main():
    icons = get_icons()

    # Get project path from argument or use current directory
    project_path = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
    src_path = project_path / 'src'

    print(f"{icons['search']} 미사용 컴포넌트 후보 탐지")
    print("=" * 32)
    print()

    # Check if src directory exists
    if not src_path.exists():
        print(f"{icons['error']} src 폴더를 찾을 수 없습니다: {src_path}")
        sys.exit(1)

    unused = find_unused_components(src_path)

    if unused is None:
        print(f"{icons['error']} components 폴더를 찾을 수 없습니다.")
        sys.exit(1)

    if not unused:
        print("미사용 컴포넌트 후보가 없습니다.")
    else:
        for component in unused:
            # Show relative path from project root
            try:
                rel_path = component.relative_to(project_path)
            except ValueError:
                rel_path = component
            print(f"{icons['warn']}  {rel_path}")

    print()
    print("=" * 32)
    print(f"총 미사용 후보: {len(unused) if unused else 0} 개")
    print()
    print(f"{icons['note']}  주의: 동적 import, global 등록 컴포넌트는 미감지될 수 있음")

    sys.exit(0)


if __name__ == '__main__':
    main()
