# Centralized Logging

## Overview

Production logging requires structured output, log aggregation, and proper filtering. Rails 8 applications should log to STDOUT for container compatibility with centralized log collection.

## When to Use

- When deploying containerized applications
- When aggregating logs from multiple servers
- When debugging production issues
- When implementing audit trails

## Quick Start

### Basic Production Logging

```ruby
# config/environments/production.rb
config.log_level = ENV.fetch("LOG_LEVEL", "info").to_sym
config.log_tags = [:request_id]
config.logger = ActiveSupport::Logger.new($stdout)
  .tap { |logger| logger.formatter = Logger::Formatter.new }
  .then { |logger| ActiveSupport::TaggedLogging.new(logger) }
```

### Environment Variable

```yaml
# config/deploy.yml
env:
  clear:
    RAILS_LOG_TO_STDOUT: true
    LOG_LEVEL: info
```

## Structured Logging

### JSON Logger Setup

```ruby
# Gemfile
gem "lograge"
gem "logstash-event"
```

```ruby
# config/initializers/lograge.rb
Rails.application.configure do
  config.lograge.enabled = true
  config.lograge.formatter = Lograge::Formatters::Json.new

  config.lograge.custom_options = lambda do |event|
    {
      request_id: event.payload[:request_id],
      user_id: event.payload[:user_id],
      ip: event.payload[:ip],
      host: event.payload[:host],
      params: event.payload[:params].except("controller", "action", "format")
    }
  end

  config.lograge.custom_payload do |controller|
    {
      user_id: controller.current_user&.id,
      ip: controller.request.remote_ip,
      host: controller.request.host
    }
  end
end
```

### Sample JSON Output

```json
{
  "method": "GET",
  "path": "/posts/123",
  "format": "html",
  "controller": "PostsController",
  "action": "show",
  "status": 200,
  "duration": 52.34,
  "view": 34.12,
  "db": 8.45,
  "request_id": "abc-123-def",
  "user_id": 42,
  "ip": "1.2.3.4",
  "host": "myapp.com",
  "@timestamp": "2024-01-15T12:34:56.789Z"
}
```

## Log Aggregation Services

### Papertrail

```ruby
# Gemfile
gem "remote_syslog_logger"
```

```ruby
# config/environments/production.rb
config.logger = RemoteSyslogLogger.new(
  ENV["PAPERTRAIL_HOST"],
  ENV["PAPERTRAIL_PORT"],
  program: "rails",
  local_hostname: ENV["HOSTNAME"] || `hostname`.strip
)
```

### Logtail (Better Stack)

```ruby
# Gemfile
gem "logtail-rails"
```

```ruby
# config/initializers/logtail.rb
Logtail.config.source_token = ENV["LOGTAIL_SOURCE_TOKEN"]
```

### Datadog

```ruby
# Gemfile
gem "ddtrace"
gem "dogstatsd-ruby"
```

```ruby
# config/initializers/datadog.rb
Datadog.configure do |c|
  c.tracing.enabled = true
  c.tracing.instrument :rails
  c.tracing.instrument :active_record
  c.tracing.instrument :redis

  c.runtime_metrics.enabled = true
  c.runtime_metrics.statsd = Datadog::Statsd.new(
    ENV["DD_AGENT_HOST"],
    ENV["DD_DOGSTATSD_PORT"]
  )
end
```

## Docker/Kamal Logging

### STDOUT Configuration

```ruby
# config/environments/production.rb
if ENV["RAILS_LOG_TO_STDOUT"].present?
  logger = ActiveSupport::Logger.new($stdout)
  logger.formatter = config.log_formatter
  config.logger = ActiveSupport::TaggedLogging.new(logger)
end
```

### Docker Log Drivers

```yaml
# docker-compose.yml
services:
  web:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### Kamal Log Viewing

```bash
# View logs
kamal logs

# Follow logs
kamal logs -f

# Filter by host
kamal logs --hosts=192.168.1.1
```

## Log Levels

### Configuration

```ruby
# config/environments/production.rb
config.log_level = ENV.fetch("LOG_LEVEL", "info").to_sym
```

### Level Guidelines

| Level | Use For |
|-------|---------|
| `debug` | Detailed debugging info (development only) |
| `info` | Normal operations (default for production) |
| `warn` | Potentially harmful situations |
| `error` | Error conditions |
| `fatal` | Unrecoverable errors |

### Dynamic Log Level

```ruby
# Change log level at runtime
Rails.logger.level = Logger::DEBUG

