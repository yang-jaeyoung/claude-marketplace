# Plan File Patterns

Pattern definitions for recognizing plan files created in Plan Mode.

## Recognized Plan Structures

### Implementation Steps Pattern

Patterns that indicate implementation steps:

```markdown
# Heading Patterns
- "## Implementation" or "## 구현"
- "## Implementation Steps" or "## 구현 단계"
- "### Phase N:" or "### 단계 N:"

# Numbering Patterns
- Numbered: 1., 2., 3. or 1) 2) 3)
- Checkbox: - [ ] or - [x]
- Step format: "Step X.Y" or "단계 X.Y"
```

### File Change Pattern

Patterns that indicate file changes:

```markdown
# Action Keywords
- "Create:" or "생성:"
- "Modify:" or "수정:"
- "Delete:" or "삭제:"
- "Update:" or "업데이트:"

# File Indicators
- File paths with extensions (*.ts, *.js, *.py, etc.)
- Directory structure diagrams (├── └──)
- Inline code paths: `src/auth/jwt.ts`
```

### Phase/Step Pattern

Patterns that indicate Phase and Step structure:

```markdown
# Phase Patterns
- "Phase 1:" or "Phase 1 -"
- "단계 1:" or "1단계:"
- "### Phase N: [Title]"

# Step Patterns
- "Step 1.1" or "Step 1.1:"
- "1.1.", "1.2.", "1.3."
- "- Step: [description]"
```

## Example Valid Plans

### Minimal Valid Plan

```markdown
# Feature: [Title]

## Implementation Steps
1. First step
2. Second step
3. Third step

## Files
- src/feature/index.ts
```

### Full Valid Plan

```markdown
# Feature: User Authentication

## Overview
JWT-based authentication system implementation.

## Implementation Steps

### Phase 1: Setup
1. Create auth directory structure
2. Install dependencies (jsonwebtoken, bcrypt)

### Phase 2: Core Implementation
1. Implement JWT utilities
2. Create auth middleware
3. Add login endpoint

### Phase 3: Testing
1. Add unit tests
2. Add integration tests

## Files to Create
- src/auth/jwt.ts
- src/auth/middleware.ts
- src/routes/auth.ts
- tests/auth/jwt.test.ts

## Files to Modify
- src/routes/index.ts
- package.json

## Technical Decisions
- JWT for stateless authentication
- RS256 algorithm for token signing
```

## Invalid Plan Indicators

Plans that are not suitable for CAW workflow:

```markdown
# Missing Elements
- No implementation steps or phases
- No file changes specified
- Only high-level descriptions without actionable items

# Too Vague
- "Implement the feature"
- "Fix the bug"
- No specific deliverables

# Research/Investigation Plans
- "Investigate options for..."
- "Research best practices..."
- No concrete implementation path
```

## Pattern Matching Priority

Pattern matching priority order:

| Priority | Pattern Type | Weight |
|----------|-------------|--------|
| 1 | Phase/Step structure | High |
| 2 | File change list | High |
| 3 | Implementation heading | Medium |
| 4 | Numbered steps | Medium |
| 5 | Checkbox items | Low |

## Localization Support

Supported languages:

| English | Korean |
|---------|--------|
| Implementation | 구현 |
| Phase | 단계, Phase |
| Step | 스텝, Step |
| Create | 생성 |
| Modify | 수정 |
| Delete | 삭제 |
| Files | 파일 |
