---
name: plan-detector
description: Detects Plan Mode completion and suggests starting CAW workflow. Use when ExitPlanMode is called or when a plan file is created/updated in the configured plansDirectory (resolves from settings).
allowed-tools: Read, Glob, AskUserQuestion
hooks:
  ExitPlanMode:
    action: suggest_caw_workflow
    priority: 1
    condition: "requires .caw/ directory"
---

# Plan Detector

Automatically detect Plan Mode completion and offer to start a structured CAW workflow.

## Triggers

This skill activates when:
1. `ExitPlanMode` tool is called
2. Plan file is created/modified in configured `plansDirectory` (see `_shared/plans-directory-resolution.md`)
3. User mentions "plan is ready" or similar phrases

## Behavior

### Step 1: Detect Plan File

When triggered, locate the plan file:

```
1. Resolve plansDirectory setting:
   - Read .claude/settings.local.json → "plansDirectory"
   - If not found → Read .claude/settings.json
   - If not found → Read ~/.claude/settings.json
   - If not found → Use default ".claude/plans/"

2. Check for recently modified files:
   - {plansDirectory}/*.md (configured location)
   - .claude/plan.md (legacy, always check)

3. Validate file contains implementation steps
4. Parse plan structure using patterns from patterns.md
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
🎯 Plan Mode Completion Detected

Plan file: [plan file path]
Analysis result:
  ✅ Implementation stages: [N] Phases, [M] Steps detected
  ✅ File changes: [X] files expected
  [✅/⚠️] Technical decisions: [documented/not found]

CAW Workflow Options:
[1] Auto start - Execute /cw:start --from-plan
[2] Design first - Start after detailed design with /cw:design
[3] Manual proceed - Start manually later
[4] Edit plan - Return to Plan Mode
```

### Step 4: Execute Selected Option

Based on user selection:

| Option | Action |
|--------|--------|
| 1 | Invoke `/cw:start --from-plan` |
| 2 | Invoke `/cw:design --all` |
| 3 | Display reminder message |
| 4 | Suggest re-entering Plan Mode |

## Integration

- **Hook Trigger**: PostToolUse (ExitPlanMode)
- **Pattern Reference**: `patterns.md` for plan file recognition
- **Output**: User decision → appropriate command invocation
- **Next Steps**: `/cw:start`, `/cw:design`, or manual workflow

## Output Messages

### Plan Detected Successfully
```
🎯 Plan Mode Completion Detected

Plan file: .claude/plans/auth-implementation.md

📋 Plan Summary:
   Title: User Authentication with JWT
   Implementation stages: 2 Phases, 6 Steps
   Expected files: 5 created, 2 modified

💡 You can start systematic implementation with CAW workflow.
```

### Plan Not Suitable
```
ℹ️ Plan Mode Completion Detected

Plan file was found but is not suitable for CAW workflow:
  ⚠️ Implementation stages are not clear
  ⚠️ File changes are not defined

Recommendations:
  • Write more detailed implementation stages in Plan Mode
  • Or start fresh with /cw:start "task description"
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
