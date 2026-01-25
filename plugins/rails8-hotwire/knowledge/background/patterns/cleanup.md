# Cleanup Jobs

## Overview

Scheduled background jobs for maintenance tasks, data retention policies, temporary file cleanup, and database housekeeping.

## When to Use

- Delete old sessions
- Purge temporary files
- Archive old records
- Remove expired tokens
- Clean up test data
- Enforce data retention policies

## Quick Start

```ruby
# Schedule daily cleanup
CleanupJob.perform_later

# Or configure as recurring job
```

## Main Patterns

### Pattern 1: Basic Cleanup Job

```ruby
# app/jobs/cleanup_job.rb
class CleanupJob < ApplicationJob
  queue_as :low

  def perform
    cleanup_sessions
    cleanup_temp_files
    cleanup_expired_tokens
    cleanup_old_logs

    Rails.logger.info "Cleanup completed at #{Time.current}"
  end

  private

  def cleanup_sessions
    # Delete sessions older than 30 days
    count = Session.where("updated_at < ?", 30.days.ago).delete_all
    Rails.logger.info "Deleted #{count} old sessions"
  end

  def cleanup_temp_files
    # Purge unattached Active Storage blobs older than 7 days
    count = ActiveStorage::Blob.unattached
                                .where("created_at < ?", 7.days.ago)
                                .count

    ActiveStorage::Blob.unattached
                       .where("created_at < ?", 7.days.ago)
                       .find_each(&:purge_later)

    Rails.logger.info "Purged #{count} unattached files"
  end

  def cleanup_expired_tokens
    # Delete expired password reset tokens
    count = User.where("reset_token_expires_at < ?", Time.current)
                .update_all(reset_token: nil, reset_token_expires_at: nil)

    Rails.logger.info "Cleared #{count} expired reset tokens"
  end

  def cleanup_old_logs
    # Clear Action Mailer deliveries in development
    if Rails.env.development?
      ActionMailer::Base.deliveries.clear
    end
  end
end

# config/schedule.yml (sidekiq-cron)
daily_cleanup:
  cron: "0 3 * * *"  # 3 AM daily
  class: "CleanupJob"
  queue: low

# Or with Solid Queue
# config/queue.yml
production:
  recurring_tasks:
    daily_cleanup:
      class: CleanupJob
      schedule: "0 3 * * *"
      queue: low
```

### Pattern 2: Data Retention Policy

```ruby
# app/jobs/data_retention_job.rb
class DataRetentionJob < ApplicationJob
  queue_as :low

  RETENTION_POLICIES = {
    # Model => days to keep
    "Log" => 90,
    "AuditEvent" => 365,
    "Export" => 7,
    "Import" => 30,
    "Notification" => 60
  }.freeze

  def perform
    RETENTION_POLICIES.each do |model_name, days|
      delete_old_records(model_name, days)
    end
  end

  private

  def delete_old_records(model_name, days)
    model = model_name.constantize
    cutoff = days.days.ago

    count = model.where("created_at < ?", cutoff).delete_all

    Rails.logger.info "Deleted #{count} #{model_name} records older than #{days} days"
  rescue => e
    Rails.logger.error "Failed to delete old #{model_name}: #{e.message}"
    Sentry.capture_exception(e) if defined?(Sentry)
  end
end

# config/schedule.yml
data_retention:
  cron: "0 2 * * *"  # 2 AM daily
  class: "DataRetentionJob"
```

### Pattern 3: Archive Old Records

```ruby
# app/jobs/archive_job.rb
class ArchiveJob < ApplicationJob
  queue_as :low

  def perform(model_name, archive_after_days = 365)
    model = model_name.constantize
    cutoff = archive_after_days.days.ago

    # Find old records
    old_records = model.where("created_at < ?", cutoff)
                       .where(archived: false)

    count = 0

    old_records.find_in_batches(batch_size: 1000) do |batch|
      # Archive to separate table or storage
      batch.each do |record|
        archive_record(record)
        count += 1
      end

      # Throttle to avoid database load
      sleep 1
    end

    Rails.logger.info "Archived #{count} #{model_name} records"
  end

  private

  def archive_record(record)
    # Option 1: Mark as archived
    record.update!(archived: true, archived_at: Time.current)

    # Option 2: Move to archive table
    # ArchivedOrder.create!(record.attributes)
    # record.destroy

    # Option 3: Export to S3/external storage
    # S3Archive.store(record)
    # record.destroy
  end
end

# Schedule monthly
# config/schedule.yml
monthly_archive:
  cron: "0 1 1 * *"  # 1 AM on first of month
  class: "ArchiveJob"
  args: ["Order", 365]
```

### Pattern 4: Cleanup Failed Jobs

