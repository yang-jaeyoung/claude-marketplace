---
description: Copy note content to clipboard or output
---

# Copy Note Command

Copy the content of a note for use elsewhere.

## Usage

```
/magic-note:copy [note_id] [optional: format]
```

## Behavior

### Basic Copy:

1. **Fetch Note**:
   Use `get_note` to retrieve content

2. **Output Content**:
   Display the full content for easy copying:
   ```
   📋 Note content copied to output:

   ───────────────────────────────────
   [Full note content]
   ───────────────────────────────────

   💡 Select and copy the content above.

   Format options:
   • `/magic-note:copy [id] markdown` - Markdown format
   • `/magic-note:copy [id] plain` - Plain text
   • `/magic-note:copy [id] full` - With metadata
   ```

### Format Options:

**markdown** (default):
```markdown
# [Note Title]

[Content in original markdown]
```

**plain**:
```
[Note Title]

[Content with markdown stripped]
```

**full** (with metadata):
```markdown
---
id: abc123
type: plan
title: [Note Title]
tags: [auth, jwt]
project: my-app
created: 2024-01-15
updated: 2024-01-16
---

[Content]
```

**json**:
```json
{
  "id": "abc123",
  "type": "plan",
  "title": "Note Title",
  "content": "...",
  "tags": ["auth", "jwt"],
  "project": "my-app"
}
```

## Examples

```
/magic-note:copy abc123
→ Outputs note content in markdown format

/magic-note:copy abc123 plain
→ Outputs plain text without markdown

/magic-note:copy abc123 full
→ Outputs with YAML frontmatter metadata

/magic-note:copy abc123 json
→ Outputs as JSON object
```

## Quick Selection

Without ID, show recent notes:
```
📚 Select a note to copy:

1. abc123 - Auth Plan (plan)
2. def456 - Review Checklist (prompt)

Enter number or ID:
```

## Clipboard Integration Note

```
📋 Content Output

Since I can't directly access your clipboard,
the content is displayed above for you to copy.

On most systems:
• macOS: Cmd+C to copy selected text
• Windows/Linux: Ctrl+C to copy selected text

For CLI users, the `mn cp [id]` command copies directly to clipboard.
```

## Use Cases

Suggest use cases based on note type:

**For prompts**:
```
💡 You can paste this prompt:
• Into another AI conversation
• Into your team's prompt library
• Into documentation
```

**For plans**:
```
💡 You can paste this plan:
• Into project management tools (Jira, Linear)
• Into documentation (Notion, Confluence)
• Into pull request descriptions
```

**For choices**:
```
💡 You can paste this decision record:
• Into ADR (Architecture Decision Record)
• Into project documentation
• Into team communication (Slack, email)
```
