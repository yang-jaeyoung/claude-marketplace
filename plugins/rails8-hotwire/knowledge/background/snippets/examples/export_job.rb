# Complete CSV Export Job with Progress Tracking
#
# Features:
# - Memory-efficient streaming with find_in_batches
# - Progress tracking with Turbo Stream broadcasts
# - Active Storage integration
# - Email notification on completion
# - Automatic cleanup of temp files
# - Error handling and retry logic
#
# Usage:
#   ExportJob.perform_later(current_user.id, "orders", { status: "completed" })

class ExportJob < ApplicationJob
  queue_as :low

  retry_on StandardError, wait: :polynomially_longer, attempts: 3

  def perform(user_id, export_type, filters = {})
    user = User.find(user_id)

    # Create export record
    export = user.exports.create!(
      export_type: export_type,
      status: :processing,
      filters: filters,
      progress: 0
    )

    # Generate CSV file
    file = generate_csv(user, export_type, filters, export)

    # Attach to Active Storage
    export.file.attach(
      io: File.open(file.path),
      filename: "#{export_type}_#{Date.current.strftime('%Y%m%d')}.csv",
      content_type: "text/csv"
    )

    # Mark as completed
    export.update!(
      status: :completed,
      progress: 100,
      completed_at: Time.current
    )

    # Send notification email
    ExportMailer.ready(user, export).deliver_later

    # Cleanup temp file
    file.unlink

    Rails.logger.info "Export completed: #{export.id}"
  rescue => e
    # Mark export as failed
    export&.update!(
      status: :failed,
      error_message: e.message
    )

    # Send error notification
    ExportMailer.failed(user, export).deliver_later if export

    Rails.logger.error "Export failed: #{e.message}"
    Sentry.capture_exception(e) if defined?(Sentry)

    raise  # Re-raise for retry
  end

  private

  def generate_csv(user, export_type, filters, export)
    require "csv"

    file = Tempfile.new([export_type, ".csv"])

    CSV.open(file.path, "wb") do |csv|
      # Write headers
      csv << headers_for(export_type)

      # Get total count for progress
      records = records_for(user, export_type, filters)
      total = records.count
      processed = 0

      # Stream records in batches
      records.find_in_batches(batch_size: 1000) do |batch|
        batch.each do |record|
          csv << row_for(record, export_type)
          processed += 1
        end

        # Update progress
        if total > 0
          progress = (processed.to_f / total * 100).round
          export.update!(progress: progress)

          # Broadcast progress via Turbo Stream
          broadcast_progress(export, progress)
        end

        # Throttle to avoid overwhelming database
        sleep 0.1 if total > 10_000
      end
    end

    file
  end

  def records_for(user, export_type, filters)
    case export_type
    when "orders"
      scope = user.orders.includes(:customer, :items)
      scope = scope.where(status: filters[:status]) if filters[:status].present?
      scope = scope.where("created_at >= ?", filters[:start_date]) if filters[:start_date].present?
      scope = scope.where("created_at <= ?", filters[:end_date]) if filters[:end_date].present?
      scope
    when "customers"
      scope = user.customers
      scope = scope.where(status: filters[:status]) if filters[:status].present?
      scope
    when "products"
      scope = user.products
      scope = scope.where(category: filters[:category]) if filters[:category].present?
      scope
    else
      raise ArgumentError, "Unknown export type: #{export_type}"
    end
  end

  def headers_for(export_type)
    case export_type
    when "orders"
      [
        "Order ID",
        "Date",
        "Customer Name",
        "Customer Email",
        "Items Count",
        "Total Amount",
        "Status",
        "Payment Method",
        "Shipping Address",
        "Notes"
      ]
    when "customers"
      [
        "Customer ID",
        "Name",
        "Email",
        "Phone",
        "Company",
        "Address",
        "City",
        "State",
        "Zip",
        "Country",
        "Created At",
        "Total Orders",
        "Total Spent"
      ]
    when "products"
      [
        "Product ID",
        "SKU",
        "Name",
        "Category",
        "Price",
        "Cost",
        "Quantity",
        "Status",
        "Created At"
      ]
    end
  end

  def row_for(record, export_type)
    case export_type
    when "orders"
      [
        record.id,
        record.created_at.to_s(:db),
        record.customer&.name,
        record.customer&.email,
        record.items.size,
        record.total,
        record.status,
        record.payment_method,
        format_address(record.shipping_address),
        record.notes
      ]
    when "customers"
      [
        record.id,
        record.name,
        record.email,
        record.phone,
        record.company,
        record.address,
        record.city,
        record.state,
        record.zip,
        record.country,
        record.created_at.to_s(:db),
        record.orders.count,
        record.orders.sum(:total)
      ]
    when "products"
      [
        record.id,
        record.sku,
        record.name,
        record.category,
        record.price,
        record.cost,
        record.quantity,
        record.status,
        record.created_at.to_s(:db)
      ]
    end
  end

  def format_address(address)
    return "" if address.blank?

    "#{address[:street]}, #{address[:city]}, #{address[:state]} #{address[:zip]}"
  end

  def broadcast_progress(export, progress)
    Turbo::StreamsChannel.broadcast_replace_to(
      "export_#{export.id}",
      target: "export_#{export.id}_progress",
      partial: "exports/progress",
      locals: { export: export, progress: progress }
    )
  end
end

# Supporting Models and Mailers:

# app/models/export.rb
# class Export < ApplicationRecord
#   belongs_to :user
#   has_one_attached :file
#
#   enum status: { pending: 0, processing: 1, completed: 2, failed: 3 }
#
#   def download_url
#     Rails.application.routes.url_helpers.rails_blob_path(file, disposition: "attachment")
#   end
# end

# app/mailers/export_mailer.rb
# class ExportMailer < ApplicationMailer
#   def ready(user, export)
#     @user = user
#     @export = export
#     @download_url = export_url(export)
#
#     mail(to: user.email, subject: "Your #{export.export_type} export is ready")
#   end
#
#   def failed(user, export)
#     @user = user
#     @export = export
#
#     mail(to: user.email, subject: "Export failed: #{export.export_type}")
#   end
# end

# Migration:
# create_table :exports do |t|
#   t.references :user, null: false, foreign_key: true
#   t.string :export_type, null: false
#   t.integer :status, default: 0, null: false
#   t.integer :progress, default: 0
#   t.jsonb :filters
#   t.jsonb :results
#   t.text :error_message
#   t.datetime :completed_at
#   t.timestamps
# end
