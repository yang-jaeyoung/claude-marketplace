---
description: Execute multiple agents in parallel swarm mode for concurrent task completion
argument-hint: "<tasks...> [--workers N] [--timeout S] [--merge]"
---

# /cw:swarm - Parallel Agent Swarm

Execute multiple independent tasks concurrently using agent swarm.

## Usage

```bash
/cw:swarm "task1" "task2" "task3"         # 3 tasks in parallel
/cw:swarm --workers 4 "taskA" "taskB"     # Limit workers
/cw:swarm --timeout 120 "task1" "task2"   # Per-task timeout
/cw:swarm --merge "feature-A" "feature-B" # Auto-merge results
/cw:swarm --from-plan                     # Swarm plan steps
/cw:swarm --dry-run "task1" "task2"       # Preview only
```

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--workers N` | task count | Max concurrent workers |
| `--timeout S` | 300 | Per-task timeout (seconds) |
| `--merge` | false | Auto-merge file results |
| `--from-plan` | false | Extract from task_plan.md |
| `--worktrees` | false | Each task gets git worktree |
| `--on-error` | continue | continue or stop |

## Workflow

1. **Analyze**: Check task independence, detect dependencies
2. **Allocate**: Assign agents by category/complexity
3. **Execute**: Parallel Task agents with progress tracking
4. **Aggregate**: Collect results, resolve conflicts

## Output

```
Swarm Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Workers: 3/3 active | Timeout: 120s

[1] login API      ████████░░░░ 65%  builder-sonnet
[2] logout button  ██████████░░ 85%  builder-haiku
[3] auth review    ████░░░░░░░░ 35%  Reviewer

Elapsed: 45s | Est. remaining: 30s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Swarm Complete
  Total: 3 | Success: 3 | Failed: 0
  Tokens: 45,200 | Cost: $0.42 | Duration: 1m 7s
```

## Swarm Modes

| Mode | Description |
|------|-------------|
| **Independent** | Each task isolated context |
| **Worktree** | Each task gets git worktree |
| **Shared Context** | Read-only shared, write separate |

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Single task failure | Continue (or stop with --on-error stop) |
| Timeout | Kill task, mark failed |
| Conflict | Show options: manual merge, keep one, abort |

## Conflict Resolution

When multiple tasks modify same file:
```
Conflict: src/Button.tsx
  [1] task1: Added onClick
  [2] task3: Changed styling

Options: 1. Manual | 2. Keep task1 | 3. Keep task3 | 4. Abort
```

## State

Saved in `.caw/swarm_state.json`:
- Worker assignments and status
- Per-task results
- Config (workers, timeout, error handling)

## Metrics

```json
{
  "total_tasks": 3,
  "parallel_workers": 3,
  "total_duration_s": 67,
  "sequential_estimate_s": 180,
  "speedup_factor": 2.7
}
```

## Best Practices

1. Only swarm truly independent tasks
2. Set appropriate timeouts
3. Use worktrees for file conflicts
4. Monitor resource usage
5. Review merge results

## Related

- [/cw:loop](./loop.md) - Sequential execution
- [/cw:auto](./auto.md) - Full automation
- [/cw:pipeline](./pipeline.md) - Stage pipeline
