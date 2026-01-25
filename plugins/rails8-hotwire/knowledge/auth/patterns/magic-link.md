# Magic Link Authentication

## Overview

Passwordless authentication using secure, time-limited email links. Users receive a unique token via email that signs them in automatically when clicked.

## When to Use

- When reducing friction in authentication flow
- When users frequently forget passwords
- When building apps for non-technical users
- When implementing passwordless authentication
- When combining with traditional password auth as fallback

## Quick Start

```ruby
# Generate token column
rails g migration AddMagicTokenToUsers magic_token:string magic_token_expires_at:datetime

# User model
class User < ApplicationRecord
  has_secure_token :magic_token

  def generate_magic_link_token!
    regenerate_magic_token
    update!(magic_token_expires_at: 30.minutes.from_now)
  end

  def magic_token_valid?
    magic_token_expires_at&.future?
  end
end
```

## Main Patterns

### Pattern 1: Database Setup

```bash
rails g migration AddMagicLinkToUsers magic_token:string:uniq magic_token_expires_at:datetime
```

```ruby
# db/migrate/xxx_add_magic_link_to_users.rb
class AddMagicLinkToUsers < ActiveRecord::Migration[8.0]
  def change
    add_column :users, :magic_token, :string
    add_column :users, :magic_token_expires_at, :datetime
    add_index :users, :magic_token, unique: true
  end
end
```

### Pattern 2: User Model

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_secure_token :magic_token

  MAGIC_TOKEN_EXPIRY = 30.minutes

  def generate_magic_link_token!
    regenerate_magic_token
    update!(magic_token_expires_at: MAGIC_TOKEN_EXPIRY.from_now)
    magic_token
  end

  def magic_token_valid?
    magic_token.present? && magic_token_expires_at&.future?
  end

  def clear_magic_token!
    update!(magic_token: nil, magic_token_expires_at: nil)
  end

  def self.find_by_valid_magic_token(token)
    return nil if token.blank?

    user = find_by(magic_token: token)
    return nil unless user&.magic_token_valid?

    user
  end
end
```

### Pattern 3: Using Signed GlobalID (Recommended)

```ruby
# app/models/user.rb
class User < ApplicationRecord
  def signed_id_for_magic_link
    signed_id(purpose: :magic_link, expires_in: 30.minutes)
  end

  def self.find_by_magic_link_token(token)
    find_signed(token, purpose: :magic_link)
  rescue ActiveSupport::MessageVerifier::InvalidSignature
    nil
  end
end
```

### Pattern 4: Magic Link Controller

```ruby
# app/controllers/magic_links_controller.rb
class MagicLinksController < ApplicationController
  skip_before_action :authenticate_user!

  # GET /magic_link/new - Request form
  def new
  end

  # POST /magic_link - Send magic link
  def create
    user = User.find_by(email: params[:email]&.downcase&.strip)

    if user
      token = user.signed_id_for_magic_link
      MagicLinkMailer.login_link(user, token).deliver_later

      # Track for rate limiting
      Rails.cache.increment("magic_link:#{user.id}", 1, expires_in: 1.hour)
    end

    # Always show same message (prevent email enumeration)
    redirect_to root_path,
      notice: "If an account exists, you'll receive a login link shortly."
  end

  # GET /magic_link/:token - Verify and sign in
  def show
    user = User.find_by_magic_link_token(params[:token])

    if user
      sign_in(user)
      redirect_to after_sign_in_path_for(user),
        notice: "Welcome back!"
    else
      redirect_to new_magic_link_path,
        alert: "This link has expired or is invalid. Please request a new one."
    end
  end
end
```

### Pattern 5: Alternative with Custom Token

```ruby
# app/controllers/magic_links_controller.rb
class MagicLinksController < ApplicationController
  skip_before_action :authenticate_user!
  before_action :rate_limit_magic_links, only: :create

  def create
    user = User.find_by(email: params[:email]&.downcase)

    if user
      token = user.generate_magic_link_token!
      MagicLinkMailer.login_link(user, token).deliver_later
    end

    redirect_to root_path,
      notice: "Check your email for a sign-in link."
  end

  def show
    user = User.find_by_valid_magic_token(params[:token])

    if user
      user.clear_magic_token!  # One-time use
      sign_in(user)
      redirect_to root_path, notice: "Signed in successfully!"
    else
      redirect_to new_magic_link_path,
        alert: "Invalid or expired link."
    end
  end

  private

  def rate_limit_magic_links
    email = params[:email]&.downcase
    key = "magic_link_rate:#{Digest::SHA256.hexdigest(email.to_s)}"

    if Rails.cache.read(key).to_i >= 5
      redirect_to new_magic_link_path,
        alert: "Too many requests. Please try again later."
    else
      Rails.cache.increment(key, 1, expires_in: 1.hour)
    end
  end
