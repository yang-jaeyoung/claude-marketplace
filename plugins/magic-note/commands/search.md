---
description: Search notes in Magic Note by content, tags, or metadata
---

# Search Notes Command

Advanced search across all notes with multiple filter options.

## Usage

```
/magic-note:search [query] [filters...]
```

## Behavior

### Basic Search:

Search across titles, content, and tags:

```
/magic-note:search authentication
```

Output:
```
🔍 Search results for "authentication":

Found 3 notes:

1. 📋 abc123 - Auth Implementation Plan
   Type: plan | Tags: auth, jwt, middleware
   Match: Title, Content (5 occurrences)
   Preview: "...implement JWT authentication with refresh tokens..."

2. 📝 def456 - Authentication Code Review Checklist
   Type: prompt | Tags: auth, security, review
   Match: Title, Tags
   Preview: "...verify authentication middleware is properly..."

3. 🎯 ghi789 - OAuth vs JWT Decision
   Type: choice | Tags: auth, oauth, jwt
   Match: Content (3 occurrences)
   Preview: "...decided to use JWT for authentication because..."

💡 Use `/magic-note:load [id]` to view full content
```

### Advanced Filters:

| Filter | Syntax | Example |
|--------|--------|---------|
| Type | `type:plan` | `type:prompt` |
| Project | `project:name` | `project:my-app` |
| Tag | `tag:name` or `#name` | `#auth` |
| Date | `after:date` `before:date` | `after:2024-01-01` |
| Content only | `content:term` | `content:jwt` |
| Title only | `title:term` | `title:review` |

### Combined Search Examples:

```
/magic-note:search type:prompt #review
→ All prompts tagged with "review"

/magic-note:search project:my-app type:plan
→ All plans for "my-app" project

/magic-note:search jwt auth after:2024-01-01
→ Notes about jwt/auth created this year

/magic-note:search title:checklist type:prompt
→ Prompts with "checklist" in title
```

## Implementation

1. **Parse Query**:
   - Extract filter keywords (type:, project:, #, etc.)
   - Remaining text is the search query

2. **Execute Search**:
   Use `list_notes` MCP tool with:
   ```
   type: [extracted type filter]
   project: [extracted project filter]
   tags: [extracted tags array]
   search: [remaining search terms]
   ```

3. **Rank Results**:
   Sort by relevance:
   - Title match (highest)
   - Tag match (high)
   - Content match (by occurrence count)

4. **Display Results**:
   Show formatted results with previews

## Search Tips

Show tips when no results or few results:
```
💡 Search tips:
- Use quotes for exact phrases: "code review"
- Combine filters: type:prompt #api
- Try broader terms if no results
- Use `/magic-note:list` to browse all notes
```

## Empty Results:

```
🔍 No notes found for "[query]"

Suggestions:
- Check spelling
- Try related terms: [suggested alternatives]
- Browse by type: `/magic-note:list prompts`
- Browse by tag: `/magic-note:list #[common-tag]`
```

## Quick Actions on Results:

After showing results:
```
Quick actions:
- Enter note number (1-3) to load
- `/magic-note:load [id]` for specific note
- Refine search with additional filters
```

## Statistics:

Show search statistics:
```
📊 Search stats:
- Total notes searched: 25
- Matches found: 3
- Search time: <1s
- Most relevant: abc123 (5 content matches)
```

## Interactive Mode:

Without arguments, enter interactive search:
```
/magic-note:search

🔍 Enter search query (or 'help' for tips):
> _

Recent searches:
- authentication (3 results)
- api design (2 results)
- #react (5 results)
```
