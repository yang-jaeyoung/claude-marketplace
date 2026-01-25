# Basic CSV Import

## Overview

Simple CSV import pattern with streaming, error tracking, and email notifications. Processes records one at a time with proper error handling.

## When to Use

- Standard CSV file imports
- Simple data models without complex relationships
- Want basic error tracking and reporting
- Files under 10,000 rows

## Code Example

```ruby
# app/jobs/import_job.rb
class ImportJob < ApplicationJob
  queue_as :default

  def perform(upload_id)
    upload = Upload.find(upload_id)
    upload.update!(status: :processing)

    results = { created: 0, updated: 0, failed: 0, errors: [] }

    CSV.foreach(upload.file.path, headers: true) do |row|
      result = process_row(row, upload)

      case result[:status]
      when :created
        results[:created] += 1
      when :updated
        results[:updated] += 1
      when :failed
        results[:failed] += 1
        results[:errors] << result[:error]
      end
    end

    upload.update!(
      status: :completed,
      results: results,
      completed_at: Time.current
    )

    # Notify user
    ImportMailer.completed(upload.user, upload).deliver_later
  rescue => e
    upload.update!(
      status: :failed,
      error_message: e.message
    )
    raise
  end

  private

  def process_row(row, upload)
    customer = Customer.find_or_initialize_by(
      email: row["email"],
      company: upload.company
    )

    customer.assign_attributes(
      name: row["name"],
      phone: row["phone"],
      address: row["address"]
    )

    if customer.save
      status = customer.previously_new_record? ? :created : :updated
      { status: status }
    else
      {
        status: :failed,
        error: "Row #{row.line_number}: #{customer.errors.full_messages.join(', ')}"
      }
    end
  rescue => e
    {
      status: :failed,
      error: "Row #{row.line_number}: #{e.message}"
    }
  end
end

# app/controllers/uploads_controller.rb
class UploadsController < ApplicationController
  def create
    @upload = current_user.uploads.create!(
      file: params[:file],
      upload_type: params[:upload_type],
      status: :pending
    )

    ImportJob.perform_later(@upload.id)

    redirect_to uploads_path, notice: "Import started"
  end
end
```

## Key Features

- **Streaming**: Uses `CSV.foreach` to avoid loading entire file into memory
- **Find or Initialize**: Prevents duplicates, updates existing records
- **Error Tracking**: Collects all errors with line numbers
- **Status Management**: Tracks pending/processing/completed/failed states
- **Email Notifications**: Notifies user when import completes

## Related Patterns

- [Batch Import with Progress](./batch-progress.md): Add progress tracking
- [Import with Validation](./validation.md): Add pre-validation phase
- [Import Error Reporting](./error-reporting.md): Generate downloadable error reports
