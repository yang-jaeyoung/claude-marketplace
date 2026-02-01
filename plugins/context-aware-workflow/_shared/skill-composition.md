# Skill Composition Model

3-layer skill architecture for structured workflow execution.

## Overview

The Skill Composition Model organizes skills into three hierarchical layers, ensuring proper sequencing and dependency management:

```
┌─────────────────────────────────────────────┐
│            GUARANTEE LAYER                   │
│    (Pre-conditions, validation, safety)     │
├─────────────────────────────────────────────┤
│           ENHANCEMENT LAYER                  │
│    (Optimization, analysis, enrichment)     │
├─────────────────────────────────────────────┤
│            EXECUTION LAYER                   │
│    (Core action, implementation, output)    │
└─────────────────────────────────────────────┘
```

## Layer Definitions

### 1. Guarantee Layer (Pre-execution)

Skills that ensure preconditions are met before any action is taken.

| Skill | Purpose | Blocks on Failure |
|-------|---------|-------------------|
| `quality-gate` | Validate code quality thresholds | Yes |
| `commit-discipline` | Enforce commit conventions | Yes |
| `plan-detector` | Verify task plan exists | Yes |
| `context-helper` | Ensure required context is loaded | No (degrades) |

**Characteristics:**
- Run before main execution
- Can block workflow if preconditions fail
- Provide clear error messages for failures
- Are idempotent (safe to run multiple times)

### 2. Enhancement Layer (Optimization)

Skills that improve quality but don't block execution.

| Skill | Purpose | Optional |
|-------|---------|----------|
| `insight-collector` | Capture learnings | Yes |
| `pattern-learner` | Learn from usage | Yes |
| `dependency-analyzer` | Analyze cross-module dependencies | Yes |
| `context-manager` | Optimize context loading | Yes |
| `hud` | Real-time metrics display | Yes |

**Characteristics:**
- Run in parallel with or after guarantees
- Failures degrade gracefully (don't block)
- Can be skipped in eco mode
- Enhance but don't transform the workflow

### 3. Execution Layer (Core Action)

Skills that perform the primary workflow action.

| Skill | Purpose | Required |
|-------|---------|----------|
| `reflect` | Ralph Loop reflection | Conditional |
| `research` | Information gathering | Conditional |
| `review-assistant` | Code review support | Conditional |
| `quick-fix` | Apply quick fixes | Conditional |
| `session-persister` | Persist session state | Yes |

**Characteristics:**
- Perform the actual work
- Sequential execution (one at a time)
- Results are captured for next steps
- Can invoke sub-skills as needed

## Composition Patterns

### Sequential Composition

Skills execute in order, each building on previous results:

```
plan-detector → context-manager → insight-collector → reflect
     ↓                ↓                  ↓              ↓
  Validate         Load ctx         Capture          Execute
```

### Parallel Composition

Independent skills run simultaneously:

```
              ┌─ hud (metrics display)
              │
main-task ───┼─ insight-collector (learning)
              │
              └─ pattern-learner (analysis)
```

### Conditional Composition

Skills execute based on conditions:

```
IF mode == "DEEP_WORK":
  reflect → insight-collector → evolve
ELIF mode == "ECO":
  [skip enhancement layer]
  execute-only
ELSE:
  standard-composition
```

## Skill Manifest Format

Each skill declares its layer and dependencies in SKILL.md:

```yaml
---
name: quality-gate
layer: guarantee
description: Validate code quality thresholds
dependencies: []  # No dependencies
blocks-on-failure: true
eco-mode-skip: false
---
```

```yaml
---
name: insight-collector
layer: enhancement
description: Capture learnings from workflow execution
dependencies:
  - context-manager  # Needs context loaded
blocks-on-failure: false
eco-mode-skip: true  # Skip in eco mode
---
```

```yaml
---
name: reflect
layer: execution
description: Ralph Loop continuous improvement reflection
dependencies:
  - plan-detector
  - context-manager
blocks-on-failure: true
eco-mode-skip: false
---
```

## Composition Algorithm

```python
def compose_skills(task: Task, mode: Mode) -> SkillChain:
    skills = []

    # [1] Guarantee Layer - always runs first
    for skill in get_layer_skills("guarantee"):
        if skill.is_applicable(task):
            skills.append(skill)

    # [2] Enhancement Layer - conditional
    if mode != "ECO":
        for skill in get_layer_skills("enhancement"):
            if skill.is_applicable(task):
                skills.append(SkillNode(
                    skill=skill,
                    parallel=True,  # Run in background
                    required=False
                ))

    # [3] Execution Layer - based on task
    for skill in get_layer_skills("execution"):
        if skill.matches_task(task):
            skills.append(skill)

    # [4] Resolve dependencies
    chain = resolve_dependencies(skills)

    return chain
```

## Eco Mode Optimization

In eco mode, the enhancement layer is skipped:

```
Standard Mode:
  guarantee → enhancement → execution

Eco Mode:
  guarantee → execution (enhancement skipped)
```

Skills with `eco-mode-skip: true` are bypassed, reducing:
- Token usage (30-50% reduction)
- Execution time
- Cost

## Error Handling

### Guarantee Layer Failures

```
quality-gate fails
    ↓
BLOCK workflow
    ↓
Return error: "Quality gate failed: [reason]"
    ↓
User must fix before retry
```

### Enhancement Layer Failures

```
insight-collector fails
    ↓
LOG warning: "Enhancement failed (non-blocking)"
    ↓
CONTINUE with execution layer
    ↓
Note degraded mode in output
```

### Execution Layer Failures

```
reflect fails
    ↓
RETRY with backoff (up to 3 times)
    ↓
If still fails: BLOCK and notify
    ↓
Save state for resume
```

## Integration with Other Systems

### With Model Routing

Each layer has preferred model tiers:
- **Guarantee**: Haiku (fast, cheap validation)
- **Enhancement**: Haiku/Sonnet (background processing)
- **Execution**: Based on task complexity

### With Background Heuristics

Enhancement layer skills typically run in background:
```json
{
  "enhancement_background": true,
  "default_timeout": 30,
  "silent": true
}
```

### With Analytics

Layer-level metrics tracked:
```json
{
  "layer_metrics": {
    "guarantee": {"tokens": 500, "duration_ms": 200},
    "enhancement": {"tokens": 2000, "duration_ms": 5000},
    "execution": {"tokens": 15000, "duration_ms": 45000}
  }
}
```

## Best Practices

1. **Keep guarantees fast**: Sub-second validation preferred
2. **Make enhancements optional**: Should never block core workflow
3. **Isolate execution**: Each execution skill should be self-contained
4. **Use parallel where possible**: Enhancement layer benefits most
5. **Fail gracefully**: Enhancements should log, not crash
6. **Respect eco mode**: Mark optional skills as skippable

## Related Documentation

- [Agent Resolver](./agent-resolver.md) - Agent selection
- [Model Routing](./model-routing.md) - Tier selection
- [Background Heuristics](./background-heuristics.md) - Async execution
- [Magic Keywords](./magic-keywords.md) - Mode activation
