---
description: Run autonomous loop until task completion (dingco Ralph Loop pattern)
argument-hint: "<task description>"
---

# /cw:loop - Autonomous Execution Loop

Run tasks autonomously until completion conditions are met. Repeatedly executes Builder agent until the task is done, max iterations reached, or all steps are complete.

## Usage

```bash
# Basic usage
/cw:loop "Implement user authentication with JWT"

# Resume interrupted loop
/cw:loop --continue

# With custom settings
/cw:loop "Add dark mode support" --max-iterations 30
/cw:loop "Fix all linting errors" --completion-promise "ALL_FIXED"

# Disable auto-fix for strict mode
/cw:loop "Critical security fix" --no-auto-fix

# Skip reflection phase
/cw:loop "Quick refactor" --no-reflect

# Verbose progress output
/cw:loop "Complex feature" --verbose
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max-iterations` | 20 | Maximum iterations before forced exit |
| `--completion-promise` | "DONE" | Keyword to detect for early completion |
| `--continue` | false | Resume from saved loop_state.json |
| `--auto-fix` | true | Enable Fixer agent for error recovery |
| `--no-auto-fix` | - | Disable auto-fix (strict mode) |
| `--reflect` | true | Run /cw:reflect after completion |
| `--no-reflect` | - | Skip reflection phase |
| `--verbose` | false | Show detailed iteration progress |
| `--qa-each-step` | false | Run QA loop after each completed step |
| `--qa-severity` | major | QA severity threshold (with --qa-each-step) |

## Exit Conditions

The loop exits when ANY of these conditions are met:

| Condition | Status | Description |
|-----------|--------|-------------|
| Completion Promise | `completed` | Output contains completion keyword |
| All Steps Complete | `completed` | All task_plan.md steps are ✅ |
| Max Iterations | `max_iterations_reached` | Reached --max-iterations limit |
| Consecutive Failures | `failed` | 3+ consecutive failures |
| Critical Error | `failed` | Unrecoverable error encountered |
| Manual Abort | `paused` | User interrupts execution |

## Execution Flow

### Phase 1: Initialization

```
1. Check for existing .caw/loop_state.json
   ├─ EXISTS + --continue → Resume from saved state
   ├─ EXISTS + no flag → Ask: Resume or restart?
   └─ NOT EXISTS → Create new loop state

2. Verify prerequisites:
   ├─ .caw/context_manifest.json exists?
   │   └─ NO → Invoke Bootstrapper Agent
   └─ .caw/task_plan.md exists?
       └─ NO → Invoke Planner Agent with task description

3. Initialize loop_state.json:
   {
     "schema_version": "1.0",
     "loop_id": "loop_YYYYMMDD_HHMMSS",
     "status": "running",
     "config": { ... user parameters ... },
     "current_iteration": 0,
     "iterations": []
   }
```

### Phase 2: Iteration Loop

```
WHILE status == "running":

  [1] Increment iteration counter
      current_iteration += 1

  [2] Check exit conditions (pre-iteration)
      IF current_iteration > max_iterations:
        → EXIT (max_iterations_reached)

  [3] Execute Builder Agent
      Task tool:
        subagent_type: "cw:Builder"
        prompt: |
          Execute next pending step from .caw/task_plan.md.
          Append execution summary to .caw/iteration_output.md.
          When ALL tasks are complete, output: [COMPLETION_PROMISE]

          Current iteration: [N] of [max]
          Previous outcome: [last iteration result]

  [4] Capture Builder Output
      Read: .caw/iteration_output.md (created/updated by Builder)

  [5] Analyze Results
      Parse task_plan.md for step status changes:
      - steps_completed = newly ✅ steps
      - steps_attempted = steps that were worked on
      - errors = any failures or blockers

      Determine outcome:
      - "success": steps_completed.length > 0
      - "partial": steps_attempted.length > 0 AND steps_completed.length == 0 AND no errors
      - "failure": errors.length > 0
      - "no_progress": no steps attempted or completed
      - "skipped": step was skipped via error recovery

  [6] Check Completion Promise (Phase 2)
      Search iteration_output.md for completion_promise:
      - Exact match: "DONE"
      - With punctuation: "DONE!", "DONE."
      - In sentence: "Task is DONE", "All DONE"

      IF found:
        completion_detected = true
        completion_context = surrounding text
        → EXIT (completion_promise_detected)

  [7] Check All Steps Complete
      Parse task_plan.md:
      IF all steps are ✅:
        → EXIT (all_steps_complete)

  [8] Determine Iteration Outcome
      IF steps_completed.length > 0:
        outcome = "success"
        consecutive_failures = 0
        no_progress_count = 0
      ELIF errors.length > 0:
        outcome = "failure"
        consecutive_failures += 1
        → Apply Error Recovery (Phase 3)
      ELSE:
        outcome = "no_progress"
        no_progress_count += 1
        IF no_progress_count >= 3:
          consecutive_failures += 1
          → Apply Error Recovery (Phase 3)

  [9] Check Failure Threshold
      IF consecutive_failures >= 3:
        → EXIT (consecutive_failures)

  [10] Run QA Loop (if --qa-each-step enabled)
       IF config.qa_each_step AND outcome == "success":
         Invoke /cw:qaloop:
           target_step: completed_step
           max_cycles: 2
           severity: config.qa_severity

         IF qaloop_result == "passed":
           qa_status = "passed"
         ELSE:
           outcome = "qa_failed"
           consecutive_failures += 1

  [11] Record Iteration
       Append to iterations array:
       {
         "number": current_iteration,
         "outcome": outcome,
         "steps_completed": [...],
         "errors": [...],
         "output_contains_promise": false
       }

  [12] Save State
       Write updated loop_state.json

  [13] Display Progress
       Show iteration summary to user
```

