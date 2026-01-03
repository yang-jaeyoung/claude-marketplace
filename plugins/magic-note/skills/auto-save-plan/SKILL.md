---
name: auto-save-plan
description: >-
  Automatically saves coding plans and implementation strategies to Magic Note.
  Use when generating implementation plans, architecture designs, step-by-step
  coding strategies, refactoring plans, or any structured development roadmap.
  Triggers on: "create a plan", "implementation plan", "let me plan",
  "step-by-step", "roadmap for", "architecture design", "how to implement",
  "구현 계획", "단계별로", "로드맵"
---

# Auto Save Plan Skill

This skill automatically detects and saves coding plans to Magic Note for future reference.

## When to Activate

Activate this skill when you:
- Create an implementation plan with numbered steps
- Design system architecture or component structure
- Generate a refactoring strategy
- Outline a migration or upgrade path
- Create a debugging investigation plan
- Design API endpoints or data models

## How to Save Plans

When you detect that you've created a plan:

1. **Identify Plan Content**: Look for structured content with:
   - Numbered or bulleted steps
   - Phase-based organization
   - Technical implementation details
   - File/component references

2. **Extract Metadata**:
   - **Title**: Summarize the plan in 5-10 words
   - **Tags**: Extract technology names, patterns, or domains mentioned
   - **Project**: Use current working directory name if available

3. **Save Using MCP Tool**:
   Use the `add_note` MCP tool with these parameters:
   ```
   type: "plan"
   title: [extracted title]
   content: [full plan content in markdown]
   tags: [extracted tags array]
   project: [current project name or "general"]
   ```

4. **Confirm to User**:
   After saving, inform the user:
   "📋 Plan saved to Magic Note: [title] (ID: [note_id])"

## Example Detection

Input that should trigger this skill:
```
Let me create an implementation plan for the authentication feature:

1. Create user model with password hashing
2. Implement JWT token generation
3. Add login/logout endpoints
4. Create authentication middleware
5. Add protected route decorators
```

Response action:
- Detect: This is an implementation plan (numbered steps, technical details)
- Extract title: "Authentication Feature Implementation Plan"
- Extract tags: ["auth", "jwt", "middleware"]
- Save with type: "plan"

## Non-Triggers

Do NOT activate for:
- Simple code explanations without steps
- Single-line responses
- Questions or clarifications
- Code-only responses without planning context
