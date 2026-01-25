---
name: rails8-auth
description: Rails 8 built-in authentication, Devise, Pundit authorization, OAuth social login, API authentication. Use when building user authentication/authorization systems.
triggers:
  - authentication
  - authorization
  - devise
  - pundit
  - oauth
  - omniauth
  - login
  - sign in
  - permission
  - policy
  - api token
  - 인증
  - 인가
  - 로그인
  - 로그아웃
  - 권한
  - 정책
  - 소셜 로그인
summary: |
  Rails 8의 인증과 인가 시스템을 다룹니다. Rails 8 내장 인증, Devise, Pundit 인가,
  OAuth 소셜 로그인, API 토큰 인증을 포함합니다. 사용자 인증 시스템이나
  역할 기반 권한 관리가 필요할 때 참조하세요.
token_cost: high
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - builtin/*.md
    - devise/*.md
    - authorization/*.md
  deep:
    - "**/*.md"
    - "**/*.rb"
---

# Auth: Authentication & Authorization

## Overview

Covers authentication and authorization in Rails 8. Includes Rails 8 built-in authentication, Devise, Pundit, and OAuth integration patterns.

## Subdirectories

| Directory | Description |
|-----------|-------------|
| [builtin/](./builtin/) | **Rails 8 built-in authentication** - Lightweight, no-gem auth |
| [devise/](./devise/) | Devise setup, configuration, and Turbo compatibility |
| [authorization/](./authorization/) | Pundit policies and scopes |
| [oauth/](./oauth/) | OmniAuth and social login providers |
| [patterns/](./patterns/) | Advanced patterns (2FA, magic links, invitations) |

## When to Use

- When building user authentication systems
- When managing role-based permissions
- When integrating social login
- When implementing API authentication

## Core Principles

| Principle | Description |
|-----------|-------------|
| Least Privilege | Grant only necessary permissions |
| Explicit Authorization | Check permissions on all actions |
| Secure Defaults | Deny access by default |
| Secret Separation | Manage secrets with credentials |

## Quick Start

### Option 1: Rails 8 Built-in Authentication (Recommended)

```bash
# Rails 8 default authentication generator
bin/rails generate authentication
bin/rails db:migrate
```

**Generated features:**
- User model (has_secure_password)
- Session model (session tracking)
- SessionsController (login/logout)
- Password reset
- Rate Limiting (10 attempts per 3 minutes)

**Not included (manual implementation required):**
- Registration
- OAuth
- 2FA

### Option 2: Devise (Full-featured)

```bash
bundle add devise
rails generate devise:install
rails generate devise User
rails db:migrate
```

```ruby
# config/initializers/devise.rb (Rails 8 + Turbo compatible)
Devise.setup do |config|
  config.responder.error_status = :unprocessable_entity
  config.responder.redirect_status = :see_other
end
```

## File Structure

```
auth/
├── SKILL.md
├── builtin/                    # NEW: Rails 8 built-in authentication
│   ├── SKILL.md               # Overview and comparison with Devise
│   ├── setup.md               # Generation and configuration
│   ├── customization.md       # Registration, remember me, etc.
│   └── turbo-integration.md   # Turbo compatibility patterns
├── devise/
│   ├── setup.md
│   ├── configuration.md
│   ├── views.md
│   ├── controllers.md
│   ├── turbo.md
│   └── testing.md
├── oauth/
│   ├── omniauth.md
│   ├── google.md
│   ├── github.md
│   └── apple.md
├── authorization/
│   ├── pundit.md
│   ├── policies.md
│   ├── scopes.md
│   └── testing.md
├── patterns/
│   ├── magic-link.md
│   ├── invitation.md
│   ├── two-factor.md
│   └── api-tokens.md
└── snippets/
    ├── policies/
    │   ├── application_policy.rb
    │   └── post_policy.rb
    └── devise/
        └── turbo_failure_app.rb
```

## Main Patterns

