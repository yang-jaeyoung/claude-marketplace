# Team Sharing Guide

Team collaboration features for sharing and merging learned instincts across team members.

## Overview

The instinct CLI now supports:
- **Comparing** local instincts with another file (`diff`)
- **Merging** instincts from another file with conflict resolution (`merge`)

## Commands

### diff - Compare Instincts

Compare your local instincts with another file to see differences.

```bash
python instinct-cli.py diff -i <remote-file.json>
```

**Options:**
- `-i, --input`: Path to the file to compare (required)
- `--summary`: Show summary only (hide details)

**Example:**
```bash
# Full diff
python instinct-cli.py diff -i teammate-instincts.json

# Summary only
python instinct-cli.py diff -i teammate-instincts.json --summary
```

**Output:**
```
============================================================
                    INSTINCT DIFF
============================================================

Only in LOCAL (1):
  - pre-commit-check-ghi11111

Only in REMOTE (1):
  - error-recovery-def67890

CONFLICTS (2):
  ID: safe-modify-pattern-xyz99999
    confidence: LOCAL=0.85, REMOTE=0.72
    evidence_count: LOCAL=12, REMOTE=8

  ID: prefer-grep-search-abc12345
    confidence: LOCAL=0.85, REMOTE=0.92
    evidence_count: LOCAL=12, REMOTE=18

IDENTICAL (0):

============================================================
```

### merge - Merge Instincts

Merge instincts from another file with automatic conflict resolution.

```bash
python instinct-cli.py merge -i <remote-file.json> [OPTIONS]
```

**Options:**
- `-i, --input`: Path to the file to merge (required)
- `-s, --strategy`: Conflict resolution strategy (default: `keep-higher`)
  - `keep-local`: Keep your version on conflict
  - `keep-remote`: Keep their version on conflict
  - `keep-higher`: Keep the version with higher confidence
- `--dry-run`: Preview changes without applying them

**Example:**
```bash
# Preview merge with keep-higher strategy
python instinct-cli.py merge -i teammate-instincts.json --dry-run

# Actually merge (default: keep-higher)
python instinct-cli.py merge -i teammate-instincts.json

# Merge and always keep remote version
python instinct-cli.py merge -i teammate-instincts.json -s keep-remote

# Merge and always keep local version
python instinct-cli.py merge -i teammate-instincts.json -s keep-local
```

**Output:**
```
============================================================
                   MERGE REPORT
============================================================

Strategy: keep-higher

Added from remote: 1
  - error-recovery-def67890 (confidence: 0.78)

Conflicts resolved: 2
  - safe-modify-pattern-xyz99999
    Kept: LOCAL (confidence: 0.85 >= 0.72)
  - prefer-grep-search-abc12345
    Kept: REMOTE (confidence: 0.92 > 0.85)

Unchanged: 1

Total instincts after merge: 4
============================================================
```

## Conflict Resolution Strategies

### keep-higher (Recommended Default)
Keeps the instinct with higher confidence score. This is best when you want the most reliable patterns.

**Use when:**
- Merging from multiple team members
- You trust confidence scores as quality indicators

**Example:**
```bash
python instinct-cli.py merge -i remote.json -s keep-higher
```

### keep-local
Always keeps your local version when there's a conflict.

**Use when:**
- You've manually reviewed and tuned your instincts
- Remote instincts are from experimentation
- You want to preserve your workflow preferences

**Example:**
```bash
python instinct-cli.py merge -i remote.json -s keep-local
```

### keep-remote
Always keeps the remote version when there's a conflict.

**Use when:**
- Remote instincts are from a senior team member
- You want to adopt team standards
- Remote has more evidence/testing

**Example:**
```bash
python instinct-cli.py merge -i remote.json -s keep-remote
```

## Team Workflow Examples

### Scenario 1: Merge from Senior Team Member

