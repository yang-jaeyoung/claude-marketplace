---
description: "스킬 실행 완료를 기록"
argument-hint: "<skill> <session> <duration> <total> <pass> <fail> <warn>"
allowed-tools: ["Bash"]
---
# /feedback-complete

스킬 실행 완료를 기록합니다.

## 사용법

```
/feedback-complete <skill> <session> <duration> <total> <pass> <fail> <warn>
```

## 파라미터

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| skill | O | 스킬 이름 |
| session | O | 세션 ID (feedback-start에서 반환된 값) |
| duration | O | 실행 시간 (초) |
| total | O | 전체 검증 항목 수 |
| pass | O | 통과 항목 수 |
| fail | O | 실패 항목 수 |
| warn | O | 경고 항목 수 |

## 예시

```
/feedback-complete vue-project-analyzer abc-123-def 45 10 9 1 0
```

## 실행 지시

다음 bash 명령을 실행하세요:

```bash
python ${CLAUDE_PLUGIN_ROOT}/lib/feedback_collector.py complete "$skill" "$session" "$duration" "$total" "$pass" "$fail" "$warn"
```

## 기록 내용

- 스킬 실행 시간
- 검증 결과 요약 (통과/실패/경고 건수)
- 세션 종료 타임스탬프
