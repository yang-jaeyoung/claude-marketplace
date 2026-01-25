---
name: rails8-background
description: Solid Queue, Sidekiq background job processing. Use when implementing async email sending, bulk processing, and scheduled tasks.
triggers:
  - background job
  - async
  - solid queue
  - sidekiq
  - active job
  - scheduled task
  - worker
  - mailer
  - 백그라운드 작업
  - 비동기
  - 솔리드 큐
  - 사이드킥
  - 액티브 잡
  - 예약 작업
  - 워커
  - 메일러
summary: |
  Rails 8의 백그라운드 작업 처리를 다룹니다. Solid Queue(기본값), Sidekiq,
  Active Job을 포함합니다. 비동기 이메일 발송, 대용량 처리, 예약 작업이
  필요할 때 참조하세요.
token_cost: medium
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - solid-queue/*.md
    - patterns/*.md
  deep:
    - "**/*.md"
    - "**/*.rb"
---

# Background: Background Jobs

## Overview

Covers background job processing in Rails 8. Includes Solid Queue (default), Sidekiq (alternative), and practical patterns for email, exports, and notifications.

## When to Use

- When processing long-running tasks
- When sending emails asynchronously
- When processing large volumes of data
- When running scheduled tasks

## Core Principles

| Principle | Description |
|-----------|-------------|
| Idempotency | Same job runs multiple times with same result |
| Retryable | Automatic retry on failure |
| Small Units | Split large jobs into smaller ones |
| Monitoring | Track job status |

## Quick Start

### Solid Queue (Rails 8 Default)

```yaml
# config/queue.yml
default: &default
  dispatchers:
    - polling_interval: 1
      batch_size: 500
  workers:
    - queues: "*"
      threads: 3
      processes: 1
      polling_interval: 0.1

development:
  <<: *default

production:
  dispatchers:
    - polling_interval: 1
      batch_size: 500
  workers:
    - queues: critical
      threads: 5
      processes: 2
      polling_interval: 0.1
    - queues: default
      threads: 3
      processes: 2
    - queues: low
      threads: 2
      processes: 1
```

```ruby
# config/application.rb
config.active_job.queue_adapter = :solid_queue
```

### Basic Job Generation

```bash
bin/rails generate job ProcessOrder
```

```ruby
# app/jobs/process_order_job.rb
class ProcessOrderJob < ApplicationJob
  queue_as :default

  retry_on StandardError, wait: :polynomially_longer, attempts: 5
  discard_on ActiveJob::DeserializationError

  def perform(order_id)
    order = Order.find(order_id)
    OrderProcessor.new(order).process
  end
end

# Invocation
ProcessOrderJob.perform_later(order.id)
```

## File Structure

```
background/
├── SKILL.md
├── solid-queue/
│   ├── setup.md
│   ├── jobs.md
│   └── configuration.md
├── sidekiq/
│   ├── setup.md
│   ├── jobs.md
│   ├── scheduling.md
│   └── monitoring.md
├── patterns/
│   ├── mailers.md
│   ├── exports.md
│   ├── imports.md
│   ├── notifications.md
│   └── cleanup.md
└── snippets/
    ├── application_job.rb
    └── examples/
        ├── export_job.rb
        └── notification_job.rb
```

## Main Patterns

### Pattern 1: Async Email Sending

```ruby
# app/mailers/application_mailer.rb
class ApplicationMailer < ActionMailer::Base
  default from: "noreply@example.com"
  layout "mailer"

  # Use deliver_later by default
end

# app/mailers/user_mailer.rb
class UserMailer < ApplicationMailer
  def welcome_email(user)
    @user = user
    mail(to: @user.email, subject: "Welcome!")
  end

  def password_reset(user)
    @user = user
    @reset_url = edit_password_reset_url(user.password_reset_token)
    mail(to: @user.email, subject: "Password Reset")
  end
end

# Invocation (async)
UserMailer.welcome_email(user).deliver_later
UserMailer.welcome_email(user).deliver_later(wait: 1.hour)
UserMailer.welcome_email(user).deliver_later(wait_until: Date.tomorrow.noon)
```

### Pattern 2: Large CSV Export

```ruby
# app/jobs/export_job.rb
class ExportJob < ApplicationJob
  queue_as :low

  def perform(user_id, export_type)
    user = User.find(user_id)

    case export_type
    when "orders"
      file = generate_orders_csv(user)
    when "customers"
      file = generate_customers_csv(user)
    end

    # Save with Active Storage
    export = user.exports.create!(
      file_type: export_type,
      status: :completed
    )
    export.file.attach(
      io: File.open(file.path),
      filename: "#{export_type}_#{Time.current.strftime('%Y%m%d')}.csv",
      content_type: "text/csv"
    )

    # Send notification
    ExportMailer.completed(user, export).deliver_later

    # Cleanup temp file
    file.unlink
  end

  private

  def generate_orders_csv(user)
    require "csv"

    file = Tempfile.new(["orders", ".csv"])

    CSV.open(file.path, "wb") do |csv|
      csv << ["ID", "Date", "Amount", "Status"]

      user.orders.find_each do |order|
        csv << [order.id, order.created_at, order.total, order.status]
      end
    end

    file
  end
end

# Invocation
ExportJob.perform_later(current_user.id, "orders")
```

