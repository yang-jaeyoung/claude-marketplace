# Option A: /cw:loop Command Addition Plan

Design document for integrating dingco Ralph Loop (iteration automation) into the cw plugin

## 1. Overview

### 1.1 Purpose

The existing `/cw:auto` executes each step only once and stops on error.
`/cw:loop` provides an **autonomous agent mode that automatically repeats execution until completion conditions are met**.

### 1.2 Key Differences

| Aspect | /cw:auto | /cw:loop (New) |
|--------|----------|----------------|
| Execution Mode | Single execution per step | Repeat until complete |
| Error Handling | Stop and request manual intervention | Auto-retry/fix attempt |
| Exit Condition | All steps complete | completion-promise detection |
| Max Execution | Number of steps | max-iterations limit |

## 2. Command Specification

### 2.1 Basic Usage

```bash
# Basic usage
/cw:loop "Create REST API server and web client with integration. Output DONE when complete."

# With options
/cw:loop "Implement project" --max-iterations 30 --completion-promise "COMPLETE"

# Continue from existing task_plan
/cw:loop --continue --max-iterations 50
```

### 2.2 Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max-iterations` | 20 | Maximum iteration count (infinite loop prevention) |
| `--completion-promise` | "DONE" | Keyword indicating task completion |
| `--continue` | false | Continue execution based on existing task_plan.md |
| `--auto-fix` | true | Attempt auto-fix on error |
| `--verbose` | false | Detailed progress output |
| `--reflect` | true | Run Ralph Loop retrospective after completion |

### 2.3 Exit Conditions

Loop terminates when:

```
EXIT_CONDITIONS:
  1. completion-promise keyword appears in output
  2. max-iterations reached
  3. User manual stop (Ctrl+C)
  4. 3 consecutive identical errors (infinite failure prevention)
  5. All steps in task_plan.md are ✅ Complete
```

## 3. Implementation Architecture

### 3.1 File Structure

```
plugins/context-aware-workflow/
├── commands/
│   └── loop.md                    # New: Command definition
├── _shared/
│   └── schemas/
│       └── loop-state.schema.json # New: Loop state schema
└── hooks/
    └── hooks.json                 # Modified: Add Stop hook
```

### 3.2 Core Components

#### A. commands/loop.md

```yaml
---
description: Run autonomous loop until task completion (dingco Ralph Loop pattern)
argument-hint: "<task description>"
---
```

#### B. Loop State Management (.caw/loop_state.json)

```json
{
  "schema_version": "1.0",
  "loop_id": "loop_20240115_143022",
  "started_at": "2024-01-15T14:30:22Z",
  "status": "running",
  "config": {
    "max_iterations": 20,
    "completion_promise": "DONE",
    "auto_fix": true
  },
  "iterations": [
    {
      "number": 1,
      "started_at": "...",
      "ended_at": "...",
      "outcome": "partial",
      "steps_completed": ["1.1", "1.2"],
      "errors": [],
      "output_contains_promise": false
    }
  ],
  "current_iteration": 3,
  "consecutive_failures": 0,
  "completion_detected": false
}
```

**Schema Version Management**

```markdown
## Version Compatibility

Manage backward compatibility via schema_version field:
- "1.0": Initial version (MVP)
- "1.1": iteration_result.json integration (Phase 2)
- "2.0": Parallel loop support (Phase 4+)

## Migration Logic

When loading loop_state.json:
1. Check schema_version
2. If lower than current version: auto-migrate
3. If higher than current version: warning + read-only mode
```

#### C. Stop Hook (Completion Condition Check)

**Implementation Method**: Conditional activation based on file existence

The current cw plugin's hooks.json uses string matchers (tool name based).
Instead of a `loop_active` conditional matcher, we adopt **direct control of iteration logic within commands/loop.md**.

