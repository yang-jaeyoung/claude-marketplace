# ActiveRecord Enums

## Overview

Enums map symbolic values to integers in the database, providing readable code while storing efficient integers.

## Basic Usage (Rails 8)

```ruby
class Post < ApplicationRecord
  # Rails 8 syntax (recommended)
  enum :status, { draft: 0, published: 1, archived: 2 }
end

# Generated methods
post.draft?      # Check status
post.published?
post.draft!      # Set status
post.published!
Post.draft       # Scope
Post.published
```

## Array vs Hash Syntax

```ruby
class Post < ApplicationRecord
  # Array (implicit values: 0, 1, 2)
  # AVOID - fragile if order changes
  enum :status, [:draft, :published, :archived]

  # Hash (explicit values) - PREFERRED
  enum :status, { draft: 0, published: 1, archived: 2 }
end
```

## Enum Options

```ruby
class Post < ApplicationRecord
  enum :status, { draft: 0, published: 1, archived: 2 },
    prefix: true,           # post.status_draft?
    suffix: true,           # post.draft_status?
    default: :draft,        # Default value (Rails 7+)
    validate: true          # Add inclusion validation (Rails 7.1+)

  # Custom prefix
  enum :visibility, { public: 0, private: 1, unlisted: 2 },
    prefix: :is             # post.is_public?
end
```

## Multiple Enums

```ruby
class Post < ApplicationRecord
  enum :status, { draft: 0, published: 1, archived: 2 }
  enum :visibility, { public: 0, private: 1, unlisted: 2 }

  # With prefix to avoid method collision
  enum :status, { draft: 0, published: 1 }, prefix: true
  enum :visibility, { draft: 0, final: 1 }, prefix: true

  post.status_draft?
  post.visibility_draft?
end
```

## Querying Enums

```ruby
# Auto-generated scopes
Post.draft
Post.published
Post.archived

# Chaining
Post.published.recent

# Where clause
Post.where(status: :published)
Post.where(status: [:draft, :published])
Post.where.not(status: :archived)

# Getting integer value
Post.statuses[:published]  # => 1

# Getting all statuses
Post.statuses  # => { "draft" => 0, "published" => 1, "archived" => 2 }
```

## Validations

```ruby
class Post < ApplicationRecord
  # Rails 7.1+ automatic validation
  enum :status, { draft: 0, published: 1 }, validate: true

  # Or manual validation
  validates :status, inclusion: { in: statuses.keys }
end
```

## Default Values

```ruby
class Post < ApplicationRecord
  # Option 1: In enum definition (Rails 7+)
  enum :status, { draft: 0, published: 1 }, default: :draft

  # Option 2: In migration
  # add_column :posts, :status, :integer, default: 0, null: false

  # Option 3: Callback
  after_initialize :set_default_status, if: :new_record?

  private

  def set_default_status
    self.status ||= :draft
  end
end
```

## Migration

```ruby
class AddStatusToPosts < ActiveRecord::Migration[8.0]
  def change
    add_column :posts, :status, :integer, default: 0, null: false
    add_index :posts, :status
  end
end
```

## String-Based Enums

```ruby
# If you need string storage (less efficient but more readable in DB)
class Post < ApplicationRecord
  enum :status, { draft: "draft", published: "published", archived: "archived" }
end

# Migration
add_column :posts, :status, :string, default: "draft", null: false
```

## Form Integration

```erb
<%= form_with model: @post do |f| %>
  <%= f.select :status, Post.statuses.keys.map { |s| [s.humanize, s] } %>

  <!-- Or with human-readable labels -->
  <%= f.select :status, Post.statuses.keys.map { |s| [I18n.t("post.status.#{s}"), s] } %>

  <!-- Radio buttons -->
  <% Post.statuses.each_key do |status| %>
    <label>
      <%= f.radio_button :status, status %>
      <%= status.humanize %>
    </label>
  <% end %>
<% end %>
```

## I18n Support

```yaml
# config/locales/en.yml
en:
  activerecord:
    attributes:
      post:
        statuses:
          draft: "Draft"
          published: "Published"
          archived: "Archived"
```

```ruby
# Helper
class Post < ApplicationRecord
  enum :status, { draft: 0, published: 1, archived: 2 }

  def status_label
    I18n.t("activerecord.attributes.post.statuses.#{status}")
  end
end
```

## State Transitions

```ruby
class Post < ApplicationRecord
  enum :status, { draft: 0, published: 1, archived: 2 }

  def publish!
    raise "Cannot publish archived post" if archived?
    published!
  end

  def archive!
    raise "Cannot archive draft" if draft?
    archived!
  end
end

# Or use a state machine gem like AASM
class Post < ApplicationRecord
  include AASM

  aasm column: :status do
    state :draft, initial: true
    state :published
    state :archived

    event :publish do
      transitions from: :draft, to: :published
    end

    event :archive do
      transitions from: :published, to: :archived
    end
  end
end
```

## Bitfield/Flags Pattern

```ruby
# For multiple boolean flags, consider a bitmask
class User < ApplicationRecord
  FLAGS = {
    email_notifications: 1,
    push_notifications: 2,
    sms_notifications: 4,
    newsletter: 8
  }

  def flag_enabled?(flag)
    (flags & FLAGS[flag]) != 0
  end

  def enable_flag(flag)
    update(flags: flags | FLAGS[flag])
  end

  def disable_flag(flag)
    update(flags: flags & ~FLAGS[flag])
  end
end

# Or use the `flag_shih_tzu` gem
```

## Common Patterns

### Scopes with Enums

```ruby
class Order < ApplicationRecord
  enum :status, { pending: 0, processing: 1, shipped: 2, delivered: 3, cancelled: 4 }

  scope :active, -> { where(status: [:pending, :processing, :shipped]) }
  scope :completed, -> { where(status: [:delivered, :cancelled]) }
  scope :in_progress, -> { where(status: [:processing, :shipped]) }
end
```

### Enum with Concern

```ruby
# app/models/concerns/publishable.rb
module Publishable
  extend ActiveSupport::Concern

  included do
    enum :status, { draft: 0, published: 1, archived: 2 }

    scope :visible, -> { published }
  end

  def publish!
    update!(status: :published, published_at: Time.current)
  end
end

class Post < ApplicationRecord
  include Publishable
end

class Page < ApplicationRecord
  include Publishable
end
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| ArgumentError | Invalid enum value | Use validation or rescue |
| Method collision | Same method name | Use prefix/suffix |
| Migration fails | Missing default | Add default value |
| Form shows integers | Using raw value | Use `.keys` for select |

### Handling Invalid Values

```ruby
class Post < ApplicationRecord
  enum :status, { draft: 0, published: 1 }, validate: true

  # Or with error handling
  def status=(value)
    super
  rescue ArgumentError
    # Handle invalid value
    self[:status] = :draft
  end
end
```

## Related

- [validations.md](./validations.md): Enum validations
- [scopes.md](./scopes.md): Enum scopes
- [migrations.md](./migrations.md): Database setup
