# Export Jobs

## Overview

Background jobs for exporting large datasets to CSV, Excel, or PDF. Handle memory-efficient streaming, progress tracking, and file delivery.

## When to Use

- Exporting user data
- Generating reports
- Bulk data downloads
- Compliance (GDPR data export)
- Analytics reports

## Quick Start

```ruby
# Trigger export
ExportJob.perform_later(current_user.id, "orders")

# Job handles file generation and notification
```

## Main Patterns

### Pattern 1: Basic CSV Export

```ruby
# app/jobs/export_job.rb
class ExportJob < ApplicationJob
  queue_as :low

  def perform(user_id, export_type)
    user = User.find(user_id)

    file = generate_csv(user, export_type)

    # Save with Active Storage
    export = user.exports.create!(
      export_type: export_type,
      status: :completed
    )

    export.file.attach(
      io: File.open(file.path),
      filename: "#{export_type}_#{Date.current}.csv",
      content_type: "text/csv"
    )

    # Send notification
    ExportMailer.ready(user, export).deliver_later

    # Cleanup
    file.unlink
  end

  private

  def generate_csv(user, type)
    require "csv"

    file = Tempfile.new([type, ".csv"])

    CSV.open(file.path, "wb") do |csv|
      case type
      when "orders"
        csv << ["ID", "Date", "Total", "Status"]
        user.orders.find_each do |order|
          csv << [order.id, order.created_at, order.total, order.status]
        end
      when "customers"
        csv << ["ID", "Name", "Email", "Created"]
        user.customers.find_each do |customer|
          csv << [customer.id, customer.name, customer.email, customer.created_at]
        end
      end
    end

    file
  end
end

# app/controllers/exports_controller.rb
class ExportsController < ApplicationController
  def create
    ExportJob.perform_later(current_user.id, params[:export_type])

    redirect_to exports_path, notice: "Export started. You'll receive an email when ready."
  end

  def show
    @export = current_user.exports.find(params[:id])
    redirect_to rails_blob_path(@export.file, disposition: "attachment")
  end
end
```

### Pattern 2: Progress Tracking

```ruby
# app/jobs/export_with_progress_job.rb
class ExportWithProgressJob < ApplicationJob
  queue_as :low

  def perform(export_id)
    export = Export.find(export_id)
    export.update!(status: :processing)

    total = export.record_count
    processed = 0

    file = Tempfile.new(["export", ".csv"])

    CSV.open(file.path, "wb") do |csv|
      csv << export.headers

      export.records.find_in_batches(batch_size: 1000) do |batch|
        batch.each do |record|
          csv << export.row_for(record)
          processed += 1
        end

        # Update progress
        progress = (processed.to_f / total * 100).round
        export.update!(progress: progress)

        # Broadcast via Turbo Stream
        export.broadcast_replace_to(
          "export_#{export.id}",
          partial: "exports/progress",
          locals: { export: export }
        )
      end
    end

    # Attach file
    export.file.attach(
      io: File.open(file.path),
      filename: "#{export.name}_#{Date.current}.csv",
      content_type: "text/csv"
    )

    export.update!(status: :completed, completed_at: Time.current)

    # Cleanup
    file.unlink

    # Notify user
    ExportMailer.ready(export.user, export).deliver_later
  end
end

# app/models/export.rb
class Export < ApplicationRecord
  belongs_to :user
  has_one_attached :file

  enum status: { pending: 0, processing: 1, completed: 2, failed: 3 }

  def record_count
    case export_type
    when "orders"
      user.orders.count
    when "customers"
      user.customers.count
    end
  end

  def records
    case export_type
    when "orders"
      user.orders
    when "customers"
      user.customers
    end
  end

  def headers
    case export_type
    when "orders"
      ["ID", "Date", "Total", "Status"]
    when "customers"
      ["ID", "Name", "Email", "Phone"]
    end
  end

  def row_for(record)
    case export_type
    when "orders"
      [record.id, record.created_at, record.total, record.status]
    when "customers"
      [record.id, record.name, record.email, record.phone]
    end
  end
end
```

### Pattern 3: Excel Export with Styling