```markdown
## Loop Completion Check (logic within commands/loop.md)

At end of each iteration:
1. Read .caw/loop_state.json
2. Search for completion_promise in current iteration output
3. If detected → Update status to 'completed', exit loop
4. If not detected AND iterations < max → Proceed to next iteration
5. If max reached → Update status to 'max_iterations_reached'
```

**Alternative A: PreToolUse Hook (Phase 2)**

```json
{
  "PreToolUse": [
    {
      "matcher": "Task",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "IF .caw/loop_state.json exists AND status == 'running':\n  Check exit conditions before proceeding"
        }
      ]
    }
  ]
}
```

**Alternative B: Dedicated Loop Controller Agent (Phase 3)**

A separate loop-controller agent handles iteration management:
- Builder agent invocation/monitoring
- Output capture and completion_promise detection
- State update and next iteration decision

### 3.3 Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    /cw:loop "task"                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  [1] Initialize                                             │
│  ├─ Create .caw/loop_state.json                            │
│  ├─ Check .caw/context_manifest.json (bootstrap if needed) │
│  └─ Generate initial task_plan.md (if not --continue)      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  [2] Iteration N            │◄────────────────┐
        │  ├─ Execute pending steps   │                 │
        │  ├─ Handle errors (auto-fix)│                 │
        │  └─ Log iteration result    │                 │
        └─────────────┬───────────────┘                 │
                      │                                  │
                      ▼                                  │
        ┌─────────────────────────────┐                 │
        │  [3] Check Exit Conditions  │                 │
        │  ├─ completion_promise?     │                 │
        │  ├─ max_iterations?         │                 │
        │  ├─ all steps complete?     │                 │
        │  └─ consecutive failures?   │                 │
        └─────────────┬───────────────┘                 │
                      │                                  │
              ┌───────┴───────┐                         │
              │               │                         │
          CONTINUE         EXIT                         │
              │               │                         │
              └───────────────┼─────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────┐
        │  [4] Finalize               │
        │  ├─ Update loop_state       │
        │  ├─ Generate summary        │
        │  └─ Run /cw:reflect (opt)   │
        └─────────────────────────────┘
```

## 4. Detailed Design

### 4.1 Iteration Logic

```markdown
## Single Iteration Execution

FOR each iteration:

1. **Read Current State**
   - Load .caw/task_plan.md
   - Find pending steps (⏳ status)
   - Load .caw/loop_state.json for context

2. **Execute Steps**
   - Invoke Builder agent for each pending step
   - On success: Update step status to ✅
   - On failure:
     - If auto_fix enabled: Attempt Fixer agent
     - Log error to iteration record

3. **Check Progress**
   - Count completed vs total steps
   - Check if any output contains completion_promise
   - Check if new steps were added (dynamic planning)

4. **Record Iteration**
   - Save iteration result to loop_state.json
   - Update consecutive_failure counter
   - Log progress message

5. **Evaluate Exit**
   - Apply exit conditions
   - If continuing: Increment iteration, goto step 1
   - If exiting: Proceed to finalization
```

### 4.2 Error Recovery Strategy

```markdown
## Auto-Fix Strategy

Level 1: Retry
  - Same step, fresh attempt
  - Clear any cached state

Level 2: Analyze & Fix
  - Read error message
  - Invoke Fixer agent with error context
  - Apply suggested fix
  - Retry step

Level 3: Alternative Approach
  - If step fails 3 times
  - Invoke Planner to suggest alternative
  - Update task_plan.md with new approach
  - Continue with modified plan

Level 4: Skip & Continue
  - Mark step as ⏭️ Skipped with reason
  - Log to iteration errors
  - Continue to next step
  - Note: Only if step is not blocking

Level 5: Abort
  - If 3 consecutive iterations with no progress
  - Save state and exit
  - Report to user for manual intervention
```

### 4.3 Completion Promise Detection

#### Output Capture Mechanism

Methods to capture agent output in Claude Code:

**Method 1: File-based Logging (Recommended)**

```markdown
## When invoking Builder agent

1. Before Builder execution: Initialize .caw/iteration_output.md
2. Add to Builder agent system prompt:
   "Append results to .caw/iteration_output.md upon each step completion"
