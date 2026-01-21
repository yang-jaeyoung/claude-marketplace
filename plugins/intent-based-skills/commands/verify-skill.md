---
description: "스킬 출력물을 검증"
argument-hint: "<skill> [--output-dir=./docs/architecture]"
allowed-tools: ["Bash", "Read", "Glob"]
---
# /verify-skill

스킬이 생성한 출력물을 검증합니다.

## 사용법

```
/verify-skill <skill> [--output-dir=./docs/architecture]
```

## 파라미터

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| skill | O | 검증할 스킬 이름 |
| --output-dir | X | 출력물 디렉토리 경로 (기본: ./docs/architecture) |

## 예시

```
/verify-skill vue-project-analyzer --output-dir=./docs/architecture
/verify-skill dotnet-project-analyzer
```

## 검증 항목

### MUST (필수)
- 필수 출력 파일 존재
- JSON/YAML 형식 유효성
- Mermaid 다이어그램 문법 유효성

### SHOULD (권장)
- 모든 항목이 올바르게 분류됨
- 필수 섹션 포함

### MANUAL (수동 확인)
- 분류가 실제 용도와 일치
- 의존성 그래프가 정확함

## 실행 지시

스킬별 검증 스크립트를 실행하세요 (Windows/macOS/Linux 호환):

```bash
# Python 검증기 (권장 - 크로스 플랫폼)
python -c "import os, sys; from pathlib import Path; root=Path(os.environ.get('CLAUDE_PLUGIN_ROOT','.')).parent/'$skill'/'verification'; sys.path.insert(0,str(root)); import verifier; verifier.main('${output_dir:-./docs/architecture}')"
```

> **Note**: 레거시 Bash 검증기 (`run-verification.sh`)는 Unix 시스템에서만 지원됩니다.

## 출력

검증 결과를 다음 형식으로 출력합니다:

```
=== 검증 결과 ===
MUST:   9/10 통과
SHOULD: 4/5 통과
COULD:  2/2 통과

실패 항목:
- [MUST] FILE-001: ARCHITECTURE.md 파일 없음
```
