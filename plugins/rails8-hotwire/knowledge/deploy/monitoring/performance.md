# Performance Monitoring (APM)

## Overview

Application Performance Monitoring (APM) tracks request times, database queries, external calls, and resource usage. Essential for identifying bottlenecks and maintaining SLAs.

## When to Use

- When monitoring production performance
- When identifying slow endpoints
- When debugging N+1 queries
- When tracking deployment impact

## Quick Start

### Choose Your APM

| Service | Strengths | Pricing |
|---------|-----------|---------|
| **Sentry Performance** | Integrated with errors | Free tier available |
| **New Relic** | Comprehensive, mature | $0-$0.30/GB |
| **Scout APM** | Rails-focused, simple | $79+/month |
| **Skylight** | Rails-specific, lightweight | $50+/month |
| **Datadog** | Full observability | $15+/host |

## Sentry Performance

### Setup (with Error Tracking)

```ruby
# Gemfile
gem "sentry-ruby"
gem "sentry-rails"
```

```ruby
# config/initializers/sentry.rb
Sentry.init do |config|
  config.dsn = ENV["SENTRY_DSN"]
  config.traces_sample_rate = 0.2
  config.profiles_sample_rate = 0.2

  # Custom sampling
  config.traces_sampler = lambda do |context|
    transaction = context[:transaction_context][:name]

    case transaction
    when /health/i then 0.0
    when /admin/i then 1.0
    else 0.2
    end
  end
end
```

## New Relic

### Installation

```ruby
# Gemfile
gem "newrelic_rpm"
```

```yaml
# config/newrelic.yml
common: &default_settings
  license_key: <%= ENV["NEW_RELIC_LICENSE_KEY"] %>
  app_name: <%= ENV.fetch("NEW_RELIC_APP_NAME", "MyApp") %>
  log_level: info
  distributed_tracing:
    enabled: true
  application_logging:
    enabled: true
    forwarding:
      enabled: true
    metrics:
      enabled: true
    local_decorating:
      enabled: true

development:
  <<: *default_settings
  monitor_mode: false

staging:
  <<: *default_settings
  app_name: MyApp (Staging)

production:
  <<: *default_settings
```

### Custom Instrumentation

```ruby
# app/services/payment_service.rb
class PaymentService
  include ::NewRelic::Agent::MethodTracer

  def process_payment(order)
    # Method automatically traced
    gateway.charge(order.total)
  end

  add_method_tracer :process_payment, "Custom/PaymentService/process_payment"
end
```

### Custom Metrics

```ruby
# Record custom metric
::NewRelic::Agent.record_metric("Custom/Orders/Total", order.total)

# Record custom event
::NewRelic::Agent.record_custom_event("OrderCompleted", {
  order_id: order.id,
  amount: order.total,
  items: order.items.count
})
```

## Scout APM

### Installation

```ruby
# Gemfile
gem "scout_apm"
```

```ruby
# config/scout_apm.yml
common: &defaults
  monitor: true
  name: <%= ENV["SCOUT_NAME"] || "MyApp" %>
  key: <%= ENV["SCOUT_KEY"] %>

production:
  <<: *defaults

staging:
  <<: *defaults
  name: MyApp (Staging)

development:
  <<: *defaults
  monitor: false
```

### Custom Context

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  before_action :set_scout_context

  private

  def set_scout_context
    ScoutApm::Context.add_user(
      id: current_user&.id,
      email: current_user&.email
    )
  end
end
```

## Skylight

### Installation

```ruby
# Gemfile
gem "skylight"
```

```bash
bundle exec skylight setup
# Follow prompts to configure
```

### Custom Instrumentation

```ruby
class PaymentService
  include Skylight::Helpers

  instrument_method
  def process_payment(order)
    Skylight.instrument(title: "External Payment API") do
      gateway.charge(order.total)
    end
  end
end
```

## Datadog APM

### Installation

```ruby
# Gemfile
gem "ddtrace"
gem "dogstatsd-ruby"
```

```ruby
# config/initializers/datadog.rb
Datadog.configure do |c|
  c.service = ENV.fetch("DD_SERVICE", "myapp")
  c.env = Rails.env
  c.version = ENV.fetch("GIT_SHA", "unknown")

  c.tracing.enabled = true
  c.tracing.instrument :rails
  c.tracing.instrument :active_record
  c.tracing.instrument :redis
  c.tracing.instrument :faraday
  c.tracing.instrument :sidekiq

  c.runtime_metrics.enabled = true
end
```

### Docker Compose with Agent

```yaml
# docker-compose.yml
services:
  datadog:
    image: datadog/agent:latest
    environment:
      - DD_API_KEY=${DD_API_KEY}
      - DD_APM_ENABLED=true
      - DD_APM_NON_LOCAL_TRAFFIC=true
    ports:
      - "8126:8126"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /proc/:/host/proc/:ro
      - /sys/fs/cgroup:/host/sys/fs/cgroup:ro
```

## Custom Metrics

### StatsD Integration

```ruby
# config/initializers/statsd.rb
require "statsd"

STATSD = Statsd.new(
  ENV.fetch("STATSD_HOST", "localhost"),
  ENV.fetch("STATSD_PORT", 8125)
)
```

```ruby
# Usage
STATSD.increment("orders.created")
STATSD.gauge("orders.pending", Order.pending.count)
STATSD.timing("orders.processing_time", duration_ms)

