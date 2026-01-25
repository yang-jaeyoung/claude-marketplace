# Sentry Error Tracking

## Overview

Sentry provides real-time error tracking, performance monitoring, and release tracking for Rails applications. Essential for production debugging and issue triage.

## When to Use

- When deploying to production
- When tracking and triaging errors
- When monitoring performance
- When correlating errors with releases

## Quick Start

### Installation

```ruby
# Gemfile
gem "sentry-ruby"
gem "sentry-rails"
gem "sentry-sidekiq"  # If using Sidekiq
```

### Basic Configuration

```ruby
# config/initializers/sentry.rb
Sentry.init do |config|
  config.dsn = ENV["SENTRY_DSN"]
  config.breadcrumbs_logger = [:active_support_logger, :http_logger]

  config.traces_sample_rate = 0.1  # 10% of transactions
  config.profiles_sample_rate = 0.1  # 10% of traced transactions

  config.enabled_environments = %w[production staging]

  # Set release version
  config.release = ENV.fetch("GIT_SHA") { `git rev-parse HEAD`.strip }
end
```

### Environment Variable

```bash
# .kamal/secrets
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/123456
```

## Advanced Configuration

### Full Setup

```ruby
# config/initializers/sentry.rb
Sentry.init do |config|
  config.dsn = ENV["SENTRY_DSN"]

  # Environment
  config.environment = Rails.env
  config.enabled_environments = %w[production staging]

  # Release tracking
  config.release = ENV.fetch("GIT_SHA") { `git rev-parse HEAD`.strip }

  # Breadcrumbs
  config.breadcrumbs_logger = [:active_support_logger, :http_logger]
  config.max_breadcrumbs = 100

  # Sampling
  config.traces_sample_rate = ENV.fetch("SENTRY_TRACES_RATE", 0.1).to_f
  config.profiles_sample_rate = ENV.fetch("SENTRY_PROFILES_RATE", 0.1).to_f

  # Dynamic sampling
  config.traces_sampler = lambda do |sampling_context|
    transaction_context = sampling_context[:transaction_context]
    transaction_name = transaction_context[:name]

    case transaction_name
    when /health/i
      0.0  # Don't trace health checks
    when /admin/i
      1.0  # Trace all admin actions
    else
      0.1  # 10% for everything else
    end
  end

  # Filter sensitive data
  config.before_send = lambda do |event, hint|
    # Filter specific errors
    if hint[:exception].is_a?(ActiveRecord::RecordNotFound)
      return nil  # Don't send to Sentry
    end

    # Scrub sensitive params
    if event.request&.data
      event.request.data = filter_sensitive_params(event.request.data)
    end

    event
  end

  # User context
  config.before_send_transaction = lambda do |event, hint|
    event
  end
end

def filter_sensitive_params(data)
  return data unless data.is_a?(Hash)

  sensitive_keys = %w[password credit_card ssn token secret]
  data.transform_values do |value|
    if sensitive_keys.any? { |key| key.in?(value.to_s.downcase) }
      "[FILTERED]"
    else
      value
    end
  end
end
```

## User Context

### Set Current User

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  before_action :set_sentry_context

  private

  def set_sentry_context
    if current_user
      Sentry.set_user(
        id: current_user.id,
        email: current_user.email,
        username: current_user.name,
        ip_address: request.remote_ip
      )
    end
  end
end
```

### Additional Context

```ruby
# Add custom context
Sentry.set_context("order", {
  order_id: @order.id,
  status: @order.status,
  total: @order.total
})

# Add tags for filtering
Sentry.set_tags(
  tier: current_user.subscription_tier,
  feature_flag: "new_checkout"
)
```

## Manual Error Capture

### Capture Exception

```ruby
begin
  risky_operation
rescue => e
  Sentry.capture_exception(e, extra: {
    order_id: @order.id,
    attempt: retry_count
  })
  raise  # Re-raise if needed
end
```

### Capture Message

```ruby
Sentry.capture_message(
  "Rate limit exceeded",
  level: :warning,
  extra: {
    user_id: current_user.id,
    limit: rate_limit,
    requests: request_count
  }
)
```

## Performance Monitoring

### Transaction Tracking

```ruby
# Automatic for web requests and background jobs

# Manual transaction
Sentry.with_scope do |scope|
  scope.set_transaction_name("import_users")

  transaction = Sentry.start_transaction(name: "import_users", op: "task")

  begin
    # Child span
    span = transaction.start_child(op: "file.read", description: "Read CSV")
    data = File.read("users.csv")
    span.finish

    # Another span
    span = transaction.start_child(op: "db.insert", description: "Insert users")
    import_users(data)
    span.finish

    transaction.finish
  rescue => e
    transaction.set_status("internal_error")
    transaction.finish
    raise
  end
