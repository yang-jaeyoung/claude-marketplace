# Idempotent Import

## Overview

Import pattern that supports safe retries and resume capability. Uses Redis to track processed rows, preventing duplicates when job is retried.

## When to Use

- Import jobs may fail mid-process
- Need to retry without duplicating data
- Want resume capability for large imports
- Running on unreliable infrastructure

## Code Example

```ruby
# app/jobs/idempotent_import_job.rb
class IdempotentImportJob < ApplicationJob
  queue_as :default

  # Allow retries without duplicating data
  def perform(upload_id)
    upload = Upload.find(upload_id)

    # Skip if already completed
    return if upload.completed?

    upload.update!(status: :processing)

    results = { created: 0, updated: 0, skipped: 0 }

    CSV.foreach(upload.file.path, headers: true) do |row|
      # Check if already processed
      if already_processed?(row, upload)
        results[:skipped] += 1
        next
      end

      result = process_row(row, upload)
      results[result[:status]] += 1

      # Mark as processed
      mark_processed(row, upload)
    end

    upload.update!(
      status: :completed,
      results: results,
      completed_at: Time.current
    )
  end

  private

  def already_processed?(row, upload)
    key = row_key(row)
    $redis.sismember("upload:#{upload.id}:processed", key)
  end

  def mark_processed(row, upload)
    key = row_key(row)
    $redis.sadd("upload:#{upload.id}:processed", key)
    $redis.expire("upload:#{upload.id}:processed", 7.days)
  end

  def row_key(row)
    # Use a unique identifier from the row
    Digest::MD5.hexdigest(row["email"] || row.to_h.values.join("|"))
  end
end
```

## Alternative: Database-based Tracking

```ruby
# For Rails 8 without Redis (using Solid Cache)
class IdempotentImportJob < ApplicationJob
  def perform(upload_id)
    upload = Upload.find(upload_id)
    return if upload.completed?

    upload.update!(status: :processing)
    results = { created: 0, updated: 0, skipped: 0 }

    CSV.foreach(upload.file.path, headers: true) do |row|
      if already_processed?(row, upload)
        results[:skipped] += 1
        next
      end

      result = process_row(row, upload)
      results[result[:status]] += 1

      mark_processed(row, upload)
    end

    upload.update!(
      status: :completed,
      results: results,
      completed_at: Time.current
    )
  end

  private

  def already_processed?(row, upload)
    cache_key = "upload:#{upload.id}:row:#{row_key(row)}"
    Rails.cache.exist?(cache_key)
  end

  def mark_processed(row, upload)
    cache_key = "upload:#{upload.id}:row:#{row_key(row)}"
    Rails.cache.write(cache_key, true, expires_in: 7.days)
  end

  def row_key(row)
    Digest::MD5.hexdigest(row["email"] || row.to_h.values.join("|"))
  end
end
```

## Model-based Tracking (Most Reliable)

```ruby
# Create migration
class CreateImportRows < ActiveRecord::Migration[8.0]
  def change
    create_table :import_rows do |t|
      t.references :upload, null: false, foreign_key: true
      t.string :row_hash, null: false
      t.string :status
      t.text :error_message
      t.timestamps
    end

    add_index :import_rows, [:upload_id, :row_hash], unique: true
  end
end

# app/models/import_row.rb
class ImportRow < ApplicationRecord
  belongs_to :upload
end

# app/jobs/idempotent_import_job.rb
class IdempotentImportJob < ApplicationJob
  def perform(upload_id)
    upload = Upload.find(upload_id)
    return if upload.completed?

    upload.update!(status: :processing)
    results = { created: 0, updated: 0, skipped: 0, failed: 0 }

    CSV.foreach(upload.file.path, headers: true) do |row|
      row_hash = row_key(row)

      # Find or create tracking record
      import_row = upload.import_rows.find_or_initialize_by(row_hash: row_hash)

      # Skip if already successfully processed
      if import_row.persisted? && import_row.status == "completed"
        results[:skipped] += 1
        next
      end

      # Process the row
      result = process_row(row, upload)

      # Update tracking
      import_row.update!(
        status: result[:status] == :failed ? "failed" : "completed",
        error_message: result[:error]
      )

      results[result[:status]] += 1
    end

    upload.update!(
      status: :completed,
      results: results,
      completed_at: Time.current
    )
  end

  private

  def row_key(row)
    Digest::MD5.hexdigest(row["email"] || row.to_h.values.join("|"))
  end
end
```

## Progress Resume with Position Tracking

```ruby
# Track last processed position
class IdempotentImportJob < ApplicationJob
  def perform(upload_id)
    upload = Upload.find(upload_id)
    return if upload.completed?

    upload.update!(status: :processing)

    # Resume from last position
    start_line = upload.last_processed_line || 0
    results = upload.results || { created: 0, updated: 0, failed: 0 }

    CSV.foreach(upload.file.path, headers: true).with_index do |row, index|
      next if index < start_line

      result = process_row(row, upload)
      results[result[:status]] += 1

      # Update progress every 100 rows
      if index % 100 == 0
        upload.update!(
          last_processed_line: index,
          results: results
        )
      end
    end

    upload.update!(
      status: :completed,
      results: results,
      completed_at: Time.current
    )
  end
end
```

## Key Features

- **Safe Retries**: Can retry job without duplicating data
- **Resume Capability**: Skips already-processed rows
- **Flexible Tracking**: Redis, cache, or database options
- **Automatic Cleanup**: 7-day expiration on tracking data
- **Hash-based Keys**: Uses MD5 of unique row data

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **Redis** | Fast, automatic expiration | Extra dependency |
| **Rails Cache** | Works with Solid Cache | May evict under memory pressure |
| **Database** | Most reliable, queryable | Slower, needs cleanup |
| **Position Tracking** | Simple, no hashing | Can't handle re-ordered rows |

## Cleanup Job

```ruby
# app/jobs/cleanup_import_tracking_job.rb
class CleanupImportTrackingJob < ApplicationJob
  def perform
    # Clean up database tracking
    ImportRow.where("created_at < ?", 7.days.ago).delete_all

    # Clean up completed uploads
    Upload.where(status: :completed)
          .where("completed_at < ?", 7.days.ago)
          .find_each do |upload|
      # Clear Redis tracking if used
      $redis.del("upload:#{upload.id}:processed") if $redis
    end
  end
end
```

## Related Patterns

- [Basic CSV Import](./basic-csv.md): Base pattern to extend
- [Batch Import with Progress](./batch-progress.md): Combine with progress tracking
