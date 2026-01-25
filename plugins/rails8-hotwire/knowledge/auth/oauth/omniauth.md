# OmniAuth Setup

## Overview

Complete guide to setting up OmniAuth for social authentication in Rails 8 applications. Covers gem installation, middleware configuration, callback handling, and CSRF protection.

## When to Use

- When implementing "Sign in with Google/GitHub/etc."
- When offering passwordless social login
- When linking multiple social accounts to one user
- When building multi-tenant applications with SSO

## Quick Start

```ruby
# Gemfile
gem "omniauth"
gem "omniauth-rails_csrf_protection"  # Required for Rails 8
gem "omniauth-google-oauth2"
gem "omniauth-github"
```

```ruby
# config/initializers/omniauth.rb
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :google_oauth2,
    Rails.application.credentials.dig(:google, :client_id),
    Rails.application.credentials.dig(:google, :client_secret)

  provider :github,
    Rails.application.credentials.dig(:github, :client_id),
    Rails.application.credentials.dig(:github, :client_secret)
end
```

## Main Patterns

### Pattern 1: Basic OmniAuth Setup

```ruby
# Gemfile
gem "omniauth", "~> 2.1"
gem "omniauth-rails_csrf_protection", "~> 1.0"

# Provider gems (add as needed)
gem "omniauth-google-oauth2"
gem "omniauth-github"
gem "omniauth-twitter2"
gem "omniauth-facebook"
gem "omniauth-apple"
```

```ruby
# config/initializers/omniauth.rb
OmniAuth.config.logger = Rails.logger
OmniAuth.config.allowed_request_methods = [:post]  # Security: POST only

Rails.application.config.middleware.use OmniAuth::Builder do
  provider :google_oauth2,
    Rails.application.credentials.dig(:google, :client_id),
    Rails.application.credentials.dig(:google, :client_secret),
    {
      scope: "email,profile",
      prompt: "select_account",
      image_aspect_ratio: "square",
      image_size: 200
    }

  provider :github,
    Rails.application.credentials.dig(:github, :client_id),
    Rails.application.credentials.dig(:github, :client_secret),
    {
      scope: "user:email,read:user"
    }
end
```

### Pattern 2: Identity Model for Multiple Providers

```ruby
# Generate migration
# rails g model Identity user:references provider:string uid:string

# db/migrate/xxx_create_identities.rb
class CreateIdentities < ActiveRecord::Migration[8.0]
  def change
    create_table :identities do |t|
      t.references :user, null: false, foreign_key: true
      t.string :provider, null: false
      t.string :uid, null: false
      t.string :token
      t.string :refresh_token
      t.datetime :expires_at

      t.timestamps
    end

    add_index :identities, [:provider, :uid], unique: true
  end
end
```

```ruby
# app/models/identity.rb
class Identity < ApplicationRecord
  belongs_to :user

  validates :provider, :uid, presence: true
  validates :uid, uniqueness: { scope: :provider }

  def self.find_or_create_from_omniauth(auth, user = nil)
    identity = find_or_initialize_by(provider: auth.provider, uid: auth.uid)

    identity.token = auth.credentials&.token
    identity.refresh_token = auth.credentials&.refresh_token
    identity.expires_at = auth.credentials&.expires_at ? Time.at(auth.credentials.expires_at) : nil

    if identity.user.nil?
      identity.user = user || User.find_or_create_from_omniauth(auth)
    end

    identity.save!
    identity
  end
end
```

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_many :identities, dependent: :destroy

  def self.find_or_create_from_omniauth(auth)
    # First try to find by email
    user = find_by(email: auth.info.email)

    if user
      user
    else
      create!(
        email: auth.info.email,
        name: auth.info.name,
        avatar_url: auth.info.image,
        password: SecureRandom.hex(16)
      )
    end
  end

  def linked_providers
    identities.pluck(:provider)
  end

  def linked_to?(provider)
    identities.exists?(provider: provider)
  end
