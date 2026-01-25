# ActionCable Deployment

## Overview

Deploying ActionCable requires consideration of WebSocket handling, adapter selection, and scaling strategies. Rails 8's Solid Cable simplifies deployment, while Redis remains the choice for high-scale applications.

## When to Use

- When deploying ActionCable to production
- When scaling WebSocket connections
- When configuring load balancers for WebSockets
- When choosing between Solid Cable and Redis

## Quick Start

### Solid Cable Production Setup

```yaml
# config/cable.yml
production:
  adapter: solid_cable
  polling_interval: 0.1.seconds
  message_retention: 1.day
  silence_polling: true
```

```ruby
# config/environments/production.rb
config.action_cable.url = "wss://#{ENV['DOMAIN']}/cable"
config.action_cable.allowed_request_origins = [
  "https://#{ENV['DOMAIN']}"
]
```

### Redis Production Setup

```yaml
# config/cable.yml
production:
  adapter: redis
  url: <%= ENV.fetch("REDIS_URL") %>
  channel_prefix: myapp_production
```

## Main Patterns

### Pattern 1: Kamal Deployment with Solid Cable

```yaml
# config/deploy.yml
service: myapp

servers:
  web:
    hosts:
      - 192.168.1.1
    labels:
      traefik.http.routers.myapp.rule: Host(`myapp.com`)

env:
  clear:
    RAILS_ENV: production
  secret:
    - RAILS_MASTER_KEY

accessories:
  # No Redis needed with Solid Cable!
```

```ruby
# Procfile
web: bundle exec puma -C config/puma.rb
```

### Pattern 2: Kamal Deployment with Redis

```yaml
# config/deploy.yml
service: myapp

servers:
  web:
    hosts:
      - 192.168.1.1

accessories:
  redis:
    image: redis:7-alpine
    host: 192.168.1.2
    port: 6379
    directories:
      - data:/data
    cmd: redis-server --appendonly yes

env:
  clear:
    RAILS_ENV: production
    REDIS_URL: redis://192.168.1.2:6379/1
  secret:
    - RAILS_MASTER_KEY
```

### Pattern 3: Nginx WebSocket Configuration

```nginx
# /etc/nginx/sites-available/myapp
upstream app {
    server 127.0.0.1:3000;
}

upstream cable {
    server 127.0.0.1:3000;
}

server {
    listen 443 ssl http2;
    server_name myapp.com;

    ssl_certificate /etc/letsencrypt/live/myapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/myapp.com/privkey.pem;

    # Regular HTTP requests
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket connections
    location /cable {
        proxy_pass http://cable;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings for WebSocket
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

### Pattern 4: AWS ALB Configuration

```ruby
# config/environments/production.rb
config.action_cable.url = "wss://myapp.com/cable"
config.action_cable.allowed_request_origins = [
  "https://myapp.com",
  "https://www.myapp.com"
]
```

```yaml
# AWS ALB Target Group Settings
# - Protocol: HTTP
# - Health check path: /health
# - Deregistration delay: 300 seconds
# - Stickiness: Enabled (for WebSocket)

# ALB Listener Rule for WebSocket
# - Path pattern: /cable*
# - Forward to: web-target-group
# - Idle timeout: 3600 seconds (1 hour)
```

### Pattern 5: Horizontal Scaling with Redis

```yaml
# config/cable.yml
production:
  adapter: redis
  url: <%= ENV.fetch("REDIS_URL") %>
  channel_prefix: myapp_production

# config/database.yml - Use separate Redis for cable
production:
  cache:
    url: <%= ENV.fetch("REDIS_CACHE_URL") %>
  cable:
    url: <%= ENV.fetch("REDIS_CABLE_URL") %>
```

```ruby
# config/initializers/redis.rb
CABLE_REDIS = ConnectionPool.new(size: 5) do
  Redis.new(
    url: ENV.fetch("REDIS_CABLE_URL"),
    timeout: 1,
    reconnect_attempts: 3
  )
end
```

### Pattern 6: Connection Pool Tuning

```ruby
# config/puma.rb
workers ENV.fetch("WEB_CONCURRENCY") { 2 }
threads_count = ENV.fetch("RAILS_MAX_THREADS") { 5 }
threads threads_count, threads_count

# Adjust ActionCable worker pool based on Puma configuration
# app/config/environments/production.rb
config.action_cable.worker_pool_size = ENV.fetch("CABLE_WORKERS") do
  # Formula: workers * threads * 1.5 (for headroom)
  (ENV.fetch("WEB_CONCURRENCY", 2).to_i * ENV.fetch("RAILS_MAX_THREADS", 5).to_i * 1.5).ceil
end
```

### Pattern 7: Health Checks

```ruby
# app/controllers/health_controller.rb
class HealthController < ApplicationController
  skip_before_action :authenticate_user!, if: -> { defined?(authenticate_user!) }

  def show
    checks = {
      database: database_connected?,
      cable: cable_working?
    }

    if checks.values.all?
      render json: { status: "healthy", checks: checks }
    else
      render json: { status: "unhealthy", checks: checks }, status: :service_unavailable
    end
  end

  private

  def database_connected?
    ActiveRecord::Base.connection.execute("SELECT 1")
    true
  rescue
    false
  end

  def cable_working?
    case ActionCable.server.config.cable[:adapter]
    when "redis"
      Redis.new(url: ENV["REDIS_URL"]).ping == "PONG"
    when "solid_cable"
      SolidCable::Message.count >= 0
      true
    else
      true
    end
  rescue
    false
  end
end

# config/routes.rb
get "/health", to: "health#show"
```

### Pattern 8: Docker Compose Development

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - RAILS_ENV=development
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      - db
      - redis

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=password

volumes:
  redis_data:
  postgres_data:
```

## Scaling Considerations

| Scale | Recommended Setup | Notes |
|-------|------------------|-------|
| < 1000 connections | Solid Cable, single server | Simplest setup |
| 1000-10000 | Solid Cable, multiple servers | Add sticky sessions |
| 10000-100000 | Redis, clustered | Use Redis Cluster |
| > 100000 | Redis Cluster + AnyCable | Consider AnyCable |

## Monitoring

```ruby
# config/initializers/action_cable_monitoring.rb
ActiveSupport::Notifications.subscribe("perform_action.action_cable") do |*args|
  event = ActiveSupport::Notifications::Event.new(*args)

  Rails.logger.info({
    event: "action_cable.perform",
    channel: event.payload[:channel_class],
    action: event.payload[:action],
    duration: event.duration
  }.to_json)
end

ActiveSupport::Notifications.subscribe("transmit.action_cable") do |*args|
  event = ActiveSupport::Notifications::Event.new(*args)
  StatsD.increment("action_cable.transmit")
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No sticky sessions with multi-server | Connection drops | Enable ALB stickiness |
| Missing WebSocket proxy headers | Connection failures | Configure Upgrade headers |
| Single Redis instance at scale | Bottleneck | Use Redis Cluster |
| No connection limits | Resource exhaustion | Set worker pool limits |
| Missing health checks | Silent failures | Add /health endpoint |

## Related Skills

- [setup.md](./setup.md): ActionCable configuration
- [../../deploy/SKILL.md](../../deploy/SKILL.md): Kamal deployment

## References

- [Action Cable Overview](https://guides.rubyonrails.org/action_cable_overview.html)
- [Solid Cable GitHub](https://github.com/rails/solid_cable)
- [AnyCable](https://anycable.io/) - For extreme scale
- [Kamal Documentation](https://kamal-deploy.org/)
