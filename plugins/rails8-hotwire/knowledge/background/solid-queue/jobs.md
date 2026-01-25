# Solid Queue Jobs

## Overview

Creating and managing background jobs with Solid Queue and ActiveJob. Covers job generation, execution patterns, priorities, and error handling.

## When to Use

- Async email sending
- Long-running computations
- External API calls
- Bulk data processing
- Scheduled tasks

## Quick Start

## Common Setup

For ActiveJob base patterns with retry/discard configuration, see:
- [`snippets/common/job-base.rb`](../../snippets/common/job-base.rb): Job base class with logging

### Generate a Job

```bash
bin/rails generate job ProcessOrder
# Creates: app/jobs/process_order_job.rb
```

```ruby
# app/jobs/process_order_job.rb
class ProcessOrderJob < ApplicationJob
  queue_as :default

  def perform(order_id)
    order = Order.find(order_id)
    # Process the order
  end
end
```

### Enqueue a Job

```ruby
# Async (recommended)
ProcessOrderJob.perform_later(order.id)

# Sync (blocks execution)
ProcessOrderJob.perform_now(order.id)

# Delayed execution
ProcessOrderJob.set(wait: 1.hour).perform_later(order.id)
ProcessOrderJob.set(wait_until: Date.tomorrow.noon).perform_later(order.id)
```

## Main Patterns

### Pattern 1: Basic Job Structure

```ruby
# app/jobs/application_job.rb
class ApplicationJob < ActiveJob::Base
  # Global retry configuration
  retry_on StandardError, wait: :polynomially_longer, attempts: 5

  # Discard unrecoverable errors
  discard_on ActiveJob::DeserializationError

  # Log all jobs
  before_perform do |job|
    Rails.logger.info "Starting #{job.class.name} with #{job.arguments.inspect}"
  end

  after_perform do |job|
    Rails.logger.info "Completed #{job.class.name}"
  end
end
```

```ruby
# app/jobs/send_welcome_email_job.rb
class SendWelcomeEmailJob < ApplicationJob
  queue_as :high

  def perform(user_id)
    user = User.find(user_id)
    UserMailer.welcome_email(user).deliver_now
  end
end

# Usage
SendWelcomeEmailJob.perform_later(user.id)
```

### Pattern 2: Job with Priority

```ruby
# app/jobs/payment_job.rb
class PaymentJob < ApplicationJob
  queue_as :critical  # Highest priority

  # Override retry for payment-specific errors
  retry_on Stripe::RateLimitError, wait: :polynomially_longer, attempts: 5
  retry_on Stripe::APIConnectionError, wait: 5.seconds, attempts: 3
  discard_on Stripe::InvalidRequestError

  def perform(order_id)
    order = Order.find(order_id)

    result = PaymentService.charge(
      amount: order.total_cents,
      currency: "usd",
      customer: order.customer.stripe_id
    )

    if result.success?
      order.update!(status: :paid, paid_at: Time.current)
      OrderMailer.confirmation(order).deliver_later
    else
      order.update!(status: :payment_failed, error: result.error_message)
      raise PaymentError, result.error_message
    end
  end
end
```

### Pattern 3: Batch Processing Job

```ruby
# app/jobs/bulk_update_job.rb
class BulkUpdateJob < ApplicationJob
  queue_as :default

  # Process in batches to avoid memory issues
  def perform(model_class, ids, attributes)
    model_class.constantize.where(id: ids).find_in_batches(batch_size: 100) do |batch|
      batch.each do |record|
        record.update!(attributes)
      end
    end
  end
end

# Usage: Update 10,000 users
user_ids = User.inactive.pluck(:id)
BulkUpdateJob.perform_later("User", user_ids, { status: "archived" })
```

### Pattern 4: Job with Arguments

```ruby
# app/jobs/export_job.rb
class ExportJob < ApplicationJob
  queue_as :low

  # Supports multiple argument types
  def perform(user_id, export_type, options = {})
    user = User.find(user_id)

    case export_type.to_sym
    when :orders
      export_orders(user, options)
    when :customers
      export_customers(user, options)
    when :products
      export_products(user, options)
    else
      raise ArgumentError, "Unknown export type: #{export_type}"
    end
  end

  private

  def export_orders(user, options)
    orders = user.orders
    orders = orders.where("created_at >= ?", options[:start_date]) if options[:start_date]

    # Generate CSV
    file = CSV.generate do |csv|
      csv << ["ID", "Date", "Total", "Status"]
      orders.find_each do |order|
        csv << [order.id, order.created_at, order.total, order.status]
      end
    end

    # Save with Active Storage
    user.exports.create!(
      file_type: :orders,
      file: {
        io: StringIO.new(file),
        filename: "orders_#{Date.current}.csv",
        content_type: "text/csv"
      }
    )
  end
end

# Usage
ExportJob.perform_later(
  current_user.id,
  :orders,
  { start_date: 30.days.ago }
)
```

