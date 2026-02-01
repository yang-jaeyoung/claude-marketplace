# Model Routing System

Intelligent complexity-based model selection for CAW agents.

## Overview

The Model Routing System automatically selects the appropriate model tier (Haiku/Sonnet/Opus) based on task complexity, optimizing for cost and performance.

## Model Tiers

| Tier | Complexity | Best For | Cost | Latency |
|------|------------|----------|------|---------|
| **Haiku** | 0-30% | Simple tasks, boilerplate, formatting | Low | Fast |
| **Sonnet** | 30-70% | Standard tasks, code review, planning | Medium | Moderate |
| **Opus** | 70-100% | Complex reasoning, architecture, security | High | Slower |

## Complexity Calculation

Complexity score (0.0 - 1.0) is calculated from:

### Indicators

| Factor | Weight | Low (0.0) | Medium (0.5) | High (1.0) |
|--------|--------|-----------|--------------|------------|
| **File Count** | 20% | 1-3 files | 4-10 files | 10+ files |
| **Scope Keywords** | 30% | fix, update, typo | feature, implement | architecture, security |
| **Cross-Module** | 25% | Single directory | 2-3 modules | System-wide |
| **Dependencies** | 15% | None | Internal | External/API |
| **User Override** | 100% | "quick", "fast" | "standard" | "complex", "deep" |

### Formula

```
complexity = sum(indicator_score * weight) / sum(weights)

If user_override detected:
  complexity = override_value (0.2 for haiku, 0.5 for sonnet, 0.9 for opus)
```

## Agent Routing Rules

### Bootstrapper
- **Default**: Haiku (always)
- **Upgrades**: Never (initialization is always simple)
- **Rationale**: Fast environment setup, no complex reasoning needed

### Planner
- **Default**: Sonnet
- **Upgrade to Opus**: Architecture planning, large scope, security-critical
- **Downgrade to Haiku**: Simple feature, single-file scope
- **Variants**: `planner-haiku.md`, `planner.md` (sonnet), `planner-opus.md`

### Builder
- **Default**: Sonnet
- **Upgrade to Opus**: Complex algorithms, security-critical code, performance optimization
- **Downgrade to Haiku**: Boilerplate, simple CRUD, formatting
- **Variants**: `builder-haiku.md`, `builder-sonnet.md`, `builder.md` (opus)

### Reviewer
- **Default**: Sonnet
- **Upgrade to Opus**: Security audit, architecture review, deep analysis
- **Downgrade to Haiku**: Quick check, style-only review
- **Variants**: `reviewer-haiku.md`, `reviewer.md` (sonnet), `reviewer-opus.md`

### Fixer
- **Default**: Sonnet
- **Upgrade to Opus**: Multi-file refactor, architecture changes, security fixes
- **Downgrade to Haiku**: Auto-fix, simple renames
- **Variants**: `fixer-haiku.md`, `fixer-sonnet.md`, `fixer.md` (opus)

## Usage Examples

### Automatic Routing
```bash
# Simple task → Haiku
/cw:start "fix typo in README"
# → Builder-Haiku selected (complexity: 0.15)

# Standard task → Sonnet
/cw:start "implement user profile page"
# → Builder-Sonnet selected (complexity: 0.55)

# Complex task → Opus
/cw:start "redesign authentication architecture"
# → Builder-Opus selected (complexity: 0.85)
```

### Manual Override
```bash
# Force fast execution
/cw:start "quick fix the login bug"
# → Haiku forced via "quick" keyword

# Force thorough analysis
/cw:review --deep security audit
# → Opus forced via "deep" keyword
```

## Tier Selection Flow

```
1. Parse task description
2. Calculate complexity score
3. Check for user override keywords
4. Select appropriate tier:
   - score ≤ 0.3 → Haiku
   - 0.3 < score ≤ 0.7 → Sonnet  
   - score > 0.7 → Opus
5. Load tiered agent variant
6. Announce: "🎯 Model: [TIER] selected (complexity: X.XX)"
```

## Cost Optimization

- **Prefer Lower Tier**: When complexity is ambiguous, use lower cost tier
- **Cascade on Failure**: If lower tier produces poor results, upgrade automatically
- **Max Cascades**: 1 upgrade per task (prevents infinite cost escalation)

## Integration with Magic Keywords

Model tier can be influenced by magic keywords from `mode.json`:

| Mode | Preferred Tier |
|------|----------------|
| MINIMAL_CHANGE | Haiku (fast, essential changes) |
| NORMAL | Sonnet (balanced) |
| DEEP_ANALYSIS | Opus (thorough reasoning) |
| DEEP_WORK | Sonnet (efficient completion) |

## Schema Reference

See [model-routing.schema.json](../schemas/model-routing.schema.json) for complete schema definition.
