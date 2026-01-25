# Devise Setup

## Overview

Complete installation and setup guide for Devise authentication in Rails 8 applications. Covers gem installation, generator commands, User model generation, and initial configuration.

## When to Use

- When building user authentication with email/password
- When needing full-featured authentication (confirmation, lockout, etc.)
- When Rails 8 built-in authentication is insufficient
- When integrating with OmniAuth for social login

## Quick Start

### Installation

```bash
# Add to Gemfile
bundle add devise

# Run installer
rails generate devise:install
```

### Post-Installation Checklist

The installer will display required steps:

```ruby
# 1. config/environments/development.rb
config.action_mailer.default_url_options = { host: 'localhost', port: 3000 }

# 2. config/routes.rb - ensure root route exists
root to: "home#index"

# 3. app/views/layouts/application.html.erb - add flash messages
<p class="notice"><%= notice %></p>
<p class="alert"><%= alert %></p>
```

### Generate User Model

```bash
# Basic user model
rails generate devise User

# With additional fields
rails generate devise User name:string avatar:string

# Run migrations
rails db:migrate
```

## Main Patterns

### Pattern 1: Standard Installation

```ruby
# Gemfile
gem "devise", "~> 4.9"

# After bundle install:
# config/initializers/devise.rb is created
# config/locales/devise.en.yml is created
```

```bash
rails generate devise:install
rails generate devise User
rails db:migrate
```

### Pattern 2: User Model with Common Fields

```bash
rails generate devise User \
  name:string \
  role:integer \
  avatar:string \
  phone:string
```

```ruby
# Generated migration (add defaults/indexes as needed)
class DeviseCreateUsers < ActiveRecord::Migration[8.0]
  def change
    create_table :users do |t|
      ## Database authenticatable
      t.string :email,              null: false, default: ""
      t.string :encrypted_password, null: false, default: ""

      ## Recoverable
      t.string   :reset_password_token
      t.datetime :reset_password_sent_at

      ## Rememberable
      t.datetime :remember_created_at

      ## Custom fields
      t.string :name
      t.integer :role, default: 0
      t.string :avatar
      t.string :phone

      t.timestamps null: false
    end

    add_index :users, :email,                unique: true
    add_index :users, :reset_password_token, unique: true
  end
end
```

### Pattern 3: Multiple Devise Models

```bash
# Generate admin model
rails generate devise Admin

# Generate different user type
rails generate devise Vendor
```

```ruby
# config/routes.rb
Rails.application.routes.draw do
  devise_for :users
  devise_for :admins, path: 'admin'
  devise_for :vendors, path: 'vendor'
end
```

### Pattern 4: User Model with Devise Modules

```ruby
# app/models/user.rb
class User < ApplicationRecord
  # Standard modules (included by default)
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable

  # Optional modules (add as needed)
  # devise :confirmable      # Email confirmation
  # devise :lockable         # Lock after failed attempts
  # devise :timeoutable      # Session timeout
  # devise :trackable        # Track sign in count, timestamps, IPs
  # devise :omniauthable     # OmniAuth support

  # Validations
  validates :name, presence: true, length: { maximum: 100 }

  # Role enum
  enum :role, { user: 0, moderator: 1, admin: 2 }
end
```

### Pattern 5: Adding Modules to Existing User

```bash
# Generate migration for confirmable
rails generate migration AddConfirmableToUsers \
  confirmation_token:string:uniq \
  confirmed_at:datetime \
  confirmation_sent_at:datetime \
  unconfirmed_email:string
```

```ruby
# Migration
class AddConfirmableToUsers < ActiveRecord::Migration[8.0]
  def change
    add_column :users, :confirmation_token, :string
    add_column :users, :confirmed_at, :datetime
    add_column :users, :confirmation_sent_at, :datetime
    add_column :users, :unconfirmed_email, :string

    add_index :users, :confirmation_token, unique: true

    # Confirm existing users
    User.update_all(confirmed_at: Time.current)
  end
end
```

```ruby
# Update user model
class User < ApplicationRecord
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable,
         :confirmable  # Add this
end
```

## Generated Files

| File | Purpose |
|------|---------|
| `config/initializers/devise.rb` | Main configuration |
| `config/locales/devise.en.yml` | I18n translations |
| `app/models/user.rb` | User model with Devise modules |
| `db/migrate/*_devise_create_users.rb` | Database migration |

## Authentication Helpers

After setup, these helpers are available:

```ruby
# In controllers
authenticate_user!          # Require login
current_user                 # Current logged-in user
user_signed_in?             # Check if logged in
user_session                # Access session hash

# Routes
new_user_session_path       # Login form
destroy_user_session_path   # Logout
new_user_registration_path  # Sign up form
edit_user_registration_path # Edit profile
new_user_password_path      # Password reset
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Skipping mailer config | Password reset/confirmation fails | Set `default_url_options` |
| No root route | Devise redirects fail | Define `root to:` in routes |
| Forgetting `db:migrate` | Authentication won't work | Always run migrations |
| Editing generated migration incorrectly | Data loss on rollback | Review migration carefully |

## Related Skills

- [configuration.md](./configuration.md): Devise configuration options
- [turbo.md](./turbo.md): Rails 8 + Turbo compatibility
- [views.md](./views.md): Customizing authentication views

## References

- [Devise GitHub](https://github.com/heartcombo/devise)
- [Devise Wiki - Getting Started](https://github.com/heartcombo/devise/wiki)
