---
name: rails8-models
description: ActiveRecord 모델, 관계, 쿼리, 유효성 검사 가이드
allowed-tools: Read, Glob, Grep
---

# Rails 8 Models - ActiveRecord Model Skill

## Topics

- Model definition and associations (has_many, belongs_to, etc.)
- Validations
- Callbacks
- Scopes
- Enums
- Query optimization
- N+1 problem resolution

## Key Patterns

- Eager loading with `includes`
- Query objects for complex queries
- Concerns for shared behavior
- Soft delete implementation

## Knowledge Reference

For comprehensive documentation, see:
- **[knowledge/models/SKILL.md](../../knowledge/models/SKILL.md)**: Full model patterns, validations, and query optimization

## Related Agents

- `activerecord-optimizer`: Query optimization
- `rails-migrator`: Database migrations
- `rails-executor`: Model implementation

## Related Skills

- [rails8-core](../rails8-core/SKILL.md): Service/Query objects
- [rails8-controllers](../rails8-controllers/SKILL.md): Using query results
- [rails8-testing](../rails8-testing/SKILL.md): Model testing
