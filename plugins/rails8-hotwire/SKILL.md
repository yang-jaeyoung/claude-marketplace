---
name: rails8-hotwire
description: Rails 8 + Hotwire full-stack web development guide. Covers project creation, Turbo/Stimulus, models, controllers, views, authentication, real-time features, deployment, and more. Use when working on Rails 8 projects.
triggers:
  - rails8
  - rails 8
  - hotwire
  - rails hotwire
  - turbo
  - stimulus
  - 레일즈
  - 레일즈8
  - 핫와이어
  - 풀스택
  - 터보
  - 스티뮬러스
summary: |
  Rails 8과 Hotwire를 사용한 풀스택 웹 개발 가이드. 프로젝트 생성부터 Turbo/Stimulus,
  모델, 컨트롤러, 뷰, 인증, 실시간 기능, 배포까지 전체 스택을 다룹니다.
  "No PaaS Required" 철학과 "HTML Over The Wire" 패러다임 기반.
token_cost: medium
depth_files:
  shallow:
    - SKILL.md
    - knowledge/SKILL.md
  standard:
    - SKILL.md
    - knowledge/SKILL.md
    - knowledge/core/SKILL.md
    - knowledge/hotwire/SKILL.md
  deep:
    - "**/*.md"
---

# Rails 8 + Hotwire Plugin

**Entry point for Rails 8 + Hotwire full-stack development skills.**

This is the root skill file that loads the comprehensive Rails 8 + Hotwire knowledge base.

## Quick Reference

For detailed documentation, see [knowledge/SKILL.md](./knowledge/SKILL.md).

## Plugin Structure

```
rails8-hotwire/
├── SKILL.md              # This file (plugin entry point)
├── LOADING-PROTOCOL.md   # Skill loading algorithm
├── knowledge/            # Main knowledge base
│   ├── SKILL.md          # Knowledge entry point
│   ├── core/             # Project setup, structure, gems
│   ├── hotwire/          # Turbo Drive/Frame/Stream, Stimulus
│   ├── models/           # ActiveRecord, queries, validations
│   ├── controllers/      # RESTful, service objects
│   ├── views/            # Partials, components, forms
│   ├── auth/             # Devise, Pundit, OAuth
│   ├── realtime/         # ActionCable, Turbo Streams
│   ├── background/       # Solid Queue, Sidekiq
│   ├── testing/          # RSpec, Factory Bot
│   ├── deploy/           # Kamal, Docker
│   ├── recipes/          # Practical recipes
│   ├── snippets/         # Code snippets (Ruby, JS, ERB)
│   └── templates/        # Project/config templates
├── agents/               # Specialized Rails agents
├── hooks/                # Plugin lifecycle hooks
├── pipelines/            # Pre-built workflows
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

| Skill | Trigger | Purpose |
|-------|---------|---------|
| [knowledge](./knowledge/SKILL.md) | rails8, hotwire | Main knowledge base |
| [core](./knowledge/core/SKILL.md) | rails setup, rails project | Project creation & configuration |
| [hotwire](./knowledge/hotwire/SKILL.md) | turbo, stimulus | Hotwire patterns |
| [models](./knowledge/models/SKILL.md) | activerecord, models | Model patterns |
| [controllers](./knowledge/controllers/SKILL.md) | controllers, actions | Controller patterns |
| [views](./knowledge/views/SKILL.md) | views, partials, components | View components |
| [auth](./knowledge/auth/SKILL.md) | authentication, devise | Auth & authorization |
| [realtime](./knowledge/realtime/SKILL.md) | actioncable, websockets | Real-time features |
| [background](./knowledge/background/SKILL.md) | solid queue, sidekiq | Background jobs |
| [testing](./knowledge/testing/SKILL.md) | rspec, testing | Testing patterns |
| [deploy](./knowledge/deploy/SKILL.md) | kamal, deployment | Deployment strategies |
| [recipes](./knowledge/recipes/SKILL.md) | saas, mvp | Complete feature recipes |

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

## Usage

1. **Learn concepts**: Reference skill SKILL.md files
2. **Copy code**: Use snippets from `knowledge/snippets/`
3. **Use templates**: Apply from `knowledge/templates/`
4. **Follow recipes**: Complete features from `knowledge/recipes/`

## Specialized Agents

This plugin includes specialized agents for Rails development:

- **rails-architect**: Rails architecture & best practices
- **rails-executor**: Rails code implementation
- **hotwire-specialist**: Turbo & Stimulus expert
- **kamal-deployer**: Deployment specialist

## Loading Protocol

This plugin uses intelligent skill loading based on query analysis. See [LOADING-PROTOCOL.md](./LOADING-PROTOCOL.md) for details on:

- Trigger matching algorithm
- Token-efficient depth selection
- Skill composition strategies
- Performance optimization

## References

- [Ruby on Rails Guides](https://guides.rubyonrails.org/)
- [Hotwire Official](https://hotwired.dev/)
- [Turbo Handbook](https://turbo.hotwired.dev/handbook/introduction)
- [Stimulus Handbook](https://stimulus.hotwired.dev/handbook/introduction)
- [Kamal Deploy](https://kamal-deploy.org/)

---

**For detailed documentation, navigate to [knowledge/SKILL.md](./knowledge/SKILL.md)**