3. After Builder exit: Read .caw/iteration_output.md and search for completion_promise
```

**Method 2: task_plan.md Status-based (Supplementary)**

```markdown
## Implicit completion detection

Parse step status from task_plan.md:
- All steps ✅ → Implicit completion
- ⏳ or ❌ exists → Not complete
```

**Method 3: Structured Result File (Phase 3)**

```json
// .caw/iteration_result.json
{
  "iteration": 3,
  "steps_executed": ["3.1", "3.2"],
  "outputs": [
    { "step": "3.1", "result": "success", "message": "Tests created" },
    { "step": "3.2", "result": "success", "message": "All tests passing. DONE" }
  ],
  "completion_promise_found": true,
  "found_in": "step 3.2 output"
}
```

#### File Role Distinction (iteration_output.md vs iteration_result.json)

| File | Phase | Purpose | Primary Source |
|------|-------|---------|----------------|
| `iteration_output.md` | Phase 2+ | Human-readable log, completion promise detection | **Phase 2 truth** |
| `iteration_result.json` | Phase 3+ | Structured analysis data, enhanced error tracking | Phase 3+ supplementary |

**Decision Rationale**:
- Phase 2 (MVP): Use only `iteration_output.md` - Builder can write naturally
- Phase 3+: Add `iteration_result.json` - For complex error analysis, metrics collection
- `iteration_output.md` remains the primary source for completion promise detection

#### Detection Logic

```markdown
## Detection Logic

AFTER each iteration:

1. Read .caw/iteration_output.md (or iteration_result.json)
2. Normalize (lowercase, trim whitespace)
3. Check if contains completion_promise (case-insensitive)
4. Check for variations:
   - Exact match: "DONE"
   - With punctuation: "DONE!", "DONE."
   - In sentence: "Task is DONE"

IF detected:
  - Set completion_detected = true
  - Record detection context (which step, which output)
  - Proceed to finalization

ALSO check for implicit completion:
  - All steps in task_plan.md are ✅
  - No pending or blocked steps
  - Tests passing (if applicable)
```

## 5. Output Format

### 5.1 Progress Display

```
🔄 /cw:loop "REST API and web integration"

══════════════════════════════════════════════════════════════
📍 Iteration 1/20
══════════════════════════════════════════════════════════════
[1.1] Creating Express server...        ✓
[1.2] Setting up API endpoints...       ✓
[1.3] Adding CORS middleware...         ✓

Progress: 3/8 steps (37.5%)
Completion promise "DONE" not detected
Continuing to next iteration...

══════════════════════════════════════════════════════════════
📍 Iteration 2/20
══════════════════════════════════════════════════════════════
[2.1] Creating web client...            ✓
[2.2] Implementing fetch calls...       ✓
[2.3] Connecting to API...              ⚠️ Error: CORS issue

🔧 Auto-fix attempt 1/3...
   → Analyzing error...
   → Applying fix: Update CORS origin
   → Retrying step 2.3...                ✓

Progress: 6/8 steps (75%)
Completion promise "DONE" not detected
Continuing to next iteration...

══════════════════════════════════════════════════════════════
📍 Iteration 3/20
══════════════════════════════════════════════════════════════
[3.1] Writing E2E tests...              ✓
[3.2] Running full test suite...        ✓

🎯 Output: "All tests passing. DONE"

✅ Completion promise "DONE" detected!
══════════════════════════════════════════════════════════════

📊 Loop Summary
──────────────────────────────────────────────────────────────
• Iterations: 3/20
• Steps completed: 8/8 (100%)
• Errors encountered: 1 (auto-fixed)
• Duration: 4m 32s

Running /cw:reflect for continuous improvement...
```

### 5.2 Error Exit Output

```
🔄 /cw:loop "complex task"

══════════════════════════════════════════════════════════════
⚠️ Loop Stopped: Max Iterations Reached
══════════════════════════════════════════════════════════════

