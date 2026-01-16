---
description: Execute the next pending step from task_plan.md using the Builder agent
---

# /caw:next - Execute Next Step

Automatically proceed with the next pending step from the task plan, invoking the Builder agent for TDD-based implementation.

## Usage

```bash
# Basic (existing)
/caw:next                      # Execute next pending step
/caw:next --all                # Execute all steps in current phase (sequential, lightweight)
/caw:next --step 2.3           # Execute specific step

# Phase-based execution (NEW)
/caw:next phase 1              # Execute Phase 1 sequentially
/caw:next --parallel phase 1   # Execute Phase 1 with background agents
/caw:next --worktree phase 2   # Create worktree for Phase 2
/caw:next --parallel --worktree phase 2  # Create worktree with parallel hint

# Batch control
/caw:next --batch 3            # Execute up to 3 steps in parallel
```

## Flags

| Flag | Description |
|------|-------------|
| `--all` | 현재 phase 순차 실행 (가벼운 작업용, 기존 호환) |
| `--parallel` | Background agent로 병렬 실행 |
| `--worktree` | Phase 단위 worktree 생성 |
| `--step N.M` | 특정 step 실행 |
| `--batch N` | 최대 N개 병렬 실행 |
| `phase N` | Phase 번호 지정 (positional argument) |

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
- Phase Deps for dependency validation
- Next actionable step based on mode

### Step 3: Validate Dependencies

**Phase Dependency Check** (for phase-based execution):

```
Checking Phase 2 dependencies...

**Phase Deps**: phase 1

Phase 1 status:
├─ Step 1.1: ✅ Complete
├─ Step 1.2: ✅ Complete
└─ Step 1.3: ✅ Complete

✅ All dependencies satisfied. Proceeding with Phase 2.
```

If dependencies not met:
```
⚠️ Phase 3 cannot start

Dependencies not satisfied:
  Phase 2: 🔄 In Progress (3/5 steps complete)

Options:
  [1] Wait for Phase 2 to complete
  [2] Start anyway (may cause issues)
  [3] View Phase 2 status
```

### Step 4: Execute Based on Mode

---

## Execution Modes

### Mode 1: Default (Single Step)

```bash
/caw:next
```

- Finds first ⏳ Pending step
- Invokes Builder agent (blocking)
- Updates task_plan.md status
- Reports result and suggests next action

### Mode 2: Sequential All (Lightweight)

```bash
/caw:next --all
```

- Identifies current phase (first phase with pending steps)
- Executes all pending steps sequentially
- Stops on first failure
- **Best for**: Simple tasks, few steps

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

### Mode 3: Phase Sequential

```bash
/caw:next phase 2
```

1. Validate Phase 2 dependencies (Phase Deps)
2. Execute all pending steps in Phase 2 sequentially
3. Stop on failure

**Output**:
```
🚀 Phase 2: Core Implementation

Checking dependencies...
  Phase Deps: phase 1 ✅

Executing steps:
  2.1 Create JWT utility... ✅
  2.2 Implement middleware... ✅
  2.3 Add login endpoint... ✅

──────────────────────────────────────────
📊 Phase 2: Complete (3/3 steps)

💡 Next: /caw:next phase 3
```

### Mode 4: Phase Parallel (Background Agents)

```bash
/caw:next --parallel phase 1
```

1. Validate Phase 1 dependencies
2. Analyze step dependencies within phase
3. Group steps into parallel batches
4. Launch Builder agents with `run_in_background=true`
5. Return immediately with monitoring info

**Step Grouping Logic**:
```
Phase 1 Steps:
  1.1 (Deps: -)     ─┐
  1.2 (Deps: -)     ─┼─ Wave 1: All parallel (no deps)
  1.3 (Deps: -)     ─┘
  1.4 (Deps: 1.1)   ─── Wave 2: After 1.1
  1.5 (Deps: 1.2,1.3)── Wave 3: After 1.2, 1.3
```

**Output**:
```
🚀 Phase 1: Background Parallel Execution

Analyzing dependencies...
  Wave 1: [1.1, 1.2, 1.3] - All independent
  Wave 2: [1.4] - After 1.1
  Wave 3: [1.5] - After 1.2, 1.3

Launching Wave 1 (3 background agents):
  ⚡ Step 1.1 - Install dependencies (task_id: abc123)
  ⚡ Step 1.2 - Add type definitions (task_id: def456)
  ⚡ Step 1.3 - Setup test fixtures (task_id: ghi789)

📋 Monitor progress:
  /caw:status --agents     # Check all agent status
  TaskOutput abc123        # Get specific agent output

⏳ Wave 2, 3 will execute after Wave 1 completes.
   Run /caw:next --parallel phase 1 again to continue.
```

**Technical Implementation**:
```
For each step in parallel group:
  Task tool:
    subagent_type: "caw:builder"
    prompt: "Execute step N.M from .caw/task_plan.md"
    run_in_background: true
```

