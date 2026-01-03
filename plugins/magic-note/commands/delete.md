---
description: Delete a note from Magic Note
allowed-tools: ["mcp__magic-note__get_note", "mcp__magic-note__delete_note"]
---

# Delete Note Command

Remove a note from Magic Note permanently.

## Usage

```
/magic-note:delete [note_id]
```

## Behavior

### With Note ID:

1. **Fetch Note Details**:
   Show what will be deleted

2. **Confirm Deletion**:
   ```
   ⚠️ Delete Note?

   📄 Title: [Note Title]
   📌 Type: [type]
   🏷️ Tags: [tags]
   📁 Project: [project]
   📅 Created: [date]

   Content preview:
   "[first 100 characters...]"

   ⚠️ This action cannot be undone.

   Type 'yes' to confirm deletion:
   ```

3. **Execute Deletion**:
   Use `delete_note` MCP tool

4. **Confirm Success**:
   ```
   🗑️ Note deleted successfully.

   Deleted: "[Note Title]" (ID: abc123)

   💡 Tip: Use `/magic-note:list` to see remaining notes.
   ```

### Without ID:

Show notes for selection:
```
📚 Select a note to delete:

1. abc123 - Old Implementation Plan (plan) - 30 days old
2. def456 - Unused Prompt (prompt) - 45 days old

Enter note number or ID (or 'cancel' to abort):
```

## Safety Features

### Double Confirmation for Important Notes:

For notes with many tags or recent updates:
```
⚠️ This note has been updated recently and has multiple tags.
Are you sure you want to delete it?

Type the note title to confirm: [Note Title]
```

### Bulk Delete Protection:

If user tries to delete multiple notes:
```
⚠️ Bulk deletion is not supported for safety.
Please delete notes one at a time.
```

## Error Handling

Note not found:
```
❌ Note not found: [id]

The note may have already been deleted.
Use `/magic-note:list` to see existing notes.
```

## Alternative Actions

Before deletion, suggest alternatives:
```
💡 Instead of deleting, you could:
• Archive: `/magic-note:edit [id] add tag:archived`
• Move: `/magic-note:edit [id] project:archive`
• Export first: `/magic-note:export [id]`

Still want to delete? (yes/no)
```
