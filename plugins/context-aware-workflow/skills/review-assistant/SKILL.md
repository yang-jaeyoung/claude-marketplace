---
name: review-assistant
description: Generates context-aware review checklists based on learned patterns, recorded decisions, and collected insights. Enhances the Reviewer agent with project-specific checks. Invoked during /cw:review or code review requests.
allowed-tools: Read, Glob, Grep
---

# Review Assistant

Generates context-aware review checklists by aggregating patterns, decisions, and insights.

## Core Principle

**Contextual Review = Effective Review**

Generate customized checklists reflecting project patterns/decisions/insights, not generic checklists.

## Triggers

This Skill activates in the following situations:

1. **/cw:review execution**
   - Activated with Reviewer Agent
   - Generate context-based checklist

2. **Phase completion review**
   - During review before Phase transition
   - Check items related to that Phase

3. **Pre-merge review**
   - Review before PR creation
   - Overall quality check

4. **Specific file/area review**
   - "Review the auth module"
   - Checklist related to that area

## Dependencies

This Skill utilizes data from other Skills:

| Skill | Usage | Required |
|-------|-------|----------|
| **pattern-learner** | Code pattern compliance check | Yes |
| **decision-logger** | ADR compliance check | Yes |
| **insight-collector** | Related insights reference | No |
| **knowledge-base** | Domain rule verification | No |

## Behavior

### Step 1: Identify Review Scope

Identify review scope:

```yaml
scope_detection:
  from_command:
    "/cw:review": All files in current phase
    "/cw:review src/auth/": Specific directory
    "/cw:review --phase 2": Specific phase

  from_git:
    - Changed files (git diff)
    - Staged files (git diff --staged)

  from_task_plan:
    - Files mentioned in completed steps
    - Files in current phase context
```

### Step 2: Gather Context

Collect relevant information from each data source:

```yaml
context_gathering:
  patterns:
    source: .caw/patterns/patterns.md
    extract:
      - Naming conventions for changed file types
      - Architecture patterns for affected modules
      - Error handling patterns
      - Testing patterns

  decisions:
    source: .caw/decisions/*.md
    filter:
      - ADRs related to changed components
      - Recent decisions (last 30 days)
    extract:
      - Decision requirements to verify
      - Deprecated patterns to avoid

  insights:
    source: .caw/insights/*.md
    filter:
      - Insights tagged with affected areas
      - Gotchas and warnings
    extract:
      - Known issues to watch for
      - Best practices learned

  knowledge:
    source: .caw/knowledge/
    filter:
      - Domain rules for affected features
      - Technical constraints
    extract:
      - Business rules to verify
      - Integration requirements
```

### Step 3: Generate Checklist

Generate checklist from collected context:

```yaml
checklist_structure:
  sections:
    - code_quality: From pattern-learner
    - architecture: From pattern-learner + decisions
    - decisions: From decision-logger
    - testing: From pattern-learner
    - security: Standard + knowledge-base
    - domain: From knowledge-base
    - gotchas: From insights + knowledge-base
```

### Step 4: Contextualize

Filter according to changes:

```yaml
filtering:
  relevance_check:
    - Is this check applicable to changed files?
    - Does this pattern apply to this file type?
    - Is this ADR related to changed components?

  priority:
    high: Security, breaking changes, ADR compliance
    medium: Pattern compliance, test coverage
    low: Style suggestions, documentation

  removal:
    - Checks not applicable to change scope
    - Duplicate checks
    - Outdated/superseded checks
```

### Step 5: Present Checklist

See [templates/review-checklist.md](templates/review-checklist.md) for the full format.

```markdown
## Context-Aware Review Checklist

**Scope**: [Files/directories]
**Generated**: YYYY-MM-DD HH:MM
**Phase**: [If in workflow]

---

### Code Quality (from patterns)
- [ ] Functions use camelCase naming
- [ ] Error handling follows Result<T,E> pattern
...

### Architecture Compliance
- [ ] ADR-001: JWT implementation correct
...

### Testing
- [ ] New functions have tests
...

### Security
- [ ] Input validation present
...

### Related Insights
| Insight | Relevance |
...
```

## Checklist Categories

### 1. Code Quality (from pattern-learner)

```yaml
code_quality:
  naming:
    - Functions follow {convention}
    - Classes follow {convention}
    - Files follow {convention}

  structure:
    - Single responsibility
    - Appropriate abstraction level
    - Consistent with project patterns

  style:
    - Import organization
    - Error handling pattern
    - Logging format
```

