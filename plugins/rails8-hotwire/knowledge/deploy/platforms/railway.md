# Railway Deployment

## Overview

Railway is a modern deployment platform with instant deployments, built-in databases, and generous free tier. Excellent for MVPs and side projects with fast iteration needs.

## When to Use

- When you need fast deployment iteration
- When building MVPs or side projects
- When you want Git-push deployments
- When instant database provisioning is needed

## Quick Start

### railway.toml Configuration

```toml
# railway.toml
[build]
builder = "nixpacks"
buildCommand = "bundle install && bin/rails assets:precompile && bin/rails db:migrate"

[deploy]
startCommand = "bin/rails server -b 0.0.0.0 -p $PORT"
healthcheckPath = "/up"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 5
```

### Docker Deployment

```toml
# railway.toml
[build]
builder = "dockerfile"
dockerfilePath = "./Dockerfile"

[deploy]
healthcheckPath = "/up"
healthcheckTimeout = 100
```

## Project Setup

### Initialize Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project (in Rails directory)
railway init

# Link to existing project
railway link
```

### Environment Setup

```bash
# Add PostgreSQL
railway add -d postgres

# Add Redis
railway add -d redis

# View environment variables
railway variables

# Set environment variable
railway variables set RAILS_MASTER_KEY=your_key_here
```

## Service Configuration

### Web Service

```toml
# railway.toml
[build]
builder = "nixpacks"
buildCommand = "bundle install && bin/rails assets:precompile"

[deploy]
startCommand = "bin/rails server -b 0.0.0.0 -p $PORT"
healthcheckPath = "/up"
healthcheckTimeout = 100
numReplicas = 1
```

### Worker Service

Create `railway-worker.toml` or use Railway dashboard:

```toml
# railway-worker.toml (for separate service)
[build]
builder = "nixpacks"
buildCommand = "bundle install"

[deploy]
startCommand = "bin/rails solid_queue:start"
numReplicas = 1
```

### Cron Job

```toml
# railway.toml
[[crons]]
name = "daily-cleanup"
schedule = "0 0 * * *"
command = "bin/rails cleanup:run"
```

## Database Configuration

### PostgreSQL

```bash
# Add PostgreSQL plugin
railway add -d postgres
```

Railway automatically sets `DATABASE_URL`. Configure Rails:

```ruby
# config/database.yml
production:
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
```

### Redis

```bash
# Add Redis plugin
railway add -d redis
```

Railway sets `REDIS_URL`:

```yaml
# config/cable.yml
production:
  adapter: redis
  url: <%= ENV.fetch("REDIS_URL") %>
```

### Multiple Databases

```bash
# Add additional PostgreSQL
railway add -d postgres

# Railway creates DATABASE_URL and DATABASE_URL_2
# Rename in dashboard for clarity
```

```ruby
# config/database.yml
production:
  primary:
    url: <%= ENV["DATABASE_URL"] %>
  cache:
    url: <%= ENV["CACHE_DATABASE_URL"] %>
    migrations_paths: db/cache_migrate
```

## Environment Variables

### Required Variables

```bash
# Set via CLI
railway variables set RAILS_ENV=production
railway variables set RAILS_LOG_TO_STDOUT=true
railway variables set RAILS_SERVE_STATIC_FILES=true
railway variables set RAILS_MASTER_KEY=your_master_key

# Or via dashboard: Settings > Variables
```

### Auto-injected Variables

| Variable | Description |
|----------|-------------|
| `PORT` | Port to bind (use in startCommand) |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `RAILWAY_ENVIRONMENT` | Environment name |
| `RAILWAY_SERVICE_NAME` | Service name |

### Variable References

```bash
# Reference other service variables
REDIS_URL=${{redis.REDIS_URL}}
DATABASE_URL=${{postgres.DATABASE_URL}}
```

## Deployment

### Git Push Deploy

```bash
# After initial setup, just push
git push railway main

# Or use GitHub integration (recommended)
# Connect in Railway dashboard
```

### CLI Deploy

```bash
# Deploy current directory
railway up

# Deploy with logs
railway up --detach=false

# View deployment status
railway status
```

### Rollback

```bash
# View deployments
railway deployments

# Rollback to previous
railway rollback
```

## GitHub Actions Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]

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
      - name: Run tests
        env:
          DATABASE_URL: postgres://postgres:password@localhost:5432/test
          RAILS_ENV: test
        run: |
          bin/rails db:setup
          bin/rails test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: railwayapp/railway-github-link@v1.0.0
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: web
```

## Monorepo Support

```toml
# railway.toml
[build]
builder = "nixpacks"
watchPatterns = ["backend/**"]

[deploy]
startCommand = "cd backend && bin/rails server -b 0.0.0.0 -p $PORT"
```

## Networking

### Public Domains

```bash
# Generate Railway domain
railway domain

# Custom domain
railway domain add myapp.com
```

### Private Networking

Services can communicate internally:

```bash
# Reference internal URL
SERVICE_URL=${{web.RAILWAY_PRIVATE_DOMAIN}}:${{web.PORT}}
```

## Scaling

### Horizontal Scaling

```toml
# railway.toml
[deploy]
numReplicas = 3
```

### Resource Limits

Set in dashboard or via API:

| Plan | Memory | vCPU | Price |
|------|--------|------|-------|
| Hobby | 512MB | 0.5 | $5/mo credit |
| Pro | 8GB | 8 | $20/mo + usage |
| Team | 32GB | 32 | $20/seat/mo |

## Volume Storage

```bash
# Add persistent volume
railway volume add

# Mount path in railway.toml
```

```toml
[deploy]
startCommand = "bin/rails server -b 0.0.0.0 -p $PORT"

[[mounts]]
path = "/rails/storage"
```

## Logs and Monitoring

```bash
# View logs
railway logs

# Follow logs
railway logs --follow

# View specific service
railway logs --service web
```

## Health Check

```ruby
# config/routes.rb
get "up" => "rails/health#show", as: :rails_health_check
```

```toml
# railway.toml
[deploy]
healthcheckPath = "/up"
healthcheckTimeout = 100  # seconds
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Missing healthcheck | Failed deploys | Add /up endpoint |
| Hardcoded PORT | Deployment fails | Use $PORT variable |
| No database pool | Connection errors | Configure pool size |
| Skipping migrations | Schema mismatch | Include in buildCommand |

## Related Files

- [render.md](./render.md): Render deployment
- [fly-io.md](./fly-io.md): Fly.io deployment
- [../database/postgresql.md](../database/postgresql.md): PostgreSQL config

## References

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Railway Templates](https://railway.app/templates)
