---
description: "검증 실패를 기록"
argument-hint: "<skill> <session> <check_id> <check_name> <priority> [error]"
allowed-tools: ["Bash"]
---
# /feedback-failure

검증 실패를 기록합니다.

## 사용법

```
/feedback-failure <skill> <session> <check_id> <check_name> <priority> [error]
```

## 파라미터

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| skill | O | 스킬 이름 |
| session | O | 세션 ID |
| check_id | O | 검증 ID (예: FILE-001) |
| check_name | O | 검증 이름 |
| priority | O | 우선순위 (must/should/could) |
| error | X | 에러 메시지 |

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

## 실행 지시

다음 bash 명령을 실행하세요:

```bash
python ${CLAUDE_PLUGIN_ROOT}/lib/feedback_collector.py failure "$skill" "$session" "$check_id" "$check_name" "$priority" "${error:-}"
```
