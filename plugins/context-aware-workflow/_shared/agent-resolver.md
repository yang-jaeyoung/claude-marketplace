# Agent Resolver System

Intelligent agent resolution with OMC integration and graceful degradation.

## Overview

The Agent Resolver System provides seamless integration between CAW (Context-Aware Workflow) and OMC (Oh-My-ClaudeCode) plugins. When OMC is available, it enables access to powerful specialized agents. When OMC is not installed, the system gracefully falls back to equivalent CAW agents, ensuring all functionality remains available.

## Core Principle: CAW Independence

**CAW must function completely without OMC.** All OMC features are enhancements, not requirements.

```
┌────────────────────────────────────────────────────────────────┐
│                  AGENT RESOLUTION STRATEGY                      │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Request: omc:architect                                        │
│         ↓                                                       │
│   [1] Check OMC Availability                                    │
│         ↓                                                       │
│   ┌─────────────────┬─────────────────────────────────────────┐│
│   │  OMC Present ✅  │  OMC Missing ❌                          ││
│   │                 │                                          ││
│   │  omc:architect  │  → cw:architect (CAW Fallback)           ││
│   │  (Use as-is)    │  → Warning: "Using CAW fallback agent"   ││
│   │                 │  → Core functionality preserved          ││
│   └─────────────────┴─────────────────────────────────────────┘│
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Agent Mapping Table

### OMC → CAW Fallback Mapping

| OMC Agent | Model | CAW Fallback | Fallback Model | Capability Difference |
|-----------|-------|--------------|----------------|----------------------|
| `omc:architect` | Opus | `cw:architect` | Opus | None (equivalent) |
| `omc:architect-low` | Haiku | `cw:architect` | Sonnet | Higher tier fallback |
| `omc:architect-medium` | Sonnet | `cw:architect` | Sonnet | None (equivalent) |
| `omc:researcher` | Sonnet | `cw:Planner` | Sonnet | Manual web search |
| `omc:researcher-low` | Haiku | `cw:planner-haiku` | Haiku | None (equivalent) |
| `omc:scientist` | Sonnet | `cw:Builder` | Sonnet | Manual data analysis |
| `omc:scientist-high` | Opus | `cw:Builder` | Sonnet | Lower tier fallback |
| `omc:scientist-low` | Haiku | `cw:builder-haiku` | Haiku | None (equivalent) |
| `omc:explore` | Haiku | `Explore` | Haiku | Native explore agent |
| `omc:explore-medium` | Sonnet | `Explore` | Haiku | Lower tier fallback |
| `omc:executor` | Sonnet | `cw:Builder` | Sonnet | Less specialized |
| `omc:executor-high` | Opus | `cw:Builder` | Sonnet | Lower tier fallback |
| `omc:executor-low` | Haiku | `cw:builder-haiku` | Haiku | None (equivalent) |
| `omc:qa-tester` | Sonnet | `cw:Reviewer` | Sonnet | Manual test execution |
| `omc:critic` | Opus | `cw:reviewer-opus` | Opus | Less focused critique |
| `omc:analyst` | Opus | `cw:planner-opus` | Opus | Less data-focused |
| `omc:build-fixer` | Sonnet | `cw:Fixer` | Sonnet | Generic fixing |
| `omc:build-fixer-low` | Haiku | `cw:fixer-haiku` | Haiku | None (equivalent) |
| `omc:security-reviewer` | Opus | `cw:reviewer-opus` | Opus | Less security-focused |
| `omc:security-reviewer-low` | Haiku | `cw:reviewer-haiku` | Haiku | Less security-focused |
| `omc:code-reviewer` | Opus | `cw:reviewer-opus` | Opus | Less specialized |
| `omc:code-reviewer-low` | Haiku | `cw:reviewer-haiku` | Haiku | Less specialized |
| `omc:designer` | Sonnet | `cw:designer` | Sonnet | None (equivalent) |
| `omc:designer-high` | Opus | `cw:designer` | Sonnet | Lower tier fallback |
| `omc:designer-low` | Haiku | `cw:designer` | Sonnet | Higher tier fallback |
| `omc:writer` | Sonnet | `general-purpose` | Sonnet | No specialized prompt |
| `omc:vision` | Sonnet | `general-purpose` | Sonnet | No specialized prompt |
| `omc:tdd-guide` | Sonnet | `cw:Builder` | Sonnet | Less TDD focus |
| `omc:tdd-guide-low` | Haiku | `cw:builder-haiku` | Haiku | Less TDD focus |
| `omc:planner` | Opus | `cw:Planner` | Sonnet | Lower tier fallback |

## Detection Logic

### OMC Availability Check

The resolver checks OMC availability through multiple methods:

```markdown
## Detection Methods (in order)

