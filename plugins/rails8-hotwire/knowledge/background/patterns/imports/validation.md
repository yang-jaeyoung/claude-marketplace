# Import with Validation

## Overview

Two-phase import pattern that validates all rows before processing any data. Provides early feedback and prevents partial imports of invalid data.

## When to Use

- Data quality is critical
- Want all-or-nothing import behavior
- Need to catch duplicates within the file
- Can afford two-pass processing

## Code Example

```ruby
# app/jobs/validated_import_job.rb
class ValidatedImportJob < ApplicationJob
  queue_as :default

  def perform(upload_id)
    upload = Upload.find(upload_id)

    # Phase 1: Validate all rows
    errors = validate_file(upload)

    if errors.any?
      upload.update!(
        status: :failed,
        error_message: "Validation failed",
        results: { errors: errors }
      )
      ImportMailer.validation_failed(upload.user, upload).deliver_later
      return
    end

    # Phase 2: Process if valid
    upload.update!(status: :processing)

    results = import_file(upload)

    upload.update!(
      status: :completed,
      results: results,
      completed_at: Time.current
    )

    ImportMailer.completed(upload.user, upload).deliver_later
  end

  private

  def validate_file(upload)
    errors = []

    CSV.foreach(upload.file.path, headers: true).with_index(2) do |row, line|
      # Check required fields
      if row["email"].blank?
        errors << "Line #{line}: Email is required"
      elsif !valid_email?(row["email"])
        errors << "Line #{line}: Invalid email format"
      end

      if row["name"].blank?
        errors << "Line #{line}: Name is required"
      end

      # Check for duplicates in file
      if duplicate_in_batch?(row["email"], upload)
        errors << "Line #{line}: Duplicate email in file"
      end

      # Stop after 10 errors for quick feedback
      break if errors.size >= 10
    end

    errors
  end

  def import_file(upload)
    results = { created: 0, updated: 0 }

    CSV.foreach(upload.file.path, headers: true) do |row|
      customer = Customer.find_or_initialize_by(email: row["email"])
      customer.assign_attributes(row_to_attributes(row))
      customer.save!

      results[customer.previously_new_record? ? :created : :updated] += 1
    end

    results
  end

  def valid_email?(email)
    email =~ URI::MailTo::EMAIL_REGEXP
  end

  def duplicate_in_batch?(email, upload)
    # Track seen emails in Redis or database
    key = "import:#{upload.id}:emails"
    return true if $redis.sismember(key, email)

    $redis.sadd(key, email)
    $redis.expire(key, 1.hour)
    false
  end
end
```

## Key Features

- **Two-Phase Processing**: Validate first, then import
- **Early Failure**: Stops immediately if validation fails
- **Email Validation**: Checks format using URI regexp
- **Duplicate Detection**: Uses Redis sets to track seen emails
- **Error Limiting**: Reports first 10 errors for quick feedback
- **All-or-Nothing**: Either all rows import or none do

## Alternative: Database-based Duplicate Tracking

```ruby
# Without Redis dependency
def duplicate_in_batch?(email, upload)
  # Use a temporary table or upload-scoped model
  ImportTracking.where(upload: upload).exists?(email: email)
end

def mark_seen(email, upload)
  ImportTracking.create!(upload: upload, email: email)
end
```

## Performance Considerations

- Reads file twice (validation + import)
- Redis operations for each row during validation
- Consider streaming validation for very large files
- May not scale well beyond 100K rows

## Related Patterns

- [Basic CSV Import](./basic-csv.md): Simpler single-pass version
- [Import Error Reporting](./error-reporting.md): Detailed error CSVs
