# Solid Queue Configuration

## Overview

Advanced configuration options for Solid Queue including worker tuning, dispatcher settings, concurrency control, and production optimization.

## When to Use

- Optimizing job throughput
- Configuring queue priorities
- Setting up recurring jobs
- Production performance tuning

## Quick Start

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

production:
  <<: *default
```

## Main Patterns

### Pattern 1: Worker Configuration

```yaml
# config/queue.yml
production:
  workers:
    # High-performance worker for critical jobs
    - queues: critical
      threads: 10        # Concurrent jobs per process
      processes: 3       # Number of worker processes
      polling_interval: 0.1  # Poll every 100ms

    # Standard worker
    - queues: [default, high]
      threads: 5
      processes: 2
      polling_interval: 0.5

    # Low-priority worker
    - queues: low
      threads: 2
      processes: 1
      polling_interval: 5  # Poll every 5 seconds

    # Catch-all for any other queues
    - queues: "*"
      threads: 3
      processes: 1
      polling_interval: 1
```

**Configuration Options:**
- `threads`: How many jobs run concurrently per process
- `processes`: How many worker processes to spawn
- `polling_interval`: Seconds between database queries for new jobs
- `queues`: Array of queue names, or "*" for all queues

### Pattern 2: Dispatcher Configuration

```yaml
# config/queue.yml
production:
  dispatchers:
    # Main dispatcher for scheduled jobs
    - polling_interval: 1
      batch_size: 500
      concurrency_maintenance_interval: 600  # 10 minutes

    # Secondary dispatcher for recurring tasks
    - polling_interval: 10
      batch_size: 100
```

**Dispatcher Options:**
- `polling_interval`: How often to check for scheduled jobs
- `batch_size`: Max jobs to dispatch per poll
- `concurrency_maintenance_interval`: How often to check for stuck jobs

### Pattern 3: Recurring Jobs (Cron-like)

```yaml
# config/queue.yml
production:
  recurring_tasks:
    # Daily cleanup at 3 AM
    daily_cleanup:
      class: CleanupJob
      schedule: "0 3 * * *"
      queue: low

    # Hourly stats update
    hourly_stats:
      class: UpdateStatsJob
      schedule: "0 * * * *"
      queue: default

    # Weekly report on Mondays at 9 AM
    weekly_report:
      class: WeeklyReportJob
      schedule: "0 9 * * 1"
      args: ["weekly"]
      queue: low

    # Every 15 minutes
    frequent_sync:
      class: SyncJob
      schedule: "*/15 * * * *"
      queue: high

    # First day of month
    monthly_billing:
      class: BillingJob
      schedule: "0 0 1 * *"
      args: ["monthly"]
      queue: critical
```

**Cron Syntax:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-6, Sunday=0)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)

*/15 = Every 15 minutes
0 */2 = Every 2 hours
0 9-17 = Every hour from 9 AM to 5 PM
```

### Pattern 4: Environment-Specific Configuration

```yaml
# config/queue.yml
default: &default
  dispatchers:
    - polling_interval: 1
      batch_size: 500

development:
  <<: *default
  workers:
    - queues: "*"
      threads: 2
      processes: 1
      polling_interval: 1

test:
  # Inline processing in tests
  workers:
    - queues: "*"
      threads: 1
      processes: 1
      polling_interval: 0.1

staging:
  <<: *default
  workers:
    - queues: "*"
      threads: 3
      processes: 2

production:
  dispatchers:
    - polling_interval: 1
      batch_size: 1000
      concurrency_maintenance_interval: 300

  workers:
    - queues: critical
      threads: 10
      processes: 5
      polling_interval: 0.1

    - queues: [default, high]
      threads: 5
      processes: 3
      polling_interval: 0.5

    - queues: low
      threads: 2
      processes: 1
      polling_interval: 5
```

### Pattern 5: Database Connection Configuration

```ruby
# config/database.yml
production:
  primary:
    adapter: postgresql
    database: myapp_production
    pool: 5

  queue:
    adapter: postgresql
    database: myapp_queue_production
    pool: 20  # Higher pool for job processing
    migrations_paths: db/queue_migrate
```

```ruby
# config/application.rb
module MyApp
  class Application < Rails::Application
    # Configure Solid Queue to use separate database
    config.solid_queue.connects_to = { database: { writing: :queue } }

    # Or use primary database (default)
    # config.solid_queue.connects_to = { database: { writing: :primary } }
  end
end
```

### Pattern 6: Performance Tuning

