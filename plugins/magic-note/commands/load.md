---
description: Load a note's content into the current conversation context
---

# Load Note Command

Load a saved note into the current conversation for reference or use.

## Usage

```
/magic-note:load [note_id or search term]
```

## Behavior

### With Note ID:

If $ARGUMENTS looks like a note ID (short alphanumeric string):

1. **Fetch Note**:
   Use `get_note` MCP tool with the ID

2. **Display Content**:
   ```
   📄 Loaded: [Note Title]

   Type: [type] | Tags: [tags] | Project: [project]
   Created: [date] | Updated: [date]

   ───────────────────────────────────
   [Full note content in markdown]
   ───────────────────────────────────

   💡 This note is now in context. How would you like to use it?
   ```

3. **Offer Actions Based on Type**:

   For **prompt** type:
   ```
   🎯 This is a saved prompt. Would you like me to:
   a) Apply this prompt to your current task
   b) Modify this prompt for a specific use
   c) Just keep it as reference
   ```

   For **plan** type:
   ```
   📋 This is a saved plan. Would you like me to:
   a) Review progress against this plan
   b) Update this plan with new information
   c) Start implementing from a specific step
   ```

   For **choice** type:
   ```
   🎯 This is a decision record. Would you like me to:
   a) Explain the rationale in more detail
   b) Revisit this decision with new context
   c) Just keep it as reference
   ```

### With Search Term:

If $ARGUMENTS is not a valid ID, search for matching notes:

1. **Search Notes**:
   Use `list_notes` with search parameter

2. **Show Matches**:
   ```
   🔍 Found notes matching "[search term]":

   1. abc123 - Code Review Checklist (prompt)
   2. def456 - API Review Guidelines (prompt)

   Enter number to load, or be more specific:
   ```

3. **Load Selected**:
   After selection, load the full note

### Without Arguments:

Show recent notes for quick selection:
```
📚 Recent Notes:

1. abc123 - Auth Implementation Plan (plan) - 2 hours ago
2. def456 - Database Selection (choice) - 1 day ago
3. ghi789 - Code Review Checklist (prompt) - 3 days ago

Enter number or note ID to load:
```

## Examples

```
/magic-note:load abc123
→ Directly loads note with ID abc123

/magic-note:load auth plan
→ Searches for notes matching "auth plan", shows matches

/magic-note:load
→ Shows recent notes for selection

/magic-note:load my code review prompt
→ Searches and loads matching prompt
```

## Context Integration

After loading a note, it becomes part of the conversation context:

- **Prompts**: Can be applied to current tasks
- **Plans**: Can guide implementation discussions
- **Choices**: Provide context for related decisions

## Multiple Note Loading

For loading multiple related notes:
```
/magic-note:load project:my-app
→ Shows all notes for project, allows batch loading

📚 Notes for project "my-app":
1. Auth Plan
2. API Design
3. Tech Stack Decision

Load all? (yes/no/select specific)
```

## Error Handling

If note not found:
```
❌ Note not found: [id or search term]

Did you mean one of these?
- abc124 - Similar Note Title
- abc125 - Another Similar Note

Or use `/magic-note:list` to browse all notes.
```
