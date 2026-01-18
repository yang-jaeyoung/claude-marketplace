---
name: pattern-learner
description: Analyzes codebase to learn project-specific patterns including code style, architecture conventions, and testing approaches. Invoked during /cw:start or when agents need pattern information for consistency.
allowed-tools: Read, Glob, Grep, Bash
---

# Pattern Learner

Analyzes codebase to learn and document project-specific coding patterns for consistency enforcement.

## Core Principle

**패턴 학습 = 일관성 보장**

프로젝트의 기존 코드를 분석하여 패턴을 학습하고, 새 코드가 동일한 규칙을 따르도록 합니다.

## Triggers

이 Skill은 다음 상황에서 활성화됩니다:

1. **/cw:start 실행**
   - 워크플로우 시작 시 자동 분석
   - 프로젝트 패턴 초기 학습

2. **Agent 요청**
   - "이 프로젝트의 패턴은?"
   - "기존 코드 스타일 확인"

3. **패턴 갱신 요청**
   - "패턴 다시 분석해줘"
   - 새로운 파일 유형 발견 시

4. **새 파일 생성 전**
   - Builder가 파일 생성 전 패턴 확인

## Pattern Categories

| Category | What to Learn | Examples |
|----------|---------------|----------|
| **Naming** | 명명 규칙 | camelCase functions, PascalCase classes |
| **Architecture** | 디렉토리 구조, 모듈화 | Clean Architecture, Feature-based |
| **Error Handling** | 에러 처리 패턴 | Result<T,E>, try-catch style |
| **Testing** | 테스트 구조, 명명 | AAA pattern, *.test.ts |
| **Imports** | import 정리 방식 | Grouped, path aliases |
| **Documentation** | 주석 스타일 | JSDoc, docstrings |

## Behavior

### Step 1: File Discovery

분석 대상 파일 탐색:

```yaml
discovery:
  config_files:
    primary:
      - package.json
      - tsconfig.json
      - pyproject.toml
      - go.mod
    linting:
      - .eslintrc*
      - .prettierrc*
      - ruff.toml
      - .golangci.yml
    testing:
      - jest.config.*
      - pytest.ini
      - vitest.config.*

  source_files:
    patterns:
      - "src/**/*.{ts,tsx,js,jsx}"
      - "lib/**/*.py"
      - "**/*.go"
    sample_size: 5-10 files per type
    priority: Recently modified first

  test_files:
    patterns:
      - "tests/**/*"
      - "**/__tests__/**/*"
      - "**/*.test.*"
      - "**/*_test.*"
```

### Step 2: Pattern Analysis

각 카테고리별 패턴 추출:

```yaml
analysis:
  naming:
    functions: Extract function naming pattern
    classes: Extract class/component naming
    constants: Extract constant naming
    files: Extract file naming convention

  architecture:
    directories: Analyze directory structure
    modules: Identify module boundaries
    exports: Check export patterns (barrel, named)

  error_handling:
    patterns: try-catch, Result type, Error classes
    logging: Logger usage patterns
    propagation: Error propagation style

  testing:
    location: Test file locations
    naming: Test file naming
    structure: Test case structure (AAA, BDD)
    mocking: Mocking approach

  imports:
    ordering: External vs internal vs relative
    aliases: Path alias usage (@/, ~/)
    grouping: Import grouping style
```

### Step 3: Generate Documentation

패턴을 문서화:

```yaml
action: Write tool
path: .caw/patterns/patterns.md
content: See Pattern Template below
```

### Step 4: Cache for Performance

분석 결과 캐싱:

```yaml
cache:
  path: .caw/patterns/.pattern-cache.json
  content:
    analyzed_at: timestamp
    file_hashes: {file: hash}
    patterns: {extracted patterns}
  invalidation:
    - Config file changes
    - Significant source changes
    - Manual refresh request
```

### Step 5: Confirm

분석 완료 확인:

```
📊 Patterns analyzed: {N} files scanned
   - Naming: {convention}
   - Architecture: {pattern}
   - Testing: {framework}
```

## Pattern Template

See [templates/patterns-template.md](templates/patterns-template.md) for the full template.

