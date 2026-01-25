# Export and Import

## Overview

Async CSV/Excel export with Solid Queue, CSV import with batch processing and validation, progress tracking with Turbo Streams.

## Prerequisites

- [background/solid-queue](../../background/solid-queue.md)
- [hotwire/turbo-streams](../../hotwire/turbo-streams.md)

## Quick Start

```ruby
gem "csv"
gem "rubyXL" # For Excel
```

## Implementation

### Export Job

```ruby
# app/jobs/export_users_job.rb
class ExportUsersJob < ApplicationJob
  queue_as :default

  def perform(user_id, filters = {})
    user = User.find(user_id)
    users = User.where(filters)

    csv_data = CSV.generate(headers: true) do |csv|
      csv << ["Name", "Email", "Created At"]
      users.find_each do |u|
        csv << [u.name, u.email, u.created_at]
      end
    end

    # Store in ActiveStorage
    user.exports.attach(
      io: StringIO.new(csv_data),
      filename: "users_#{Date.today}.csv",
      content_type: "text/csv"
    )

    # Notify user
    ExportMailer.ready(user, user.exports.last).deliver_now
  end
end
```

### Import Service

```ruby
# app/services/user_import_service.rb
class UserImportService
  def initialize(file, account)
    @file = file
    @account = account
    @errors = []
  end

  def import
    CSV.foreach(@file.path, headers: true).with_index do |row, index|
      user = @account.users.new(
        name: row["Name"],
        email: row["Email"]
      )

      unless user.save
        @errors << { row: index + 2, errors: user.errors.full_messages }
      end
    end

    { success: @errors.empty?, errors: @errors }
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Synchronous export | Request timeout | Use background job |
| Loading all records | Memory issues | Use `find_each` |
| No validation on import | Bad data | Validate before save |

## Related Skills

- [background/solid-queue](../../background/solid-queue.md)
- [models/validations](../../models/validations.md)

## References

- [Ruby CSV](https://ruby-doc.org/stdlib/libdoc/csv/rdoc/CSV.html)