end
```

### Pattern 3: OmniAuth Callbacks Controller

```ruby
# config/routes.rb
Rails.application.routes.draw do
  # Without Devise
  get "/auth/:provider/callback", to: "omniauth_callbacks#callback"
  get "/auth/failure", to: "omniauth_callbacks#failure"

  # With Devise
  devise_for :users, controllers: {
    omniauth_callbacks: 'users/omniauth_callbacks'
  }
end
```

```ruby
# app/controllers/omniauth_callbacks_controller.rb (without Devise)
class OmniauthCallbacksController < ApplicationController
  skip_before_action :authenticate_user!
  skip_before_action :verify_authenticity_token, only: :callback

  def callback
    auth = request.env["omniauth.auth"]

    if current_user
      # Link account to existing user
      link_identity(auth)
    else
      # Sign in or create new user
      sign_in_from_oauth(auth)
    end
  end

  def failure
    redirect_to root_path, alert: "Authentication failed: #{params[:message]}"
  end

  private

  def sign_in_from_oauth(auth)
    identity = Identity.find_or_create_from_omniauth(auth)
    user = identity.user

    if user.persisted?
      session[:user_id] = user.id
      redirect_to root_path, notice: "Signed in with #{auth.provider.titleize}!"
    else
      redirect_to root_path, alert: "Could not sign in."
    end
  end

  def link_identity(auth)
    identity = Identity.find_or_create_from_omniauth(auth, current_user)

    if identity.persisted?
      redirect_to settings_path, notice: "#{auth.provider.titleize} account linked!"
    else
      redirect_to settings_path, alert: "Could not link account."
    end
  end
end
```

### Pattern 4: Devise Integration

```ruby
# app/models/user.rb
class User < ApplicationRecord
  devise :database_authenticatable, :registerable, :recoverable,
         :rememberable, :validatable, :omniauthable,
         omniauth_providers: [:google_oauth2, :github]

  has_many :identities, dependent: :destroy

  def self.from_omniauth(auth)
    identity = Identity.find_by(provider: auth.provider, uid: auth.uid)
    return identity.user if identity

    user = find_or_initialize_by(email: auth.info.email)

    if user.new_record?
      user.name = auth.info.name
      user.password = Devise.friendly_token[0, 20]
      user.skip_confirmation! if user.respond_to?(:skip_confirmation!)
    end

    user.save!

    Identity.create!(
      user: user,
      provider: auth.provider,
      uid: auth.uid,
      token: auth.credentials&.token
    )

    user
  end
end
```

```ruby
# app/controllers/users/omniauth_callbacks_controller.rb
class Users::OmniauthCallbacksController < Devise::OmniauthCallbacksController
  skip_before_action :verify_authenticity_token, only: [:google_oauth2, :github]

  def google_oauth2
    handle_auth("Google")
  end

  def github
    handle_auth("GitHub")
  end

  def failure
    redirect_to root_path, alert: failure_message
  end

  private

  def handle_auth(kind)
    @user = User.from_omniauth(auth_hash)

    if @user.persisted?
      flash[:notice] = "Signed in with #{kind}!"
      sign_in_and_redirect @user, event: :authentication
    else
      session["devise.#{kind.downcase}_data"] = auth_hash.except(:extra)
      redirect_to new_user_registration_url,
                  alert: @user.errors.full_messages.join("\n")
    end
  end

  def auth_hash
    request.env["omniauth.auth"]
  end

  def failure_message
    exception = request.env["omniauth.error"]
    error = exception.respond_to?(:message) ? exception.message : exception.to_s
    I18n.t("devise.omniauth_callbacks.failure", kind: "OAuth", reason: error)
  end
end
```

### Pattern 5: Login Buttons

```erb
<%# app/views/shared/_oauth_buttons.html.erb %>
<div class="oauth-buttons space-y-3">
  <%# IMPORTANT: Must use POST for CSRF protection %>
  <%= button_to user_google_oauth2_omniauth_authorize_path,
      method: :post,
      data: { turbo: false },
      class: "w-full flex items-center justify-center gap-3 px-4 py-2 border rounded-md hover:bg-gray-50" do %>
    <%= image_tag "icons/google.svg", class: "w-5 h-5" %>
    <span>Continue with Google</span>
  <% end %>

  <%= button_to user_github_omniauth_authorize_path,
      method: :post,
      data: { turbo: false },
      class: "w-full flex items-center justify-center gap-3 px-4 py-2 border rounded-md hover:bg-gray-50" do %>
    <%= image_tag "icons/github.svg", class: "w-5 h-5" %>
    <span>Continue with GitHub</span>
  <% end %>