1. **Task Tool Description Check**
   - Search for "omc:" prefix in Task tool's available agent types
   - Most reliable runtime detection

2. **Plugin Directory Check**
   - Look for ~/.claude/plugins/oh-my-claudecode/
   - Or similar plugin installation paths

3. **Environment Variable**
   - Check for OMC_ENABLED=true
   - Allows explicit override

## Detection Result Caching

- Cache detection result in memory for session
- Store in context_manifest.json for persistence:

```json
{
  "environment": {
    "omc_available": true,
    "omc_version": "2.1.0",
    "detection_method": "task_tool",
    "detected_at": "2024-01-15T10:30:00Z"
  }
}
```
```

### Implementation Script

The detection and resolution logic is implemented in `hooks/scripts/omc_resolver.py`.

#### Key Functions

| Function | Description | Returns |
|----------|-------------|---------|
| `detect_omc()` | Full detection with metadata | `Dict` with all fields |
| `is_omc_available()` | Quick availability check (cached) | `bool` |
| `resolve_agent(agent)` | Resolve with fallback | `(resolved, is_fallback, warning)` |
| `get_fallback_map()` | Complete fallback mapping | `Dict[str, str]` |
| `update_manifest_environment(path)` | Write to manifest | `bool` |

#### CLI Usage

```bash
# Check OMC detection status
python hooks/scripts/omc_resolver.py

# Resolve an agent
python hooks/scripts/omc_resolver.py resolve omc:architect

# Show all fallback mappings
python hooks/scripts/omc_resolver.py fallbacks

# Update context_manifest.json
python hooks/scripts/omc_resolver.py update-manifest

# Enable debug output
set OMC_DEBUG=enabled && python hooks/scripts/omc_resolver.py
```

#### Usage in Skills/Commands

```python
# Import and use in Python
from omc_resolver import resolve_agent, is_omc_available

if is_omc_available():
    agent = "omc:architect"
else:
    agent, _, _ = resolve_agent("omc:architect")
    # agent = "cw:architect" (fallback)
```

#### Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `OMC_ENABLED` | `true`, `1`, `enabled` | Force OMC as available |
| `OMC_DEBUG` | `enabled`, `true`, `1` | Enable debug logging to stderr |

### Resolution Algorithm

```markdown
## Agent Resolution Process

FUNCTION resolve_agent(requested_agent: string):

  [1] Parse agent request
      namespace = extract_namespace(requested_agent)  // "cw" or "omc"
      agent_name = extract_name(requested_agent)      // "architect", "builder", etc.
      tier = extract_tier(requested_agent)            // "haiku", "sonnet", "opus" or null

  [2] Handle CAW-native agents
      IF namespace == "cw":
        RETURN requested_agent  // No resolution needed

  [3] Handle OMC agents
      IF namespace == "omc":
        IF omc_available():
          RETURN requested_agent  // Use OMC agent
        ELSE:
          fallback = FALLBACK_MAP[requested_agent]
          LOG_WARNING("OMC not available, using fallback: {fallback}")
          RETURN fallback

  [4] Handle bare agent names
      IF namespace == null:
        // Assume CAW agent
        RETURN "cw:" + agent_name

  [5] Unknown namespace
      LOG_ERROR("Unknown agent namespace: {namespace}")
      RETURN null
```

## Warning Messages

### Fallback Activation Warning

When OMC agent is requested but unavailable:

```
⚠️ OMC Agent Fallback Active

Requested: omc:architect
Using:     cw:architect (CAW equivalent)

Note: OMC plugin not detected. Some advanced features may be limited.
Install OMC for full functionality: https://github.com/oh-my-claudecode

