---
description: Execute the next pending step from task_plan.md using the Builder agent
argument-hint: "[phase N] [--step N.M] [--parallel]"
---

# /cw:next - Execute Next Step

Automatically proceed with the next pending step from the task plan, invoking the Builder agent for TDD-based implementation.

## Usage

```bash
# Basic - Auto Parallel (DEFAULT)
/cw:next                      # ≥2 parallelizable steps → auto background parallel execution
/cw:next --sequential         # Force sequential execution
/cw:next --step 2.3           # Execute specific step

# Phase-based execution
/cw:next phase 1              # Execute Phase 1 (auto parallel applied)
/cw:next --parallel phase 1   # Force parallel Phase 1
/cw:next --worktree phase 2   # Create worktree for Phase 2

# Batch control
/cw:next --batch 3            # Execute up to 3 steps in parallel
/cw:next --all                # Execute all steps in current phase (sequential)
```

## Flags

| Flag | Description |
|------|-------------|
| (none) | **Auto parallel**: ≥2 executable steps → background agent parallel execution |
| `--sequential` | Force sequential execution |
| `--parallel` | Force parallel execution |
| `--all` | Execute entire current phase sequentially |
| `--worktree` | Create worktree per phase |
| `--step N.M` | Execute specific step |
| `--batch N` | Max N parallel executions (default: 5) |
| `phase N` | Specify phase number |

## Execution Flow

### Step 1: Validate Task Plan
Check for `.caw/task_plan.md`. Error if not found.

### Step 2: Parse Current State
Identify current Phase, Phase Deps, and next actionable step.

### Step 3: Validate Dependencies
Check Phase Deps are satisfied before proceeding.

### Step 4: Execute Based on Mode

**Auto-Parallel (Default):**
1. Analyze runnable steps with `dependency-analyzer`
2. If 0 steps: "No runnable steps"
3. If 1 step: Execute blocking
4. If ≥2 steps: Launch background agents

**Phase Execution:**
```bash
/cw:next phase 2  # Sequential phase execution
```
1. Validate Phase 2 dependencies
2. Execute all pending steps sequentially
3. Stop on failure

**Parallel Phase:**
```bash
/cw:next --parallel phase 1
```
- Groups steps into waves based on dependencies
- Launches background Builder agents per wave

**Worktree:**
```bash
/cw:next --worktree phase 2
```
- Creates `.worktrees/phase-2/` with `caw/phase-2` branch
- Outputs terminal commands for execution

## Status Icons

| Icon | Status | Action |
|------|--------|--------|
| ⏳ | Pending | Ready to execute |
| 🔄 | In Progress | Currently working |
| ✅ | Complete | Done |
| ❌ | Blocked | Cannot proceed |
| ⏭️ | Skipped | Bypassed |
| 🌳 | In Worktree | In separate worktree |

## Edge Cases

- **All Complete**: Shows completion message with suggested actions
- **Blocked Steps**: Lists incomplete dependencies with options
- **Worktree Exists**: Offers continue, recreate, or view status

## Integration

- **Reads**: `.caw/task_plan.md`
- **Invokes**: Builder agent via Task tool
- **Updates**: `.caw/task_plan.md` (via Builder)
- **Creates**: `.worktrees/phase-N/` (with --worktree)
