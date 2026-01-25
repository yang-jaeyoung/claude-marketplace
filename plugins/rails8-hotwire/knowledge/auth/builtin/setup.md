# Rails 8 Built-in Authentication Setup

## Prerequisites

- Rails 8.0 or later
- PostgreSQL, MySQL, or SQLite database
- ActionMailer configured for password reset emails

## Generation

### Basic Setup

```bash
# Generate authentication
bin/rails generate authentication

# Review generated files
git status

# Run migrations
bin/rails db:migrate
```

### Generated Migration: Users

```ruby
# db/migrate/XXXXXX_create_users.rb
class CreateUsers < ActiveRecord::Migration[8.0]
  def change
    create_table :users do |t|
      t.string :email_address, null: false
      t.string :password_digest, null: false

      t.timestamps
    end
    add_index :users, :email_address, unique: true
  end
end
```

### Generated Migration: Sessions

```ruby
# db/migrate/XXXXXX_create_sessions.rb
class CreateSessions < ActiveRecord::Migration[8.0]
  def change
    create_table :sessions do |t|
      t.references :user, null: false, foreign_key: true
      t.string :ip_address
      t.string :user_agent

      t.timestamps
    end
  end
end
```

## Configuration

### ActionMailer Setup (Required for Password Reset)

```ruby
# config/environments/development.rb
Rails.application.configure do
  config.action_mailer.delivery_method = :letter_opener
  config.action_mailer.default_url_options = { host: "localhost", port: 3000 }
end

# config/environments/production.rb
Rails.application.configure do
  config.action_mailer.delivery_method = :smtp
  config.action_mailer.default_url_options = { host: "yourdomain.com", protocol: "https" }

  config.action_mailer.smtp_settings = {
    address: Rails.application.credentials.dig(:smtp, :address),
    port: 587,
    user_name: Rails.application.credentials.dig(:smtp, :username),
    password: Rails.application.credentials.dig(:smtp, :password),
    authentication: "plain",
    enable_starttls_auto: true
  }
end
```

### Routes (Auto-generated)

```ruby
# config/routes.rb
Rails.application.routes.draw do
  resource :session
  resources :passwords, param: :token

  # Add these for a complete auth flow
  get "login", to: "sessions#new"
  get "logout", to: "sessions#destroy"
end
```

## Usage in Controllers

### Requiring Authentication

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  include Authentication
end

# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  # All actions require authentication by default

  def index
    @posts = current_user.posts
  end
end
```

### Allowing Unauthenticated Access

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  allow_unauthenticated_access only: [:index, :show]

  def index
    @posts = Post.published
  end
end

# app/controllers/home_controller.rb
class HomeController < ApplicationController
  allow_unauthenticated_access

  def index
  end
end
```

### Accessing Current User

```ruby
# In controllers
def create
  @post = Current.user.posts.build(post_params)
end

# In views
<%= Current.user.email_address %>

# In models (use sparingly)
class Post < ApplicationRecord
  before_create do
    self.author ||= Current.user
  end
end
```

## Helper Method: current_user

The generated code uses `Current.user`. To add a more familiar `current_user` helper:

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  include Authentication

  helper_method :current_user

  private

  def current_user
    Current.user
  end
end
```

## Test Setup

### Test Helper

```ruby
# test/test_helper.rb or spec/rails_helper.rb
module AuthenticationTestHelper
  def sign_in(user)
    session_record = user.sessions.create!
    Current.session = session_record

    # For integration/system tests
    if respond_to?(:cookies)
      cookies.signed[:session_id] = session_record.id
    end
  end

  def sign_out
    Current.session&.destroy
    Current.reset
  end
end

# Include in test classes
class ActiveSupport::TestCase
  include AuthenticationTestHelper
end

# Or for RSpec
RSpec.configure do |config|
  config.include AuthenticationTestHelper, type: :request
  config.include AuthenticationTestHelper, type: :system
end
```

### Request Spec Example

```ruby
# spec/requests/posts_spec.rb
RSpec.describe "Posts", type: :request do
  let(:user) { create(:user) }

  describe "GET /posts" do
    context "when authenticated" do
      before { sign_in(user) }

      it "returns posts" do
        get posts_path
        expect(response).to have_http_status(:ok)
      end
    end

    context "when not authenticated" do
      it "redirects to login" do
        get posts_path
        expect(response).to redirect_to(new_session_path)
      end
    end
  end
end
```

## Common Issues

### Issue: Password reset emails not sending

```ruby
# Check ActionMailer configuration
Rails.application.config.action_mailer.raise_delivery_errors = true

# Verify mailer preview works
# Visit: http://localhost:3000/rails/mailers/passwords_mailer
```

### Issue: Session not persisting

```ruby
# Ensure cookies are configured correctly
# config/initializers/session_store.rb
Rails.application.config.session_store :cookie_store,
  key: '_myapp_session',
  same_site: :lax,
  secure: Rails.env.production?
```

### Issue: CSRF token issues with Turbo

```ruby
# Ensure CSRF meta tags are in layout
# app/views/layouts/application.html.erb
<head>
  <%= csrf_meta_tags %>
  <%= csp_meta_tag %>
</head>
```

## Next Steps

- [customization.md](./customization.md): Add registration, remember me, etc.
- [turbo-integration.md](./turbo-integration.md): Ensure Turbo compatibility
- [../patterns/two-factor.md](../patterns/two-factor.md): Add 2FA