### Phase 3: Error Recovery

Five-level progressive recovery strategy:

```
Error Recovery Levels:

┌─────────────────────────────────────────────────────────────────┐
│ Level 1: Retry (failure_count = 1)                              │
│ ─────────────────────────────────────────────────────────────── │
│ Action: Re-attempt the same step                                │
│ Builder prompt: "Previous attempt failed. Retry with fresh      │
│                  approach. Error: [error_message]"              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Level 2: Fixer (failure_count = 2, auto_fix enabled)            │
│ ─────────────────────────────────────────────────────────────── │
│ Action: Invoke Fixer-Haiku for automated correction             │
│ Task tool:                                                      │
│   subagent_type: "cw:Fixer"                                     │
│   model: "haiku"                                                │
│   prompt: "Fix error in step [step_id]: [error_message]"        │
│                                                                 │
│ After fix: Retry step with Builder                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Level 3: Alternative (failure_count = 3)                        │
│ ─────────────────────────────────────────────────────────────── │
│ Action: Invoke Planner-Haiku for alternative approach           │
│ Task tool:                                                      │
│   subagent_type: "cw:Planner"                                   │
│   model: "haiku"                                                │
│   prompt: |                                                     │
│     Step [step_id] failed 3 times. Suggest alternative:         │
│     - Original step: [step_description]                         │
│     - Errors: [error_history]                                   │
│     - Propose simpler alternative or decomposition              │
│                                                                 │
│ Update task_plan.md with alternative step(s)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Level 4: Skip (failure_count > 3, step is non-blocking)         │
│ ─────────────────────────────────────────────────────────────── │
│ Condition: Step has no dependents OR all dependents can proceed │
│ Action: Mark step as ⏭️ Skipped                                 │
│ Update task_plan.md:                                            │
│   | N.M | Step description | ⏭️ Skipped | Notes: [reason] |     │
│                                                                 │
│ Log: "Step [step_id] skipped after 4 failed attempts"           │
│ Continue with next available step                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Level 5: Abort (consecutive_failures >= 3 OR blocking step)     │
│ ─────────────────────────────────────────────────────────────── │
│ Condition: 3+ consecutive failures OR step is critical/blocking │
│ Action: Abort loop with state preservation                      │
│                                                                 │
│ Update loop_state.json:                                         │
│   status: "failed"                                              │
│   summary.exit_reason: "consecutive_failures"                   │
│                                                                 │
│ Output:                                                         │
│   ⚠️ Loop aborted after [N] consecutive failures                │
│   Last error: [error_message]                                   │
│   State saved to .caw/loop_state.json                           │
│   Resume with: /cw:loop --continue                              │
└─────────────────────────────────────────────────────────────────┘
```

**Recovery Decision Tree**:
```
ON step_failure:
  failure_count = get_step_failure_count(step_id)

  IF failure_count == 1:
    → Level 1: Retry
  ELIF failure_count == 2 AND config.auto_fix:
    → Level 2: Fixer
  ELIF failure_count == 3:
    → Level 3: Alternative
  ELIF failure_count > 3:
    IF step_is_non_blocking(step_id):
      → Level 4: Skip
    ELSE:
      → Level 5: Abort

  IF consecutive_failures >= 3:
    → Level 5: Abort
```

### Phase 4: Finalization

```
ON loop_exit:

  [1] Update Final Status
      loop_state.status = exit_reason
      loop_state.completed_at = now()

  [2] Generate Summary
      summary = {
        "total_iterations": current_iteration,
        "total_steps_completed": count(✅ steps),
        "total_errors": count(all errors),
        "exit_reason": exit_reason,
        "duration_seconds": completed_at - started_at
      }

  [3] Update Metrics (if .caw/metrics.json exists)
      metrics.loops.total += 1
      metrics.loops.last_duration = summary.duration_seconds
      metrics.loops.avg_iterations = updated_average

  [4] Display Final Report
      ┌──────────────────────────────────────────────┐
      │ /cw:loop Complete                            │
      ├──────────────────────────────────────────────┤
      │ Status: [status icon] [exit_reason]          │
      │ Iterations: [N] / [max]                      │
      │ Steps: [completed] / [total]                 │
      │ Errors: [count] ([recovered])                │
      │ Duration: [HH:MM:SS]                         │
      └──────────────────────────────────────────────┘

  [5] Invoke Reflection (if --reflect enabled)
      IF config.reflect_on_complete AND status != "paused":
        Skill tool: skill = "cw:reflect"
```

