# Neon Serverless Postgres

## Overview

Neon is a serverless PostgreSQL database that scales to zero, branches for development, and provides instant database provisioning. Excellent for development workflows and cost-sensitive production.

## When to Use

- When you need database branching for development
- When scale-to-zero cost optimization is valuable
- When instant database provisioning is needed
- When deploying preview environments

## Quick Start

### Connection Configuration

```yaml
# config/database.yml
production:
  adapter: postgresql
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  prepared_statements: false  # Required for Neon pooler
```

### Connection String

```bash
# Pooled connection (recommended for applications)
DATABASE_URL=postgres://user:password@ep-xxx-xxx-123456.us-east-2.aws.neon.tech/neondb?sslmode=require

# Direct connection (for migrations)
DIRECT_DATABASE_URL=postgres://user:password@ep-xxx-xxx-123456.us-east-2.aws.neon.tech/neondb?sslmode=require&options=endpoint%3Dep-xxx-xxx-123456
```

## Connection Pooling

### Neon Pooler Configuration

```yaml
# config/database.yml
production:
  adapter: postgresql
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  prepared_statements: false  # Required for pooler
  advisory_locks: false       # Required for transaction mode
```

### Connection Pool Sizing

| Plan | Max Connections | Recommendation |
|------|-----------------|----------------|
| Free | 100 pooled | pool: 5-10 |
| Pro | 500 pooled | pool: 10-20 |
| Custom | Custom | Based on needs |

## Database Branching

### Branch Workflow

```bash
# Create branch from main
neon branches create --name feature-xyz --parent main

# Get connection string for branch
neon connection-string feature-xyz

# Delete branch
neon branches delete feature-xyz
```

### Development Branches

```yaml
# config/database.yml
development:
  adapter: postgresql
  url: <%= ENV.fetch("DATABASE_URL") { "postgres://localhost/myapp_development" } %>
  pool: 5
```

```bash
# Use Neon branch for development
DATABASE_URL=postgres://user:pass@ep-branch-xxx.neon.tech/neondb rails server
```

### CI/CD Branch per PR

```yaml
# .github/workflows/test.yml
name: Test

on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create Neon branch
        id: create-branch
        uses: neondatabase/create-branch-action@v4
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          api_key: ${{ secrets.NEON_API_KEY }}
          branch_name: pr-${{ github.event.number }}
          parent: main

      - uses: ruby/setup-ruby@v1
        with:
          bundler-cache: true

      - name: Run tests
        env:
          DATABASE_URL: ${{ steps.create-branch.outputs.db_url }}
        run: |
          bin/rails db:migrate
          bin/rails test

      - name: Delete branch on failure
        if: failure()
        uses: neondatabase/delete-branch-action@v3
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          api_key: ${{ secrets.NEON_API_KEY }}
          branch: pr-${{ github.event.number }}
```

## Scale to Zero

### Auto-suspend Configuration

Neon automatically suspends compute after inactivity:

| Plan | Auto-suspend | Wake Time |
|------|--------------|-----------|
| Free | 5 minutes | ~1 second |
| Pro | Configurable | ~1 second |
| Custom | Custom | ~500ms |

### Keep-alive for Production

```ruby
# config/initializers/neon.rb
if Rails.env.production? && ENV["NEON_KEEP_ALIVE"]
  # Prevent cold starts by pinging periodically
  Thread.new do
    loop do
      sleep 4.minutes
      ActiveRecord::Base.connection.execute("SELECT 1")
    rescue => e
      Rails.logger.error("Neon keep-alive failed: #{e.message}")
    end
  end
end
```

### Cold Start Handling

```ruby
# config/puma.rb
before_fork do
  # Disconnect before forking
  ActiveRecord::Base.connection_pool.disconnect!
end

on_worker_boot do
  # Reconnect after fork
  ActiveRecord::Base.establish_connection
end
```

## Migrations

### With Direct Connection

```bash
# Migrations use direct connection
DIRECT_DATABASE_URL=... bin/rails db:migrate

# Application uses pooled connection
DATABASE_URL=... bin/rails server
```

### Kamal Configuration

