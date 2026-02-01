---
description: Execute explicit sequential pipeline with defined stages and transitions
argument-hint: "[--stages S1,S2,S3] [--config FILE] [--resume] [--from STAGE]"
---

# /cw:pipeline - Sequential Stage Pipeline

Execute a defined sequence of stages with explicit transitions and checkpoints.

## Usage

```bash
/cw:pipeline --stages "plan,build,review,deploy"   # Run 4-stage pipeline
/cw:pipeline --config pipeline.yaml                # Load from config
/cw:pipeline --resume                              # Resume interrupted
/cw:pipeline --from build                          # Start from stage
/cw:pipeline --to review                           # Stop at stage
/cw:pipeline --skip-stage review                   # Skip stage
/cw:pipeline --dry-run                             # Preview only
```

## Flags

| Flag | Description |
|------|-------------|
| `--stages` | Inline stage list (comma-separated) |
| `--config` | Load from YAML config file |
| `--resume` | Resume from last checkpoint |
| `--from` | Start from specific stage |
| `--to` | Stop after specific stage |
| `--skip-stage` | Skip a stage |
| `--dry-run` | Preview without executing |
| `--rollback` | Restore checkpoint before stage |

## Stage Configuration

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
    depends_on: plan
    parallel_substeps: true

  - name: review
    agent: Reviewer
    gate: true  # Must pass to continue

  - name: deploy
    agent: builder-haiku
    optional: true
```

### Stage Properties

| Property | Description |
|----------|-------------|
| `name` | Unique stage identifier |
| `agent` | Agent to use (auto-selected if omitted) |
| `model` | Force model tier (sonnet/opus/haiku) |
| `timeout` | Timeout in seconds |
| `retries` | Retry count on failure |
| `checkpoint` | Save state after completion |
| `gate` | Must pass to continue |
| `optional` | Can be skipped |
| `depends_on` | Explicit dependency |
| `parallel_substeps` | Allow parallel execution within stage |

## Gate Stages

Gates must pass for pipeline to continue:

```yaml
- name: security-scan
  gate: true
  gate_conditions:
    - no_critical_issues
    - no_high_vulnerabilities
```

Gate failure halts pipeline with fix instructions.

## Built-in Pipelines

| Config | Stages |
|--------|--------|
| `standard` | plan → build → test → review |
| `quickfix` | fix → test |
| `release` | plan → build → test → review → security-scan → deploy |

## Error Handling

| Scenario | Options |
|----------|---------|
| Stage failure | Retry, skip, or abort |
| Gate failure | Fix issues, resume from gate |
| Timeout | Retry with extended timeout |

Retry configuration:
```yaml
- name: flaky-test
  retries: 3
  retry_delay: 10
  retry_on: [timeout, exit_code: 1]
```

## Pipeline State

State saved in `.caw/pipeline_state.json`:
- Current stage and status
- Completed stage timestamps
- Checkpoint locations

## Integration

### With /cw:swarm

```yaml
- name: implement-features
  mode: swarm
  tasks: ["Feature A", "Feature B", "Feature C"]
```

### With Eco Mode

```bash
/cw:pipeline --config standard --eco
# Uses Haiku for all stages (unless gate)
# Skips optional stages
```

## Best Practices

1. **Gate quality stages**: Review, security, test
2. **Checkpoint long pipelines**: Enable resume
3. **Set timeouts**: Based on expected duration
4. **Keep stages focused**: Single responsibility
5. **Use parallel substeps**: For independent work

## Related

- [/cw:swarm](./swarm.md) - Parallel execution
- [/cw:loop](./loop.md) - Iterative execution
- [/cw:auto](./auto.md) - Automatic workflow
