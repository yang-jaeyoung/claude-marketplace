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

## Delegation Categories

Category-based routing selects agents based on task type, improving selection accuracy beyond complexity alone.

### Category Definitions

```yaml
delegation_categories:
  research:
    description: "Information gathering, exploration, analysis"
    agents:
      - analyst
      - ideator
      - Planner (research phase)
    keywords:
      - research, investigate, explore, analyze
      - understand, discover, learn, study
      - what, why, how, where

  implementation:
    description: "Code writing, feature building"
    agents:
      - Builder (all tiers)
      - Fixer (all tiers)
      - architect
    keywords:
      - implement, build, create, add
      - write, code, develop, construct
      - feature, function, component

  review:
    description: "Code review, validation, compliance"
    agents:
      - Reviewer (all tiers)
      - ComplianceChecker
    keywords:
      - review, check, validate, verify
      - audit, inspect, assess, evaluate
      - compliance, quality, security

  design:
    description: "UX/UI design, architecture planning"
    agents:
      - designer
      - architect
      - ideator
    keywords:
      - design, plan, architect, structure
      - layout, interface, UX, UI
      - mockup, wireframe, prototype

  maintenance:
    description: "Fixes, refactoring, cleanup"
    agents:
      - Fixer (all tiers)
      - Bootstrapper
    keywords:
      - fix, repair, correct, patch
      - refactor, clean, tidy, optimize
      - update, upgrade, migrate
```

### Category Resolution Algorithm

```
FUNCTION resolve_by_category(task_description: string) -> string:

  # [1] Extract keywords from task
  keywords = extract_keywords(task_description)

  # [2] Score each category
  category_scores = {}
  FOR category, config IN delegation_categories:
    score = count_matching_keywords(keywords, config.keywords)
    category_scores[category] = score

  # [3] Select highest scoring category
  best_category = max(category_scores, key=score)

  # [4] Return primary agent for category
  RETURN delegation_categories[best_category].agents[0]
```

### Category + Complexity Combined

The resolver combines category and complexity for optimal selection:

```
FUNCTION resolve_agent_full(task: string, complexity: float) -> string:

  # [1] Determine category
  category = resolve_by_category(task)

  # [2] Get category agents
  agents = delegation_categories[category].agents

  # [3] Select agent by complexity within category
  IF category == "implementation":
    RETURN select_builder_tier(complexity)
  ELIF category == "review":
    RETURN select_reviewer_tier(complexity)
  ELIF category == "research":
    RETURN "analyst"  # No tiering for research
  ELSE:
    RETURN agents[0]  # Primary agent
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
5. **Trust categories**: Category detection improves agent selection accuracy
6. **Combine signals**: Use both category keywords and complexity indicators

## Category Detection Examples

```markdown
# Research task → analyst
"Investigate how the payment system handles refunds"
→ Category: research (keywords: investigate)
→ Agent: analyst

# Implementation task → builder-sonnet (medium complexity)
"Implement user profile page with avatar upload"
→ Category: implementation (keywords: implement)
→ Complexity: 0.55 (medium)
→ Agent: builder-sonnet

# Review task → reviewer-opus (security-related)
"Security audit of the authentication module"
→ Category: review (keywords: audit)
→ Complexity: 0.85 (high, security keyword)
→ Agent: reviewer-opus

# Maintenance task → fixer-haiku (simple fix)
"Fix typo in the login form"
→ Category: maintenance (keywords: fix)
→ Complexity: 0.15 (low)
→ Agent: fixer-haiku
```

## Related Documentation

- [Agent Registry](./agent-registry.md) - Complete agent catalog
- [Model Routing](./model-routing.md) - Tier selection logic
- [Parallel Execution](./parallel-execution.md) - Background task management
- [Background Heuristics](./background-heuristics.md) - Async task management
