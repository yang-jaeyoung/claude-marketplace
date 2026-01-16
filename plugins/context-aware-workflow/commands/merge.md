---
description: Merge completed worktree branches back to main and synchronize task plan state
argument-hint: "[options]"
---

# /caw:merge - Merge Worktree Branches

Merges completed worktree branches back to the main branch and synchronizes task plan state.

## Usage

```bash
# Phase-based (PRIMARY)
/caw:merge                     # Auto-detect and merge completed worktrees
/caw:merge --all               # Merge all phase worktrees (dependency order)
/caw:merge phase 2             # Merge specific phase's worktree
/caw:merge phase 2,3           # Merge multiple phases

# Step-based (Legacy)
/caw:merge --step 2.2          # Merge specific step's worktree

# Control
/caw:merge --dry-run           # Preview without executing
/caw:merge --abort             # Abort current merge
/caw:merge --continue          # Continue after conflict resolution
```

## Behavior

### Default Merge (`/caw:merge`)

Auto-detects and merges all completed worktrees (both phase and step-based).

**Workflow**:
1. **Scan Worktrees**: Find `.worktrees/phase-*` and `.worktrees/caw-step-*`
2. **Check Completion**: Read each worktree's `.caw/task_plan.md`
3. **Order by Dependencies**: Merge in Phase Deps order
4. **Sequential Merge**: Merge each branch one at a time
5. **Sync Task Plan**: Update main `.caw/task_plan.md`
6. **Suggest Cleanup**: Recommend `/caw:worktree clean`

**Output**:
```
🔀 Merging Worktree Branches

Scanning worktrees...
  .worktrees/phase-2: ✅ Complete (5/5 steps)
  .worktrees/phase-3: ✅ Complete (4/4 steps)
  .worktrees/phase-4: 🔄 In Progress (2/3 steps, skipping)

Merge order (by Phase Deps):
  1. caw/phase-2 (Phase Deps: phase 1)
  2. caw/phase-3 (Phase Deps: phase 1)

Merging caw/phase-2 into main...
  ✓ Fast-forward merge successful
  Files changed: 5

Merging caw/phase-3 into main...
  ✓ 3-way merge successful
  Files changed: 4

Updating task_plan.md...
  ✓ Phase 2: ✅ Complete (5/5)
  ✓ Phase 3: ✅ Complete (4/4)

📊 Summary:
  Merged: 2 phase branches
  Skipped: 1 (in progress)
  Conflicts: 0

💡 Run /caw:worktree clean to remove merged worktrees
```

### Merge All (`/caw:merge --all`)

Merges all phase worktrees in dependency order, regardless of completion status warning.

**Use Case**: When you want to merge all completed phases at once.

**Output**:
```
🔀 Merging All Phase Worktrees

Detected worktrees:
  ├─ phase-2: ✅ Complete (5/5 steps)
  ├─ phase-3: ✅ Complete (4/4 steps)
  └─ phase-4: ✅ Complete (3/3 steps)

Merge order (by Phase Deps):
  1. phase-2 (no deps among worktrees)
  2. phase-3 (no deps among worktrees)
  3. phase-4 (depends on phase-2, phase-3)

Merging...
  ✅ caw/phase-2 merged successfully
     Files: src/auth/jwt.ts, src/auth/validation.ts (+3 more)

  ✅ caw/phase-3 merged successfully
     Files: src/models/user.ts, src/utils/hash.ts (+2 more)

  ✅ caw/phase-4 merged successfully
     Files: src/routes/auth.ts, tests/integration/auth.test.ts

📊 Main task_plan.md updated:
  Phase 2: ✅ Complete
  Phase 3: ✅ Complete
  Phase 4: ✅ Complete

💡 Next: /caw:next phase 5 (if exists)
   Or: /caw:worktree clean to remove worktrees
```

### Specific Phase Merge (`/caw:merge phase 2`)

Merges only the specified phase's worktree.

```
🔀 Merging Phase 2

Checking worktree status...
  .worktrees/phase-2: ✅ Complete (5/5 steps)

Merging caw/phase-2 into main...
  ✓ Merge successful

Files changed:
  M src/auth/jwt.ts
  M src/auth/validation.ts
  A src/auth/middleware.ts
  A tests/auth/jwt.test.ts
  A tests/auth/validation.test.ts

Updating task_plan.md...
  ✓ Phase 2: ✅ Complete

✅ Phase 2 merged successfully

💡 Next steps:
  /caw:merge phase 3          # Merge next phase
  /caw:worktree clean         # Clean up
```

### Multiple Phases (`/caw:merge phase 2,3`)

Merges multiple phases in dependency order.

```
🔀 Merging Phases 2, 3

Checking worktree status...
  .worktrees/phase-2: ✅ Complete
  .worktrees/phase-3: ✅ Complete

Merge order:
  1. phase-2 (Phase Deps: phase 1)
  2. phase-3 (Phase Deps: phase 1)

Merging...
  ✅ caw/phase-2 merged
  ✅ caw/phase-3 merged

📊 Summary: 2 phases merged
```

### Dry Run (`/caw:merge --dry-run`)

Shows what would be merged without actually merging.

