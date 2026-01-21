# Cross-Platform Development Guide

Claude Code 플러그인 개발 시 macOS/Linux와 Windows 호환성을 보장하기 위한 가이드입니다.

## 피해야 할 패턴

### 1. Shell 변수 직접 사용

```bash
# ❌ Windows에서 작동하지 않음
python ${CLAUDE_PLUGIN_ROOT}/scripts/my_script.py
python "$CLAUDE_PLUGIN_ROOT/scripts/my_script.py"
```

Windows CMD와 PowerShell에서는 `${VAR}` 또는 `$VAR` 형태의 환경변수 확장이 기본적으로 작동하지 않습니다.

### 2. Unix 전용 Shell 명령어

```bash
# ❌ Windows에서 작동하지 않음
find src -name "*.vue" | wc -l
mkdir -p .caw/archives
cp -r source/ dest/
grep -r "pattern" .
```

### 3. Single Quote Echo

```json
// ❌ Windows PowerShell에서 문제 발생
{
  "type": "command",
  "command": "echo '{\"key\": \"value\"}'"
}
```

---

## 권장 패턴

### 1. Python Inline 패턴 (환경변수 처리)

```bash
# ✅ 크로스 플랫폼 호환
python -c "import os, sys; sys.path.insert(0, os.path.join(os.environ.get('CLAUDE_PLUGIN_ROOT', '.'), 'lib')); import my_module; my_module.main()"
```

**장점:**
- Python의 `os.environ.get()`으로 환경변수 안전하게 처리
- `os.path.join()`으로 경로 구분자 자동 처리
- Windows/macOS/Linux 모두 작동

### 2. Prompt 타입 Hook (단순 메시지)

```json
// ✅ 크로스 플랫폼 호환
{
  "type": "prompt",
  "prompt": "Plugin is active. Use /command to start."
}
```

**사용 사례:**
- SessionStart 메시지
- 단순 알림
- 사용자 안내

### 3. pathlib.Path 사용 (Python 코드)

```python
# ✅ 크로스 플랫폼 호환
from pathlib import Path

project_root = Path(__file__).parent.parent
config_file = project_root / "config" / "settings.json"
```

### 4. Windows UTF-8 지원

```python
# Python 스크립트 상단에 추가
import os
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
```

### 5. 플랫폼별 아이콘

```python
def get_icons():
    """플랫폼에 따른 아이콘 반환"""
    if sys.platform == 'win32' and not os.environ.get('WT_SESSION'):
        # Windows Terminal이 아닌 경우 이모지 미지원
        return {'check': '[OK]', 'warn': '[WARN]', 'error': '[ERROR]'}
    return {'check': '✅', 'warn': '⚠️', 'error': '❌'}
```

---

## 명령어 대체표

| Unix 명령어 | Windows 대체 | 크로스 플랫폼 Python |
|------------|-------------|---------------------|
| `find . -name "*.vue"` | `dir /s /b *.vue` | `Path('.').rglob('*.vue')` |
| `wc -l file.txt` | `find /c /v "" file.txt` | `len(Path('file.txt').read_text().splitlines())` |
| `mkdir -p dir/sub` | `mkdir dir\sub` | `Path('dir/sub').mkdir(parents=True, exist_ok=True)` |
| `cp -r src/ dest/` | `xcopy src dest /E` | `shutil.copytree('src', 'dest')` |
| `grep -r pattern .` | `findstr /s pattern *` | `for f in Path('.').rglob('*'): if pattern in f.read_text()` |

---

## Hook 설정 가이드

### SessionStart

```json
{
  "SessionStart": [
    {
      "matcher": "startup",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Your welcome message here"
        }
      ]
    }
  ]
}
```

### PreToolUse (스크립트 실행)

```json
{
  "PreToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "type": "command",
          "command": "python -c \"import os, sys; sys.path.insert(0, os.path.join(os.environ.get('CLAUDE_PLUGIN_ROOT', '.'), 'hooks', 'scripts')); import my_validator; my_validator.main()\""
        }
      ]
    }
  ]
}
```

---

## 테스트 가이드

### 로컬 테스트

```bash
# 모든 테스트 실행
cd plugins/your-plugin
python -m pytest tests/ -v

# 크로스 플랫폼 테스트만
python -m pytest tests/test_cross_platform.py -v
```

### CI/CD (GitHub Actions)

```yaml
name: Cross-Platform Tests

on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11']

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Run Tests
        run: python -m pytest tests/ -v
```

---

## 체크리스트

플러그인 배포 전 확인 사항:

- [ ] Shell 스크립트(.sh)를 Python으로 변환
- [ ] `${CLAUDE_PLUGIN_ROOT}` 사용 시 Python inline 패턴 적용
- [ ] SessionStart hook에 prompt 타입 사용
- [ ] Python 스크립트에 Windows UTF-8 지원 추가
- [ ] pathlib.Path 사용하여 경로 처리
- [ ] 크로스 플랫폼 테스트 추가
- [ ] Windows/macOS/Linux에서 수동 테스트 완료
