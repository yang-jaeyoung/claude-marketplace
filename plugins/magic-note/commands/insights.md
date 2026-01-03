---
name: insights
description: View collected insights for a project
argument-hint: "[project-name]"
allowed-tools:
  - mcp__plugin_magic-note_magic-note__list_notes
  - mcp__plugin_magic-note_magic-note__get_note
---

# View Project Insights Command

Display insights collected for a specific project or all projects.

## Usage

```
/magic-note:insights [optional: project-name]
```

## Behavior

### With Project Name:

1. Call `list_notes` MCP tool with:
   - type: "insight"
   - project: [provided project name]

2. If insight note found, call `get_note` to retrieve full content

3. Display formatted output:
   ```
   💡 [Project Name] Insights

   Total insights: N
   Last updated: [date]
   Tags: [tag list]

   ---

   [Full insight content with timestamps]
   ```

### Without Project Name (Current Project):

1. Extract project name from current working directory
2. Follow same process as above

### No Insights Found:

```
📭 No insights found for project: [project-name]

Insights are automatically captured when Claude generates educational content
using the ★ Insight format in learning/explanatory mode.

To manually add an insight:
/magic-note:add --type insight "Your insight content"
```

## All Insights View

If user specifies "all" or "--all":

```
/magic-note:insights all
```

List all insight notes across all projects:

```
💡 All Project Insights

| Project | Insights | Last Updated | Top Tags |
|---------|----------|--------------|----------|
| my-app  | 12       | 2 hours ago  | react, hooks |
| api-srv | 5        | 1 day ago    | nodejs, express |

Use `/magic-note:insights [project]` to view specific project insights.
```

## Quick Actions

After displaying insights, suggest:
```
💡 Quick actions:
- `/magic-note:insights all` - View all projects
- `/magic-note:view [id]` - View full note details
- `/magic-note:edit [id]` - Edit insight note
```
