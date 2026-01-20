---
name: feedback-failure
description: "검증 실패를 기록합니다."
arguments:
  - name: skill
    description: "스킬 이름"
    required: true
  - name: session
    description: "세션 ID"
    required: true
  - name: check_id
    description: "검증 ID (예: FILE-001)"
    required: true
  - name: check_name
    description: "검증 이름"
    required: true
  - name: priority
    description: "우선순위 (must/should/could)"
    required: true
  - name: error
    description: "에러 메시지"
    required: false
---
# /feedback-failure

검증 실패를 기록합니다.

## 사용법

```
/feedback-failure <skill> <session> <check_id> <check_name> <priority> [error]
```

## 예시

```
/feedback-failure vue-project-analyzer abc-123 STRUCT-001 "버전 명시" must "Vue 버전을 찾을 수 없음"
/feedback-failure dotnet-project-analyzer xyz-789 LAYER-002 "레이어 분류" should
```

## 우선순위

| 우선순위 | 의미 | 실패 시 영향 |
|----------|------|-------------|
| `must` | 필수 | 전체 실패 |
| `should` | 권장 | 경고 |
| `could` | 선택 | 정보 |

## 실행

```bash
python ${CLAUDE_PLUGIN_ROOT}/lib/feedback_collector.py failure "$skill" "$session" "$check_id" "$check_name" "$priority" "${error:-}"
```