```yaml
# config/deploy.yml
env:
  secret:
    - DATABASE_URL         # Pooled
    - DIRECT_DATABASE_URL  # For migrations
```

```bash
# Run migration with direct connection
RAILS_ENV=production DATABASE_URL=$DIRECT_DATABASE_URL bin/rails db:migrate
```

## Solid Queue with Neon

```yaml
# config/database.yml
production:
  primary:
    url: <%= ENV["DATABASE_URL"] %>
    pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
    prepared_statements: false
    advisory_locks: false
  queue:
    url: <%= ENV["DATABASE_URL"] %>
    pool: 5
    prepared_statements: false
    advisory_locks: false
    migrations_paths: db/queue_migrate
```

## Preview Environments

### Automated Branch Creation

```yaml
# .github/workflows/preview.yml
name: Preview

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create Neon branch
        id: neon
        uses: neondatabase/create-branch-action@v4
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          api_key: ${{ secrets.NEON_API_KEY }}
          branch_name: preview-${{ github.event.number }}
          parent: main

      - name: Deploy preview
        uses: some/deploy-action@v1
        with:
          environment: preview-${{ github.event.number }}
          database_url: ${{ steps.neon.outputs.db_url }}

      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: 'Preview deployed with branch database: preview-${{ github.event.number }}'
            })
```

### Cleanup on PR Close

```yaml
# .github/workflows/cleanup.yml
name: Cleanup

on:
  pull_request:
    types: [closed]

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Delete Neon branch
        uses: neondatabase/delete-branch-action@v3
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          api_key: ${{ secrets.NEON_API_KEY }}
          branch: preview-${{ github.event.number }}
```

## Neon CLI

```bash
# Install
brew install neon

# Login
neon auth

# List projects
neon projects list

# Create branch
neon branches create --name my-feature --parent main

# Get connection string
neon connection-string my-feature --pooled

# Delete branch
neon branches delete my-feature
```

## SSL Configuration

```yaml
# config/database.yml
production:
  url: <%= ENV["DATABASE_URL"] %>
  sslmode: require  # Required for Neon
```

## Monitoring

### Connection Stats

```ruby
# app/controllers/health_controller.rb
def database
  result = ActiveRecord::Base.connection.execute(<<~SQL)
    SELECT
      numbackends as connections,
      xact_commit as commits,
      xact_rollback as rollbacks
    FROM pg_stat_database
    WHERE datname = current_database()
  SQL

  render json: result.first
end
```

### Query Performance

Use Neon Dashboard > Monitoring for:
- Query latency
- Connection usage
- Compute utilization

## Kamal Integration

```yaml
# config/deploy.yml
service: myapp
image: ghcr.io/myuser/myapp

env:
  clear:
    RAILS_ENV: production
    RAILS_LOG_TO_STDOUT: true
  secret:
    - RAILS_MASTER_KEY
    - DATABASE_URL
    - DIRECT_DATABASE_URL

# No database accessory - using Neon
```

## Cost Optimization

### Scale to Zero Benefits

- Free tier: 0.5 GB storage, auto-suspend
- Pro tier: 10GB storage, configurable auto-suspend
- Only pay for active compute time

### Branch Cleanup

```yaml
# Clean up stale branches
- name: Delete old branches
  run: |
    neon branches list --json | \
    jq -r '.[] | select(.created_at < (now - 7*24*60*60) | @iso8601) | .name' | \
    xargs -I {} neon branches delete {}
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Direct connection in app | Connection exhaustion | Use pooled connection |
| No cold start handling | Slow first request | Add health check warmup |
| Prepared statements | Pooler incompatibility | Disable prepared_statements |
| Not cleaning branches | Storage waste | Automate branch cleanup |

## Related Files

- [postgresql.md](./postgresql.md): PostgreSQL configuration
- [supabase.md](./supabase.md): Supabase integration
- [migrations.md](./migrations.md): Migration patterns

## References

- [Neon Documentation](https://neon.tech/docs)
- [Neon GitHub Actions](https://github.com/neondatabase/create-branch-action)
- [Neon CLI](https://neon.tech/docs/reference/cli-overview)
