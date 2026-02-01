---
description: Run autonomous loop until task completion (dingco Ralph Loop pattern)
argument-hint: "<task description>"
---

# /cw:loop - Autonomous Execution Loop

Run tasks autonomously until completion. Repeatedly executes Builder agent until done, max iterations reached, or all steps complete.

## Usage

```bash
/cw:loop "Implement user authentication with JWT"
/cw:loop --continue                              # Resume interrupted
/cw:loop "Add dark mode" --max-iterations 30
/cw:loop "Fix errors" --completion-promise "ALL_FIXED"
/cw:loop "Critical fix" --no-auto-fix            # Disable auto-fix
/cw:loop "Quick refactor" --no-reflect           # Skip reflection
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max-iterations` | 20 | Maximum iterations |
| `--completion-promise` | "DONE" | Keyword for early completion |
| `--continue` | false | Resume from loop_state.json |
| `--auto-fix` | true | Enable Fixer for error recovery |
| `--no-auto-fix` | - | Disable auto-fix |
| `--reflect` | true | Run /cw:reflect after completion |
| `--no-reflect` | - | Skip reflection |
| `--verbose` | false | Detailed progress |
| `--qa-each-step` | false | Run QA after each step |

## Exit Conditions

| Condition | Status |
|-----------|--------|
| Completion Promise detected | `completed` |
| All steps ✅ | `completed` |
| Max iterations reached | `max_iterations_reached` |
| 3+ consecutive failures | `failed` |
| Critical error | `failed` |
| User abort | `paused` |

## Execution Flow

### Phase 1: Initialization
1. Check for existing `.caw/loop_state.json`
2. Verify prerequisites (context_manifest.json, task_plan.md)
3. Initialize loop state

### Phase 2: Iteration Loop

```
WHILE running:
  1. Check max iterations
  2. Execute Builder Agent for next pending step
  3. Capture output to .caw/iteration_output.md
  4. Analyze results (success/failure/no_progress)
  5. Check for completion promise
  6. Check if all steps complete
  7. On failure → Apply Error Recovery
  8. Record iteration and save state
```

### Phase 3: Error Recovery (5 Levels)

| Level | Trigger | Action |
|-------|---------|--------|
| 1 | 1st failure | Retry step |
| 2 | 2nd failure | Invoke Fixer-Haiku |
| 3 | 3rd failure | Invoke Planner-Haiku for alternative |
| 4 | 4th failure (non-blocking) | Skip step |
| 5 | 3+ consecutive or blocking | Abort loop |

### Phase 4: Finalization
Update status, generate summary, invoke /cw:reflect if enabled.

## Progress Display

```
🔄 /cw:loop "Implement JWT auth"

Iteration 1/20 ━━━━━━━━━━━━━━━━━━━━
  └─ Step 1.1: Create JWT utility ✅

Iteration 2/20 ━━━━━━━━━━━━━━━━━━━━
  └─ Step 1.2: Add token validation ✅

...

✅ Loop Complete (all_steps_complete)

📊 Summary:
  • Iterations: 8 / 20
  • Steps: 5/5 complete
  • Errors: 1 (recovered)

🔮 Starting reflection...
```

Use `--verbose` for detailed iteration output.

## State Management

State saved in `.caw/loop_state.json`:
```json
{
  "schema_version": "1.0",
  "status": "running",
  "task_description": "Implement JWT",
  "config": { "max_iterations": 20, "auto_fix": true },
  "current_iteration": 5,
  "consecutive_failures": 0,
  "iterations": [...]
}
```

Builder output captured in `.caw/iteration_output.md` for completion detection.

## Integration

- **Invokes**: Builder, Fixer-Haiku, Planner-Haiku agents
- **Skills**: /cw:reflect (on completion)
- **Reads**: `.caw/task_plan.md`, `.caw/context_manifest.json`
- **Creates**: `.caw/loop_state.json`, `.caw/iteration_output.md`
- **Updates**: `.caw/task_plan.md`, `.caw/metrics.json`

## Best Practices

1. Clear task descriptions complete faster
2. Add "Output DONE when complete" for early exit
3. Default 20 max-iterations suits most tasks
4. Enable auto-fix for automatic error recovery
5. Use --verbose for debugging stuck loops

## vs /cw:auto

| Feature | /cw:loop | /cw:auto |
|---------|----------|----------|
| Focus | Iteration until done | Full workflow stages |
| Exit condition | Flexible | Stage completion |
| Error recovery | 5-level progressive | Stop and report |
| Best for | Focused task | Complete feature |
