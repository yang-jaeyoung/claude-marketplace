# ActiveRecord Migrations

## Overview

Migrations are a way to alter your database schema over time in a consistent way. They use a Ruby DSL so you don't have to write SQL by hand.

## Creating Migrations

```bash
# Generate migration
rails generate migration AddStatusToPosts status:integer

# Generate model with migration
rails generate model Post title:string body:text published:boolean user:references

# Run migrations
rails db:migrate

# Rollback
rails db:rollback
rails db:rollback STEP=3
```

## Migration Structure

```ruby
# db/migrate/20240101000000_create_posts.rb
class CreatePosts < ActiveRecord::Migration[8.0]
  def change
    create_table :posts do |t|
      t.string :title, null: false
      t.text :body
      t.boolean :published, default: false
      t.references :user, null: false, foreign_key: true

      t.timestamps
    end

    add_index :posts, :title
    add_index :posts, [:user_id, :created_at]
  end
end
```

## Column Types

| Rails Type | PostgreSQL | MySQL | SQLite |
|------------|------------|-------|--------|
| `:string` | varchar(255) | varchar(255) | varchar |
| `:text` | text | text | text |
| `:integer` | integer | int(11) | integer |
| `:bigint` | bigint | bigint | integer |
| `:float` | float | float | float |
| `:decimal` | decimal | decimal | decimal |
| `:boolean` | boolean | tinyint(1) | boolean |
| `:date` | date | date | date |
| `:datetime` | timestamp | datetime | datetime |
| `:time` | time | time | time |
| `:binary` | bytea | blob | blob |
| `:json` | json | json | text |
| `:jsonb` | jsonb | N/A | text |
| `:uuid` | uuid | char(36) | varchar |

## Common Operations

### Add Column

```ruby
class AddStatusToPosts < ActiveRecord::Migration[8.0]
  def change
    add_column :posts, :status, :integer, default: 0, null: false
  end
end
```

### Remove Column

```ruby
class RemoveStatusFromPosts < ActiveRecord::Migration[8.0]
  def change
    remove_column :posts, :status, :integer
  end
end
```

### Rename Column

```ruby
class RenameStatusInPosts < ActiveRecord::Migration[8.0]
  def change
    rename_column :posts, :status, :state
  end
end
```

### Change Column

```ruby
class ChangeBodyInPosts < ActiveRecord::Migration[8.0]
  def up
    change_column :posts, :body, :text, null: false
  end

  def down
    change_column :posts, :body, :text, null: true
  end
end
```

### Add Index

```ruby
class AddIndexToPosts < ActiveRecord::Migration[8.0]
  def change
    add_index :posts, :slug, unique: true
    add_index :posts, [:user_id, :status]
    add_index :posts, :title, using: :gin  # PostgreSQL full-text
  end
end
```

### Add Reference

```ruby
class AddCategoryToPosts < ActiveRecord::Migration[8.0]
  def change
    add_reference :posts, :category, null: true, foreign_key: true
  end
end
```

## Reversible Migrations

```ruby
class AddDetailsToProducts < ActiveRecord::Migration[8.0]
  def change
    reversible do |dir|
      dir.up do
        # Code to run when migrating up
        execute <<-SQL
          ALTER TABLE products ADD CONSTRAINT check_price
          CHECK (price > 0)
        SQL
      end

      dir.down do
        # Code to run when rolling back
        execute <<-SQL
          ALTER TABLE products DROP CONSTRAINT check_price
        SQL
      end
    end
  end
end
```

## Data Migrations

```ruby
class BackfillPostSlugs < ActiveRecord::Migration[8.0]
  def up
    Post.find_each do |post|
      post.update_column(:slug, post.title.parameterize)
    end
  end

  def down
    Post.update_all(slug: nil)
  end
end
```

### Batch Processing (Large Tables)

```ruby
class BackfillLargeTable < ActiveRecord::Migration[8.0]
  disable_ddl_transaction!

  def up
    Post.in_batches(of: 1000) do |batch|
      batch.update_all(status: 0)
    end
  end
end
```

## PostgreSQL-Specific

### JSONB Column

```ruby
add_column :posts, :metadata, :jsonb, default: {}
add_index :posts, :metadata, using: :gin
```

### UUID Primary Key

```ruby
class CreateComments < ActiveRecord::Migration[8.0]
  def change
    create_table :comments, id: :uuid do |t|
      t.text :body
      t.references :post, type: :uuid, foreign_key: true
      t.timestamps
    end
  end
end
```

### Enum Type

```ruby
class AddStatusEnumToPosts < ActiveRecord::Migration[8.0]
  def up
    execute <<-SQL
      CREATE TYPE post_status AS ENUM ('draft', 'published', 'archived');
    SQL
    add_column :posts, :status, :post_status, default: 'draft'
  end

  def down
    remove_column :posts, :status
    execute <<-SQL
      DROP TYPE post_status;
    SQL
  end
end
```

## Zero-Downtime Migrations

### Adding Index Concurrently

```ruby
class AddIndexToPostsSlug < ActiveRecord::Migration[8.0]
  disable_ddl_transaction!

  def change
    add_index :posts, :slug, algorithm: :concurrently
  end
end
```

### Adding Column with Default (Safe in Rails 8)

```ruby
class AddViewsCountToPosts < ActiveRecord::Migration[8.0]
  def change
    # Rails 8: Safe to add column with default value
    add_column :posts, :views_count, :integer, default: 0, null: false
  end
end
```

### Removing Column Safely

```ruby
# 1. First: Ignore column in model
class Post < ApplicationRecord
  self.ignored_columns += ["legacy_column"]
end

# 2. Deploy
# 3. Then: Remove column
class RemoveLegacyColumnFromPosts < ActiveRecord::Migration[8.0]
  def change
    remove_column :posts, :legacy_column
  end
end
```

## Migration Commands

```bash
# Status
rails db:migrate:status

# Run specific migration
rails db:migrate VERSION=20240101000000

# Redo last migration
rails db:migrate:redo

# Reset database
rails db:reset          # drop + create + migrate + seed
rails db:migrate:reset  # drop + create + migrate

# Schema dump
rails db:schema:dump
rails db:schema:load
```

## Best Practices

| Practice | Description |
|----------|-------------|
| Small migrations | One change per migration |
| Reversible | Always make migrations reversible |
| Test rollback | Run `db:rollback` to verify |
| No model code | Don't reference models in migrations |
| Index foreign keys | Always index `_id` columns |
| Check constraints | Add database-level constraints |

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Lock timeout | Table locked during migration | Use `disable_ddl_transaction!` |
| Data loss | Column removal | Check production data first |
| Slow migration | Large table update | Use batches, background job |
| Rollback fails | Non-reversible change | Add `up` and `down` methods |

## Related

- [validations.md](./validations.md): Model validations
- [associations.md](./associations.md): Model associations
- [../../deploy/](../../deploy/): Deployment strategies
