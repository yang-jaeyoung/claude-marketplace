# ActiveRecord Query Basics

## Overview

ActiveRecord provides a rich query interface that generates efficient SQL while keeping your code readable and database-agnostic.

## Finding Records

### Single Record

```ruby
# Find by ID (raises RecordNotFound if not found)
Post.find(1)
Post.find(1, 2, 3)  # Returns array

# Find by ID (returns nil if not found)
Post.find_by(id: 1)
Post.find_by(title: "Hello", published: true)

# First/Last
Post.first
Post.last
Post.first!  # Raises if not found
Post.take    # Random record (no order)
Post.take(5) # Random 5 records

# Find or initialize/create
Post.find_or_initialize_by(title: "Hello")
Post.find_or_create_by(title: "Hello")
Post.find_or_create_by!(title: "Hello")  # Raises on validation failure
```

### Multiple Records

```ruby
Post.all                    # All records
Post.limit(10)              # First 10
Post.offset(5).limit(10)    # Skip 5, take 10
Post.first(5)               # First 5
Post.last(5)                # Last 5
```

## Where Conditions

### Basic Where

```ruby
# Hash conditions (recommended)
Post.where(published: true)
Post.where(status: "active", user_id: 1)

# String conditions (be careful with SQL injection)
Post.where("published = ?", true)
Post.where("created_at > ?", 1.week.ago)

# Named placeholders
Post.where("title LIKE :query OR body LIKE :query", query: "%ruby%")

# Array of values
Post.where(status: ["active", "pending"])
Post.where(id: [1, 2, 3])

# Range
Post.where(created_at: 1.week.ago..Time.current)
Post.where(views_count: 100..)  # >= 100
Post.where(views_count: ..100)  # <= 100
```

### NOT Conditions

```ruby
Post.where.not(published: false)
Post.where.not(status: ["archived", "deleted"])
Post.where.not(user_id: nil)
```

### OR Conditions

```ruby
Post.where(published: true).or(Post.where(featured: true))

# More complex OR
Post.where("published = ? OR (draft = ? AND user_id = ?)", true, true, current_user.id)
```

### NULL Checks

```ruby
Post.where(deleted_at: nil)      # IS NULL
Post.where.not(deleted_at: nil)  # IS NOT NULL

# Rails 7+ missing/present
Post.where.missing(:comments)    # Posts without comments
Post.where.associated(:comments) # Posts with comments
```

## Ordering

```ruby
Post.order(:created_at)           # ASC
Post.order(created_at: :desc)     # DESC
Post.order(:user_id, created_at: :desc)  # Multiple

# Raw SQL order
Post.order("LOWER(title)")
Post.order(Arel.sql("RANDOM()"))  # Random order
```

## Select and Pluck

```ruby
# Select specific columns
Post.select(:id, :title)
Post.select("id, title, LENGTH(body) as body_length")

# Pluck returns arrays (more memory efficient)
Post.pluck(:id)                    # [1, 2, 3]
Post.pluck(:id, :title)            # [[1, "Hello"], [2, "World"]]

# IDs only
Post.ids  # Equivalent to pluck(:id)

# Distinct
Post.distinct.pluck(:user_id)
Post.select(:user_id).distinct
```

## Grouping and Aggregates

```ruby
# Count
Post.count
Post.where(published: true).count
Post.count(:user_id)  # Count non-null user_ids

# Group by
Post.group(:status).count
# => { "draft" => 5, "published" => 10 }

Post.group(:user_id).count
Post.group("DATE(created_at)").count

# Having
Post.group(:user_id).having("COUNT(*) > ?", 5).count

# Aggregates
Post.sum(:views_count)
Post.average(:views_count)
Post.minimum(:created_at)
Post.maximum(:created_at)
```

## Joins

```ruby
# Inner join
Post.joins(:user)
Post.joins(:user, :comments)
Post.joins(comments: :user)  # Nested join

# Left outer join
Post.left_joins(:comments)
Post.left_outer_joins(:comments)

# Condition on joined table
Post.joins(:user).where(users: { active: true })

# Raw join
Post.joins("LEFT JOIN comments ON comments.post_id = posts.id")
```

## Includes (Eager Loading)

```ruby
# Preload (separate queries)
Post.includes(:user)
# SELECT * FROM posts
# SELECT * FROM users WHERE id IN (...)

# Eager load (single JOIN query)
Post.eager_load(:user)
# SELECT * FROM posts LEFT OUTER JOIN users ON ...

# Rails chooses strategy
Post.includes(:user, :comments)
Post.includes(comments: :user)

# Force join with condition
Post.includes(:user).where(users: { active: true }).references(:users)
```

## Scoping

```ruby
# Default scope (use sparingly)
class Post < ApplicationRecord
  default_scope { order(:created_at) }
end

# Unscoped
Post.unscoped.all
Post.unscoped { Post.where(id: 1) }

# Rewhere (replace condition)
Post.where(status: "draft").rewhere(status: "published")

# Reorder
Post.order(:title).reorder(:created_at)

# Reselect
Post.select(:id).reselect(:id, :title)
```

## Existence Checks

```ruby
Post.exists?(1)
Post.exists?(title: "Hello")
Post.where(published: true).exists?

# Any/none/one/many
Post.any?    # Same as exists?
Post.none?   # !exists?
Post.one?    # Exactly one record
Post.many?   # More than one record

# Empty check
Post.where(published: true).empty?
Post.where(published: true).present?
```

## Batching

```ruby
# find_each (default batch size: 1000)
Post.find_each do |post|
  post.process
end

Post.find_each(batch_size: 500) do |post|
  post.process
end

# find_in_batches (yields arrays)
Post.find_in_batches(batch_size: 1000) do |posts|
  posts.each { |post| post.process }
end

# in_batches (yields relations)
Post.in_batches(of: 1000) do |batch|
  batch.update_all(processed: true)
end
```

## Calculations

```ruby
Post.count
Post.count(:user_id)           # Count non-null
Post.distinct.count(:user_id)  # Count unique

Post.sum(:views_count)
Post.average(:views_count).to_f
Post.minimum(:created_at)
Post.maximum(:views_count)

# With conditions
Post.published.sum(:views_count)
```

## Query Methods Reference

| Method | Description |
|--------|-------------|
| `where` | Add conditions |
| `order` | Set ordering |
| `select` | Choose columns |
| `limit` | Limit results |
| `offset` | Skip records |
| `joins` | Inner join |
| `left_joins` | Left outer join |
| `includes` | Eager load |
| `group` | Group by |
| `having` | Group conditions |
| `distinct` | Remove duplicates |
| `pluck` | Return arrays |
| `find_each` | Batch iteration |

## Related

- [joins.md](./joins.md): Advanced joins
- [n-plus-one.md](./n-plus-one.md): N+1 prevention
- [query-object.md](./query-object.md): Query objects
