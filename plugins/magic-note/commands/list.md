---
description: List notes from Magic Note with optional filtering
allowed-tools: ["mcp__magic-note__list_notes", "mcp__magic-note__list_tags", "mcp__magic-note__list_projects"]
---

# List Notes Command

Display a list of saved notes with optional filtering.

## Usage

```
/magic-note:list [optional: filter criteria]
```

## Behavior

### Basic List (no arguments):
Show all notes in a formatted table:

```
📚 Magic Note Library

| ID      | Type   | Title                        | Tags            | Updated    |
|---------|--------|------------------------------|-----------------|------------|
| abc123  | prompt | Code Review Checklist        | review, api     | 2 days ago |
| def456  | plan   | Auth Implementation Plan     | auth, jwt       | 1 week ago |
| ghi789  | choice | Database Selection           | db, postgres    | 3 days ago |

Total: 3 notes
```

### Filtered List:

Parse $ARGUMENTS for filter keywords:

| Argument Pattern | Filter Applied |
|------------------|----------------|
| `prompts` or `type:prompt` | type="prompt" |
| `plans` or `type:plan` | type="plan" |
| `choices` or `type:choice` | type="choice" |
| `project:name` | project="name" |
| `tag:tagname` | tags contains "tagname" |
| `#tagname` | tags contains "tagname" |
| Any other text | search in title/tags |

### Examples:

```
/magic-note:list
→ Shows all notes

/magic-note:list prompts
→ Shows only prompt-type notes

/magic-note:list project:my-app
→ Shows notes for "my-app" project

/magic-note:list #auth
→ Shows notes tagged with "auth"

/magic-note:list api review
→ Searches for notes matching "api" or "review"
```

## Implementation

1. **Parse Filters**:
   Extract filter criteria from $ARGUMENTS

2. **Call MCP Tool**:
   Use `list_notes` with appropriate parameters:
   ```
   type: [optional filter]
   project: [optional filter]
   tags: [optional filter array]
   search: [optional search term]
   ```

3. **Format Output**:
   Display results in a readable table format

4. **Empty Results**:
   If no notes found:
   ```
   📭 No notes found matching your criteria.

   Tips:
   - Use `/magic-note:add` to create your first note
   - Try broader search terms
   - Check available filters: prompts, plans, choices, #tag, project:name
   ```

5. **Offer Actions**:
   After listing, suggest:
   ```
   💡 Quick actions:
   - `/magic-note:view [id]` - View note details
   - `/magic-note:load [id]` - Load note into context
   - `/magic-note:add` - Create new note
   ```

## Summary Statistics

When showing all notes, include summary:
```
📊 Summary:
- Prompts: 5
- Plans: 3
- Choices: 2
- Projects: 4
- Most used tags: auth (3), api (2), react (2)
```
