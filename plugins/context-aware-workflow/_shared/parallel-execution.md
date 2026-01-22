# Parallel Execution System

Intelligent parallel step execution with dependency-aware wave scheduling.

## Overview

The Parallel Execution System enables concurrent execution of independent steps, dramatically improving workflow efficiency. It analyzes step dependencies to create execution waves and manages background agents safely.

## Core Concepts

### Execution Waves

Steps are grouped into waves based on dependencies:

```
Task Plan:
  1.1 Create user model      (no deps)
  1.2 Create auth service    (no deps)
  1.3 Integrate auth         (depends on 1.1, 1.2)
  1.4 Add tests              (depends on 1.3)
  1.5 Add documentation      (no deps)

Wave Analysis:
  Wave 1: [1.1, 1.2, 1.5]  ← Execute in parallel (no dependencies)
  Wave 2: [1.3]            ← Wait for Wave 1, then execute
  Wave 3: [1.4]            ← Wait for Wave 2, then execute

Timeline:
  ┌──────────────────────────────────────────────────────────┐
  │ Wave 1:  [1.1]────────┐                                   │
  │          [1.2]────────┼── Parallel                        │
  │          [1.5]────────┘                                   │
  │                       │                                   │
  │ Wave 2:               └──►[1.3]──────┐                    │
  │                                      │                    │
  │ Wave 3:                              └──►[1.4]            │
  └──────────────────────────────────────────────────────────┘
```

### Dependency Detection

Dependencies are identified from:

1. **Explicit markers** in task_plan.md:
   ```markdown
   | 1.3 | Integrate auth | ⏳ Pending | Deps: 1.1, 1.2 |
   ```

2. **Phase boundaries** (steps in phase N depend on phase N-1):
   ```markdown
   ## Phase 1: Foundation
   1.1 Create models     ← No cross-phase deps
   
   ## Phase 2: Integration  (Phase Deps: Phase 1)
   2.1 Connect services  ← Implicitly depends on all Phase 1 steps
   ```

3. **Inferred from description**:
   - "Add tests for X" depends on X
   - "Integrate A with B" depends on A and B

## Wave Calculation Algorithm

```markdown
## Wave Calculation

INPUT: steps[], dependencies[]
OUTPUT: waves[]

FUNCTION calculate_waves(steps, dependencies):
  completed = []
  remaining = steps.copy()
  waves = []
  
  WHILE remaining.length > 0:
    # Find steps with all deps satisfied
    wave = []
    FOR step IN remaining:
      step_deps = dependencies[step.id]
      IF all_in(step_deps, completed):
        wave.append(step)
    
    IF wave.length == 0:
      ERROR "Circular dependency detected"
    
    # Move wave steps from remaining to completed
    FOR step IN wave:
      remaining.remove(step)
      completed.append(step.id)
    
    waves.append(wave)
  
  RETURN waves
```

## Execution Modes

### Auto-Parallel (Default)

When `--parallel` is not specified, automatically determines if parallel execution is beneficial:

```markdown
## Auto-Parallel Decision

IF runnable_steps.count >= 2:
  # Multiple independent steps available
  USE parallel_execution
ELSE:
  # Single step or dependencies blocking
  USE sequential_execution
```

### Forced Sequential

```bash
/cw:next --sequential
```

Disables parallel execution even when possible.

### Forced Parallel

```bash
/cw:next --parallel phase 1
```

Forces parallel execution for specified scope.

### Batch Control

```bash
/cw:next --batch 3
```

Limits concurrent agents to specified number.

## Background Agent Management

### Launching Background Agents

```markdown
## Background Agent Launch

FOR step IN current_wave:
  task_id = Task(
    subagent_type: "cw:Builder",
    prompt: "Execute step {step.id}: {step.description}",
    run_in_background: true
  )
  
  Record in parallel_state:
    {
      "step": step.id,
      "task_id": task_id,
      "status": "running",
      "started_at": now()
    }
```

### Collecting Results

```markdown
## Result Collection

FOR agent IN running_agents:
  result = TaskOutput(
    task_id: agent.task_id,
    block: true,          # Wait for completion
    timeout: 300000       # 5 minute timeout
  )
  
  Update parallel_state:
    agent.status = result.success ? "completed" : "failed"
    agent.completed_at = now()
    agent.output = result.output
```

### Handling Failures

```markdown
## Failure Handling in Parallel Execution

WHEN agent_fails(step_id):
  
  [1] Mark step as failed
      parallel_state.agents[step_id].status = "failed"
  
  [2] Check dependent steps
      dependents = find_dependents(step_id)
      
      FOR dependent IN dependents:
        IF dependent.status == "pending":
          dependent.status = "blocked"
          dependent.blocked_by = step_id
  
  [3] Continue other waves
      # Don't stop entire execution
      # Other independent steps continue
  
  [4] Report at wave end
      "⚠️ Step {step_id} failed. Dependent steps blocked."
```

## Integration with /cw:next

### Enhanced Next Command

```markdown
## /cw:next Parallel Flow

[1] Parse arguments
    parallel_mode = determine_mode(args)
    scope = determine_scope(args)  # step, phase, or all

[2] Analyze dependencies
    steps = get_steps(scope)
    deps = extract_dependencies(steps)
    waves = calculate_waves(steps, deps)

[3] Execute by mode
    IF parallel_mode == "sequential":
      execute_sequential(steps)
    ELIF parallel_mode == "auto":
      IF waves[0].length >= 2:
        execute_parallel(waves)
      ELSE:
        execute_sequential(steps)
    ELIF parallel_mode == "parallel":
      execute_parallel(waves)

[4] Report progress
    Show wave completion status
    Show any blocked steps
```

