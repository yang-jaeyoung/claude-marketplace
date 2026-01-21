---
description: "스킬 실행 피드백 수집을 시작하고 session_id를 반환"
argument-hint: "<skill> [version] [input]"
allowed-tools: ["Bash"]
---
# /feedback-start

피드백 수집 세션을 시작합니다.

## 사용법

```
/feedback-start <skill> [version] [input]
```

## 파라미터

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| skill | O | 스킬 이름 |
| version | X | 스킬 버전 (기본: 1.0.0) |
| input | X | 입력 요약 |

## 예시

```
/feedback-start vue-project-analyzer 1.0.0 "/path/to/project"
/feedback-start dotnet-project-analyzer
```

## 실행 지시

다음 bash 명령을 실행하세요 (Windows/macOS/Linux 호환):

```bash
python -c "import os, sys; sys.path.insert(0, os.path.join(os.environ.get('CLAUDE_PLUGIN_ROOT', '.'), 'lib')); import feedback_collector; sys.argv=['fc','start','$skill','${version:-1.0.0}','${input:-}']; feedback_collector.main()"
```

## 출력

session_id (UUID 형식)를 출력합니다. 이 ID는 이후 `feedback-complete`, `feedback-failure`, `feedback-correction` 명령어에서 사용됩니다.
