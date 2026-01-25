---
name: rails8-hotwire
description: Rails 8 + Hotwire 풀스택 웹 개발 가이드. 프로젝트 생성부터 Turbo/Stimulus, 모델, 컨트롤러, 뷰, 인증, 실시간 기능, 배포까지 전체 스택을 다룹니다.
allowed-tools: Read, Glob, Grep
---

# Rails 8 + Hotwire Plugin

**Entry point for Rails 8 + Hotwire full-stack development skills.**

## Quick Reference

For detailed documentation, see [knowledge/SKILL.md](./knowledge/SKILL.md).

## Plugin Structure

```
rails8-hotwire/
├── SKILL.md              # This file (plugin entry point)
├── knowledge/            # Main knowledge base
│   ├── SKILL.md          # Knowledge entry point
│   ├── core/             # Project setup, structure, gems
│   ├── hotwire/          # Turbo Drive/Frame/Stream, Stimulus
│   ├── auth/             # Devise, Pundit, OAuth
│   ├── background/       # Solid Queue, Sidekiq
│   ├── deploy/           # Kamal, Docker
├── agents/               # Specialized Rails agents
├── hooks/                # Plugin lifecycle hooks
└── skills/               # Individual skill modules
```

## Core Principles

| Principle | Description |
|-----------|-------------|
| **Convention over Configuration** | Follow Rails conventions |
| **HTML over the Wire** | Server-rendered HTML instead of JSON APIs |
| **Server-side First** | Server rendering first, JS for Progressive Enhancement |
| **No PaaS Required** | Remove Redis with Solid Trifecta, self-deploy with Kamal |

## Available Skills

| Skill | Purpose |
|-------|---------|
| `/rails8-hotwire:rails8-core` | Project creation & configuration |
| `/rails8-hotwire:rails8-turbo` | Turbo Drive/Frame/Stream patterns |
| `/rails8-hotwire:rails8-models` | ActiveRecord patterns |
| `/rails8-hotwire:rails8-controllers` | Controller patterns |
| `/rails8-hotwire:rails8-views` | View components |
| `/rails8-hotwire:rails8-auth` | Authentication & authorization |
| `/rails8-hotwire:rails8-realtime` | Real-time features |
| `/rails8-hotwire:rails8-background` | Background jobs |
| `/rails8-hotwire:rails8-testing` | Testing patterns |
| `/rails8-hotwire:rails8-deploy` | Deployment strategies |
| `/rails8-hotwire:rails-autopilot` | Auto Rails app generation |
| `/rails8-hotwire:scaffold-plus` | Enhanced scaffolding |
| `/rails8-hotwire:turbo-wizard` | Turbo setup wizard |
| `/rails8-hotwire:stimulus-gen` | Stimulus controller generator |
| `/rails8-hotwire:auth-setup` | Auth setup wizard |
| `/rails8-hotwire:deploy-kamal` | Kamal deployment automation |
| `/rails8-hotwire:test-gen` | Test generator |
| `/rails8-hotwire:n1-hunter` | N+1 query hunter |
| `/rails8-hotwire:solid-setup` | Solid Trifecta setup |
| `/rails8-hotwire:hotwire-debug` | Hotwire debugging |

## Quick Start

```bash
# Create Rails 8 project
rails new myapp \
  --database=postgresql \
  --css=tailwind \
  --skip-jbuilder \
  --skip-action-mailbox

cd myapp

# Set up built-in authentication (Rails 8)
bin/rails generate authentication
bin/rails db:migrate
```

## Rails 8 Key Technologies

- **Solid Queue**: Redis-free DB-based job queue (Rails 8 default)
- **Solid Cache**: DB-based cache store
- **Solid Cable**: Redis-free WebSocket Pub/Sub
- **Kamal 2**: Docker-based zero-downtime deployment
- **Propshaft + Import Maps**: Bundler-free frontend
- **Built-in Authentication**: `bin/rails generate authentication`

## Specialized Agents

This plugin includes specialized agents for Rails development:

- **rails-architect**: Rails architecture & best practices
- **rails-executor**: Rails code implementation
- **hotwire-specialist**: Turbo & Stimulus expert
- **kamal-deployer**: Deployment specialist
- **rspec-tester**: RSpec test writing
- **rails-reviewer**: Code review

## References

- [Ruby on Rails Guides](https://guides.rubyonrails.org/)
- [Hotwire Official](https://hotwired.dev/)
- [Turbo Handbook](https://turbo.hotwired.dev/handbook/introduction)
- [Stimulus Handbook](https://stimulus.hotwired.dev/handbook/introduction)
- [Kamal Deploy](https://kamal-deploy.org/)

---

**For detailed documentation, navigate to [knowledge/SKILL.md](./knowledge/SKILL.md)**
