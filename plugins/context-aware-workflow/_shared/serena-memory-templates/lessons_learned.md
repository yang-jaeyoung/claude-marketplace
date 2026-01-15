# Lessons Learned Template

Template for `lessons_learned` Serena memory.

## Structure

```markdown
# Lessons Learned

## Metadata
- **Last Updated**: YYYY-MM-DDTHH:MM:SSZ
- **Total Entries**: [N]
- **Categories**: Build, Test, Config, Pattern, Library, Runtime

## Entries

### YYYY-MM-DD: [Brief Title]

**Category**: [Build | Test | Config | Pattern | Library | Runtime]

- **Problem**: [What went wrong - 1 sentence]
- **Cause**: [Root cause analysis]
- **Solution**: [How it was fixed]
- **Prevention**: [How to avoid in future]

**Tags**: `[tag1]`, `[tag2]`

---

### YYYY-MM-DD: [Another Title]
...

## By Category

### Build Issues
- [Date]: [Title] - [1-line summary]

### Test Issues
- [Date]: [Title] - [1-line summary]

### Config Issues
- [Date]: [Title] - [1-line summary]

### Pattern Issues
- [Date]: [Title] - [1-line summary]

### Library Issues
- [Date]: [Title] - [1-line summary]

### Runtime Issues
- [Date]: [Title] - [1-line summary]

## Prevention Checklists

### Before Adding Dependencies
- [ ] Check compatibility with existing versions
- [ ] Review security advisories
- [ ] Check bundle size impact

### Before Major Refactoring
- [ ] Ensure test coverage exists
- [ ] Create rollback plan
- [ ] Update documentation

## Common Gotchas

1. **[Gotcha]**: [Quick solution]
2. **[Gotcha]**: [Quick solution]
```

## Usage

**Save (Builder)**:
```
write_memory("lessons_learned", content)
```

**Load (Any Agent)**:
```
read_memory("lessons_learned")
```

## When to Update

- Debugging took >30 minutes
- Required 3+ attempts to fix
- Unexpected behavior discovered
- Environment/config issue resolved
- Pattern violation caused error

## Retention Policy

- Keep entries for 90 days
- Archive older entries to `lessons_archive_YYYY`
- High-value entries marked `[KEEP]` are never archived