📊 Final Status
──────────────────────────────────────────────────────────────
• Iterations: 20/20 (limit reached)
• Steps completed: 15/23 (65%)
• Remaining steps:
  - [4.2] Integration testing     ⏳
  - [4.3] Performance tuning      ⏳
  - [5.1] Documentation           ⏳
  ...

📋 State saved to: .caw/loop_state.json

💡 To continue:
   /cw:loop --continue --max-iterations 30

💡 To review current state:
   /cw:status
```

## 6. Implementation Order

> **Design Principle**: Phase 1 is configured for minimal functionality to enable quick validation.
> Complex hook-based logic is deferred to Phase 2 and beyond.

### Phase 1: MVP (Required) - Simple Iteration Execution

```
□ 1.1 Create commands/loop.md
    - Command definition and parameter description
    - Basic iteration flow (max_iterations based exit only)
    - Builder agent invocation logic

□ 1.2 Create _shared/schemas/loop-state.schema.json
    - Loop state JSON schema definition (include schema_version)

□ 1.3 Basic exit conditions
    - Exit on max_iterations reached
    - Exit on task_plan.md all steps complete (implicit)
    - Exit on 3 consecutive failures

Goal: `/cw:loop --continue` can iterate on existing task_plan
```

### Phase 2: Completion Detection (Required)

```
□ 2.1 Output capture mechanism
    - .caw/iteration_output.md file-based logging
    - Builder agent prompt modification

□ 2.2 completion_promise detection
    - Keyword search in iteration_output.md
    - Exit loop and update state on detection

□ 2.3 Enhanced state management
    - Manage loop_state.json iterations array
    - Support restart (--continue)

Goal: `/cw:loop "task" --completion-promise "DONE"` works
```

### Phase 3: Error Handling (Recommended)

```
□ 3.1 Auto-fix integration
    - Fixer agent invocation (Level 1-2)
    - Retry logic

□ 3.2 Recovery strategy
    - Alternative approach suggestion (Level 3)
    - Skip & continue option (Level 4)

□ 3.3 iteration_result.json structuring
    - Step-by-step result recording
    - Enhanced error tracking
```

### Phase 4: Integration & Optimization (Optional)

```
□ 4.1 /cw:reflect integration
    - Auto-retrospective after loop completion

□ 4.2 Context management
    - Auto-cleanup every 5 iterations
    - Serena memory storage

□ 4.3 Test writing
    - Loop scenario tests
    - Edge case verification
```

### Phase 5: Advanced Features (Future)

```
□ 5.1 /cw:auto --review-loop integration
    - Reuse loop logic in auto.md

□ 5.2 PreToolUse Hook-based conditional activation
    - Hook that operates only when loop is active

□ 5.3 Loop Controller Agent
    - Separate iteration management to dedicated agent
```

## 7. Relationship with Existing Features

### 7.1 Difference from /cw:auto

```
/cw:auto:
├─ 7-step sequential execution
├─ Stop on error
├─ Manual intervention required
└─ Goal: Complete in one pass

/cw:loop:
├─ N iteration execution
├─ Auto-recovery on error
├─ Autonomous progress
└─ Goal: Repeat until complete
```

### 7.2 Relationship with /cw:reflect

```
After /cw:loop completion:
└─ Automatically invoke /cw:reflect (--reflect option)
    └─ Run Ralph Loop retrospective cycle
        ├─ Reflect: Review loop execution
        ├─ Analyze: Analyze iteration patterns
        ├─ Learn: Learn automation improvements
        ├─ Plan: Optimize next loop
        └─ Habituate: Save learnings
