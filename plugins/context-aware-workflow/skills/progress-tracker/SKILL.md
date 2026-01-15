---
name: progress-tracker
description: Tracks workflow progress metrics including completion percentage, time spent, and step status. Use to maintain .caw/metrics.json and provide progress visualization.
allowed-tools: Read, Write, Bash
forked-context: true
forked-context-returns: |
  progress: 진행률 %
  current: { phase: N, step: X.Y }
  eta: 예상 완료 시간
  visualization: 컴팩트 프로그레스 바
hooks:
  StepStarted:
    action: record_start
    condition: "requires .caw/ directory"
  StepCompleted:
    action: record_completion
    condition: "requires .caw/ directory"
  PhaseCompleted:
    action: generate_summary
    condition: "requires .caw/ directory"
---

# Progress Tracker

Track and visualize workflow progress with detailed metrics.

## Triggers

This skill activates when:
1. Step status changes (pending → in_progress → completed)
2. Phase transitions
3. `/caw:status` command runs
4. Periodic updates (every 10 minutes)

## Metrics Data

### `.caw/metrics.json` Structure

```json
{
  "task_id": "auth-jwt-implementation",
  "task_title": "JWT Authentication Implementation",
  "started": "2026-01-04T10:00:00Z",
  "estimated_completion": "2026-01-04T14:00:00Z",
  "phases": {
    "phase_1": {
      "name": "Setup",
      "status": "completed",
      "started": "2026-01-04T10:00:00Z",
      "completed": "2026-01-04T10:30:00Z",
      "duration_minutes": 30,
      "steps": {
        "total": 3,
        "completed": 3,
        "in_progress": 0,
        "pending": 0
      }
    },
    "phase_2": {
      "name": "Core Implementation",
      "status": "in_progress",
      "started": "2026-01-04T10:30:00Z",
      "completed": null,
      "duration_minutes": null,
      "steps": {
        "total": 5,
        "completed": 2,
        "in_progress": 1,
        "pending": 2
      }
    },
    "phase_3": {
      "name": "Testing",
      "status": "pending",
      "started": null,
      "completed": null,
      "duration_minutes": null,
      "steps": {
        "total": 3,
        "completed": 0,
        "in_progress": 0,
        "pending": 3
      }
    }
  },
  "totals": {
    "phases_total": 3,
    "phases_completed": 1,
    "steps_total": 11,
    "steps_completed": 5,
    "progress_percentage": 45.5
  },
  "timeline": [
    {
      "timestamp": "2026-01-04T10:00:00Z",
      "event": "workflow_started",
      "details": "Task plan created"
    },
    {
      "timestamp": "2026-01-04T10:30:00Z",
      "event": "phase_completed",
      "details": "Phase 1: Setup completed"
    },
    {
      "timestamp": "2026-01-04T11:15:00Z",
      "event": "step_completed",
      "details": "Step 2.2: Auth middleware"
    }
  ],
  "performance": {
    "avg_step_duration_minutes": 15,
    "fastest_step": { "id": "1.1", "minutes": 5 },
    "slowest_step": { "id": "2.1", "minutes": 35 },
    "quality_gate_pass_rate": 0.85
  },
  "insights_captured": 3,
  "decisions_logged": 2,
  "parallel_execution": {
    "enabled": true,
    "total_batches": 3,
    "max_concurrent_achieved": 3,
    "steps_executed_parallel": ["2.2", "2.3", "3.2", "3.3"],
    "time_saved_minutes": 25,
    "parallel_efficiency": 0.72,
    "speedup_factor": 2.0
  },
  "worktrees": {
    "active": [
      {
        "path": ".worktrees/caw-step-2.2",
        "branch": "caw/step-2.2",
        "step_id": "2.2",
        "status": "completed",
        "merged": true
      },
      {
        "path": ".worktrees/caw-step-2.3",
        "branch": "caw/step-2.3",
        "step_id": "2.3",
        "status": "in_progress",
        "merged": false
      }
    ],
    "total_created": 4,
    "total_merged": 2,
    "merge_conflicts": 0
  }
}
```

## Behavior

### On Step Start

```yaml
action: step_started
updates:
  - Set step status to "in_progress"
  - Record start timestamp
  - Add timeline event
```

### On Step Complete

```yaml
action: step_completed
updates:
  - Set step status to "completed"
  - Record completion timestamp
  - Calculate duration
  - Update totals
  - Check for phase completion
  - Add timeline event
  - Recalculate progress percentage
```

### On Phase Complete

```yaml
action: phase_completed
updates:
  - Set phase status to "completed"
  - Record phase duration
  - Start next phase if exists
  - Update estimated completion
  - Add timeline event
```

## Progress Calculation

### Overall Progress

```python
def calculate_progress(metrics):
    total_steps = metrics['totals']['steps_total']
    completed_steps = metrics['totals']['steps_completed']

    # Weight in-progress as 50% complete
    in_progress = sum(
        phase['steps']['in_progress']
        for phase in metrics['phases'].values()
    )

    effective_completed = completed_steps + (in_progress * 0.5)
    return (effective_completed / total_steps) * 100
```

### Estimated Completion

```python
def estimate_completion(metrics):
    avg_duration = metrics['performance']['avg_step_duration_minutes']
    remaining_steps = (
        metrics['totals']['steps_total'] -
        metrics['totals']['steps_completed']
    )

    remaining_minutes = avg_duration * remaining_steps
    return now() + timedelta(minutes=remaining_minutes)
```

## Visualization

### Progress Bar (for /caw:status)

