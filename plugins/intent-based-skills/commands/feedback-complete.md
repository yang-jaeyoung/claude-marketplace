---
name: feedback-complete
description: "스킬 실행 완료를 기록합니다."
arguments:
  - name: skill
    description: "스킬 이름"
    required: true
  - name: session
    description: "세션 ID (feedback-start에서 반환된 값)"
    required: true
  - name: duration
    description: "실행 시간 (초)"
    required: true
  - name: total
    description: "전체 검증 항목 수"
    required: true
  - name: pass
    description: "통과 항목 수"
    required: true
  - name: fail
    description: "실패 항목 수"
    required: true
  - name: warn
    description: "경고 항목 수"
    required: true
---
# /feedback-complete

스킬 실행 완료를 기록합니다.

## 사용법

```
/feedback-complete <skill> <session> <duration> <total> <pass> <fail> <warn>
```

## 예시

```
/feedback-complete vue-project-analyzer abc-123-def 45 10 9 1 0
```

## 실행

```bash
python ${CLAUDE_PLUGIN_ROOT}/lib/feedback_collector.py complete "$skill" "$session" "$duration" "$total" "$pass" "$fail" "$warn"
```

## 기록 내용

- 스킬 실행 시간
- 검증 결과 요약 (통과/실패/경고 건수)
- 세션 종료 타임스탬프