```

### 7.3 Naming Clarification

| Command | Meaning | Origin |
|---------|---------|--------|
| `/cw:loop` | Iteration automation | dingco Ralph Loop |
| `/cw:reflect` | Retrospective cycle (RALPH) | cw existing implementation |
| `/cw:auto` | Single-pass automation | cw existing implementation |

## 8. Risks and Considerations

### 8.1 Infinite Loop Prevention

```
Safeguards:
1. max_iterations required (default 20)
2. Stop on 3 consecutive identical errors
3. Stop on 3 iterations with no progress
4. User interrupt support (Ctrl+C)
```

### 8.2 Resource Management

```
Considerations:
- Context exhaustion from long execution
- Increased API call costs
- File system state management
```

#### Context Window Management Strategy

```markdown
## Per-Iteration Context Optimization

At each iteration start:
1. Keep previous iteration detailed logs only in loop_state.json
2. Load only minimal info needed for current iteration:
   - task_plan.md (only current pending steps)
   - loop_state.json (config + current_iteration only)
3. Auto-cleanup when conversation context reaches threshold (Phase 3)

## File-based State Separation

Keep in context:           Store in files only:
├─ Current iteration info   ├─ Previous iterations detail
├─ Current step list        ├─ Error history
└─ completion config        └─ Modification history
```

**Auto Context Cleanup (Phase 3 Implementation)**:
```
## Auto Cleanup Trigger

Implementation: Phase 3

Trigger conditions:
- Every 5 iterations auto-run
- Or when loop_state.json iterations array size > 10

Cleanup actions:
1. Compress old iteration details in loop_state.json to summary
2. Convert iteration_output.md content to summary, then reinitialize
3. Keep only current progress and last 3 iterations
```

#### Cost Management

```markdown
## API Call Optimization

1. Limit Builder agent to only read necessary files
2. Minimize repeated context loading
3. Default --verbose=false to minimize output

## Estimated Cost (Reference)

Per iteration average:
- Sonnet calls: 3-5
- Tokens: ~10K input, ~3K output

For 20 iterations:
- Total calls: 60-100
- Total tokens: ~200K input, ~60K output
```

#### Mitigation Measures

```
- Save state after each iteration (recoverable)
- Progress-based intermediate checkpoints
- Set upper limit with --max-iterations
- Consider auto context cleanup every 5 iterations (Phase 3)
```

### 8.3 Existing Feature Compatibility

```
Guarantees:
- No change to existing /cw:auto behavior
- No change to existing /cw:reflect behavior
- Use same task_plan.md format
- Reuse same agents
```

## 9. Future Extension Possibilities

### 9.1 Parallel Loops

```bash
# Multiple task concurrent execution
/cw:loop "API development" --worktree api &
/cw:loop "UI development" --worktree ui &
```

### 9.2 Conditional Branching

```bash
# Conditional branch execution
/cw:loop "Until tests pass" --until "all tests pass"
/cw:loop "Achieve 80% coverage" --until "coverage >= 80%"
```

### 9.3 Scheduling

```bash
# Scheduled execution
/cw:loop "Regular refactoring" --schedule "weekly"
```

## 10. Use Cases

### 10.1 Review-Fix Loop

Automatically repeat review and fix until no High severity or above issues in code review.

#### Usage

```bash
/cw:loop "Code review then fix High+ issues. Output REVIEW_PASSED if no issues" \
  --completion-promise "REVIEW_PASSED" \
  --max-iterations 10
```

#### Internal Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Iteration N                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  [1] Run /cw:review         │
        │  → .caw/review_result.json  │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  [2] Analyze results        │
        │  ├─ Critical issues?        │
        │  └─ High issues?            │
        └─────────────┬───────────────┘
                      │
              ┌───────┴───────┐
              │               │
        Found (≥1)        None (0)
              │               │
              ▼               ▼
   ┌──────────────────┐  ┌──────────────────┐
   │ [3a] /cw:fix     │  │ [3b] Output:     │
   │ → Fix issues     │  │ "REVIEW_PASSED"  │
   │ → Next iteration │  │ → Exit loop      │
   └──────────────────┘  └──────────────────┘
```

#### Review Result Schema Extension

