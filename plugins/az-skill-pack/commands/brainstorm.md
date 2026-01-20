---
description: Start a structured brainstorming session using techniques like SCAMPER, Six Thinking Hats, or Divergent Expansion
argument-hint: "[topic]"
allowed-tools: Read, Write, Glob
---

# Brainstorm Command

Start a creative brainstorming session for the given topic.

## Instructions

1. If a topic is provided, use it directly. If not, ask the user what they want to brainstorm about.

2. Load the brainstorm skill knowledge from `${CLAUDE_PLUGIN_ROOT}/skills/brainstorm/SKILL.md`

3. Select the most appropriate technique based on context:
   - **Divergent Expansion**: For open-ended exploration (default)
   - **SCAMPER**: For improving existing solutions
   - **Six Thinking Hats**: For complex decision-making
   - **Rapid Fire**: When maximum creativity is needed

4. Apply the selected technique and generate 8-15 diverse ideas

5. Organize output using visual formatting (tables, categories, or bullet lists)

6. Offer to:
   - Expand on any promising ideas
   - Apply a different technique
   - Combine or refine ideas

## Usage Examples

```
/az:brainstorm marketing strategies for new product
/az:brainstorm how to improve team productivity
/az:brainstorm
```

## Advanced Techniques

For specialized scenarios, refer to `${CLAUDE_PLUGIN_ROOT}/skills/brainstorm/references/techniques.md`:
- Reverse Brainstorming
- Starbursting
- Mind Mapping
- Attribute Listing
- Random Word Association
