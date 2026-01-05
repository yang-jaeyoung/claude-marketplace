# Review Checklist Template

Use this template when generating context-aware review checklists.

---

```markdown
## Context-Aware Review Checklist

**Scope**: [Files or directories being reviewed]
**Generated**: YYYY-MM-DD HH:MM
**Phase**: [Current workflow phase, if applicable]
**Context Sources**: patterns, decisions, insights, knowledge

---

### 🔴 Critical Checks

These items must pass before approval.

#### Security
- [ ] Input validation present for all user inputs
- [ ] Authentication/authorization checks where required
- [ ] No sensitive data in logs or error messages
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)

#### ADR Compliance
- [ ] **[ADR-XXX](../decisions/ADR-XXX.md)**: [Requirement to verify]
- [ ] **[ADR-YYY](../decisions/ADR-YYY.md)**: [Requirement to verify]

---

### 🟠 Important Checks

These items should pass, explain if skipped.

#### Code Quality (from patterns)

**Naming Conventions**
- [ ] Functions use {detected_convention}
- [ ] Classes/Components use {detected_convention}
- [ ] Constants use {detected_convention}
- [ ] Files follow {detected_convention}

**Code Structure**
- [ ] Single responsibility principle followed
- [ ] Appropriate abstraction level
- [ ] No unnecessary complexity
- [ ] Clear and readable logic

**Error Handling**
- [ ] Errors handled appropriately
- [ ] Error pattern matches project standard: {pattern}
- [ ] Meaningful error messages
- [ ] Proper error propagation

#### Architecture
- [ ] Module boundaries respected
- [ ] Dependency direction correct
- [ ] No circular dependencies
- [ ] Consistent with project structure

#### Testing
- [ ] New code has corresponding tests
- [ ] Test coverage adequate for changes
- [ ] Edge cases covered
- [ ] Error paths tested
- [ ] Test structure follows {pattern} pattern

---

### 🟡 Recommended Checks

Nice to have, not blocking.

#### Documentation
- [ ] Public APIs documented
- [ ] Complex logic has comments
- [ ] README updated if needed

#### Performance
- [ ] No obvious performance issues
- [ ] Efficient algorithms used
- [ ] No unnecessary operations in loops

#### Maintainability
- [ ] Code is self-documenting
- [ ] No magic numbers/strings
- [ ] DRY principle followed

---

### 🔵 Domain-Specific (from knowledge-base)

Project-specific rules and constraints.

#### Business Rules
- [ ] **[Rule Name]**: [What to verify]
- [ ] **[Rule Name]**: [What to verify]

#### Integration Requirements
- [ ] **[Service Name]**: [What to verify]

---

### 💡 Related Insights

Previous learnings relevant to this review.

| Insight | Relevance | Link |
|---------|-----------|------|
| [Title] | High/Medium/Low | [Link](../insights/...) |
| [Title] | High/Medium/Low | [Link](../insights/...) |

---

### ⚠️ Known Gotchas

Watch out for these known issues.

| Gotcha | Risk | Applies To |
|--------|------|------------|
| [Issue description] | High/Medium/Low | [File/Pattern] |
| [Issue description] | High/Medium/Low | [File/Pattern] |

---

### 📊 Review Summary

After completing the review:

| Category | Status | Issues Found |
|----------|--------|--------------|
| Security | ✅/⚠️/❌ | N |
| ADR Compliance | ✅/⚠️/❌ | N |
| Code Quality | ✅/⚠️/❌ | N |
| Testing | ✅/⚠️/❌ | N |
| Domain Rules | ✅/⚠️/❌ | N |

**Overall**: ✅ Approved / ⚠️ Approved with notes / ❌ Changes requested

---

### 📝 Review Notes

[Space for reviewer to add notes]

---

### ✅ Action Items

| Priority | Item | File | Line |
|----------|------|------|------|
| 🔴 High | [Description] | [file.ts] | [line] |
| 🟠 Medium | [Description] | [file.ts] | [line] |
| 🟡 Low | [Description] | [file.ts] | [line] |
```

---

## Section Customization Guide

### When to Include Each Section

| Section | Include When |
|---------|--------------|
| Security | Always |
| ADR Compliance | ADRs exist and relate to scope |
| Code Quality | Patterns analyzed |
| Architecture | Multiple files/modules changed |
| Testing | Source code changed |
| Documentation | Public API changed |
| Domain Rules | Domain knowledge exists |
| Insights | Related insights found |
| Gotchas | Known issues apply |

### Priority Assignment

| Priority | Criteria |
|----------|----------|
| 🔴 Critical | Security issues, ADR violations, breaking changes |
| 🟠 Important | Pattern violations, missing tests, quality issues |
| 🟡 Recommended | Style issues, documentation, minor improvements |
| 🔵 Info | FYI items, suggestions, nice-to-haves |

### Context Source Indicators

Add source indicators to help reviewers understand where checks come from:

```markdown
- [ ] Functions use camelCase *(pattern)*
- [ ] JWT uses RS256 *(ADR-001)*
- [ ] Watch for Date.now() in tests *(insight)*
- [ ] Orders $100+ get free shipping *(knowledge)*
```

---

## Minimal Checklist (No Context Sources)

When no project-specific data is available:

```markdown
## Basic Review Checklist

**Scope**: [Files being reviewed]
**Note**: No project-specific patterns/decisions found. Using standard checks.

### Code Quality
- [ ] Code is readable and well-organized
- [ ] Naming is clear and consistent
- [ ] No obvious bugs or logic errors
- [ ] Error handling is appropriate

### Security
- [ ] Input validation present
- [ ] No sensitive data exposed
- [ ] Authentication/authorization correct

### Testing
- [ ] Tests exist for new code
- [ ] Tests are meaningful and passing

### General
- [ ] No breaking changes without notice
- [ ] Documentation updated if needed
```
