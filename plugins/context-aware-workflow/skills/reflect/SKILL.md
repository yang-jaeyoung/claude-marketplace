---
name: reflect
description: "Run Ralph Loop - continuous improvement cycle after task completion (Reflect-Analyze-Learn-Plan-Habituate)"
allowed-tools: Read, Glob, Grep, Bash
---

# /caw:reflect - Ralph Loop Skill

Run the Ralph Loop continuous improvement cycle after completing a task or workflow.

## Usage

```bash
/caw:reflect              # Reflect on last completed task
/caw:reflect --task 2.3   # Reflect on specific step
/caw:reflect --full       # Full workflow retrospective
```

## Ralph Loop Phases

Execute each phase in order:

### Phase 1: REFLECT (R)
Review what happened during the task.

```
📝 Reading .caw/task_plan.md for completed steps
📝 Reading .caw/sessions/ for execution history

Output:
- Task summary
- Outcome assessment (success/partial/failure)
- Duration assessment (faster/expected/slower)
- Blockers encountered
- Tools and agents used
```

### Phase 2: ANALYZE (A)
Identify patterns and issues.

```
Questions to answer:
- What approaches worked well?
- What didn't work as expected?
- What were the root causes of issues?
- Are there recurring patterns?

Output:
- List of what worked
- List of what didn't work
- Root cause analysis
- Pattern identification
```

### Phase 3: LEARN (L)
Extract lessons from the analysis.

```
Questions to answer:
- What key insights emerged?
- What skills were improved?
- What knowledge gaps were revealed?

Output:
- Key insights list
- Skills improvement notes
- Knowledge gaps to address
```

### Phase 4: PLAN (P)
Plan concrete improvements.

```
Generate:
- Action items with priority (high/medium/low)
- Process changes to implement
- Tool recommendations

Output:
- Prioritized action items
- Process improvement suggestions
- Tool/workflow recommendations
```

### Phase 5: HABITUATE (H)
Apply learnings to future work.

```
Actions:
- Update .caw/learnings.md with new insights
- Add items to project checklists
- Create Serena memories for persistent learnings

Output:
- New defaults established
- Checklist additions
- Memory updates for future sessions
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
- [item 2]

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
- ✅ Updated checklist: [item]
- ✅ Created memory: [name]

---
📊 **Improvement Score**: [0.0-1.0]
📈 **Cumulative Learnings**: [N] insights captured
```

## Integration

### After Task Completion
When a workflow step completes:
1. Optionally prompt: "Run /caw:reflect for improvement insights?"
2. User can run manually anytime

### With Serena Memory
Store persistent learnings:
```
write_memory("ralph_learning_[date]", insights)
```

### With Stop Hook
The Stop hook can suggest reflection:
```
"💡 Task complete. Consider /caw:reflect for continuous improvement."
```

## Learnings Storage

Insights are stored in `.caw/learnings.md`:

```markdown
# CAW Learnings

## 2024-01-15: Auth Implementation
- TDD approach reduced debugging time by 50%
- Security review should happen earlier

## 2024-01-14: API Refactoring
- Batch operations more efficient than sequential
```

## Auto-Reflection Triggers

Consider automatic reflection when:
- Task took 2x longer than estimated
- Multiple blockers encountered
- User explicitly requested deep work mode
- Significant code changes (>500 lines)
