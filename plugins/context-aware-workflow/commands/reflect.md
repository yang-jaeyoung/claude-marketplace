---
description: Run Ralph Loop - continuous improvement cycle after task completion (Reflect-Analyze-Learn-Plan-Habituate)
argument-hint: "[--task N.M] [--full]"
---

# /cw:reflect - Ralph Loop Improvement Cycle

Run the Ralph Loop continuous improvement cycle after completing a task or workflow.

## Usage

```bash
/cw:reflect              # Reflect on last completed task
/cw:reflect --task 2.3   # Reflect on specific step
/cw:reflect --full       # Full workflow retrospective
```

## RALPH Phases

**R**eflect → **A**nalyze → **L**earn → **P**lan → **H**abituate

| Phase | Action |
|-------|--------|
| **R - Reflect** | Review task: outcome, duration, blockers, tools used |
| **A - Analyze** | Identify: what worked, what didn't, root causes, patterns |
| **L - Learn** | Extract: key insights, skills improved, knowledge gaps |
| **P - Plan** | Plan improvements with priority (High/Medium/Low) |
| **H - Habituate** | Apply: update learnings.md, checklists, Serena memories |

## Options

| Option | Description |
|--------|-------------|
| `--task <step>` | Reflect on specific task step (e.g., 2.3) |
| `--full` | Full workflow retrospective |
| `--no-memory` | Skip Serena memory creation |
| `--quiet` | Minimal output, just save learnings |

## Output

```markdown
## 🔄 Ralph Loop - Improvement Cycle

**Task**: [Task name] | **Outcome**: ✅/⚠️/❌ | **Duration**: ⏱️ Faster/Expected/Slower

### Key Insights
1. [insight]

### Actions
| Priority | Action | Applies To |
|----------|--------|------------|
| 🔴 High | [action] | [scope] |

### Applied
- ✅ Added to .caw/learnings.md
- ✅ Created memory: ralph_learning_[date]

📊 Improvement Score: [0.0-1.0]
```

## Auto-Reflection Triggers

Consider running when:
- Task took 2x longer than estimated
- Multiple blockers encountered
- Deep work mode requested
- Significant code changes (>500 lines)

## Learnings Storage

Insights accumulated in `.caw/learnings.md`:
```markdown
## 2024-01-15: Auth Implementation
- TDD approach reduced debugging time by 50%
- Security review should happen earlier
```

## Integration

- **Reads**: `.caw/task_plan.md`, `.caw/session.json`
- **Writes**: `.caw/learnings.md`
- **Serena**: `write_memory("ralph_learning_[date]", insights)`
