---
description: "개선 제안 적용 가이드를 생성"
argument-hint: "<skill> [--dry-run]"
allowed-tools: ["Bash"]
---
# /feedback-apply

분석된 개선 제안을 실제 스킬에 적용하기 위한 가이드를 생성합니다.

## 사용법

```
/feedback-apply <skill> [--dry-run]
```

## 파라미터

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| skill | O | 대상 스킬 이름 |
| --dry-run | X | 적용하지 않고 가이드만 출력 |

## 예시

```
/feedback-apply vue-project-analyzer --dry-run
/feedback-apply dotnet-project-analyzer
```

## 워크플로우

```
feedback analyze <skill>
    ↓
스킬 존재 확인
    ├─ 존재함 (exists: true)
    │   └─ 분석 + 적용 가이드 생성
    │       ├─ HIGH 우선순위: verification/checklist.yaml 수정
    │       └─ MEDIUM 우선순위: SKILL.md 가이드 보강
    │
    └─ 존재하지 않음 (exists: false)
        └─ 안내 메시지 출력
            ├─ 옵션 1: intent-skill-creator로 새 스킬 생성
            ├─ 옵션 2: 피드백 데이터 정리 (삭제)
            └─ 옵션 3: 기존 스킬 이름으로 데이터 이전
```

## 출력 형식

```json
{
  "skill_exists": true,
  "applicable": true,
  "total_suggestions": 3,
  "actions": [
    {
      "priority": "HIGH",
      "target": "verification/checklist.yaml",
      "action": "modify",
      "description": "STRUCT-001 검증 로직 수정"
    }
  ],
  "message": "3개의 개선 제안이 적용 가능합니다."
}
```

## 실행 지시

다음 bash 명령을 실행하세요:

```bash
python ${CLAUDE_PLUGIN_ROOT}/lib/feedback_analyzer.py apply "$skill" ${dry_run:+--dry-run}
```
