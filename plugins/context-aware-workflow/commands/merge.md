---
description: Merge completed worktree branches back to main and synchronize task plan state
argument-hint: "[options]"
---

# /caw:merge - Merge Worktree Branches

Merges completed worktree branches back to the main branch and synchronizes task plan state.

## Usage

```bash
/caw:merge                 # Merge all completed worktree branches
/caw:merge --step 2.2      # Merge specific step's worktree
/caw:merge --dry-run       # Show what would be merged without executing
/caw:merge --abort         # Abort current merge in progress
/caw:merge --continue      # Continue merge after conflict resolution
```

## Behavior

### Default Merge (`/caw:merge`)

Merges all worktrees where the step is marked ✅ Complete.

**Workflow**:
1. **Scan Worktrees**: Find all `.worktrees/caw-step-*` directories
2. **Check Completion**: Read each worktree's `.caw/task_plan.md`
3. **Order by Dependencies**: Merge in dependency order (2.2 before 2.4 if 2.4 depends on 2.2)
4. **Sequential Merge**: Merge each branch one at a time
5. **Sync Task Plan**: Update main `.caw/task_plan.md` with merged status
6. **Clean Up**: Optionally remove merged worktrees

**Output**:
```
🔀 Merging Worktree Branches

Scanning worktrees...
  .worktrees/caw-step-2.2: ✅ Complete (ready to merge)
  .worktrees/caw-step-2.3: ✅ Complete (ready to merge)
  .worktrees/caw-step-3.3: 🔄 In Progress (skipping)

Merge order (by dependencies):
  1. caw/step-2.2 (no deps)
  2. caw/step-2.3 (no deps)

Merging caw/step-2.2 into main...
  ✓ Fast-forward merge successful
  Files changed: 2

Merging caw/step-2.3 into main...
  ✓ 3-way merge successful
  Files changed: 3

Updating task_plan.md...
  ✓ Step 2.2: ✅ Complete
  ✓ Step 2.3: ✅ Complete

📊 Summary:
  Merged: 2 branches
  Skipped: 1 (in progress)
  Conflicts: 0

💡 Run /caw:worktree clean to remove merged worktrees
```

### Specific Step Merge (`/caw:merge --step 2.2`)

Merges only the specified step's worktree.

```
🔀 Merging Step 2.2

Checking worktree status...
  .worktrees/caw-step-2.2: ✅ Complete

Merging caw/step-2.2 into main...
  ✓ Merge successful

Files changed:
  M src/auth/jwt.ts
  A tests/auth/jwt.test.ts

✅ Step 2.2 merged successfully
```

### Dry Run (`/caw:merge --dry-run`)

Shows what would be merged without actually merging.

```
🔍 Dry Run - Merge Preview

Would merge:
  1. caw/step-2.2 → main
     Files: src/auth/jwt.ts, tests/auth/jwt.test.ts
     Conflicts: None detected

  2. caw/step-2.3 → main
     Files: src/auth/validation.ts
     Conflicts: Possible (src/auth/index.ts modified in both)

Would skip:
  - caw/step-3.3 (not complete)

💡 Run /caw:merge to execute
```

## Conflict Handling

### Automatic Resolution

Simple conflicts are auto-resolved when possible:
- Different sections of same file modified
- Only one side modified a file

### Manual Resolution Required

When conflicts cannot be auto-resolved:

```
⚠️ Merge Conflict in caw/step-2.3

Conflicting files:
  src/auth/index.ts

To resolve:
  1. Edit src/auth/index.ts to resolve conflicts
  2. Run: git add src/auth/index.ts
  3. Run: /caw:merge --continue

Or abort with: /caw:merge --abort
```

### Continue After Resolution (`/caw:merge --continue`)

```
🔀 Continuing Merge

Checking resolved files...
  ✓ src/auth/index.ts resolved

Completing merge of caw/step-2.3...
  ✓ Merge committed

Continuing with remaining branches...
```

### Abort Merge (`/caw:merge --abort`)

```
⏹️ Aborting Merge

Reverting merge state...
  ✓ Merge aborted
  ✓ Working directory restored

💡 Fix issues and try /caw:merge again
```

## Merge Order Strategy

Worktrees are merged in dependency order to prevent conflicts:

```
Dependencies:
  2.2 → 2.4 (2.4 depends on 2.2)
  2.3 → 2.4
  2.4 → 3.1

Merge Order:
  1. 2.2, 2.3 (no dependencies between them)
  2. 2.4 (after 2.2 and 2.3)
  3. 3.1 (after 2.4)
```

If circular dependencies exist (shouldn't happen with valid plan):
```
⚠️ Circular dependency detected in merge order
  2.2 → 2.3 → 2.2

Falling back to creation-time order.
Please review task_plan.md dependencies.
```

## Task Plan Synchronization

After merge, the main `.caw/task_plan.md` is updated:

1. **Read Worktree State**: Get step status from worktree's task_plan.md
2. **Update Main Plan**: Set corresponding step to ✅ Complete
3. **Preserve Notes**: Copy any notes added during implementation
4. **Update Timestamps**: Record merge time

```markdown
## Execution Phases

### Phase 2: Core Implementation
| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 2.2 | Token generation | ✅ Complete | Builder | 2.1 | Merged from caw/step-2.2 |
| 2.3 | Token validation | ✅ Complete | Builder | 2.1 | Merged from caw/step-2.3 |
```

## Git Commands Executed

```bash
# Merge a branch
git merge caw/step-2.2 --no-edit

# If conflict occurs
git merge --abort  # For /caw:merge --abort

# After conflict resolution
git add <resolved-files>
git merge --continue

# Clean up after merge
git worktree remove .worktrees/caw-step-2.2
git branch -d caw/step-2.2
```

## Edge Cases

### No Completed Worktrees

```
ℹ️ No worktrees ready to merge

Worktree status:
  .worktrees/caw-step-2.2: 🔄 In Progress
  .worktrees/caw-step-2.3: ⏳ Pending

💡 Complete work in worktrees first, then run /caw:merge
```

### No Worktrees Exist

```
ℹ️ No worktrees found

No .worktrees/caw-step-* directories exist.

💡 Create worktrees with: /caw:worktree create
```

### Worktree Modified but Not Committed

```
⚠️ Uncommitted changes in worktree

.worktrees/caw-step-2.2 has uncommitted changes:
  M src/auth/jwt.ts

Please commit changes in the worktree first:
  cd .worktrees/caw-step-2.2
  git add -A && git commit -m "Complete step 2.2"
```

## Integration

- **`/caw:worktree create`**: Creates worktrees that will be merged
- **`/caw:worktree clean`**: Removes worktrees after merge
- **`/caw:status`**: Shows pending merge status
- **`progress-tracker`**: Records merge events in metrics

## Merge Strategy Options

Future enhancement - allow customization:
```bash
/caw:merge --strategy rebase    # Rebase instead of merge
/caw:merge --squash             # Squash commits on merge
```

Currently uses standard `git merge` with commit.