```ruby
# app/jobs/cleanup_failed_jobs_job.rb
class CleanupFailedJobsJob < ApplicationJob
  queue_as :low

  def perform
    if defined?(Sidekiq)
      cleanup_sidekiq_jobs
    elsif defined?(SolidQueue)
      cleanup_solid_queue_jobs
    end
  end

  private

  def cleanup_sidekiq_jobs
    require "sidekiq/api"

    # Clean dead jobs older than 30 days
    dead_set = Sidekiq::DeadSet.new
    initial_count = dead_set.size

    dead_set.each do |job|
      if job.at < 30.days.ago.to_f
        job.delete
      end
    end

    final_count = dead_set.size
    Rails.logger.info "Cleaned #{initial_count - final_count} old dead jobs"

    # Clear retry queue for permanently failed jobs
    retry_set = Sidekiq::RetrySet.new
    retry_count = retry_set.size

    retry_set.each do |job|
      if job.retry_count >= 25  # Max retries
        job.delete
      end
    end

    Rails.logger.info "Cleaned #{retry_count - retry_set.size} exhausted retries"
  end

  def cleanup_solid_queue_jobs
    # Clean failed executions older than 30 days
    count = SolidQueue::FailedExecution
              .where("created_at < ?", 30.days.ago)
              .delete_all

    Rails.logger.info "Cleaned #{count} old failed executions"
  end
end

# config/schedule.yml
cleanup_failed_jobs:
  cron: "0 4 * * 0"  # Sunday at 4 AM
  class: "CleanupFailedJobsJob"
```

### Pattern 5: Database Maintenance

```ruby
# app/jobs/database_maintenance_job.rb
class DatabaseMaintenanceJob < ApplicationJob
  queue_as :low

  def perform
    vacuum_tables if postgres?
    optimize_tables if mysql?
    update_statistics
    rebuild_indexes
  end

  private

  def postgres?
    ActiveRecord::Base.connection.adapter_name == "PostgreSQL"
  end

  def mysql?
    ActiveRecord::Base.connection.adapter_name == "Mysql2"
  end

  def vacuum_tables
    # PostgreSQL VACUUM to reclaim space
    tables = ActiveRecord::Base.connection.tables

    tables.each do |table|
      ActiveRecord::Base.connection.execute("VACUUM ANALYZE #{table}")
      Rails.logger.info "Vacuumed table: #{table}"
    end
  end

  def optimize_tables
    # MySQL OPTIMIZE TABLE
    tables = ActiveRecord::Base.connection.tables

    tables.each do |table|
      ActiveRecord::Base.connection.execute("OPTIMIZE TABLE #{table}")
      Rails.logger.info "Optimized table: #{table}"
    end
  end

  def update_statistics
    if postgres?
      ActiveRecord::Base.connection.execute("ANALYZE")
      Rails.logger.info "Updated PostgreSQL statistics"
    end
  end

  def rebuild_indexes
    # Only if needed (check fragmentation first)
    # REINDEX can lock tables
  end
end

# config/schedule.yml
database_maintenance:
  cron: "0 1 * * 0"  # Sunday at 1 AM
  class: "DatabaseMaintenanceJob"
```

### Pattern 6: Cleanup External Resources

```ruby
# app/jobs/cleanup_external_resources_job.rb
class CleanupExternalResourcesJob < ApplicationJob
  queue_as :low

  def perform
    cleanup_s3_files
    cleanup_cdn_cache
    cleanup_redis_keys
  end

  private

  def cleanup_s3_files
    # Find orphaned S3 files (not in Active Storage)
    # This is a simplified example
    s3 = Aws::S3::Resource.new
    bucket = s3.bucket(ENV["S3_BUCKET"])

    bucket.objects.each do |obj|
      # Check if file exists in Active Storage
      blob_key = obj.key.split("/").last

      unless ActiveStorage::Blob.exists?(key: blob_key)
        if obj.last_modified < 7.days.ago
          obj.delete
          Rails.logger.info "Deleted orphaned S3 file: #{obj.key}"
        end
      end
    end
  end

  def cleanup_cdn_cache
    # Purge old cache entries
    # CloudFlare.purge_cache(...)
  end

  def cleanup_redis_keys
    # Clean up old cache keys
    return unless defined?(Redis)

    redis = Redis.new(url: ENV["REDIS_URL"])

    # Find keys matching pattern
    keys = redis.keys("cache:temp:*")

    keys.each do |key|
      ttl = redis.ttl(key)

      # Delete if expired or very old
      if ttl == -1 || ttl > 7.days
        redis.del(key)
      end
    end

    Rails.logger.info "Cleaned #{keys.size} Redis keys"
  end
end

# config/schedule.yml
cleanup_external:
  cron: "0 5 * * 0"  # Sunday at 5 AM
  class: "CleanupExternalResourcesJob"
```

