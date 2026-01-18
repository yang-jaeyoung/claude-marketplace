---
description: Start a context-aware workflow session. Initializes environment if needed, analyzes task requirements, imports Plan Mode plans, and generates structured task_plan.md.
---

# /cw:start - Workflow Initialization

Initialize a context-aware workflow session for structured task execution.

## Pre-flight Check: Environment Initialization

**IMPORTANT**: Before any planning, check if environment is initialized.

```
Check: Does .caw/context_manifest.json exist?
├─ NO  → MUST invoke Bootstrapper Agent using Task tool:
│        Task(subagent_type="cw:bootstrapper", prompt="Initialize CAW environment")
│        WAIT for Task to complete before proceeding
│        Verify .caw/context_manifest.json was created
│        Then proceed to planning
└─ YES → Proceed directly to planning
```

### CRITICAL: Bootstrapper Invocation

When environment is NOT initialized, you MUST:

1. **Invoke Bootstrapper as separate Task agent**:
   ```
   Task tool:
     subagent_type: "cw:bootstrapper"
     prompt: "Initialize CAW environment. Create .caw/ directory structure, detect project context, and generate context_manifest.json"
   ```

2. **Wait for completion** - Do NOT proceed until Task returns successfully

3. **Verify initialization**:
   ```
   Check: Does .caw/context_manifest.json now exist?
   ├─ YES → Proceed to Planner
   └─ NO → Report error, do not proceed
   ```

**DO NOT** attempt to bootstrap inline. The Bootstrapper agent has specific tools (Bash, Write, Glob) and logic that must be executed as a separate agent to properly create files on disk.

## Invocation Modes

### Mode 1: New Task with Description
When invoked with a task description:
```
/cw:start "Implement user authentication with JWT"
```

1. **Check environment**: Verify `.caw/context_manifest.json` exists
2. **If not initialized**:
   - Use Task tool with `subagent_type="cw:bootstrapper"` to initialize
   - Wait for bootstrapper Task to complete
   - Verify `.caw/context_manifest.json` was created
3. **Invoke Planner Agent** using Task tool with `subagent_type="cw:planner"`
4. Planner will:
   - Ask clarifying questions if needed
   - Explore codebase for context
   - **CRITICAL**: Generate `.caw/task_plan.md` with:
     - **Phase Deps** for each phase (enables parallel execution)
     - **Deps column** for each step (enables dependency tracking)
   - Identify parallel execution opportunities

### Post-Bootstrap Verification

After Bootstrapper Task completes (if invoked):

1. **Verify files exist**:
   - `.caw/context_manifest.json` must exist
   - `.caw/archives/` directory must exist

2. **If verification fails**:
   ```
   ❌ Bootstrap verification failed
   - Expected: .caw/context_manifest.json
   - Status: NOT_FOUND

   Please run /cw:init manually to debug initialization.
   ```

3. **If verification succeeds**:
   - Log: "✅ Environment initialized successfully"
   - Proceed to Planner invocation

### Mode 2: Import from Plan Mode
When invoked with `--from-plan`:
```
/cw:start --from-plan
```

1. **Detect** existing Plan Mode output:
   - Check `.claude/plan.md` (default)
   - Check `.claude/plans/current.md`
2. If found:
   - Display plan summary
   - Ask user to confirm import
   - Convert to `.caw/task_plan.md` format
3. If not found:
   - Inform user no plan detected
   - Offer to start fresh workflow

### Mode 3: Specific Plan File
When invoked with `--plan-file <path>`:
```
/cw:start --plan-file docs/my-plan.md
```

1. **Read** the specified plan file
2. **Validate** it contains actionable steps
3. **Convert** to `.caw/task_plan.md` format

## Interactive Discovery

When starting a new task (Mode 1), engage in discovery dialogue:

1. **Initial Analysis**:
   - Parse the task description for key entities
   - Identify ambiguous requirements
   - Detect mentioned files or components

2. **Clarifying Questions** (use AskUserQuestion):
   - Scope boundaries: "Should this include X?"
   - Technical choices: "Prefer approach A or B?"
   - Priority: "Core functionality first, or complete feature?"
   - Constraints: "Any existing patterns to follow?"

3. **Context Gathering**:
   - Use Glob to find relevant files
   - Use Grep to search for related code
   - Read key configuration files (package.json, tsconfig.json, etc.)

## Output: .caw/task_plan.md

**IMPORTANT**: You MUST use the Write tool to create `.caw/task_plan.md`. First create the `.caw/` directory if it doesn't exist. Do not just display the plan - actually write it to disk.

Generate and **write** `.caw/task_plan.md` with this structure:

