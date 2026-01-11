---
name: context-helper
description: Helps agents understand and manage context efficiently. Provides relevant files, previous phase outputs, and related insights based on current workflow step.
allowed-tools: Read, Glob, Grep
forked-context: true
forked-context-returns: |
  files: 우선순위 파일 목록 (최대 10개)
  step_outputs: 이전 단계 요약
  insights: 관련 인사이트 (압축)
  dependencies: 의존성 파일 목록
hooks:
  AgentStartStep:
    action: provide_context
    priority: 2
    condition: "requires .caw/ directory"
---

# Context Helper

Intelligent context management to help agents work efficiently with relevant information.

## Triggers

This skill activates when:
1. Agent starts working on a new step
2. Agent requests context for current task
3. Context window nearing limits
4. Phase transition (summarize previous phase)

## Context Categories

### 1. Task Context
```yaml
source: .caw/task_plan.md
provides:
  - Current phase and step details
  - Pending steps overview
  - Success criteria
  - Open questions
```

### 2. Code Context
```yaml
source: .caw/context_manifest.json + codebase
provides:
  - Files to modify (priority order)
  - Dependencies between files
  - Related existing code
  - Test files for current scope
```

### 3. Knowledge Context
```yaml
source: .caw/insights/, .caw/decisions/
provides:
  - Relevant insights for current step
  - Technical decisions that apply
  - Learned patterns
```

### 4. Progress Context
```yaml
source: .caw/metrics.json
provides:
  - What was completed in previous steps
  - Current step duration
  - Quality gate history
```

## Behavior

### Step 1: Analyze Current Step

```yaml
parse_step:
  from: task_plan.md
  extract:
    - step_id: "2.3"
    - step_description: "Implement auth middleware"
    - phase_context: "Core Implementation"
    - dependencies: ["2.1", "2.2"]
```

### Step 2: Gather Relevant Context

```yaml
context_gathering:
  # Required context (always include)
  required:
    - task_plan.md (current step section)
    - Files listed in step description

  # Dependency context (if referenced)
  dependencies:
    - Outputs from dependent steps
    - Files modified in dependent steps

  # Related context (if space permits)
  related:
    - Matching insights
    - Relevant decisions
    - Similar code patterns
```

### Step 3: Prioritize and Filter

```yaml
prioritization:
  # By relevance score
  scoring:
    direct_reference: 1.0    # Mentioned in step
    dependency_output: 0.8   # From required step
    same_directory: 0.6      # Same folder as target
    pattern_match: 0.4       # Keyword/pattern match
    insight_related: 0.3     # Related insight

  # By context budget
  budget:
    high_priority: 70%       # Required + dependencies
    medium_priority: 20%     # Related code
    low_priority: 10%        # Insights/decisions
```

### Step 4: Present Context

```markdown
## 📋 Context for Step 2.3: Auth Middleware

### Required Files (Read First)
| Priority | File | Reason |
|----------|------|--------|
| 1 | src/auth/jwt.ts | Step 2.1 output, dependency |
| 2 | src/auth/types.ts | Type definitions |
| 3 | src/middleware/index.ts | Integration point |

### Previous Step Outputs
**Step 2.1** (JWT Utilities):
- Created `generateToken()`, `verifyToken()` functions
- Token expiry: 1 hour (configurable)

**Step 2.2** (Token Validation):
- Implemented `validateToken()` middleware base
- Added error handling for expired tokens

### Related Insights
💡 **JWT Token Refresh Pattern** (2026-01-04)
   Token refresh should happen before expiry, not after...

### Relevant Decisions
📋 **ADR-001**: JWT vs Session
   Chose JWT for stateless architecture...

### Test Files
- tests/auth/middleware.test.ts (create new)
- tests/auth/jwt.test.ts (reference)
```

## Context Summaries

### Phase Completion Summary

When a phase completes, create summary for next phase:

