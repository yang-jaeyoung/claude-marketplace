# Production Migration Patterns

## Overview

Zero-downtime database migrations require careful planning to avoid locking tables, breaking running code, or losing data. This guide covers safe migration patterns for production Rails applications.

## When to Use

- When deploying migrations to production
- When modifying large tables
- When changing column types
- When removing columns or tables

## Quick Start

### Strong Migrations Setup

```ruby
# Gemfile
gem "strong_migrations"
```

```ruby
# config/initializers/strong_migrations.rb
StrongMigrations.auto_analyze = true
StrongMigrations.start_after = 20240101000000

# Safe operations timeout
StrongMigrations.lock_timeout = 10.seconds
StrongMigrations.statement_timeout = 1.hour

# Target version (optional)
StrongMigrations.target_postgresql_version = "16"
```

## Safe Migration Patterns

### Adding Columns

```ruby
# SAFE: Adding nullable column
class AddDescriptionToPosts < ActiveRecord::Migration[8.0]
  def change
    add_column :posts, :description, :text
  end
end

# SAFE: Adding column with default (PostgreSQL 11+)
class AddStatusToPosts < ActiveRecord::Migration[8.0]
  def change
    add_column :posts, :status, :string, default: "draft", null: false
  end
end
```

### Adding Indexes

```ruby
# DANGEROUS: Locks table
class AddIndexToUsersEmail < ActiveRecord::Migration[8.0]
  def change
    add_index :users, :email  # Table locked during build
  end
end

# SAFE: Concurrent index creation
class AddIndexToUsersEmail < ActiveRecord::Migration[8.0]
  disable_ddl_transaction!

  def change
    add_index :users, :email, algorithm: :concurrently
  end
end
```

### Removing Columns

```ruby
# Step 1: Stop using column in code (deploy first)
# Remove all reads/writes to the column

# Step 2: Ignore column in model (deploy)
class User < ApplicationRecord
  self.ignored_columns += ["old_column"]
end

# Step 3: Remove column (separate deploy)
class RemoveOldColumnFromUsers < ActiveRecord::Migration[8.0]
  def change
    safety_assured { remove_column :users, :old_column }
  end
end
```

### Renaming Columns

```ruby
# DON'T: Direct rename breaks running code
class RenameEmailToEmailAddress < ActiveRecord::Migration[8.0]
  def change
    rename_column :users, :email, :email_address  # DANGEROUS
  end
end

# DO: Multi-step safe rename
# Step 1: Add new column
class AddEmailAddressToUsers < ActiveRecord::Migration[8.0]
  def change
    add_column :users, :email_address, :string
  end
end

# Step 2: Copy data (background job or migration)
class BackfillEmailAddress < ActiveRecord::Migration[8.0]
  disable_ddl_transaction!

  def up
    User.in_batches.update_all("email_address = email")
  end
end

# Step 3: Update code to use new column (deploy)
# Step 4: Add constraints
class AddEmailAddressConstraints < ActiveRecord::Migration[8.0]
  def change
    change_column_null :users, :email_address, false
  end
end

# Step 5: Remove old column (after code fully migrated)
class RemoveEmailFromUsers < ActiveRecord::Migration[8.0]
  def change
    safety_assured { remove_column :users, :email }
  end
end
```

### Changing Column Types

```ruby
# DANGEROUS: May lock table, lose data
class ChangeDescriptionType < ActiveRecord::Migration[8.0]
  def change
    change_column :posts, :description, :text  # DANGEROUS
  end
end

# SAFE: Add new column, migrate, remove old
# Step 1: Add new column
class AddDescriptionTextToPosts < ActiveRecord::Migration[8.0]
  def change
    add_column :posts, :description_text, :text
  end
end

# Step 2: Dual-write in model
class Post < ApplicationRecord
  before_save :sync_description

  private

  def sync_description
    self.description_text = description
  end
end

# Step 3: Backfill
class BackfillDescriptionText < ActiveRecord::Migration[8.0]
  disable_ddl_transaction!

  def up
    Post.in_batches.update_all("description_text = description::text")
  end
end

# Step 4: Switch reads to new column
# Step 5: Stop writes to old column
# Step 6: Remove old column
```

### Adding NOT NULL Constraint

```ruby
# DANGEROUS: Scans entire table
class AddNotNullToUsersName < ActiveRecord::Migration[8.0]
  def change
    change_column_null :users, :name, false  # DANGEROUS for large tables
  end
end

# SAFE: Validate in separate step
class AddNotNullToUsersName < ActiveRecord::Migration[8.0]
  def change
    add_check_constraint :users, "name IS NOT NULL",
                         name: "users_name_null",
                         validate: false
  end
end

class ValidateUsersNameNotNull < ActiveRecord::Migration[8.0]
  def change
    validate_check_constraint :users, name: "users_name_null"
    change_column_null :users, :name, false
    remove_check_constraint :users, name: "users_name_null"
  end
end
```

### Adding Foreign Keys