### Pattern 7: Targeted Cleanup with Notifications

```ruby
# app/jobs/notification_cleanup_job.rb
class NotificationCleanupJob < ApplicationJob
  queue_as :low

  def perform
    stats = {
      read: cleanup_read_notifications,
      unread: archive_old_unread_notifications
    }

    # Notify admins of cleanup
    AdminMailer.cleanup_report("notifications", stats).deliver_later

    Rails.logger.info "Notification cleanup: #{stats.inspect}"
  end

  private

  def cleanup_read_notifications
    # Delete read notifications older than 60 days
    Notification.where(read_at: ...60.days.ago).delete_all
  end

  def archive_old_unread_notifications
    # Archive (don't delete) old unread notifications
    count = Notification.where(read_at: nil)
                       .where("created_at < ?", 90.days.ago)
                       .update_all(archived: true)

    count
  end
end
```

### Pattern 8: Conditional Cleanup

```ruby
# app/jobs/smart_cleanup_job.rb
class SmartCleanupJob < ApplicationJob
  queue_as :low

  def perform
    # Only run cleanup if database is getting full
    if database_usage_high?
      aggressive_cleanup
    else
      normal_cleanup
    end
  end

  private

  def database_usage_high?
    # Check database size (PostgreSQL example)
    result = ActiveRecord::Base.connection.execute(
      "SELECT pg_database_size(current_database())"
    )

    size_bytes = result.first["pg_database_size"]
    size_gb = size_bytes / 1024.0 / 1024.0 / 1024.0

    # Alert if over 80% of quota
    max_size_gb = ENV.fetch("MAX_DB_SIZE_GB", 100).to_f
    size_gb > (max_size_gb * 0.8)
  end

  def aggressive_cleanup
    # More aggressive retention
    Log.where("created_at < ?", 30.days.ago).delete_all
    Notification.where("created_at < ?", 14.days.ago).delete_all

    Rails.logger.warn "Aggressive cleanup performed due to database size"
  end

  def normal_cleanup
    # Standard retention
    Log.where("created_at < ?", 90.days.ago).delete_all
    Notification.where("created_at < ?", 60.days.ago).delete_all
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Cleanup during peak hours | Performance impact | Schedule off-peak |
| No batching | Long-running locks | Use find_in_batches |
| Deleting without archiving | Data loss | Archive before delete |
| No monitoring | Silent failures | Log cleanup stats |
| Single large transaction | Database locks | Batch deletions |

```ruby
# Bad: Delete all at once during business hours
def perform
  OldRecord.where("created_at < ?", 1.year.ago).delete_all
end

# Good: Batch deletion during off-peak
def perform
  OldRecord.where("created_at < ?", 1.year.ago)
           .find_in_batches(batch_size: 1000) do |batch|
    batch.each(&:destroy)
    sleep 1  # Throttle
  end
end
```

## Monitoring Cleanup Jobs

```ruby
# app/jobs/application_job.rb
class ApplicationJob < ActiveJob::Base
  after_perform do |job|
    if job.class.name.ends_with?("CleanupJob")
      # Track cleanup metrics
      CleanupMetric.create!(
        job_name: job.class.name,
        completed_at: Time.current,
        duration: Time.current - job.enqueued_at
      )
    end
  end
end
```

## Testing Cleanup Jobs

```ruby
# spec/jobs/cleanup_job_spec.rb
RSpec.describe CleanupJob do
  describe "#perform" do
    it "deletes old sessions" do
      old_session = create(:session, updated_at: 31.days.ago)
      new_session = create(:session, updated_at: 1.day.ago)

      CleanupJob.perform_now

      expect(Session.exists?(old_session.id)).to be false
      expect(Session.exists?(new_session.id)).to be true
    end

    it "purges unattached files" do
      blob = create(:blob, :unattached, created_at: 8.days.ago)

      expect {
        CleanupJob.perform_now
      }.to have_enqueued_job(ActiveStorage::PurgeJob)
    end
  end
end
```

## Related Skills

- [solid-queue/configuration](../solid-queue/configuration.md): Recurring jobs
- [sidekiq/scheduling](../sidekiq/scheduling.md): Cron scheduling
- [exports](./exports.md): Export cleanup
- [imports](./imports.md): Import file cleanup

## References

- [Active Job Basics](https://guides.rubyonrails.org/active_job_basics.html)
- [PostgreSQL VACUUM](https://www.postgresql.org/docs/current/sql-vacuum.html)
- [Active Storage](https://guides.rubyonrails.org/active_storage_overview.html)
- [Database Maintenance Best Practices](https://guides.rubyonrails.org/maintenance_policy.html)
