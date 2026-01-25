# ActiveRecord Associations

## Overview

Associations define relationships between models. Rails supports six types of associations that cover all common database relationships.

## Association Types

| Type | Relationship | Foreign Key Location |
|------|--------------|---------------------|
| `belongs_to` | Many-to-one | This model |
| `has_one` | One-to-one | Other model |
| `has_many` | One-to-many | Other model |
| `has_many :through` | Many-to-many (with join model) | Join model |
| `has_one :through` | One-to-one (through another) | Through model |
| `has_and_belongs_to_many` | Many-to-many (no join model) | Join table |

## belongs_to

```ruby
class Post < ApplicationRecord
  belongs_to :user
  belongs_to :category, optional: true  # nullable
  belongs_to :author, class_name: "User", foreign_key: "author_id"
end
```

### Options

```ruby
belongs_to :user,
  class_name: "Account",       # Custom class name
  foreign_key: "account_id",   # Custom foreign key
  primary_key: "uuid",         # Custom primary key
  optional: true,              # Allow nil (Rails 5+ requires by default)
  touch: true,                 # Update parent's updated_at
  counter_cache: true,         # Cache count on parent
  inverse_of: :posts           # Bidirectional association
```

## has_one

```ruby
class User < ApplicationRecord
  has_one :profile, dependent: :destroy
  has_one :avatar, as: :attachable  # polymorphic
end

class Profile < ApplicationRecord
  belongs_to :user
end
```

## has_many

```ruby
class User < ApplicationRecord
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :nullify
  has_many :published_posts, -> { where(published: true) }, class_name: "Post"
end
```

### Dependent Options

| Option | Behavior |
|--------|----------|
| `:destroy` | Call destroy on each associated record |
| `:delete_all` | Delete directly from database (skip callbacks) |
| `:nullify` | Set foreign key to NULL |
| `:restrict_with_error` | Add error if records exist |
| `:restrict_with_exception` | Raise exception if records exist |

## has_many :through

```ruby
# Many-to-many through join model
class User < ApplicationRecord
  has_many :memberships
  has_many :teams, through: :memberships
end

class Membership < ApplicationRecord
  belongs_to :user
  belongs_to :team
  # Additional attributes: role, joined_at, etc.
end

class Team < ApplicationRecord
  has_many :memberships
  has_many :users, through: :memberships
end
```

### With Conditions

```ruby
class User < ApplicationRecord
  has_many :memberships
  has_many :teams, through: :memberships
  has_many :admin_teams, -> { where(memberships: { role: "admin" }) },
           through: :memberships, source: :team
end
```

## has_one :through

```ruby
class User < ApplicationRecord
  has_one :membership
  has_one :team, through: :membership
end
```

## has_and_belongs_to_many

```ruby
# Simpler but less flexible than has_many :through
class Post < ApplicationRecord
  has_and_belongs_to_many :tags
end

class Tag < ApplicationRecord
  has_and_belongs_to_many :posts
end

# Migration for join table
class CreatePostsTags < ActiveRecord::Migration[8.0]
  def change
    create_join_table :posts, :tags do |t|
      t.index [:post_id, :tag_id], unique: true
    end
  end
end
```

## Polymorphic Associations

```ruby
class Comment < ApplicationRecord
  belongs_to :commentable, polymorphic: true
end

class Post < ApplicationRecord
  has_many :comments, as: :commentable
end

class Photo < ApplicationRecord
  has_many :comments, as: :commentable
end
```

### Migration

```ruby
class CreateComments < ActiveRecord::Migration[8.0]
  def change
    create_table :comments do |t|
      t.text :body
      t.references :commentable, polymorphic: true, null: false
      t.timestamps
    end
  end
end
```

## Self-Referential Associations

```ruby
# Tree structure
class Category < ApplicationRecord
  belongs_to :parent, class_name: "Category", optional: true
  has_many :children, class_name: "Category", foreign_key: "parent_id"
end

# Following/Followers
class User < ApplicationRecord
  has_many :followings, class_name: "Follow", foreign_key: "follower_id"
  has_many :followed_users, through: :followings, source: :followed

  has_many :followers_rel, class_name: "Follow", foreign_key: "followed_id"
  has_many :followers, through: :followers_rel, source: :follower
end

class Follow < ApplicationRecord
  belongs_to :follower, class_name: "User"
  belongs_to :followed, class_name: "User"
end
```

## Scoped Associations

```ruby
class User < ApplicationRecord
  has_many :posts
  has_many :published_posts, -> { where(published: true) }, class_name: "Post"
  has_many :recent_posts, -> { order(created_at: :desc).limit(5) }, class_name: "Post"
  has_many :draft_posts, -> { draft }, class_name: "Post"  # Using scope from Post
end
```

## Association Extensions

```ruby
class User < ApplicationRecord
  has_many :posts do
    def published
      where(published: true)
    end

    def by_month(month)
      where("EXTRACT(MONTH FROM created_at) = ?", month)
    end
  end
end

# Usage
user.posts.published
user.posts.by_month(6)
```

## Inverse Associations

```ruby
class User < ApplicationRecord
  has_many :posts, inverse_of: :user
end

class Post < ApplicationRecord
  belongs_to :user, inverse_of: :posts
end

# Benefits: Memory efficiency, consistency
user = User.first
post = user.posts.first
post.user.equal?(user)  # true - same object in memory
```

## Eager Loading

```ruby
# Avoid N+1 queries
class PostsController < ApplicationController
  def index
    # Bad: N+1
    @posts = Post.all

    # Good: Eager load
    @posts = Post.includes(:user, :comments)

    # Nested eager load
    @posts = Post.includes(comments: :user)

    # Preload (separate queries)
    @posts = Post.preload(:user)

    # Eager load (single JOIN query)
    @posts = Post.eager_load(:user)
  end
end
```

## Association Callbacks

```ruby
class User < ApplicationRecord
  has_many :posts,
    before_add: :check_post_limit,
    after_add: :notify_followers,
    before_remove: :archive_post,
    after_remove: :update_stats

  private

  def check_post_limit(post)
    raise "Post limit reached" if posts.count >= 100
  end

  def notify_followers(post)
    NotifyFollowersJob.perform_later(self, post)
  end
end
```

## Common Patterns

### Counter Cache

```ruby
class Post < ApplicationRecord
  belongs_to :user, counter_cache: true
  # or: counter_cache: :posts_count
end

# Migration
add_column :users, :posts_count, :integer, default: 0, null: false

# Reset counter
User.reset_counters(user.id, :posts)
```

### Touch Parent

```ruby
class Comment < ApplicationRecord
  belongs_to :post, touch: true
end

# Updates post.updated_at when comment changes
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| N+1 queries | Missing eager load | Use `includes` |
| Memory issues | Loading too many records | Use `find_each` or pagination |
| Orphaned records | Missing dependent | Add `dependent: :destroy` |
| Validation errors | Missing `inverse_of` | Add inverse associations |

## Related

- [validations.md](./validations.md): Association validations
- [callbacks.md](./callbacks.md): Association callbacks
- [../queries/n-plus-one.md](../queries/n-plus-one.md): N+1 resolution
