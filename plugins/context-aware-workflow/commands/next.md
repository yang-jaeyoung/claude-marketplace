---
description: Execute the next pending step from task_plan.md using the Builder agent
---

# /caw:next - Execute Next Step

Automatically proceed with the next pending step from the task plan, invoking the Builder agent for TDD-based implementation.

## Usage

```bash
/caw:next              # Execute next pending step
/caw:next --all        # Execute all steps in current phase (sequential)
/caw:next --step 2.3   # Execute specific step
/caw:next --parallel   # Execute all runnable steps in parallel
/caw:next --batch 3    # Execute up to 3 steps in parallel
/caw:next --worktree   # Create worktrees for parallel execution (see /caw:worktree)
```

## Behavior

### Step 1: Validate Task Plan

1. Check for `.caw/task_plan.md`
2. If not found, display error:

```
❌ No active workflow

.caw/task_plan.md not found.

💡 Start a workflow first:
   /caw:start "your task description"
   /caw:start --from-plan
```

### Step 2: Parse Current State

Read `.caw/task_plan.md` and identify:
- Current Phase being worked on
- Next actionable step based on mode:
  - **Default**: First step with ⏳ (Pending) status
  - **--step N.M**: Specified step number
  - **--all**: All pending steps in current phase

### Step 3: Validate Step

Before execution, verify:
- Step exists in task_plan.md
- Step is not already ✅ Complete
- No blocking dependencies (❌ Blocked steps before it)

**Dependency Check**:
```
If step 2.3 requested but 2.1 or 2.2 are ❌ Blocked:
  → Display warning with blocker details
  → Ask user to resolve or skip
```

### Step 4: Invoke Builder Agent

Call the Builder agent via Task tool with context:

```markdown
## Builder Agent Invocation

**Task**: Implement step [N.M] from .caw/task_plan.md

**Step Details**:
- Description: [Step description from plan]
- Phase: [Current phase name]
- Notes: [Any notes from plan]

**Context Files**:
[List from task_plan.md Active Context section]

**Instructions**:
1. Read the step requirements from .caw/task_plan.md
2. Follow TDD approach (test first, then implement)
3. Run tests automatically after implementation
4. Update .caw/task_plan.md status upon completion
```

### Step 5: Report Results

After Builder agent completes:

**Success Output**:
```
✅ Step [N.M] Complete

📋 [Step description]

Changes:
  • Created: src/auth/jwt.ts
  • Modified: src/middleware/auth.ts
  • Tests: 3 passed, 0 failed

📊 Progress: 50% (5/10 steps)

💡 Next: /caw:next to continue with step [N.M+1]
```

**Failure Output**:
```
❌ Step [N.M] Failed

📋 [Step description]

Error:
  🧪 Tests failed: 1 failed, 2 passed

  FAIL: should validate token expiration
  Expected: TokenExpiredError
  Received: undefined

💡 Options:
   • Review the error and fix manually
   • /caw:next --step [N.M] to retry
   • /caw:status to see full progress
```

## Execution Modes

### Default Mode (Single Step)

```bash
/caw:next
```

- Finds first ⏳ Pending step
- Executes only that step
- Reports result and suggests next action

### All Mode (Current Phase)

```bash
/caw:next --all
```

- Identifies current phase (first phase with pending steps)
- Executes all pending steps in that phase sequentially
- Stops on first failure
- Reports cumulative progress

**Output**:
```
🚀 Executing Phase 2: Core Implementation

Step 2.1: Create JWT utility...
  ✅ Complete (tests: 3/3 passed)

Step 2.2: Add auth middleware...
  ✅ Complete (tests: 5/5 passed)

Step 2.3: Implement login endpoint...
  ❌ Failed (tests: 2/4 passed)

──────────────────────────────────────────
📊 Phase 2 Progress: 66% (2/3 steps)
⚠️ Stopped at step 2.3 due to test failure

💡 Fix the issue and run /caw:next to continue
```

### Specific Step Mode

```bash
/caw:next --step 2.3
```

- Executes the specified step regardless of order
- Warns if dependencies are incomplete
- Updates status for that specific step

### Parallel Mode (Same Session)

```bash
/caw:next --parallel
/caw:next --batch 3
```

**Prerequisites**: Task plan must have `Deps` column. If missing, falls back to sequential.

