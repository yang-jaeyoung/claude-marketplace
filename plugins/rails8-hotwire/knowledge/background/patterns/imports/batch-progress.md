# Batch Import with Progress

## Overview

Import pattern with real-time progress tracking and Turbo Stream updates. Processes records in batches for better performance and user feedback.

## When to Use

- Large CSV imports (10,000+ rows)
- Need real-time progress feedback
- Want to show progress in UI
- Processing can be batched for efficiency

## Code Example

```ruby
# app/jobs/batch_import_job.rb
class BatchImportJob < ApplicationJob
  queue_as :default

  def perform(upload_id)
    upload = Upload.find(upload_id)
    upload.update!(status: :processing, progress: 0)

    # Parse file to count rows
    total_rows = CSV.read(upload.file.path, headers: true).size
    processed = 0

    results = { created: 0, updated: 0, failed: 0, errors: [] }

    CSV.foreach(upload.file.path, headers: true).each_slice(100) do |batch|
      batch.each do |row|
        result = process_row(row, upload)
        update_results(results, result)
        processed += 1
      end

      # Update progress
      progress = (processed.to_f / total_rows * 100).round
      upload.update!(progress: progress)

      # Broadcast via Turbo Stream
      upload.broadcast_replace_to(
        "upload_#{upload.id}",
        partial: "uploads/progress",
        locals: { upload: upload }
      )

      # Allow other jobs to run
      sleep 0.1
    end

    upload.update!(
      status: :completed,
      progress: 100,
      results: results,
      completed_at: Time.current
    )

    ImportMailer.completed(upload.user, upload).deliver_later
  end

  private

  def update_results(results, result)
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
end
```

## UI Component

```erb
<!-- app/views/uploads/_progress.html.erb -->
<div id="<%= dom_id(upload, :progress) %>">
  <div class="progress">
    <div class="progress-bar" style="width: <%= upload.progress %>%">
      <%= upload.progress %>%
    </div>
  </div>

  <div class="status">
    <%= upload.status.titleize %>

    <% if upload.completed? %>
      <div class="results">
        Created: <%= upload.results["created"] %> |
        Updated: <%= upload.results["updated"] %> |
        Failed: <%= upload.results["failed"] %>
      </div>
    <% end %>
  </div>
</div>
```

## Turbo Stream Subscription

```erb
<!-- app/views/uploads/show.html.erb -->
<%= turbo_stream_from "upload_#{@upload.id}" %>

<div class="upload-details">
  <%= render "progress", upload: @upload %>
</div>
```

## Key Features

- **Batch Processing**: Processes 100 rows at a time
- **Progress Tracking**: Updates percentage completion
- **Real-time Updates**: Broadcasts progress via Turbo Streams
- **Cooperative**: Sleeps between batches to allow other jobs
- **Pre-counting**: Reads file twice (count then process) for accurate progress

## Performance Considerations

- First pass counts rows (memory intensive for huge files)
- Consider storing row count when file is uploaded
- Adjust batch size based on record complexity
- Sleep duration affects responsiveness vs throughput

## Related Patterns

- [Basic CSV Import](./basic-csv.md): Simpler version without progress
- [Idempotent Import](./idempotent.md): Add resume capability