```json
// .caw/review_result.json
{
  "review_id": "review_20240115_150000",
  "timestamp": "2024-01-15T15:00:00Z",
  "issues": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 12,
    "info": 8
  },
  "details": [
    {
      "severity": "high",
      "category": "security",
      "file": "src/auth/jwt.ts",
      "line": 42,
      "message": "JWT secret is hardcoded",
      "suggestion": "Use environment variable"
    }
  ],
  "pass_threshold": {
    "critical": 0,
    "high": 0
  },
  "passed": false
}
```

#### Output Example

```
🔄 /cw:loop "Review-Fix until clean"

══════════════════════════════════════════════════════════════
📍 Iteration 1/10
══════════════════════════════════════════════════════════════
🔍 Running /cw:review...

📊 Review Results:
   Critical: 0 | High: 2 | Medium: 5 | Low: 12

⚠️ High severity issues found:
   [1] src/auth/jwt.ts:42 - JWT secret is hardcoded
   [2] src/api/user.ts:88 - SQL injection vulnerability

🔧 Running /cw:fix...
   → Fixing issue 1/2: JWT secret...     ✓
   → Fixing issue 2/2: SQL injection...  ✓

Continuing to next iteration...

══════════════════════════════════════════════════════════════
📍 Iteration 2/10
══════════════════════════════════════════════════════════════
🔍 Running /cw:review...

📊 Review Results:
   Critical: 0 | High: 0 | Medium: 4 | Low: 12

✅ No Critical or High severity issues!

🎯 Output: "REVIEW_PASSED"

══════════════════════════════════════════════════════════════
✅ Completion promise "REVIEW_PASSED" detected!
══════════════════════════════════════════════════════════════

📊 Loop Summary
──────────────────────────────────────────────────────────────
• Iterations: 2/10
• Issues fixed: 2 High
• Remaining: 4 Medium, 12 Low (below threshold)
• Duration: 1m 45s

💡 To fix remaining issues:
   /cw:loop "Fix up to Medium issues. Output ALL_CLEAN when done" \
     --completion-promise "ALL_CLEAN"
```

#### Extension: Condition-based Exit (Phase 2)

Adding `--until` parameter in Phase 2 enables more flexible condition specification:

```bash
# Expression-based exit condition
/cw:loop review-fix \
  --until "review.issues.high == 0 && review.issues.critical == 0" \
  --max-iterations 10

# Threshold-based
/cw:loop review-fix \
  --severity-threshold medium \
  --max-iterations 15
```

#### loop_state.json Extension

```json
{
  "loop_id": "loop_20240115_150000",
  "mode": "review-fix",
  "config": {
    "completion_promise": "REVIEW_PASSED",
    "max_iterations": 10,
    "exit_condition": {
      "type": "review_threshold",
      "max_severity": "medium",
      "data_source": ".caw/review_result.json"
    }
  },
  "iterations": [
    {
      "number": 1,
      "review_result": {
        "critical": 0,
        "high": 2,
        "medium": 5
      },
      "issues_fixed": ["jwt_secret", "sql_injection"],
      "passed": false
    },
    {
      "number": 2,
      "review_result": {
        "critical": 0,
        "high": 0,
        "medium": 4
      },
      "issues_fixed": [],
      "passed": true
    }
  ],
  "completion_detected": true
}
```

### 10.2 Test-Fix Loop

Repeat until all tests pass:

```bash
/cw:loop "Run tests and fix failures. Output ALL_TESTS_PASS when all pass" \
  --completion-promise "ALL_TESTS_PASS" \
  --max-iterations 15
```

### 10.3 Build-Fix Loop

Repeat until no build errors:

```bash
/cw:loop "Run build and fix errors. Output BUILD_SUCCESS on success" \
  --completion-promise "BUILD_SUCCESS" \
  --max-iterations 10
```

### 10.4 Combined Quality Loop

Sequential pass through multiple quality gates:

```bash
/cw:loop "Pass build, tests, lint, and review. Output QUALITY_GATE_PASSED when all pass" \
  --completion-promise "QUALITY_GATE_PASSED" \
  --max-iterations 20
```