```markdown
# Project Patterns

## Metadata
| Field | Value |
|-------|-------|
| **Analyzed** | YYYY-MM-DD HH:MM |
| **Files Scanned** | N files |
| **Language** | TypeScript / Python / Go |
| **Framework** | React / FastAPI / Gin |

## Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Functions | camelCase | `getUserById()` |
| Classes | PascalCase | `UserService` |
| Constants | UPPER_SNAKE | `MAX_RETRY` |
| Files | kebab-case | `user-service.ts` |

## Architecture Patterns

### Directory Structure
[Detected structure]

### Module Pattern
[Export/import patterns]

## Error Handling

### Pattern
[Detected error handling pattern]

## Testing Patterns

### Structure
[Test organization]

### Naming
[Test naming convention]
```

## File Output Structure

```
.caw/
└── patterns/
    ├── patterns.md              # Main patterns document
    └── .pattern-cache.json      # Analysis cache
```

## Language-Specific Analysis

### TypeScript/JavaScript

```yaml
analyze:
  config: tsconfig.json, package.json
  naming:
    - Function: Check for camelCase
    - Component: Check for PascalCase
    - Types/Interfaces: Check for I prefix or T prefix
  imports:
    - Check for path aliases in tsconfig
    - Analyze import grouping
  patterns:
    - async/await usage
    - Error handling (try-catch, .catch())
```

### Python

```yaml
analyze:
  config: pyproject.toml, setup.py
  naming:
    - Function: snake_case
    - Class: PascalCase
    - Constant: UPPER_SNAKE
  imports:
    - Standard lib vs third-party vs local
    - Absolute vs relative imports
  patterns:
    - Exception handling
    - Type hints usage
```

### Go

```yaml
analyze:
  config: go.mod
  naming:
    - Exported: PascalCase
    - Unexported: camelCase
    - Package: lowercase
  patterns:
    - Error handling (if err != nil)
    - Interface patterns
    - Package organization
```

## Example Flow

```
1. 사용자: "/cw:start"

2. pattern-learner 활성화
   - 설정 파일 탐색
   - 소스 파일 샘플링
   - 패턴 분석

3. 분석 결과:
   📊 Patterns analyzed: 15 files scanned
      - Language: TypeScript
      - Naming: camelCase functions, PascalCase components
      - Architecture: Feature-based structure
      - Testing: Jest with AAA pattern

4. 저장:
   → .caw/patterns/patterns.md

5. Builder 사용 시:
   "새 함수는 camelCase로 작성해야 합니다 (프로젝트 패턴)"
```

## Integration with Agents

| Agent | How It Uses Patterns |
|-------|---------------------|
| **Planner** | 아키텍처 패턴 참고하여 계획 |
| **Builder** | 코드 작성 시 패턴 준수 |
| **Reviewer** | 패턴 준수 여부 검토 |
| **Architect** | 새 컴포넌트 설계 시 참고 |

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| **quality-gate** | conventions check에서 패턴 활용 |
| **review-assistant** | 패턴 기반 체크리스트 생성 |
| **context-helper** | 패턴 문서를 컨텍스트로 제공 |

## Incremental Analysis

처음 분석 이후 점진적 업데이트:

```yaml
incremental:
  trigger:
    - New file type detected
    - Config file changed
    - Manual refresh

  process:
    1. Compare file hashes with cache
    2. Analyze only changed files
    3. Merge with existing patterns
    4. Update cache
```

## Pattern Confidence

패턴 신뢰도 표시:

| Confidence | Criteria |
|------------|----------|
| **High** | 90%+ files follow pattern |
| **Medium** | 70-90% files follow |
| **Low** | 50-70% files follow |
| **Mixed** | No clear pattern (< 50%) |

```markdown
## Naming Conventions

| Element | Pattern | Confidence | Example |
|---------|---------|------------|---------|
| Functions | camelCase | High (95%) | `getUserById()` |
| Files | Mixed | Low (45%) | kebab-case vs camelCase |
```

## Boundaries

**Will:**
- 기존 코드 분석하여 패턴 추출
- 패턴 문서화 및 캐싱
- 패턴 갱신 요청 시 재분석
- 신뢰도와 함께 패턴 제시

**Will Not:**
- 패턴 강제 적용 (quality-gate 역할)
- 코드 자동 수정
- 설정 파일 변경
- 외부 린터 설정 덮어쓰기
