---
description: Web search using Google Search Grounding
argument-hint: "<query>"
allowed-tools: ["Bash"]
---

# Gemini Search

Perform web search using Google Search Grounding.

## Instructions

1. Get the user query from arguments
2. Run Gemini CLI with web search prompt:

```bash
gemini -p "Perform a web search for the following question and answer based on the search results.
Always include source URLs.

Question: <user_query>"
```

3. Display the search results to the user

## Output Format

- Search results summary
- Key information
- Source URLs list

## Usage Examples

```
/gemini:search jQuery 4 release date 2026
/gemini:search latest React 19 features
/gemini:search Claude Code plugins documentation
```

## Notes

- Gemini automatically activates Search Grounding when web search is requested in prompt
- Free tier limit: 1,500 queries/day
- Suitable when real-time information and LLM analysis are both needed
- For complex research, consider combining with `/research` command
