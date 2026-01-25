---
name: rails8-deploy
description: Kamal 2, Docker, cloud deployment, database/storage configuration. Use for production deployment and infrastructure setup.
triggers:
  - deploy
  - deployment
  - kamal
  - docker
  - production
  - ci/cd
  - github actions
  - render
  - railway
  - fly.io
  - 배포
  - 카말
  - 도커
  - 프로덕션
  - 운영 환경
summary: |
  Rails 8 애플리케이션의 배포와 인프라를 다룹니다. Kamal 2, Docker, 클라우드 플랫폼,
  데이터베이스/스토리지 설정, CI/CD 파이프라인을 포함합니다. 프로덕션 배포나
  인프라 설정 시 참조하세요.
token_cost: high
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - kamal/*.md
    - docker/*.md
  deep:
    - "**/*.md"
    - "**/*.yml"
    - "**/*.yaml"
---

# Deploy: Deployment & Infrastructure

## Overview

Covers deployment of Rails 8 applications. Includes Kamal 2, Docker, cloud platforms, database, storage, and caching configuration.

## When to Use

- When deploying to production
- When containerizing with Docker
- When configuring database/storage
- When building CI/CD pipelines

## Core Principles

| Principle | Description |
|-----------|-------------|
| Infrastructure as Code | Manage all configuration as code |
| Zero-downtime Deployment | Apply rolling updates |
| Secret Separation | Credentials + environment variables |
| Observability | Logging and monitoring required |

## Quick Start

### Kamal 2 Setup (Recommended)

```bash
# Install Kamal
gem install kamal

# Initialize Kamal in project
kamal init
```

```yaml
# config/deploy.yml
service: myapp

image: myregistry/myapp

servers:
  web:
    hosts:
      - 192.168.1.1
    labels:
      traefik.http.routers.myapp.rule: Host(`myapp.com`)
    options:
      memory: 1g

registry:
  server: ghcr.io
  username: myuser
  password:
    - KAMAL_REGISTRY_PASSWORD

env:
  clear:
    RAILS_ENV: production
    RAILS_LOG_TO_STDOUT: true
  secret:
    - RAILS_MASTER_KEY
    - DATABASE_URL

builder:
  multiarch: false

accessories:
  db:
    image: postgres:16
    host: 192.168.1.1
    port: 5432
    env:
      secret:
        - POSTGRES_PASSWORD
    directories:
      - data:/var/lib/postgresql/data

traefik:
  options:
    publish:
      - "443:443"
    volume:
      - "/letsencrypt:/letsencrypt"
  args:
    entryPoints.websecure.address: ":443"
    certificatesResolvers.letsencrypt.acme.email: "admin@myapp.com"
    certificatesResolvers.letsencrypt.acme.storage: "/letsencrypt/acme.json"
    certificatesResolvers.letsencrypt.acme.httpchallenge.entrypoint: "web"
```

```bash
# Set secrets
kamal env push

# Deploy
kamal deploy

# Rollback
kamal rollback
```

## File Structure

```
deploy/
├── SKILL.md
├── kamal/
│   ├── setup.md
│   ├── configuration.md
│   ├── secrets.md
│   └── zero-downtime.md
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── production.md
│   └── multi-stage.md
├── platforms/
│   ├── render.md
│   ├── railway.md
│   ├── fly-io.md
│   └── heroku.md
├── database/
│   ├── postgresql.md
│   ├── supabase.md
│   ├── neon.md
│   └── migrations.md
├── storage/
│   ├── active-storage.md
│   ├── cloudflare-r2.md
│   └── s3.md
├── caching/
│   ├── solid-cache.md
│   ├── redis.md
│   └── cdn.md
└── monitoring/
    ├── logging.md
    ├── sentry.md
    └── performance.md
```

## Main Patterns

### Pattern 1: Rails 8 Dockerfile

```dockerfile
# Dockerfile (Rails 8 default generated)
ARG RUBY_VERSION=3.3.0
FROM ruby:$RUBY_VERSION-slim AS base

WORKDIR /rails

ENV RAILS_ENV="production" \
    BUNDLE_DEPLOYMENT="1" \
    BUNDLE_PATH="/usr/local/bundle" \
    BUNDLE_WITHOUT="development:test"

# Build stage
FROM base AS build

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential \
    git \
    libpq-dev \
    pkg-config

COPY Gemfile Gemfile.lock ./
RUN bundle install && \
    rm -rf ~/.bundle/ "${BUNDLE_PATH}"/ruby/*/cache

COPY . .

RUN SECRET_KEY_BASE_DUMMY=1 ./bin/rails assets:precompile

# Final stage
FROM base

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    curl \
    libpq5 && \
    rm -rf /var/lib/apt/lists /var/cache/apt/archives

COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /rails /rails

RUN useradd rails --create-home --shell /bin/bash && \
    chown -R rails:rails db log storage tmp
USER rails:rails

EXPOSE 3000
CMD ["./bin/thrust", "./bin/rails", "server"]
```

