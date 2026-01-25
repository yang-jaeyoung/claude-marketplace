# Sidekiq Monitoring

## Overview

Monitoring Sidekiq performance, tracking job metrics, setting up dashboards, and alerting on failures. Includes web UI, metrics integration, and error tracking.

## When to Use

- Production job queue monitoring
- Performance optimization
- Failure detection and alerting
- Capacity planning
- SLA tracking

## Quick Start

### Enable Web UI

```ruby
# config/routes.rb
require "sidekiq/web"

Rails.application.routes.draw do
  # Option 1: Protect with authentication
  authenticate :user, ->(user) { user.admin? } do
    mount Sidekiq::Web => "/sidekiq"
  end

  # Option 2: Basic auth
  Sidekiq::Web.use Rack::Auth::Basic do |username, password|
    username == ENV["SIDEKIQ_USERNAME"] &&
    password == ENV["SIDEKIQ_PASSWORD"]
  end
  mount Sidekiq::Web => "/sidekiq"
end
```

Visit: `http://localhost:3000/sidekiq`

## Main Patterns

### Pattern 1: Web UI Authentication

```ruby
# config/routes.rb
require "sidekiq/web"

# Devise authentication
authenticate :user, ->(user) { user.admin? } do
  mount Sidekiq::Web => "/sidekiq"
end

# Custom authentication
class AdminConstraint
  def matches?(request)
    return false unless request.session[:user_id]
    user = User.find_by(id: request.session[:user_id])
    user&.admin?
  end
end

constraints AdminConstraint.new do
  mount Sidekiq::Web => "/sidekiq"
end

# HTTP Basic Auth
Sidekiq::Web.use Rack::Auth::Basic do |username, password|
  ActiveSupport::SecurityUtils.secure_compare(
    ::Digest::SHA256.hexdigest(username),
    ::Digest::SHA256.hexdigest(ENV["SIDEKIQ_USERNAME"])
  ) &
  ActiveSupport::SecurityUtils.secure_compare(
    ::Digest::SHA256.hexdigest(password),
    ::Digest::SHA256.hexdigest(ENV["SIDEKIQ_PASSWORD"])
  )
end
mount Sidekiq::Web => "/sidekiq"
```

### Pattern 2: Custom Dashboard Tabs

```ruby
# config/initializers/sidekiq.rb
require "sidekiq/web"

# Add custom tab
Sidekiq::Web.app_url = "/"
Sidekiq::Web.locales << File.join(Rails.root, "config/locales")

# Custom tab for queue-specific metrics
module Sidekiq
  module WebExtensions
    def self.registered(app)
      app.get "/custom" do
        @stats = {
          critical: Sidekiq::Queue.new("critical").size,
          high: Sidekiq::Queue.new("high").size,
          default: Sidekiq::Queue.new("default").size,
          low: Sidekiq::Queue.new("low").size
        }

        erb :custom
      end
    end
  end
end

Sidekiq::Web.register Sidekiq::WebExtensions

# Create view: app/views/sidekiq/custom.erb
```

### Pattern 3: Programmatic Monitoring

```ruby
# lib/sidekiq/monitor.rb
module Sidekiq
  class Monitor
    def self.stats
      stats = Sidekiq::Stats.new

      {
        processed: stats.processed,
        failed: stats.failed,
        busy: stats.workers_size,
        enqueued: stats.enqueued,
        scheduled: stats.scheduled_size,
        retry: stats.retry_size,
        dead: stats.dead_size,
        processes: stats.processes_size,
        default_latency: stats.default_queue_latency
      }
    end

    def self.queue_stats
      Sidekiq::Queue.all.map do |queue|
        {
          name: queue.name,
          size: queue.size,
          latency: queue.latency.round(2)
        }
      end
    end

    def self.worker_stats
      Sidekiq::Workers.new.map do |process_id, thread_id, work|
        {
          queue: work["queue"],
          worker: work["payload"]["class"],
          run_at: Time.at(work["run_at"]),
          args: work["payload"]["args"]
        }
      end
    end

    def self.critical_alerts?
      stats = self.stats

      # Alert conditions
      stats[:enqueued] > 10_000 ||         # Queue backed up
      stats[:retry] > 500 ||                # Many retries
      stats[:dead] > 100 ||                 # Many dead jobs
      queue_latency_critical?               # Queue latency high
    end

    def self.queue_latency_critical?
      critical = Sidekiq::Queue.new("critical")
      critical.latency > 60  # Critical jobs delayed > 1 minute
    end
  end
end

# Usage
stats = Sidekiq::Monitor.stats
queues = Sidekiq::Monitor.queue_stats
workers = Sidekiq::Monitor.worker_stats
alert = Sidekiq::Monitor.critical_alerts?
```

