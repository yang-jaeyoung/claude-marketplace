---
description: Create Codex Cloud task (requires --env)
argument-hint: "--env <env_id> <task>"
allowed-tools: ["Bash"]
---

# Codex Cloud

Create a task on Codex Cloud for remote execution.

## Instructions

1. Parse the arguments:
   - `--env <env_id>`: Required environment ID
   - Remaining arguments: the task description

2. Run Codex Cloud task:

```bash
codex cloud --env <env_id> "<task>"
```

3. Display the task ID and status to the user

## Options

- Environment ID: Required cloud environment identifier
- Task: The task to execute remotely

## Usage Examples

```
/codex:cloud --env env123 Review this PR
/codex:cloud --env prod-env Deploy the latest changes
/codex:cloud --env test-env Run the full test suite
/codex:cloud --env dev-env Fix the failing CI pipeline
```

## Workflow

1. Create cloud task with this command
2. Task runs asynchronously in the cloud
3. Check task status with Codex CLI
4. Apply results locally with `/codex:apply`

## Notes

- Requires valid Codex Cloud environment ID
- Cloud tasks run asynchronously
- Use `/codex:apply <task_id>` to apply changes locally
- This is an experimental feature
- Ensure you have proper cloud authentication configured