**Workflow**:
1. **Analyze Dependencies**: Use `dependency-analyzer` skill to find runnable steps
2. **Identify Parallel Group**: Steps with same dependencies and different target files
3. **Launch Parallel Builders**: Invoke multiple Builder agents via Task tool in single message
4. **Aggregate Results**: Collect all results, batch update task_plan.md
5. **Report Summary**: Show parallel execution results

**Example**:
```
🚀 Parallel Execution Mode

Runnable steps identified:
  ⚡ 2.2 - Implement token generation
  ⚡ 2.3 - Implement token validation

Launching 2 Builder agents in parallel...

Results:
  ✅ 2.2 Complete (45s, tests: 3/3)
  ✅ 2.3 Complete (38s, tests: 4/4)

⏱️ Total: 48s (vs ~83s sequential)
📈 Speedup: 1.7x

💡 Next: /caw:next --parallel to continue
```

**Batch Mode**:
```bash
/caw:next --batch 3   # Max 3 concurrent steps
```

Limits concurrent execution to prevent resource exhaustion. Remaining runnable steps execute in next batch.

### Worktree Mode (Multi-Session)

```bash
/caw:next --worktree
```

**When to Use**:
- Large independent branches requiring full isolation
- Steps that modify many files in same subsystem
- When single-session parallel has conflict risk

**Workflow**:
1. **Analyze for Worktree**: Identify steps suitable for isolation
2. **Create Worktrees**: Generate `.worktrees/caw-step-N.M/` directories
3. **Output Guide**: Print terminal commands for user
4. **User Executes**: User opens terminals and runs commands
5. **Merge**: User runs `/caw:merge` when complete

**Output**:
```
🌳 Worktree Mode Activated

Creating worktrees for parallel execution:
  ✓ .worktrees/caw-step-2.2/ (branch: caw/step-2.2)
  ✓ .worktrees/caw-step-2.3/ (branch: caw/step-2.3)

📋 Run these commands in separate terminals:

Terminal 1:
  cd .worktrees/caw-step-2.2 && claude
  /caw:next --step 2.2

Terminal 2:
  cd .worktrees/caw-step-2.3 && claude
  /caw:next --step 2.3

After all complete, return here and run:
  /caw:merge
```

**See Also**: `/caw:worktree`, `/caw:merge`

## Edge Cases

### All Steps Complete

```
🎉 Workflow Complete!

All steps in .caw/task_plan.md are finished.

📊 Final Progress: 100% (10/10 steps)

💡 Suggested actions:
   • Review the implementation
   • Run full test suite: npm test
   • Start new workflow: /caw:start "next task"
```

### Blocked Steps

```
⚠️ Cannot proceed

Step 2.3 is blocked by incomplete dependencies:
  ❌ 2.1: Missing database configuration
  ❌ 2.2: Depends on 2.1

💡 Options:
   • Resolve blockers manually
   • /caw:next --step 2.1 to work on blocker
   • Update .caw/task_plan.md to mark as ⏭️ Skipped
```

### No Pending Steps in Current Phase

```
✅ Phase 2 Complete

All steps in Phase 2: Core Implementation are done.

💡 Moving to Phase 3: Testing
   /caw:next to start step 3.1
```

## Builder Agent Integration

The `/caw:next` command delegates implementation to the Builder agent:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   /caw:next     │────▶│  Builder Agent  │────▶│.caw/task_plan.md│
│   (Command)     │     │  (Implementer)  │     │  (State Store)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │  1. Parse plan        │  2. TDD implement    │
        │  2. Find next step    │  3. Run tests        │
        │  3. Invoke Builder    │  4. Update status    │
        │  4. Report results    │                       │
        ▼                       ▼                       ▼
```

## Status Icons Reference

| Icon | Status | Action |
|------|--------|--------|
| ⏳ | Pending | Ready to execute |
| 🔄 | In Progress | Currently being worked on |
| ✅ | Complete | Skip, already done |
| ❌ | Blocked | Cannot proceed, show warning |
| ⏭️ | Skipped | Skip, intentionally bypassed |

## Integration

- **Reads**: `.caw/task_plan.md`
- **Invokes**: Builder agent via Task tool
- **Updates**: `.caw/task_plan.md` (via Builder)
- **Suggests**: `/caw:status`, `/caw:next`