### Pattern 4: Prometheus Metrics

```ruby
# Gemfile
gem "sidekiq"
gem "yabeda-sidekiq"
gem "yabeda-prometheus"

# config/initializers/yabeda.rb
require "yabeda/sidekiq"
require "yabeda/prometheus"

Yabeda.configure do
  # Automatically collects:
  # - sidekiq_jobs_executed_total
  # - sidekiq_jobs_failed_total
  # - sidekiq_jobs_success_total
  # - sidekiq_job_runtime_seconds
  # - sidekiq_queue_latency_seconds
  # - sidekiq_jobs_waiting_count
  # - sidekiq_active_workers_count

  # Custom metrics
  counter :jobs_by_priority do
    comment "Jobs processed by priority"
    tags [:priority]
  end

  histogram :custom_job_duration do
    comment "Custom job duration"
    tags [:job_name]
    buckets [0.1, 0.5, 1, 5, 10, 30, 60, 300]
  end
end

# config/routes.rb
mount Yabeda::Prometheus::Exporter => "/metrics"
```

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'rails'
    static_configs:
      - targets: ['localhost:3000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Pattern 5: Health Check Endpoint

```ruby
# app/controllers/health_controller.rb
class HealthController < ApplicationController
  skip_before_action :authenticate_user!

  def sidekiq
    redis_alive = redis_alive?
    workers_running = workers_running?
    queue_healthy = queue_healthy?

    if redis_alive && workers_running && queue_healthy
      render json: {
        status: "healthy",
        redis: "connected",
        workers: Sidekiq::ProcessSet.new.size,
        queues: queue_status
      }, status: :ok
    else
      render json: {
        status: "unhealthy",
        redis: redis_alive ? "connected" : "disconnected",
        workers: Sidekiq::ProcessSet.new.size,
        queues: queue_status
      }, status: :service_unavailable
    end
  end

  private

  def redis_alive?
    Sidekiq.redis(&:ping) == "PONG"
  rescue
    false
  end

  def workers_running?
    Sidekiq::ProcessSet.new.size > 0
  end

  def queue_healthy?
    critical = Sidekiq::Queue.new("critical")
    critical.latency < 60  # Critical queue latency < 1 minute
  end

  def queue_status
    Sidekiq::Queue.all.map do |queue|
      {
        name: queue.name,
        size: queue.size,
        latency: queue.latency.round(2)
      }
    end
  end
end

# config/routes.rb
get "/health/sidekiq", to: "health#sidekiq"
```

### Pattern 6: Error Tracking Integration

```ruby
# config/initializers/sidekiq.rb
Sidekiq.configure_server do |config|
  # Sentry integration
  config.error_handlers << proc { |exception, context|
    Sentry.capture_exception(
      exception,
      extra: {
        sidekiq: context,
        job_class: context[:job]["class"],
        job_id: context[:job]["jid"],
        args: context[:job]["args"],
        queue: context[:job]["queue"]
      },
      tags: {
        queue: context[:job]["queue"],
        job: context[:job]["class"]
      }
    )
  }

  # Honeybadger integration
  config.error_handlers << proc { |exception, context|
    Honeybadger.notify(exception, context: context)
  }

  # Custom logging
  config.error_handlers << proc { |exception, context|
    Rails.logger.error({
      event: "sidekiq_job_failed",
      exception: exception.class.name,
      message: exception.message,
      job_class: context[:job]["class"],
      job_id: context[:job]["jid"],
      args: context[:job]["args"],
      backtrace: exception.backtrace.first(10)
    }.to_json)
  }
end
```

### Pattern 7: Job Performance Tracking

```ruby
# app/jobs/application_job.rb
class ApplicationJob < ActiveJob::Base
  around_perform do |job, block|
    start = Time.current

    block.call

    duration = Time.current - start

    # Log performance
    Rails.logger.info({
      event: "job_completed",
      job: job.class.name,
      duration_ms: (duration * 1000).round(2),
      arguments: job.arguments
    }.to_json)

    # Track slow jobs
    if duration > 30
      SlowJobAlert.notify(job.class.name, duration)
    end

    # Send to metrics
    JobMetrics.record(job.class.name, duration)
  end
end

# lib/job_metrics.rb
class JobMetrics
  def self.record(job_name, duration)
    # Send to StatsD
    $statsd&.histogram("job.duration", duration * 1000, tags: ["job:#{job_name}"])

    # Or Prometheus
    Yabeda.custom_job_duration.measure({ job_name: job_name }, duration)
  end
end
```

### Pattern 8: Alerting on Failures

```ruby
# lib/sidekiq/alerting.rb
module Sidekiq
  class Alerting
    def self.check_and_alert
      stats = Sidekiq::Stats.new

      # Check queue backlog
      if stats.enqueued > 10_000
        alert("Queue backlog: #{stats.enqueued} jobs pending")
      end

      # Check dead jobs
      if stats.dead_size > 100
        alert("Dead jobs: #{stats.dead_size} jobs failed permanently")
      end

      # Check retry queue
      if stats.retry_size > 500
        alert("Retry queue: #{stats.retry_size} jobs retrying")
      end

      # Check critical queue latency
      critical = Sidekiq::Queue.new("critical")
      if critical.latency > 60
        alert("Critical queue latency: #{critical.latency.round(2)}s")
      end

      # Check for stopped workers
      if Sidekiq::ProcessSet.new.size == 0
        alert("No Sidekiq workers running!")
      end
    end

    def self.alert(message)
      # Slack notification
      SlackNotifier.notify(
        channel: "#alerts",
        text: ":warning: Sidekiq Alert: #{message}"
      )

      # PagerDuty
      # PagerDuty.trigger(message)

      # Email
      AdminMailer.sidekiq_alert(message).deliver_now
    end
  end
end

# config/schedule.yml (with sidekiq-cron)
sidekiq_health_check:
  cron: "*/5 * * * *"  # Every 5 minutes
  class: "SidekiqHealthCheckJob"

# app/jobs/sidekiq_health_check_job.rb
class SidekiqHealthCheckJob < ApplicationJob
  queue_as :default

  def perform
    Sidekiq::Alerting.check_and_alert
  end
end
```

## Web UI Features

### Available Tabs

- **Dashboard**: Overall stats, throughput charts
- **Busy**: Currently running jobs
- **Queues**: Queue sizes and latencies
- **Retries**: Jobs pending retry
- **Scheduled**: Jobs scheduled for future
- **Dead**: Jobs that exhausted retries
- **Processes**: Running Sidekiq processes

### Bulk Actions

```ruby
# Delete all jobs in a queue
Sidekiq::Queue.new("low").clear

# Retry all failed jobs
Sidekiq::RetrySet.new.retry_all

# Clear all dead jobs
Sidekiq::DeadSet.new.clear

# Kill all scheduled jobs
Sidekiq::ScheduledSet.new.clear
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Publicly accessible web UI | Security risk | Require authentication |
| No monitoring | Silent failures | Set up health checks and alerts |
| Ignoring dead jobs | Lost work | Monitor and investigate failures |
| No error tracking | Hard to debug | Integrate Sentry/Honeybadger |
| Missing latency alerts | SLA violations | Alert on queue latency |

```ruby
# Bad: No authentication
mount Sidekiq::Web => "/sidekiq"

# Good: Protected
authenticate :user, ->(user) { user.admin? } do
  mount Sidekiq::Web => "/sidekiq"
end
```

## Recommended Alerts

| Metric | Threshold | Action |
|--------|-----------|--------|
| Critical queue latency | > 60s | Page on-call |
| Total enqueued | > 10,000 | Investigate |
| Dead jobs | > 100 | Review failures |
| Retry queue | > 500 | Check error patterns |
| Workers running | = 0 | Restart workers |
| Redis connection | Failed | Check Redis health |

## Grafana Dashboard Example

```json
{
  "dashboard": {
    "panels": [
      {
        "title": "Jobs Processed",
        "targets": [
          {
            "expr": "rate(sidekiq_jobs_executed_total[5m])"
          }
        ]
      },
      {
        "title": "Job Duration",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sidekiq_job_runtime_seconds)"
          }
        ]
      },
      {
        "title": "Queue Sizes",
        "targets": [
          {
            "expr": "sidekiq_jobs_waiting_count"
          }
        ]
      }
    ]
  }
}
```

## Related Skills

- [setup](./setup.md): Initial Sidekiq configuration
- [jobs](./jobs.md): Job patterns and error handling
- [scheduling](./scheduling.md): Recurring jobs
- [solid-queue](../solid-queue/setup.md): Alternative queue system

## References

- [Sidekiq Wiki - Monitoring](https://github.com/sidekiq/sidekiq/wiki/Monitoring)
- [Sidekiq Web UI](https://github.com/sidekiq/sidekiq/wiki/Monitoring#web-ui)
- [yabeda-sidekiq](https://github.com/yabeda-rb/yabeda-sidekiq)
- [Sidekiq Best Practices](https://github.com/sidekiq/sidekiq/wiki/Best-Practices)