### 2. Architecture Compliance

```yaml
architecture:
  from_patterns:
    - Directory structure followed
    - Module boundaries respected
    - Dependency direction correct

  from_decisions:
    - ADR requirements met
    - Deprecated patterns avoided
    - Agreed technologies used
```

### 3. Testing

```yaml
testing:
  coverage:
    - New code has tests
    - Edge cases covered
    - Error paths tested

  quality:
    - Test structure (AAA pattern)
    - Mocking approach consistent
    - No flaky test patterns
```

### 4. Security

```yaml
security:
  standard:
    - Input validation
    - Authentication checks
    - Authorization checks
    - Sensitive data handling

  from_knowledge:
    - Project-specific security rules
    - Known vulnerability patterns
```

### 5. Domain Rules (from knowledge-base)

```yaml
domain:
  business_rules:
    - Domain logic correctly implemented
    - Edge cases handled per rules
    - Calculations accurate

  constraints:
    - Business constraints respected
    - Validation rules applied
```

### 6. Gotchas (from insights)

```yaml
gotchas:
  known_issues:
    - Known pitfalls avoided
    - Learned lessons applied

  warnings:
    - Risk areas flagged
    - Common mistakes checked
```

## Example Flow

```
1. User: "/cw:review"

2. review-assistant activated
   Scope: src/auth/*.ts (Phase 2 files)

3. Context collection:
   - patterns.md: TypeScript patterns
   - ADR-001: JWT Authentication
   - insight-20260104-jwt-refresh: Token refresh timing

4. Checklist generation:

   ## Context-Aware Review Checklist

   **Scope**: src/auth/jwt.ts, src/auth/middleware.ts
   **Phase**: Phase 2: Core Implementation

   ### Code Quality
   - [ ] Functions use camelCase (pattern)
   - [ ] Error handling uses Result<T,E> (pattern)

   ### Architecture (ADR-001)
   - [ ] JWT RS256 algorithm used
   - [ ] Token expiry set to 1 hour
   - [ ] Refresh token stored securely

   ### Testing
   - [ ] Token generation tested
   - [ ] Token validation tested
   - [ ] Expiry edge cases covered

   ### Related Insights
   | Insight | Note |
   |---------|------|
   | JWT Refresh Timing | Refresh recommended 5 min before expiry |

5. Hand off to Reviewer Agent
```

## Integration with Reviewer Agent

```yaml
integration:
  workflow:
    1. /cw:review called
    2. review-assistant generates checklist
    3. Reviewer Agent reviews based on checklist
    4. Check each item and provide feedback

  handoff:
    review-assistant:
      - Generate checklist
      - Provide context
      - Include related links

    reviewer:
      - Actual code review
      - Issue discovery
      - Feedback writing
```

## Checklist Priority Levels

| Level | Icon | Meaning | Examples |
|-------|------|---------|----------|
| **Critical** | 🔴 | Must check, blocking | Security, ADR compliance |
| **Important** | 🟠 | Should check | Pattern compliance, tests |
| **Recommended** | 🟡 | Nice to check | Style, documentation |
| **Info** | 🔵 | FYI only | Related insights |

## Dynamic Checklist Features

### File Type Specific

```yaml
file_type_rules:
  "*.tsx":
    add:
      - Component naming (PascalCase)
      - Props interface defined
      - Key prop in lists

  "*.test.ts":
    add:
      - Test structure (AAA)
      - No async void
      - Cleanup in afterEach

  "*.service.ts":
    add:
      - Error handling
      - Logging
      - Transaction handling
```

### Module Specific

```yaml
module_rules:
  "src/auth/*":
    add:
      - Security checks
      - Token handling
      - Session management

  "src/api/*":
    add:
      - Input validation
      - Response format
      - Error responses
```

## Fallback Behavior

When data sources are missing:

```yaml
fallbacks:
  no_patterns:
    message: "No pattern analysis. Using standard checklist"
    action: Use standard checklist

  no_decisions:
    message: "No recorded decisions"
    action: Skip ADR section

  no_insights:
    message: "No related insights"
    action: Skip insights section

  no_knowledge:
    message: "No domain knowledge"
    action: Skip domain section
```

## Boundaries

**Will:**
- Generate project context-based checklist
- Integrate patterns/decisions/insights
- Filter according to change scope
- Present priorities

**Will Not:**
- Perform actual code review (Reviewer role)
- Modify code
- Decide review approval/rejection
- Auto-check checklist items
