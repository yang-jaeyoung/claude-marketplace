# 02. Architecture Concept Draft

## Overview
This document outlines the architecture for the **"Context-Aware Workflow Plugin"**. It leverages the Claude Code Plugin system capabilities: Commands, Agents, Skills, and Hooks.

## Architecture Guidelines

### 1. Plugin Structure
The tool will follow the standard Claude Code Plugin layout:
```
my-workflow-plugin/
├── .claude-plugin/
│   └── plugin.json       # Manifest: name, version, permissions
├── commands/             # Entry points
│   ├── start.md          # /start: Initialize a new task
│   └── status.md         # /status: Check current progress
├── agents/               # Specialized Personas
│   ├── planner.md        # "Architect": Breaks down tasks
│   └── reviewer.md       # "Critic": Validates against guidelines
├── skills/               # Reusable Capabilities
│   └── context-manager/  # The core "Memory" skill
│       ├── SKILL.md
│       └── scripts/      # Python scripts for context logic
└── hooks/                # Event Triggers
    └── hooks.json        # Config: PreToolUse, PostToolUse
```

### 2. Logic Engine (The "Hybrid" Part)
We will use **Python Scripts** embedded in the `skills/` or `hooks/` directories to handle logic.

*   **Context Manager Script (`skills/context-manager/scripts/manage.py`)**:
    *   **Function**: Scans the codebase, generates summaries, and "packs" context.
    *   **Trigger**: Invoked by the `context-manager` Skill or automatically via `PreToolUse` hook when starting a complex task.
*   **Validation Hooks (`hooks/hooks.json`)**:
    *   **PreCommit**: Run linting/tests.
    *   **PostEdit**: Check for forbidden patterns.

### 3. Context Management Strategy
We will implement a **"Tiered Context"** system:
*   **Active Context**: The files currently being edited.
*   **Project Context (Read-Only)**: `GUIDELINES.md`, `ARCHITECTURE.md`. These are always available via a "Goal-Seeking" Skill.
*   **Archived Context**: Old tasks, completed plans. Stored in `.docs/archive/` and indexed but not loaded unless requested.

### 4. Interactive Workflow (The "Loop")
The workflow is defined by a state machine enforced by the **Planner Agent**:
1.  **Phase 1: Discovery** (User + Planner)
    *   User inputs request.
    *   Planner asks clarifying questions (Brainstorming).
    *   *Artifact: `task_plan.md` (Proposed)*
2.  **Phase 2: Review** (User)
    *   User reviews `task_plan.md`.
    *   User approves/rejects via Chat.
3.  **Phase 3: Execution** (Builder Agent)
    *   Agent executes steps in `task_plan.md`.
    *   *Logic*: Hooks run validation on every step.
4.  **Phase 4: Handoff** (Reviewer Agent)
    *   Reviewer checks against `GUIDELINES.md`.
    *   User gives final sign-off.

## Next Steps
*   Define the exact "Slash Commands" needed.
*   Prototype the `context-manager` script.