# Or via environment
LOG_LEVEL=debug kamal app exec "bin/rails server"
```

## Request Logging

### Request ID Tracking

```ruby
# config/environments/production.rb
config.log_tags = [:request_id]
```

### Custom Tags

```ruby
config.log_tags = [
  :request_id,
  -> request { request.session[:user_id] },
  -> request { request.headers["X-Tenant-ID"] }
]
```

### Application Logging

```ruby
# In controllers/services
Rails.logger.info("Processing order", {
  order_id: @order.id,
  user_id: current_user.id,
  amount: @order.total
})
```

## Background Job Logging

### Solid Queue

```ruby
# config/solid_queue.yml
production:
  workers:
    - queues: "*"
      threads: 5
      processes: 2

# Logs to Rails.logger automatically
```

### Sidekiq

```ruby
# config/initializers/sidekiq.rb
Sidekiq.configure_server do |config|
  config.logger = Sidekiq::Logger.new($stdout)
  config.logger.level = Logger::INFO
end
```

## Audit Logging

### Audit Trail Model

```ruby
# app/models/audit_log.rb
class AuditLog < ApplicationRecord
  belongs_to :user, optional: true
  belongs_to :auditable, polymorphic: true, optional: true

  scope :recent, -> { order(created_at: :desc).limit(100) }
end

# Migration
class CreateAuditLogs < ActiveRecord::Migration[8.0]
  def change
    create_table :audit_logs do |t|
      t.references :user, foreign_key: true
      t.references :auditable, polymorphic: true
      t.string :action
      t.jsonb :metadata
      t.string :ip_address
      t.string :user_agent
      t.timestamps
    end
  end
end
```

### Controller Integration

```ruby
# app/controllers/concerns/auditable.rb
module Auditable
  extend ActiveSupport::Concern

  included do
    after_action :log_audit, if: :auditable_action?
  end

  private

  def log_audit
    AuditLog.create!(
      user: current_user,
      auditable: @resource,
      action: "#{controller_name}##{action_name}",
      metadata: audit_metadata,
      ip_address: request.remote_ip,
      user_agent: request.user_agent
    )
  end

  def audit_metadata
    {
      params: request.params.except("controller", "action", "authenticity_token"),
      request_id: request.request_id
    }
  end

  def auditable_action?
    %w[create update destroy].include?(action_name)
  end
end
```

## Log Filtering

### Parameter Filtering

```ruby
# config/initializers/filter_parameter_logging.rb
Rails.application.config.filter_parameters += [
  :password,
  :password_confirmation,
  :credit_card,
  :ssn,
  :secret,
  :token,
  :_key,
  :crypt,
  :salt,
  :certificate,
  :otp,
  :pin
]
```

### SQL Query Filtering

```ruby
# Mask sensitive values in SQL logs
config.active_record.filter_attributes = [
  :email, :phone, :ssn
]
```

## Health Check Logging

### Skip Health Check Logs

```ruby
# config/initializers/lograge.rb
Rails.application.configure do
  config.lograge.ignore_actions = [
    "Rails::HealthController#show",
    "HealthController#show"
  ]
end
```

## Log Rotation

### Logrotate Configuration

```conf
# /etc/logrotate.d/myapp
/var/log/myapp/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    copytruncate
}
```

### Docker/Container Rotation

```yaml
# docker-compose.yml
services:
  web:
    logging:
      driver: json-file
      options:
        max-size: "50m"
        max-file: "5"
```

## Monitoring Integration

### Sentry Breadcrumbs

```ruby
# config/initializers/sentry.rb
Sentry.init do |config|
  config.breadcrumbs_logger = [:active_support_logger, :http_logger]
end
```

### Custom Metrics from Logs

```ruby
# Log with metrics data
Rails.logger.info({
  event: "order_completed",
  order_id: @order.id,
  amount: @order.total,
  duration_ms: (Time.current - @start_time) * 1000
}.to_json)
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Logging to files in containers | Logs lost on restart | Log to STDOUT |
| Unstructured logs | Hard to parse/search | Use JSON format |
| Logging sensitive data | Security breach | Filter parameters |
| No request ID | Can't trace requests | Enable request_id tagging |
| Debug level in production | Performance impact | Use info or higher |

## Related Files

- [sentry.md](./sentry.md): Error tracking
- [performance.md](./performance.md): APM monitoring
- [../kamal/setup.md](../kamal/setup.md): Deployment logging

## References

- [Rails Logging](https://guides.rubyonrails.org/debugging_rails_applications.html#the-logger)
- [Lograge](https://github.com/roidrage/lograge)
- [12 Factor: Logs](https://12factor.net/logs)
