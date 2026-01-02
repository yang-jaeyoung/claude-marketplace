---
description: View full details of a specific note
---

# View Note Command

Display the complete content and metadata of a note.

## Usage

```
/magic-note:view [note_id]
```

## Behavior

### With Note ID:

1. **Fetch Note**:
   Use `get_note` MCP tool with the provided ID

2. **Display Full Details**:
   ```
   ┌─────────────────────────────────────────────────────┐
   │ 📄 [Note Title]                                     │
   ├─────────────────────────────────────────────────────┤
   │ ID: abc123                                          │
   │ Type: plan                                          │
   │ Project: my-app                                     │
   │ Tags: auth, jwt, middleware                         │
   │ Created: 2024-01-15 10:30                           │
   │ Updated: 2024-01-16 14:22                           │
   └─────────────────────────────────────────────────────┘

   ## Content

   [Full markdown content of the note]

   ─────────────────────────────────────────────────────

   📋 Actions:
   • Edit: `/magic-note:edit abc123`
   • Copy to clipboard: `/magic-note:copy abc123`
   • Delete: `/magic-note:delete abc123`
   • Load into context: `/magic-note:load abc123`
   ```

### Without ID (Interactive):

Show recent notes for selection:
```
📚 Select a note to view:

1. abc123 - Auth Implementation Plan (plan)
2. def456 - Code Review Checklist (prompt)
3. ghi789 - Database Decision (choice)

Enter number or note ID:
```

## Error Handling

Note not found:
```
❌ Note not found: [id]

Suggestions:
• Check the ID spelling
• Use `/magic-note:list` to see all notes
• Use `/magic-note:search` to find by content
```

## Output Formatting

Format content based on note type:

**For prompts**: Show with usage hints
**For plans**: Show with progress indicators if applicable
**For choices**: Highlight the decision and rationale
