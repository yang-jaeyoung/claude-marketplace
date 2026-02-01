---
name: reflect
description: "Run Ralph Loop - continuous improvement cycle after task completion (Reflect-Analyze-Learn-Plan-Habituate)"
allowed-tools: Read, Glob, Grep, Bash
---

# /cw:reflect - Ralph Loop Skill

Run the Ralph Loop continuous improvement cycle after completing a task or workflow.

## Usage

```bash
/cw:reflect              # Reflect on last completed task
/cw:reflect --task 2.3   # Reflect on specific step
/cw:reflect --full       # Full workflow retrospective
```

## Ralph Loop Phases

Execute each phase in order:

### Phase 1: REFLECT (R)
Review what happened during the task.

```
📝 Reading .caw/task_plan.md for completed steps
📝 Reading .caw/session.json for execution history

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
- Create Serena memories for persistent learnings (ENHANCED)

Output:
- New defaults established
- Checklist additions
- Memory updates for future sessions
```

#### Serena Memory Persistence (ENHANCED)

Save Ralph Loop results to Serena memory for cross-session utilization:

```
# 1. Save workflow patterns (successful approaches)
write_memory("workflow_patterns", """
# Workflow Patterns

## Last Updated
[ISO timestamp] by Ralph Loop

## Successful Approaches

### [Task Type]: [Pattern Name]
- **Context**: When to use this pattern
- **Approach**: Step-by-step method
- **Outcome**: Expected results
- **Caveats**: Things to watch out for

## Anti-patterns
- [What to avoid]
""")

# 2. Save individual Ralph learning (detailed analysis)
write_memory("ralph_learning_YYYYMMDD", """
# Ralph Learning: [Date]

## Cycle Summary
- **Task**: [name]
- **Outcome**: [success/partial/failure]
- **Duration**: [faster/expected/slower]

## Key Insights
1. [insight 1]
2. [insight 2]

## Action Items
- [ ] [action 1]
- [ ] [action 2]

## Patterns Identified
- [pattern 1]
- [pattern 2]
""")
```

**Save timing**:
- Auto-save immediately after Ralph Loop completion
- On explicit `/cw:sync --to-serena` execution

**Memory naming convention**:
| Memory | Content | Retention |
|--------|---------|-----------|
| `workflow_patterns` | Accumulated success patterns | Permanent (updated) |
| `ralph_learning_YYYYMMDD` | Individual retrospective results | Cleanup after 90 days |

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
1. Optionally prompt: "Run /cw:reflect for improvement insights?"
2. User can run manually anytime

### With Serena Memory
Store persistent learnings:
```
write_memory("ralph_learning_[date]", insights)
```

### After Task Completion
Consider running reflection after completing tasks:
```
💡 Task complete. Consider /cw:reflect for continuous improvement.
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
