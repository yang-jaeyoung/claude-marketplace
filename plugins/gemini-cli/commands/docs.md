---
description: Generate documentation for code using Gemini
argument-hint: "<file>"
allowed-tools: ["Bash"]
---

# Gemini Docs

Generate comprehensive documentation for code using Google Gemini CLI.

## Instructions

1. Get the file path from arguments
2. If no file specified, inform the user and exit
3. Run Gemini CLI to generate documentation:

```bash
cat <file> | gemini -p "Generate comprehensive documentation for this code. Include: 1) Overview and purpose, 2) Function/class descriptions with parameters and return values, 3) Usage examples, 4) Important notes or caveats. Use markdown format."
```

4. Display the generated documentation to the user

## Options

- Mode: Headless (`-p` flag for prompt)
- Input: File contents piped to Gemini
- Output: Markdown formatted documentation

## Usage Examples

```
/gemini:docs src/utils.py
/gemini:docs api/routes.js
/gemini:docs lib/auth.ts
```

## Output Format

The generated documentation will include:

- **Overview**: Brief description of the file's purpose
- **Functions/Classes**: Detailed descriptions with parameters and return values
- **Usage Examples**: Practical code examples
- **Notes**: Important caveats or considerations

## Notes

- Provide a valid file path as argument
- The output is in markdown format for easy integration
- For code review, use `/gemini:review`
- For commit messages, use `/gemini:commit`