### Mode 5: Worktree (Phase Isolation)

```bash
/caw:next --worktree phase 2
```

1. Validate Phase 2 dependencies
2. Create `.worktrees/phase-2/` directory
3. Create git branch `caw/phase-2`
4. Copy `.caw/` state to worktree
5. Output terminal commands

**Output**:
```
🌳 Worktree Created for Phase 2

Checking dependencies...
  Phase Deps: phase 1 ✅

Creating worktree:
  ✓ Directory: .worktrees/phase-2/
  ✓ Branch: caw/phase-2
  ✓ Copied: .caw/task_plan.md

📋 Execute in new terminal:

  cd .worktrees/phase-2 && claude
  /caw:next phase 2              # Sequential execution
  # or
  /caw:next --parallel phase 2   # Parallel execution

After complete, return to main and run:
  /caw:merge
```

### Mode 6: Worktree + Parallel Hint

```bash
/caw:next --parallel --worktree phase 2
```

Same as Mode 5, but with parallel execution hint:

**Output**:
```
🌳 Worktree Created for Phase 2 (Parallel Mode)

Checking dependencies...
  Phase Deps: phase 1 ✅

Creating worktree:
  ✓ Directory: .worktrees/phase-2/
  ✓ Branch: caw/phase-2
  ✓ Copied: .caw/task_plan.md

📋 Execute in new terminal:

  cd .worktrees/phase-2 && claude
  /caw:next --parallel phase 2   # Background parallel execution

After complete, return to main and run:
  /caw:merge
```

### Mode 7: Specific Step

```bash
/caw:next --step 2.3
```

- Executes the specified step regardless of order
- Warns if dependencies are incomplete
- Updates status for that specific step

---

## Multi-Terminal Parallel Workflow

여러 터미널에서 동시에 다른 Phase 작업:

```bash
# 메인 터미널: Phase 1 완료 확인
/caw:status

# 터미널 1
/caw:next --worktree phase 2
cd .worktrees/phase-2 && claude
/caw:next --parallel phase 2

# 터미널 2
/caw:next --worktree phase 3
cd .worktrees/phase-3 && claude
/caw:next --parallel phase 3

# 터미널 3
/caw:next --worktree phase 4
cd .worktrees/phase-4 && claude
/caw:next phase 4  # Sequential if preferred

# 모든 작업 완료 후 메인 터미널에서
/caw:merge --all
```

**Prerequisites for Multi-Phase Parallel**:
- Phase들이 동일한 Phase Deps를 가져야 함
- 또는 각 Phase의 dependencies가 이미 완료됨

---

## Edge Cases

### All Steps Complete

```
🎉 Workflow Complete!

All steps in .caw/task_plan.md are finished.

📊 Final Progress: 100% (10/10 steps)

💡 Suggested actions:
   • /caw:review - Review implementation
   • Run full test suite: npm test
   • /caw:start "next task" - Start new workflow
```

### Blocked Steps

```
⚠️ Cannot proceed

Step 2.3 is blocked by incomplete dependencies:
  ❌ 2.1: In Progress
  ❌ 2.2: Depends on 2.1

💡 Options:
   • Wait for 2.1 to complete
   • /caw:next --step 2.1 to work on blocker
   • Update task_plan.md to skip
```

### Phase Already in Worktree

```
⚠️ Phase 2 already has an active worktree

Existing worktree:
  Directory: .worktrees/phase-2/
  Branch: caw/phase-2
  Status: In Progress (2/5 steps)

💡 Options:
  [1] Continue in existing worktree
  [2] Delete and recreate (⚠️ loses progress)
  [3] View worktree status
```

---

## Builder Agent Integration

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   /caw:next     │────▶│  Builder Agent  │────▶│.caw/task_plan.md│
│   (Command)     │     │  (Implementer)  │     │  (State Store)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │  1. Parse plan        │  2. TDD implement    │
        │  2. Validate deps     │  3. Run tests        │
        │  3. Invoke Builder    │  4. Update status    │
        │  4. Report results    │                       │
        ▼                       ▼                       ▼
```

---

## Status Icons Reference

| Icon | Status | Action |
|------|--------|--------|
| ⏳ | Pending | Ready to execute |
| 🔄 | In Progress | Currently being worked on |
| ✅ | Complete | Skip, already done |
| ❌ | Blocked | Cannot proceed, show warning |
| ⏭️ | Skipped | Skip, intentionally bypassed |
| 🌳 | In Worktree | Being worked in separate worktree |

---

## Integration

- **Reads**: `.caw/task_plan.md`
- **Invokes**: Builder agent via Task tool
- **Updates**: `.caw/task_plan.md` (via Builder)
- **Creates**: `.worktrees/phase-N/` (with --worktree)
- **Suggests**: `/caw:status`, `/caw:merge`, `/caw:next`
