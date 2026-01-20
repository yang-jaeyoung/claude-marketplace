---
name: feedback-correction
description: "사용자 수정을 기록합니다."
arguments:
  - name: skill
    description: "스킬 이름"
    required: true
  - name: session
    description: "세션 ID"
    required: true
  - name: file
    description: "수정된 파일"
    required: true
  - name: action
    description: "수정 행위 (modify/add/delete)"
    required: true
  - name: section
    description: "수정된 섹션"
    required: false
  - name: added
    description: "추가된 줄 수"
    required: false
  - name: removed
    description: "삭제된 줄 수"
    required: false
---
# /feedback-correction

사용자가 스킬 출력물을 수정한 내용을 기록합니다.

## 사용법

```
/feedback-correction <skill> <session> <file> <action> [section] [added] [removed]
```

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

## 실행

```bash
python ${CLAUDE_PLUGIN_ROOT}/lib/feedback_collector.py correction "$skill" "$session" "$file" "$action" "${section:-}" "${added:-0}" "${removed:-0}"
```

## 분석 활용

반복적으로 동일 섹션이 수정되면 해당 섹션의 생성 가이드 개선이 필요하다는 신호입니다.
