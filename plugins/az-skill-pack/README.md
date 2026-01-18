# Claude Skills Plugin

A collection of specialized skills for Claude Code covering brainstorming, code conventions, security audits, documentation generation, and project analysis.

## Installation

```bash
# Install from marketplace
claude plugins add github:jyyang/claude-marketplace
```

## Skills

| Skill | Description | Language |
|-------|-------------|----------|
| **brainstorm** | Creative ideation using SCAMPER, Six Thinking Hats, Divergent Expansion | EN |
| **csharp-convention** | Microsoft C# coding conventions | KR |
| **csharp-security** | NIST/OWASP secure coding for C# | KR |
| **reverse-engineering-docs** | Generate 7 types of project documentation from codebase | KR |
| **security-audit** | Universal security audit for any framework | KR |
| **vue-project-analyzer** | Vue.js project structure analysis and documentation | KR |

## Commands

### `/az:brainstorm [topic]`

Start a structured brainstorming session.

```bash
/az:brainstorm marketing strategies for new product
/az:brainstorm how to improve team productivity
```

### `/az:security-audit [scope] [options]`

Run a comprehensive security audit.

**Options:**
- `scope`: `full`, `error`, `auth`, `data`, `api`, `deps`, `config`
- `--severity`: `critical`, `high`, `medium`, `low`
- `--format`: `table`, `report`, `checklist`
- `--fix`: Include fix examples
- `--path`: Target directory

```bash
/az:security-audit
/az:security-audit auth --severity=critical
/az:security-audit deps --fix
```

### `/az:reverse-engineer-docs [type] [--output=format]`

Generate project documentation from codebase.

**Types:** `all`, `requirements`, `functional`, `usecase`, `architecture`, `ui`, `database`, `operations`

```bash
/az:reverse-engineer-docs
/az:reverse-engineer-docs architecture
/az:reverse-engineer-docs database --output=docx
```

### `/az:analyze-vue`

Analyze Vue.js project structure and generate documentation.

```bash
/az:analyze-vue
```

## Project Structure

```
az-skill-pack/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── brainstorm.md
│   ├── security-audit.md
│   ├── reverse-engineer-docs.md
│   └── analyze-vue.md
├── skills/
│   ├── brainstorm/
│   ├── csharp-convention/
│   ├── csharp-security/
│   ├── reverse-engineering-docs/
│   ├── security-audit/
│   └── vue-project-analyzer/
└── README.md
```

## License

MIT
