---
name: rails8-core
description: Rails 8 프로젝트 초기 설정, 디렉토리 구조, Gem 설정, 환경 설정 가이드
allowed-tools: Read, Glob, Grep, Bash
---

# Rails 8 Core - Project Setup and Structure

## Topics

- Rails 8 new project creation
- Solid Trifecta setup (Queue, Cache, Cable)
- Propshaft + Import Maps configuration
- Environment-specific settings (development, test, production)
- Directory structure and conventions
- Service/Form/Query object patterns

## Quick Start

```bash
# Create Rails 8 project
rails new myapp --database=postgresql --css=tailwind --skip-jbuilder

# Built-in authentication (Rails 8)
bin/rails generate authentication
bin/rails db:migrate
```

## Solid Trifecta (Rails 8 Default)

- **Solid Queue**: DB-based job queue (replaces Redis/Sidekiq)
- **Solid Cache**: DB-based cache store
- **Solid Cable**: DB-based WebSocket Pub/Sub

## Knowledge Reference

For comprehensive documentation, see:
- **[knowledge/core/SKILL.md](../../knowledge/core/SKILL.md)**: Full setup guide, patterns, and best practices

## Related Agents

- `rails-architect`: Architecture decisions
- `rails-executor`: Implementation

## Related Skills

- [rails8-models](../rails8-models/SKILL.md): Model patterns
- [rails8-turbo](../rails8-turbo/SKILL.md): Turbo/Stimulus setup
- [rails8-auth](../rails8-auth/SKILL.md): Authentication setup
