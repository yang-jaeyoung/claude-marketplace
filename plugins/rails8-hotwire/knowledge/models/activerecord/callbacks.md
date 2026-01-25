# ActiveRecord Callbacks

## Overview

Callbacks allow you to trigger logic during the life cycle of an object. Use them sparingly and thoughtfully.

## Callback Order

### Creating

1. `before_validation`
2. `after_validation`
3. `before_save`
4. `around_save`
5. `before_create`
6. `around_create`
7. **INSERT**
8. `after_create`
9. `after_save`
10. `after_commit` / `after_rollback`

### Updating

1. `before_validation`
2. `after_validation`
3. `before_save`
4. `around_save`
5. `before_update`
6. `around_update`
7. **UPDATE**
8. `after_update`
9. `after_save`
10. `after_commit` / `after_rollback`

### Destroying

1. `before_destroy`
2. `around_destroy`
3. **DELETE**
4. `after_destroy`
5. `after_commit` / `after_rollback`

## Basic Usage

```ruby
class User < ApplicationRecord
  before_validation :normalize_email
  before_save :encrypt_password, if: :password_changed?
  after_create :send_welcome_email
  after_commit :sync_to_crm, on: :create

  private

  def normalize_email
    self.email = email&.downcase&.strip
  end

  def encrypt_password
    self.password_digest = BCrypt::Password.create(password)
  end

  def send_welcome_email
    UserMailer.welcome(self).deliver_later
  end

  def sync_to_crm
    CrmSyncJob.perform_later(self)
  end
end
```

## Conditional Callbacks

```ruby
class Post < ApplicationRecord
  before_save :generate_slug, if: :title_changed?
  after_save :notify_subscribers, if: :published?
  after_update :clear_cache, unless: :draft?

  # Multiple conditions
  after_create :send_notification, if: [:published?, :featured?]

  # Lambda condition
  before_save :log_changes, if: -> { Rails.env.development? }
end
```

## Callback Classes

```ruby
# app/callbacks/slug_generator.rb
class SlugGenerator
  def self.before_save(record)
    if record.slug.blank? && record.respond_to?(:title)
      record.slug = record.title.parameterize
    end
  end
end

class Post < ApplicationRecord
  before_save SlugGenerator
end
```

### Instance Method Style

```ruby
class AuditLogger
  def initialize(action)
    @action = action
  end

  def after_commit(record)
    AuditLog.create!(
      auditable: record,
      action: @action,
      user: Current.user
    )
  end
end

class Post < ApplicationRecord
  after_commit AuditLogger.new(:create), on: :create
  after_commit AuditLogger.new(:update), on: :update
  after_commit AuditLogger.new(:destroy), on: :destroy
end
```

## Transaction Callbacks

```ruby
class Order < ApplicationRecord
  after_commit :send_confirmation_email, on: :create
  after_commit :process_refund, on: :destroy
  after_rollback :log_failure

  # Runs after ANY successful commit
  after_commit :clear_cache

  private

  def send_confirmation_email
    # Safe: transaction committed, record persisted
    OrderMailer.confirmation(self).deliver_later
  end

  def log_failure
    Rails.logger.error("Order save failed: #{id}")
  end
end
```

### after_create_commit Shorthand

```ruby
class Message < ApplicationRecord
  # Equivalent to: after_commit :broadcast, on: :create
  after_create_commit :broadcast
  after_update_commit :update_broadcast
  after_destroy_commit :remove_broadcast
  after_save_commit :sync_search_index

  private

  def broadcast
    broadcast_append_to conversation
  end
end
```

## Around Callbacks

```ruby
class Post < ApplicationRecord
  around_save :measure_save_time

  private

  def measure_save_time
    start = Time.current
    yield  # Actually performs the save
    duration = Time.current - start
    Rails.logger.info("Post save took #{duration}s")
  end
end
```

## Halting Execution

```ruby
class User < ApplicationRecord
  before_destroy :check_admin

  private

  def check_admin
    if admin?
      errors.add(:base, "Cannot delete admin user")
      throw(:abort)  # Halts the chain
    end
  end
end
```

## Skipping Callbacks

```ruby
# These methods skip callbacks:
user.update_column(:status, "active")
user.update_columns(status: "active", updated_at: Time.current)
User.update_all(status: "inactive")
user.delete  # vs user.destroy
User.delete_all

# Skip specific callbacks
class User < ApplicationRecord
  attr_accessor :skip_welcome_email

  after_create :send_welcome_email, unless: :skip_welcome_email
end

user = User.new(skip_welcome_email: true)
user.save
```

## Callback Concerns

```ruby
# app/models/concerns/sluggable.rb
module Sluggable
  extend ActiveSupport::Concern

  included do
    before_validation :generate_slug, on: :create
  end

  private

  def generate_slug
    self.slug = title.parameterize if respond_to?(:title) && slug.blank?
  end
end

class Post < ApplicationRecord
  include Sluggable
end
```

## Common Patterns

### Timestamp Tracking

```ruby
class Document < ApplicationRecord
  before_save :set_published_at, if: :publishing?

  private

  def publishing?
    status_changed? && status == "published"
  end

  def set_published_at
    self.published_at = Time.current
  end
end
```

### Broadcast Updates

```ruby
class Comment < ApplicationRecord
  belongs_to :post

  after_create_commit -> { broadcast_append_to post }
  after_update_commit -> { broadcast_replace_to post }
  after_destroy_commit -> { broadcast_remove_to post }
end
```

### Counter Updates

```ruby
class Like < ApplicationRecord
  belongs_to :post, counter_cache: true

  # Or manual counter
  after_create :increment_likes_count
  after_destroy :decrement_likes_count

  private

  def increment_likes_count
    post.increment!(:likes_count)
  end

  def decrement_likes_count
    post.decrement!(:likes_count)
  end
end
```

## Anti-Patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| External API calls in `after_save` | Delays transaction, may fail | Use `after_commit` + background job |
| Heavy processing in callbacks | Slow saves | Use background job |
| Modifying other models in `after_create` | Unexpected rollbacks | Use service object |
| Too many callbacks | Hard to debug | Extract to service |
| Callbacks calling callbacks | Infinite loops | Careful design, use guards |

### Bad Example

```ruby
# DON'T DO THIS
class Order < ApplicationRecord
  after_create :charge_card
  after_create :send_email
  after_create :update_inventory
  after_create :notify_warehouse
  after_create :sync_crm
end
```

### Good Example

```ruby
# DO THIS
class Order < ApplicationRecord
  after_create_commit :process_order

  private

  def process_order
    ProcessOrderJob.perform_later(id)
  end
end

class ProcessOrderJob < ApplicationJob
  def perform(order_id)
    order = Order.find(order_id)
    OrderProcessor.new(order).process
  end
end
```

## Debugging Callbacks

```ruby
class Post < ApplicationRecord
  before_save { puts "before_save triggered" }
  after_save { puts "after_save triggered" }

  # Or use logging
  before_save { Rails.logger.debug "Saving post #{id}" }
end
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Email sent but record not saved | Using `after_save` not `after_commit` | Use `after_commit` |
| Callback runs twice | Nested saves | Add guard condition |
| Record not found | Using ID before commit | Use `after_commit` |
| Slow tests | Callbacks running | Use `skip_callback` in tests |

## Related

- [validations.md](./validations.md): Validation callbacks
- [associations.md](./associations.md): Association callbacks
- [../../background/](../../background/): Background jobs
