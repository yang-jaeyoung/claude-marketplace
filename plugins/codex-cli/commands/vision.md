---
description: Query Codex with image context
argument-hint: "<image_path> <question>"
allowed-tools: ["Bash"]
---

# Codex Vision

Query Codex CLI with image context for visual analysis.

## Instructions

1. Parse the arguments:
   - First argument: path to the image file
   - Remaining arguments: the question about the image

2. Run Codex CLI with image input:

```bash
codex exec -i "<image_path>" -m gpt-5.2 -s read-only --skip-git-repo-check "<question>"
```

3. Display the result to the user

## Options

- Model: `gpt-5.2` (supports vision capabilities)
- Sandbox: `read-only` (safe mode)
- Image input: `-i` flag for image path

## Usage Examples

```
/codex:vision ./screenshot.png What does this UI show?
/codex:vision ./error.png Explain this error message
/codex:vision ./diagram.png Describe the architecture in this diagram
/codex:vision ./mockup.png What improvements would you suggest for this design?
```

## Supported Image Formats

- PNG
- JPEG/JPG
- GIF
- WebP

## Notes

- Image path can be absolute or relative to current directory
- Useful for analyzing screenshots, diagrams, UI mockups, error messages
- For code-specific questions about images, consider using gpt-5.2-codex by modifying the command
