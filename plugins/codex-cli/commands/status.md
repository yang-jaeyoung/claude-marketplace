---
description: Check Codex CLI authentication status
allowed-tools: ["Bash"]
---

# Codex Status

Check Codex CLI authentication and configuration status.

## Instructions

1. Run the Codex status command:

```bash
codex auth status
```

2. Display the authentication status to the user

## Output

The command shows:
- Authentication status (logged in/out)
- Current user/account
- API endpoint
- Token expiration (if applicable)

## Usage Examples

```
/codex:status
```

## Related Commands

- `codex auth login` - Log in to Codex
- `codex auth logout` - Log out from Codex
- `codex auth refresh` - Refresh authentication token

## Notes

- Useful for troubleshooting authentication issues
- Shows current API configuration
- Run before using cloud features
