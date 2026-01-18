---
description: Manage git worktrees for parallel step execution in isolated environments
argument-hint: "<subcommand> [options]"
---

# /cw:worktree - Git Worktree Management

Manage git worktrees for parallel execution of CAW phases/steps in fully isolated environments.

## Usage

```bash
# Phase-based (PRIMARY)
/cw:worktree create phase 2          # Create worktree for Phase 2
/cw:worktree create phase 2,3,4      # Create worktrees for multiple phases

# Step-based (Legacy)
/cw:worktree create --steps 2.2,2.3  # Create for specific steps

# Management
/cw:worktree list                    # Show all worktree status
/cw:worktree clean                   # Remove completed/merged worktrees
/cw:worktree clean --all             # Remove all CAW worktrees
```

## Subcommands

### create phase N

Creates isolated git worktree for an entire phase.

**Usage**:
```bash
/cw:worktree create phase 2          # Single phase
/cw:worktree create phase 2,3,4      # Multiple phases at once
```

**Workflow**:
1. **Validate Phase**: Check Phase Deps are satisfied
2. **Create Worktree**: Create `.worktrees/phase-N/`
3. **Create Branch**: Create `caw/phase-N` branch from current HEAD
4. **Copy CAW State**: Copy `.caw/` directory to worktree
5. **Output Guide**: Print terminal commands

**Output (Single Phase)**:
```
🌳 Creating Worktree for Phase 2

Checking dependencies...
  Phase Deps: phase 1 ✅

Creating worktree:
  ✓ Directory: .worktrees/phase-2/
  ✓ Branch: caw/phase-2
  ✓ Copied: .caw/task_plan.md

📋 Execute in new terminal:

  cd .worktrees/phase-2 && claude
  /cw:next phase 2              # Sequential
  # or
  /cw:next --parallel phase 2   # Parallel

After complete, return to main and run:
  /cw:merge
```

**Output (Multiple Phases)**:
```
🌳 Creating Worktrees for Phases 2, 3, 4

Checking dependencies...
  Phase 2 Deps: phase 1 ✅
  Phase 3 Deps: phase 1 ✅
  Phase 4 Deps: phase 1 ✅

Creating worktrees:
  ✓ .worktrees/phase-2/ (branch: caw/phase-2)
  ✓ .worktrees/phase-3/ (branch: caw/phase-3)
  ✓ .worktrees/phase-4/ (branch: caw/phase-4)

📋 Terminal Commands:

# Terminal 1 (Phase 2)
cd .worktrees/phase-2 && claude
/cw:next --parallel phase 2

# Terminal 2 (Phase 3)
cd .worktrees/phase-3 && claude
/cw:next --parallel phase 3

# Terminal 3 (Phase 4)
cd .worktrees/phase-4 && claude
/cw:next phase 4

💡 After all complete, run in main directory:
   /cw:merge --all
```

**Git Commands Executed**:
```bash
# Create worktrees directory
mkdir -p .worktrees

# Create worktree with new branch
git worktree add .worktrees/phase-2 -b caw/phase-2

# Copy CAW state
cp -r .caw .worktrees/phase-2/
```

### create --steps (Legacy)

Creates worktrees for specific steps. Maintained for backward compatibility.

```bash
/cw:worktree create --steps 2.2,2.3
```

**Directory Structure**:
```
.worktrees/
├── caw-step-2.2/    # Step-based (legacy)
└── caw-step-2.3/    # Step-based (legacy)
```

### list

Shows status of all CAW worktrees (both phase and step-based).

**Output**:
```
🌳 CAW Worktrees

## Phase Worktrees
| Path | Branch | Phase | Status | Progress |
|------|--------|-------|--------|----------|
| .worktrees/phase-2 | caw/phase-2 | 2 | 🔄 In Progress | 3/5 |
| .worktrees/phase-3 | caw/phase-3 | 3 | ✅ Complete | 4/4 |
| .worktrees/phase-4 | caw/phase-4 | 4 | ⏳ Pending | 0/3 |

## Step Worktrees (Legacy)
| Path | Branch | Step | Status |
|------|--------|------|--------|
| (none) |

💡 Commands:
  /cw:merge --all          # Merge all completed
  /cw:merge phase 3        # Merge specific phase
  /cw:worktree clean       # Clean completed
```

**Status Detection**:
- Reads `.caw/task_plan.md` in each worktree
- Counts completed/total steps for progress
- Reports aggregate status

### clean

Removes worktrees that have been merged or are no longer needed.

