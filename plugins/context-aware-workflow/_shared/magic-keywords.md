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

### Research Keywords

| Keyword | Mode | Behavior |
|---------|------|----------|
| `research` | RESEARCH | Comprehensive info gathering |
| `investigate` | RESEARCH | Thorough exploration |
| `explore` | RESEARCH | Open-ended discovery |

## Mode State

When a keyword is detected, mode state is stored in `.caw/mode.json`:

```json
{
  "active_mode": "DEEP_WORK",
  "activated_at": "2024-01-15T10:30:00Z",
  "keyword_trigger": "deepwork",
  "completion_required": true
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
```

## Detection Rules

1. Keywords are case-insensitive
2. Process only highest priority keyword if multiple detected
3. Mode persists until task completion or explicit reset
4. DEEP_WORK mode prevents stopping until all steps complete

## Integration

Magic Keywords work with:
- `/caw:start` - Sets initial mode for workflow
- `/caw:next` - Maintains mode through execution
- Stop hook - Enforces completion in DEEP_WORK mode
- Model Routing - Influences tier selection