```ruby
# DANGEROUS: Validates all existing data
class AddForeignKeyToComments < ActiveRecord::Migration[8.0]
  def change
    add_foreign_key :comments, :posts  # DANGEROUS
  end
end

# SAFE: Add unvalidated, then validate
class AddForeignKeyToComments < ActiveRecord::Migration[8.0]
  def change
    add_foreign_key :comments, :posts, validate: false
  end
end

class ValidateCommentsForeignKey < ActiveRecord::Migration[8.0]
  def change
    validate_foreign_key :comments, :posts
  end
end
```

## Backfilling Data

### Batch Updates

```ruby
class BackfillUserFullName < ActiveRecord::Migration[8.0]
  disable_ddl_transaction!

  def up
    User.unscoped.in_batches(of: 1000) do |batch|
      batch.update_all("full_name = CONCAT(first_name, ' ', last_name)")
      sleep(0.1)  # Reduce database load
    end
  end
end
```

### Background Job Backfill

```ruby
# Migration just adds column
class AddProcessedAtToOrders < ActiveRecord::Migration[8.0]
  def change
    add_column :orders, :processed_at, :datetime
  end
end

# Background job handles data
class BackfillOrdersProcessedAtJob < ApplicationJob
  def perform(start_id, end_id)
    Order.where(id: start_id..end_id)
         .where(processed_at: nil)
         .find_each do |order|
      order.update_column(:processed_at, order.completed_at || order.created_at)
    end
  end
end

# Enqueue jobs
Order.in_batches(of: 10_000) do |batch|
  BackfillOrdersProcessedAtJob.perform_later(batch.minimum(:id), batch.maximum(:id))
end
```

### Data Migration Best Practices

```ruby
# app/services/data_migrations/backfill_user_settings.rb
module DataMigrations
  class BackfillUserSettings
    include Sidekiq::Job

    def perform(batch_start, batch_end)
      User.where(id: batch_start..batch_end)
          .where(settings: nil)
          .find_each do |user|
        user.update_column(:settings, default_settings)
      end
    end

    private

    def default_settings
      { notifications: true, theme: "light" }
    end
  end
end
```

## Large Table Operations

### Partitioning

```ruby
# Convert large table to partitioned
class PartitionEventsTable < ActiveRecord::Migration[8.0]
  def up
    # Create partitioned table
    execute <<~SQL
      CREATE TABLE events_partitioned (
        id BIGSERIAL,
        event_type VARCHAR(255),
        created_at TIMESTAMP NOT NULL,
        PRIMARY KEY (id, created_at)
      ) PARTITION BY RANGE (created_at);
    SQL

    # Create partitions
    execute <<~SQL
      CREATE TABLE events_y2024m01 PARTITION OF events_partitioned
      FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
    SQL

    # Migrate data in batches
    # Switch table names atomically
  end
end
```

### Online Schema Changes (pt-online-schema-change)

```bash
# For very large tables, use pt-online-schema-change
pt-online-schema-change \
  --alter "ADD COLUMN new_field VARCHAR(255)" \
  --execute \
  h=localhost,D=myapp_production,t=large_table
```

## Deployment Strategy

### Pre-Deployment Migrations

```yaml
# config/deploy.yml (Kamal)
# Migrations run before containers swap
```

### Separate Migration Deployment

```bash
# 1. Deploy code that works with both schemas
kamal deploy

# 2. Run migration
kamal app exec "bin/rails db:migrate"

# 3. Deploy code that uses new schema
kamal deploy
```

### Migration CI Checks

```yaml
# .github/workflows/migrations.yml
name: Migration Safety

on: [pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: password
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4

      - uses: ruby/setup-ruby@v1
        with:
          bundler-cache: true

      - name: Check migrations
        env:
          DATABASE_URL: postgres://postgres:password@localhost:5432/test
        run: |
          bin/rails db:setup
          bin/rails db:migrate:status
```

## Rollback Strategy

### Reversible Migrations

```ruby
class AddCategoryToPosts < ActiveRecord::Migration[8.0]
  def change
    # Automatically reversible
    add_column :posts, :category, :string
    add_index :posts, :category
  end
end
```

### Manual Rollback

```ruby
class ComplexMigration < ActiveRecord::Migration[8.0]
  def up
    add_column :posts, :metadata, :jsonb
    execute "UPDATE posts SET metadata = '{}' WHERE metadata IS NULL"
  end

  def down
    remove_column :posts, :metadata
  end
end
```

### Emergency Rollback

```bash
# Rollback last migration
kamal app exec "bin/rails db:rollback"

# Rollback multiple
kamal app exec "bin/rails db:rollback STEP=3"

# Rollback to specific version
kamal app exec "bin/rails db:migrate:down VERSION=20240101000000"
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Direct column rename | Breaks running code | Multi-step rename |
| Non-concurrent index | Table lock | algorithm: :concurrently |
| Inline data migration | Blocks deployment | Background jobs |
| No rollback plan | Stuck with errors | Test rollbacks |
| Large batch updates | Database load | In batches with sleep |

## Related Files

- [postgresql.md](./postgresql.md): PostgreSQL configuration
- [../kamal/zero-downtime.md](../kamal/zero-downtime.md): Zero-downtime deployment

## References

- [Strong Migrations](https://github.com/ankane/strong_migrations)
- [Rails Migrations](https://guides.rubyonrails.org/active_record_migrations.html)
- [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