STATSD.time("api.external_call") do
  external_api.call
end
```

### ActiveSupport Instrumentation

```ruby
# app/controllers/orders_controller.rb
def create
  ActiveSupport::Notifications.instrument("order.create", order_id: @order.id) do
    @order.save
  end
end
```

```ruby
# config/initializers/instrumentation.rb
ActiveSupport::Notifications.subscribe("order.create") do |*args|
  event = ActiveSupport::Notifications::Event.new(*args)
  Rails.logger.info("Order created in #{event.duration}ms")
  STATSD.timing("orders.create", event.duration)
end
```

## Database Query Monitoring

### Query Analysis

```ruby
# config/initializers/query_monitor.rb
if Rails.env.production?
  ActiveSupport::Notifications.subscribe("sql.active_record") do |*args|
    event = ActiveSupport::Notifications::Event.new(*args)

    if event.duration > 100  # 100ms threshold
      Rails.logger.warn({
        event: "slow_query",
        duration_ms: event.duration.round(2),
        sql: event.payload[:sql].truncate(500),
        binds: event.payload[:type_casted_binds]&.first(5)
      }.to_json)
    end
  end
end
```

### N+1 Detection

```ruby
# Gemfile
gem "bullet", group: %i[development test]
```

```ruby
# config/environments/development.rb
config.after_initialize do
  Bullet.enable = true
  Bullet.alert = true
  Bullet.bullet_logger = true
  Bullet.rails_logger = true
end
```

## Memory Monitoring

### Memory Profiling

```ruby
# Gemfile
gem "memory_profiler", group: :development
```

```ruby
# Usage
report = MemoryProfiler.report do
  # Code to profile
end
report.pretty_print
```

### Production Memory Tracking

```ruby
# config/initializers/memory_monitor.rb
if Rails.env.production?
  Thread.new do
    loop do
      memory_mb = `ps -o rss= -p #{Process.pid}`.to_i / 1024
      STATSD.gauge("rails.memory_mb", memory_mb)
      sleep 60
    end
  end
end
```

## Health Endpoints

### Comprehensive Health Check

```ruby
# app/controllers/health_controller.rb
class HealthController < ApplicationController
  skip_before_action :authenticate_user!

  def show
    checks = {
      status: "ok",
      timestamp: Time.current.iso8601,
      checks: {
        database: database_check,
        redis: redis_check,
        memory: memory_check
      }
    }

    status = checks[:checks].values.all? { |c| c[:status] == "ok" } ? :ok : :service_unavailable
    render json: checks, status: status
  end

  private

  def database_check
    ActiveRecord::Base.connection.execute("SELECT 1")
    { status: "ok", latency_ms: measure { ActiveRecord::Base.connection.execute("SELECT 1") } }
  rescue => e
    { status: "error", message: e.message }
  end

  def redis_check
    Redis.current.ping
    { status: "ok", latency_ms: measure { Redis.current.ping } }
  rescue => e
    { status: "error", message: e.message }
  end

  def memory_check
    memory_mb = `ps -o rss= -p #{Process.pid}`.to_i / 1024
    { status: memory_mb < 1024 ? "ok" : "warning", memory_mb: memory_mb }
  end

  def measure
    start = Process.clock_gettime(Process::CLOCK_MONOTONIC)
    yield
    ((Process.clock_gettime(Process::CLOCK_MONOTONIC) - start) * 1000).round(2)
  end
end
```

## Kamal Integration

```yaml
# config/deploy.yml
env:
  clear:
    RAILS_ENV: production
  secret:
    - NEW_RELIC_LICENSE_KEY
    - SENTRY_DSN
    - DD_API_KEY
```

## Alerting

### Key Metrics to Alert On

| Metric | Warning | Critical |
|--------|---------|----------|
| Response time p95 | >500ms | >1000ms |
| Error rate | >1% | >5% |
| Apdex score | <0.9 | <0.7 |
| Memory usage | >80% | >95% |
| Database connections | >80% pool | >95% pool |

### Sample Alert Rules

```yaml
# New Relic NRQL Alert
SELECT average(duration) FROM Transaction
WHERE appName = 'MyApp'
FACET transactionName
SINCE 5 minutes ago
# Alert when > 500ms
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| 100% tracing | Cost and overhead | Sample 10-20% |
| No custom metrics | Missing business insight | Add key metrics |
| Alert fatigue | Ignored alerts | Tune thresholds |
| No baseline | Can't detect regressions | Establish benchmarks |
| Development APM | Wasted resources | Disable in dev |

## Related Files

- [logging.md](./logging.md): Logging configuration
- [sentry.md](./sentry.md): Error tracking
- [../kamal/zero-downtime.md](../kamal/zero-downtime.md): Deployment monitoring

## References

- [Rails Performance](https://guides.rubyonrails.org/v8.0/performance_testing.html)
- [New Relic Ruby](https://docs.newrelic.com/docs/apm/agents/ruby-agent/)
- [Sentry Performance](https://docs.sentry.io/product/performance/)
- [Scout APM](https://scoutapm.com/docs/ruby)
