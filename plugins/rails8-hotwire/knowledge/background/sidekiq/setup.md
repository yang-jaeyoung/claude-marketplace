# Sidekiq Setup

## Overview

Sidekiq is a high-performance Redis-backed background job processor. Use when you need advanced features like real-time dashboard, scheduled jobs, or high throughput beyond Solid Queue's capacity.

## When to Use

- High job volume (10,000+ jobs/hour)
- Need real-time monitoring dashboard
- Advanced scheduling requirements
- Already using Redis for caching
- Need commercial support

## Quick Start

### Installation

```ruby
# Gemfile
gem "sidekiq", "~> 7.0"

# Optional: For scheduled jobs
gem "sidekiq-cron"

# Optional: For unique jobs
gem "sidekiq-unique-jobs"
```

```bash
bundle install
```

### Redis Setup

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Configuration

```ruby
# config/application.rb
module MyApp
  class Application < Rails::Application
    # Set Sidekiq as Active Job adapter
    config.active_job.queue_adapter = :sidekiq
  end
end
```

```ruby
# config/initializers/sidekiq.rb
Sidekiq.configure_server do |config|
  config.redis = { url: ENV.fetch("REDIS_URL", "redis://localhost:6379/0") }

  # Set concurrency (number of threads)
  config.concurrency = 10

  # Optional: Configure error handling
  config.error_handlers << proc { |exception, context|
    Rails.logger.error "Sidekiq error: #{exception.message}"
    Sentry.capture_exception(exception) if defined?(Sentry)
  }
end

Sidekiq.configure_client do |config|
  config.redis = { url: ENV.fetch("REDIS_URL", "redis://localhost:6379/0") }
end
```

## Main Patterns

### Pattern 1: Basic Configuration File

```yaml
# config/sidekiq.yml
:concurrency: 10
:timeout: 25
:verbose: false

:queues:
  - [critical, 5]
  - [default, 3]
  - [low, 1]

# Production
:production:
  :concurrency: 25
  :queues:
    - [critical, 10]
    - [high, 5]
    - [default, 3]
    - [low, 1]

# Staging
:staging:
  :concurrency: 10
```

**Queue Priority Syntax:**
- `[critical, 5]` means critical jobs are 5x more likely to be picked than weight-1 queues
- Higher weight = higher priority

### Pattern 2: Environment Variables

```bash
# .env
REDIS_URL=redis://localhost:6379/0
SIDEKIQ_CONCURRENCY=10

# Production
REDIS_URL=redis://production-redis.example.com:6379/0
SIDEKIQ_CONCURRENCY=25
```

```ruby
# config/initializers/sidekiq.rb
redis_config = {
  url: ENV.fetch("REDIS_URL", "redis://localhost:6379/0"),
  network_timeout: 5,
  pool_timeout: 5
}

Sidekiq.configure_server do |config|
  config.redis = redis_config
  config.concurrency = ENV.fetch("SIDEKIQ_CONCURRENCY", 10).to_i
end

Sidekiq.configure_client do |config|
  config.redis = redis_config
end
```

### Pattern 3: Web UI (Dashboard)

```ruby
# config/routes.rb
require "sidekiq/web"

Rails.application.routes.draw do
  # Protect with authentication
  authenticate :user, ->(user) { user.admin? } do
    mount Sidekiq::Web => "/sidekiq"
  end

  # Or with basic auth
  Sidekiq::Web.use Rack::Auth::Basic do |username, password|
    ActiveSupport::SecurityUtils.secure_compare(
      ::Digest::SHA256.hexdigest(username),
      ::Digest::SHA256.hexdigest(ENV["SIDEKIQ_USERNAME"])
    ) & ActiveSupport::SecurityUtils.secure_compare(
      ::Digest::SHA256.hexdigest(password),
      ::Digest::SHA256.hexdigest(ENV["SIDEKIQ_PASSWORD"])
    )
  end
  mount Sidekiq::Web => "/sidekiq"
end
```

Visit `http://localhost:3000/sidekiq` to see:
- Queue sizes
- Job processing stats
- Failed jobs
- Retry counts
- Real-time throughput

### Pattern 4: Redis Connection Pool

```ruby
# config/initializers/sidekiq.rb
# For high-traffic applications
REDIS_POOL_SIZE = ENV.fetch("RAILS_MAX_THREADS", 5).to_i + 5

Sidekiq.configure_server do |config|
  config.redis = {
    url: ENV.fetch("REDIS_URL"),
    size: REDIS_POOL_SIZE,
    network_timeout: 5
  }
end

Sidekiq.configure_client do |config|
  config.redis = {
    url: ENV.fetch("REDIS_URL"),
    size: REDIS_POOL_SIZE
  }
end
```

### Pattern 5: Multiple Redis Instances

```ruby
# config/initializers/sidekiq.rb
# Use separate Redis for Sidekiq vs caching
Sidekiq.configure_server do |config|
  config.redis = { url: ENV["SIDEKIQ_REDIS_URL"] }
end

Sidekiq.configure_client do |config|
  config.redis = { url: ENV["SIDEKIQ_REDIS_URL"] }
end

# config/environments/production.rb
config.cache_store = :redis_cache_store, {
  url: ENV["CACHE_REDIS_URL"]
}
```