```
🔍 Dry Run - Merge Preview

Would merge (in order):
  1. caw/phase-2 → main
     Status: ✅ Complete (5/5 steps)
     Files: 5 changed
     Conflicts: None detected

  2. caw/phase-3 → main
     Status: ✅ Complete (4/4 steps)
     Files: 4 changed
     Conflicts: Possible (src/types/index.ts modified in both)

Would skip:
  - caw/phase-4 (In Progress: 2/3 steps)

💡 Run /caw:merge to execute
   Or /caw:merge --all to include all
```

## Conflict Handling

### Automatic Resolution

Simple conflicts are auto-resolved when possible:
- Different sections of same file modified
- Only one side modified a file
- Non-overlapping changes

### Manual Resolution Required

When conflicts cannot be auto-resolved:

```
⚠️ Merge Conflict in caw/phase-3

Conflicting files:
  src/types/index.ts
  src/auth/index.ts

To resolve:
  1. Edit conflicting files to resolve
  2. Run: git add <resolved-files>
  3. Run: /caw:merge --continue

Or abort with: /caw:merge --abort

💡 Tip: Use VS Code or your preferred merge tool
```

### Continue After Resolution (`/caw:merge --continue`)

```
🔀 Continuing Merge

Checking resolved files...
  ✓ src/types/index.ts resolved
  ✓ src/auth/index.ts resolved

Completing merge of caw/phase-3...
  ✓ Merge committed

Continuing with remaining phases...
  ✅ caw/phase-4 merged

📊 All merges complete
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

### Phase-Based Ordering

Phases are merged in Phase Deps order:

```
Phase Deps:
  Phase 2: phase 1
  Phase 3: phase 1
  Phase 4: phase 2, phase 3
  Phase 5: phase 4

Merge Order:
  1. Phase 2, Phase 3 (both depend only on Phase 1)
  2. Phase 4 (after Phase 2, 3)
  3. Phase 5 (after Phase 4)

Note: Phases with same deps can be merged in any order,
      but we merge sequentially to avoid conflicts.
```

### Topological Sort

The merge uses topological sort based on Phase Deps:

```
Input worktrees: [phase-2, phase-3, phase-4]

Build dependency graph:
  phase-2 → []
  phase-3 → []
  phase-4 → [phase-2, phase-3]

Topological order: [phase-2, phase-3, phase-4]
```

## Task Plan Synchronization

After merge, the main `.caw/task_plan.md` is updated:

1. **Read Worktree State**: Get all step statuses from worktree's task_plan.md
2. **Update Main Plan**: Set corresponding steps to their final status
3. **Preserve Notes**: Copy any notes added during implementation
4. **Update Phase Status**: Mark phase as complete if all steps done

```markdown
## Execution Phases

### Phase 2: Core Implementation
**Phase Deps**: phase 1

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 2.1 | JWT utility | ✅ | Builder | - | Merged from caw/phase-2 |
| 2.2 | Token generation | ✅ | Builder | 2.1 | Merged from caw/phase-2 |
| 2.3 | Token validation | ✅ | Builder | 2.1 | Merged from caw/phase-2 |
```

## Git Commands Executed

```bash
# Merge a phase branch
git merge caw/phase-2 --no-edit

# If conflict occurs
git merge --abort  # For /caw:merge --abort

# After conflict resolution
git add <resolved-files>
git merge --continue

# Clean up after merge (done by /caw:worktree clean)
git worktree remove .worktrees/phase-2
git branch -d caw/phase-2
```

## Edge Cases

### No Completed Worktrees

```
ℹ️ No worktrees ready to merge

Worktree status:
  .worktrees/phase-2: 🔄 In Progress (3/5)
  .worktrees/phase-3: ⏳ Pending (0/4)

💡 Complete work in worktrees first, then run /caw:merge
```

### No Worktrees Exist

```
ℹ️ No worktrees found

No .worktrees/phase-* or .worktrees/caw-step-* directories exist.

💡 Create worktrees with:
   /caw:next --worktree phase N
   /caw:worktree create phase N
```

### Worktree Modified but Not Committed

```
⚠️ Uncommitted changes in worktree

.worktrees/phase-2 has uncommitted changes:
  M src/auth/jwt.ts
  M src/auth/validation.ts

Please commit changes in the worktree first:
  cd .worktrees/phase-2
  git add -A && git commit -m "Complete Phase 2"
```

### Phase Not Complete

```
⚠️ Phase 2 is not complete

Status: 🔄 In Progress (3/5 steps)
  ✅ 2.1 JWT utility
  ✅ 2.2 Token generation
  ✅ 2.3 Token validation
  🔄 2.4 Middleware (in progress)
  ⏳ 2.5 Error handling

Options:
  [1] Wait for completion
  [2] Merge partial (⚠️ not recommended)
  [3] View remaining steps
```

## Integration

- **`/caw:worktree create`**: Creates worktrees that will be merged
- **`/caw:worktree clean`**: Removes worktrees after merge
- **`/caw:status --worktrees`**: Shows pending merge status
- **`/caw:next`**: Continues work after merge

## Best Practices

1. **Complete all steps** in a worktree before merging
2. **Commit frequently** in worktrees to preserve progress
3. **Use `--dry-run`** before merging to preview changes
4. **Merge in order** when phases have dependencies
5. **Clean up** after merging with `/caw:worktree clean`
