# Gemini CLI Plugin

Google Gemini CLI integration for Claude Code - leveraging Gemini AI for code review, commit messages, documentation, and more.

## Prerequisites

### 1. Install Gemini CLI

```bash
# macOS (Homebrew)
brew install google-gemini/tap/gemini-cli

# Or via npm
npm install -g @anthropic-ai/gemini-cli
```

### 2. Authenticate

```bash
gemini auth login
```

Follow the prompts to authenticate with your Google account.

### 3. Verify Installation

```bash
gemini --version
```

## Available Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/gemini:ask` | Ask Gemini a general question | `/gemini:ask <question>` |
| `/gemini:review` | Run code review on staged changes or a file | `/gemini:review [file]` |
| `/gemini:commit` | Generate commit message from staged changes | `/gemini:commit` |
| `/gemini:docs` | Generate documentation for a file | `/gemini:docs <file>` |
| `/gemini:release` | Generate release notes from git commits | `/gemini:release <from-tag>` |

## Command Details

### `/gemini:ask`

Ask Gemini any question using headless mode.

```bash
/gemini:ask What is machine learning?
/gemini:ask Explain the difference between REST and GraphQL
```

### `/gemini:review`

Run code review on your changes.

```bash
# Review staged changes
/gemini:review

# Review a specific file
/gemini:review src/auth.py
```

Reviews focus on:
- Bugs and logic errors
- Security vulnerabilities
- Code quality and best practices

### `/gemini:commit`

Generate a commit message from staged changes.

```bash
# Stage your changes first
git add .

# Generate commit message
/gemini:commit
```

Output follows conventional commit format:
```
feat(auth): add OAuth2 support for Google login

- Add OAuth2 flow implementation
- Add token refresh logic
- Update user model with provider field
```

### `/gemini:docs`

Generate comprehensive documentation for a file.

```bash
/gemini:docs src/utils.py
/gemini:docs api/routes.js
```

Documentation includes:
- Overview and purpose
- Function/class descriptions
- Parameter and return value documentation
- Usage examples

### `/gemini:release`

Generate release notes from git commit history.

```bash
# From a specific tag
/gemini:release v1.0.0

# From the most recent tag (auto-detected)
/gemini:release
```

Release notes include:
- Summary of changes
- Features
- Bug Fixes
- Improvements
- Breaking Changes

## Configuration

Gemini CLI configuration is managed through the `gemini` CLI tool:

```bash
# Set default model
gemini config set model gemini-2.0-flash

# View current config
gemini config show
```

## Installation

Install this plugin in Claude Code:

```bash
claude plugins add github:jyyang/claude-marketplace --subpath plugins/gemini-cli
```

Or if you have the full marketplace:

```bash
claude plugins add github:jyyang/claude-marketplace
```

## Troubleshooting

### "gemini: command not found"

Ensure Gemini CLI is installed and in your PATH:

```bash
which gemini
```

### Authentication errors

Re-authenticate with Gemini:

```bash
gemini auth logout
gemini auth login
```

### No output from commands

Check that you have an active internet connection and valid API quota.

## License

MIT
