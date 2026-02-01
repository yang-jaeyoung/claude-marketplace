# Magic Keywords System

Workflow mode activation through natural language keywords.

## Overview

Magic Keywords allow users to activate special workflow modes by including specific words in their prompts. These keywords are detected by CAW commands and agents.

## Supported Keywords

### Continuation Keywords (Highest Priority)

| Keyword | Mode | Behavior |
|---------|------|----------|
| `deepwork` | DEEP_WORK | Complete ALL tasks without stopping |
| `fullwork` | DEEP_WORK | Same as deepwork |
| `ultrawork` | DEEP_WORK | Same as deepwork |
| `nonstop` | CONTINUOUS | Continue until explicit stop |
| `keepgoing` | CONTINUOUS | Same as nonstop |

### Thinking Keywords

| Keyword | Mode | Behavior |
|---------|------|----------|
| `thinkhard` | DEEP_ANALYSIS | Extended reasoning, multi-approach |
| `ultrathink` | DEEP_ANALYSIS | Maximum analysis depth |
| `think` | DEEP_ANALYSIS | Standard deep analysis |

### Speed Keywords

| Keyword | Mode | Behavior |
|---------|------|----------|
| `quickfix` | MINIMAL_CHANGE | Essential changes only |
| `quick` | MINIMAL_CHANGE | Prioritize speed |
| `fast` | MINIMAL_CHANGE | Skip optional improvements |

### Economy Keywords (Cost Optimization)

| Keyword | Mode | Behavior |
|---------|------|----------|
| `ecomode` | ECO | Force Haiku, skip optional phases, minimize context |
| `eco` | ECO | Same as ecomode |
| `budget` | ECO | Cost-conscious execution |
| `cheap` | ECO | Minimize token usage |
| `frugal` | ECO | Same as eco |

**ECO Mode Effects:**
- Force Haiku tier for all agents (30-50% cost reduction)
- Skip optional phases: `reflect`, `check`, extensive context loading
- Minimize context: Load only essential files
- Disable verbose logging
- Prefer cached results when available

### Research Keywords

| Keyword | Mode | Behavior |
|---------|------|----------|
| `research` | RESEARCH | Comprehensive info gathering |
| `investigate` | RESEARCH | Thorough exploration |
| `explore` | RESEARCH | Open-ended discovery |

### Background Control Keywords

| Keyword | Mode | Behavior |
|---------|------|----------|
| `nowait` | ASYNC | Force background execution |
| `async` | ASYNC | Same as nowait |
| `background` | ASYNC | Run tasks asynchronously |
| `wait` | SYNC | Force foreground execution |
| `sync` | SYNC | Same as wait |
| `blocking` | SYNC | Wait for completion |

## Mode State

When a keyword is detected, mode state is stored in `.caw/mode.json`:

```json
{
  "active_mode": "DEEP_WORK",
  "activated_at": "2024-01-15T10:30:00Z",
  "keyword_trigger": "deepwork",
  "completion_required": true,
  "eco_mode": false,
  "background_mode": null
}
```

## Usage Examples

```bash
# Deep work mode - complete all tasks
"deepwork implement the authentication system"

# Quick fixes only
"quickfix the failing tests"

# Research first
"research how other projects handle caching"

# Extended analysis
"thinkhard about the architecture design"

# Economy mode - cost-conscious execution
"ecomode fix the API response format"

# Force async execution
"async run the test suite"
```

## Detection Rules

1. Keywords are case-insensitive
2. Process only highest priority keyword if multiple detected
3. Mode persists until task completion or explicit reset
4. DEEP_WORK mode signals agents to prioritize thorough completion

## Integration

Magic Keywords work with:
- `/cw:start` - Sets initial mode for workflow
- `/cw:next` - Maintains mode through execution
- `/cw:status` - Shows current active mode
- Model Routing - Influences tier selection
- Background Heuristics - Override async behavior
- Analytics - Track cost savings in eco mode
