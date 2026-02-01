# Context-Aware Workflow (CAW) Documentation

> **Version**: 1.9.0 | **Last Updated**: 2026-01-23

This directory contains all documentation for the CAW plugin.

---

## 📚 Documentation Structure

```
docs/
├── README.md              ← Current file (Documentation index)
├── USER_GUIDE.md          ← User guide (Main)
├── SKILL_DESIGN.md        ← Skill ecosystem design
├── design/                ← Design documents
│   ├── 01_philosophy.md
│   ├── 02_architecture_draft.md
│   ├── 03_feature_selection.md
│   ├── 04_plan_mode_integration.md
│   └── 05_ralph_loop_integration.md
└── references/            ← Reference documents (Claude Code features)
    ├── AgentSkills.md
    ├── Hooks.md
    ├── Plugins.md
    └── Subagents.md
```

---

## 🆕 v1.9.0 New Features

| Feature | Description | Related Docs |
|---------|-------------|--------------|
| **`--with-guidelines`** | Auto-generate GUIDELINES.md | [USER_GUIDE.md](./USER_GUIDE.md#-initialization-advanced-features-new) |
| **`--deep`** | Hierarchical AGENTS.md generation (deepinit pattern) | [USER_GUIDE.md](./USER_GUIDE.md#-initialization-advanced-features-new) |
| **Template System** | Templates stored in `_shared/templates/` | [USER_GUIDE.md](./USER_GUIDE.md#-initialization-advanced-features-new) |

## v1.8.0 Features

| Feature | Description | Related Docs |
|---------|-------------|--------------|
| **OMC Integration** | oh-my-claudecode integration with Graceful Degradation | [USER_GUIDE.md](./USER_GUIDE.md#-omc-integration) |
| **`/cw:qaloop`** | QA loop (build→review→fix iteration) | [USER_GUIDE.md](./USER_GUIDE.md#-qa-loop--ultraqa) |
| **`/cw:ultraqa`** | Intelligent automated QA | [USER_GUIDE.md](./USER_GUIDE.md#-qa-loop--ultraqa) |
| **`/cw:research`** | Unified research mode | [USER_GUIDE.md](./USER_GUIDE.md#-research-mode) |

## v1.7.0 Features

| Feature | Description | Related Docs |
|---------|-------------|--------------|
| **`/cw:loop`** | Autonomous iteration loop (5-level error recovery) | [USER_GUIDE.md](./USER_GUIDE.md#-autonomous-loop) |
| **Gemini CLI Review** | Gemini CLI review integration in Edit/Commit hooks | [USER_GUIDE.md](./USER_GUIDE.md#-hook-behavior) |
| **Loop State Persistence** | Pause/resume via `.caw/loop_state.json` | [USER_GUIDE.md](./USER_GUIDE.md#generated-artifacts) |

---

## 🎯 Quick Navigation

### For First-Time Users

1. **[USER_GUIDE.md](./USER_GUIDE.md)** - Complete guide from installation to all commands

### For Developers

| Topic | Document |
|-------|----------|
| Overall Architecture | [design/02_architecture_draft.md](./design/02_architecture_draft.md) |
| Design Philosophy | [design/01_philosophy.md](./design/01_philosophy.md) |
| Skill Design | [SKILL_DESIGN.md](./SKILL_DESIGN.md) |
| Plan Mode Integration | [design/04_plan_mode_integration.md](./design/04_plan_mode_integration.md) |
| Ralph Loop | [design/05_ralph_loop_integration.md](./design/05_ralph_loop_integration.md) |

### Claude Code Feature Reference

| Topic | Document |
|-------|----------|
| Agent/Skill System | [references/AgentSkills.md](./references/AgentSkills.md) |
| Subagents | [references/Subagents.md](./references/Subagents.md) |
| Plugin Structure | [references/Plugins.md](./references/Plugins.md) |
| Hook System | [references/Hooks.md](./references/Hooks.md) |

---

## 📖 Documentation Overview

### USER_GUIDE.md (User Guide)

**Audience**: All CAW users

**Key Contents**:
- Quick start (2 minutes)
- 17 commands detailed (`/cw:loop` included)
- 9 agents (17 including tiered variants)
- 16 skills list
- Autonomous execution loop (`/cw:loop` vs `/cw:auto`)
- Tidy First methodology
- Git Worktree parallel execution
- Ralph Loop continuous improvement
- Gemini CLI review integration
- Workflow examples
- Troubleshooting guide

### SKILL_DESIGN.md (Skill Design)

**Audience**: Plugin developers, contributors

**Key Contents**:
- Skill design principles
- 16 skills detailed specifications (6 new included)
  - `commit-discipline` - Tidy First commit separation
  - `context-manager` - Context window optimization
  - `dependency-analyzer` - Dependency analysis and parallel execution
  - `quick-fix` - Auto-fix
  - `reflect` - Ralph Loop continuous improvement
  - `serena-sync` - Serena MCP synchronization
- Hook integration patterns
- Agent-Skill mapping
- Progressive Disclosure strategy

---

## 🏗️ Design Documents (design/)

| Document | Description |
|----------|-------------|
| **01_philosophy.md** | Core philosophy: Hybrid Automation, Human-in-the-Loop, etc. |
| **02_architecture_draft.md** | Component structure, data flow, agent pipeline |
| **03_feature_selection.md** | MVP feature selection criteria and roadmap |
| **04_plan_mode_integration.md** | Integration design with Claude Code Plan Mode |
| **05_ralph_loop_integration.md** | Continuous improvement cycle (RALPH) design |

---

## 📚 Reference Documents (references/)

Reference documents for Claude Code core features.

| Document | Description |
|----------|-------------|
| **AgentSkills.md** | Differences between agents and skills, usage patterns |
| **Subagents.md** | Subagent execution via Task tool |
| **Plugins.md** | Plugin structure (plugin.json, components, etc.) |
| **Hooks.md** | Event hook system (SessionStart, PreToolUse, etc.) |

---

## 🔗 Related Links

- **README.md** (root): [../README.md](../README.md) - Project overview
- **AGENTS.md**: [../AGENTS.md](../AGENTS.md) - Agent detailed specifications
- **Schemas Directory**: [../schemas/](../schemas/) - JSON schema definitions
- **_shared Directory**: [../_shared/](../_shared/) - Shared resources

---

## 📝 Contributing to Documentation

Documentation improvements are welcome:

1. USER_GUIDE.md is written in **Korean**
2. README.md (root) is written in **English**
3. Design documents allow **Korean/English mixed**
4. Actively use markdown tables and diagrams

---

## 📋 Version History

| Version | Date | Major Changes |
|---------|------|---------------|
| **1.9.0** | 2026-01-23 | `--with-guidelines`, `--deep` flags, template system |
| 1.8.0 | 2026-01-22 | OMC integration, QA Loop, UltraQA, Research Mode |
| 1.7.0 | 2026-01-21 | `/cw:loop` autonomous execution, Gemini CLI integration, 6 new skills |
| 1.6.0 | 2026-01-19 | Tidy First, Git Worktree, Serena sync |
| 1.5.0 | 2026-01-15 | Ralph Loop continuous improvement |
| 1.4.0 | 2026-01-10 | Model routing, tiered agents, `/cw:auto` |

---

*Last updated: 2026-01-23*
