---
name: decision-logger
description: Captures architectural and technical decisions in ADR format. Invoked when AskUserQuestion responses contain decisions or architecture choices are made. Use to document technology selections, design patterns, or trade-off decisions.
allowed-tools: Read, Write, Glob
---

# Decision Logger

Captures and documents architectural and technical decisions in Architecture Decision Record (ADR) format.

## Core Principle

**Decision = Record Immediately**

Record technical decisions in ADR format immediately when made. Answer "why did we do it this way?" later.

## Triggers

This Skill activates in the following situations:

1. **AskUserQuestion response contains decision**
   - "I'll choose X", "Let's go with Y"
   - "Use B instead of A"

2. **Architecture choice discussion**
   - Technology stack selection
   - Design pattern decisions
   - Library/framework selection

3. **Trade-off discussion completed**
   - Conclusion after pros/cons comparison
   - Final choice after reviewing alternatives

4. **Explicit request**
   - "Record this decision"
   - "Log as ADR"

## Decision Detection Patterns

| Pattern | Example |
|---------|---------|
| Choice expression | "chose X over Y", "decided to use X" |
| Comparison conclusion | "X instead of Y because..." |
| Rationale provided | "because", "due to", "the reason is" |
| Trade-off | "trade-off", "pros/cons" |
| Final decision | "concluded", "final choice" |

## Behavior

### Step 1: Detect Decision

Detect decision patterns in conversation:

```yaml
detection:
  keywords:
    - "decided", "chose", "selected", "will use"
  context:
    - Technology comparison
    - Architecture discussion
    - Library selection
    - Pattern choice
```

### Step 2: Generate ADR ID

Generate sequential ID:

```yaml
id_format: ADR-{NNN}
examples:
  - ADR-001
  - ADR-002
  - ADR-015

process:
  1. Read .caw/decisions/ directory
  2. Find highest existing ADR number
  3. Increment by 1
  4. If no existing ADRs, start with 001
```

### Step 3: Extract Components

Extract key elements from decision:

```yaml
components:
  title: Short description of the decision
  context: What prompted this decision
  options: Alternatives that were considered
  decision: The chosen option
  rationale: Why this was chosen
  consequences: Expected impacts (positive/negative)
```

### Step 4: Write ADR File

Save to `.caw/decisions/`:

```yaml
action: Write tool
path: .caw/decisions/ADR-{NNN}-{slug}.md
content: See ADR Template below
```

### Step 5: Update Index

Update index file (if exists):

```yaml
action: Append to .caw/decisions/index.md
content: |
  | ADR-{NNN} | [Title] | [Status] | [Date] |
```

### Step 6: Confirm

Confirm save completion:

```
📋 ADR saved: ADR-{NNN} - {Title}
```

## ADR Template

See [templates/adr-template.md](templates/adr-template.md) for the full template.

```markdown
# ADR-{NNN}: {Title}

## Metadata
| Field | Value |
|-------|-------|
| **ID** | ADR-{NNN} |
| **Date** | YYYY-MM-DD |
| **Status** | Proposed / Accepted / Deprecated / Superseded |
| **Context** | [Related workflow phase/step if applicable] |

## Context
[What is the issue that we're seeing that is motivating this decision?]

## Options Considered
### Option A: [Name]
- **Pros**: ...
- **Cons**: ...

### Option B: [Name]
- **Pros**: ...
- **Cons**: ...

## Decision
[What is the change that we're proposing and/or doing?]

## Rationale
[Why was this option chosen over others?]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

## Related
- [Links to related ADRs, insights, or documentation]
```

## File Naming Convention

**Pattern**: `ADR-{NNN}-{slug}.md`

- NNN: 3-digit sequential number (001, 002, ...)
- slug: 3-5 words from title, kebab-case

**Examples**:
- `ADR-001-jwt-over-session-auth.md`
- `ADR-002-postgres-database-selection.md`
- `ADR-003-rest-api-design.md`

## Directory Structure

```
.caw/
└── decisions/
    ├── index.md                        # Master ADR index
    ├── ADR-001-jwt-over-session.md
    ├── ADR-002-postgres-database.md
    └── ADR-003-rest-api-design.md
```

## ADR Status Values

| Status | Meaning |
|--------|---------|
| **Proposed** | Under discussion, not yet accepted |
| **Accepted** | Approved and in effect |
| **Deprecated** | No longer recommended, but not replaced |
| **Superseded** | Replaced by another ADR (link to new one) |

## Index File Format

```markdown
# Architecture Decision Records

| ID | Title | Status | Date |
|----|-------|--------|------|
| [ADR-001](ADR-001-jwt-over-session.md) | JWT over Session Auth | Accepted | 2026-01-04 |
| [ADR-002](ADR-002-postgres-database.md) | PostgreSQL Selection | Accepted | 2026-01-04 |
```

## Example Flow

```
1. User: "Should we use JWT or Session for authentication?"

2. Model: Present pros/cons comparison
   - JWT: Stateless, good scalability, larger token size
   - Session: Requires server management, instant invalidation possible

3. User: "I'll use JWT. Scalability is important."

4. Model: Detect decision → Create ADR
   → Save .caw/decisions/ADR-001-jwt-authentication.md

5. Model: Confirmation message
   📋 ADR saved: ADR-001 - JWT Authentication Selection
```

## Integration with Workflow

### CAW Workflow Active

When workflow is active, include Phase/Step info in metadata:

```markdown
## Metadata
| Field | Value |
|-------|-------|
| **ID** | ADR-001 |
| **Date** | 2026-01-04 |
| **Status** | Accepted |
| **Context** | Phase 1: Architecture Design, Step 1.2 |
```

### Without Workflow

ADRs can be saved during general conversation:

```markdown
## Metadata
| Field | Value |
|-------|-------|
| **ID** | ADR-001 |
| **Date** | 2026-01-04 |
| **Status** | Accepted |
| **Context** | General Discussion - Tech Stack Selection |
```

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| knowledge-base | Link ADRs to knowledge entries |
| insight-collector | Link related insights |
| review-assistant | Generate decision compliance checklist |

## Superseding ADRs

When replacing existing decisions:

1. Change existing ADR status to `Superseded`
2. Specify replacement reason in new ADR
3. Add bidirectional links

```markdown
# ADR-001: JWT Authentication (SUPERSEDED)

**Status**: Superseded by [ADR-005](ADR-005-oauth2-migration.md)
```

## Boundaries

**Will:**
- Create ADR immediately when decision occurs
- Manage sequential IDs
- Maintain links between related ADRs
- Track status changes

**Will Not:**
- Make decisions (only record)
- Modify existing ADRs without user confirmation
- Auto-delete or expire ADRs
