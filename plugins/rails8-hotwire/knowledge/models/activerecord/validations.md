# ActiveRecord Validations

## Overview

Validations ensure that only valid data is saved into your database. They are defined in your model and run before `save`, `create`, and `update`.

## Basic Validations

```ruby
class User < ApplicationRecord
  # Presence
  validates :name, presence: true

  # Uniqueness
  validates :email, uniqueness: true
  validates :email, uniqueness: { case_sensitive: false }
  validates :slug, uniqueness: { scope: :account_id }

  # Length
  validates :bio, length: { minimum: 10 }
  validates :password, length: { in: 8..72 }
  validates :username, length: { maximum: 30 }

  # Format
  validates :email, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :phone, format: { with: /\A\d{3}-\d{4}-\d{4}\z/ }

  # Numericality
  validates :age, numericality: { only_integer: true, greater_than: 0 }
  validates :price, numericality: { greater_than_or_equal_to: 0 }

  # Inclusion/Exclusion
  validates :role, inclusion: { in: %w[admin moderator user] }
  validates :subdomain, exclusion: { in: %w[www admin api] }

  # Acceptance
  validates :terms, acceptance: true

  # Confirmation
  validates :email, confirmation: true
end
```

## Validation Options

```ruby
class Post < ApplicationRecord
  # Custom message
  validates :title, presence: { message: "can't be empty" }

  # Conditional validation
  validates :body, presence: true, if: :published?
  validates :summary, presence: true, unless: :draft?

  # Multiple conditions
  validates :content, presence: true, if: [:published?, :featured?]

  # Lambda condition
  validates :author_name, presence: true, if: -> { author.nil? }

  # Allow blank/nil
  validates :website, format: { with: URI::DEFAULT_PARSER.make_regexp }, allow_blank: true

  # On specific context
  validates :password, presence: true, on: :create
  validates :reason, presence: true, on: :archive
end

# Using context
@post.valid?(:archive)
@post.save(context: :archive)
```

## Custom Validations

### Custom Method

```ruby
class Post < ApplicationRecord
  validate :title_is_not_clickbait

  private

  def title_is_not_clickbait
    clickbait_words = %w[amazing incredible unbelievable]

    if title.present? && clickbait_words.any? { |word| title.downcase.include?(word) }
      errors.add(:title, "sounds like clickbait")
    end
  end
end
```

### Custom Validator Class

```ruby
# app/validators/email_validator.rb
class EmailValidator < ActiveModel::EachValidator
  def validate_each(record, attribute, value)
    return if value.blank?

    unless value =~ URI::MailTo::EMAIL_REGEXP
      record.errors.add(attribute, options[:message] || "is not a valid email")
    end

    if options[:disposable] == false && disposable_email?(value)
      record.errors.add(attribute, "cannot be a disposable email")
    end
  end

  private

  def disposable_email?(email)
    domain = email.split("@").last
    DisposableDomain.exists?(name: domain)
  end
end

# Usage
class User < ApplicationRecord
  validates :email, email: { disposable: false }
end
```

### Model Validator

```ruby
# app/validators/consistent_dates_validator.rb
class ConsistentDatesValidator < ActiveModel::Validator
  def validate(record)
    if record.start_date && record.end_date
      if record.end_date < record.start_date
        record.errors.add(:end_date, "must be after start date")
      end
    end
  end
end

# Usage
class Event < ApplicationRecord
  validates_with ConsistentDatesValidator
end
```

## Working with Errors

```ruby
user = User.new
user.valid?                      # => false
user.errors.full_messages        # => ["Name can't be blank", "Email is invalid"]
user.errors[:name]               # => ["can't be blank"]
user.errors.add(:base, "Custom error message")
user.errors.where(:name)         # => [#<ActiveModel::Error attribute=name...>]
user.errors.of_kind?(:name, :blank)  # => true
```

### Display in Views

```erb
<% if @user.errors.any? %>
  <div class="errors">
    <h2><%= pluralize(@user.errors.count, "error") %> prohibited saving:</h2>
    <ul>
      <% @user.errors.full_messages.each do |message| %>
        <li><%= message %></li>
      <% end %>
    </ul>
  </div>
<% end %>

<!-- Field-level errors -->
<%= form_with model: @user do |f| %>
  <div class="field">
    <%= f.label :email %>
    <%= f.email_field :email, class: @user.errors[:email].any? ? "error" : "" %>
    <% if @user.errors[:email].any? %>
      <span class="error-message"><%= @user.errors[:email].first %></span>
    <% end %>
  </div>
<% end %>
```

## Strict Validations

```ruby
class Account < ApplicationRecord
  validates :subdomain, presence: true, strict: true
end

# Raises ActiveModel::StrictValidationFailed instead of returning false
Account.new.valid?  # raises exception
```

## Skip Validations

```ruby
# Skip all validations
user.save(validate: false)

# Update specific column without validation
user.update_column(:updated_at, Time.current)
user.update_columns(status: 1, updated_at: Time.current)

# Increment/decrement
user.increment!(:login_count)
```

## Association Validations

```ruby
class Post < ApplicationRecord
  belongs_to :user
  has_many :comments

  # Validate associated records
  validates_associated :comments

  # Require association
  validates :user, presence: true  # or use `optional: false` on belongs_to
end
```

## Nested Attributes Validation

```ruby
class Post < ApplicationRecord
  has_many :comments
  accepts_nested_attributes_for :comments, reject_if: :all_blank

  # Comments are validated when post is saved
end
```

## Database Constraints

Always back up validations with database constraints:

```ruby
# Migration
class CreateUsers < ActiveRecord::Migration[8.0]
  def change
    create_table :users do |t|
      t.string :email, null: false
      t.string :username, null: false
      t.timestamps
    end

    add_index :users, :email, unique: true
    add_index :users, :username, unique: true
  end
end
```

## Common Patterns

### Password Validation

```ruby
class User < ApplicationRecord
  has_secure_password

  validates :password, length: { minimum: 8 }, if: -> { new_record? || password.present? }

  validate :password_complexity, if: -> { password.present? }

  private

  def password_complexity
    return if password.match?(/\A(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    errors.add(:password, "must include uppercase, lowercase, and a number")
  end
end
```

### Slug Validation

```ruby
class Post < ApplicationRecord
  validates :slug, presence: true,
                   uniqueness: true,
                   format: { with: /\A[a-z0-9-]+\z/, message: "only allows lowercase letters, numbers, and hyphens" }

  before_validation :generate_slug, on: :create

  private

  def generate_slug
    self.slug ||= title&.parameterize
  end
end
```

### Conditional Required Fields

```ruby
class Order < ApplicationRecord
  validates :shipping_address, presence: true, if: :requires_shipping?
  validates :email, presence: true, unless: :guest_checkout?

  def requires_shipping?
    !digital_only?
  end
end
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Uniqueness race condition | No DB constraint | Add unique index |
| Validation not running | Using `update_column` | Use `update` instead |
| Password re-validation | Validating on every save | Add condition |
| Associated record invalid | Missing `validates_associated` | Add validation or check manually |

## Related

- [migrations.md](./migrations.md): Database constraints
- [associations.md](./associations.md): Association validations
- [callbacks.md](./callbacks.md): Validation callbacks
