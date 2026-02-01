---
description: Execute explicit sequential pipeline with defined stages and transitions
argument-hint: "[--stages S1,S2,S3] [--config FILE] [--resume] [--from STAGE]"
---

# /cw:pipeline - Sequential Stage Pipeline

Execute a defined sequence of stages with explicit transitions and checkpoints.

## Usage

```bash
/cw:pipeline --stages "plan,build,review,deploy"   # Run 4-stage pipeline
/cw:pipeline --config pipeline.yaml                # Load from config file
/cw:pipeline --resume                              # Resume interrupted pipeline
/cw:pipeline --from build                          # Start from specific stage
/cw:pipeline --to review                           # Stop at specific stage
/cw:pipeline --skip-stage review                   # Skip specific stage
```

## Behavior

### Step 1: Pipeline Definition

Define stages with explicit dependencies and configurations:

```yaml
# .caw/pipeline.yaml
name: feature-implementation
stages:
  - name: plan
    agent: Planner
    timeout: 300
    checkpoint: true

  - name: build
    agent: Builder
    timeout: 600
    depends_on: plan
    parallel_substeps: true

  - name: review
    agent: Reviewer
    timeout: 300
    depends_on: build
    gate: true  # Must pass to continue

  - name: deploy
    agent: builder-haiku
    timeout: 120
    depends_on: review
    optional: true
```

### Step 2: Stage Execution

```
Pipeline: feature-implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stage 1/4: plan
─────────────────────────────────────────────
Agent: Planner (Sonnet)
Status: ████████████ 100% Complete
Duration: 2m 15s
Checkpoint: ✅ Saved

Stage 2/4: build
─────────────────────────────────────────────
Agent: Builder (Opus)
Status: ████████░░░░ 65% In Progress
Duration: 4m 32s (ongoing)
Substeps: 3/5 complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: 2/4 stages | 41% overall
```

### Step 3: Stage Transitions

```
Stage Transition: plan → build
─────────────────────────────────────────────
Preconditions:
  ✅ Plan document exists
  ✅ No blocking issues
  ✅ Context loaded

Transferring:
  → Plan output: .caw/stages/plan/output.json
  → Context: 12 files (45KB)

Starting build stage...
```

### Step 4: Completion

```
Pipeline Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stages:
  [1] plan     ✅ 2m 15s
  [2] build    ✅ 8m 42s
  [3] review   ✅ 3m 18s
  [4] deploy   ⏭️  Skipped (optional)

Total Duration: 14m 15s
Tokens: 78,500 | Cost: $0.82

Artifacts:
  → Plan: .caw/stages/plan/output.json
  → Code: 8 files modified
  → Review: .caw/stages/review/report.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Flags

### --stages

Define stages inline (comma-separated):

```bash
/cw:pipeline --stages "analyze,implement,test,document"
```

### --config FILE

Load pipeline configuration from file:

```bash
/cw:pipeline --config .caw/pipelines/standard.yaml
```

### --resume

Resume from last checkpoint:

```bash
/cw:pipeline --resume
# Reads .caw/pipeline_state.json
# Continues from last successful checkpoint
```

### --from STAGE

Start from a specific stage (skips prior stages):

```bash
/cw:pipeline --from build
# Assumes plan is complete, starts at build
```

### --to STAGE

Stop after a specific stage:

```bash
/cw:pipeline --to review
# Runs plan → build → review, skips deploy
```

### --skip-stage STAGE

Skip a specific stage:

```bash
/cw:pipeline --skip-stage test
# plan → build → (skip test) → deploy
```

### --dry-run

Preview pipeline without executing:

```bash
/cw:pipeline --dry-run --stages "plan,build,review"
```

Output:
```
Pipeline Preview (dry-run)
─────────────────────────────────────────────
Stages: 3

[1] plan
    Agent: Planner (auto-selected)
    Est. tokens: ~15,000
    Est. time: ~3 minutes

[2] build
    Agent: Builder (auto-selected)
    Est. tokens: ~35,000
    Est. time: ~8 minutes

[3] review
    Agent: Reviewer (auto-selected)
    Est. tokens: ~12,000
    Est. time: ~3 minutes

Total estimates:
    Tokens: ~62,000
    Cost: ~$0.55
    Time: ~14 minutes