```markdown
# Task Plan: [Task Title]

## Metadata
| Field | Value |
|-------|-------|
| **Created** | [timestamp] |
| **Source** | User request / Plan Mode import |
| **Status** | Planning |

## Context Files

### Active Context
| File | Reason | Status |
|------|--------|--------|
| `src/auth/index.ts` | Main implementation target | 📝 Edit |

### Project Context (Read-Only)
- `GUIDELINES.md`
- `package.json`

## Task Summary
[2-3 sentence summary of what will be accomplished]

## Execution Phases

### Phase 1: [Phase Name]
**Phase Deps**: -

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 1.1 | [Step description] | ⏳ | Builder | - | |
| 1.2 | [Step description] | ⏳ | Builder | - | ⚡ Parallel OK |
| 1.3 | [Step description] | ⏳ | Builder | - | ⚡ Parallel OK |

### Phase 2: [Phase Name]
**Phase Deps**: phase 1

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 2.1 | [Step description] | ⏳ | Builder | - | |
| 2.2 | [Step description] | ⏳ | Builder | 2.1 | |

### Phase 3: [Phase Name]
**Phase Deps**: phase 1

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 3.1 | [Step description] | ⏳ | Builder | - | |

### Phase 4: [Integration Phase Name]
**Phase Deps**: phase 2, phase 3

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 4.1 | [Integration step] | ⏳ | Builder | - | |

## Validation Checklist
- [ ] Existing tests pass
- [ ] New tests added
- [ ] Code follows project conventions

## Open Questions
- [Any unresolved questions for user]
```

## Integration

- **Triggers ContextManager Skill**: Updates `.caw/context_manifest.json`
- **Works with Hooks**: SessionStart hook may pre-detect plans
- **Enables PreToolUse Hook**: After plan exists, hook validates plan adherence

## Parallel Execution Requirements

**CRITICAL**: Planner Agent MUST generate plans that support parallel execution.

### Phase Deps (Required)

Every phase MUST include a `**Phase Deps**` line:
- `**Phase Deps**: -` - No dependencies (can start immediately)
- `**Phase Deps**: phase 1` - Depends on Phase 1 completion
- `**Phase Deps**: phase 2, phase 3` - Depends on multiple phases

### Deps Column (Required)

Every step MUST have a Deps column:
- `-` - No dependencies within the phase
- `2.1` - Depends on step 2.1
- `2.1, 2.2` - Depends on multiple steps
- `1.*` - Depends on all Phase 1 steps

### Parallel Opportunity Identification

When creating the plan, identify:
1. **Phases with same Phase Deps** → Can run in parallel worktrees
2. **Steps with same Deps** → Can run in parallel background agents

Mark parallel opportunities in Notes column:
- `⚡ Parallel OK` - Can run with other marked steps
- `🔒 Sequential` - Must run alone

### Example Parallel Structure

```markdown
### Phase 2: Auth Implementation
**Phase Deps**: phase 1        ← Same as Phase 3, can parallel

### Phase 3: User Management
**Phase Deps**: phase 1        ← Same as Phase 2, can parallel

### Phase 4: Integration
**Phase Deps**: phase 2, phase 3  ← Must wait for both
```

This enables:
```bash
/cw:next --worktree phase 2   # Terminal 1
/cw:next --worktree phase 3   # Terminal 2
# ... work in parallel ...
/cw:merge --all               # Merge both when done
```

## Tips

- Be thorough in discovery - better planning reduces rework
- Always confirm understanding before generating plan
- Reference specific files and line numbers when possible
- Keep phases small and testable
- **Design phases for parallel execution when possible**

## Plan Mode Detection

워크플로우 시작 시 **기존 Plan Mode 계획이 있는지 자동 감지**합니다.

### 자동 감지 워크플로우

```
/cw:start 실행 시:
1. Plan Mode 파일 확인:
   - .claude/plan.md
   - .claude/plans/current.md
   - .claude/plans/*.md (최신 파일)

2. 파일이 존재하면:
   - 계획 내용 요약 표시
   - 변환 여부 확인 질문

3. 사용자 선택:
   [1] Plan Mode 계획을 CAW task_plan.md로 변환
   [2] 새로운 계획 작성 (Plan Mode 무시)
   [3] Plan Mode 계획 확인 후 결정
```

### 감지 대화 예시

```
📋 Plan Mode 계획 감지됨

파일: .claude/plan.md
제목: JWT Authentication Implementation
단계 수: 8 steps in 3 phases

이 계획을 CAW 워크플로우로 변환하시겠습니까?

[1] 변환하여 진행 (Recommended)
[2] 새로운 계획 작성
[3] 계획 내용 먼저 확인
```

### 변환 프로세스

```yaml
plan_mode_to_cw:
  source_patterns:
    - ".claude/plan.md"
    - ".claude/plans/*.md"

  extraction:
    title: "# 또는 첫 번째 heading"
    steps: "- [ ] 또는 numbered list"
    context: "File mentions, code blocks"

  conversion:
    1. 제목 추출 → Task Plan title
    2. 체크리스트 항목 → Steps
    3. 관련 파일 언급 → Context Files
    4. 코드 블록 → Implementation hints

  output:
    file: ".caw/task_plan.md"
    format: "CAW standard template"
```

### 변환 결과 예시

**Plan Mode 원본:**
```markdown
# JWT Authentication

## Steps
- [ ] Create JWT utility functions
- [ ] Implement auth middleware
- [ ] Add login endpoint
```

**CAW task_plan.md 변환:**
```markdown
# Task Plan: JWT Authentication

## Execution Phases

### Phase 1: Core Implementation
**Phase Deps**: -

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 1.1 | Create JWT utility functions | ⏳ | Builder | - | |
| 1.2 | Implement auth middleware | ⏳ | Builder | 1.1 | |
| 1.3 | Add login endpoint | ⏳ | Builder | 1.2 | |
```

### Plan Mode 없이 시작

Plan Mode 계획이 감지되지 않으면:
```
No Plan Mode plan detected.
Proceeding with new CAW workflow...

→ Invoke Planner Agent for interactive discovery
```
