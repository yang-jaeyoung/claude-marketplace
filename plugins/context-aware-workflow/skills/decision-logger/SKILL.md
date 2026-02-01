---
name: decision-logger
description: Captures architectural and technical decisions in ADR format
allowed-tools: Read, Write, Glob
---

# Decision Logger

Records technical decisions in Architecture Decision Record (ADR) format.

## Triggers

1. AskUserQuestion response contains decision ("chose X", "use Y")
2. Architecture choice discussion
3. Trade-off discussion completed
4. Explicit request ("Record this decision")

## Detection Patterns

| Pattern | Example |
|---------|---------|
| Choice | "chose X over Y", "decided to use X" |
| Comparison | "X instead of Y because..." |
| Rationale | "because", "due to", "the reason is" |
| Final | "concluded", "final choice" |

## Workflow

1. **Detect**: Keywords in conversation (decided, chose, selected)
2. **Generate ID**: Sequential ADR-{NNN}
3. **Extract**: title, context, options, decision, rationale, consequences
4. **Write**: `.caw/decisions/ADR-{NNN}-{slug}.md`
5. **Update Index**: Append to `.caw/decisions/index.md`
6. **Confirm**: `📋 ADR saved: ADR-{NNN} - {Title}`

## ADR Template

```markdown
# ADR-{NNN}: {Title}

| Field | Value |
|-------|-------|
| **ID** | ADR-{NNN} |
| **Date** | YYYY-MM-DD |
| **Status** | Proposed | Accepted | Deprecated | Superseded |

## Context
[What prompted this decision?]

## Options Considered
### Option A
- Pros: ... | Cons: ...

### Option B
- Pros: ... | Cons: ...

## Decision
[The chosen option]

## Rationale
[Why this was chosen]

## Consequences
Positive: [...] | Negative: [...]
```

## Directory Structure

```
.caw/decisions/
├── index.md
├── ADR-001-jwt-over-session.md
└── ADR-002-postgres-database.md
```

## Status Values

| Status | Meaning |
|--------|---------|
| Proposed | Under discussion |
| Accepted | Approved, in effect |
| Deprecated | Not recommended |
| Superseded | Replaced (link new ADR) |

## Integration

| Skill | Integration |
|-------|-------------|
| knowledge-base | Link ADRs to entries |
| insight-collector | Link related insights |
| review-assistant | Generate compliance checklist |

## Boundaries

**Will:** Create ADR immediately, manage IDs, maintain links, track status
**Won't:** Make decisions (only record), modify without confirmation, auto-delete