```bash
# 1. Get teammate's instincts export
# (they run: python instinct-cli.py export -o my-instincts.json)

# 2. Review differences first
python instinct-cli.py diff -i teammate-instincts.json

# 3. Dry run to preview merge
python instinct-cli.py merge -i teammate-instincts.json --dry-run

# 4. Actually merge, preferring their higher-confidence patterns
python instinct-cli.py merge -i teammate-instincts.json -s keep-higher
```

### Scenario 2: Share Your Instincts

```bash
# 1. Export your instincts
python instinct-cli.py export -o my-instincts.json

# 2. Share the JSON file with team
# (via git, Slack, email, etc.)
```

### Scenario 3: Team Consensus Building

```bash
# Collect exports from multiple team members
# member1-instincts.json, member2-instincts.json, member3-instincts.json

# Merge sequentially, keeping higher confidence
python instinct-cli.py merge -i member1-instincts.json -s keep-higher
python instinct-cli.py merge -i member2-instincts.json -s keep-higher
python instinct-cli.py merge -i member3-instincts.json -s keep-higher

# Result: You have the highest-confidence patterns from all members
```

### Scenario 4: Adopt Team Standards

```bash
# Team lead exports standardized instincts
# team-standards.json

# Everyone on team imports, preferring team standards
python instinct-cli.py merge -i team-standards.json -s keep-remote
```

## Conflict Detection

Conflicts are detected when instincts have the same ID but different:
- **confidence**: Different confidence scores
- **evidence_count**: Different observation counts
- **trigger**: Different trigger conditions
- **domain**: Different domains

## Best Practices

1. **Use `--dry-run` first**: Always preview changes before merging
2. **Review diffs**: Check what's different before deciding on a strategy
3. **Keep evidence**: Higher `evidence_count` usually means more reliable
4. **Trust confidence**: `keep-higher` is usually the best default strategy
5. **Version control**: Keep exports in git for team history
6. **Document decisions**: Note why certain instincts were promoted/demoted

## Troubleshooting

**Q: Merge keeps failing with "File not found"**
A: Ensure the input file path is correct and the file exists.

**Q: No conflicts detected but I expected some**
A: Instincts are matched by ID. If IDs are different, they're treated as separate instincts.

**Q: Wrong instinct was kept in merge**
A: Check confidence scores - `keep-higher` uses confidence, not evidence_count. Use `keep-local` if you want to preserve your version.

**Q: How do I undo a merge?**
A: Instincts are not version controlled by default. Export before merging:
```bash
python instinct-cli.py export -o backup-before-merge.json
python instinct-cli.py merge -i teammate.json
# If you need to revert:
# Delete current instincts and import backup
```

## API Reference

### detect_conflicts(local, remote)
```python
def detect_conflicts(
    local: List[Dict[str, Any]],
    remote: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Returns:
        {
            'only_local': [...],
            'only_remote': [...],
            'conflicts': [
                {
                    'id': '...',
                    'local': {...},
                    'remote': {...},
                    'diff_fields': ['confidence', 'evidence_count']
                }
            ],
            'identical': [...]
        }
    """
```

### resolve_conflict(local, remote, strategy)
```python
def resolve_conflict(
    local: Dict[str, Any],
    remote: Dict[str, Any],
    strategy: str
) -> Dict[str, Any]:
    """
    Strategy: 'keep-local', 'keep-remote', 'keep-higher'
    Returns: The chosen instinct dict
    """
```

## File Format

Instinct export files are JSON:

```json
{
  "version": "1.0",
  "exported_at": "2026-01-27T10:00:00Z",
  "instincts": [
    {
      "id": "prefer-grep-search-abc12345",
      "trigger": "when searching for code patterns",
      "action": "Use Grep instead of naive file iteration",
      "confidence": 0.92,
      "evidence_count": 18,
      "domain": "preference",
      "source": "session-observation",
      "last_observed": "2026-01-25",
      "created_at": "2026-01-20T08:00:00Z"
    }
  ]
}
```

## Future Enhancements

Potential future features:
- Interactive conflict resolution (prompt for each conflict)
- Three-way merge (base, local, remote)
- Automatic team synchronization
- Instinct versioning and history
- Merge statistics and analytics
