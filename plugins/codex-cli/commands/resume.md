---
description: Resume previous Codex CLI session
argument-hint: "[session_id | --last]"
allowed-tools: ["Bash"]
---

# Codex Resume

Resume a previous Codex CLI session for continued conversation.

## Instructions

1. Check the arguments:
   - If `--last` is provided, resume the most recent session
   - If a session ID is provided, resume that specific session
   - If no arguments, list available sessions

2. Run the appropriate Codex CLI command:

**List sessions (no arguments):**
```bash
codex sessions list
```

**Resume last session:**
```bash
codex resume --last
```

**Resume specific session:**
```bash
codex resume <session_id>
```

3. Display the result to the user

## Options

- Session ID: The ID of a previous session to resume
- `--last`: Resume the most recent session

## Usage Examples

```
/codex:resume
/codex:resume --last
/codex:resume session_abc123
```

## Notes

- Session history allows continuing multi-turn conversations
- Sessions include context from previous interactions
- Use session list to find specific session IDs