```
📊 Workflow Progress

JWT Authentication Implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░ 45%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phases:
  ✅ Phase 1: Setup (3/3 steps)         30m
  🔄 Phase 2: Implementation (2/5)      45m+
  ⏳ Phase 3: Testing (0/3)             --

Current: Step 2.3 - Auth middleware validation
Estimated completion: 14:00 (2시간 남음)
```

### Timeline View

```
📅 Activity Timeline

10:00  ▶️  Workflow started
10:05  ✅  Step 1.1: Project setup
10:15  ✅  Step 1.2: Dependencies
10:30  ✅  Step 1.3: Config files
10:30  🎉  Phase 1 completed (30m)
10:35  ✅  Step 2.1: JWT utilities
11:15  ✅  Step 2.2: Auth middleware
11:20  🔄  Step 2.3: Started...

💡 3 insights captured
📋 2 decisions logged
```

### Compact View

```
[45%] Phase 2/3 | Step 5/11 | ETA: 14:00
```

## Parallel & Worktree Tracking

### On Parallel Execution Start

```yaml
action: parallel_batch_started
updates:
  - Record batch start time
  - Log parallel step IDs
  - Increment total_batches
  - Track max_concurrent_achieved
```

### On Parallel Execution Complete

```yaml
action: parallel_batch_completed
updates:
  - Calculate time saved vs sequential
  - Update parallel_efficiency
  - Update speedup_factor
  - Record steps_executed_parallel
```

### Parallel Efficiency Calculation

```python
def calculate_parallel_efficiency(metrics):
    # Theoretical max speedup = number of concurrent steps
    max_concurrent = metrics['parallel_execution']['max_concurrent_achieved']

    # Actual speedup
    sequential_time = sum(step_durations)
    parallel_time = max(step_durations)  # Longest step determines batch time
    actual_speedup = sequential_time / parallel_time

    # Efficiency = actual / theoretical
    efficiency = actual_speedup / max_concurrent
    return efficiency  # 0.0 to 1.0
```

### Worktree State Aggregation

When checking status across multiple worktrees:

```yaml
action: aggregate_worktree_status
workflow:
  1. Scan .worktrees/caw-step-* directories
  2. Read each worktree's .caw/task_plan.md
  3. Extract step status for assigned step
  4. Combine into single view

output:
  worktrees:
    - path: .worktrees/caw-step-2.2
      step: 2.2
      status: ✅ Complete
    - path: .worktrees/caw-step-2.3
      step: 2.3
      status: 🔄 In Progress (45%)
```

### Post-Merge Metrics Update

After `/caw:merge`:

```yaml
action: merge_completed
updates:
  - Mark worktree as merged: true
  - Update main metrics with worktree data
  - Combine timelines
  - Recalculate total progress
  - Record merge_conflicts count
```

### Worktree Progress Visualization

```
📊 Parallel Execution Progress

Main Branch: 45% (5/11 steps)

Worktrees:
  🌳 caw-step-2.2: ✅ Complete (merged)
  🌳 caw-step-2.3: 🔄 70% in progress

Combined Progress: 55% effective
  ├─ Sequential estimate: 3h 20m
  └─ Parallel actual: 2h 10m (⚡ 1.5x speedup)
```

## Performance Analytics

### Step Duration Analysis

```yaml
analytics:
  average_step_time: 15 minutes
  variance: low  # consistent pace

  by_phase:
    phase_1: 10 min/step (setup - fast)
    phase_2: 20 min/step (implementation - normal)

  outliers:
    - step_2.1: 35 min (complex, expected)

  trend: stable  # no slowdown detected
```

### Quality Metrics

```yaml
quality:
  gate_pass_rate: 85%
  first_try_pass: 70%
  avg_retries: 0.3

  common_issues:
    - test_failures: 40%
    - lint_warnings: 35%
    - type_errors: 25%
```

## Integration

### With /caw:status

Progress tracker provides data for status command:

```markdown
## Status Output Components

1. Progress bar visualization
2. Phase/step breakdown
3. Time metrics
4. Current step indicator
5. Estimated completion
```

### With Session Persister

```yaml
session_data:
  includes:
    - current_progress_percentage
    - current_phase
    - current_step
    - elapsed_time
```

### With Quality Gate

```yaml
on_quality_gate_result:
  passed:
    - Record step completion
    - Update pass rate
  failed:
    - Record retry attempt
    - Update failure stats
```

## Notifications

### Milestone Notifications

```yaml
notifications:
  - trigger: phase_completed
    message: "🎉 Phase {n} completed in {duration}!"

  - trigger: progress_50
    message: "📊 Halfway there! 50% complete"

  - trigger: progress_90
    message: "🏁 Almost done! 90% complete"

  - trigger: workflow_completed
    message: "✅ Workflow completed in {total_duration}!"
```

### Warning Notifications

```yaml
warnings:
  - trigger: step_taking_long
    threshold: 2x average
    message: "⏰ Step taking longer than usual"

  - trigger: no_progress
    threshold: 30 minutes
    message: "📌 No progress in 30 minutes"
```

## Boundaries

**Will:**
- Track all step/phase transitions
- Calculate accurate progress metrics
- Provide time estimates
- Store historical performance data

**Will Not:**
- Modify task_plan.md (read-only)
- Make decisions based on metrics
- Alert external systems
- Store indefinitely (follows session retention)

## Forked Context Behavior

See [Forked Context Pattern](../../_shared/forked-context.md).

**Returns**: Progress percentage with visualization

**Output Examples:**
- `📊 [45%] Phase 2/3 | Step 5/11 | ETA: 14:00` - Status
- `🎉 Phase 1 completed (30분)` - Milestone
- `✅ Workflow completed in 3시간 45분` - Completion
