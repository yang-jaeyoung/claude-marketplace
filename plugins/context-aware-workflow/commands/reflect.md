---
description: Run Ralph Loop - continuous improvement cycle after task completion (Reflect-Analyze-Learn-Plan-Habituate)
---

# /caw:reflect - Ralph Loop Improvement Cycle

Run the Ralph Loop continuous improvement cycle after completing a task or workflow.

## Usage

```bash
/caw:reflect              # Reflect on last completed task
/caw:reflect --task 2.3   # Reflect on specific step
/caw:reflect --full       # Full workflow retrospective
```

## Behavior

### Overview

RALPH = **R**eflect → **A**nalyze → **L**earn → **P**lan → **H**abituate

This command executes a structured improvement cycle to capture learnings and improve future workflows.

### Phase 1: REFLECT (R)

Review what happened during the task.

1. Read `.caw/task_plan.md` for completed steps
2. Read `.caw/session.json` for execution history
3. Generate:

```
📝 REFLECT

Task: [Task name from plan]
Outcome: ✅ Success / ⚠️ Partial / ❌ Failure
Duration: ⏱️ Faster / Expected / Slower than planned
Blockers: [list or "None"]
Tools Used: [agent/tool list]
```

### Phase 2: ANALYZE (A)

Identify patterns and issues.

Questions to answer:
- What approaches worked well?
- What didn't work as expected?
- What were the root causes of issues?
- Are there recurring patterns?

```
🔍 ANALYZE

What Worked:
- [item 1]
- [item 2]

What Didn't Work:
- [item 1]

Root Causes:
- [cause 1]

Patterns:
- [pattern 1]
```

### Phase 3: LEARN (L)

Extract lessons from the analysis.

```
💡 LEARN

Key Insights:
1. [insight]

Skills Improved: [list]
Knowledge Gaps: [list]
```

### Phase 4: PLAN (P)

Plan concrete improvements.

```
📋 PLAN

| Priority | Action | Applies To |
|----------|--------|------------|
| 🔴 High | [action] | [scope] |
| 🟡 Medium | [action] | [scope] |
| 🟢 Low | [action] | [scope] |
```

### Phase 5: HABITUATE (H)

Apply learnings to future work.

Actions:
1. Update `.caw/learnings.md` with new insights
2. Add items to project checklists if applicable
3. Create Serena memories for persistent learnings

```
🔧 HABITUATE

Applied Changes:
- ✅ Added to .caw/learnings.md
- ✅ Updated checklist: [item]
- ✅ Created memory: ralph_learning_[date]
```

## Output Format

```markdown
## 🔄 Ralph Loop - Improvement Cycle

**Task**: [Task name from plan]
**Cycle**: #[N] | **Date**: [timestamp]

### 📝 REFLECT
- **Outcome**: ✅ Success / ⚠️ Partial / ❌ Failure
- **Duration**: ⏱️ Faster / Expected / Slower than planned
- **Blockers**: [list or "None"]
- **Tools Used**: [agent/tool list]

### 🔍 ANALYZE
**What Worked**:
- [item 1]

**What Didn't Work**:
- [item 1]

**Root Causes**:
- [cause 1]

**Patterns**:
- [pattern 1]

### 💡 LEARN
**Key Insights**:
1. [insight]

**Skills Improved**: [list]
**Knowledge Gaps**: [list]

### 📋 PLAN
| Priority | Action | Applies To |
|----------|--------|------------|
| 🔴 High | [action] | [scope] |
| 🟡 Medium | [action] | [scope] |

### 🔧 HABITUATE
**Applied Changes**:
- ✅ Added to .caw/learnings.md
- ✅ Created memory: [name]

---
📊 **Improvement Score**: [0.0-1.0]
📈 **Cumulative Learnings**: [N] insights captured
```

## Options

| Option | Description |
|--------|-------------|
| `--task <step>` | Reflect on specific task step (e.g., 2.3) |
| `--full` | Full workflow retrospective |
| `--no-memory` | Skip Serena memory creation |
| `--quiet` | Minimal output, just save learnings |

## Integration

### With Serena Memory

Store persistent learnings:
```
write_memory("ralph_learning_[date]", insights)
```

### After Task Completion

Consider running reflection when tasks complete:
```
💡 Task complete. Consider /caw:reflect for continuous improvement.
```

## Auto-Reflection Triggers

Consider running `/caw:reflect` when:
- Task took 2x longer than estimated
- Multiple blockers were encountered
- User explicitly requested deep work mode
- Significant code changes (>500 lines)

## Learnings Storage

Insights are accumulated in `.caw/learnings.md`:

```markdown
# CAW Learnings

## 2024-01-15: Auth Implementation
- TDD approach reduced debugging time by 50%
- Security review should happen earlier

## 2024-01-14: API Refactoring
- Batch operations more efficient than sequential
```

## Edge Cases

### No Task Plan Found

```
⚠️ No task plan found

Cannot run reflection without context.
Please start a workflow first:
   /caw:start "your task description"

Or specify what to reflect on:
   /caw:reflect --task "manual task description"
```

### Empty Execution History

```
ℹ️ Limited execution history available

Proceeding with available context...
[Partial reflection based on task_plan.md only]

💡 For richer reflections, use /caw:next to execute tasks
```
