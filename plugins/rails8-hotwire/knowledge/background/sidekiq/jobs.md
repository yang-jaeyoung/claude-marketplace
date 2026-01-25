# Sidekiq Jobs

## Overview

Creating and configuring Sidekiq-specific job patterns. While Sidekiq uses ActiveJob by default in Rails, it also supports native Sidekiq::Worker for advanced features.

## When to Use

- Standard background jobs via ActiveJob (recommended)
- Native Sidekiq::Worker for advanced features (batches, unique jobs)
- High-performance job processing
- Complex retry strategies

## Quick Start

### ActiveJob Style (Recommended)

```ruby
# app/jobs/process_order_job.rb
class ProcessOrderJob < ApplicationJob
  queue_as :default

  def perform(order_id)
    order = Order.find(order_id)
    OrderProcessor.new(order).process
  end
end

# Usage
ProcessOrderJob.perform_later(order.id)
```

### Native Sidekiq::Worker Style

```ruby
# app/workers/process_order_worker.rb
class ProcessOrderWorker
  include Sidekiq::Worker

  sidekiq_options queue: :default, retry: 5

  def perform(order_id)
    order = Order.find(order_id)
    OrderProcessor.new(order).process
  end
end

# Usage
ProcessOrderWorker.perform_async(order.id)
```

## Main Patterns

### Pattern 1: Sidekiq Options

```ruby
# app/jobs/payment_job.rb
class PaymentJob < ApplicationJob
  queue_as :critical

  # ActiveJob retry configuration
  retry_on Stripe::RateLimitError, wait: :polynomially_longer, attempts: 10
  discard_on Stripe::InvalidRequestError

  # Or use Sidekiq-specific options
  sidekiq_options retry: 5, dead: true, backtrace: 20

  def perform(order_id)
    # Process payment
  end
end
```

**Available sidekiq_options:**
- `retry`: Number of retry attempts (default: 25)
- `dead`: Send to Dead Job Queue after retries exhausted
- `queue`: Queue name
- `backtrace`: Number of backtrace lines to save (default: 0)
- `pool`: Redis connection pool to use
- `tags`: Array of tags for filtering in dashboard

### Pattern 2: Custom Retry Logic

```ruby
# app/workers/api_call_worker.rb
class ApiCallWorker
  include Sidekiq::Worker

  sidekiq_options retry: 10

  # Custom retry logic
  sidekiq_retry_in do |count, exception|
    case exception
    when Net::OpenTimeout
      10 * (count + 1)  # Linear backoff
    when ApiRateLimitError
      3600  # Wait 1 hour for rate limit
    else
      :default  # Use Sidekiq's exponential backoff
    end
  end

  def perform(api_endpoint, params)
    response = HTTP.post(api_endpoint, json: params)
    raise ApiRateLimitError if response.status == 429
    response
  end
end
```

### Pattern 3: Unique Jobs

```ruby
# Gemfile
gem "sidekiq-unique-jobs"

# app/workers/sync_user_worker.rb
class SyncUserWorker
  include Sidekiq::Worker

  sidekiq_options(
    lock: :until_executed,  # Prevent duplicates until job starts
    lock_timeout: 3600,     # Release lock after 1 hour
    on_conflict: :log       # Log when duplicate detected
  )

  def perform(user_id)
    user = User.find(user_id)
    ExternalAPI.sync(user)
  end
end

# Only one job per user_id will execute at a time
SyncUserWorker.perform_async(123)
SyncUserWorker.perform_async(123)  # Skipped (duplicate)
```

**Lock Strategies:**
- `:until_executed` - Lock until job starts
- `:until_executing` - Lock while job runs
- `:until_performed` - Lock until job completes
- `:while_executing` - Lock only during execution

### Pattern 4: Job Batches

```ruby
# Requires Sidekiq Pro/Enterprise
# app/workers/batch_processor_worker.rb
class BatchProcessorWorker
  include Sidekiq::Worker

  def perform(batch_id)
    batch = Batch.find(batch_id)

    # Create Sidekiq batch
    sidekiq_batch = Sidekiq::Batch.new
    sidekiq_batch.description = "Processing batch #{batch_id}"

    # Callback when all jobs complete
    sidekiq_batch.on(:success, BatchCallbackWorker, batch_id: batch_id)

    sidekiq_batch.jobs do
      batch.items.each do |item|
        ProcessItemWorker.perform_async(item.id)
      end
    end
  end
end

class BatchCallbackWorker
  include Sidekiq::Worker

  def on_success(status, options)
    batch_id = options["batch_id"]
    Batch.find(batch_id).update!(status: :completed)
  end
end
```

### Pattern 5: Scheduled Jobs

```ruby
# app/jobs/scheduled_job.rb
class ScheduledJob < ApplicationJob
  queue_as :default

  def perform(user_id)
    user = User.find(user_id)
    # Process scheduled task
  end
end

# Schedule for later
ScheduledJob.set(wait: 1.hour).perform_later(user.id)
ScheduledJob.set(wait_until: Date.tomorrow.noon).perform_later(user.id)

# Or with native Sidekiq
ScheduledWorker.perform_in(1.hour, user.id)
ScheduledWorker.perform_at(Date.tomorrow.noon, user.id)
```

### Pattern 6: Job Middleware

