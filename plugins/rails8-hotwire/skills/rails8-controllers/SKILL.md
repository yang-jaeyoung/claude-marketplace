---
name: rails8-controllers
description: RESTful 컨트롤러, 서비스 객체 통합, 응답 처리 가이드
allowed-tools: Read, Glob, Grep
---

# Rails 8 Controllers - Controller Patterns Skill

## Topics

- RESTful actions (7 standard actions)
- Strong Parameters
- Response formats (HTML, Turbo Stream, JSON)
- Filters (before_action, etc.)
- Service object integration
- Error handling
- Pagination

## Critical: Turbo-Compatible Status Codes

| Scenario | Status Code |
|----------|-------------|
| Redirect after success | `status: :see_other` (303) |
| Form validation errors | `status: :unprocessable_entity` (422) |

## Knowledge Reference

For comprehensive documentation, see:
- **[knowledge/controllers/SKILL.md](../../knowledge/controllers/SKILL.md)**: Full controller patterns, responses, and API design

## Related Agents

- `rails-executor`: Controller implementation
- `rails-architect`: Architecture decisions

## Related Skills

- [rails8-turbo](../rails8-turbo/SKILL.md): Turbo Stream responses
- [rails8-models](../rails8-models/SKILL.md): Query objects
- [rails8-auth](../rails8-auth/SKILL.md): Authentication filters
