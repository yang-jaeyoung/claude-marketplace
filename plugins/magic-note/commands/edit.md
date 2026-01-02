---
description: Edit an existing note's content or metadata
---

# Edit Note Command

Modify the content, title, tags, or other metadata of an existing note.

## Usage

```
/magic-note:edit [note_id] [optional: what to edit]
```

## Behavior

### Basic Edit (ID only):

1. **Load Current Note**:
   Use `get_note` to fetch current content

2. **Show Current State**:
   ```
   📝 Editing: [Note Title]

   Current content:
   ───────────────────────────────────
   [current content preview]
   ───────────────────────────────────

   What would you like to edit?
   1. Title
   2. Content
   3. Tags
   4. Type
   5. Project

   Enter number or describe changes:
   ```

3. **Apply Changes**:
   Use `update_note` MCP tool with modified fields

4. **Confirm**:
   ```
   ✅ Note updated!

   Changes:
   - Title: "Old Title" → "New Title"
   - Tags: Added "new-tag"

   View updated note? `/magic-note:view [id]`
   ```

### Quick Edit (with description):

```
/magic-note:edit abc123 add tag:security
→ Adds "security" tag to note abc123

/magic-note:edit abc123 change title to "Updated Plan"
→ Updates the title

/magic-note:edit abc123 append "Step 5: Deploy to production"
→ Appends content to the note
```

### Edit Operations:

| Command | Action |
|---------|--------|
| `add tag:name` | Add a tag |
| `remove tag:name` | Remove a tag |
| `title:new title` | Change title |
| `type:plan` | Change type |
| `project:name` | Change project |
| `append [content]` | Add to end |
| `prepend [content]` | Add to beginning |

## Interactive Content Editing

For content changes:
```
Current content will be shown. How would you like to edit?

1. Replace entirely - I'll provide new content
2. Append - Add to the end
3. Modify section - Edit a specific part
4. AI-assisted - Describe changes to make

Choice:
```

For AI-assisted editing:
```
Describe the changes you want:
> "Add error handling considerations to the plan"

Preview of changes:
[Show diff or preview]

Apply these changes? (yes/no/modify)
```

## Metadata Editing

Tags management:
```
Current tags: [auth, jwt]

Options:
1. Add tags: tag1, tag2
2. Remove tags: tag1
3. Replace all: tag1, tag2, tag3

Enter choice:
```

## Error Handling

```
❌ Cannot edit note: [reason]

Common issues:
• Note ID not found
• Invalid tag format
• Type must be: prompt, plan, or choice
```
