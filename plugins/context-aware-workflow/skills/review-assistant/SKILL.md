---
name: review-assistant
description: Generates context-aware review checklists based on learned patterns, recorded decisions, and collected insights
allowed-tools: Read, Glob, Grep
---

# Review Assistant

Generates customized review checklists reflecting project patterns/decisions/insights.

## Triggers

1. `/cw:review` execution
2. Phase completion review
3. Pre-merge review
4. Specific file/area review ("Review the auth module")

## Dependencies

| Skill | Usage | Required |
|-------|-------|----------|
| pattern-learner | Code pattern compliance | Yes |
| decision-logger | ADR compliance | Yes |
| insight-collector | Related insights | No |
| knowledge-base | Domain rules | No |

## Workflow

### 1. Identify Scope
- Command: `/cw:review`, `/cw:review src/auth/`, `/cw:review --phase 2`
- Git: Changed/staged files
- Task plan: Files in current phase

### 2. Gather Context

| Source | Location | Extract |
|--------|----------|---------|
| Patterns | `.caw/patterns/patterns.md` | Naming, architecture, error handling |
| Decisions | `.caw/decisions/*.md` | ADR requirements, deprecated patterns |
| Insights | `.caw/insights/*.md` | Gotchas, warnings, best practices |
| Knowledge | `.caw/knowledge/` | Domain rules, constraints |

### 3. Generate Checklist

```markdown
## Context-Aware Review Checklist
**Scope**: src/auth/*.ts | **Phase**: Phase 2

### Code Quality (from patterns)
- [ ] Functions use camelCase | Error handling follows Result<T,E>

### Architecture (ADR-001)
- [ ] JWT RS256 used | Token expiry = 1h | Refresh token secure

### Testing
- [ ] New code tested | Edge cases | Error paths

### Security
- [ ] Input validation | Auth checks | Sensitive data handling

### Related Insights
| Insight | Note |
|---------|------|
| JWT Refresh | Refresh 5 min before expiry |
```

### 4. Filter by Relevance

| Priority | Items | Examples |
|----------|-------|----------|
| 🔴 Critical | Must check | Security, ADR compliance |
| 🟠 Important | Should check | Pattern compliance, tests |
| 🟡 Recommended | Nice to check | Style, documentation |
| 🔵 Info | FYI | Related insights |

## Dynamic Rules

```yaml
file_type_rules:
  "*.tsx": Component naming, Props interface, Key prop
  "*.test.ts": AAA structure, No async void, Cleanup
  "*.service.ts": Error handling, Logging, Transactions

module_rules:
  "src/auth/*": Security, Token handling, Session
  "src/api/*": Input validation, Response format, Errors
```

## Fallbacks

| Missing | Action |
|---------|--------|
| No patterns | Use standard checklist |
| No decisions | Skip ADR section |
| No insights | Skip insights section |
| No knowledge | Skip domain section |

## Integration

1. `/cw:review` called
2. review-assistant generates checklist
3. Reviewer Agent reviews based on checklist
4. Feedback provided per item

## Boundaries

**Will:** Generate context-based checklist, integrate patterns/decisions/insights, filter by scope
**Won't:** Perform actual review (Reviewer role), modify code, decide approval