```yaml
# config/queue.yml - High throughput configuration
production:
  dispatchers:
    - polling_interval: 0.5  # Poll more frequently
      batch_size: 2000       # Larger batches
      concurrency_maintenance_interval: 300

  workers:
    # Payment processing: high concurrency, low latency
    - queues: payments
      threads: 20
      processes: 5
      polling_interval: 0.05  # Very frequent polling

    # Background exports: lower concurrency
    - queues: exports
      threads: 3
      processes: 2
      polling_interval: 2

    # Cleanup: minimal resources
    - queues: cleanup
      threads: 1
      processes: 1
      polling_interval: 60  # Poll every minute
```

**Resource Calculation:**
```ruby
# Total concurrent jobs = threads × processes
# Example:
threads: 10
processes: 3
# Max concurrent: 30 jobs

# Database connections needed ≈ threads × processes + buffer
# Example for above: ~35 connections
```

### Pattern 7: Monitoring and Logging

```ruby
# config/initializers/solid_queue.rb
Rails.application.config.after_initialize do
  # Subscribe to job events
  ActiveSupport::Notifications.subscribe("enqueue.active_job") do |name, start, finish, id, payload|
    job = payload[:job]
    Rails.logger.info({
      event: "job_enqueued",
      job_class: job.class.name,
      queue: job.queue_name,
      arguments: job.arguments,
      scheduled_at: job.scheduled_at
    }.to_json)
  end

  ActiveSupport::Notifications.subscribe("perform_start.active_job") do |name, start, finish, id, payload|
    job = payload[:job]
    Rails.logger.info({
      event: "job_started",
      job_class: job.class.name,
      job_id: job.job_id
    }.to_json)
  end

  ActiveSupport::Notifications.subscribe("perform.active_job") do |name, start, finish, id, payload|
    job = payload[:job]
    duration_ms = (finish - start) * 1000

    Rails.logger.info({
      event: "job_completed",
      job_class: job.class.name,
      job_id: job.job_id,
      duration_ms: duration_ms.round(2)
    }.to_json)

    # Send to metrics service
    # Prometheus.histogram(:job_duration, duration_ms, labels: { job: job.class.name })
  end
end
```

### Pattern 8: Graceful Shutdown

```ruby
# config/initializers/solid_queue.rb
# Handle graceful shutdown on SIGTERM
Signal.trap("TERM") do
  Rails.logger.info "Received SIGTERM, shutting down gracefully..."
  SolidQueue.stop
end

Signal.trap("INT") do
  Rails.logger.info "Received SIGINT, shutting down gracefully..."
  SolidQueue.stop
end
```

```yaml
# docker-compose.yml
services:
  worker:
    image: myapp:latest
    command: bin/jobs
    stop_grace_period: 30s  # Allow 30 seconds for jobs to finish
    environment:
      - RAILS_ENV=production
```

## Advanced Patterns

### Multiple Worker Groups

```yaml
# config/queue.yml
production:
  workers:
    # CPU-intensive jobs
    - queues: heavy
      threads: 2   # Fewer threads to avoid CPU contention
      processes: 4  # More processes to use all cores

    # I/O-bound jobs (API calls, DB queries)
    - queues: api
      threads: 20  # More threads OK for I/O wait
      processes: 2

    # Mixed workload
    - queues: default
      threads: 5
      processes: 3
```

### Queue Weighting

```yaml
# config/queue.yml
production:
  workers:
    # Process critical 3x more than default
    - queues: critical,critical,critical,default
      threads: 5
      processes: 2
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Too many threads | Database connection exhaustion | Match threads to connection pool |
| Single worker for all queues | Low priority blocks high | Separate workers by priority |
| No recurring task monitoring | Silent failures | Log recurring task execution |
| Polling too frequently | Database load | Tune interval per queue priority |
| No graceful shutdown | Lost jobs | Handle SIGTERM |

```yaml
# Bad: Single worker, frequent polling everywhere
workers:
  - queues: "*"
    threads: 50
    polling_interval: 0.01

# Good: Separate workers, tuned polling
workers:
  - queues: critical
    threads: 10
    polling_interval: 0.1
  - queues: low
    threads: 2
    polling_interval: 5
```

## Performance Guidelines

| Queue Priority | Polling Interval | Threads | Use Case |
|----------------|------------------|---------|----------|
| Critical | 0.1s | 10-20 | Payments, user-facing |
| High | 0.5s | 5-10 | Emails, notifications |
| Default | 1s | 3-5 | General background work |
| Low | 5-60s | 1-2 | Cleanup, analytics |

## Related Skills

- [setup](./setup.md): Initial Solid Queue installation
- [jobs](./jobs.md): Creating job classes
- [sidekiq/configuration](../sidekiq/setup.md): Alternative queue system
- [deploy](../../deploy/SKILL.md): Production deployment

## References

- [Solid Queue Configuration](https://github.com/rails/solid_queue#configuration)
- [Cron Syntax Reference](https://crontab.guru/)
- [Active Job Queue Adapters](https://guides.rubyonrails.org/active_job_basics.html#backends)