### Pattern 3: Batch Processing

```ruby
# app/jobs/batch_notification_job.rb
class BatchNotificationJob < ApplicationJob
  queue_as :default

  def perform(notification_type, user_ids)
    User.where(id: user_ids).find_each do |user|
      NotificationJob.perform_later(user.id, notification_type)
    end
  end
end

# app/jobs/notification_job.rb
class NotificationJob < ApplicationJob
  queue_as :default

  retry_on Net::OpenTimeout, wait: 5.seconds, attempts: 3

  def perform(user_id, notification_type)
    user = User.find(user_id)

    notification = user.notifications.create!(
      notification_type: notification_type,
      title: notification_title(notification_type),
      body: notification_body(notification_type)
    )

    # Push notification (optional)
    PushService.send(user, notification) if user.push_enabled?
  end

  private

  def notification_title(type)
    I18n.t("notifications.#{type}.title")
  end

  def notification_body(type)
    I18n.t("notifications.#{type}.body")
  end
end

# Invocation: Send notifications to 1000 users
user_ids = User.active.pluck(:id)
user_ids.each_slice(100) do |batch|
  BatchNotificationJob.perform_later("weekly_digest", batch)
end
```

### Pattern 4: Recurring Jobs

```ruby
# app/jobs/cleanup_job.rb
class CleanupJob < ApplicationJob
  queue_as :low

  def perform
    # Delete sessions older than 30 days
    Session.where("updated_at < ?", 30.days.ago).delete_all

    # Delete unattached temp files older than 7 days
    ActiveStorage::Blob.unattached.where("created_at < ?", 7.days.ago).find_each(&:purge_later)

    # Clear logs
    ActionMailer::Base.deliveries.clear if Rails.env.development?

    Rails.logger.info "Cleanup completed at #{Time.current}"
  end
end

# config/initializers/scheduler.rb (using solid_queue)
# Or run via cron:
# 0 3 * * * cd /app && bin/rails runner "CleanupJob.perform_later"
```

### Pattern 5: Retry and Error Handling

```ruby
# app/jobs/payment_job.rb
class PaymentJob < ApplicationJob
  queue_as :critical

  # Retry for specific errors
  retry_on Stripe::RateLimitError, wait: :polynomially_longer, attempts: 5
  retry_on Stripe::APIConnectionError, wait: 5.seconds, attempts: 3

  # Discard unrecoverable errors
  discard_on Stripe::InvalidRequestError

  # Handle all errors
  rescue_from StandardError do |exception|
    Rails.logger.error "Payment failed: #{exception.message}"
    Sentry.capture_exception(exception)
    raise # Re-raise for retry
  end

  def perform(order_id)
    order = Order.find(order_id)

    result = PaymentService.charge(order)

    if result.success?
      order.update!(status: :paid, paid_at: Time.current)
      OrderMailer.confirmation(order).deliver_later
    else
      order.update!(status: :payment_failed)
      OrderMailer.payment_failed(order).deliver_later
    end
  end
end
```

### Pattern 6: Sidekiq (Alternative)

```ruby
# Gemfile
gem "sidekiq"

# config/application.rb
config.active_job.queue_adapter = :sidekiq

# config/initializers/sidekiq.rb
Sidekiq.configure_server do |config|
  config.redis = { url: ENV.fetch("REDIS_URL", "redis://localhost:6379/0") }
end

Sidekiq.configure_client do |config|
  config.redis = { url: ENV.fetch("REDIS_URL", "redis://localhost:6379/0") }
end

# config/sidekiq.yml
:concurrency: 5
:queues:
  - [critical, 3]
  - [default, 2]
  - [low, 1]
```

## Solid Queue vs Sidekiq

| Criteria | Solid Queue | Sidekiq |
|----------|-------------|---------|
| Infrastructure | Uses existing DB | Requires Redis |
| Cost | Free | Pro/Enterprise paid |
| Performance | Good for small/medium | Excellent for large scale |
| Dashboard | None | Web UI included |
| Scheduling | Limited | Advanced features |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Serializing large objects | Memory/DB overhead | Pass IDs only |
| Unlimited retries | Resource waste | Limit attempts |
| Synchronous processing | Response delay | Use perform_later |
| Order dependencies | Hard to recover on failure | Ensure idempotency |

```ruby
# Bad: Passing large objects
ExportJob.perform_later(users)  # Entire collection

# Good: Pass IDs only
ExportJob.perform_later(user_ids)
```

## Related Skills

- [core](../core/SKILL.md): Service object patterns
- [realtime](../realtime/SKILL.md): Real-time notifications
- [deploy](../deploy/SKILL.md): Production setup

## References

- [Active Job Basics](https://guides.rubyonrails.org/active_job_basics.html)
- [Solid Queue GitHub](https://github.com/rails/solid_queue)
- [Sidekiq](https://sidekiq.org/)
