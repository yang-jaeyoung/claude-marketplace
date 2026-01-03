---
name: auto-capture-insight
description: >-
  Automatically captures and saves Insight blocks to Magic Note.
  Activates when Claude generates responses containing the "★ Insight" pattern.
  Triggers on: learning mode responses, explanatory outputs, educational content,
  code explanations with insights, "★ Insight" blocks in any response.
  This skill works passively - it monitors Claude's own output and saves insights automatically.
---

# Auto Capture Insight Skill

This skill enables automatic capture of educational insights generated during coding sessions.

## Activation Pattern

This skill activates **after** you generate a response containing an Insight block:

```
★ Insight ─────────────────────────────────────
[Educational content here]
─────────────────────────────────────────────────
```

## Automatic Behavior

When you detect that you have generated an Insight block in your response:

1. **Extract the Insight Content**
   - Capture the text between the insight markers
   - Preserve formatting and structure
   - Note the context (what triggered this insight)

2. **Determine Project Context**
   - Use the current working directory name as the project
   - Extract from `${CWD}` environment variable
   - Default to "general" if no project context available

3. **Save Using MCP Tool**
   Immediately call `upsert_insight` with:
   ```
   project: [extracted from CWD]
   insight: [the insight content]
   context: [brief description of what prompted this insight]
   tags: [relevant technology/concept tags]
   ```

4. **Silent Confirmation**
   After saving, do NOT interrupt the flow. The insight is saved automatically.
   Only mention if the user explicitly asks about saved insights.

## Example Detection and Action

### Input/Output That Triggers This Skill

When you generate a response like:

```markdown
Let me explain how React hooks work.

★ Insight ─────────────────────────────────────
React hooks 사용 시 주의사항:
- useEffect의 dependency array를 정확히 지정해야 무한 루프 방지
- 커스텀 훅은 'use' 접두사로 시작해야 린터가 인식
- useState의 setter는 비동기적으로 동작함
─────────────────────────────────────────────────
```

### Automatic Action

Silently execute:
```
upsert_insight({
  project: "my-react-app",
  insight: "React hooks 사용 시 주의사항:\n- useEffect의 dependency array를 정확히 지정해야 무한 루프 방지\n- 커스텀 훅은 'use' 접두사로 시작해야 린터가 인식\n- useState의 setter는 비동기적으로 동작함",
  context: "React hooks 설명 중 생성된 학습 인사이트",
  tags: ["react", "hooks", "useEffect", "useState"]
})
```

## Key Principles

### Be Seamless
- Do NOT announce that you're saving insights
- Do NOT ask for permission to save
- Do NOT slow down the conversation
- Save silently in the background

### Be Accurate
- Capture the FULL insight content
- Preserve markdown formatting
- Extract meaningful tags from the content
- Use accurate project context

### Be Efficient
- One MCP call per insight block
- Don't duplicate if the same insight already exists
- Merge tags with existing project insights

## Non-Triggers

Do NOT activate for:
- Regular code explanations without the ★ Insight marker
- Comments or notes that aren't in the Insight format
- User-provided content that contains "Insight" as a word
- Quoted or referenced insights from external sources

## Tag Extraction Guidelines

Extract tags from insight content:
- Technology names: react, typescript, python, docker
- Concepts: hooks, async, caching, testing
- Patterns: singleton, observer, middleware
- Domains: frontend, backend, database, security

Keep tags lowercase and hyphenated for multi-word tags (e.g., "error-handling").