```ruby
# lib/sidekiq_middleware/job_logger.rb
class JobLogger
  def call(worker, job, queue)
    start = Time.current
    Rails.logger.info "Starting #{worker.class.name}"

    yield  # Execute the job

    duration = Time.current - start
    Rails.logger.info "Completed #{worker.class.name} in #{duration}s"
  rescue => e
    Rails.logger.error "Failed #{worker.class.name}: #{e.message}"
    raise
  end
end

# config/initializers/sidekiq.rb
Sidekiq.configure_server do |config|
  config.server_middleware do |chain|
    chain.add JobLogger
  end
end
```

### Pattern 7: Bulk Enqueuing

```ruby
# Efficient bulk job creation
user_ids = User.active.pluck(:id)

# Instead of:
# user_ids.each { |id| NotifyUserJob.perform_later(id) }  # Slow

# Use Sidekiq's push_bulk for better performance
Sidekiq::Client.push_bulk(
  "class" => NotifyUserJob,
  "args" => user_ids.map { |id| [id] }
)

# Or with ActiveJob
user_ids.each_slice(1000) do |batch|
  NotifyUserJob.perform_bulk(batch.map { |id| [id] })
end
```

### Pattern 8: Error Handling

```ruby
# app/workers/resilient_worker.rb
class ResilientWorker
  include Sidekiq::Worker

  sidekiq_options retry: 10

  sidekiq_retries_exhausted do |job, exception|
    # Called when all retries are exhausted
    order_id = job["args"].first
    order = Order.find(order_id)

    order.update!(
      status: :failed,
      error_message: exception.message
    )

    # Notify admins
    AdminMailer.job_failed(order, exception).deliver_now

    # Send to error tracking
    Sentry.capture_exception(exception, extra: { order_id: order_id })
  end

  def perform(order_id)
    order = Order.find(order_id)
    PaymentService.charge(order)
  end
end
```

### Pattern 9: Job Priority

```ruby
# config/sidekiq.yml
:queues:
  - [critical, 50]   # 50x weight
  - [high, 20]       # 20x weight
  - [default, 5]     # 5x weight
  - [low, 1]         # 1x weight (baseline)

# Jobs in 'critical' are 50x more likely to run than 'low'

# app/jobs/priority_job.rb
class UrgentJob < ApplicationJob
  queue_as :critical
end

class NormalJob < ApplicationJob
  queue_as :default
end

class BackgroundJob < ApplicationJob
  queue_as :low
end
```

## Sidekiq-Specific Features

### Dead Job Queue

```ruby
# Jobs go to Dead Job Queue after retries exhausted
class ImportWorker
  include Sidekiq::Worker

  sidekiq_options retry: 5, dead: true

  def perform(file_id)
    # Import logic
  end
end

# View dead jobs in web UI or programmatically
require "sidekiq/api"

dead_set = Sidekiq::DeadSet.new
dead_set.size  # Number of dead jobs

# Retry a dead job
dead_set.each do |job|
  job.retry if job.klass == "ImportWorker"
end

# Clear all dead jobs
dead_set.clear
```

### Job Inspection

```ruby
require "sidekiq/api"

# Queue stats
stats = Sidekiq::Stats.new
stats.processed      # Total processed
stats.failed         # Total failed
stats.enqueued       # Currently enqueued

# Specific queue
queue = Sidekiq::Queue.new("critical")
queue.size           # Jobs waiting
queue.latency        # Seconds oldest job has been waiting

# Clear queue
queue.clear

# Retry queue
retry_set = Sidekiq::RetrySet.new
retry_set.size
retry_set.clear

# Scheduled jobs
scheduled_set = Sidekiq::ScheduledSet.new
scheduled_set.size
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Unlimited retries | Wastes resources | Set retry: 5 or 10 |
| Passing large objects | Serialization overhead | Pass IDs only |
| No dead queue | Lost error visibility | Enable dead: true |
| Mixing ActiveJob and Sidekiq::Worker | Inconsistent patterns | Pick one style |
| No error tracking | Silent failures | Use retries_exhausted callback |

```ruby
# Bad: Passing full object
ExportJob.perform_later(User.all.to_a)

# Good: Pass IDs
ExportJob.perform_later(User.pluck(:id))

# Bad: No retry limit
sidekiq_options retry: true  # Retries 25 times!

# Good: Reasonable limit
sidekiq_options retry: 5, dead: true
```

## Performance Tips

1. **Use `perform_bulk` for large batches** - 10-100x faster than individual enqueues
2. **Keep job arguments small** - Serialize IDs, not full objects
3. **Set appropriate queue priorities** - Prevent low-priority jobs from blocking critical ones
4. **Monitor queue latency** - Alert if jobs are backing up
5. **Use connection pooling** - Size Redis pool appropriately

## Related Skills

- [setup](./setup.md): Installing and configuring Sidekiq
- [scheduling](./scheduling.md): Cron-like recurring jobs
- [monitoring](./monitoring.md): Dashboard and alerting
- [solid-queue/jobs](../solid-queue/jobs.md): Alternative queue system

## References

- [Sidekiq Wiki](https://github.com/sidekiq/sidekiq/wiki)
- [Sidekiq Best Practices](https://github.com/sidekiq/sidekiq/wiki/Best-Practices)
- [Active Job Basics](https://guides.rubyonrails.org/active_job_basics.html)
- [Sidekiq Unique Jobs](https://github.com/mhenrixon/sidekiq-unique-jobs)
