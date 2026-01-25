# Zero-Downtime Deployment

## Overview

Kamal 2 provides zero-downtime deployments through rolling updates. Traefik routes traffic to healthy containers while new versions start, ensuring no requests are dropped.

## When to Use

- When deploying to production with active users
- When running multiple application servers
- When database migrations are involved
- When maximum uptime is critical

## Quick Start

### Health Check Configuration

```yaml
# config/deploy.yml
healthcheck:
  path: /up
  port: 3000
  interval: 10s
  max_attempts: 10
```

```ruby
# config/routes.rb
Rails.application.routes.draw do
  get "up" => "rails/health#show", as: :rails_health_check
end
```

### Rolling Deployment Flow

```
1. Build new image
2. Push to registry
3. Pull on each server (one at a time)
4. Start new container
5. Wait for health check to pass
6. Traefik routes traffic to new container
7. Stop old container
8. Move to next server
```

## Health Check Patterns

### Basic Health Check

```ruby
# config/routes.rb
get "up" => "rails/health#show"
```

### Custom Health Check

```ruby
# app/controllers/health_controller.rb
class HealthController < ApplicationController
  skip_before_action :authenticate_user!, if: -> { action_name == "show" }

  def show
    checks = {
      database: database_connected?,
      redis: redis_connected?,
      disk_space: sufficient_disk_space?
    }

    if checks.values.all?
      render json: { status: "ok", checks: checks }, status: :ok
    else
      render json: { status: "error", checks: checks }, status: :service_unavailable
    end
  end

  private

  def database_connected?
    ActiveRecord::Base.connection.execute("SELECT 1")
    true
  rescue StandardError
    false
  end

  def redis_connected?
    Redis.current.ping == "PONG"
  rescue StandardError
    false
  end

  def sufficient_disk_space?
    available = `df -k / | tail -1 | awk '{print $4}'`.to_i
    available > 1_000_000  # 1GB minimum
  rescue StandardError
    false
  end
end
```

```ruby
# config/routes.rb
get "up" => "health#show"
```

### Health Check with Dependencies

```yaml
# config/deploy.yml
healthcheck:
  path: /up
  port: 3000
  interval: 10s
  max_attempts: 20    # More attempts for slow boots
  cmd: |
    curl -f http://localhost:3000/up && \
    curl -f http://localhost:3000/sidekiq/health
```

## Rolling Update Strategies

### Default: One Server at a Time

```yaml
# config/deploy.yml
servers:
  web:
    hosts:
      - 192.168.1.1
      - 192.168.1.2
      - 192.168.1.3
    # Deploys to one host, waits for healthy, then next
```

### Parallel Deployment (Faster, Higher Risk)

```bash
# Deploy to all servers simultaneously
kamal deploy --parallel
```

### Canary Deployment

```yaml
# config/deploy.yml
servers:
  web:
    hosts:
      - 192.168.1.1    # Canary server (first)
      - 192.168.1.2
      - 192.168.1.3
```

```bash
# Deploy to canary only
kamal deploy --hosts=192.168.1.1

# Monitor, then deploy to rest
kamal deploy --hosts=192.168.1.2,192.168.1.3
```

## Database Migrations

### Zero-Downtime Migration Strategy

```ruby
# Step 1: Add new column (backward compatible)
class AddNewColumnToUsers < ActiveRecord::Migration[8.0]
  def change
    add_column :users, :new_field, :string
  end
end

# Step 2: Deploy code that writes to both old and new
# Step 3: Backfill data
# Step 4: Deploy code that reads from new
# Step 5: Remove old column (separate deploy)
```

### Pre-Deployment Migrations

```yaml
# config/deploy.yml
# Migrations run before the rolling update starts
```

```bash
# Run migrations separately before deploy
kamal app exec "bin/rails db:migrate"
kamal deploy --skip-migrations
```

### Strong Migrations Gem

```ruby
# Gemfile
gem "strong_migrations"
```

```ruby
# config/initializers/strong_migrations.rb
StrongMigrations.auto_analyze = true
StrongMigrations.start_after = 20240101000000

# Catches dangerous migrations:
# - Removing column without ignore
# - Adding index without concurrently
# - Changing column type
```

### Safe Index Addition

```ruby
class AddIndexToUsersEmail < ActiveRecord::Migration[8.0]
  disable_ddl_transaction!

  def change
    add_index :users, :email, algorithm: :concurrently
  end
end
```

### Safe Column Removal

```ruby
# Step 1: Stop reading/writing in code
# Step 2: Deploy

# Step 3: Remove column
class RemoveOldFieldFromUsers < ActiveRecord::Migration[8.0]
  def change
    safety_assured { remove_column :users, :old_field }
  end
end
```

## Rollback Strategies

### Quick Rollback

```bash
# Rollback to previous version
kamal rollback

# Rollback to specific version
kamal rollback --version=abc123
```

### Database Rollback

```bash
# If migration caused issues
kamal app exec "bin/rails db:rollback"

# Then rollback app
kamal rollback
```

### Asset Rollback

```bash
# Assets are baked into image, rollback includes them
kamal rollback
```

## Monitoring During Deploy

### Real-time Logs

```bash
# Watch logs during deploy
kamal logs -f

# Watch specific server
kamal logs -f --hosts=192.168.1.1
```

### Health Check Status

```bash
# Check container health
kamal details

# Check Traefik routing
kamal traefik logs
```

### Deployment Status

```bash
# Current deployment info
kamal version

# All running containers
kamal app containers
```

## Advanced Patterns

### Blue-Green Deployment

```yaml
# config/deploy.yml
servers:
  web:
    hosts:
      - 192.168.1.1  # Blue
      - 192.168.1.2  # Blue
  web-green:
    hosts:
      - 192.168.1.3  # Green
      - 192.168.1.4  # Green
    labels:
      traefik.enable: false  # Initially disabled
```

```bash
# Deploy to green
kamal deploy --roles=web-green

# Test green environment
# Switch traffic (update labels)
# Retire blue
```

### Graceful Shutdown

```ruby
# config/puma.rb
on_worker_shutdown do
  # Finish processing current requests
  sleep 5
end

# Or with Thruster
# Thruster handles graceful shutdown automatically
```

### Maintenance Mode

```ruby
# app/controllers/application_controller.rb
before_action :check_maintenance_mode

def check_maintenance_mode
  if ENV["MAINTENANCE_MODE"] == "true"
    render file: Rails.root.join("public/maintenance.html"),
           layout: false,
           status: :service_unavailable
  end
end
```

```bash
# Enable maintenance mode
kamal env push MAINTENANCE_MODE=true
kamal app restart

# Deploy
kamal deploy

# Disable maintenance mode
kamal env push MAINTENANCE_MODE=false
kamal app restart
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No health check | Deploy blindly | Configure /up endpoint |
| Destructive migrations | Downtime/data loss | Use multi-step migrations |
| Long boot times | Extended deployment | Optimize boot, increase attempts |
| No rollback plan | Stuck with bugs | Test rollback procedure |
| Skipping staging | Production surprises | Always test in staging first |

## Related Files

- [setup.md](./setup.md): Initial Kamal setup
- [configuration.md](./configuration.md): Health check config
- [../database/migrations.md](../database/migrations.md): Safe migration patterns

## References

- [Kamal Rolling Deployments](https://kamal-deploy.org/)
- [Strong Migrations](https://github.com/ankane/strong_migrations)
- [Traefik Health Checks](https://doc.traefik.io/traefik/routing/services/#health-check)
