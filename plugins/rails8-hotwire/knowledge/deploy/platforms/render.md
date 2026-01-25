# Render.com Deployment

## Overview

Render is a modern cloud platform with native Rails support, automatic SSL, and managed PostgreSQL. Excellent for startups and small-to-medium applications.

## When to Use

- When you want simple PaaS deployment
- When automatic SSL and scaling are needed
- When using managed PostgreSQL
- When deploying from GitHub/GitLab

## Quick Start

### render.yaml Blueprint

```yaml
# render.yaml
services:
  # Web service
  - type: web
    name: myapp
    runtime: ruby
    plan: starter
    buildCommand: |
      bundle install
      bin/rails assets:precompile
      bin/rails db:migrate
    startCommand: bin/rails server -p $PORT
    healthCheckPath: /up
    envVars:
      - key: RAILS_ENV
        value: production
      - key: RAILS_LOG_TO_STDOUT
        value: true
      - key: RAILS_SERVE_STATIC_FILES
        value: true
      - key: RAILS_MASTER_KEY
        sync: false  # Manual entry required
      - key: DATABASE_URL
        fromDatabase:
          name: myapp-db
          property: connectionString

  # Background worker (optional)
  - type: worker
    name: myapp-worker
    runtime: ruby
    plan: starter
    buildCommand: bundle install
    startCommand: bin/rails solid_queue:start
    envVars:
      - key: RAILS_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: myapp-db
          property: connectionString
      - key: RAILS_MASTER_KEY
        sync: false

databases:
  - name: myapp-db
    plan: starter
    databaseName: myapp_production
    user: myapp
```

### Docker Deployment

```yaml
# render.yaml (Docker)
services:
  - type: web
    name: myapp
    runtime: docker
    plan: starter
    dockerfilePath: ./Dockerfile
    dockerContext: .
    healthCheckPath: /up
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

## Service Types

### Web Service

```yaml
services:
  - type: web
    name: myapp
    runtime: ruby           # Or docker
    plan: starter           # free, starter, standard, pro, pro-plus
    numInstances: 1         # Auto-scale available on paid plans
    region: oregon          # oregon, frankfurt, ohio, singapore
    branch: main            # Git branch to deploy
    buildCommand: bundle install && bin/rails assets:precompile
    startCommand: bin/rails server -p $PORT
    healthCheckPath: /up
    autoDeploy: true        # Deploy on push
```

### Background Worker

```yaml
services:
  - type: worker
    name: myapp-worker
    runtime: ruby
    plan: starter
    buildCommand: bundle install
    startCommand: bin/rails solid_queue:start
    autoDeploy: true
```

### Cron Job

```yaml
services:
  - type: cron
    name: myapp-daily-cleanup
    runtime: ruby
    plan: starter
    schedule: "0 0 * * *"  # Daily at midnight
    buildCommand: bundle install
    startCommand: bin/rails cleanup:run
```

### Private Service (Internal Only)

```yaml
services:
  - type: pserv
    name: myapp-internal-api
    runtime: ruby
    plan: starter
    startCommand: bin/rails server -p $PORT
    # No public URL, accessible only within Render network
```

## Database Configuration

### Managed PostgreSQL

```yaml
databases:
  - name: myapp-db
    plan: starter           # free, starter, standard, pro, pro-plus
    databaseName: myapp_production
    user: myapp
    region: oregon
    postgresMajorVersion: "16"
    ipAllowList: []         # Empty = all IPs (use internal URL)
```

### Connection String

```yaml
# Automatically injected
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: myapp-db
      property: connectionString    # Full URL
  # Or individual properties
  - key: PGHOST
    fromDatabase:
      name: myapp-db
      property: host
  - key: PGPORT
    fromDatabase:
      name: myapp-db
      property: port
```

### Connection Pooling

```ruby
# config/database.yml
production:
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  prepared_statements: false  # For connection pooling
```

## Environment Variables

### Static Values

```yaml
envVars:
  - key: RAILS_ENV
    value: production
  - key: RAILS_LOG_TO_STDOUT
    value: true
```

### Secrets (Manual Entry)

```yaml
envVars:
  - key: RAILS_MASTER_KEY
    sync: false  # Enter manually in dashboard
  - key: STRIPE_SECRET_KEY
    sync: false
```

### From Other Services

```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: myapp-db
      property: connectionString
  - key: REDIS_URL
    fromService:
      name: myapp-redis
      type: pserv
      property: hostport
```

### Secret Files

```yaml
envVars:
  - key: GOOGLE_APPLICATION_CREDENTIALS
    value: /etc/secrets/gcp-key.json
secretFiles:
  - name: gcp-key.json
    path: /etc/secrets/gcp-key.json
```

## Scaling

### Horizontal Scaling

```yaml
services:
  - type: web
    name: myapp
    plan: standard
    numInstances: 3         # Fixed instances
    # Or auto-scaling (pro plan)
    scaling:
      minInstances: 1
      maxInstances: 10
      targetMemoryPercent: 70
      targetCPUPercent: 70
```

### Plan Comparison

| Plan | RAM | CPU | Price | Instances |
|------|-----|-----|-------|-----------|
| free | 512MB | 0.1 | $0 | 1 |
| starter | 512MB | 0.5 | $7/mo | 1 |
| standard | 2GB | 1 | $25/mo | 1-10 |
| pro | 4GB | 2 | $85/mo | 1-20 |
| pro-plus | 8GB | 4 | $175/mo | 1-50 |

## Redis (Key-Value Store)

```yaml
services:
  - type: redis
    name: myapp-redis
    plan: starter
    maxmemoryPolicy: allkeys-lru
    ipAllowList: []
```

```yaml
# Reference in web service
envVars:
  - key: REDIS_URL
    fromService:
      name: myapp-redis
      type: redis
      property: connectionString
```

## GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

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
      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
```

## Health Check

```ruby
# config/routes.rb
get "up" => "rails/health#show", as: :rails_health_check
```

```yaml
# render.yaml
services:
  - type: web
    healthCheckPath: /up
```

## Custom Domain

```yaml
services:
  - type: web
    name: myapp
    customDomains:
      - myapp.com
      - www.myapp.com
```

Configure DNS:
- A record: `@ -> 216.24.57.1`
- CNAME: `www -> myapp.onrender.com`

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Free tier for production | Sleep after inactivity | Use paid plan |
| External DATABASE_URL | Higher latency | Use Render's managed DB |
| No health check | Failed deploys undetected | Add /up endpoint |
| Secrets in render.yaml | Exposed credentials | Use sync: false |

## Related Files

- [railway.md](./railway.md): Railway deployment
- [fly-io.md](./fly-io.md): Fly.io deployment
- [../database/postgresql.md](../database/postgresql.md): PostgreSQL config

## References

- [Render Documentation](https://render.com/docs)
- [Render Rails Guide](https://render.com/docs/deploy-rails)
- [Render YAML Spec](https://render.com/docs/blueprint-spec)