```

## Stage Configuration

### Stage Properties

```yaml
stages:
  - name: build               # Required: unique stage name
    description: "Build feature"  # Optional: stage description
    agent: Builder            # Agent to use (auto-selected if omitted)
    model: sonnet             # Force specific model tier
    timeout: 600              # Timeout in seconds
    retries: 2                # Retry count on failure
    checkpoint: true          # Save state after completion
    gate: false               # Must pass to continue (default: false)
    optional: false           # Can be skipped (default: false)
    depends_on: plan          # Explicit dependency
    parallel_substeps: false  # Allow parallel execution within stage
    env:                      # Environment variables for stage
      DEBUG: "true"
    inputs:                   # Input mappings from previous stages
      plan_output: "${plan.output}"
    outputs:                  # Output definitions
      - type: files
        pattern: "src/**/*.ts"
```

### Gate Stages

Gate stages must pass for pipeline to continue:

```yaml
- name: security-scan
  agent: Reviewer
  gate: true
  gate_conditions:
    - no_critical_issues
    - no_high_vulnerabilities
```

If gate fails:
```
Gate Failed: security-scan
─────────────────────────────────────────────
Reason: 2 critical vulnerabilities found

Details:
  → SQL injection in src/api/users.ts:45
  → XSS vulnerability in src/components/Input.tsx:23

Pipeline halted. Fix issues and run:
  /cw:pipeline --from security-scan
```

### Checkpoint Stages

Checkpoints save state for resume:

```yaml
- name: build
  checkpoint: true
  checkpoint_includes:
    - .caw/stages/build/
    - src/
    - tests/
```

## Pipeline State

State is saved in `.caw/pipeline_state.json`:

```json
{
  "pipeline_id": "pipe-abc123",
  "config": "pipeline.yaml",
  "started_at": "2024-01-15T10:00:00Z",
  "current_stage": "build",
  "stages": [
    {
      "name": "plan",
      "status": "completed",
      "started_at": "2024-01-15T10:00:00Z",
      "completed_at": "2024-01-15T10:02:15Z",
      "checkpoint": ".caw/checkpoints/plan.tar.gz"
    },
    {
      "name": "build",
      "status": "in_progress",
      "started_at": "2024-01-15T10:02:16Z"
    }
  ]
}
```

## Built-in Pipelines

### Standard Development Pipeline

```bash
/cw:pipeline --config standard
```

Stages: `plan → build → test → review`

### Quick Fix Pipeline

```bash
/cw:pipeline --config quickfix
```

Stages: `fix → test` (minimal, fast)

### Full Release Pipeline

```bash
/cw:pipeline --config release
```

Stages: `plan → build → test → review → security-scan → deploy`

## Error Handling

### Stage Failure

```
Stage Failed: build
─────────────────────────────────────────────
Error: Build compilation error
Exit code: 1

Options:
  1. Retry stage (/cw:pipeline --from build)
  2. Skip stage (/cw:pipeline --from build --skip-stage build)
  3. Abort pipeline
```

### Retry Logic

```yaml
- name: flaky-test
  retries: 3
  retry_delay: 10  # seconds between retries
  retry_on:
    - timeout
    - exit_code: 1
```

### Rollback

```bash
/cw:pipeline --rollback build
# Restores checkpoint before build stage
```

## Integration

### With /cw:swarm

Pipeline stages can use swarm internally:

```yaml
- name: implement-features
  mode: swarm
  tasks:
    - "Feature A"
    - "Feature B"
    - "Feature C"
```

### With Analytics

Pipeline metrics tracked:

```json
{
  "pipeline_metrics": {
    "pipeline_id": "pipe-abc123",
    "total_duration_s": 855,
    "stage_durations": {
      "plan": 135,
      "build": 522,
      "review": 198
    },
    "bottleneck_stage": "build"
  }
}
```

### With Eco Mode

Eco mode affects pipeline:
- Uses Haiku for all stages (unless gate stage)
- Skips optional stages
- Reduces checkpointing

```bash
/cw:pipeline --config standard --eco
```

## Best Practices

1. **Define gates for quality stages**: Review, security, test stages should gate
2. **Use checkpoints for long pipelines**: Enable resume on failure
3. **Set appropriate timeouts**: Based on expected stage duration
4. **Keep stages focused**: Single responsibility per stage
5. **Use parallel substeps**: For independent work within stages
6. **Document stage inputs/outputs**: Clear data flow

## Related Commands

- [/cw:swarm](./swarm.md) - Parallel agent execution
- [/cw:loop](./loop.md) - Iterative execution
- [/cw:auto](./auto.md) - Automatic workflow

## Related Documentation

- [Skill Composition](../_shared/skill-composition.md) - Layer model
- [Model Routing](../_shared/model-routing.md) - Tier selection
- [Session Management](../_shared/session-management.md) - State persistence
