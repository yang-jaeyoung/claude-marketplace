---
name: review-assistant
description: Generates context-aware review checklists based on learned patterns, recorded decisions, and collected insights. Enhances the Reviewer agent with project-specific checks. Invoked during /caw:review or code review requests.
allowed-tools: Read, Glob, Grep
---

# Review Assistant

Generates context-aware review checklists by aggregating patterns, decisions, and insights.

## Core Principle

**맥락 있는 리뷰 = 효과적인 리뷰**

일반적인 체크리스트가 아닌, 프로젝트의 패턴/결정/인사이트를 반영한 맞춤형 체크리스트를 생성합니다.

## Triggers

이 Skill은 다음 상황에서 활성화됩니다:

1. **/caw:review 실행**
   - Reviewer Agent와 함께 활성화
   - 컨텍스트 기반 체크리스트 생성

2. **Phase 완료 리뷰**
   - Phase 전환 전 리뷰 시
   - 해당 Phase 관련 체크 항목

3. **Pre-merge 리뷰**
   - PR 생성 전 리뷰
   - 전체적인 품질 체크

4. **특정 파일/영역 리뷰**
   - "auth 모듈 리뷰해줘"
   - 해당 영역 관련 체크리스트

## Dependencies

이 Skill은 다른 Skills의 데이터를 활용합니다:

| Skill | Usage | Required |
|-------|-------|----------|
| **pattern-learner** | 코드 패턴 준수 확인 | Yes |
| **decision-logger** | ADR 준수 확인 | Yes |
| **insight-collector** | 관련 인사이트 참조 | No |
| **knowledge-base** | 도메인 규칙 확인 | No |

## Behavior

### Step 1: Identify Review Scope

리뷰 대상 파악:

```yaml
scope_detection:
  from_command:
    "/caw:review": All files in current phase
    "/caw:review src/auth/": Specific directory
    "/caw:review --phase 2": Specific phase

  from_git:
    - Changed files (git diff)
    - Staged files (git diff --staged)

  from_task_plan:
    - Files mentioned in completed steps
    - Files in current phase context
```

### Step 2: Gather Context

각 데이터 소스에서 관련 정보 수집:

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

수집된 컨텍스트로 체크리스트 생성:

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

변경 사항에 맞게 필터링:

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
1. 사용자: "/caw:review"

2. review-assistant 활성화
   Scope: src/auth/*.ts (Phase 2 파일)

3. 컨텍스트 수집:
   - patterns.md: TypeScript 패턴
   - ADR-001: JWT Authentication
   - insight-20260104-jwt-refresh: 토큰 갱신 타이밍

4. 체크리스트 생성:

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
   | JWT Refresh Timing | 만료 5분 전 갱신 권장 |

5. Reviewer Agent에 전달
```

## Integration with Reviewer Agent

```yaml
integration:
  workflow:
    1. /caw:review 호출
    2. review-assistant가 체크리스트 생성
    3. Reviewer Agent가 체크리스트 기반 리뷰
    4. 각 항목 확인 및 피드백 제공

  handoff:
    review-assistant:
      - 체크리스트 생성
      - 컨텍스트 제공
      - 관련 링크 포함

    reviewer:
      - 실제 코드 리뷰
      - 이슈 발견
      - 피드백 작성
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

데이터 소스가 없을 때:

```yaml
fallbacks:
  no_patterns:
    message: "패턴 분석이 없습니다. 일반 체크리스트 사용"
    action: Use standard checklist

  no_decisions:
    message: "기록된 결정이 없습니다"
    action: Skip ADR section

  no_insights:
    message: "관련 인사이트 없음"
    action: Skip insights section

  no_knowledge:
    message: "도메인 지식 없음"
    action: Skip domain section
```

## Boundaries

**Will:**
- 프로젝트 컨텍스트 기반 체크리스트 생성
- 패턴/결정/인사이트 통합
- 변경 범위에 맞게 필터링
- 우선순위 제시

**Will Not:**
- 실제 코드 리뷰 수행 (Reviewer 역할)
- 코드 수정
- 리뷰 승인/거부 결정
- 체크리스트 항목 자동 체크