### Pattern 2: docker-compose Development Environment

```yaml
# docker-compose.yml
services:
  web:
    build: .
    command: bash -c "rm -f tmp/pids/server.pid && bin/rails server -b 0.0.0.0"
    volumes:
      - .:/rails
      - bundle:/usr/local/bundle
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://postgres:password@db:5432/myapp_development
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    volumes:
      - postgres:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp_development

  redis:
    image: redis:7-alpine
    volumes:
      - redis:/data

volumes:
  bundle:
  postgres:
  redis:
```

### Pattern 3: Environment-specific Database Configuration

```yaml
# config/database.yml
default: &default
  adapter: postgresql
  encoding: unicode
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>

development:
  <<: *default
  database: myapp_development

test:
  <<: *default
  database: myapp_test

production:
  <<: *default
  url: <%= ENV["DATABASE_URL"] %>
  prepared_statements: true
  advisory_locks: true
```

### Pattern 4: Active Storage + Cloudflare R2

```ruby
# config/storage.yml
cloudflare:
  service: S3
  endpoint: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
  access_key_id: <%= Rails.application.credentials.dig(:cloudflare, :access_key_id) %>
  secret_access_key: <%= Rails.application.credentials.dig(:cloudflare, :secret_access_key) %>
  bucket: myapp-production
  region: auto

# config/environments/production.rb
config.active_storage.service = :cloudflare
```

### Pattern 5: Solid Cache Configuration

```ruby
# config/environments/production.rb
config.cache_store = :solid_cache_store

# config/solid_cache.yml
production:
  database: cache
  store_options:
    max_age: 1.week
    max_entries: 100_000
    namespace: myapp
```

```yaml
# config/database.yml
production:
  primary:
    <<: *default
    url: <%= ENV["DATABASE_URL"] %>
  cache:
    <<: *default
    url: <%= ENV["CACHE_DATABASE_URL"] %>
    migrations_paths: db/cache_migrate
```

### Pattern 6: CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - uses: ruby/setup-ruby@v1
        with:
          bundler-cache: true

      - name: Setup database
        env:
          DATABASE_URL: postgres://postgres:password@localhost:5432/test
          RAILS_ENV: test
        run: bin/rails db:setup

      - name: Run tests
        env:
          DATABASE_URL: postgres://postgres:password@localhost:5432/test
          RAILS_ENV: test
        run: bin/rails test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - uses: webfactory/ssh-agent@v0.8.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - uses: ruby/setup-ruby@v1
        with:
          bundler-cache: true

      - name: Deploy with Kamal
        env:
          KAMAL_REGISTRY_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
          RAILS_MASTER_KEY: ${{ secrets.RAILS_MASTER_KEY }}
        run: |
          gem install kamal
          kamal deploy
```

### Pattern 7: Render.com Deployment

```yaml
# render.yaml
services:
  - type: web
    name: myapp
    runtime: ruby
    buildCommand: bundle install && bin/rails assets:precompile
    startCommand: bin/rails server
    envVars:
      - key: RAILS_MASTER_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: myapp-db
          property: connectionString

databases:
  - name: myapp-db
    plan: starter
```

### Pattern 8: Railway Deployment

```toml
# railway.toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "bin/rails server -b 0.0.0.0 -p $PORT"
healthcheckPath = "/up"
healthcheckTimeout = 100

[[services]]
name = "web"
```

## Deployment Platform Comparison

| Platform | Pros | Cons | Best For |
|----------|------|------|----------|
| **Kamal** | Full control, cost-effective | Server management required | Medium to large scale |
| **Render** | Easy setup, auto SSL | Cost increases | Startups |
| **Railway** | Fast deployment, Git integration | Limited customization | MVP |
| **Fly.io** | Edge deployment, affordable | Learning curve | Global apps |
| **Heroku** | Mature ecosystem | High cost | Enterprise |

## Production Checklist

```bash
# Required configuration verification
[ ] RAILS_MASTER_KEY set
[ ] DATABASE_URL set
[ ] SECRET_KEY_BASE set
[ ] config.force_ssl = true
[ ] config.assume_ssl = true  # Behind Kamal/proxy
[ ] Asset precompile verified
[ ] Database migrations
[ ] Logging configured (STDOUT)
[ ] Error monitoring (Sentry)
[ ] Backup configured
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Hardcoded secrets | Security risk | Use credentials |
| Single point of failure | Availability issues | Multiple instances |
| Missing migrations | Deployment failure | Verify in CI |
| No log collection | Cannot debug | Centralized logging |

## Related Skills

- [core](../core/SKILL.md): Credentials setup
- [background](../background/): Job queue deployment (Phase 3)
- [realtime](../realtime/SKILL.md): Redis/Solid Cable

## References

- [Kamal Documentation](https://kamal-deploy.org/)
- [Rails Deployment](https://guides.rubyonrails.org/deployment.html)
- [Docker Official](https://docs.docker.com/)
- [12 Factor App](https://12factor.net/)
