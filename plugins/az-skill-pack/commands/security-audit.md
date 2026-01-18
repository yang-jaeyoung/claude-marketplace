---
name: az:security-audit
description: Run a comprehensive security audit on the codebase, detecting project type and applying appropriate checks
argument-hint: "[scope] [--severity=level] [--format=type] [--fix] [--path=dir]"
allowed-tools: Read, Grep, Glob, Bash
---

# Security Audit Command

Perform a security audit on the codebase with automatic project detection and framework-specific checks.

## Arguments

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `scope` | `full`, `error`, `auth`, `data`, `api`, `deps`, `config` | `full` | Audit scope |
| `--severity` | `critical`, `high`, `medium`, `low` | `medium` | Minimum severity to report |
| `--format` | `table`, `report`, `checklist` | `table` | Output format |
| `--fix` | flag | `false` | Include fix code examples |
| `--path` | directory | `.` | Target directory |

## Instructions

1. **Project Detection Phase**
   - Detect project type from config files (package.json, *.csproj, Cargo.toml, go.mod, etc.)
   - Identify framework (Next.js, ASP.NET Core, Django, Spring Boot, etc.)
   - Load appropriate security checklist from skill

2. **Load Security Checklist**
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/security-audit/SKILL.md` for full checklist
   - Filter by requested scope and severity

3. **Execute Security Checks**
   By scope:
   - `error`: Error handling, logging, stack traces
   - `auth`: Authentication, password hashing, JWT, sessions
   - `data`: Encryption, secret management, masking
   - `api`: HTTPS, CORS, rate limiting, headers
   - `deps`: Dependency vulnerabilities, lock files
   - `config`: Security headers, cookie settings

4. **Generate Report**
   Use status icons: ✅ Implemented | ⚠️ Partial | ❌ Missing | 🔍 Manual check | ➖ N/A

   Include severity: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low

5. **Priority Actions**
   List critical and high severity issues with file locations and recommended fixes

## Usage Examples

```
/az:security-audit
/az:security-audit auth --severity=critical
/az:security-audit deps --fix
/az:security-audit full --format=report --path=./src
```

## Output Template

```markdown
## Summary
| Category | ✅ | ⚠️ | ❌ | Score |
|----------|---|---|---|-------|

## [Category Name]
| ID | Item | Status | Severity | Location |

## Priority Actions
### 🔴 Critical
| ID | Item | Location | Fix |
```