---
Continuing with fallback agent...
```

### Feature Degradation Warnings

Specific warnings for commands that lose functionality:

```markdown
## /cw:ultraqa Degradation Warning

⚠️ Running UltraQA in Basic Mode

OMC agents not available. Using simplified diagnostics:
- Build errors: Direct error parsing
- Test failures: Stacktrace analysis
- Lint issues: Standard review

For advanced root cause analysis, install OMC plugin.

---
Proceeding with basic mode...
```

```markdown
## /cw:research Degradation Warning

⚠️ Running Research in Basic Mode

OMC researchers not available. Using direct tools:
- External: WebSearch + WebFetch
- Internal: Serena symbolic tools
- Analysis: Bash + Python scripts

For specialized research agents, install OMC plugin.

---
Proceeding with basic mode...
```

## Integration Points

### 1. Command-Level Integration

Each command using OMC agents should call resolver:

```markdown
## Example: /cw:qaloop Integration

BEFORE executing QA loop:

  [1] Resolve build agent
      build_agent = resolve_agent("omc:executor")
      // Returns "omc:executor" or "cw:builder"

  [2] Resolve diagnose agent
      diagnose_agent = resolve_agent("omc:architect")
      // Returns "omc:architect" or "cw:architect"

  [3] Resolve fix agent
      fix_agent = resolve_agent("omc:executor")
      // Returns "omc:executor" or "cw:fixer"
```

### 2. Model Routing Integration

Agent resolver respects model routing:

```markdown
## Tier Preservation

When falling back, preserve requested tier:

  omc:architect-opus → cw:architect (Opus by default)
  omc:executor-haiku → cw:builder-haiku
  omc:critic → cw:reviewer-opus (Opus is default for critic)
```

### 3. Context Manifest Integration

Environment info stored in manifest:

```json
{
  "schema_version": "1.0",
  "project": { ... },
  "environment": {
    "omc_available": false,
    "omc_version": null,
    "fallback_mode": true,
    "degraded_features": [
      "ultraqa:advanced_diagnosis",
      "research:specialized_agents",
      "qaloop:intelligent_fix"
    ],
    "last_check": "2024-01-15T10:30:00Z"
  }
}
```

## Usage Examples

### Direct Agent Resolution

```bash
# In skill/command implementation
resolved = resolve_agent("omc:architect")
Task(subagent_type=resolved, prompt="...")
```

### Conditional Logic

```markdown
IF omc_available():
  # Use advanced OMC features
  diagnose_agent = "omc:architect"
  analysis_depth = "deep"
ELSE:
  # Use CAW fallback
  diagnose_agent = "cw:reviewer-opus"
  analysis_depth = "standard"
  WARN "Running in basic mode"
```

### Batch Resolution

```markdown
FOR each agent in required_agents:
  resolved_agents.append(resolve_agent(agent))

IF any_fallbacks_used:
  DISPLAY_ONCE "Some OMC agents unavailable, using CAW equivalents"
```

## Best Practices

### For Command Authors

1. **Always use resolver** - Never hardcode OMC agents
2. **Handle fallbacks gracefully** - Provide useful warnings
3. **Test both paths** - Verify behavior with and without OMC
4. **Document degradation** - Clearly state what's lost

### For Users

1. **Check status** - Run `/cw:status` to see environment
2. **Install OMC** - For full functionality
3. **Understand limitations** - Know what fallbacks mean

## Schema Reference

### Agent Resolution Request

```json
{
  "requested_agent": "omc:architect",
  "context": {
    "command": "qaloop",
    "step": "diagnose",
    "task_complexity": 0.75
  }
}
```

### Agent Resolution Response

```json
{
  "resolved_agent": "cw:architect",
  "is_fallback": true,
  "original_request": "omc:architect",
  "warning": "OMC not available, using CAW fallback",
  "capability_diff": [
    "Less specialized prompt",
    "No parallel execution hints"
  ]
}
```

## Related Documentation

- [Agent Registry](./agent-registry.md) - Complete agent catalog
- [Model Routing](./model-routing.md) - Tier selection logic
- [Parallel Execution](./parallel-execution.md) - Background task management
