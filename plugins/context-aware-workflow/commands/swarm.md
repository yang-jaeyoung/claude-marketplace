---
description: Execute multiple agents in parallel swarm mode for concurrent task completion
argument-hint: "<tasks...> [--workers N] [--timeout S] [--merge]"
---

# /cw:swarm - Parallel Agent Swarm

Execute multiple independent tasks concurrently using agent swarm.

## Usage

```bash
/cw:swarm "task1" "task2" "task3"              # Run 3 tasks in parallel
/cw:swarm --workers 4 "taskA" "taskB"          # Limit to 4 concurrent workers
/cw:swarm --timeout 120 "long-task1" "task2"   # Set timeout per task
/cw:swarm --merge "feature-A" "feature-B"      # Auto-merge results
/cw:swarm --from-plan                          # Swarm independent plan steps
```

## Behavior

### Step 1: Task Analysis

Analyze tasks for independence and optimal parallelization:

```python
def analyze_swarm_tasks(tasks: list) -> SwarmConfig:
    dependencies = detect_dependencies(tasks)

    independent = [t for t in tasks if not dependencies[t]]
    dependent = [t for t in tasks if dependencies[t]]

    return SwarmConfig(
        parallel=independent,
        sequential=dependent,
        estimated_workers=len(independent)
    )
```

### Step 2: Worker Allocation

Assign agents to tasks based on category and complexity:

```
Task Analysis
─────────────────────────────────────────────
Task 1: "Implement login API"
  → Category: implementation
  → Complexity: 0.6 (medium)
  → Agent: builder-sonnet

Task 2: "Add logout button"
  → Category: implementation
  → Complexity: 0.3 (low)
  → Agent: builder-haiku

Task 3: "Review auth module"
  → Category: review
  → Complexity: 0.5 (medium)
  → Agent: Reviewer
```

### Step 3: Parallel Execution

```
Swarm Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Workers: 3/3 active | Timeout: 120s

[1] login API      ████████░░░░ 65%  builder-sonnet
[2] logout button  ██████████░░ 85%  builder-haiku
[3] auth review    ████░░░░░░░░ 35%  Reviewer

Elapsed: 45s | Est. remaining: 30s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 4: Result Aggregation

Collect and merge results from all workers:

```
Swarm Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 3 tasks | Success: 3 | Failed: 0

[1] login API      ✅ Complete (52s)
    → Files: src/api/auth.ts, src/routes/login.ts

[2] logout button  ✅ Complete (38s)
    → Files: src/components/LogoutButton.tsx

[3] auth review    ✅ Complete (67s)
    → Issues: 2 minor, 0 critical

Tokens: 45,200 | Cost: $0.42 | Duration: 1m 7s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Flags

### --workers N

Limit concurrent workers (default: number of tasks):

```bash
/cw:swarm --workers 2 "task1" "task2" "task3" "task4"
# Runs 2 at a time, queues remaining
```

### --timeout S

Set per-task timeout in seconds (default: 300):

```bash
/cw:swarm --timeout 60 "quick-task1" "quick-task2"
```

### --merge

Automatically merge results if tasks modify files:

```bash
/cw:swarm --merge "feature-a" "feature-b"
# Creates merge commit after all complete
```

### --from-plan

Extract parallelizable steps from current task plan:

```bash
/cw:swarm --from-plan
# Reads .caw/task_plan.md
# Identifies independent steps
# Executes in parallel
```

### --dry-run

Preview swarm execution without running:

```bash
/cw:swarm --dry-run "task1" "task2"
```

Output:
```
Swarm Preview (dry-run)
─────────────────────────────────────────────
Tasks: 2
Workers: 2 (parallel)
Dependencies: none detected

[1] task1 → builder-sonnet (0.55 complexity)
[2] task2 → builder-haiku (0.25 complexity)

Estimated tokens: ~40,000
Estimated cost: ~$0.35
Estimated time: ~2 minutes
```

## Swarm Modes

### Independent Mode (default)

Each task runs in isolation with its own context:

