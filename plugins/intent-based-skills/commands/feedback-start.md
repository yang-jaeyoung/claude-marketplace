---
name: feedback-start
description: "스킬 실행 피드백 수집을 시작하고 session_id를 반환합니다."
arguments:
  - name: skill
    description: "스킬 이름"
    required: true
  - name: version
    description: "스킬 버전 (기본값: 1.0.0)"
    required: false
  - name: input
    description: "입력 요약"
    required: false
---
# /feedback-start

스킬 실행 피드백 수집을 시작합니다.

## 사용법

```
/feedback-start <skill> [version] [input]
```

## 예시

```
/feedback-start vue-project-analyzer 1.0.0 "/path/to/project"
/feedback-start dotnet-project-analyzer
```

## 실행

```bash
python ${CLAUDE_PLUGIN_ROOT}/lib/feedback_collector.py start "$skill" ${version:-"1.0.0"} "${input:-}"
```

## 출력

session_id (UUID 형식)를 출력합니다. 이 ID는 이후 `feedback-complete`, `feedback-failure`, `feedback-correction` 명령어에서 사용됩니다.
