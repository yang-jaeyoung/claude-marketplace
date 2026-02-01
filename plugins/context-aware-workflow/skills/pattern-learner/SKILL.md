---
name: pattern-learner
description: Analyzes codebase to learn project-specific patterns including code style, architecture conventions, and testing approaches. Invoked during /cw:start or when agents need pattern information for consistency.
allowed-tools: Read, Glob, Grep, Bash
---

# Pattern Learner

Analyzes codebase to learn and document project-specific coding patterns for consistency enforcement.

## Core Principle

**Pattern Learning = Consistency Guarantee**

Analyze existing project code to learn patterns and ensure new code follows the same rules.

## Triggers

This Skill activates in the following situations:

1. **/cw:start execution**
   - Auto-analyze at workflow start
   - Initial project pattern learning

2. **Agent request**
   - "What are the patterns in this project?"
   - "Check existing code style"

3. **Pattern refresh request**
   - "Re-analyze patterns"
   - When new file types are discovered

4. **Before new file creation**
   - Builder checks patterns before creating files

## Pattern Categories

| Category | What to Learn | Examples |
|----------|---------------|----------|
| **Naming** | Naming conventions | camelCase functions, PascalCase classes |
| **Architecture** | Directory structure, modularization | Clean Architecture, Feature-based |
| **Error Handling** | Error handling patterns | Result<T,E>, try-catch style |
| **Testing** | Test structure, naming | AAA pattern, *.test.ts |
| **Imports** | Import organization | Grouped, path aliases |
| **Documentation** | Comment styles | JSDoc, docstrings |

## Behavior

### Step 1: File Discovery

Discover files to analyze:

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

Extract patterns for each category:

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

Document patterns:

```yaml
action: Write tool
path: .caw/patterns/patterns.md
content: See Pattern Template below
```

### Step 4: Cache for Performance

Cache analysis results:

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

Confirm analysis completion:

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
1. User: "/cw:start"

2. pattern-learner activated
   - Discover config files
   - Sample source files
   - Analyze patterns

3. Analysis results:
   📊 Patterns analyzed: 15 files scanned
      - Language: TypeScript
      - Naming: camelCase functions, PascalCase components
      - Architecture: Feature-based structure
      - Testing: Jest with AAA pattern

4. Save:
   → .caw/patterns/patterns.md

5. When Builder uses:
   "New functions should use camelCase (project pattern)"
```

## Integration with Agents

| Agent | How It Uses Patterns |
|-------|---------------------|
| **Planner** | Reference architecture patterns for planning |
| **Builder** | Follow patterns when writing code |
| **Reviewer** | Review pattern compliance |
| **Architect** | Reference when designing new components |

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| **quality-gate** | Use patterns in conventions check |
| **review-assistant** | Generate pattern-based checklist |
| **context-helper** | Provide pattern docs as context |

## Incremental Analysis

Incremental updates after initial analysis:

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

Pattern confidence indicators:

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
- Analyze existing code to extract patterns
- Document and cache patterns
- Re-analyze on pattern refresh requests
- Present patterns with confidence levels

**Will Not:**
- Enforce patterns (quality-gate role)
- Auto-fix code
- Modify config files
- Override external linter settings