Internal operation:
```
FOR each iteration:
  1. npm run build     → Fix on failure
  2. npm test          → Fix on failure
  3. npm run lint      → Fix on failure
  4. /cw:review        → Fix on High+ issues
  5. All pass → "QUALITY_GATE_PASSED"
```

## 11. /cw:auto Integration Plan

Plan to integrate loop pattern into existing `/cw:auto`'s review → fix stages.

> **Duplication Prevention Principle**: `/cw:auto --review-loop` **reuses** `/cw:loop` logic.
> Uses internal invocation rather than separate implementation to avoid code duplication.

### 11.1 Current /cw:auto Workflow

```
[1/7] init     → Environment initialization
[2/7] start    → Plan generation
[3/7] next     → Step execution
[4/7] review   → Code review (once)
[5/7] fix      → Issue fix (once)
[6/7] check    → Compliance check
[7/7] reflect  → Retrospective
```

**Problem**: review-fix runs only once, may leave High issues

### 11.2 Proposal: Add --review-loop Flag

```bash
# Existing behavior (single review-fix) - backward compatible
/cw:auto "task"

# Review-Fix Loop mode activated
/cw:auto "task" --review-loop

# With options
/cw:auto "task" --review-loop --max-review-iterations 5 --review-threshold high
```

### 11.3 New Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--review-loop` | false | Run Review-Fix in iteration mode |
| `--max-review-iterations` | 5 | Max Review-Fix iteration count |
| `--review-threshold` | high | Iterate on this severity and above (critical, high, medium) |

### 11.4 Modified Workflow

```
[1/6] init
[2/6] start
[3/6] next
[4/6] review-fix-loop  ← Conditional iteration
      │
      ├─► review
      │     ↓
      │   High issues?
      │     ├─ YES → fix → next iteration
      │     └─ NO  → exit loop
      │
      └─► Safeguard: Exit on max-review-iterations reached
[5/6] check
[6/6] reflect
```

### 11.5 Exit Conditions

```
Review-Fix Loop exit conditions:
  1. Zero issues at review-threshold severity or above
  2. max-review-iterations reached
  3. 2 consecutive identical issues (unfixable determination)
```

### 11.6 Output Example

```
🚀 /cw:auto "Add logout button" --review-loop

[1/6] Initializing...     ✓
[2/6] Planning...         ✓ (2 phases, 5 steps)
[3/6] Executing...        ✓ (5/5 steps complete)
[4/6] Review-Fix Loop...
      ├─ Iteration 1/5: 2 High issues found
      │   🔧 Fixing: JWT secret hardcoded... ✓
      │   🔧 Fixing: SQL injection risk... ✓
      ├─ Iteration 2/5: 1 High issue found
      │   🔧 Fixing: Missing input validation... ✓
      └─ Iteration 3/5: 0 High issues ✓
[5/6] Checking...         ✓ (compliant)
[6/6] Reflecting...       ✓

✅ Workflow Complete

📊 Summary:
  • Steps executed: 5
  • Review-Fix iterations: 3
  • Issues fixed: 3 High, 2 Medium (auto)
  • Remaining: 4 Low (below threshold)
  • Compliance: Pass
```

### 11.7 Error Handling

#### Max Iterations Reached

```
[4/6] Review-Fix Loop...
      ├─ Iteration 1/5: 3 High issues → fixed 2
      ├─ Iteration 2/5: 2 High issues → fixed 1
      ├─ Iteration 3/5: 2 High issues → fixed 1
      ├─ Iteration 4/5: 2 High issues → fixed 0 ⚠️
      └─ Iteration 5/5: 2 High issues → MAX REACHED

⚠️ Review-Fix Loop: Max iterations reached

📋 Remaining High Issues (2):
  1. src/auth/oauth.ts:88 - Complex refactoring needed
  2. src/api/upload.ts:156 - Architecture change required

💡 Options:
  1. Fix manually and run: /cw:review
  2. Continue without fixing: /cw:check
  3. Increase limit: /cw:auto --continue --max-review-iterations 10
```

