# Solid Queue Setup

## Overview

Solid Queue is Rails 8's default database-backed job queue system, eliminating Redis dependency. Jobs are stored in your existing database using SQLite, PostgreSQL, or MySQL.

## When to Use

- Default choice for Rails 8 applications
- When you want to minimize infrastructure dependencies
- For small to medium scale background jobs (thousands per hour)
- When you need reliable job processing without Redis

## Quick Start

### Installation (Rails 8)

Solid Queue is included by default in new Rails 8 apps. For existing apps:

```bash
# Add gem (already included in Rails 8 Gemfile by default)
bundle add solid_queue

# Run installer
bin/rails solid_queue:install

# This creates:
# - config/queue.yml
# - db/queue_schema.rb
# - Migration files for job tables
```

### Database Migration

```bash
# Run migrations to create job tables
bin/rails db:migrate

# Creates tables:
# - solid_queue_jobs
# - solid_queue_scheduled_executions
# - solid_queue_ready_executions
# - solid_queue_claimed_executions
# - solid_queue_failed_executions
# - solid_queue_recurring_executions
```

### Configuration (config/application.rb)

```ruby
module MyApp
  class Application < Rails::Application
    # Set Solid Queue as the Active Job adapter (default in Rails 8)
    config.active_job.queue_adapter = :solid_queue

    # Optional: Configure default queue
    config.active_job.default_queue_name = :default
  end
end
```

## Main Patterns

### Pattern 1: Basic Configuration (config/queue.yml)

```yaml
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

test:
  <<: *default

production:
  dispatchers:
    - polling_interval: 1
      batch_size: 500
  workers:
    # High priority queue
    - queues: critical
      threads: 5
      processes: 2
      polling_interval: 0.1

    # Default queue
    - queues: default
      threads: 3
      processes: 2
      polling_interval: 0.1

    # Low priority queue
    - queues: low
      threads: 2
      processes: 1
      polling_interval: 1
```

**Explanation:**
- `dispatchers`: Poll database for scheduled jobs and dispatch them
- `workers`: Process queued jobs
- `threads`: Concurrent jobs per worker process
- `processes`: Number of worker processes to spawn
- `polling_interval`: Seconds between database polls

### Pattern 2: Multiple Queue Priorities

```yaml
# config/queue.yml
production:
  dispatchers:
    - polling_interval: 1
      batch_size: 500

  workers:
    # Critical: Payment processing, user-facing actions
    - queues: critical
      threads: 10
      processes: 3
      polling_interval: 0.1

    # High: Email, notifications
    - queues: high
      threads: 5
      processes: 2
      polling_interval: 0.5

    # Default: General background work
    - queues: default
      threads: 3
      processes: 2
      polling_interval: 1

    # Low: Cleanup, analytics
    - queues: low
      threads: 2
      processes: 1
      polling_interval: 5
```

```ruby
# app/jobs/payment_job.rb
class PaymentJob < ApplicationJob
  queue_as :critical  # Runs on high-resource worker

  def perform(order_id)
    # Process payment
  end
end

# app/jobs/cleanup_job.rb
class CleanupJob < ApplicationJob
  queue_as :low  # Runs on low-resource worker

  def perform
    # Clean old data
  end
end
```

### Pattern 3: Recurring Jobs

```yaml
# config/queue.yml
production:
  dispatchers:
    - polling_interval: 1
      batch_size: 500

  workers:
    - queues: "*"
      threads: 3
      processes: 2

  # Recurring jobs (cron-like scheduling)
  recurring_tasks:
    daily_cleanup:
      class: CleanupJob
      schedule: "0 3 * * *"  # Every day at 3 AM
      queue: low

    hourly_stats:
      class: UpdateStatsJob
      schedule: "0 * * * *"  # Every hour
      queue: default

    weekly_report:
      class: WeeklyReportJob
      schedule: "0 9 * * 1"  # Every Monday at 9 AM
      args: ["weekly"]
      queue: low
```

```ruby
# app/jobs/cleanup_job.rb
class CleanupJob < ApplicationJob
  queue_as :low

  def perform
    # Delete old sessions
    Session.where("updated_at < ?", 30.days.ago).delete_all

    # Purge unattached blobs
    ActiveStorage::Blob.unattached
      .where("created_at < ?", 7.days.ago)
      .find_each(&:purge_later)
  end
end
```

### Pattern 4: Database Sharding (Multi-Database)

```ruby
# config/database.yml
production:
  primary:
    <<: *default
    database: myapp_production

  queue:
    <<: *default
    database: myapp_queue
    migrations_paths: db/queue_migrate
```

```ruby
# config/application.rb
config.solid_queue.connects_to = { database: { writing: :queue } }
```

### Pattern 5: Running Workers

```bash
# Development: Run in foreground
bin/jobs

# Production: Run as daemon with Procfile
# Procfile
web: bin/rails server
worker: bin/jobs

# Or use systemd service
# /etc/systemd/system/solid-queue.service
[Unit]
Description=Solid Queue Worker
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/var/www/myapp
ExecStart=/var/www/myapp/bin/jobs
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Pattern 6: Monitoring and Observability

```ruby
# config/initializers/solid_queue.rb
Rails.application.config.after_initialize do
  # Log job metrics
  ActiveSupport::Notifications.subscribe("enqueue.active_job") do |event|
    job = event.payload[:job]
    Rails.logger.info "Enqueued #{job.class.name} to #{job.queue_name}"
  end

  ActiveSupport::Notifications.subscribe("perform.active_job") do |event|
    job = event.payload[:job]
    duration = event.duration
    Rails.logger.info "Performed #{job.class.name} in #{duration}ms"
  end
end
```

```ruby
# Query job statistics
SolidQueue::Job.pending.count
SolidQueue::Job.failed.count
SolidQueue::Job.where(queue_name: "critical").count

# Recent failed jobs
SolidQueue::FailedExecution.order(created_at: :desc).limit(10)
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Running without database indexes | Slow job polling | Run migrations fully |
| Single worker for all queues | Low-priority jobs block critical ones | Configure multiple workers by priority |
| No monitoring | Silent failures | Log metrics and failed jobs |
| Passing large objects as arguments | Database bloat | Pass IDs only, fetch in job |
| No recurring job deduplication | Duplicate scheduled jobs | Use unique task names |

```ruby
# Bad: Passing entire object
ExportJob.perform_later(User.all.to_a)

# Good: Pass IDs
ExportJob.perform_later(User.pluck(:id))
```

## Comparison with Other Solutions

| Feature | Solid Queue | Sidekiq | Good Job |
|---------|-------------|---------|----------|
| Infrastructure | Existing database | Redis required | PostgreSQL required |
| Setup complexity | Low | Medium | Low |
| Throughput | Medium | High | Medium |
| Dashboard | None | Built-in web UI | Built-in web UI |
| Recurring jobs | Yes (cron syntax) | Requires sidekiq-cron | Yes |
| Cost | Free | Pro/Enterprise paid | Free |

## Related Skills

- [jobs](./jobs.md): Creating and running jobs
- [configuration](./configuration.md): Advanced queue.yml options
- [sidekiq](../sidekiq/setup.md): Alternative with Redis
- [deploy](../../deploy/SKILL.md): Production deployment

## References

- [Solid Queue GitHub](https://github.com/rails/solid_queue)
- [Rails 8 Release Notes](https://guides.rubyonrails.org/8_0_release_notes.html)
- [Active Job Basics](https://guides.rubyonrails.org/active_job_basics.html)
