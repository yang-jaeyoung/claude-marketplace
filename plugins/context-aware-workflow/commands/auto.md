---
description: Run the full CW workflow automatically - from expansion to completion with review and reflection
argument-hint: "<task description>"
---

# /cw:auto - Automated Full Workflow (v2.0)

Execute the complete CW workflow in a single command with enhanced features:
- **Expansion Phase**: Requirements analysis before planning
- **Signal-Based Transitions**: Automatic phase progression
- **Parallel Validation**: 3-architect review (functional/security/quality)
- **Persistence Enforcement**: Auto-resume on interruption

## Usage

```bash
# Basic usage
/cw:auto "Add a logout button to the header"

# Skip optional stages
/cw:auto "Fix login validation" --skip-qa
/cw:auto "Update API endpoint" --skip-reflect
/cw:auto "Add tests" --skip-review --skip-reflect

# Disable parallel validation
/cw:auto "Simple fix" --no-parallel-validation

# Verbose output
/cw:auto "Implement dark mode" --verbose
```

## Workflow Stages (9-Stage Pipeline)

```
/cw:auto "task description"

[1/9] expansion → Analyze requirements, create spec.md
[2/9] init      → Initialize .caw/ environment if not exists
[3/9] planning  → Generate task_plan.md
[4/9] execution → Execute all steps until completion
[5/9] qa        → Run automated QA cycles (build → test → fix)
[6/9] review    → Parallel validation (3 architects)
[7/9] fix       → Auto-fix remaining resolvable issues
[8/9] check     → Validate compliance with project rules
[9/9] reflect   → Run Ralph Loop for learning capture
```

## Flags

| Flag | Description |
|------|-------------|
| `--skip-expansion` | Skip expansion phase (use for well-defined tasks) |
| `--skip-qa` | Skip QA loop stage (stage 5) |
| `--skip-review` | Skip review, fix, and check stages (stages 6-8) |
| `--skip-reflect` | Skip reflect stage (stage 9) |
| `--no-parallel-validation` | Use single reviewer instead of 3 parallel |
| `--verbose` | Show detailed progress for each stage |
| `--no-questions` | Minimize interactive questions during all phases |

## Signal-Based Phase Transitions

Each phase outputs a completion signal. See [Signal Detection](_shared/signal-detection.md).

| Phase | Completion Signal |
|-------|-------------------|
| Expansion | `EXPANSION_COMPLETE` |
| Init | `INIT_COMPLETE` |
| Planning | `PLANNING_COMPLETE` |
| Execution | `EXECUTION_COMPLETE` |
| QA | `QA_COMPLETE` |
| Review | `REVIEW_COMPLETE` |
| Fix | `FIX_COMPLETE` |
| Check | `CHECK_COMPLETE` |
| Reflect | `REFLECT_COMPLETE` |
| Final | `AUTO_COMPLETE` |

## Execution Flow

### Stage 1: Expansion (unless --skip-expansion)

```
NEW: Requirements Analysis Phase

1. Invoke Analyst Agent:
   - Parse task description
   - Analyze existing codebase
   - Extract functional requirements
   - Identify non-functional requirements
   - Discover implicit requirements

2. Output:
   - .caw/spec.md (specification document)
   - Tech stack recommendations
   - Integration points identified

3. Signal: EXPANSION_COMPLETE
```

### Stage 2: Initialize (if needed)

```
Check for .caw/context_manifest.json:

├─ EXISTS  → Skip to Stage 3
└─ MISSING → Invoke Bootstrapper Agent
              └─ Create .caw/ directory structure
              └─ Generate context_manifest.json
              └─ Verify initialization success

Signal: INIT_COMPLETE
```

### Stage 3: Planning

```
Invoke Planner Agent with context:

Input:
  - .caw/spec.md (from expansion)
  - Task description
  - Codebase patterns

Auto-Mode Behavior:
  - Use spec.md requirements as guide
  - Minimize clarifying questions
  - Prefer simpler plans (fewer phases)
  - Mark parallelizable steps

Output:
  - .caw/task_plan.md

Signal: PLANNING_COMPLETE
```

