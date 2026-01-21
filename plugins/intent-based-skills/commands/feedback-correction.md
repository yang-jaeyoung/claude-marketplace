---
description: "사용자 수정을 기록"
argument-hint: "<skill> <session> <file> <action> [section] [added] [removed]"
allowed-tools: ["Bash"]
---
# /feedback-correction

사용자가 스킬 출력물을 수정한 내용을 기록합니다.

## 사용법

```
/feedback-correction <skill> <session> <file> <action> [section] [added] [removed]
```

## 파라미터

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| skill | O | 스킬 이름 |
| session | O | 세션 ID |
| file | O | 수정된 파일 |
| action | O | 수정 행위 (modify/add/delete) |
| section | X | 수정된 섹션 |
| added | X | 추가된 줄 수 (기본: 0) |
| removed | X | 삭제된 줄 수 (기본: 0) |

## 예시

```
/feedback-correction vue-project-analyzer abc-123 ARCHITECTURE.md modify overview 5 2
/feedback-correction dotnet-project-analyzer xyz-789 analysis-data.json add dependencies 10 0
```

## 수정 행위 유형

| action | 설명 |
|--------|------|
| `modify` | 기존 내용 수정 |
| `add` | 새 내용 추가 |
| `delete` | 내용 삭제 |

## 실행 지시

다음 bash 명령을 실행하세요 (Windows/macOS/Linux 호환):

```bash
python -c "import os, sys; sys.path.insert(0, os.path.join(os.environ.get('CLAUDE_PLUGIN_ROOT', '.'), 'lib')); import feedback_collector; sys.argv=['fc','correction','$skill','$session','$file','$action','${section:-}','${added:-0}','${removed:-0}']; feedback_collector.main()"
```

## 분석 활용

반복적으로 동일 섹션이 수정되면 해당 섹션의 생성 가이드 개선이 필요하다는 신호입니다.
