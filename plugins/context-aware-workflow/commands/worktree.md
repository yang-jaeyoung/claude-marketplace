---
description: Manage git worktrees for parallel step execution in isolated environments
argument-hint: "<subcommand> [options]"
---

# /caw:worktree - Git Worktree Management

Manage git worktrees for parallel execution of CAW steps in fully isolated environments.

## Usage

```bash
/caw:worktree create              # Create worktrees for runnable parallel steps
/caw:worktree create --steps 2.2,2.3  # Create for specific steps
/caw:worktree list                # Show current worktree status
/caw:worktree clean               # Remove completed/merged worktrees
/caw:worktree clean --all         # Remove all CAW worktrees
```

## Subcommands

### create

Creates isolated git worktrees for parallel step execution.

**Workflow**:
1. **Analyze Dependencies**: Use `dependency-analyzer` skill to find parallelizable steps
2. **Create Worktrees**: For each step, create `.worktrees/caw-step-N.M/`
3. **Create Branches**: Create `caw/step-N.M` branch from current HEAD
4. **Copy CAW State**: Copy `.caw/` directory to each worktree
5. **Output Guide**: Print terminal commands

**Output**:
```
🌳 Creating Worktrees for Parallel Execution

Analyzing dependencies...
  Runnable steps: 2.2, 2.3, 3.3
  Parallel groups: [2.2, 2.3], [3.3]

Creating worktrees:
  ✓ .worktrees/caw-step-2.2/
    Branch: caw/step-2.2
    Task: Implement token generation

  ✓ .worktrees/caw-step-2.3/
    Branch: caw/step-2.3
    Task: Implement token validation

📋 Terminal Commands:

# Terminal 1 (Step 2.2)
cd .worktrees/caw-step-2.2 && claude
/caw:next --step 2.2

# Terminal 2 (Step 2.3)
cd .worktrees/caw-step-2.3 && claude
/caw:next --step 2.3

💡 After completion, run in main directory:
   /caw:merge
```

**Git Commands Executed**:
```bash
# Create worktree directory
mkdir -p .worktrees

# Create worktree with new branch
git worktree add .worktrees/caw-step-2.2 -b caw/step-2.2

# Copy CAW state
cp -r .caw .worktrees/caw-step-2.2/
```

### list

Shows status of all CAW worktrees.

**Output**:
```
🌳 CAW Worktrees

| Path | Branch | Step | Status |
|------|--------|------|--------|
| .worktrees/caw-step-2.2 | caw/step-2.2 | 2.2 | ✅ Complete |
| .worktrees/caw-step-2.3 | caw/step-2.3 | 2.3 | 🔄 In Progress |
| .worktrees/caw-step-3.3 | caw/step-3.3 | 3.3 | ⏳ Pending |

💡 Run /caw:merge when steps are complete
```

**Status Detection**:
- Reads `.caw/task_plan.md` in each worktree
- Finds the target step and checks its status
- Reports aggregate progress

### clean

Removes worktrees that have been merged or are no longer needed.

**Default Behavior** (`/caw:worktree clean`):
- Only removes worktrees where step is ✅ Complete
- Removes corresponding branch if merged
- Preserves in-progress worktrees

**Force All** (`/caw:worktree clean --all`):
- Removes all `.worktrees/caw-step-*` directories
- Removes all `caw/step-*` branches
- Confirmation required

**Output**:
```
🧹 Cleaning Worktrees

Checking worktree status...
  .worktrees/caw-step-2.2: ✅ Complete, merged
  .worktrees/caw-step-2.3: 🔄 In Progress (skipping)

Removing completed worktrees:
  ✓ Removed .worktrees/caw-step-2.2
  ✓ Deleted branch caw/step-2.2

Summary:
  Removed: 1 worktree
  Preserved: 1 worktree (in progress)

💡 Use --all to force remove all worktrees
```

## Directory Structure

```
project/
├── .caw/
│   ├── task_plan.md
│   └── session.json
├── .worktrees/
│   ├── caw-step-2.2/          # Isolated worktree
│   │   ├── .caw/              # Copied CAW state
│   │   │   └── task_plan.md
│   │   ├── src/               # Full project copy
│   │   └── ...
│   └── caw-step-2.3/
│       └── ...
└── src/
    └── ...
```

## Worktree Lifecycle

```
1. CREATE
   /caw:worktree create
   → Creates .worktrees/caw-step-N.M/
   → Creates branch caw/step-N.M

2. WORK
   User opens terminal, navigates to worktree
   Runs /caw:next --step N.M
   Builder implements the step

3. COMPLETE
   Step marked ✅ in worktree's task_plan.md
   User returns to main directory

4. MERGE
   /caw:merge
   → Merges caw/step-N.M into main
   → Updates main task_plan.md

5. CLEAN
   /caw:worktree clean
   → Removes worktree directory
   → Deletes merged branch
```

## Edge Cases

### No Parallelizable Steps

```
⚠️ No steps available for worktree execution

Current state:
  - Completed: 2.1
  - In Progress: 2.2
  - Blocked: 2.3 (waiting for 2.2)

💡 Wait for 2.2 to complete, or use /caw:next for sequential
```

### Worktree Already Exists

```
⚠️ Worktree already exists for step 2.2

Path: .worktrees/caw-step-2.2
Branch: caw/step-2.2
Status: 🔄 In Progress

Options:
  • Continue in existing worktree
  • /caw:worktree clean --step 2.2 to remove and recreate
```

### Uncommitted Changes

```
⚠️ Cannot create worktree with uncommitted changes

Please commit or stash your changes first:
  git stash
  /caw:worktree create
  git stash pop
```

## Integration

- **`/caw:next --worktree`**: Shortcut that calls `worktree create`
- **`/caw:merge`**: Merges completed worktrees back
- **`/caw:status`**: Shows worktree status if any exist
- **`dependency-analyzer`**: Identifies parallelizable steps

## .gitignore Recommendation

Add to `.gitignore`:
```
# CAW worktrees (local only)
.worktrees/
```