### Stage 4: Execution

```
WHILE pending_steps exist:
  1. Identify next runnable step (check dependencies)
  2. Invoke Builder Agent for the step
  3. Update task_plan.md status
  4. Track files created/modified

  IF error:
    - Apply error recovery (Fixer agent)
    - If unrecoverable:
      - Save state to .caw/auto-state.json
      - Report error with resume instructions
      - Output PHASE_ERROR signal
      - STOP workflow

  IF all steps complete:
    - Signal: EXECUTION_COMPLETE
    - Proceed to Stage 5
```

### Stage 5: QA Loop (unless --skip-qa)

```
IF all steps completed successfully:
  Invoke /cw:qaloop:
    target: all_completed_steps
    max_cycles: 2
    severity: major

  IF qaloop_result == "passed":
    Signal: QA_COMPLETE
    Proceed to Stage 6
  ELIF qaloop_result == "stalled":
    Display warning: "QA found recurring issues"
    Signal: QA_COMPLETE (with warnings)
    Proceed to Stage 6 anyway
```

### Stage 6: Review (Enhanced with Parallel Validation)

```
IF config.parallel_validation enabled (default):

  Round 1 (max 3 rounds):
    Spawn 3 Reviewer agents in parallel:
    ┌─────────────────────────────────────────────────────┐
    │ Task 1: Functional Completeness Review              │
    │   - Verify all spec.md requirements implemented     │
    │   - Check acceptance criteria                       │
    │   - Validate edge cases                             │
    │                                                     │
    │ Task 2: Security Vulnerability Review               │
    │   - Check OWASP Top 10                              │
    │   - Validate input handling                         │
    │   - Review authentication/authorization             │
    │                                                     │
    │ Task 3: Code Quality Review                         │
    │   - Check maintainability                           │
    │   - Validate conventions                            │
    │   - Review test coverage                            │
    └─────────────────────────────────────────────────────┘

  Aggregate verdicts:
    - All APPROVED → Signal: REVIEW_COMPLETE
    - Any REJECTED/NEEDS_FIX → Proceed to Stage 7 (Fix)
    - After fix, retry (max 3 rounds)

  Save to .caw/validation-results.json

ELSE (single reviewer):
  Invoke single Reviewer Agent
  Output: .caw/last_review.json
  Signal: REVIEW_COMPLETE
```

### Stage 7: Fix (unless --skip-review)

```
IF review found issues:
  Parse validation results or .caw/last_review.json

  FOR each issue:
    IF auto_fixable:
      Apply fix via Fixer Agent (Haiku tier)
      Track fix in validation-results.json
    ELSE:
      Add to deferred_issues list

  IF parallel_validation enabled:
    Return to Stage 6 for re-validation (max 3 rounds)
  ELSE:
    Signal: FIX_COMPLETE
    Proceed to Stage 8
```

### Stage 8: Check (unless --skip-review)

```
Invoke ComplianceChecker Agent:
  - Validate against CLAUDE.md rules
  - Check project conventions
  - Report any violations

IF violations found AND fixable:
  Apply fixes
  Re-run check

Signal: CHECK_COMPLETE
```

### Stage 9: Reflect (unless --skip-reflect)

```
Invoke Ralph Loop:
  - REFLECT on completed task
  - ANALYZE what worked/didn't
  - LEARN key insights
  - PLAN improvements
  - HABITUATE via .caw/learnings.md

Signal: REFLECT_COMPLETE
Final Signal: AUTO_COMPLETE
```

## State Management

### Auto State File (.caw/auto-state.json)

