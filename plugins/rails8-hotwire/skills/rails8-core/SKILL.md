# rails8-core

Rails 8 Project Setup and Structure Skill

## Invocation
`/rails8:core`

## Description
Guides Rails 8 project initial setup, directory structure, Gem configuration, and environment setup.

## Topics
- Rails 8 new project creation
- Solid Trifecta setup (Queue, Cache, Cable)
- Propshaft + Import Maps configuration
- Environment-specific settings (development, test, production)
- Directory structure and conventions
- Service/Form/Query object patterns

## Commands
```bash
rails new myapp --database=postgresql --css=tailwind
bin/rails generate authentication
```

## Knowledge Reference
For comprehensive documentation, see:
- **[knowledge/core/SKILL.md](../../knowledge/core/SKILL.md)**: Full setup guide, patterns, and best practices

## Related Agents
- `rails-architect`: Architecture decisions
- `rails-executor`: Implementation

## Related Skills
- [rails8-models](../rails8-models/SKILL.md): Model patterns
- [rails8-hotwire](../rails8-turbo/SKILL.md): Turbo/Stimulus setup
- [rails8-auth](../rails8-auth/SKILL.md): Authentication setup
