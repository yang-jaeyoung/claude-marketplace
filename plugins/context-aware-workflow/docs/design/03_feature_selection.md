# 03. Feature Selection & Specification

This document details the specific features for the **Context-Aware Workflow Plugin**.

## 1. Slash Commands (User Interface)

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `/workflow:start` | `[task description]` | **Entry Point**. Analyzes the task, selects an Agent (Planner/Builder), and sets up the workspace. |
| `/workflow:plan` | `[active task]` | explicit call to the **Planner Agent**. Generates `implementation_plan.md`. |
| `/workflow:review` | `[target]` | Invokes the **Reviewer Agent**. Target can be a plan (`--plan`) or code (`--code`). |
| `/workflow:context` | `--refresh` / `--pack` | Manages the "Active Context". Forces a re-scan of dependencies or packs files into a summary. |
| `/workflow:status` | N/A | Displays current workflow state (building, planning, waiting for review) and context token usage. |

## 2. Agents (Personas)

| Agent | Role | Responsibilities | Key Skills |
| :--- | :--- | :--- | :--- |
| **Planner** | Architect | 1. Analyze request.<br>2. Explore codebase.<br>3. Draft `task_plan.md`.<br>4. Identify required context. | `ContextExplorer`, `PlanWriter` |
| **Builder** | Engineer | 1. Read `task_plan.md`.<br>2. Execute code changes (TDD).<br>3. Run tests. | `TestRunner`, `CodeEditor` |
| **Reviewer** | Critic | 1. Compare implementation vs Plan.<br>2. Check style/linting.<br>3. Validation against `GUIDELINES.md`. | `GuidelineChecker`, `DiffAnalyzer` |

## 3. Skills (The Logic Engine)
*These are backed by Python scripts in the plugin.*

### 3.1. ContextManager (`skills/context/`)
*   **Logic**:
    *   `pack_context(files)`: concise summary of file interfaces (class/function signatures) to save tokens.
    *   `prune_context()`: Detects files that haven't been touched in N turns and suggests removing them.
    *   `search_docs()`: Vector/Keyword search over `docs/` or archived tasks.

### 3.2. ComplianceChecker (`skills/compliance/`)
*   **Logic**:
    *   `check_guidelines()`: Scans changes against `GUIDELINES.md`.
    *   `verify_tests()`: Ensures new code has corresponding tests.

## 4. Hooks (Workflow Enforcement)

| Event | Matcher | Action | Purpose |
| :--- | :--- | :--- | :--- |
| **SessionStart** | N/A | `init_session.py` | Check plugin version, load `GUIDELINES.md` into memory. |
| **PreToolUse** | `Edit\|Write` | `check_plan_exists.py` | **Goal**: Prevent "coding without a plan". Warns if no `task_plan.md` exists. |
| **PostToolUse** | `Edit\|Write` | `auto_lint.py` | Run formatters immediately after edits. |
| **SubagentStop** | `Planner` | `request_review.py` | Automatically trigger a "Review" prompt when the Planner finishes. |

## 5. Artifacts
*   `task_plan.md`: The central source of truth for the current task.
*   `.claude/context_manifest.json`: Tracks which files are "Active", "Packed", or "Ignored".
*   `project_memory.md`: Long-term memory of architectural decisions.