**Default Behavior** (`/cw:worktree clean`):
- Only removes worktrees where all steps are ✅ Complete
- Removes corresponding branch if merged
- Preserves in-progress worktrees

**Force All** (`/cw:worktree clean --all`):
- Removes all `.worktrees/phase-*` and `.worktrees/caw-step-*` directories
- Removes all corresponding branches
- Confirmation required

**Output**:
```
🧹 Cleaning Worktrees

Checking worktree status...
  .worktrees/phase-2: 🔄 In Progress (skipping)
  .worktrees/phase-3: ✅ Complete, merged

Removing completed worktrees:
  ✓ Removed .worktrees/phase-3
  ✓ Deleted branch caw/phase-3

Summary:
  Removed: 1 worktree
  Preserved: 1 worktree (in progress)

💡 Use --all to force remove all worktrees
```

## Directory Structure

```
project/
├── .caw/
│   ├── task_plan.md           # Master plan
│   ├── context_manifest.json
│   └── session.json
├── .worktrees/
│   ├── phase-2/               # Phase 2 worktree (NEW)
│   │   ├── .caw/
│   │   │   └── task_plan.md   # Copied plan
│   │   ├── src/
│   │   └── ...
│   ├── phase-3/               # Phase 3 worktree (NEW)
│   │   └── ...
│   └── caw-step-2.2/          # Legacy step worktree
│       └── ...
└── src/
    └── ...
```

## Worktree Lifecycle

```
1. CREATE
   /cw:worktree create phase 2
   → Creates .worktrees/phase-2/
   → Creates branch caw/phase-2
   → Copies .caw/ state

2. WORK (in separate terminal)
   cd .worktrees/phase-2 && claude
   /cw:next --parallel phase 2
   → Builder executes steps
   → Updates local task_plan.md

3. COMPLETE
   All steps in phase marked ✅
   User returns to main directory

4. MERGE
   /cw:merge [--all | phase N]
   → Merges caw/phase-N into main
   → Syncs main task_plan.md

5. CLEAN
   /cw:worktree clean
   → Removes worktree directory
   → Deletes merged branch
```

## Multi-Phase Parallel Workflow

```bash
# Step 1: Complete Phase 1 in main
/cw:next phase 1

# Step 2: Create worktrees for independent phases
/cw:worktree create phase 2,3,4

# Step 3: Work in parallel terminals
# Terminal 1:
cd .worktrees/phase-2 && claude
/cw:next --parallel phase 2

# Terminal 2:
cd .worktrees/phase-3 && claude
/cw:next --parallel phase 3

# Terminal 3:
cd .worktrees/phase-4 && claude
/cw:next phase 4

# Step 4: Merge all back
cd /path/to/main/project
/cw:merge --all

# Step 5: Continue with dependent phases
/cw:next phase 5
```

## Edge Cases

### Phase Dependencies Not Met

```
⚠️ Cannot create worktree for Phase 3

Dependencies not satisfied:
  Phase Deps: phase 2
  Phase 2 Status: 🔄 In Progress (2/5 steps)

💡 Options:
  • Wait for Phase 2 to complete
  • Create worktree for Phase 2 instead
  • Force create with --force (not recommended)
```

### Worktree Already Exists

```
⚠️ Worktree already exists for Phase 2

Path: .worktrees/phase-2
Branch: caw/phase-2
Status: 🔄 In Progress (3/5 steps)

💡 Options:
  [1] Continue in existing worktree
  [2] Delete and recreate (⚠️ loses progress)
  [3] View worktree status
```

### Uncommitted Changes

```
⚠️ Cannot create worktree with uncommitted changes

Please commit or stash your changes first:
  git stash
  /cw:worktree create phase 2
  git stash pop
```

### Conflicting Phase Dependencies

```
⚠️ Phases 3 and 4 have conflicting dependencies

Phase 3 Deps: phase 2 (not complete)
Phase 4 Deps: phase 2, phase 3 (phase 3 not complete)

Cannot create worktrees for both simultaneously.

💡 Create worktree for Phase 3 first:
  /cw:worktree create phase 3
```

## Integration

- **`/cw:next --worktree phase N`**: Shortcut that calls `worktree create phase N`
- **`/cw:merge`**: Merges completed worktrees back
- **`/cw:status --worktrees`**: Shows worktree status
- **`dependency-analyzer`**: Validates phase dependencies

## .gitignore Recommendation

Add to `.gitignore`:
```
# CAW worktrees (local only)
.worktrees/
```
