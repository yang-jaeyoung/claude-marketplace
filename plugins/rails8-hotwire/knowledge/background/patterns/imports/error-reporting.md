# Import Error Reporting

## Overview

Import pattern that generates downloadable error reports. Failed rows are collected into a CSV with error messages for user correction.

## When to Use

- Users need to fix failed rows
- Want batch correction workflow
- Need audit trail of failures
- Compliance requires error documentation

## Code Example

```ruby
# app/jobs/import_with_error_log_job.rb
class ImportWithErrorLogJob < ApplicationJob
  queue_as :default

  def perform(upload_id)
    upload = Upload.find(upload_id)
    upload.update!(status: :processing)

    results = { created: 0, updated: 0, failed: 0 }
    error_csv = []

    CSV.foreach(upload.file.path, headers: true) do |row|
      result = process_row(row, upload)

      case result[:status]
      when :created
        results[:created] += 1
      when :updated
        results[:updated] += 1
      when :failed
        results[:failed] += 1
        # Add row to error CSV with reason
        error_csv << row.to_h.merge("Error" => result[:error])
      end
    end

    # Generate error report if there were failures
    if error_csv.any?
      generate_error_report(upload, error_csv)
    end

    upload.update!(
      status: :completed,
      results: results,
      completed_at: Time.current
    )

    ImportMailer.completed(upload.user, upload).deliver_later
  end

  private

  def generate_error_report(upload, error_rows)
    csv_data = CSV.generate do |csv|
      csv << error_rows.first.keys
      error_rows.each { |row| csv << row.values }
    end

    upload.error_report.attach(
      io: StringIO.new(csv_data),
      filename: "errors_#{Date.current}.csv",
      content_type: "text/csv"
    )
  end
end
```

## Model Setup

```ruby
# app/models/upload.rb
class Upload < ApplicationRecord
  belongs_to :user
  has_one_attached :file
  has_one_attached :error_report  # For error CSV

  enum :status, {
    pending: 0,
    processing: 1,
    completed: 2,
    failed: 3
  }
end
```

## Download UI

```erb
<!-- app/views/uploads/_upload.html.erb -->
<div class="upload">
  <h3><%= upload.filename %></h3>
  <div class="status <%= upload.status %>">
    <%= upload.status.titleize %>
  </div>

  <% if upload.completed? && upload.results %>
    <div class="results">
      <span class="created">✓ <%= upload.results["created"] %> created</span>
      <span class="updated">↻ <%= upload.results["updated"] %> updated</span>
      <span class="failed">✗ <%= upload.results["failed"] %> failed</span>
    </div>

    <% if upload.error_report.attached? %>
      <%= link_to "Download Error Report",
                  rails_blob_path(upload.error_report, disposition: "attachment"),
                  class: "btn btn-warning" %>
    <% end %>
  <% end %>
</div>
```

## Enhanced Error Details

```ruby
# Include more context in error report
def process_row(row, upload)
  customer = Customer.find_or_initialize_by(email: row["email"])
  customer.assign_attributes(row_to_attributes(row))

  if customer.save
    status = customer.previously_new_record? ? :created : :updated
    { status: status }
  else
    {
      status: :failed,
      error: customer.errors.full_messages.join(", "),
      error_fields: customer.errors.keys.join(", "),  # Which fields failed
      suggestion: suggest_fix(customer.errors)         # Helpful hints
    }
  end
rescue => e
  {
    status: :failed,
    error: e.message,
    error_type: e.class.name
  }
end

def suggest_fix(errors)
  if errors[:email].include?("taken")
    "Use a different email or update existing record"
  elsif errors[:email].include?("invalid")
    "Check email format (must include @)"
  end
end
```

## Summary Email with Report

```ruby
# app/mailers/import_mailer.rb
class ImportMailer < ApplicationMailer
  def completed(user, upload)
    @upload = upload
    @results = upload.results

    if upload.error_report.attached?
      attachments["import_errors.csv"] = upload.error_report.download
    end

    mail(
      to: user.email,
      subject: "Import completed: #{upload.results['created']} records"
    )
  end
end
```

```erb
<!-- app/views/import_mailer/completed.html.erb -->
<h2>Import Complete</h2>

<div class="results">
  <p>✓ Created: <%= @results["created"] %></p>
  <p>↻ Updated: <%= @results["updated"] %></p>
  <% if @results["failed"] > 0 %>
    <p>✗ Failed: <%= @results["failed"] %></p>
    <p>Download the attached error report to fix failed rows.</p>
  <% end %>
</div>

<%= link_to "View Upload", upload_url(@upload) %>
```

## Key Features

- **Error Collection**: Preserves original row data plus error message
- **CSV Generation**: Creates downloadable error report
- **Active Storage**: Attaches report to upload record
- **Email Attachment**: Optionally emails error report
- **Re-import Ready**: Error CSV can be fixed and re-imported

## Cleanup Strategy

```ruby
# app/jobs/cleanup_error_reports_job.rb
class CleanupErrorReportsJob < ApplicationJob
  def perform
    # Delete error reports older than 30 days
    Upload.where("created_at < ?", 30.days.ago)
          .where.not(error_report_attachment_id: nil)
          .find_each do |upload|
      upload.error_report.purge
    end
  end
end
```

## Related Patterns

- [Basic CSV Import](./basic-csv.md): Base pattern to extend
- [Import with Validation](./validation.md): Pre-validation alternative