#### Unfixable Issue Detected

```
[4/6] Review-Fix Loop...
      ├─ Iteration 1/5: 2 High issues → fixed 1
      ├─ Iteration 2/5: 1 High issue → fixed 0
      └─ Iteration 3/5: 1 High issue → same issue detected ⚠️

⚠️ Review-Fix Loop: Unfixable issue detected

📋 Unfixable Issue:
  src/legacy/parser.ts:234
  "Deprecated API usage requires manual migration"

💡 This issue cannot be auto-fixed. Options:
  1. Fix manually and resume: /cw:auto --continue
  2. Skip and continue: /cw:check
  3. Add to tech debt: /cw:defer
```

### 11.8 session.json Extension

```json
{
  "auto_mode": {
    "active": true,
    "current_stage": 4,
    "options": {
      "review_loop": true,
      "max_review_iterations": 5,
      "review_threshold": "high"
    }
  },
  "review_loop_state": {
    "current_iteration": 3,
    "iterations": [
      {
        "number": 1,
        "issues_found": { "high": 2, "medium": 3 },
        "issues_fixed": { "high": 2, "medium": 1 },
        "unfixable": []
      },
      {
        "number": 2,
        "issues_found": { "high": 1, "medium": 2 },
        "issues_fixed": { "high": 1, "medium": 0 },
        "unfixable": []
      },
      {
        "number": 3,
        "issues_found": { "high": 0, "medium": 2 },
        "issues_fixed": {},
        "passed": true
      }
    ],
    "total_fixed": { "high": 3, "medium": 1 },
    "completion_reason": "threshold_met"
  }
}
```

### 11.9 Implementation Priority

```
Phase 1 (MVP):
  □ --review-loop flag parsing
  □ Basic iteration logic (max-review-iterations)
  □ High issue threshold exit condition

Phase 2 (Enhanced):
  □ --review-threshold parameter
  □ Unfixable issue detection
  □ session.json state persistence

Phase 3 (Polish):
  □ Detailed output format
  □ --continue resume support
  □ Test writing
```

### 11.10 Relationship with /cw:loop

| Command | Purpose | Review-Fix | Implementation |
|---------|---------|------------|----------------|
| `/cw:auto` | Full workflow | Once (default) | Existing |
| `/cw:auto --review-loop` | Full workflow | N times (loop) | **Reuse loop.md** |
| `/cw:loop` | Generic iteration | Customizable | New (core) |

**Architecture**:
```
/cw:auto --review-loop
    │
    ├─ [1-3] init → start → next (existing logic)
    │
    └─ [4] review-fix-loop
           │
           └─► Internally invoke /cw:loop logic
               - completion_promise: "REVIEW_PASSED"
               - task: "Review and fix High+ issues"
               - max_iterations: --max-review-iterations value
```

**Differences**:
- `/cw:auto --review-loop`: Only iterate review-fix within full workflow (reuses loop.md logic)
- `/cw:loop`: Independent generic iteration (various patterns beyond review-fix)

**Implementation Priority**:
1. Implement `/cw:loop` first (Phase 1-2)
2. Implement `/cw:auto --review-loop` as loop logic reuse (Phase 5)

**Usage Scenarios**:
```bash
# Full task automation + quality assurance
/cw:auto "implement feature" --review-loop

# Review-fix only, separate execution
/cw:loop "Review and fix High+ issues. Output DONE when complete" --max-iterations 10

# Improve existing code quality (without full workflow)
/cw:loop "Full codebase review and fix" --completion-promise "ALL_CLEAN"
```

---

## Appendix: References

- [dingco Ralph Loop](https://github.com/dingcodingco/dingco-ralph-wiggum)
- [Existing /cw:auto implementation](../commands/auto.md)
- [Existing /cw:reflect implementation](../skills/reflect/SKILL.md)
