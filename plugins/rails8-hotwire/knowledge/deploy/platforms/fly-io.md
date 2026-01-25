# Fly.io Deployment

## Overview

Fly.io runs applications close to users worldwide using edge computing. Excellent for globally distributed applications with low-latency requirements.

## When to Use

- When deploying globally distributed apps
- When low latency is critical
- When you need edge computing
- When running containerized applications

## Quick Start

### fly.toml Configuration

```toml
# fly.toml
app = "myapp"
primary_region = "iad"

[build]

[env]
  RAILS_ENV = "production"
  RAILS_LOG_TO_STDOUT = "true"
  RAILS_SERVE_STATIC_FILES = "true"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1

  [http_service.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20

[[vm]]
  memory = "1gb"
  cpu_kind = "shared"
  cpus = 1

[[statics]]
  guest_path = "/rails/public"
  url_prefix = "/"
```

### Initial Deployment

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app (in Rails directory)
fly launch

# This creates:
# - fly.toml
# - Dockerfile (if needed)
# - PostgreSQL database (optional)
# - Redis (optional)
```

## Project Structure

```
myapp/
├── fly.toml            # Fly configuration
├── Dockerfile          # Container build
├── .dockerignore       # Docker ignore
└── config/
    └── fly.rb          # Fly-specific settings (optional)
```

## Service Configuration

### Web Application

```toml
# fly.toml
app = "myapp"
primary_region = "iad"

[build]

[env]
  RAILS_ENV = "production"
  RAILS_LOG_TO_STDOUT = "true"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[checks]
  [checks.status]
    grace_period = "30s"
    interval = "15s"
    method = "get"
    path = "/up"
    port = 3000
    timeout = "5s"
    type = "http"

[[vm]]
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1
```

### Background Worker

```toml
# fly.toml
[processes]
  app = "bin/rails server -b 0.0.0.0 -p 3000"
  worker = "bin/rails solid_queue:start"

[[vm]]
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1
  processes = ["app"]

[[vm]]
  memory = "256mb"
  cpu_kind = "shared"
  cpus = 1
  processes = ["worker"]
```

### Release Command (Migrations)

```toml
# fly.toml
[deploy]
  release_command = "bin/rails db:migrate"
```

## Database Configuration

### PostgreSQL

```bash
# Create PostgreSQL cluster
fly postgres create --name myapp-db

# Attach to app
fly postgres attach myapp-db

# This sets DATABASE_URL automatically
```

### PostgreSQL Options

```bash
# Create with specific region and size
fly postgres create \
  --name myapp-db \
  --region iad \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 10
```

### Database Configuration

```ruby
# config/database.yml
production:
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  prepared_statements: false
```

### Connect to Database

```bash
# Open psql console
fly postgres connect -a myapp-db

# Or proxy locally
fly proxy 5432 -a myapp-db
# Then connect with: psql postgres://localhost:5432
```

## Redis

```bash
# Create Redis (Upstash)
fly redis create

# Attach to app
fly redis attach

# This sets REDIS_URL
```

```yaml
# config/cable.yml
production:
  adapter: redis
  url: <%= ENV.fetch("REDIS_URL") %>
```

## Secrets Management

```bash
# Set secrets
fly secrets set RAILS_MASTER_KEY=your_key_here
fly secrets set STRIPE_SECRET_KEY=sk_live_xxx

# View secrets (names only)
fly secrets list

# Remove secret
fly secrets unset SECRET_NAME

# Set from file
fly secrets set RAILS_MASTER_KEY=$(cat config/master.key)
```

## Multi-Region Deployment

### Primary Region with Read Replicas

```toml
# fly.toml
app = "myapp"
primary_region = "iad"

[env]
  PRIMARY_REGION = "iad"

[[vm]]
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1
```

```bash
# Scale to multiple regions
fly scale count 2 --region iad
fly scale count 2 --region lhr
fly scale count 2 --region sin
```

### PostgreSQL Read Replicas

```bash
# Add read replica
fly postgres create --name myapp-db-replica \
  --region lhr \
  --primary myapp-db

# Configure app for replica
fly secrets set DATABASE_URL_REPLICA=postgres://...
```

```ruby
# config/database.yml
production:
  primary:
    url: <%= ENV["DATABASE_URL"] %>
  primary_replica:
    url: <%= ENV["DATABASE_URL_REPLICA"] %>
    replica: true
```

## Deployment

### Deploy

```bash
# Deploy
fly deploy

# Deploy with specific config
fly deploy --config fly.production.toml

# Deploy and wait for health check
fly deploy --wait-timeout 300
```

### Rollback

```bash
# View releases
fly releases

# Rollback to previous
fly releases rollback

# Rollback to specific version
fly releases rollback 42
```

## Scaling

### Horizontal Scaling

```bash
# Scale to 3 instances
fly scale count 3

# Scale per region
fly scale count 2 --region iad
fly scale count 1 --region lhr

# View current scale
fly scale show
```

### Vertical Scaling

```bash
# Scale VM size
fly scale vm shared-cpu-2x --memory 1024

# VM sizes: shared-cpu-1x, shared-cpu-2x, shared-cpu-4x
# dedicated-cpu-1x, dedicated-cpu-2x, etc.
```

### Auto-scaling

```toml
# fly.toml
[http_service]
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1

  [http_service.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20
```

## Volume Storage

```bash
# Create volume
fly volumes create myapp_storage --size 10 --region iad

# Mount in fly.toml
```

```toml
# fly.toml
[mounts]
  source = "myapp_storage"
  destination = "/rails/storage"
```

## GitHub Actions Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy to Fly

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
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

## Logs and Monitoring

```bash
# View logs
fly logs

# Follow logs
fly logs --follow

# View specific instance
fly logs --instance INSTANCE_ID
```

## Custom Domains

```bash
# Add custom domain
fly certs add myapp.com

# View certificates
fly certs show myapp.com
```

Configure DNS:
- CNAME: `@ -> myapp.fly.dev`
- Or A/AAAA records from `fly ips list`

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No health check | Silent failures | Configure [checks] |
| Single region | High latency | Deploy to multiple regions |
| Missing release_command | Schema drift | Add db:migrate |
| No auto-stop | Wasted resources | Enable auto_stop_machines |

## Related Files

- [render.md](./render.md): Render deployment
- [railway.md](./railway.md): Railway deployment
- [../database/postgresql.md](../database/postgresql.md): PostgreSQL config

## References

- [Fly.io Documentation](https://fly.io/docs/)
- [Fly.io Rails Guide](https://fly.io/docs/rails/)
- [fly.toml Reference](https://fly.io/docs/reference/configuration/)
