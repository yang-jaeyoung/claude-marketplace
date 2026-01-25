---
name: rails8-hotwire
description: Rails 8 + Hotwire full-stack web development guide. Covers project creation, Turbo/Stimulus, models, controllers, views, authentication, real-time features, deployment, and more. Use when working on Rails 8 projects.
triggers:
  - rails8
  - rails 8
  - hotwire
  - rails hotwire
  - 레일즈
  - 레일즈8
  - 핫와이어
  - 풀스택
summary: |
  Rails 8과 Hotwire를 사용한 풀스택 웹 개발 가이드. 프로젝트 생성부터 Turbo/Stimulus,
  모델, 컨트롤러, 뷰, 인증, 실시간 기능, 배포까지 전체 스택을 다룹니다.
  "No PaaS Required" 철학과 "HTML Over The Wire" 패러다임 기반.
token_cost: medium
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - core/SKILL.md
    - hotwire/SKILL.md
  deep:
    - "**/*.md"
---

# Rails 8 + Hotwire Development Skills

## Overview

A comprehensive guide for full-stack web development with Rails 8 and Hotwire. Build modern web applications based on the "No PaaS Required" philosophy and "HTML Over The Wire" paradigm.

## When to Use

- When creating/configuring Rails 8 projects
- When implementing Hotwire (Turbo/Stimulus)
- When applying patterns like service objects and form objects
- When setting up authentication, real-time features, or deployment

## Core Principles

| Principle | Description |
|-----------|-------------|
| Convention over Configuration | Following Rails conventions minimizes configuration |
| HTML over the Wire | Server-rendered HTML responses instead of JSON APIs |
| Server-side First | Server rendering first, JS for enhancement |
| Progressive Enhancement | Core functionality works without JS |

## Skill Structure

| Skill | Purpose |
|-------|---------|
| [core](./core/SKILL.md) | Project setup, structure, gems |
| [hotwire](./hotwire/SKILL.md) | Turbo Drive/Frame/Stream, Stimulus |
| [models](./models/SKILL.md) | ActiveRecord, queries, validations |
| [controllers](./controllers/SKILL.md) | RESTful, service objects, responses |
| [views](./views/SKILL.md) | Partials, components, forms |
| [auth](./auth/SKILL.md) | Devise, authorization, OAuth |
| [realtime](./realtime/SKILL.md) | ActionCable, broadcasting |
| [background](./background/SKILL.md) | Solid Queue, Sidekiq |
| [testing](./testing/SKILL.md) | RSpec, Factory Bot |
| [deploy](./deploy/SKILL.md) | Kamal, Docker, cloud |

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

## Usage

1. Reference the SKILL.md in the relevant skill folder
2. Copy code from snippets/
3. Use file templates from templates/
4. Check combination patterns in recipes/

## File Structure

```
rails8-hotwire/
├── SKILL.md          # This file (main entry point)
├── core/             # Project setup
├── hotwire/          # Turbo + Stimulus
├── models/           # ActiveRecord
├── controllers/      # Controller patterns
├── views/            # Views + components
├── auth/             # Authentication + authorization
├── realtime/         # Real-time features
├── background/       # Background jobs
├── testing/          # Testing
├── deploy/           # Deployment + infrastructure
├── recipes/          # Practical recipes
├── snippets/         # Common snippets
└── templates/        # Templates
```

## Quick Reference

| Task | Reference Location |
|------|-------------------|
| New project | core/setup/ |
| Turbo Frame | hotwire/turbo/frames.md |
| Service object | core/patterns/service-object.md |
| Form handling | controllers/patterns/form-objects.md |
| Authentication setup | auth/ |
| Real-time features | realtime/ |
| Deployment | deploy/ |

## References

- [Ruby on Rails Guides](https://guides.rubyonrails.org/)
- [Hotwire Official](https://hotwired.dev/)
- [Turbo Handbook](https://turbo.hotwired.dev/handbook/introduction)
- [Stimulus Handbook](https://stimulus.hotwired.dev/handbook/introduction)
