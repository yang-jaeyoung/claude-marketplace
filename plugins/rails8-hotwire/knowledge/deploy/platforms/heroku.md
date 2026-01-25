# Heroku Deployment

## Overview

Heroku is the original PaaS with a mature Rails ecosystem. Best for enterprises needing stability, extensive add-ons, and proven infrastructure.

## When to Use

- When you need mature, battle-tested PaaS
- When extensive add-on ecosystem is valuable
- When enterprise compliance is required
- When team familiarity with Heroku exists

## Quick Start

### Procfile Configuration

```procfile
# Procfile
web: bundle exec puma -C config/puma.rb
worker: bundle exec rails solid_queue:start
release: bundle exec rails db:migrate
```

### app.json (Review Apps)

```json
{
  "name": "myapp",
  "description": "My Rails 8 Application",
  "repository": "https://github.com/myuser/myapp",
  "keywords": ["rails", "ruby"],
  "stack": "heroku-24",
  "buildpacks": [
    { "url": "heroku/ruby" }
  ],
  "env": {
    "RAILS_ENV": {
      "value": "production"
    },
    "RAILS_LOG_TO_STDOUT": {
      "value": "true"
    },
    "RAILS_SERVE_STATIC_FILES": {
      "value": "true"
    },
    "RAILS_MASTER_KEY": {
      "required": true
    }
  },
  "addons": [
    "heroku-postgresql:essential-0",
    "heroku-redis:mini"
  ],
  "formation": {
    "web": {
      "quantity": 1,
      "size": "basic"
    },
    "worker": {
      "quantity": 1,
      "size": "basic"
    }
  },
  "scripts": {
    "postdeploy": "bundle exec rails db:seed"
  }
}
```

## Initial Setup

### Create Application

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create myapp

# Add PostgreSQL
heroku addons:create heroku-postgresql:essential-0

# Add Redis (if needed)
heroku addons:create heroku-redis:mini
```

### Configure Environment

```bash
# Set Rails master key
heroku config:set RAILS_MASTER_KEY=$(cat config/master.key)

# Set environment variables
heroku config:set RAILS_ENV=production
heroku config:set RAILS_LOG_TO_STDOUT=true
heroku config:set RAILS_SERVE_STATIC_FILES=true

# View all config
heroku config
```

### Deploy

```bash
# Add Heroku remote
heroku git:remote -a myapp

# Deploy
git push heroku main

# Run migrations (also in Procfile release)
heroku run rails db:migrate

# Open app
heroku open
```

## Buildpacks

### Ruby Buildpack (Default)

```bash
# Set Ruby buildpack
heroku buildpacks:set heroku/ruby
```

### Multiple Buildpacks (With Node.js)

```bash
# Add Node.js buildpack (runs first)
heroku buildpacks:add --index 1 heroku/nodejs

# View buildpacks
heroku buildpacks
```

### Custom Buildpack Order

```bash
heroku buildpacks:clear
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/ruby
```

## Database Configuration

### PostgreSQL Setup

```bash
# Add PostgreSQL
heroku addons:create heroku-postgresql:essential-0

# View database info
heroku pg:info

# Open psql console
heroku pg:psql
```

### Database Configuration

```ruby
# config/database.yml
production:
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  prepared_statements: false  # For connection pooling
```

### Connection Pooling

```bash
# Add PgBouncer buildpack
heroku buildpacks:add heroku/pgbouncer

# Enable connection pooling
heroku config:set PGBOUNCER_POOL_SIZE=20
```

### Database Maintenance

```bash
# Run migrations
heroku run rails db:migrate

# Seed database
heroku run rails db:seed

# Reset database (DESTRUCTIVE)
heroku pg:reset DATABASE_URL --confirm myapp
heroku run rails db:migrate
heroku run rails db:seed

# Create backup
heroku pg:backups:capture

