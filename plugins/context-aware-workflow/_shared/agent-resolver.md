# Agent Resolver System

Intelligent agent resolution based on task complexity and model routing.

## Overview

The Agent Resolver System selects the appropriate agent variant based on task complexity, ensuring optimal model tier usage for cost and performance.

## Agent Resolution Strategy

```
┌────────────────────────────────────────────────────────────────┐
│                  AGENT RESOLUTION STRATEGY                      │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Request: cw:Builder                                           │
│         ↓                                                       │
│   [1] Calculate Task Complexity                                 │
│         ↓                                                       │
│   [2] Select Appropriate Tier                                   │
│         ↓                                                       │
│   ┌─────────────────┬─────────────────┬─────────────────────┐  │
│   │  Low (≤0.3)     │  Medium (0.3-0.7)│  High (>0.7)       │  │
│   │                 │                  │                     │  │
│   │  builder-haiku  │  builder-sonnet  │  Builder (opus)    │  │
│   └─────────────────┴─────────────────┴─────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Resolution Algorithm

```markdown
## Agent Resolution Process

FUNCTION resolve_agent(requested_agent: string, complexity: float):

  [1] Parse agent request
      base_name = extract_base_name(requested_agent)  // "builder", "planner", etc.

  [2] Check if tiered agent
      IF base_name in TIERED_AGENTS:
        tier = complexity_to_tier(complexity)
        RETURN get_tiered_variant(base_name, tier)

  [3] Return as-is for non-tiered agents
      RETURN requested_agent
```

## Tiered Agent Mapping

### Complexity Thresholds

| Complexity Range | Tier | Description |
|------------------|------|-------------|
| 0.0 - 0.3 | Haiku | Simple tasks, boilerplate, formatting |
| 0.3 - 0.7 | Sonnet | Standard development, multi-step features |
| 0.7 - 1.0 | Opus | Complex architecture, security-critical |

### Tiered Agents

| Agent Base | Haiku | Sonnet | Opus (Default) |
|------------|-------|--------|----------------|
| Planner | planner-haiku | Planner | planner-opus |
| Builder | builder-haiku | builder-sonnet | Builder |
| Reviewer | reviewer-haiku | Reviewer | reviewer-opus |
| Fixer | fixer-haiku | fixer-sonnet | Fixer |

### Non-Tiered Agents

These agents use a single tier:

| Agent | Fixed Tier |
|-------|------------|
| Bootstrapper | Haiku |
| architect | Opus |
| designer | Sonnet |
| ideator | Sonnet |
| ComplianceChecker | Sonnet |

## Usage Examples

### Automatic Resolution

```markdown
## Task: "Fix typo in README"
complexity = 0.1  # Low complexity
agent = resolve_agent("cw:Builder", complexity)
# Returns: "cw:builder-haiku"
```

```markdown
## Task: "Implement user authentication"
complexity = 0.5  # Medium complexity
agent = resolve_agent("cw:Builder", complexity)
# Returns: "cw:builder-sonnet"
```

```markdown
## Task: "Redesign security architecture"
complexity = 0.85  # High complexity
agent = resolve_agent("cw:Builder", complexity)
# Returns: "cw:Builder" (Opus)
```

### Manual Override

Users can force a specific tier using keywords:

| Keyword | Effect |
|---------|--------|
| `quick`, `fast`, `simple` | Force Haiku |
| `standard` | Force Sonnet |
| `deep`, `thorough`, `security` | Force Opus |

## Integration Points

### With Commands

Each command uses the resolver for agent selection:

```markdown
/cw:review                    # Auto-select based on scope
/cw:review --quick            # Force reviewer-haiku
/cw:review --deep             # Force reviewer-opus
```

### With Model Routing

The resolver integrates with the model routing system:

```markdown
tier = calculate_tier(task_complexity)
agent = resolve_agent(base_agent, tier)
Task(subagent_type=agent, prompt=...)
```

## Best Practices

1. **Let the system choose**: Default complexity-based selection is optimal
2. **Override sparingly**: Only force tiers when you have specific needs
3. **Use keywords naturally**: "Quick fix" or "deep review" work intuitively
4. **Monitor costs**: Higher tiers cost more, use when needed

## Related Documentation

- [Agent Registry](./agent-registry.md) - Complete agent catalog
- [Model Routing](./model-routing.md) - Tier selection logic
- [Parallel Execution](./parallel-execution.md) - Background task management
