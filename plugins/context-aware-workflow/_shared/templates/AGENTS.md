# {{DIRECTORY_NAME}}

<!-- Parent: {{PARENT_PATH}} -->
<!-- Generated: {{TIMESTAMP}} -->

## Purpose

{{PURPOSE_DESCRIPTION}}

## Key Files

| File | Description |
|------|-------------|
{{#FILES}}
| `{{FILE_NAME}}` | {{FILE_DESCRIPTION}} |
{{/FILES}}

{{#HAS_SUBDIRECTORIES}}
## Subdirectories

| Directory | Purpose |
|-----------|---------|
{{#SUBDIRECTORIES}}
| `{{SUBDIR_NAME}}/` | {{SUBDIR_PURPOSE}} → See `{{SUBDIR_NAME}}/AGENTS.md` |
{{/SUBDIRECTORIES}}
{{/HAS_SUBDIRECTORIES}}

## For AI Agents

### Working In This Directory

{{WORKING_INSTRUCTIONS}}

### Dependencies

#### Internal
{{#INTERNAL_DEPS}}
- `{{DEP_PATH}}`: {{DEP_REASON}}
{{/INTERNAL_DEPS}}

#### External
{{#EXTERNAL_DEPS}}
- `{{PACKAGE_NAME}}`: {{PACKAGE_PURPOSE}}
{{/EXTERNAL_DEPS}}

{{#HAS_PATTERNS}}
### Common Patterns

{{PATTERNS_DESCRIPTION}}
{{/HAS_PATTERNS}}

{{#HAS_TESTING}}
### Testing Requirements

{{TESTING_INSTRUCTIONS}}
{{/HAS_TESTING}}

<!-- MANUAL: Notes below this line are preserved across regeneration -->