```json
{
  "schema_version": "2.0",
  "active": true,
  "phase": "execution",
  "iteration": 2,
  "max_iterations": 20,
  "task_description": "Add logout button",
  "started_at": "2024-01-15T10:30:00Z",
  "session_id": "session_abc123",
  "config": {
    "skip_expansion": false,
    "skip_qa": false,
    "skip_review": false,
    "skip_reflect": false,
    "parallel_validation": true,
    "verbose": false
  },
  "expansion": {
    "analyst_complete": true,
    "spec_path": ".caw/spec.md",
    "signal_detected": true
  },
  "init": {
    "bootstrapper_complete": true,
    "signal_detected": true
  },
  "planning": {
    "plan_path": ".caw/task_plan.md",
    "phases_count": 2,
    "steps_count": 5,
    "signal_detected": true
  },
  "execution": {
    "current_step": "2.1",
    "tasks_completed": 3,
    "tasks_total": 5,
    "files_created": ["src/components/LogoutButton.tsx"],
    "files_modified": ["src/components/Header.tsx"],
    "signal_detected": false
  },
  "review": {
    "parallel_validation": {
      "enabled": true,
      "validation_rounds": 1,
      "all_approved": false
    }
  },
  "signals": {
    "last_checked": "2024-01-15T10:45:00Z",
    "detected_signals": [
      {"signal": "EXPANSION_COMPLETE", "detected_at": "2024-01-15T10:32:00Z"},
      {"signal": "INIT_COMPLETE", "detected_at": "2024-01-15T10:33:00Z"},
      {"signal": "PLANNING_COMPLETE", "detected_at": "2024-01-15T10:38:00Z"}
    ]
  }
}
```

### Persistence Enforcement

Stop hook (`hooks/scripts/auto_enforcer.py`) ensures:
1. Auto mode continues even if session pauses
2. Injects continuation prompt if signal not detected
3. Tracks iteration counts per phase
4. Transitions automatically on signal detection

See [Signal Detection](_shared/signal-detection.md) for full specification.

## Progress Display

### Standard Output

```
🚀 /cw:auto "Add logout button"

[1/9] Expanding...        ✓ (spec.md created)
[2/9] Initializing...     ✓ (already initialized)
[3/9] Planning...         ✓ (2 phases, 5 steps)
[4/9] Executing...        ✓ (5/5 steps complete)
[5/9] QA Loop...          ✓ (build: ✓, tests: ✓)
[6/9] Reviewing...        ✓ (parallel: 3/3 approved)
[7/9] Fixing...           ✓ (2 auto-fixed)
[8/9] Checking...         ✓ (compliant)
[9/9] Reflecting...       ✓

✅ Workflow Complete

📊 Summary:
  • Requirements: 8 extracted (6 P0, 2 P1)
  • Steps executed: 5
  • Validation rounds: 2
  • Issues found: 3 (3 fixed, 0 deferred)
  • Compliance: Pass

📁 Artifacts:
  • .caw/spec.md
  • .caw/task_plan.md (complete)
  • .caw/validation-results.json
  • .caw/learnings.md (updated)

---
SIGNAL: AUTO_COMPLETE
PHASE: complete
STATUS: complete
TIMESTAMP: 2024-01-15T11:10:00Z
NEXT: none
---
```

### Verbose Output (--verbose)

