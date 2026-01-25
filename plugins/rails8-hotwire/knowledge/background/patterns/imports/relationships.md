# Import with Relationships

## Overview

Complex import pattern for creating records with associations. Uses transactions to maintain data integrity across related models.

## When to Use

- Importing orders with line items
- Creating users with profiles
- Building hierarchical data (parent/child)
- Need transactional consistency across models

## Code Example

```ruby
# app/jobs/complex_import_job.rb
class ComplexImportJob < ApplicationJob
  queue_as :default

  def perform(upload_id)
    upload = Upload.find(upload_id)
    upload.update!(status: :processing)

    results = { orders: 0, items: 0, customers: 0, errors: [] }

    CSV.foreach(upload.file.path, headers: true) do |row|
      ActiveRecord::Base.transaction do
        # Find or create customer
        customer = find_or_create_customer(row, upload)
        results[:customers] += 1 if customer.previously_new_record?

        # Create order
        order = create_order(row, customer, upload)
        results[:orders] += 1

        # Create order items
        items = create_order_items(row, order)
        results[:items] += items.size
      end
    rescue => e
      results[:errors] << "Row #{row.line_number}: #{e.message}"
      # Continue with next row
    end

    upload.update!(
      status: :completed,
      results: results,
      completed_at: Time.current
    )

    ImportMailer.completed(upload.user, upload).deliver_later
  end

  private

  def find_or_create_customer(row, upload)
    Customer.find_or_create_by!(
      email: row["customer_email"],
      company: upload.company
    ) do |customer|
      customer.name = row["customer_name"]
      customer.phone = row["customer_phone"]
    end
  end

  def create_order(row, customer, upload)
    Order.create!(
      customer: customer,
      company: upload.company,
      order_number: row["order_number"],
      ordered_at: Date.parse(row["order_date"]),
      status: row["status"]
    )
  end

  def create_order_items(row, order)
    items = []

    # Assuming items are in columns: item1_sku, item1_qty, item2_sku, item2_qty, etc.
    (1..5).each do |i|
      sku = row["item#{i}_sku"]
      break if sku.blank?

      product = Product.find_by!(sku: sku)
      item = order.items.create!(
        product: product,
        quantity: row["item#{i}_qty"].to_i,
        price: row["item#{i}_price"]
      )
      items << item
    end

    items
  end
end
```

## CSV Format Example

```csv
customer_email,customer_name,customer_phone,order_number,order_date,status,item1_sku,item1_qty,item1_price,item2_sku,item2_qty,item2_price
john@example.com,John Doe,555-1234,ORD-001,2024-01-15,pending,SKU-A,2,19.99,SKU-B,1,29.99
jane@example.com,Jane Smith,555-5678,ORD-002,2024-01-16,shipped,SKU-C,3,9.99,,,
```

## Alternative: Nested Attributes

```ruby
# For simpler relationships, use accepts_nested_attributes_for
class Order < ApplicationRecord
  belongs_to :customer
  has_many :items
  accepts_nested_attributes_for :items
end

def process_row(row, upload)
  order = Order.new(
    customer: find_customer(row),
    order_number: row["order_number"],
    items_attributes: build_items(row)
  )
  order.save!
end

def build_items(row)
  (1..5).map do |i|
    next if row["item#{i}_sku"].blank?

    {
      product_id: Product.find_by(sku: row["item#{i}_sku"])&.id,
      quantity: row["item#{i}_qty"],
      price: row["item#{i}_price"]
    }
  end.compact
end
```

## Key Features

- **Transactions**: All-or-nothing for each row
- **Find or Create**: Prevents duplicate customers
- **Association Building**: Creates related records
- **Error Isolation**: One row failure doesn't stop others
- **Detailed Counting**: Tracks created records per model

## Transaction Strategy

```ruby
# Option 1: Per-row transactions (shown above)
# Pro: Failures isolated to single row
# Con: Slower due to transaction overhead

# Option 2: Batch transactions
CSV.foreach(file.path, headers: true).each_slice(50) do |batch|
  ActiveRecord::Base.transaction do
    batch.each { |row| process_row(row) }
  end
end
# Pro: Faster
# Con: One error fails entire batch

# Option 3: Single transaction
ActiveRecord::Base.transaction do
  CSV.foreach(file.path, headers: true) { |row| process_row(row) }
end
# Pro: Fastest, guaranteed consistency
# Con: Any error rolls back entire import
```

## Handling Missing References

```ruby
def create_order_items(row, order)
  items = []

  (1..5).each do |i|
    sku = row["item#{i}_sku"]
    next if sku.blank?

    product = Product.find_by(sku: sku)
    unless product
      raise "Product not found: #{sku}"
      # Or create placeholder: product = Product.create!(sku: sku, name: "Unknown")
      # Or skip: next
    end

    items << order.items.create!(
      product: product,
      quantity: row["item#{i}_qty"],
      price: row["item#{i}_price"]
    )
  end

  items
end
```

## Related Patterns

- [Basic CSV Import](./basic-csv.md): Simpler single-model version
- [Import with Validation](./validation.md): Add pre-validation
- [Import Error Reporting](./error-reporting.md): Detailed error tracking