end
```

### Custom Instrumentation

```ruby
# app/services/payment_service.rb
class PaymentService
  def process(order)
    Sentry.with_child_span(op: "payment.process", description: "Process payment") do |span|
      span.set_data(:order_id, order.id)
      span.set_data(:amount, order.total)

      result = gateway.charge(order.total)

      span.set_data(:transaction_id, result.transaction_id)
      result
    end
  end
end
```

## Background Jobs

### Sidekiq Integration

```ruby
# config/initializers/sentry.rb
Sentry.init do |config|
  config.dsn = ENV["SENTRY_DSN"]
end

# Automatically captures job errors
```

### Solid Queue Integration

```ruby
# Sentry-rails automatically integrates with Active Job
class ImportJob < ApplicationJob
  def perform(user_id)
    Sentry.set_tags(job_class: self.class.name, user_id: user_id)

    # Job logic
  rescue => e
    Sentry.capture_exception(e)
    raise
  end
end
```

## Release Tracking

### Kamal Integration

```yaml
# config/deploy.yml
env:
  clear:
    SENTRY_ENVIRONMENT: production
  secret:
    - SENTRY_DSN
```

```bash
# .kamal/hooks/post-deploy
#!/bin/bash
curl -sL https://sentry.io/api/0/organizations/YOUR_ORG/releases/ \
  -H "Authorization: Bearer ${SENTRY_AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"version\": \"${KAMAL_VERSION}\",
    \"projects\": [\"myapp\"]
  }"
```

### GitHub Actions Integration

```yaml
# .github/workflows/deploy.yml
- name: Create Sentry release
  uses: getsentry/action-release@v1
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: your-org
    SENTRY_PROJECT: myapp
  with:
    environment: production
    version: ${{ github.sha }}
```

## Source Maps (JavaScript)

### Upload Source Maps

```yaml
# .github/workflows/deploy.yml
- name: Upload source maps
  run: |
    npx @sentry/cli sourcemaps upload \
      --org $SENTRY_ORG \
      --project myapp \
      --release ${{ github.sha }} \
      ./public/assets
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
```

### JavaScript SDK

```javascript
// app/javascript/application.js
import * as Sentry from "@sentry/browser"

Sentry.init({
  dsn: window.SENTRY_DSN,
  environment: window.RAILS_ENV,
  release: window.GIT_SHA,
  tracesSampleRate: 0.1
})
```

```erb
<!-- app/views/layouts/application.html.erb -->
<script>
  window.SENTRY_DSN = "<%= ENV['SENTRY_DSN'] %>";
  window.RAILS_ENV = "<%= Rails.env %>";
  window.GIT_SHA = "<%= ENV['GIT_SHA'] %>";
</script>
```

## Filtering and Ignoring

### Ignore Specific Errors

```ruby
# config/initializers/sentry.rb
config.excluded_exceptions += [
  "ActionController::RoutingError",
  "ActiveRecord::RecordNotFound",
  "ActionController::InvalidAuthenticityToken"
]
```

### Fingerprinting

```ruby
config.before_send = lambda do |event, hint|
  exception = hint[:exception]

  if exception.is_a?(PaymentFailedError)
    event.fingerprint = ["payment-failed", exception.error_code]
  end

  event
end
```

## Alerts and Notifications

### Configure in Sentry Dashboard

1. Go to Project Settings > Alerts
2. Create Alert Rule:
   - When: An issue is seen (first time)
   - If: None (or add conditions)
   - Then: Send notification to Slack/email

### Example Rules

| Rule | Condition | Action |
|------|-----------|--------|
| New Issue | First seen | Slack notification |
| High Frequency | >100 events/hour | PagerDuty |
| Error Spike | 300% increase | Email + Slack |

## Testing

### Test Sentry Configuration

```ruby
# Rails console
Sentry.capture_message("Test from Rails console")
```

### RSpec Helpers

```ruby
# spec/support/sentry.rb
RSpec.configure do |config|
  config.before(:each) do
    Sentry.get_current_scope.clear
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No sampling | Too much data/cost | Configure traces_sample_rate |
| Capturing all exceptions | Noise | Filter common errors |
| No user context | Hard to debug | Set user on each request |
| No release tracking | Can't correlate deploys | Set release version |
| Logging sensitive data | Privacy violation | Filter before_send |

## Related Files

- [logging.md](./logging.md): Logging configuration
- [performance.md](./performance.md): APM monitoring
- [../kamal/setup.md](../kamal/setup.md): Deployment setup

## References

- [Sentry Rails Documentation](https://docs.sentry.io/platforms/ruby/guides/rails/)
- [Sentry Performance](https://docs.sentry.io/product/performance/)
- [Sentry Releases](https://docs.sentry.io/product/releases/)
