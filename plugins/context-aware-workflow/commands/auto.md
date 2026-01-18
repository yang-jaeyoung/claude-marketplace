---
description: Run the full CW workflow automatically - from initialization to completion with review and reflection
argument-hint: "<task description>"
---

# /cw:auto - Automated Full Workflow

Execute the complete CW workflow in a single command. Ideal for simple projects where you want to run through all stages without manual intervention.

## Usage

```bash
# Basic usage
/cw:auto "Add a logout button to the header"

# Skip optional stages
/cw:auto "Fix login validation" --skip-review
/cw:auto "Update API endpoint" --skip-reflect
/cw:auto "Add tests" --skip-review --skip-reflect

# Verbose output
/cw:auto "Implement dark mode" --verbose
```

## Workflow Stages

```
/cw:auto "task description"

[1/7] init     → Initialize .caw/ environment if not exists
[2/7] start    → Generate task_plan.md (minimal questions)
[3/7] next     → Execute all steps until completion
[4/7] review   → Run code review on implemented code
[5/7] fix      → Auto-fix resolvable issues
[6/7] check    → Validate compliance with project rules
[7/7] reflect  → Run Ralph Loop for learning capture
```

## Flags

| Flag | Description |
|------|-------------|
| `--skip-review` | Skip review, fix, and check stages (stages 4-6) |
| `--skip-reflect` | Skip reflect stage (stage 7) |
| `--verbose` | Show detailed progress for each stage |
| `--no-questions` | Minimize interactive questions during planning |

## Execution Flow

### Stage 1: Initialize (if needed)

Check for `.caw/context_manifest.json`:

```
├─ EXISTS  → Skip to Stage 2
└─ MISSING → Invoke Bootstrapper Agent
              └─ Create .caw/ directory structure
              └─ Generate context_manifest.json
              └─ Verify initialization success
```

### Stage 2: Start/Plan

Invoke Planner Agent with auto-mode hints:

```markdown
## Planner Invocation (Auto Mode)

**Task**: [user's task description]

**Auto-Mode Behavior**:
- Minimize clarifying questions
- Use reasonable defaults
- Prefer simpler plans (fewer phases)
- Focus on core functionality first

**Output**: .caw/task_plan.md
```

### Stage 3: Execute Steps

Loop through all pending steps:

```
WHILE pending_steps exist:
  1. Identify next runnable step (check dependencies)
  2. Invoke Builder Agent for the step
  3. Update task_plan.md status
  4. IF error:
       - Save state to .caw/session.json
       - Report error with resume instructions
       - STOP workflow
  5. IF all steps complete:
       - Proceed to Stage 4
```

### Stage 4: Review (unless --skip-review)

```
Invoke Reviewer Agent:
  - Scope: All files modified during execution
  - Mode: Standard review (not deep)
  - Output: Review report + .caw/last_review.json
```

### Stage 5: Fix (unless --skip-review)

```
IF review found issues:
  Parse .caw/last_review.json

  FOR each issue:
    IF auto_fixable:
      Apply fix via Fixer Agent (Haiku tier)
    ELSE:
      Add to deferred_issues list

  IF deferred_issues exist:
    Display summary: "N issues require manual attention"
```

### Stage 6: Check (unless --skip-review)

```
Invoke ComplianceChecker Agent:
  - Validate against CLAUDE.md rules
  - Check project conventions
  - Report any violations
```

### Stage 7: Reflect (unless --skip-reflect)

```
Invoke Ralph Loop:
  - REFLECT on completed task
  - ANALYZE what worked/didn't
  - LEARN key insights
  - PLAN improvements
  - HABITUATE via .caw/learnings.md
```

## Progress Display

### Standard Output

```
🚀 /cw:auto "Add logout button"

[1/7] Initializing...     ✓
[2/7] Planning...         ✓ (2 phases, 5 steps)
[3/7] Executing...        ✓ (5/5 steps complete)
[4/7] Reviewing...        ✓ (2 suggestions)
[5/7] Fixing...           ✓ (1 auto-fixed)
[6/7] Checking...         ✓ (compliant)
[7/7] Reflecting...       ✓

✅ Workflow Complete

📊 Summary:
  • Steps executed: 5
  • Review issues: 2 (1 fixed, 1 deferred)
  • Compliance: Pass

💡 Deferred Issues (1):
  • src/header.tsx:45 - Consider extracting logout logic to custom hook

📁 Artifacts:
  • .caw/task_plan.md (complete)
  • .caw/learnings.md (updated)
```

### Verbose Output (--verbose)

