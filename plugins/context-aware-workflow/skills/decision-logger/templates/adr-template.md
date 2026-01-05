# ADR Template

Use this template when creating new Architecture Decision Records.

---

```markdown
# ADR-{NNN}: {Title}

## Metadata

| Field | Value |
|-------|-------|
| **ID** | ADR-{NNN} |
| **Date** | YYYY-MM-DD |
| **Status** | Proposed / Accepted / Deprecated / Superseded |
| **Context** | [Workflow phase/step or general context] |
| **Deciders** | [Who made this decision] |

## Context

[Describe the issue that we're seeing that is motivating this decision or change.]

What is the problem we are trying to solve?
What constraints do we have?
What is the context in which this decision is being made?

## Options Considered

### Option A: {Name}

[Brief description of this option]

**Pros:**
- Pro 1
- Pro 2

**Cons:**
- Con 1
- Con 2

### Option B: {Name}

[Brief description of this option]

**Pros:**
- Pro 1
- Pro 2

**Cons:**
- Con 1
- Con 2

### Option C: {Name} (if applicable)

[Brief description of this option]

**Pros:**
- Pro 1

**Cons:**
- Con 1

## Decision

[State the decision that was made. Use active voice: "We will..."]

We will use {chosen option} because {brief rationale}.

## Rationale

[Explain why this option was chosen over the alternatives.]

- Key factor 1
- Key factor 2
- Key factor 3

## Consequences

### Positive

- [Expected benefit 1]
- [Expected benefit 2]
- [Expected benefit 3]

### Negative

- [Trade-off or risk 1]
- [Trade-off or risk 2]

### Neutral

- [Side effect that is neither positive nor negative]

## Implementation Notes

[Optional: Any notes about how this decision should be implemented]

- Note 1
- Note 2

## Related

- [ADR-XXX](./ADR-XXX-related-decision.md) - Related decision
- [Insight: Related insight title](./../insights/YYYYMMDD-related-insight.md)
- [External documentation or reference]

## Changelog

| Date | Change |
|------|--------|
| YYYY-MM-DD | Initial decision |
```

---

## Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| ID | Yes | Sequential identifier (ADR-001, ADR-002, etc.) |
| Date | Yes | Date when decision was made |
| Status | Yes | Current status of the decision |
| Context | Yes | Workflow phase or general context |
| Deciders | No | Who participated in the decision |
| Options | Yes | At least 2 options should be listed |
| Decision | Yes | Clear statement of what was decided |
| Rationale | Yes | Why this option was chosen |
| Consequences | Yes | Expected positive and negative impacts |
| Related | No | Links to related ADRs, insights, or docs |

## Status Transitions

```
Proposed → Accepted
Accepted → Deprecated
Accepted → Superseded (by new ADR)
Deprecated → (no further transitions)
Superseded → (no further transitions)
```

## Naming Examples

| Decision Topic | Suggested Title |
|---------------|-----------------|
| Auth method selection | JWT over Session Authentication |
| Database choice | PostgreSQL as Primary Database |
| API style | REST API Design Standards |
| State management | Redux for State Management |
| Testing approach | Jest with React Testing Library |
