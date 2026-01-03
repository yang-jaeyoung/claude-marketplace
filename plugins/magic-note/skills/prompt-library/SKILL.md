---
name: prompt-library
description: >-
  Suggests relevant saved prompts from Magic Note when users request common
  coding tasks. Use when users ask for code reviews, refactoring, documentation,
  testing, or other repeatable coding tasks that might have saved prompts.
  Triggers on: "review this code", "refactor this", "add documentation",
  "write tests", "code review", "리뷰해줘", "리팩토링", "테스트 작성"
---

# Prompt Library Skill

This skill helps users leverage their saved prompts for common coding tasks.

## When to Activate

Activate this skill when users request:
- Code review or analysis
- Refactoring suggestions
- Documentation generation
- Test case creation
- Bug investigation
- Performance optimization
- Security audit
- API design review

## How to Suggest Prompts

1. **Detect Task Type**: Identify the category of coding task requested

2. **Search Saved Prompts**:
   Use the `list_notes` MCP tool with:
   ```
   type: "prompt"
   search: [task keywords]
   ```

3. **Present Options**:
   If relevant prompts are found, offer them to the user:
   ```
   📚 Found saved prompts that might help:

   1. [prompt_title] - [brief description]
      Tags: [tags]

   Would you like me to use one of these prompts, or proceed with a fresh approach?
   ```

4. **Load Selected Prompt**:
   If user selects a prompt, use `get_note` to retrieve full content and apply it to the current task.

## Task-to-Keyword Mapping

| User Request | Search Keywords |
|--------------|-----------------|
| "review this code" | code-review, review, analysis |
| "refactor this" | refactor, clean-code, improvement |
| "add documentation" | docs, documentation, comments |
| "write tests" | test, testing, unit-test |
| "find bugs" | debug, bug, investigation |
| "optimize performance" | performance, optimization, speed |
| "security check" | security, audit, vulnerability |

## Example Interaction

**User**: "Can you review this API endpoint?"

**Skill Action**:
1. Detect: Code review request
2. Search: `list_notes type="prompt" search="code-review api"`
3. Found: "API Code Review Checklist" prompt

**Response**:
```
📚 Found a saved prompt: "API Code Review Checklist"
   Tags: [api, review, best-practices]

Would you like me to use this saved review checklist, or perform a standard review?
```

## Prompt Saving Suggestion

When completing a task without a saved prompt, consider suggesting:
```
💡 This review approach worked well. Would you like to save it as a reusable prompt for future reviews?
```

If user agrees, use `add_note` with type="prompt" to save.

## Non-Triggers

Do NOT activate for:
- Simple questions about code
- Requests for new feature implementation
- General programming questions
- Tasks that are clearly one-off
