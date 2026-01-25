# ActionCable Setup

## Overview

ActionCable integrates WebSockets with Rails, enabling real-time features. Rails 8 introduces Solid Cable as the default adapter, eliminating Redis dependency for simpler deployments.

## When to Use

- When configuring WebSocket infrastructure
- When setting up development vs production environments
- When choosing between Solid Cable and Redis
- When customizing cable configuration

## Quick Start

### Rails 8 Default Setup (Solid Cable)

```yaml
# config/cable.yml
development:
  adapter: solid_cable
  polling_interval: 0.1.seconds
  message_retention: 1.day

test:
  adapter: test

production:
  adapter: solid_cable
  polling_interval: 0.1.seconds
  message_retention: 1.day
```

### Database Migration for Solid Cable

```bash
bin/rails solid_cable:install
bin/rails db:migrate
```

```ruby
# db/migrate/xxx_create_solid_cable_tables.rb
class CreateSolidCableTables < ActiveRecord::Migration[8.0]
  def change
    create_table :solid_cable_messages do |t|
      t.binary :channel, null: false, limit: 1024
      t.binary :payload, null: false, limit: 536_870_912
      t.datetime :created_at, null: false
      t.index :channel
      t.index :created_at
    end
  end
end
```

## Configuration Options

### Solid Cable Configuration

```yaml
# config/cable.yml
production:
  adapter: solid_cable
  polling_interval: 0.1.seconds   # How often to poll for messages
  message_retention: 1.day        # How long to keep messages
  silence_polling: true           # Suppress polling logs
  connects_to:
    database:
      writing: cable              # Use separate database
```

### Multi-database Setup

```ruby
# config/database.yml
production:
  primary:
    <<: *default
    database: myapp_production
  cable:
    <<: *default
    database: myapp_cable_production
    migrations_paths: db/cable_migrate
```

### Redis Configuration (High Scale)

```yaml
# config/cable.yml
production:
  adapter: redis
  url: <%= ENV.fetch("REDIS_URL") { "redis://localhost:6379/1" } %>
  channel_prefix: myapp_production
```

```ruby
# config/initializers/redis.rb
if Rails.env.production?
  $redis = Redis.new(
    url: ENV.fetch("REDIS_URL"),
    ssl_params: { verify_mode: OpenSSL::SSL::VERIFY_NONE }
  )
end
```

## Main Patterns

### Pattern 1: Environment-Specific Configuration

```yaml
# config/cable.yml
development:
  adapter: solid_cable
  polling_interval: 0.1.seconds
  message_retention: 1.hour

test:
  adapter: test

staging:
  adapter: solid_cable
  polling_interval: 0.1.seconds
  message_retention: 6.hours

production:
  adapter: <%= ENV.fetch("CABLE_ADAPTER", "solid_cable") %>
  <% if ENV["CABLE_ADAPTER"] == "redis" %>
  url: <%= ENV.fetch("REDIS_URL") %>
  channel_prefix: myapp_production
  <% else %>
  polling_interval: 0.1.seconds
  message_retention: 1.day
  <% end %>
```

### Pattern 2: JavaScript Client Setup

```javascript
// app/javascript/channels/consumer.js
import { createConsumer } from "@rails/actioncable"

export default createConsumer()
```

```javascript
// For custom WebSocket URL
import { createConsumer } from "@rails/actioncable"

const getWebSocketURL = () => {
  const token = document.querySelector('meta[name="cable-token"]')?.content
  return `/cable?token=${token}`
}

export default createConsumer(getWebSocketURL)
```

### Pattern 3: Allowed Request Origins

```ruby
# config/environments/production.rb
config.action_cable.allowed_request_origins = [
  "https://myapp.com",
  "https://www.myapp.com",
  /https:\/\/.*\.myapp\.com/
]

# Or allow all (not recommended for production)
# config.action_cable.disable_request_forgery_protection = true
```

### Pattern 4: Mount Point Configuration

```ruby
# config/routes.rb
Rails.application.routes.draw do
  # Default mount point
  mount ActionCable.server => "/cable"

  # Custom mount point
  # mount ActionCable.server => "/websocket"
end
```

### Pattern 5: Worker Pool Configuration

```ruby
# config/environments/production.rb
config.action_cable.worker_pool_size = ENV.fetch("CABLE_WORKERS", 4).to_i
```

## Adapter Comparison

| Feature | Solid Cable | Redis | PostgreSQL |
|---------|-------------|-------|------------|
| Setup complexity | Low | Medium | Low |
| Additional service | None | Redis server | None |
| Latency | ~100ms | ~1ms | ~50ms |
| Multi-server | Limited | Yes | Yes |
| Message persistence | Yes | Optional | Yes |
| Cost | Free | Redis hosting | Free |
| Best for | Small-medium apps | Large scale | Medium apps |

## Health Check

```ruby
# app/controllers/health_controller.rb
class HealthController < ApplicationController
  def cable
    # Test ActionCable connection
    ActionCable.server.broadcast("health_check", { status: "ok" })
    render json: { cable: "healthy" }
  rescue => e
    render json: { cable: "unhealthy", error: e.message }, status: :service_unavailable
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Redis in development | Unnecessary complexity | Use Solid Cable |
| Missing allowed_request_origins | Security vulnerability | Configure explicitly |
| Small worker pool | Connection bottleneck | Tune based on load |
| Polling interval too low | Database load | Use 0.1s minimum |

## Related Skills

- [channels.md](./channels.md): Creating channels
- [connections.md](./connections.md): Connection authentication
- [deployment.md](./deployment.md): Production deployment
- [../turbo-streams/broadcasting.md](../turbo-streams/broadcasting.md): Turbo Streams integration

## References

- [Action Cable Overview](https://guides.rubyonrails.org/action_cable_overview.html)
- [Solid Cable GitHub](https://github.com/rails/solid_cable)
- [Rails 8 Release Notes](https://guides.rubyonrails.org/8_0_release_notes.html)
