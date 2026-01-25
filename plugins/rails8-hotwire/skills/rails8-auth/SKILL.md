---
name: rails8-auth
description: Rails 8 인증, Devise, Pundit, OAuth 가이드
allowed-tools: Read, Glob, Grep
---

# Rails 8 Auth - Authentication/Authorization Skill

## Topics

- Rails 8 built-in authentication (`bin/rails generate authentication`)
- Devise setup and configuration
- Pundit authorization policies
- OmniAuth (OAuth) integration
- API token authentication
- Session management
- Two-factor authentication

## Quick Start

```bash
# Rails 8 built-in (recommended for simple apps)
bin/rails generate authentication
bin/rails db:migrate

# Or Devise (for full features)
bundle add devise
rails generate devise:install
rails generate devise User
```

## Knowledge Reference

For comprehensive documentation, see:
- **[knowledge/auth/SKILL.md](../../knowledge/auth/SKILL.md)**: Full authentication overview
- **[knowledge/auth/builtin/](../../knowledge/auth/builtin/)**: Rails 8 built-in auth details
- **[knowledge/auth/devise/](../../knowledge/auth/devise/)**: Devise configuration
- **[knowledge/auth/authorization/](../../knowledge/auth/authorization/)**: Pundit policies

## Related Agents

- `devise-specialist`: Authentication/authorization expert
- `rails-architect`: Security architecture

## Related Skills

- [rails8-controllers](../rails8-controllers/SKILL.md): Authentication filters
- [rails8-testing](../rails8-testing/SKILL.md): Policy testing