end
```

### Pattern 6: Mailer

```ruby
# app/mailers/magic_link_mailer.rb
class MagicLinkMailer < ApplicationMailer
  def login_link(user, token)
    @user = user
    @url = magic_link_url(token: token)
    @expires_in = "30 minutes"

    mail(
      to: user.email,
      subject: "Your sign-in link for #{Rails.application.config.app_name}"
    )
  end
end
```

```erb
<%# app/views/magic_link_mailer/login_link.html.erb %>
<!DOCTYPE html>
<html>
<head>
  <style>
    .button {
      display: inline-block;
      padding: 12px 24px;
      background-color: #4F46E5;
      color: white;
      text-decoration: none;
      border-radius: 6px;
    }
  </style>
</head>
<body>
  <h1>Sign in to <%= Rails.application.config.app_name %></h1>

  <p>Hi <%= @user.name || @user.email %>,</p>

  <p>Click the button below to sign in. This link expires in <%= @expires_in %>.</p>

  <p>
    <a href="<%= @url %>" class="button">Sign in</a>
  </p>

  <p>Or copy and paste this link:</p>
  <p><%= @url %></p>

  <hr>
  <p style="color: #666; font-size: 12px;">
    If you didn't request this link, you can safely ignore this email.
  </p>
</body>
</html>
```

### Pattern 7: Routes

```ruby
# config/routes.rb
Rails.application.routes.draw do
  # Magic link routes
  resource :magic_link, only: [:new, :create] do
    get ':token', action: :show, as: :verify
  end

  # Or simpler:
  get 'login', to: 'magic_links#new'
  post 'login', to: 'magic_links#create'
  get 'login/:token', to: 'magic_links#show', as: :magic_login
end
```

### Pattern 8: Request Form View

```erb
<%# app/views/magic_links/new.html.erb %>
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Sign in with email
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        We'll send you a magic link to sign in instantly.
      </p>
    </div>

    <%= form_with url: magic_link_path, method: :post, class: "mt-8 space-y-6" do |f| %>
      <div>
        <%= f.label :email, "Email address", class: "sr-only" %>
        <%= f.email_field :email,
            required: true,
            autofocus: true,
            autocomplete: "email",
            placeholder: "Enter your email",
            class: "appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" %>
      </div>

      <div>
        <%= f.submit "Send magic link",
            class: "group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" %>
      </div>
    <% end %>

    <div class="text-center">
      <p class="text-sm text-gray-600">
        Or <%= link_to "sign in with password", new_user_session_path, class: "font-medium text-indigo-600 hover:text-indigo-500" %>
      </p>
    </div>
  </div>
</div>
```

### Pattern 9: With Devise Integration

```ruby
# app/controllers/users/magic_links_controller.rb
class Users::MagicLinksController < ApplicationController
  skip_before_action :authenticate_user!

  def new
  end

  def create
    user = User.find_by(email: params[:email]&.downcase)

    if user
      raw_token, enc_token = Devise.token_generator.generate(User, :magic_token)
      user.update!(
        magic_token: enc_token,
        magic_token_expires_at: 30.minutes.from_now
      )
      MagicLinkMailer.login_link(user, raw_token).deliver_later
    end

    redirect_to new_user_session_path,
      notice: "Check your email for a sign-in link."
  end

  def show
    enc_token = Devise.token_generator.digest(User, :magic_token, params[:token])
    user = User.find_by(magic_token: enc_token)

    if user&.magic_token_valid?
      user.update!(magic_token: nil, magic_token_expires_at: nil)
      sign_in(user)
      redirect_to after_sign_in_path_for(user)
    else
      redirect_to new_user_session_path, alert: "Invalid or expired link."
    end
  end
end
```

## Security Considerations

| Consideration | Implementation |
|---------------|----------------|
| Token expiration | 15-30 minutes maximum |
| One-time use | Clear token after successful sign in |
| Rate limiting | Max 5 requests per hour per email |
| Secure comparison | Use `secure_compare` for token matching |
| HTTPS only | Always use `_url` helpers for links |
| Email enumeration | Same response for existing/non-existing emails |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Long-lived tokens | Security risk | Expire in 15-30 minutes |
| Reusable tokens | Replay attacks | Clear after use |
| Revealing email existence | Enumeration attack | Same message for all |
| Plain text tokens in DB | Token theft | Use hashed tokens or signed IDs |
| No rate limiting | Abuse/spam | Limit requests per email |

## Related Skills

- [../devise/setup.md](../devise/setup.md): Devise integration
- [invitation.md](./invitation.md): Invitation system
- [../../controllers/SKILL.md](../../controllers/SKILL.md): Controller patterns

## References

- [Rails Signed GlobalID](https://guides.rubyonrails.org/active_record_basics.html#globalid)
- [has_secure_token](https://api.rubyonrails.org/classes/ActiveRecord/SecureToken/ClassMethods.html)
- [Devise Passwordless](https://github.com/abevoelker/devise-passwordless)
