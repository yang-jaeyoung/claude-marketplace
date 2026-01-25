# Excel Import

## Overview

Import pattern for processing Excel (.xlsx, .xls) files using the Roo gem. Supports multiple sheet formats with progress tracking.

## When to Use

- Need to import Excel files
- Users prefer Excel over CSV
- Want format flexibility (multiple sheets)
- Need cell formatting information

## Setup

```ruby
# Gemfile
gem "roo"

# bundle install
```

## Code Example

```ruby
# app/jobs/excel_import_job.rb
class ExcelImportJob < ApplicationJob
  queue_as :default

  def perform(upload_id)
    upload = Upload.find(upload_id)
    upload.update!(status: :processing)

    results = { created: 0, updated: 0, failed: 0, errors: [] }

    # Open Excel file
    spreadsheet = Roo::Spreadsheet.open(upload.file.path)
    header = spreadsheet.row(1)

    (2..spreadsheet.last_row).each do |i|
      row = Hash[[header, spreadsheet.row(i)].transpose]

      result = process_row(row, upload)
      update_results(results, result)

      # Update progress
      if i % 100 == 0
        progress = (i.to_f / spreadsheet.last_row * 100).round
        upload.update!(progress: progress)
      end
    end

    upload.update!(
      status: :completed,
      results: results,
      completed_at: Time.current
    )

    ImportMailer.completed(upload.user, upload).deliver_later
  end

  private

  def process_row(row, upload)
    product = Product.find_or_initialize_by(
      sku: row["SKU"],
      company: upload.company
    )

    product.assign_attributes(
      name: row["Name"],
      price: row["Price"],
      quantity: row["Quantity"],
      category: row["Category"]
    )

    if product.save
      status = product.previously_new_record? ? :created : :updated
      { status: status }
    else
      {
        status: :failed,
        error: "SKU #{row['SKU']}: #{product.errors.full_messages.join(', ')}"
      }
    end
  rescue => e
    {
      status: :failed,
      error: "SKU #{row['SKU']}: #{e.message}"
    }
  end
end
```

## Multi-Sheet Import

```ruby
# Process specific sheet
spreadsheet = Roo::Spreadsheet.open(upload.file.path)
spreadsheet.default_sheet = "Products" # or spreadsheet.sheet(0)

# Process all sheets
spreadsheet.sheets.each do |sheet_name|
  spreadsheet.default_sheet = sheet_name
  process_sheet(spreadsheet)
end
```

## Handle Different Formats

```ruby
# Auto-detect format
spreadsheet = Roo::Spreadsheet.open(upload.file.path)

# Force specific format
spreadsheet = Roo::Excelx.new(upload.file.path)  # .xlsx
spreadsheet = Roo::Excel.new(upload.file.path)   # .xls
```

## Key Features

- **Format Support**: .xlsx, .xls, .ods files
- **Header Mapping**: Converts rows to hashes using first row as keys
- **Progress Tracking**: Updates every 100 rows
- **Row Iteration**: Simple range-based iteration
- **Multiple Sheets**: Can process multiple sheets in one file

## Performance Considerations

- Roo loads entire sheet into memory
- Not suitable for files >10MB
- Consider converting to CSV server-side for very large files
- .xlsx is faster than .xls

## Error Handling

```ruby
begin
  spreadsheet = Roo::Spreadsheet.open(upload.file.path)
rescue Roo::Error => e
  upload.update!(
    status: :failed,
    error_message: "Invalid Excel file: #{e.message}"
  )
  return
end
```

## Related Patterns

- [Basic CSV Import](./basic-csv.md): CSV alternative
- [Batch Import with Progress](./batch-progress.md): Progress tracking details
