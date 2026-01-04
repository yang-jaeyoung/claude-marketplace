# 01. Core Goals & Philosophy

Based on the brainstorming session and user requirements, the following core philosophy defines the direction for the **Agentic Workflow Tool**.

## 1. Hybrid Automation (CLI + Logic)
*   **Concept**: We will not rely solely on naive prompts. We will build a **"Hybrid" system** where rigorous programmatic logic (Hooks, Scripts, MCP) underpins the natural language interface.
*   **Why**: Prompt-only agents ("superpowers" style) are flexible but fragile. Hybrid agents ("SuperClaude" style) are reliable and efficient.
*   **Implementation**:
    *   **Interface**: Natural Language via Claude Code (`/command`).
    *   **Engine**: Shell Scripts (Hooks) and MCP Servers for heavy lifting (Context analysis, Git operations, Validation).

## 2. Target: Native Claude Code Plugin
*   **Concept**: The tool will be delivered as a **Claude Code Plugin** (`.claude-plugin`).
*   **Why**: Seamless integration into the user's existing workflow. No context switching. Easy distribution.
*   **Structure**:
    *   `commands/`: Slash commands for user interaction (`/workflow:start`).
    *   `agents/`: Specialized personas for different phases (Planner, Reviewer).
    *   `hooks/`: Enforcement engines (e.g., "Run linter before committing", "Update context after edit").

## 3. Interactive Collaboration (Human-in-the-Loop)
*   **Concept**: The tool is a **Co-pilot**, not an Autopilot. It requires specific checkpoints for user feedback.
*   **UX Pattern**: **"Propose → Review → Execute"**.
    *   The agent *proposes* a plan or code.
    *   The user *reviews* (interactive dialogue).
    *   The agent *executes* only after approval (or "auto-pilot" on low-risk tasks).

## 4. Context Management as a Core Feature
*   **Problem**: LLMs forget or get confused by large codebases.
*   **Solution**: **Active Context Engineering**.
    *   **Context Pruning**: Automatically remove irrelevant files from context.
    *   **Context Packing**: Summarize large modules into "Interface Definitions" before feeding to the LLM.
    *   **Persistence**: Save "Memory" (decisions, architectural patterns) to `.guidelines/` or similar, ensuring continuity across sessions.

## Summary Vision
> A **Native Claude Code Plugin** that acts as a **Context-Aware Project Manager**, enforcing rigorous workflows (Hybrid Logic) while collaborating interactively with the developer.
