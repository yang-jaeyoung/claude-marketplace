---
description: Save current conversation context as a note
---

# Save Context Command

Quickly save content from the current conversation as a note.

## Usage

```
/magic-note:save [description of what to save]
```

## Behavior

This command is designed for quick saving of conversation content without leaving the flow.

### With Arguments:

When $ARGUMENTS describes what to save:

1. **Identify Content**:
   Look back in the conversation for content matching the description:
   - "the plan" → Find recent implementation plan
   - "that code review" → Find recent code review
   - "the decision about X" → Find recent decision discussion
   - "last response" → Use the most recent assistant response

2. **Auto-detect Type**:
   - Contains numbered steps/phases → `plan`
   - Contains pros/cons/decision → `choice`
   - Contains instructions/checklist → `prompt`

3. **Quick Save**:
   ```
   💾 Saving to Magic Note...

   Detected: [type] note
   Title: [auto-generated from content]

   ✅ Saved! (ID: abc123)

   Edit details? Use `/magic-note:edit abc123`
   ```

### Without Arguments (Interactive):

1. **Show Recent Saveable Content**:
   ```
   📋 What would you like to save?

   Recent content in this conversation:
   1. Implementation plan for authentication (10 min ago)
   2. Code review feedback for api.ts (25 min ago)
   3. Database technology comparison (1 hour ago)

   Enter number or describe what to save:
   ```

2. **Confirm and Save**:
   After selection, confirm before saving:
   ```
   📝 About to save:

   Type: plan
   Title: "Authentication Implementation Plan"
   Content preview: "1. Set up user model with bcrypt..."

   Save this? (yes/no/edit)
   ```

## Smart Content Detection

### Plan Detection:
- Numbered lists with action items
- Phase/step structure
- Words: implement, create, add, configure, set up

### Choice Detection:
- Comparison structure (vs, or, versus)
- Pros/cons lists
- Words: decided, chose, selected, because, rationale

### Prompt Detection:
- Instructional language
- Checklist format
- Words: check, review, ensure, verify, always

## Examples

```
/magic-note:save the implementation plan
→ Finds and saves the recent plan as type="plan"

/magic-note:save our React vs Vue discussion
→ Finds comparison, saves as type="choice"

/magic-note:save that code review checklist
→ Finds checklist, saves as type="prompt"

/magic-note:save
→ Shows interactive menu of recent saveable content
```

## Auto-Tagging

Extract tags automatically from content:
- Technology names (React, Node.js, PostgreSQL)
- Common patterns (auth, api, database, testing)
- Project context if available

## Confirmation Output

```
✅ Note saved to Magic Note!

📄 ID: abc123
📌 Type: plan
📝 Title: Authentication Implementation Plan
🏷️ Tags: auth, jwt, middleware
📁 Project: my-app

Quick actions:
- View: `/magic-note:view abc123`
- Edit: `/magic-note:edit abc123`
- Copy: `/magic-note:copy abc123`
```