```ruby
# Gemfile
gem "caxlsx"
gem "caxlsx_rails"

# app/jobs/excel_export_job.rb
class ExcelExportJob < ApplicationJob
  queue_as :low

  def perform(user_id, export_type)
    user = User.find(user_id)

    file = Tempfile.new(["export", ".xlsx"])

    Axlsx::Package.new do |p|
      wb = p.workbook

      # Define styles
      header_style = wb.styles.add_style(
        b: true,
        bg_color: "4472C4",
        fg_color: "FFFFFF",
        alignment: { horizontal: :center }
      )

      currency_style = wb.styles.add_style(
        format_code: "$#,##0.00"
      )

      # Add worksheet
      wb.add_worksheet(name: export_type.titleize) do |sheet|
        case export_type
        when "orders"
          sheet.add_row ["ID", "Date", "Customer", "Total", "Status"],
                        style: header_style

          user.orders.includes(:customer).find_each do |order|
            sheet.add_row [
              order.id,
              order.created_at.to_date,
              order.customer.name,
              order.total,
              order.status
            ], style: [nil, nil, nil, currency_style, nil]
          end

          # Auto-size columns
          sheet.column_widths 10, 15, 25, 15, 15
        end
      end

      p.serialize(file.path)
    end

    # Save export
    export = user.exports.create!(export_type: export_type, status: :completed)
    export.file.attach(
      io: File.open(file.path),
      filename: "#{export_type}_#{Date.current}.xlsx",
      content_type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    file.unlink

    ExportMailer.ready(user, export).deliver_later
  end
end
```

### Pattern 4: Streaming Large Exports

```ruby
# app/jobs/streaming_export_job.rb
class StreamingExportJob < ApplicationJob
  queue_as :low

  def perform(user_id, export_type, filters = {})
    user = User.find(user_id)

    # Use streaming to handle millions of records
    file = Tempfile.new(["export", ".csv"])

    CSV.open(file.path, "wb") do |csv|
      csv << headers_for(export_type)

      # Stream from database in batches
      records_for(user, export_type, filters).find_in_batches(batch_size: 10_000) do |batch|
        batch.each do |record|
          csv << row_for(record, export_type)
        end

        # Allow other jobs to run
        sleep 0.1
      end
    end

    # Compress for large files
    compressed = compress_file(file.path)

    export = user.exports.create!(export_type: export_type, status: :completed)
    export.file.attach(
      io: File.open(compressed),
      filename: "#{export_type}_#{Date.current}.csv.gz",
      content_type: "application/gzip"
    )

    file.unlink
    File.unlink(compressed)

    ExportMailer.ready(user, export).deliver_later
  end

  private

  def compress_file(path)
    compressed_path = "#{path}.gz"

    Zlib::GzipWriter.open(compressed_path) do |gz|
      gz.write File.read(path)
    end

    compressed_path
  end

  def records_for(user, type, filters)
    case type
    when "orders"
      scope = user.orders
      scope = scope.where(status: filters[:status]) if filters[:status]
      scope = scope.where("created_at >= ?", filters[:start_date]) if filters[:start_date]
      scope
    end
  end

  def headers_for(type)
    case type
    when "orders"
      ["Order ID", "Date", "Customer", "Items", "Total", "Status"]
    end
  end

  def row_for(record, type)
    case type
    when "orders"
      [
        record.id,
        record.created_at.iso8601,
        record.customer_name,
        record.items.count,
        record.total,
        record.status
      ]
    end
  end
end
```

### Pattern 5: PDF Report Generation

```ruby
# Gemfile
gem "prawn"
gem "prawn-table"

# app/jobs/pdf_report_job.rb
class PdfReportJob < ApplicationJob
  queue_as :low

  def perform(user_id, report_type)
    user = User.find(user_id)

    pdf = generate_pdf(user, report_type)

    export = user.exports.create!(export_type: report_type, status: :completed)
    export.file.attach(
      io: StringIO.new(pdf),
      filename: "#{report_type}_#{Date.current}.pdf",
      content_type: "application/pdf"
    )

    ExportMailer.ready(user, export).deliver_later
  end

  private

  def generate_pdf(user, type)
    Prawn::Document.new do |pdf|
      # Header
      pdf.text "#{type.titleize} Report", size: 24, style: :bold
      pdf.text "Generated: #{Time.current.to_s(:long)}", size: 10
      pdf.move_down 20

      case type
      when "sales_summary"
        generate_sales_summary(pdf, user)
      when "customer_list"
        generate_customer_list(pdf, user)
      end
    end.render
  end

  def generate_sales_summary(pdf, user)
    orders = user.orders.where("created_at >= ?", 30.days.ago)

    # Summary stats
    pdf.text "Last 30 Days", size: 16, style: :bold
    pdf.move_down 10

    stats = [
      ["Total Orders", orders.count],
      ["Total Revenue", number_to_currency(orders.sum(:total))],
      ["Average Order", number_to_currency(orders.average(:total))]
    ]

    pdf.table(stats, width: 300)
    pdf.move_down 20

    # Order table
    pdf.text "Recent Orders", size: 14, style: :bold
    pdf.move_down 10

    table_data = [["Date", "Customer", "Items", "Total"]]
    orders.limit(50).each do |order|
      table_data << [
        order.created_at.to_date,
        order.customer_name,
        order.items.count,
        number_to_currency(order.total)
      ]
    end

    pdf.table(table_data, header: true, width: pdf.bounds.width)
  end
end
```

