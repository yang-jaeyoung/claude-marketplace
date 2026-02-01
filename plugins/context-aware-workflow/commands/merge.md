---
description: Merge completed worktree branches back to main and synchronize task plan state
argument-hint: "[phase N] [--all] [--dry-run]"
---

# /cw:merge - Merge Worktree Branches

Merges completed worktree branches back to the main branch and synchronizes task plan state.

## Usage

```bash
/cw:merge                     # Auto-detect and merge completed
/cw:merge --all               # Merge all (dependency order)
/cw:merge phase 2             # Merge specific phase
/cw:merge phase 2,3           # Merge multiple phases
/cw:merge --step 2.2          # Merge step worktree (legacy)
/cw:merge --dry-run           # Preview without executing
/cw:merge --abort             # Abort current merge
/cw:merge --continue          # Continue after conflict
```

## Workflow

1. **Scan**: Find `.worktrees/phase-*` directories
2. **Check**: Read each worktree's task_plan.md for completion
3. **Order**: Sort by Phase Deps (topological)
4. **Merge**: Sequential merge of each branch
5. **Sync**: Update main `.caw/task_plan.md`
6. **Cleanup**: Suggest `/cw:worktree clean`

## Output

```
🔀 Merging Worktree Branches

Scanning worktrees...
  .worktrees/phase-2: ✅ Complete (5/5)
  .worktrees/phase-3: ✅ Complete (4/4)
  .worktrees/phase-4: 🔄 In Progress (skipping)

Merging...
  ✅ caw/phase-2 merged (5 files)
  ✅ caw/phase-3 merged (4 files)

📊 Summary: 2 merged, 1 skipped, 0 conflicts
💡 Run /cw:worktree clean to remove merged worktrees
```

## Conflict Handling

| Scenario | Action |
|----------|--------|
| Auto-resolvable | Resolved automatically |
| Manual required | Lists files, waits for resolution |
| After resolution | `git add <files>` then `/cw:merge --continue` |
| Give up | `/cw:merge --abort` |

## Merge Order

Phases merged in topological order based on Phase Deps:
- Phase 2, 3 (depend only on Phase 1)
- Phase 4 (depends on Phase 2, 3)
- Phase 5 (depends on Phase 4)

## Task Plan Sync

After merge, main task_plan.md updated:
- Step statuses from worktree
- Notes preserved
- Phase marked complete if all steps done

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No completed worktrees | Shows status, suggests completing work |
| No worktrees exist | Suggests creating with `/cw:worktree create` |
| Uncommitted changes | Requires commit in worktree first |
| Phase not complete | Warns, offers partial merge option |

## Git Commands

```bash
git merge caw/phase-N --no-edit    # Merge
git merge --abort                   # Abort
git merge --continue                # After resolution
```

## Integration

- `/cw:worktree create` - Creates worktrees to merge
- `/cw:worktree clean` - Removes after merge
- `/cw:status --worktrees` - Shows pending merge status

## Best Practices

1. Complete all steps before merging
2. Commit frequently in worktrees
3. Use `--dry-run` to preview
4. Merge in dependency order
5. Clean up after merging
