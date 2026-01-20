---
description: Apply diff from Codex Cloud task to local workspace
argument-hint: "<task_id>"
allowed-tools: ["Bash"]
---

# Codex Apply

Apply changes from a Codex Cloud task to your local workspace.

## Instructions

1. Get the task ID from the arguments
2. Apply the cloud task results:

```bash
codex apply <task_id>
```

3. Display the applied changes to the user

## Options

- Task ID: The ID of the completed cloud task to apply

## Usage Examples

```
/codex:apply task_abc123
/codex:apply 550e8400-e29b-41d4-a716-446655440000
```

## Workflow

1. Create cloud task with `/codex:cloud`
2. Wait for task completion
3. Apply results with this command
4. Review the applied changes

## Notes

- Task must be completed before applying
- Changes are applied as a diff to your local workspace
- Review changes before committing
- This is an experimental feature
- Use `git diff` to inspect applied changes