### Pattern 6: Scheduled Recurring Exports

```ruby
# app/jobs/recurring_export_job.rb
class RecurringExportJob < ApplicationJob
  queue_as :low

  def perform(export_schedule_id)
    schedule = ExportSchedule.find(export_schedule_id)

    schedule.users.find_each do |user|
      ExportJob.perform_later(user.id, schedule.export_type, schedule.filters)
    end
  end
end

# config/schedule.yml (sidekiq-cron)
daily_sales_export:
  cron: "0 6 * * *"  # 6 AM daily
  class: "RecurringExportJob"
  args: [1]  # ExportSchedule ID

monthly_report:
  cron: "0 0 1 * *"  # First of month
  class: "RecurringExportJob"
  args: [2]
```

### Pattern 7: Export with Custom Formatting

```ruby
# app/services/csv_formatter.rb
class CsvFormatter
  def initialize(records, options = {})
    @records = records
    @options = options
  end

  def to_csv
    CSV.generate do |csv|
      csv << headers

      @records.find_each do |record|
        csv << format_row(record)
      end
    end
  end

  private

  def headers
    @options[:headers] || default_headers
  end

  def format_row(record)
    @options[:formatter]&.call(record) || default_formatter(record)
  end

  def default_headers
    ["ID", "Created At", "Status"]
  end

  def default_formatter(record)
    [record.id, record.created_at, record.status]
  end
end

# app/jobs/custom_format_export_job.rb
class CustomFormatExportJob < ApplicationJob
  queue_as :low

  def perform(user_id, model_class, options = {})
    user = User.find(user_id)
    records = model_class.constantize.where(user: user)

    csv_data = CsvFormatter.new(records, options).to_csv

    export = user.exports.create!(export_type: model_class.underscore, status: :completed)
    export.file.attach(
      io: StringIO.new(csv_data),
      filename: "#{model_class.underscore}_#{Date.current}.csv",
      content_type: "text/csv"
    )

    ExportMailer.ready(user, export).deliver_later
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Loading all records at once | Memory exhaustion | Use `find_in_batches` |
| No file cleanup | Disk space waste | Delete tempfiles after upload |
| Blocking job queue | Other jobs delayed | Use low-priority queue |
| No expiration | Storage costs | Auto-delete after 7 days |
| Missing error handling | Silent failures | Add retry logic |

```ruby
# Bad: Loads all into memory
csv_data = CSV.generate do |csv|
  orders = Order.all  # Could be millions!
  orders.each { |order| csv << [order.data] }
end

# Good: Stream in batches
CSV.open(file, "wb") do |csv|
  Order.find_in_batches(batch_size: 1000) do |batch|
    batch.each { |order| csv << [order.data] }
  end
end
```

## Export Cleanup

```ruby
# app/jobs/cleanup_exports_job.rb
class CleanupExportsJob < ApplicationJob
  queue_as :low

  def perform
    # Delete exports older than 7 days
    Export.where("created_at < ?", 7.days.ago).find_each do |export|
      export.file.purge_later if export.file.attached?
      export.destroy
    end
  end
end

# config/schedule.yml
cleanup_old_exports:
  cron: "0 2 * * *"  # 2 AM daily
  class: "CleanupExportsJob"
```

## Related Skills

- [solid-queue/jobs](../solid-queue/jobs.md): Background job basics
- [sidekiq/jobs](../sidekiq/jobs.md): Advanced job patterns
- [mailers](./mailers.md): Email export notifications
- [imports](./imports.md): CSV import jobs

## References

- [Active Storage](https://guides.rubyonrails.org/active_storage_overview.html)
- [CSV Documentation](https://ruby-doc.org/stdlib/libdoc/csv/rdoc/CSV.html)
- [Prawn PDF](https://github.com/prawnpdf/prawn)
- [Caxlsx](https://github.com/caxlsx/caxlsx)
