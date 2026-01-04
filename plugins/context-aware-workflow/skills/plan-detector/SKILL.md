---
name: plan-detector
description: Detects Plan Mode completion and suggests starting CAW workflow. Use when ExitPlanMode is called or when a plan file is created/updated in .claude/plans/ directory.
allowed-tools: Read, Glob, AskUserQuestion
---

# Plan Detector

Automatically detect Plan Mode completion and offer to start a structured CAW workflow.

## Triggers

This skill activates when:
1. `ExitPlanMode` tool is called
2. Plan file is created/modified in `.claude/plans/`
3. User mentions "plan is ready" or similar phrases

## Behavior

### Step 1: Detect Plan File

When triggered, locate the plan file:

```
1. Check for recently modified files in .claude/plans/
2. Validate file contains implementation steps
3. Parse plan structure using patterns from patterns.md
```

### Step 2: Analyze Plan Content

Evaluate if plan is suitable for CAW workflow:

```markdown
## Plan Analysis Criteria

Required elements (must have at least 2):
- [ ] Clear task/feature title
- [ ] Implementation steps or phases
- [ ] File modifications or creations listed

Optional but helpful:
- [ ] Technical decisions documented
- [ ] Dependencies identified
- [ ] Success criteria defined
```

See `patterns.md` for detailed pattern matching rules.

### Step 3: Present Options to User

Use AskUserQuestion to offer workflow options:

```
🎯 Plan Mode 완료 감지

계획 파일: [plan file path]
분석 결과:
  ✅ 구현 단계: [N]개 Phase, [M]개 Step 감지
  ✅ 파일 변경: [X]개 파일 예상
  [✅/⚠️] 기술 결정: [documented/not found]

CAW 워크플로우 옵션:
[1] 자동 시작 - /caw:start --from-plan 실행
[2] 설계 먼저 - /caw:design 로 상세 설계 후 시작
[3] 수동 진행 - 나중에 직접 시작
[4] 계획 수정 - Plan Mode로 돌아가기
```

### Step 4: Execute Selected Option

Based on user selection:

| Option | Action |
|--------|--------|
| 1 | Invoke `/caw:start --from-plan` |
| 2 | Invoke `/caw:design --all` |
| 3 | Display reminder message |
| 4 | Suggest re-entering Plan Mode |

## Integration

- **Hook Trigger**: PostToolUse (ExitPlanMode)
- **Pattern Reference**: `patterns.md` for plan file recognition
- **Output**: User decision → appropriate command invocation
- **Next Steps**: `/caw:start`, `/caw:design`, or manual workflow

## Output Messages

### Plan Detected Successfully
```
🎯 Plan Mode 완료 감지

계획 파일: .claude/plans/auth-implementation.md

📋 계획 요약:
   제목: User Authentication with JWT
   구현 단계: 2 Phases, 6 Steps
   예상 파일: 5개 생성, 2개 수정

💡 CAW 워크플로우로 체계적인 구현을 시작할 수 있습니다.
```

### Plan Not Suitable
```
ℹ️ Plan Mode 완료 감지

계획 파일이 발견되었으나 CAW 워크플로우에 적합하지 않습니다:
  ⚠️ 구현 단계가 명확하지 않음
  ⚠️ 파일 변경 사항 미정의

권장 사항:
  • Plan Mode에서 구현 단계를 더 상세히 작성
  • 또는 /caw:start "task description" 으로 새로 시작
```

## Directory Structure

```
skills/plan-detector/
├── SKILL.md      # This file - core behavior
└── patterns.md   # Plan file pattern definitions
```

## Boundaries

**Will:**
- Detect plan file creation/modification
- Analyze plan structure for CAW compatibility
- Offer appropriate workflow options
- Provide clear feedback on plan quality

**Will Not:**
- Automatically start workflow without user confirmation
- Modify the original plan file
- Force CAW workflow on unsuitable plans