```
┌────────────┐  ┌────────────┐  ┌────────────┐
│  Worker 1  │  │  Worker 2  │  │  Worker 3  │
│  Task A    │  │  Task B    │  │  Task C    │
│  Context A │  │  Context B │  │  Context C │
└────────────┘  └────────────┘  └────────────┘
       │              │              │
       └──────────────┴──────────────┘
                      │
              Result Aggregation
```

### Worktree Mode

Each task gets its own git worktree for file isolation:

```bash
/cw:swarm --worktrees "feature-x" "feature-y"
```

Creates:
```
.worktrees/
├── swarm-1-feature-x/   # Worktree for task 1
├── swarm-2-feature-y/   # Worktree for task 2
└── swarm-manifest.json  # Swarm state
```

### Shared Context Mode

Tasks share read-only context but write independently:

```bash
/cw:swarm --shared-context "task1" "task2"
```

## Error Handling

### Single Task Failure

```
Swarm Status
─────────────────────────────────────────────
[1] login API      ✅ Complete
[2] logout button  ❌ Failed: Build error
[3] auth review    ✅ Complete

Action: Task 2 failed. Continue with remaining? [Y/n]
```

### Partial Success

```bash
/cw:swarm --on-error continue "task1" "task2" "task3"
# Continues despite failures

/cw:swarm --on-error stop "task1" "task2" "task3"
# Stops all workers on first failure
```

### Timeout Handling

```
Worker 2 exceeded timeout (120s)
Action: Kill and mark failed

Swarm continuing with remaining workers...
```

## Conflict Resolution

When multiple tasks modify the same files:

```
Conflict Detected
─────────────────────────────────────────────
File: src/components/Button.tsx

Modified by:
  [1] task1: Added onClick handler
  [2] task3: Changed styling

Resolution options:
  1. Manual merge (recommended)
  2. Keep task1 changes
  3. Keep task3 changes
  4. Abort swarm
```

## State Management

Swarm state is saved in `.caw/swarm_state.json`:

```json
{
  "swarm_id": "swarm-abc123",
  "started_at": "2024-01-15T10:00:00Z",
  "workers": [
    {
      "id": 1,
      "task": "login API",
      "agent": "builder-sonnet",
      "status": "completed",
      "result_file": ".caw/swarm-results/1.json"
    }
  ],
  "config": {
    "max_workers": 3,
    "timeout": 300,
    "on_error": "continue"
  }
}
```

## Integration

### With Task Tool

Swarm uses Claude's Task tool for parallel execution:

```markdown
## Parallel Execution
Launch multiple Task agents simultaneously:
- Task(subagent_type="builder-sonnet", prompt="task1")
- Task(subagent_type="builder-haiku", prompt="task2")
- Task(subagent_type="Reviewer", prompt="task3")
```

### With Background Heuristics

Swarm respects background heuristics for nested operations:
- Lint/format tasks → background within worker
- Security checks → foreground (blocking)

### With Analytics

Swarm metrics tracked:
```json
{
  "swarm_metrics": {
    "total_tasks": 3,
    "parallel_workers": 3,
    "total_duration_s": 67,
    "sequential_estimate_s": 180,
    "speedup_factor": 2.7
  }
}
```

## Best Practices

1. **Identify independence**: Only swarm truly independent tasks
2. **Set appropriate timeouts**: Based on task complexity
3. **Use worktrees for file conflicts**: Isolate file modifications
4. **Monitor resource usage**: Parallel execution increases load
5. **Review merge results**: Auto-merge may need manual adjustment
6. **Limit workers on shared resources**: Prevent contention

## Related Commands

- [/cw:loop](./loop.md) - Sequential execution loop
- [/cw:auto](./auto.md) - Full workflow automation
- [/cw:pipeline](./pipeline.md) - Explicit sequential pipeline

## Related Documentation

- [Parallel Execution](../_shared/parallel-execution.md) - Parallel patterns
- [Agent Resolver](../_shared/agent-resolver.md) - Agent selection
- [Background Heuristics](../_shared/background-heuristics.md) - Async execution
