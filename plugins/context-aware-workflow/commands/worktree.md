---
description: Manage git worktrees for parallel step execution in isolated environments
argument-hint: "<subcommand> [options]"
---

# /cw:worktree - Git Worktree Management

Manage git worktrees for parallel execution of CAW phases/steps in isolated environments.

## Usage

```bash
# Create
/cw:worktree create phase 2          # Single phase
/cw:worktree create phase 2,3,4      # Multiple phases
/cw:worktree create --steps 2.2,2.3  # Legacy step-based

# Manage
/cw:worktree list                    # Show status
/cw:worktree clean                   # Remove completed
/cw:worktree clean --all             # Remove all
```

## Subcommands

### create phase N

Creates isolated git worktree for a phase.

**Workflow**:
1. Validate Phase Deps are satisfied
2. Create `.worktrees/phase-N/`
3. Create `caw/phase-N` branch from HEAD
4. Copy `.caw/` directory to worktree

**Output**:
```
🌳 Creating Worktree for Phase 2

✓ Directory: .worktrees/phase-2/
✓ Branch: caw/phase-2
✓ Copied: .caw/task_plan.md

📋 Execute in new terminal:
  cd .worktrees/phase-2 && claude
  /cw:next phase 2

After complete: /cw:merge
```

**Multiple Phases**:
```bash
/cw:worktree create phase 2,3,4
# Creates 3 worktrees, outputs terminal commands for each
```

### list

Shows status of all CAW worktrees:

```
🌳 CAW Worktrees

| Path | Branch | Status | Progress |
|------|--------|--------|----------|
| .worktrees/phase-2 | caw/phase-2 | 🔄 In Progress | 3/5 |
| .worktrees/phase-3 | caw/phase-3 | ✅ Complete | 4/4 |

💡 /cw:merge phase 3 | /cw:worktree clean
```

### clean

Removes worktrees and branches:
- Default: Only completed/merged worktrees
- `--all`: All CAW worktrees (requires confirmation)

## Directory Structure

```
project/
├── .caw/task_plan.md           # Master plan
├── .worktrees/
│   ├── phase-2/                # Phase 2 worktree
│   │   └── .caw/task_plan.md   # Copied plan
│   └── phase-3/                # Phase 3 worktree
└── src/
```

## Lifecycle

```
CREATE → WORK → COMPLETE → MERGE → CLEAN
```

1. `/cw:worktree create phase N` - Creates worktree
2. Work in separate terminal with `/cw:next phase N`
3. All steps marked ✅
4. `/cw:merge` in main directory
5. `/cw:worktree clean` removes worktree

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Deps not met | Shows missing deps, suggests alternatives |
| Already exists | Shows status, offers recreate option |
| Uncommitted changes | Requires stash first |
| Conflicting deps | Cannot create both, suggests order |

## Integration

- `/cw:next --worktree phase N` - Shortcut for create
- `/cw:merge` - Merges completed worktrees
- `/cw:status --worktrees` - Shows worktree status

## .gitignore

```
.worktrees/
```