### Pattern 1: Pundit Authorization

```bash
bundle add pundit
rails generate pundit:install
```

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  include Pundit::Authorization

  after_action :verify_authorized, except: :index
  after_action :verify_policy_scoped, only: :index

  rescue_from Pundit::NotAuthorizedError, with: :user_not_authorized

  private

  def user_not_authorized
    flash[:alert] = "You don't have permission to perform this action."
    redirect_back(fallback_location: root_path)
  end
end
```

```ruby
# app/policies/application_policy.rb
class ApplicationPolicy
  attr_reader :user, :record

  def initialize(user, record)
    @user = user
    @record = record
  end

  def index?
    true
  end

  def show?
    true
  end

  def create?
    user.present?
  end

  def new?
    create?
  end

  def update?
    owner_or_admin?
  end

  def edit?
    update?
  end

  def destroy?
    owner_or_admin?
  end

  private

  def owner_or_admin?
    user&.admin? || owner?
  end

  def owner?
    record.respond_to?(:user) && record.user == user
  end

  class Scope
    attr_reader :user, :scope

    def initialize(user, scope)
      @user = user
      @scope = scope
    end

    def resolve
      scope.all
    end
  end
end
```

```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  def show?
    record.published? || owner_or_admin?
  end

  def update?
    owner_or_admin?
  end

  def publish?
    user&.admin? || owner?
  end

  class Scope < Scope
    def resolve
      if user&.admin?
        scope.all
      elsif user
        scope.where(user: user).or(scope.published)
      else
        scope.published
      end
    end
  end
end
```

```ruby
# Usage in controller
class PostsController < ApplicationController
  def index
    @posts = policy_scope(Post).includes(:user).recent
  end

  def show
    @post = Post.find(params[:id])
    authorize @post
  end

  def update
    @post = Post.find(params[:id])
    authorize @post

    if @post.update(post_params)
      redirect_to @post, status: :see_other
    else
      render :edit, status: :unprocessable_entity
    end
  end

  def publish
    @post = Post.find(params[:id])
    authorize @post

    @post.update(published: true)
    redirect_to @post, notice: "Published successfully", status: :see_other
  end
end
```

### Pattern 2: Devise + Turbo Compatible

```ruby
# app/controllers/turbo_devise_controller.rb
class TurboDeviseController < ApplicationController
  class Responder < ActionController::Responder
    def to_turbo_stream
      controller.render(options.merge(formats: :html))
    rescue ActionView::MissingTemplate => e
      if get?
        raise e
      elsif has_errors? && default_action
        render rendering_options.merge(formats: :html, status: :unprocessable_entity)
      else
        redirect_to navigation_location
      end
    end
  end

  self.responder = Responder
  respond_to :html, :turbo_stream
end

# config/initializers/devise.rb
Devise.setup do |config|
  config.parent_controller = 'TurboDeviseController'
  config.responder.error_status = :unprocessable_entity
  config.responder.redirect_status = :see_other
end
```

### Pattern 3: OAuth (OmniAuth)

```ruby
# Gemfile
gem "omniauth-google-oauth2"
gem "omniauth-github"
gem "omniauth-rails_csrf_protection"

# config/initializers/omniauth.rb
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :google_oauth2,
    Rails.application.credentials.dig(:google, :client_id),
    Rails.application.credentials.dig(:google, :client_secret),
    scope: "email,profile"

  provider :github,
    Rails.application.credentials.dig(:github, :client_id),
    Rails.application.credentials.dig(:github, :client_secret),
    scope: "user:email"
end
```

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_many :identities, dependent: :destroy

  def self.from_omniauth(auth)
    identity = Identity.find_or_initialize_by(
      provider: auth.provider,
      uid: auth.uid
    )

    if identity.user
      identity.user
    else
      user = User.find_or_create_by(email: auth.info.email) do |u|
        u.name = auth.info.name
        u.password = SecureRandom.hex(16)
      end
      identity.user = user
      identity.save!
      user
    end
  end
end

# app/models/identity.rb
class Identity < ApplicationRecord
  belongs_to :user
  validates :provider, :uid, presence: true
  validates :uid, uniqueness: { scope: :provider }
end
```

