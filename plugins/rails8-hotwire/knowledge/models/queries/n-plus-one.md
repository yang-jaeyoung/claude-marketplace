# N+1 Query Problem

## Overview

The N+1 query problem occurs when you load a collection of records (1 query) and then access an association on each record (N additional queries). This is one of the most common performance issues in Rails applications.

## The Problem

```ruby
# Controller
@posts = Post.all  # 1 query

# View
<% @posts.each do |post| %>
  <%= post.user.name %>  # N queries (one per post)
<% end %>
```

Generated SQL:
```sql
SELECT * FROM posts;
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE id = 2;
SELECT * FROM users WHERE id = 3;
-- ... repeated for each post
```

## The Solution: Eager Loading

```ruby
# includes - Rails chooses strategy
@posts = Post.includes(:user)
# 2 queries total:
# SELECT * FROM posts
# SELECT * FROM users WHERE id IN (1, 2, 3, ...)

# View works the same
<% @posts.each do |post| %>
  <%= post.user.name %>  # No additional queries!
<% end %>
```

## Eager Loading Methods

### includes

Rails chooses between preload and eager_load:

```ruby
# Separate queries (default)
Post.includes(:user)
# SELECT * FROM posts
# SELECT * FROM users WHERE id IN (...)

# Single query when filtering on association
Post.includes(:user).where(users: { active: true })
# SELECT posts.* FROM posts
# LEFT OUTER JOIN users ON users.id = posts.user_id
# WHERE users.active = true
```

### preload

Always uses separate queries:

```ruby
Post.preload(:user)
# SELECT * FROM posts
# SELECT * FROM users WHERE id IN (...)

# Multiple associations
Post.preload(:user, :comments)
Post.preload(comments: :user)  # Nested
```

### eager_load

Always uses LEFT OUTER JOIN:

```ruby
Post.eager_load(:user)
# SELECT posts.*, users.*
# FROM posts
# LEFT OUTER JOIN users ON users.id = posts.user_id

# Good for filtering on associations
Post.eager_load(:user).where(users: { active: true })
```

### When to Use Each

| Method | Use When |
|--------|----------|
| `includes` | Default choice, Rails optimizes |
| `preload` | Need separate queries, large associations |
| `eager_load` | Filtering/ordering by association |

## Nested Associations

```ruby
# Load multiple levels
Post.includes(comments: :user)
# SELECT * FROM posts
# SELECT * FROM comments WHERE post_id IN (...)
# SELECT * FROM users WHERE id IN (...)

# Multiple associations at same level
Post.includes(:user, :tags, comments: :user)

# Deep nesting
Order.includes(line_items: { product: :category })
```

## Conditional Eager Loading

```ruby
# Load conditionally
Post.includes(:comments).where(comments: { approved: true })

# Must use references with string conditions
Post.includes(:user).where("users.created_at > ?", 1.week.ago).references(:users)
```

## Counter Cache

Avoid N+1 for counts:

```ruby
# Without counter cache
<% @posts.each do |post| %>
  <%= post.comments.count %>  # N queries
<% end %>

# With counter cache
class Comment < ApplicationRecord
  belongs_to :post, counter_cache: true
end

# Migration
add_column :posts, :comments_count, :integer, default: 0, null: false

# Now no additional queries
<% @posts.each do |post| %>
  <%= post.comments_count %>  # Reads from column
<% end %>
```

## Detection Tools

### Bullet Gem

```ruby
# Gemfile
gem 'bullet', group: :development

# config/environments/development.rb
config.after_initialize do
  Bullet.enable = true
  Bullet.alert = true
  Bullet.bullet_logger = true
  Bullet.console = true
  Bullet.rails_logger = true
end
```

### Prosopite Gem

```ruby
# Gemfile
gem 'prosopite', group: :development

# config/environments/development.rb
config.after_initialize do
  Prosopite.rails_logger = true
  Prosopite.raise = true  # Raise in tests
end
```

### Manual Detection

```ruby
# Log all queries
ActiveRecord::Base.logger = Logger.new(STDOUT)

# Or check in console
Post.all.each { |p| p.user.name }
# Watch for repeated queries
```

## Common Patterns

### Controller with Eager Loading

```ruby
class PostsController < ApplicationController
  def index
    @posts = Post
      .includes(:user, :tags)
      .published
      .recent
      .page(params[:page])
  end

  def show
    @post = Post
      .includes(comments: :user)
      .find(params[:id])
  end
end
```

### Scope with Eager Loading

```ruby
class Post < ApplicationRecord
  scope :with_details, -> {
    includes(:user, :tags, comments: :user)
  }

  scope :for_feed, -> {
    includes(:user)
      .with_attached_cover_image
      .published
      .recent
  }
end

# Usage
Post.for_feed.page(params[:page])
```

### JSON Serialization

```ruby
class PostsController < ApplicationController
  def index
    @posts = Post.includes(:user, :tags)

    render json: @posts, include: [:user, :tags]
  end
end
```

## Edge Cases

### Polymorphic Associations

```ruby
# Can't easily eager load polymorphic
class Comment < ApplicationRecord
  belongs_to :commentable, polymorphic: true
end

# Solution: Load separately or restructure
Comment.includes(:commentable)  # Works but loads all types

# Better: Scope to specific type
Comment.where(commentable_type: "Post").includes(:commentable)
```

### Optional Associations

```ruby
# Handle nil associations
Post.includes(:user).each do |post|
  # Safe navigation
  post.user&.name
end
```

### Through Associations

```ruby
class User < ApplicationRecord
  has_many :posts
  has_many :comments, through: :posts
end

# Eager load the chain
User.includes(posts: :comments)
```

## Performance Tips

1. **Only load what you need**
   ```ruby
   # Bad: loads everything
   Post.includes(:user, :comments, :tags, :categories)

   # Good: load only what view needs
   Post.includes(:user)  # If only showing author
   ```

2. **Use select for large associations**
   ```ruby
   Post.includes(:comments).select("posts.*, comments.body")
   ```

3. **Consider caching**
   ```ruby
   Rails.cache.fetch("posts_feed", expires_in: 5.minutes) do
     Post.includes(:user).recent.limit(20).to_a
   end
   ```

4. **Use strict_loading (Rails 6.1+)**
   ```ruby
   class Post < ApplicationRecord
     self.strict_loading_by_default = true
   end

   # Raises if accessing non-eager-loaded association
   Post.first.user  # Raises ActiveRecord::StrictLoadingViolationError
   Post.includes(:user).first.user  # Works
   ```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Still N+1 | Missing `includes` | Add appropriate eager loading |
| Too slow | Over-eager loading | Load only needed associations |
| Memory issues | Loading too much | Use `find_each` or pagination |
| Works locally, N+1 in prod | Different data | Test with realistic data |

## Related

- [basics.md](./basics.md): Query fundamentals
- [joins.md](./joins.md): Join queries
- [../activerecord/associations.md](../activerecord/associations.md): Association setup
