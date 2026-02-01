---
name: reflect
description: "Run Ralph Loop - continuous improvement cycle (Reflect-Analyze-Learn-Plan-Habituate)"
allowed-tools: Read, Glob, Grep, Bash
---

# /cw:reflect - Ralph Loop

Continuous improvement cycle after task completion.

## Usage

```bash
/cw:reflect              # Last completed task
/cw:reflect --task 2.3   # Specific step
/cw:reflect --full       # Full workflow retrospective
```

## Ralph Loop Phases

### R - REFLECT
```
Input: task_plan.md, session.json
Output: Task summary, outcome (success/partial/failure), duration, blockers, tools used
```

### A - ANALYZE
```
Questions: What worked? What didn't? Root causes? Patterns?
Output: Worked list, didn't work list, root causes, patterns
```

### L - LEARN
```
Questions: Key insights? Skills improved? Knowledge gaps?
Output: Insights, skills notes, gaps to address
```

### P - PLAN
```
Generate: Action items (high/medium/low), process changes, tool recommendations
```

### H - HABITUATE
```
Actions:
- Update .caw/learnings.md
- Add to checklists
- Create Serena memories
```

## Serena Memory Persistence

```yaml
workflow_patterns: Accumulated success patterns (permanent)
ralph_learning_YYYYMMDD: Individual retrospective (90-day retention)
```

## Output Format

```markdown
## 🔄 Ralph Loop

**Task**: [name] | **Cycle**: #N

### 📝 REFLECT
Outcome: ✅/⚠️/❌ | Duration: Faster/Expected/Slower

### 🔍 ANALYZE
Worked: [...] | Didn't Work: [...] | Root Causes: [...] | Patterns: [...]

### 💡 LEARN
Insights: [...] | Skills: [...] | Gaps: [...]

### 📋 PLAN
| Priority | Action | Scope |
|----------|--------|-------|
| 🔴 High | [...] | [...] |

### 🔧 HABITUATE
Applied: learnings.md ✅ | checklist ✅ | memory ✅
```

## Auto-Reflection Triggers

Consider when: 2x longer than estimated, multiple blockers, deep work mode, >500 lines changed
