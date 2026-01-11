# Insight Collection

## Trigger Conditions

| Trigger | Example |
|---------|---------|
| Effective pattern found | Elegant solution to specific problem |
| Library usage tip | Undocumented useful feature |
| Performance optimization | Benchmarked improvement method |
| Test strategy | Effective test pattern |

## Capture Format

```
★ Insight ─────────────────────────────────────
[Pattern/technique description 2-3 lines]
─────────────────────────────────────────────────

Write → .caw/insights/{YYYYMMDD}-{slug}.md
💡 Insight saved: [title]
```

## Storage Template

```markdown
# Insight: [Title]

## Metadata
| Field | Value |
|-------|-------|
| **Captured** | [timestamp] |
| **Context** | [phase/step description] |

## Content
[Insight content]

## Tags
#implementation #[technology]
```

## Insight vs Lessons Learned

| Aspect | Insight | Lessons Learned |
|--------|---------|-----------------|
| Location | `.caw/insights/*.md` | `CLAUDE.md` |
| Content | Code patterns, techniques | Problem-solving experiences |
| Scope | Project/session | Permanent knowledge |