```ruby
# app/controllers/omniauth_callbacks_controller.rb
class OmniauthCallbacksController < ApplicationController
  skip_before_action :verify_authenticity_token, only: [:google_oauth2, :github]

  def google_oauth2
    handle_auth("Google")
  end

  def github
    handle_auth("GitHub")
  end

  def failure
    redirect_to root_path, alert: "Authentication failed."
  end

  private

  def handle_auth(provider)
    @user = User.from_omniauth(request.env["omniauth.auth"])

    if @user.persisted?
      sign_in_and_redirect @user, event: :authentication
      flash[:notice] = "Signed in with #{provider} account."
    else
      redirect_to new_user_registration_path, alert: "#{provider} authentication failed."
    end
  end
end
```

### Pattern 4: API Token Authentication

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_secure_token :api_token

  def regenerate_api_token!
    regenerate_api_token
    save!
  end
end

# app/controllers/api/base_controller.rb
module Api
  class BaseController < ActionController::API
    before_action :authenticate_api_user!

    private

    def authenticate_api_user!
      token = request.headers["Authorization"]&.split(" ")&.last
      @current_api_user = User.find_by(api_token: token)

      render json: { error: "Unauthorized" }, status: :unauthorized unless @current_api_user
    end

    def current_api_user
      @current_api_user
    end
  end
end
```

### Pattern 5: Registration (Extending Rails 8 Built-in Authentication)

```ruby
# app/controllers/registrations_controller.rb
class RegistrationsController < ApplicationController
  def new
    @user = User.new
  end

  def create
    @user = User.new(user_params)

    if @user.save
      start_new_session_for(@user)
      redirect_to root_path, notice: "Registration complete!", status: :see_other
    else
      render :new, status: :unprocessable_entity
    end
  end

  private

  def user_params
    params.require(:user).permit(:email, :password, :password_confirmation, :name)
  end
end
```

```erb
<!-- app/views/registrations/new.html.erb -->
<%= form_with model: @user, url: registration_path, class: "space-y-6" do |f| %>
  <%= render "shared/form_errors", model: @user %>

  <div>
    <%= f.label :name %>
    <%= f.text_field :name, autofocus: true, required: true %>
  </div>

  <div>
    <%= f.label :email %>
    <%= f.email_field :email, required: true %>
  </div>

  <div>
    <%= f.label :password %>
    <%= f.password_field :password, required: true %>
  </div>

  <div>
    <%= f.label :password_confirmation %>
    <%= f.password_field :password_confirmation, required: true %>
  </div>

  <%= f.submit "Sign Up" %>
<% end %>
```

## Authentication Method Selection Guide

| Requirement | Recommended Method |
|-------------|-------------------|
| Simple login | Rails 8 built-in authentication |
| Full features (confirmation email, lockout, etc.) | Devise |
| Social login only | OmniAuth directly |
| API only | JWT or API tokens |
| Enterprise SSO | SAML/OIDC |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Missing permission check | Security vulnerability | Pundit verify_authorized |
| Storing plaintext passwords | Security threat | has_secure_password |
| Session fixation | Session hijacking | Regenerate session on login |
| Unlimited login attempts | Brute force attacks | Rate Limiting |

## Related Skills

- [core](../core/SKILL.md): Credentials setup
- [controllers](../controllers/SKILL.md): Authentication filters
- [testing](../testing/): Policy testing (Phase 3)

## References

- [Rails Security Guide](https://guides.rubyonrails.org/security.html)
- [Devise GitHub](https://github.com/heartcombo/devise)
- [Pundit GitHub](https://github.com/varvet/pundit)
- [OmniAuth](https://github.com/omniauth/omniauth)