```
🚀 /cw:auto "Add logout button" --verbose

══════════════════════════════════════════════════
[1/7] INITIALIZING
══════════════════════════════════════════════════
  → Checking .caw/context_manifest.json... EXISTS
  → Environment already initialized
  ✓ Stage 1 complete

══════════════════════════════════════════════════
[2/7] PLANNING
══════════════════════════════════════════════════
  → Invoking Planner Agent (Sonnet)
  → Analyzing task requirements...
  → Exploring codebase for context...
  → Generating task_plan.md...

  📋 Plan Generated:
  ┌─────────────────────────────────────────────┐
  │ Phase 1: Component Implementation           │
  │   1.1 Create LogoutButton component         │
  │   1.2 Add logout handler logic              │
  │                                             │
  │ Phase 2: Integration                        │
  │   2.1 Import LogoutButton in Header         │
  │   2.2 Add to header layout                  │
  │   2.3 Add tests                             │
  └─────────────────────────────────────────────┘

  ✓ Stage 2 complete (2 phases, 5 steps)

══════════════════════════════════════════════════
[3/7] EXECUTING
══════════════════════════════════════════════════
  → Step 1.1: Create LogoutButton component
    • Files: src/components/LogoutButton.tsx
    ✓ Complete

  → Step 1.2: Add logout handler logic
    • Files: src/hooks/useLogout.ts
    ✓ Complete

  → Step 2.1: Import LogoutButton in Header
    • Files: src/components/Header.tsx
    ✓ Complete

  ... (continues for all steps)

  ✓ Stage 3 complete (5/5 steps)

... (continues for remaining stages)
```

## Error Handling

### Execution Error

When an error occurs during step execution:

```
🚀 /cw:auto "Add logout button"

[1/7] Initializing...     ✓
[2/7] Planning...         ✓ (2 phases, 5 steps)
[3/7] Executing...        ████████░░ 60% (Step 2.1)

⚠️ Execution stopped at Phase 2, Step 2.1

Error: TypeScript compilation failed
  → src/components/Header.tsx:12
  → Cannot find module './LogoutButton'

📝 State saved to .caw/session.json

💡 To resume:
  1. Fix the error manually, then run:
     /cw:next

  2. Or restart the failed step:
     /cw:next --step 2.1

  3. Or check current status:
     /cw:status
```

### Review Issues (Non-blocking)

```
[4/7] Reviewing...        ✓ (3 issues found)

📋 Review Summary:
  • 🔴 Critical: 0
  • 🟡 Minor: 2
  • 🟢 Suggestion: 1

[5/7] Fixing...           ✓ (2 auto-fixed, 1 deferred)

Auto-fixed:
  • Missing type annotation at LogoutButton.tsx:8
  • Unused import at Header.tsx:3

Deferred (manual attention needed):
  • Consider memoizing logout handler (performance suggestion)

Continuing workflow...
```

### Critical Review Issues

If critical issues are found, workflow pauses:

```
[4/7] Reviewing...        ⚠️ Critical issues found

🔴 Critical Issues (workflow paused):

1. src/hooks/useLogout.ts:15
   Security: Token not invalidated on logout

2. src/components/LogoutButton.tsx:22
   Bug: Missing error handling for logout failure

💡 Options:
  1. Fix issues manually, then run:
     /cw:auto --continue

  2. Skip review and continue (not recommended):
     /cw:next
```

## State Management

### Session State (.caw/session.json)

Auto-mode saves progress for resumability:

```json
{
  "auto_mode": {
    "active": true,
    "started_at": "2024-01-15T10:30:00Z",
    "current_stage": 3,
    "stages_completed": [1, 2],
    "task_description": "Add logout button",
    "options": {
      "skip_review": false,
      "skip_reflect": false,
      "verbose": false
    }
  },
  "execution": {
    "current_step": "2.1",
    "steps_completed": ["1.1", "1.2"],
    "last_error": null
  }
}
```

### Resuming Interrupted Workflow

```bash
# Check current state
/cw:status

# Resume from where it stopped
/cw:next          # Continues execution

# Or restart auto mode (picks up from saved state)
/cw:auto --continue
```

## Auto-Mode Behavior Modifications

When running in auto mode, agents adjust their behavior:

### Planner Agent (Auto Mode)

```markdown
## Auto-Mode Planner Adjustments

- Skip non-essential clarifying questions
- Use project conventions as defaults
- Prefer single-phase plans for simple tasks
- Limit to 10 steps maximum
- Mark all steps as "⚡ Parallel OK" when safe
```

### Builder Agent (Auto Mode)

```markdown
## Auto-Mode Builder Adjustments

- Continue on minor warnings
- Auto-create missing directories
- Use existing patterns without asking
- Run tests automatically after implementation
```

### Reviewer Agent (Auto Mode)

```markdown
## Auto-Mode Reviewer Adjustments

- Focus on critical and major issues
- Defer style suggestions
- Generate auto_fixable flags in output
- Keep review concise
```

## Integration

- **Reads**: Task description from arguments
- **Invokes**: Bootstrapper, Planner, Builder, Reviewer, Fixer, ComplianceChecker, Ralph Loop
- **Updates**: `.caw/task_plan.md`, `.caw/session.json`, `.caw/learnings.md`
- **Creates**: `.caw/last_review.json` (during review stage)

## Best Practices

1. **Use for simple, well-defined tasks**
   - "Add a button", "Fix this bug", "Add validation"

2. **Use manual workflow for complex tasks**
   - Multi-module changes, architecture decisions
   - Use `/cw:start` instead for more control

3. **Review deferred issues after completion**
   - Auto-fix handles simple issues
   - Manual review still valuable for suggestions

4. **Use --verbose when debugging**
   - Helps understand what went wrong
   - Shows detailed agent interactions
