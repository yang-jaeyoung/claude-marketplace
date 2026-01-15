# Domain Knowledge Template

Template for `domain_knowledge` Serena memory.

## Structure

```markdown
# Domain Knowledge

## Metadata
- **Last Updated**: YYYY-MM-DDTHH:MM:SSZ
- **Contributors**: Planner, Builder
- **Version**: 1.0

## Business Rules

### [Category 1]

1. **[Rule Name]**
   - Description: [What this rule means]
   - Enforcement: [How/where it's enforced]
   - Example: [Code example if applicable]

2. **[Rule Name]**
   - Description: [...]

### [Category 2]
...

## Patterns

### Architecture Patterns

| Pattern | Usage | Location |
|---------|-------|----------|
| Repository | Data access abstraction | `src/repositories/` |
| Factory | Object creation | `src/factories/` |
| Observer | Event handling | `src/events/` |

### Code Patterns

#### [Pattern Name]
```[language]
// Example code showing the pattern
```
**When to use**: [Guidance]

## Constraints

### Technical Constraints
- [Constraint]: [Reason]
- [Constraint]: [Reason]

### Business Constraints
- [Constraint]: [Reason]

## Architecture Decisions

### ADR-001: [Decision Title]
- **Status**: Accepted
- **Context**: [Why this decision was needed]
- **Decision**: [What was decided]
- **Consequences**: [Impact of this decision]

## API Conventions

### Request/Response Format
- [Convention 1]
- [Convention 2]

### Error Handling
- [Pattern description]

## Data Models

### Core Entities
| Entity | Location | Purpose |
|--------|----------|---------|
| User | `src/models/user.ts` | User representation |

## Integration Points

### External Services
| Service | Purpose | Config |
|---------|---------|--------|
| [Service] | [Purpose] | `.env.SERVICE_URL` |
```

## Usage

**Save (Planner/Builder)**:
```
write_memory("domain_knowledge", content)
```

**Load (Any Agent)**:
```
read_memory("domain_knowledge")
```

## When to Update

- New business rule discovered
- Architecture decision made
- New pattern established
- Integration added