# Download backup
heroku pg:backups:download
```

## Dyno Types and Scaling

### Dyno Types

| Type | RAM | CPU | Price | Use Case |
|------|-----|-----|-------|----------|
| Eco | 512MB | Shared | $5/mo (1000 hrs) | Personal projects |
| Basic | 512MB | Shared | $7/mo | Low-traffic apps |
| Standard-1x | 512MB | Shared | $25/mo | Production |
| Standard-2x | 1GB | Shared | $50/mo | High-memory |
| Performance-M | 2.5GB | Dedicated | $250/mo | High-traffic |
| Performance-L | 14GB | Dedicated | $500/mo | Enterprise |

### Scaling

```bash
# Scale web dynos
heroku ps:scale web=2

# Scale workers
heroku ps:scale worker=1

# Scale with dyno type
heroku ps:scale web=2:standard-2x

# View current scale
heroku ps
```

### Autoscaling

```bash
# Enable autoscaling (Performance dynos only)
heroku autoscale:enable --min=2 --max=10 --p95=200
```

## Redis Configuration

```bash
# Add Redis
heroku addons:create heroku-redis:mini

# View Redis info
heroku redis:info

# Access Redis CLI
heroku redis:cli
```

```yaml
# config/cable.yml
production:
  adapter: redis
  url: <%= ENV.fetch("REDIS_URL") %>
```

## Background Jobs

### Solid Queue

```procfile
# Procfile
web: bundle exec puma -C config/puma.rb
worker: bundle exec rails solid_queue:start
```

### Sidekiq (Alternative)

```procfile
# Procfile
web: bundle exec puma -C config/puma.rb
worker: bundle exec sidekiq
```

```bash
# Scale worker dyno
heroku ps:scale worker=1
```

## Logs and Monitoring

```bash
# View logs
heroku logs

# Follow logs
heroku logs --tail

# Filter by dyno
heroku logs --dyno web

# View specific process
heroku logs --ps web.1
```

### Log Drains

```bash
# Add Papertrail
heroku addons:create papertrail

# Or add custom log drain
heroku drains:add https://logs.example.com/heroku
```

## Custom Domains

```bash
# Add domain
heroku domains:add myapp.com
heroku domains:add www.myapp.com

# View domains
heroku domains

# Enable SSL
heroku certs:auto:enable
```

Configure DNS:
- CNAME: `www -> your-app-name.herokuapp.com`
- ALIAS/ANAME: `@ -> your-app-name.herokuapp.com`

## Review Apps

### Pipeline Setup

```bash
# Create pipeline
heroku pipelines:create myapp-pipeline -a myapp-production

# Add staging app
heroku pipelines:add myapp-pipeline -a myapp-staging -s staging

# Enable review apps in Heroku Dashboard
# Settings > Review Apps > Enable
```

### app.json for Review Apps

```json
{
  "name": "myapp",
  "scripts": {
    "postdeploy": "bundle exec rails db:schema:load db:seed"
  },
  "env": {
    "RAILS_MASTER_KEY": {
      "required": true
    },
    "REVIEW_APP": {
      "value": "true"
    }
  },
  "addons": [
    "heroku-postgresql:essential-0"
  ],
  "formation": {
    "web": {
      "quantity": 1,
      "size": "basic"
    }
  }
}
```

## GitHub Actions Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy to Heroku

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
      - uses: akhileshns/heroku-deploy@v3.12.14
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: myapp
          heroku_email: ${{ secrets.HEROKU_EMAIL }}
```

## Maintenance

```bash
# Enable maintenance mode
heroku maintenance:on

# Deploy
git push heroku main

# Disable maintenance mode
heroku maintenance:off

# Run one-off command
heroku run rails console
heroku run bash
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Eco dyno for production | Sleeps after 30min | Use Basic or higher |
| No Procfile | Default settings | Create explicit Procfile |
| DATABASE_URL pool mismatch | Connection errors | Match pool to RAILS_MAX_THREADS |
| No release command | Manual migrations | Add release to Procfile |

## Related Files

- [render.md](./render.md): Render deployment
- [fly-io.md](./fly-io.md): Fly.io deployment
- [../database/postgresql.md](../database/postgresql.md): PostgreSQL config

## References

- [Heroku Dev Center](https://devcenter.heroku.com/)
- [Heroku Rails Guide](https://devcenter.heroku.com/articles/getting-started-with-rails8)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