### Pattern 5: Job with Callbacks

```ruby
# app/jobs/process_upload_job.rb
class ProcessUploadJob < ApplicationJob
  queue_as :default

  before_perform do |job|
    upload_id = job.arguments.first
    Upload.find(upload_id).update!(status: :processing)
  end

  after_perform do |job|
    upload_id = job.arguments.first
    Upload.find(upload_id).update!(status: :completed, completed_at: Time.current)
  end

  rescue_from StandardError do |exception|
    upload_id = arguments.first
    Upload.find(upload_id).update!(
      status: :failed,
      error_message: exception.message
    )
    raise # Re-raise for retry
  end

  def perform(upload_id)
    upload = Upload.find(upload_id)

    # Process file
    CSV.foreach(upload.file.path, headers: true) do |row|
      ImportRow.create!(
        upload: upload,
        data: row.to_h
      )
    end

    # Send notification
    UploadMailer.processing_complete(upload).deliver_later
  end
end
```

### Pattern 6: Idempotent Jobs

```ruby
# app/jobs/sync_user_job.rb
class SyncUserJob < ApplicationJob
  queue_as :default

  # Ensure job can run multiple times safely
  def perform(user_id, external_id)
    user = User.find(user_id)

    # Use find_or_initialize to avoid duplicates
    sync = UserSync.find_or_initialize_by(
      user: user,
      external_id: external_id
    )

    # Fetch external data
    external_data = ExternalAPI.get_user(external_id)

    # Update with latest data (idempotent)
    sync.update!(
      synced_at: Time.current,
      data: external_data
    )
  end
end
```

### Pattern 7: Job Progress Tracking

```ruby
# app/jobs/long_running_job.rb
class LongRunningJob < ApplicationJob
  queue_as :default

  def perform(task_id, total_items)
    task = Task.find(task_id)

    total_items.times do |i|
      # Process item
      process_item(i)

      # Update progress
      progress = ((i + 1).to_f / total_items * 100).round
      task.update!(progress: progress)

      # Broadcast progress via Turbo Stream
      task.broadcast_replace_to(
        "task_#{task.id}",
        partial: "tasks/progress",
        locals: { task: task }
      )
    end

    task.update!(status: :completed)
  end
end
```

## Solid Queue Specific Features

### Recurring Execution

```ruby
# app/jobs/cleanup_job.rb
class CleanupJob < ApplicationJob
  queue_as :low

  def perform
    # Delete old sessions
    Session.where("updated_at < ?", 30.days.ago).delete_all

    # Purge unattached files
    ActiveStorage::Blob.unattached
      .where("created_at < ?", 7.days.ago)
      .find_each(&:purge_later)
  end
end

# config/queue.yml
production:
  recurring_tasks:
    nightly_cleanup:
      class: CleanupJob
      schedule: "0 3 * * *"  # Every day at 3 AM
```

### Job Inspection

```ruby
# Check pending jobs
SolidQueue::Job.pending.where(queue_name: "critical").count

# Find failed jobs
SolidQueue::FailedExecution.order(created_at: :desc).limit(10).each do |failure|
  puts "Job: #{failure.job_class}"
  puts "Error: #{failure.error_message}"
  puts "Arguments: #{failure.arguments}"
end

# Retry failed job
failed = SolidQueue::FailedExecution.last
failed.retry
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Passing entire objects | Serialization overhead | Pass IDs only |
| No retry limits | Infinite retries waste resources | Set `attempts` limit |
| Jobs with side effects | Retry issues | Make idempotent |
| Long-running jobs | Worker blocking | Split into smaller jobs |
| No error handling | Silent failures | Add rescue_from blocks |

```ruby
# Bad: Passing full object
ExportJob.perform_later(user)

# Good: Pass ID
ExportJob.perform_later(user.id)

# Bad: Unlimited retries
retry_on StandardError

# Good: Limited retries
retry_on StandardError, attempts: 5

# Bad: Side effects
def perform(order_id)
  Order.find(order_id).charge_credit_card!  # Can't retry safely
end

# Good: Idempotent
def perform(order_id)
  order = Order.find(order_id)
  return if order.paid?  # Skip if already processed
  order.charge_credit_card!
end
```

## Related Skills

- [setup](./setup.md): Installing Solid Queue
- [configuration](./configuration.md): Advanced queue.yml
- [mailers](../patterns/mailers.md): Async email patterns
- [exports](../patterns/exports.md): CSV export jobs

## References

- [Active Job Basics](https://guides.rubyonrails.org/active_job_basics.html)
- [Solid Queue GitHub](https://github.com/rails/solid_queue)
- [Job Priority Best Practices](https://docs.solidqueue.dev/best-practices)
