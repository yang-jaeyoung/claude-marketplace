# Devise Configuration

## Overview

Comprehensive guide to configuring Devise through `config/initializers/devise.rb`. Covers all modules, security settings, and Rails 8 specific options.

## When to Use

- When customizing authentication behavior
- When enabling/disabling Devise modules
- When configuring security settings (password requirements, lockout)
- When setting up mailer and session options

## Quick Start

```ruby
# config/initializers/devise.rb
Devise.setup do |config|
  # Required for Rails 8 + Turbo
  config.responder.error_status = :unprocessable_entity
  config.responder.redirect_status = :see_other

  # Mailer
  config.mailer_sender = 'noreply@example.com'

  # Password settings
  config.password_length = 8..128
  config.email_regexp = /\A[^@\s]+@[^@\s]+\z/
end
```

## Main Patterns

### Pattern 1: Essential Configuration

```ruby
Devise.setup do |config|
  # ==> Mailer Configuration
  config.mailer_sender = 'noreply@yourapp.com'
  # config.mailer = 'Devise::Mailer'

  # ==> ORM configuration
  require 'devise/orm/active_record'

  # ==> Rails 8 + Turbo Compatibility (REQUIRED)
  config.responder.error_status = :unprocessable_entity
  config.responder.redirect_status = :see_other

  # ==> Authentication keys
  config.authentication_keys = [:email]
  # config.authentication_keys = [:username]  # Login with username

  # ==> Case insensitivity
  config.case_insensitive_keys = [:email]
  config.strip_whitespace_keys = [:email]

  # ==> Paranoid mode (don't reveal if email exists)
  config.paranoid = true

  # ==> Skip session storage for specific strategies
  # config.skip_session_storage = [:http_auth]

  # ==> Stretches (bcrypt iterations)
  config.stretches = Rails.env.test? ? 1 : 12
end
```

### Pattern 2: Password Configuration

```ruby
Devise.setup do |config|
  # Password length requirement
  config.password_length = 8..128

  # Email format validation
  config.email_regexp = /\A[^@\s]+@[^@\s]+\z/

  # Reset password within (token expiration)
  config.reset_password_within = 6.hours

  # Expire password after time period (requires :expirable module)
  # config.expire_password_after = 90.days
end
```

### Pattern 3: Session Configuration

```ruby
Devise.setup do |config|
  # ==> Remember me
  config.remember_for = 2.weeks
  config.extend_remember_period = false
  config.rememberable_options = { secure: true }

  # ==> Timeout (requires :timeoutable module)
  config.timeout_in = 30.minutes

  # ==> Expire sessions on browser close
  config.expire_all_remember_me_on_sign_out = true
end
```

### Pattern 4: Lockable Configuration

```ruby
Devise.setup do |config|
  # ==> Lockable (requires :lockable module in User model)

  # Lock strategy: :failed_attempts or :none
  config.lock_strategy = :failed_attempts

  # Unlock strategy: :time, :email, :both, :none
  config.unlock_strategy = :both

  # Number of attempts before lock
  config.maximum_attempts = 5

  # Time to unlock after lock (if :time strategy)
  config.unlock_in = 1.hour

  # Keys used for locking
  config.unlock_keys = [:email]

  # Warn on last attempt before lock
  config.last_attempt_warning = true
end
```

### Pattern 5: Confirmable Configuration

```ruby
Devise.setup do |config|
  # ==> Confirmable (requires :confirmable module in User model)

  # Allow login before confirmation for X days
  config.allow_unconfirmed_access_for = 2.days

  # Confirmation token expiration
  config.confirm_within = 3.days

  # Reconfirmable: require confirmation on email change
  config.reconfirmable = true

  # Keys used for confirmation
  config.confirmation_keys = [:email]
end
```

### Pattern 6: Trackable Configuration

```ruby
# Requires :trackable module in User model
# Add these columns to users table:
# - sign_in_count:integer
# - current_sign_in_at:datetime
# - last_sign_in_at:datetime
# - current_sign_in_ip:string
# - last_sign_in_ip:string

class User < ApplicationRecord
  devise :database_authenticatable, :trackable
  # ... other modules
end
```

### Pattern 7: Scoped Views

```ruby
Devise.setup do |config|
  # Enable scoped views for multiple Devise models
  config.scoped_views = true
  # Views will be in:
  # app/views/users/sessions/
  # app/views/admins/sessions/
end
```

### Pattern 8: Navigation Configuration

```ruby
Devise.setup do |config|
  # Sign out via DELETE (default) or GET
  config.sign_out_via = :delete
  # config.sign_out_via = :get  # Less secure, but simpler

  # Root path after sign in (can also override in ApplicationController)
  # config.root = :dashboard_path

  # Where to redirect after sign out
  # Override in ApplicationController with after_sign_out_path_for
end
```

## Devise Modules Reference

| Module | Purpose | Required Columns |
|--------|---------|-----------------|
| `database_authenticatable` | Email/password login | `email`, `encrypted_password` |
| `registerable` | User registration | None |
| `recoverable` | Password reset | `reset_password_token`, `reset_password_sent_at` |
| `rememberable` | Remember me cookie | `remember_created_at` |
| `validatable` | Email/password validation | None |
| `confirmable` | Email confirmation | `confirmation_token`, `confirmed_at`, `confirmation_sent_at`, `unconfirmed_email` |
| `lockable` | Lock after failed attempts | `failed_attempts`, `unlock_token`, `locked_at` |
| `timeoutable` | Session timeout | None |
| `trackable` | Sign in tracking | `sign_in_count`, `current_sign_in_at`, `last_sign_in_at`, `current_sign_in_ip`, `last_sign_in_ip` |
| `omniauthable` | OmniAuth integration | None (use Identity model) |

## Environment-Specific Settings

```ruby
# config/environments/development.rb
config.action_mailer.default_url_options = { host: 'localhost', port: 3000 }
config.action_mailer.delivery_method = :letter_opener

# config/environments/production.rb
config.action_mailer.default_url_options = { host: 'yourapp.com', protocol: 'https' }
config.action_mailer.delivery_method = :smtp
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Low password length | Security vulnerability | Minimum 8 characters |
| High stretches in test | Slow tests | Use `stretches = 1` in test |
| Missing paranoid mode | Email enumeration attack | Enable `config.paranoid = true` |
| GET sign out | CSRF vulnerability | Use `sign_out_via = :delete` |
| Skipping Turbo config | Forms break with Rails 8 | Set error/redirect status |

## Related Skills

- [setup.md](./setup.md): Installation guide
- [turbo.md](./turbo.md): Turbo compatibility details
- [testing.md](./testing.md): Testing authentication

## References

- [Devise Configuration Options](https://github.com/heartcombo/devise#configuring-models)
- [Devise Initializer Comments](https://github.com/heartcombo/devise/blob/main/lib/generators/templates/devise.rb)
