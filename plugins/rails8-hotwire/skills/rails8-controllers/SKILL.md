# rails8-controllers

Controller Patterns Skill

## Invocation
`/rails8:controllers`

## Description
Guides RESTful controllers, service object integration, and response handling.

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
