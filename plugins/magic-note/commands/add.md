---
description: Add a new note to Magic Note
allowed-tools: ["mcp__magic-note__add_note", "mcp__magic-note__list_templates", "mcp__magic-note__use_template"]
---

# Add Note Command

Help the user create and save a new note to Magic Note.

## Usage

```
/magic-note:add [optional: note content or title]
```

## Behavior

### If $ARGUMENTS is provided:
Use the argument as initial content or title hint.

### Interactive Flow:

1. **Determine Note Type**:
   Ask the user:
   ```
   What type of note would you like to create?
   1. 📝 prompt - Reusable AI prompt
   2. 📋 plan - Implementation plan or strategy
   3. 🎯 choice - Technical decision record
   ```

2. **Get Title**:
   If not provided in arguments, ask:
   ```
   What's the title for this note?
   ```

3. **Get Content**:
   If not provided, ask:
   ```
   Enter the note content (or describe what you want to save):
   ```

   For multi-line content, offer:
   ```
   Would you like to:
   a) Type the content directly
   b) Paste from a previous message in our conversation
   c) Let me help structure the content based on the type
   ```

4. **Optional Metadata**:
   ```
   Any tags to add? (comma-separated, or press Enter to skip)
   Project name? (or press Enter to skip)
   ```

5. **Save the Note**:
   Use the `add_note` MCP tool:
   ```
   type: [selected type]
   title: [provided title]
   content: [provided content]
   tags: [optional tags array]
   project: [optional project name]
   ```

6. **Confirm Success**:
   ```
   ✅ Note saved successfully!

   📄 ID: [note_id]
   📌 Type: [type]
   🏷️ Tags: [tags]

   Use `/magic-note:view [id]` to see it anytime.
   ```

## Quick Add Examples

```
/magic-note:add
→ Starts interactive flow

/magic-note:add My code review checklist
→ Uses "My code review checklist" as title, asks for type and content

/magic-note:add Save the authentication plan we just discussed
→ Searches recent conversation for plan content, asks for confirmation
```

## Content Templates by Type

### For prompt type:
```markdown
## Purpose
[What this prompt accomplishes]

## Instructions
[The actual prompt content]

## Usage Context
[When to use this prompt]
```

### For plan type:
```markdown
## Objective
[What this plan achieves]

## Steps
1. [Step 1]
2. [Step 2]
...

## Considerations
[Important notes or dependencies]
```

### For choice type:
```markdown
## Decision
[What was decided]

## Options Considered
- Option A: [description]
- Option B: [description]

## Rationale
[Why this choice was made]
```