```markdown
## Phase 1 Summary (for Phase 2 reference)

### Completed Steps
1. **Step 1.1**: Project structure created
   - Created src/auth/ directory
   - Added base configuration

2. **Step 1.2**: Dependencies installed
   - jsonwebtoken@9.0.0
   - bcrypt@5.1.0

3. **Step 1.3**: TypeScript config
   - Strict mode enabled
   - Path aliases configured

### Files Created
- src/auth/index.ts
- src/auth/types.ts
- tsconfig.json (modified)

### Key Decisions
- Token storage: HTTP-only cookies
- Algorithm: RS256

### Insights Captured
- JWT best practices for refresh tokens
```

## Context Commands

### For Agents

```markdown
## Agent Context Queries

# Get context for current step
"What context do I need for this step?"
→ context-helper provides prioritized file list

# Get specific context
"Show me the output from Step 2.1"
→ context-helper retrieves step output summary

# Check dependencies
"What files does this step depend on?"
→ context-helper lists dependency files

# Find related code
"Are there similar patterns in the codebase?"
→ context-helper searches for matching patterns
```

### For Users

```markdown
## User Context Commands

/caw:context                    # Show current step context
/caw:context --step 2.1         # Show specific step context
/caw:context --phase 1          # Show phase summary
/caw:context --insights         # Show related insights
/caw:context --minimal          # Compact context view
```

## Context Manifest Enhancement

### `.caw/context_manifest.json` Updates

```json
{
  "version": "1.0",
  "task_plan": ".caw/task_plan.md",
  "current_step": "2.3",
  "context_priority": {
    "critical": [
      "src/auth/jwt.ts",
      "src/auth/middleware.ts"
    ],
    "important": [
      "src/auth/types.ts",
      "src/config/auth.ts"
    ],
    "reference": [
      "tests/auth/jwt.test.ts",
      "docs/auth-flow.md"
    ]
  },
  "step_outputs": {
    "2.1": {
      "files_created": ["src/auth/jwt.ts"],
      "files_modified": [],
      "summary": "JWT utility functions implemented"
    },
    "2.2": {
      "files_created": [],
      "files_modified": ["src/auth/jwt.ts"],
      "summary": "Token validation added"
    }
  },
  "related_insights": [
    ".caw/insights/20260104-jwt-refresh.md"
  ],
  "related_decisions": [
    ".caw/decisions/ADR-001-jwt-auth.md"
  ]
}
```

## Memory Optimization

### Context Pruning

```yaml
pruning_strategy:
  # Remove completed step details (keep summary)
  completed_steps: summarize_only

  # Compress file contents
  large_files: extract_relevant_sections

  # Age-based pruning
  old_context: >24h_old → archive

  # Duplicate detection
  similar_content: deduplicate
```

### Progressive Loading

```yaml
loading_strategy:
  initial_load:
    - task_plan.md (current section)
    - context_manifest.json
    - Current step files

  on_demand:
    - Previous step outputs
    - Related insights
    - Reference files

  never_auto_load:
    - Archived sessions
    - Old insights (>7 days)
    - Unrelated code
```

## Integration

### With Agents

| Agent | Context Provided |
|-------|------------------|
| Builder | Files to modify, test patterns |
| Reviewer | Changed files, original state |
| Planner | Codebase structure, patterns |
| Architect | System overview, dependencies |

### With Other Skills

| Skill | Integration |
|-------|-------------|
| insight-collector | Provides relevant insights |
| pattern-learner | Provides coding patterns |
| session-persister | Restores context state |
| progress-tracker | Provides step history |

## Boundaries

**Will:**
- Provide prioritized, relevant context
- Summarize previous phase outputs
- Link related insights and decisions
- Optimize for context window limits

**Will Not:**
- Read files without relevance scoring
- Include entire file contents (use sections)
- Override agent's file reading decisions
- Store context permanently (transient)

## Forked Context Behavior

See [Forked Context Pattern](../../_shared/forked-context.md).

**Returns**: Prioritized file list with context summaries

**Output Examples:**
- `📋 Context for Step 2.3` - Files: critical/important/reference lists
- `step_outputs: {"2.1": "summary", "2.2": "summary"}` - Previous step context
- `📋 [Step 2.3] Files: 3 critical | Deps: 2.1, 2.2` - Minimal mode