</div>
```

### Pattern 6: Account Linking UI

```erb
<%# app/views/settings/connections.html.erb %>
<div class="space-y-4">
  <h3 class="text-lg font-medium">Connected Accounts</h3>

  <% [:google_oauth2, :github].each do |provider| %>
    <div class="flex items-center justify-between p-4 border rounded-lg">
      <div class="flex items-center gap-3">
        <%= image_tag "icons/#{provider}.svg", class: "w-6 h-6" %>
        <span class="font-medium"><%= provider.to_s.titleize %></span>
      </div>

      <% if current_user.linked_to?(provider) %>
        <% identity = current_user.identities.find_by(provider: provider) %>
        <div class="flex items-center gap-4">
          <span class="text-sm text-green-600">Connected</span>
          <%= button_to "Disconnect",
              identity_path(identity),
              method: :delete,
              data: { turbo_confirm: "Disconnect #{provider.to_s.titleize}?" },
              class: "text-sm text-red-600 hover:underline" %>
        </div>
      <% else %>
        <%= button_to "Connect",
            "/auth/#{provider}",
            method: :post,
            data: { turbo: false },
            class: "px-4 py-2 bg-gray-800 text-white rounded-md" %>
      <% end %>
    </div>
  <% end %>
</div>
```

### Pattern 7: Failure Handling

```ruby
# config/initializers/omniauth.rb
OmniAuth.config.on_failure = Proc.new do |env|
  OmniauthCallbacksController.action(:failure).call(env)
end

# Or with custom error handling
OmniAuth.config.on_failure = Proc.new do |env|
  message = env['omniauth.error.type']
  strategy = env['omniauth.error.strategy']&.name

  Rails.logger.warn("OmniAuth failure: #{strategy} - #{message}")

  new_path = "/auth/failure?message=#{message}&strategy=#{strategy}"
  Rack::Response.new(["302 Moved"], 302, 'Location' => new_path).finish
end
```

### Pattern 8: Storing Credentials Securely

```bash
# Edit credentials
EDITOR="code --wait" rails credentials:edit
```

```yaml
# config/credentials.yml.enc
google:
  client_id: "your-client-id.apps.googleusercontent.com"
  client_secret: "your-client-secret"

github:
  client_id: "your-github-client-id"
  client_secret: "your-github-client-secret"
```

## OmniAuth Auth Hash Structure

```ruby
# request.env["omniauth.auth"]
{
  provider: "google_oauth2",
  uid: "123456789",
  info: {
    name: "John Doe",
    email: "john@example.com",
    image: "https://lh3.googleusercontent.com/...",
    first_name: "John",
    last_name: "Doe"
  },
  credentials: {
    token: "access_token_here",
    refresh_token: "refresh_token_here",
    expires_at: 1234567890,
    expires: true
  },
  extra: {
    raw_info: { ... }  # Provider-specific data
  }
}
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| GET request for auth | CSRF vulnerability | Use POST with `omniauth-rails_csrf_protection` |
| Storing tokens in session | Security risk | Store in encrypted Identity model |
| Trusting provider email | Email may not be verified | Check `email_verified` claim |
| No fallback auth | Users locked out | Always offer email/password option |

## Related Skills

- [google.md](./google.md): Google OAuth specifics
- [github.md](./github.md): GitHub OAuth specifics
- [apple.md](./apple.md): Apple Sign In specifics
- [../devise/controllers.md](../devise/controllers.md): Devise integration

## References

- [OmniAuth GitHub](https://github.com/omniauth/omniauth)
- [OmniAuth Rails CSRF Protection](https://github.com/cookpad/omniauth-rails_csrf_protection)
- [OmniAuth Wiki](https://github.com/omniauth/omniauth/wiki)