### Display Format

```
🚀 /cw:next --parallel phase 1

Analyzing dependencies...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Wave 1 (3 steps in parallel)
├── 1.1 Create user model         🔄 Running...
├── 1.2 Create auth service       🔄 Running...
└── 1.5 Add documentation         🔄 Running...

Waiting for wave completion...

Wave 1 Complete ✅
├── 1.1 Create user model         ✅ Done (45s)
├── 1.2 Create auth service       ✅ Done (52s)
└── 1.5 Add documentation         ✅ Done (28s)

Wave 2 (1 step)
└── 1.3 Integrate auth            🔄 Running...

Wave 2 Complete ✅
└── 1.3 Integrate auth            ✅ Done (38s)

Wave 3 (1 step)
└── 1.4 Add tests                 🔄 Running...

Wave 3 Complete ✅
└── 1.4 Add tests                 ✅ Done (62s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Phase 1 Complete

📊 Execution Summary:
  • Total steps: 5
  • Waves: 3
  • Total time: 2m 45s
  • Time saved: ~1m 30s (vs sequential)
```

## State Tracking

### `.caw/parallel_state.json`

```json
{
  "schema_version": "1.0",
  "execution_id": "par_20240115_103045",
  "status": "running",
  "started_at": "2024-01-15T10:30:45Z",
  "mode": "auto_parallel",
  "scope": {
    "type": "phase",
    "id": "1"
  },
  "config": {
    "max_concurrency": 5,
    "timeout_per_step": 300000
  },
  "waves": [
    {
      "number": 1,
      "status": "completed",
      "started_at": "2024-01-15T10:30:46Z",
      "completed_at": "2024-01-15T10:31:38Z",
      "agents": [
        {
          "step": "1.1",
          "task_id": "task_uuid_1",
          "status": "completed",
          "started_at": "2024-01-15T10:30:46Z",
          "completed_at": "2024-01-15T10:31:31Z",
          "duration_seconds": 45
        },
        {
          "step": "1.2",
          "task_id": "task_uuid_2",
          "status": "completed",
          "started_at": "2024-01-15T10:30:46Z",
          "completed_at": "2024-01-15T10:31:38Z",
          "duration_seconds": 52
        }
      ]
    }
  ],
  "summary": {
    "total_steps": 5,
    "completed_steps": 5,
    "failed_steps": 0,
    "blocked_steps": 0,
    "total_waves": 3,
    "total_duration_seconds": 165,
    "estimated_sequential_seconds": 255,
    "time_saved_seconds": 90
  }
}
```

## Concurrency Limits

### Default Limits

| Scope | Max Concurrent | Rationale |
|-------|---------------|-----------|
| Same file | 1 | Avoid conflicts |
| Same directory | 3 | Reduce merge conflicts |
| Different directories | 5 | Balance speed vs resources |

### Override with --batch

```bash
# Conservative
/cw:next --parallel --batch 2

# Aggressive
/cw:next --parallel --batch 10
```

## Conflict Prevention

### File-Level Locking

```markdown
## Conflict Detection

BEFORE launching agent for step:
  files_to_modify = estimate_files(step)
  
  FOR file IN files_to_modify:
    IF file IN locked_files:
      # Wait for lock release
      WAIT_FOR_UNLOCK(file)
    ELSE:
      ACQUIRE_LOCK(file)

AFTER agent completes:
  RELEASE_ALL_LOCKS(step)
```

### Merge Strategy

When parallel steps modify related files:

```markdown
## Post-Wave Merge

AFTER wave_completes:
  conflicts = detect_conflicts(wave.outputs)
  
  IF conflicts.length > 0:
    # Run Fixer to resolve
    Task(
      subagent_type: "cw:Fixer",
      prompt: "Resolve merge conflicts: {conflicts}"
    )
```

## Best Practices

### When to Use Parallel

✅ **Good candidates:**
- Independent feature implementations
- Documentation and code in parallel
- Tests for different modules
- Multiple config files

❌ **Avoid parallel for:**
- Steps modifying same file
- Database migrations
- Dependent refactoring steps
- Security-critical changes

### Performance Tips

1. **Group related work**
   - Put related steps in same wave
   - Reduces context switching

2. **Use batch limits**
   - Start with `--batch 3`
   - Increase if stable

3. **Monitor resources**
   - Watch memory usage
   - Reduce concurrency if slow

4. **Review parallel output**
   - Check for subtle conflicts
   - Run tests after parallel phases

## Error Recovery

### Wave Failure Recovery

```markdown
## Recovery Options

WHEN wave_has_failures:
  
  Option 1: Skip failed, continue
    /cw:next --parallel --skip-failed
  
  Option 2: Retry failed steps
    /cw:next --parallel --retry-failed
  
  Option 3: Sequential fallback
    /cw:next --sequential
```

### Blocked Step Resolution

```markdown
## Unblock Strategy

WHEN steps_are_blocked:
  
  [1] Identify blocking step
      blocker = find_blocker(blocked_step)
  
  [2] Fix blocker manually or via fixer
      /cw:fix --step {blocker.id}
  
  [3] Resume parallel execution
      /cw:next --parallel --continue
```

## Schema Reference

See [parallel-state.schema.json](./schemas/parallel-state.schema.json) for complete schema.

## Related Documentation

- [Agent Registry](./agent-registry.md) - Available agents
- [Model Routing](./model-routing.md) - Tier selection
- [Next Command](../commands/next.md) - Execution command
