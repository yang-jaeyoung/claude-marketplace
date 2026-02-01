---
name: context-helper
description: Helps agents understand and manage context efficiently with relevant files, previous outputs, and related insights
allowed-tools: Read, Glob, Grep
forked-context: true
forked-context-returns: |
  files: Prioritized file list (max 10)
  step_outputs: Previous step summary
  insights: Related insights (compressed)
  dependencies: Dependency file list
hooks:
  AgentStartStep:
    action: provide_context
    priority: 2
---

# Context Helper

Intelligent context management for efficient agent work.

## Triggers

1. Agent starts new step
2. Agent requests context
3. Context window nearing limits
4. Phase transition (summarize previous)

## Context Categories

| Category | Source | Provides |
|----------|--------|----------|
| Task | task_plan.md | Current step, pending steps, criteria |
| Code | context_manifest.json | Files to modify, dependencies, tests |
| Knowledge | insights/, decisions/ | Related insights, decisions, patterns |
| Progress | metrics.json | Previous outputs, duration, history |

## Workflow

### 1. Analyze Current Step
```yaml
extract: step_id, description, phase_context, dependencies
```

### 2. Gather Context
```yaml
required: task_plan.md (current section), files in step
dependencies: outputs from dependent steps
related: matching insights, decisions, patterns
```

### 3. Prioritize
```yaml
scoring:
  direct_reference: 1.0
  dependency_output: 0.8
  same_directory: 0.6
  pattern_match: 0.4
  insight_related: 0.3

budget:
  high_priority: 70%
  medium_priority: 20%
  low_priority: 10%
```

### 4. Present
```markdown
## 📋 Context for Step 2.3

### Required Files
| Priority | File | Reason |
|----------|------|--------|
| 1 | src/auth/jwt.ts | Step 2.1 output |
| 2 | src/auth/types.ts | Type definitions |

### Previous Step Outputs
**Step 2.1**: Created generateToken(), verifyToken()
**Step 2.2**: Implemented validateToken() middleware

### Related Insights
💡 JWT Token Refresh Pattern (2026-01-04)
```

## User Commands

```
/cw:context                # Current step context
/cw:context --step 2.1     # Specific step
/cw:context --phase 1      # Phase summary
/cw:context --minimal      # Compact view
```

## Context Manifest (`.caw/context_manifest.json`)

```json
{
  "current_step": "2.3",
  "context_priority": {
    "critical": ["src/auth/jwt.ts"],
    "important": ["src/auth/types.ts"],
    "reference": ["tests/auth/jwt.test.ts"]
  },
  "step_outputs": {
    "2.1": { "summary": "JWT utilities implemented" }
  }
}
```

## Memory Optimization

```yaml
pruning:
  completed_steps: summarize_only
  large_files: extract_relevant_sections
  old_context: >24h → archive
  similar_content: deduplicate

loading:
  initial: task_plan, manifest, current step files
  on_demand: previous outputs, insights
  never_auto: archived, old insights, unrelated
```

## Integration

| Agent | Context Provided |
|-------|------------------|
| Builder | Files to modify, test patterns |
| Reviewer | Changed files, original state |
| Planner | Structure, patterns |
| Architect | System overview, dependencies |

## Boundaries

**Will:** Prioritize relevant context, summarize phases, link insights, optimize for limits
**Won't:** Read without scoring, include full files, override agent decisions, store permanently