```bash
# .env.production
SIDEKIQ_REDIS_URL=redis://sidekiq-redis.example.com:6379/0
CACHE_REDIS_URL=redis://cache-redis.example.com:6379/0
```

### Pattern 6: Running Sidekiq

```bash
# Development: Run in foreground
bundle exec sidekiq

# With config file
bundle exec sidekiq -C config/sidekiq.yml

# Specific queues only
bundle exec sidekiq -q critical -q default

# Custom concurrency
bundle exec sidekiq -c 20

# Production: Run as daemon with systemd
# /etc/systemd/system/sidekiq.service
```

```ini
# /etc/systemd/system/sidekiq.service
[Unit]
Description=Sidekiq Background Worker
After=network.target redis.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/var/www/myapp/current
Environment=RAILS_ENV=production
ExecStart=/usr/local/bin/bundle exec sidekiq -C config/sidekiq.yml
ExecReload=/bin/kill -TSTP $MAINPID
Restart=on-failure
RestartSec=10

# Graceful shutdown (allow 90 seconds for jobs to finish)
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=90

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable sidekiq
sudo systemctl start sidekiq
sudo systemctl status sidekiq

# View logs
sudo journalctl -u sidekiq -f
```

### Pattern 7: Procfile (Heroku/Render)

```yaml
# Procfile
web: bundle exec puma -C config/puma.rb
worker: bundle exec sidekiq -C config/sidekiq.yml
```

```yaml
# render.yaml
services:
  - type: web
    name: myapp-web
    env: ruby
    buildCommand: bundle install
    startCommand: bundle exec puma -C config/puma.rb

  - type: worker
    name: myapp-worker
    env: ruby
    buildCommand: bundle install
    startCommand: bundle exec sidekiq -C config/sidekiq.yml
```

## Advanced Configuration

### Health Check Endpoint

```ruby
# config/initializers/sidekiq.rb
Sidekiq.configure_server do |config|
  config.on(:startup) do
    Rails.logger.info "Sidekiq server started"
  end

  config.on(:quiet) do
    Rails.logger.info "Sidekiq server quieting (graceful shutdown)"
  end

  config.on(:shutdown) do
    Rails.logger.info "Sidekiq server shut down"
  end
end
```

```ruby
# config/routes.rb
get "/health/sidekiq", to: proc {
  redis_alive = Sidekiq.redis(&:ping) == "PONG"
  status = redis_alive ? 200 : 503
  [status, { "Content-Type" => "application/json" }, [{ redis: redis_alive }.to_json]]
}
```

### Error Tracking

```ruby
# config/initializers/sidekiq.rb
Sidekiq.configure_server do |config|
  config.error_handlers << proc { |exception, context|
    # Send to error tracking service
    Sentry.capture_exception(
      exception,
      extra: {
        sidekiq: context,
        job_class: context[:job]["class"],
        job_args: context[:job]["args"]
      }
    )
  }
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Single Redis for everything | Contention, data loss risk | Separate Redis for jobs vs cache |
| No connection pool sizing | Connection exhaustion | Size pool = concurrency + buffer |
| Running without systemd | No auto-restart on crash | Use systemd or supervisor |
| No authentication on web UI | Security vulnerability | Protect with login or basic auth |
| Not handling SIGTERM | Lost jobs on deploy | Configure graceful shutdown |

```ruby
# Bad: Shared Redis for cache and jobs
REDIS_URL=redis://localhost:6379/0  # Everything

# Good: Separate databases
SIDEKIQ_REDIS_URL=redis://localhost:6379/1
CACHE_REDIS_URL=redis://localhost:6379/2
```

## Comparison with Solid Queue

| Feature | Sidekiq | Solid Queue |
|---------|---------|-------------|
| Infrastructure | Requires Redis | Uses existing DB |
| Setup complexity | Medium | Low |
| Performance | Excellent (100k+ jobs/hour) | Good (10k jobs/hour) |
| Dashboard | Built-in web UI | None |
| Scheduling | Advanced (sidekiq-cron) | Basic (cron syntax) |
| Cost | Free + paid tiers | Completely free |
| Memory usage | Lower (Redis) | Higher (database) |

## Related Skills

- [jobs](./jobs.md): Creating Sidekiq jobs
- [scheduling](./scheduling.md): Cron-like scheduled jobs
- [monitoring](./monitoring.md): Dashboard and metrics
- [solid-queue/setup](../solid-queue/setup.md): Alternative queue system

## References

- [Sidekiq Documentation](https://github.com/sidekiq/sidekiq/wiki)
- [Sidekiq Best Practices](https://github.com/sidekiq/sidekiq/wiki/Best-Practices)
- [Redis Installation](https://redis.io/docs/install/)
- [Sidekiq Pro/Enterprise](https://sidekiq.org/) (paid features)
