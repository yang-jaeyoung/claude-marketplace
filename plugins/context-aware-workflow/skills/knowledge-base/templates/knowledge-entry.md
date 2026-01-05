# Knowledge Entry Template

Use this template when creating new knowledge base entries.

---

```markdown
# {Title}

## Metadata

| Field | Value |
|-------|-------|
| **ID** | kb-{NNN} |
| **Category** | {primary} > {subcategory} |
| **Created** | YYYY-MM-DD |
| **Updated** | YYYY-MM-DD |
| **Status** | Active / Outdated / Archived |
| **Sources** | insight / decision / code / conversation |
| **Confidence** | High / Medium / Low |

## Summary

[1-2 sentence summary of this knowledge entry. Should be scannable and immediately useful.]

## Content

[Detailed knowledge content. Include:]

- Key facts and rules
- Implementation details (if technical)
- Constraints and limitations
- Examples where helpful

### Details

[Expand on the summary with specifics]

### Examples

```
[Code or usage examples if applicable]
```

### Exceptions

- [Any exceptions to the rule]
- [Edge cases to be aware of]

## Context

[When does this knowledge apply?]

| Situation | Applicability |
|-----------|---------------|
| New development | Always |
| Bug fixes | Sometimes |
| Refactoring | Sometimes |

## Related

### ADRs
- [ADR-XXX: Related decision](../decisions/ADR-XXX.md)

### Insights
- [Related insight](../insights/YYYYMMDD-related.md)

### Other Knowledge
- [Related entry](./other-entry.md)

### External
- [Documentation link](https://example.com/docs)

## Keywords

#keyword1 #keyword2 #keyword3 #keyword4

## Changelog

| Date | Change | By |
|------|--------|-----|
| YYYY-MM-DD | Created | Agent/User |
| YYYY-MM-DD | Updated X | Agent/User |
```

---

## Category Guidelines

### domain/
Business rules, domain logic, policies

**Good examples:**
- Order processing rules
- Pricing calculations
- User role permissions
- Validation rules

**Template additions:**
```markdown
## Business Rule

**Rule**: [Clear statement of the rule]
**Trigger**: [When does this rule apply?]
**Result**: [What happens when triggered?]

## Stakeholder

**Owner**: [Department/Team]
**Source**: [Where this rule comes from]
```

### technical/
Implementation details, configuration, architecture

**Good examples:**
- API integration details
- Database schema decisions
- Caching strategies
- Performance considerations

**Template additions:**
```markdown
## Technical Specification

**Component**: [Which part of the system]
**Purpose**: [Why this exists]

## Configuration

| Setting | Value | Environment |
|---------|-------|-------------|
| KEY | value | production |

## Code Reference

- File: `src/path/to/file.ts`
- Function: `functionName()`
```

### conventions/
Project standards, coding rules, team agreements

**Good examples:**
- Naming conventions
- API response formats
- Git workflow
- Code review standards

**Template additions:**
```markdown
## Convention

**Standard**: [The convention]
**Rationale**: [Why we do it this way]

## Do

- [Good example 1]
- [Good example 2]

## Don't

- [Bad example 1]
- [Bad example 2]
```

### gotchas/
Known issues, pitfalls, non-obvious behaviors

**Good examples:**
- Known bugs
- Counter-intuitive behaviors
- Common mistakes
- Testing gotchas

**Template additions:**
```markdown
## The Gotcha

**Problem**: [What goes wrong]
**Cause**: [Why it happens]
**Impact**: [What breaks]

## Solution

[How to avoid or fix]

## Detection

[How to know if you've hit this issue]
```

### integrations/
External service details, API information

**Good examples:**
- Third-party API details
- Webhook configurations
- Authentication flows
- Rate limits

**Template additions:**
```markdown
## Service

**Provider**: [Company/Service name]
**Purpose**: [What we use it for]
**Environment**: Production / Staging / Development

## Authentication

**Method**: API Key / OAuth / JWT
**Credential Location**: [Where stored - NOT the actual value]

## Endpoints

| Purpose | Endpoint | Method |
|---------|----------|--------|
| Get user | /api/users/:id | GET |

## Rate Limits

| Tier | Limit |
|------|-------|
| Production | 100 req/min |

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 429 | Rate limited | Retry with backoff |
```

---

## Best Practices

1. **Be specific** - Vague knowledge isn't useful
2. **Include examples** - Show, don't just tell
3. **Link related items** - Build the knowledge graph
4. **Use keywords** - Enable effective search
5. **Note confidence** - Indicate certainty level
6. **Keep updated** - Mark outdated entries
7. **Source attribution** - Where did this come from?