```
🚀 /cw:auto "Add logout button" --verbose

══════════════════════════════════════════════════
[1/9] EXPANSION
══════════════════════════════════════════════════
  → Invoking Analyst Agent (Sonnet)
  → Parsing task description...
  → Analyzing existing codebase patterns...
  → Extracting requirements...

  📋 Specification Generated:
  ┌─────────────────────────────────────────────┐
  │ Functional Requirements (P0):              │
  │   • FR-1: Logout button in header          │
  │   • FR-2: Click triggers auth logout       │
  │   • FR-3: Redirect to login after logout   │
  │                                             │
  │ Non-Functional Requirements:               │
  │   • NFR-1: Response time < 200ms           │
  │   • NFR-2: Accessible (keyboard nav)       │
  │                                             │
  │ Integration Points:                        │
  │   • src/components/Header.tsx              │
  │   • src/hooks/useAuth.ts                   │
  └─────────────────────────────────────────────┘

  ---
  SIGNAL: EXPANSION_COMPLETE
  PHASE: expansion
  STATUS: complete
  TIMESTAMP: 2024-01-15T10:32:00Z
  NEXT: init
  ---

  ✓ Stage 1 complete

══════════════════════════════════════════════════
[2/9] INITIALIZING
══════════════════════════════════════════════════
  → Checking .caw/context_manifest.json... EXISTS
  → Environment already initialized

  ---
  SIGNAL: INIT_COMPLETE
  PHASE: init
  STATUS: complete
  TIMESTAMP: 2024-01-15T10:33:00Z
  NEXT: planning
  ---

  ✓ Stage 2 complete (skipped - already initialized)

... (continues for remaining stages)
```

## Error Handling

### Execution Error

```
🚀 /cw:auto "Add logout button"

[1/9] Expanding...        ✓
[2/9] Initializing...     ✓
[3/9] Planning...         ✓ (2 phases, 5 steps)
[4/9] Executing...        ████████░░ 60% (Step 2.1)

⚠️ Execution stopped at Phase 2, Step 2.1

Error: TypeScript compilation failed
  → src/components/Header.tsx:12
  → Cannot find module './LogoutButton'

📝 State saved to .caw/auto-state.json

---
SIGNAL: PHASE_ERROR
PHASE: execution
STATUS: error
TIMESTAMP: 2024-01-15T10:45:00Z
ERROR: TypeScript compilation failed
RECOVERABLE: true
---

💡 To resume:
  1. Fix the error manually, then run:
     /cw:next

  2. Or restart auto mode (resumes from saved state):
     /cw:auto --continue

  3. Or check current status:
     /cw:status
```

### Parallel Validation Failure

```
[6/9] Reviewing...

📋 Parallel Validation Results (Round 1/3):

  Functional Review:   ✓ APPROVED
  Security Review:     ✗ NEEDS_FIX
    • [Major] Missing input validation at LogoutButton.tsx:15
  Quality Review:      ✓ APPROVED

  Final Verdict: NEEDS_FIX

[7/9] Fixing...
  → Applying fix for: Missing input validation

📋 Parallel Validation Results (Round 2/3):

  Functional Review:   ✓ APPROVED
  Security Review:     ✓ APPROVED
  Quality Review:      ✓ APPROVED

  Final Verdict: APPROVED

Continuing workflow...
```

## Resuming Interrupted Workflow

```bash
# Check current state
/cw:status

# Resume auto mode from saved state
/cw:auto --continue

# Or continue manually step by step
/cw:next
```

## Integration

- **Reads**: Task description, .caw/spec.md, .caw/task_plan.md
- **Invokes**: Analyst, Bootstrapper, Planner, Builder, Reviewer (x3), Fixer, ComplianceChecker, Ralph Loop
- **Updates**: .caw/auto-state.json, .caw/task_plan.md, .caw/learnings.md
- **Creates**: .caw/spec.md, .caw/validation-results.json

## Best Practices

1. **Use for well-defined tasks**
   - "Add a button", "Fix this bug", "Add validation"
   - Expansion phase handles ambiguous requirements

2. **Skip expansion for trivial tasks**
   - `/cw:auto "Fix typo in README" --skip-expansion`

3. **Review validation results**
   - Check .caw/validation-results.json for detailed findings
   - Address any deferred issues manually

4. **Use verbose for debugging**
   - `--verbose` shows detailed agent interactions
   - Helps understand phase transitions

## References

- [Signal Detection](_shared/signal-detection.md)
- [Auto Mode Signals](_shared/auto-mode-signals.md)
- [Parallel Validation](_shared/parallel-validation.md)
- [Auto State Schema](_shared/schemas/auto-state.schema.json)
- [Validation Results Schema](_shared/schemas/validation-results.schema.json)