## Progress Display

### Standard Output
```
🔄 /cw:loop "Implement JWT auth"

Iteration 1/20 ━━━━━━━━━━━━━━━━━━━━
  └─ Step 1.1: Create JWT utility ✅

Iteration 2/20 ━━━━━━━━━━━━━━━━━━━━
  └─ Step 1.2: Add token validation ✅

Iteration 3/20 ━━━━━━━━━━━━━━━━━━━━
  └─ Step 2.1: Implement login endpoint ✅

...

✅ Loop Complete (all_steps_complete)

📊 Summary:
  • Iterations: 8 / 20
  • Steps: 5/5 complete
  • Errors: 1 (recovered)
  • Duration: 4m 32s

🔮 Starting reflection...
```

### Verbose Output (--verbose)
```
🔄 /cw:loop "Implement JWT auth" --verbose

══════════════════════════════════════════════════
ITERATION 1 / 20
══════════════════════════════════════════════════
  → Reading task_plan.md...
  → Next step: 1.1 Create JWT utility module
  → Invoking Builder agent...

  📝 Builder Output:
  ┌────────────────────────────────────────────────
  │ Created src/auth/jwt.ts
  │ Added tests in tests/auth/jwt.test.ts
  │ Tests: 3 passed
  └────────────────────────────────────────────────

  ✅ Outcome: success
  → Steps completed: [1.1]
  → Consecutive failures: 0
  → State saved to .caw/loop_state.json

══════════════════════════════════════════════════
ITERATION 2 / 20
══════════════════════════════════════════════════
  → Next step: 1.2 Add token validation
  ...
```

### Error Recovery Display
```
══════════════════════════════════════════════════
ITERATION 5 / 20
══════════════════════════════════════════════════
  → Step 2.1: Implement login endpoint

  ❌ Step failed: TypeScript compilation error
     src/routes/auth.ts:45 - Type 'string' is not assignable

  🔧 Recovery Level 1: Retrying...

══════════════════════════════════════════════════
ITERATION 6 / 20
══════════════════════════════════════════════════
  → Step 2.1: Implement login endpoint (retry)

  ❌ Step failed again: Same error

  🔧 Recovery Level 2: Invoking Fixer...
     → Fixer-Haiku analyzing error...
     → Fix applied: Added type annotation

  🔄 Retrying step with fix...

  ✅ Outcome: success (after recovery)
```

## State Files

### .caw/loop_state.json
Primary state file tracking loop progress:
```json
{
  "schema_version": "1.0",
  "loop_id": "loop_20240115_103045",
  "status": "running",
  "started_at": "2024-01-15T10:30:45Z",
  "task_description": "Implement JWT authentication",
  "config": {
    "max_iterations": 20,
    "completion_promise": "DONE",
    "auto_fix": true,
    "reflect_on_complete": true
  },
  "current_iteration": 5,
  "consecutive_failures": 0,
  "no_progress_count": 0,
  "completion_detected": false,
  "iterations": [
    {
      "number": 1,
      "started_at": "2024-01-15T10:30:46Z",
      "completed_at": "2024-01-15T10:32:15Z",
      "outcome": "success",
      "steps_completed": ["1.1"],
      "errors": [],
      "recovery_level": 0
    }
  ],
  "error_recovery": {
    "total_retries": 1,
    "fixer_invocations": 0,
    "planner_invocations": 0,
    "steps_skipped": []
  }
}
```

### .caw/iteration_output.md
Builder output capture for completion detection:
```markdown
# Iteration Output

## Iteration 5
- Executed step 2.1: Implement login endpoint
- Created src/routes/auth.ts
- Tests: 2 passed
- Status: Step complete

## Iteration 6
- Executed step 2.2: Add logout endpoint
- Updated src/routes/auth.ts
- All authentication endpoints DONE
```

## Integration

- **Invokes**: Builder, Fixer-Haiku, Planner-Haiku agents
- **Skills**: /cw:reflect (on completion)
- **Reads**: `.caw/task_plan.md`, `.caw/context_manifest.json`
- **Creates**: `.caw/loop_state.json`, `.caw/iteration_output.md`
- **Updates**: `.caw/task_plan.md` (via Builder), `.caw/metrics.json`

## Best Practices

1. **Clear task descriptions**: Specific tasks complete faster
2. **Use completion promises**: Add "Output DONE when complete" to task
3. **Set reasonable max-iterations**: Default 20 is good for most tasks
4. **Enable auto-fix**: Helps recover from common errors automatically
5. **Review loop_state.json**: Useful for debugging stuck loops
6. **Use --verbose for complex tasks**: Helps understand what's happening

## Comparison with /cw:auto

| Feature | /cw:loop | /cw:auto |
|---------|----------|----------|
| Focus | Iteration until done | Full workflow stages |
| Exit condition | Flexible (promise/steps/max) | Stage completion |
| Error recovery | 5-level progressive | Stop and report |
| Review/Fix | Optional (via recovery) | Built-in stages |
| Best for | Single focused task | Complete feature |

Use `/cw:loop` for: Focused tasks with clear completion criteria
Use `/cw:auto` for: End-to-end feature development with review
