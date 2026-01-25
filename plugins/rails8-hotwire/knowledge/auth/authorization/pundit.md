# Pundit Authorization Setup

## Overview

Complete guide to setting up Pundit for authorization in Rails 8 applications. Covers installation, ApplicationController integration, verify_authorized/verify_policy_scoped enforcement, and error handling.

## When to Use

- When implementing role-based access control (RBAC)
- When resources have ownership-based permissions
- When you need explicit, testable authorization logic
- When authorization logic is complex and should be separated from controllers

## Quick Start

```ruby
# Gemfile
gem "pundit"
```

```bash
bundle install
rails generate pundit:install
```

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  include Pundit::Authorization
end
```

## Main Patterns

### Pattern 1: Basic Installation

```bash
# Install Pundit
bundle add pundit

# Generate base policy
rails generate pundit:install
```

This creates `app/policies/application_policy.rb`.

### Pattern 2: ApplicationController Integration

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  include Pundit::Authorization

  # Ensure every action is authorized
  after_action :verify_authorized, except: :index
  after_action :verify_policy_scoped, only: :index

  # Handle authorization failures
  rescue_from Pundit::NotAuthorizedError, with: :user_not_authorized

  private

  def user_not_authorized(exception)
    policy_name = exception.policy.class.to_s.underscore

    flash[:alert] = t(
      "pundit.#{policy_name}.#{exception.query}",
      default: "You are not authorized to perform this action."
    )

    redirect_back(fallback_location: root_path)
  end
end
```

### Pattern 3: Selective Enforcement

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  include Pundit::Authorization

  # Only enforce on specific controller types
  after_action :verify_authorized, except: :index,
    unless: -> { devise_controller? || public_controller? }

  after_action :verify_policy_scoped, only: :index,
    unless: -> { devise_controller? || public_controller? }

  private

  def public_controller?
    # Controllers that don't need authorization
    is_a?(PagesController) || is_a?(HomeController)
  end
end
```

### Pattern 4: Skip Authorization for Specific Actions

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  # Skip for specific actions
  skip_after_action :verify_authorized, only: [:index, :show]
  skip_after_action :verify_policy_scoped, only: [:show]

  def index
    # Public index - no authorization needed
    @posts = Post.published.includes(:user)
  end

  def show
    @post = Post.find(params[:id])
    # Public show for published posts
  end

  def edit
    @post = Post.find(params[:id])
    authorize @post  # Will be verified
  end
end
```

### Pattern 5: Headless Policies (No Record)

```ruby
# For actions without a specific record
class DashboardController < ApplicationController
  def index
    # Authorize with just the class
    authorize :dashboard, :index?

    @stats = Dashboard::StatsQuery.call(current_user)
  end

  def admin
    authorize :dashboard, :admin?

    @admin_data = AdminStats.all
  end
end

# app/policies/dashboard_policy.rb
class DashboardPolicy < ApplicationPolicy
  def index?
    user.present?
  end

  def admin?
    user&.admin?
  end
end
```

### Pattern 6: Custom Error Messages

```yaml
# config/locales/pundit.en.yml
en:
  pundit:
    default: "You don't have permission to do that."
    post_policy:
      update?: "You can only edit your own posts."
      destroy?: "You can only delete your own posts."
      publish?: "Only admins can publish posts."
    comment_policy:
      create?: "You must be logged in to comment."
      destroy?: "You can only delete your own comments."
```

```ruby
# app/controllers/application_controller.rb
def user_not_authorized(exception)
  policy_name = exception.policy.class.to_s.underscore
  message = t(
    "pundit.#{policy_name}.#{exception.query}",
    default: t("pundit.default")
  )

  respond_to do |format|
    format.html do
      flash[:alert] = message
      redirect_back(fallback_location: root_path)
    end
    format.turbo_stream do
      render turbo_stream: turbo_stream.update("flash", partial: "shared/flash",
        locals: { alert: message })
    end
    format.json { render json: { error: message }, status: :forbidden }
  end
end
```

### Pattern 7: Namespaced Policies

```ruby
# For admin namespace
# app/policies/admin/user_policy.rb
module Admin
  class UserPolicy < ApplicationPolicy
    def index?
      user.admin?
    end

    def impersonate?
      user.super_admin?
    end
  end
end

# Usage
class Admin::UsersController < Admin::BaseController
  def index
    authorize [:admin, User]
    @users = policy_scope([:admin, User])
  end

  def impersonate
    @user = User.find(params[:id])
    authorize [:admin, @user], :impersonate?
  end
end
```

### Pattern 8: API Controllers

```ruby
# app/controllers/api/v1/base_controller.rb
module Api
  module V1
    class BaseController < ActionController::API
      include Pundit::Authorization

      after_action :verify_authorized

      rescue_from Pundit::NotAuthorizedError do |exception|
        render json: {
          error: "forbidden",
          message: "You are not authorized to perform this action"
        }, status: :forbidden
      end
    end
  end
end
```

## Pundit Helper Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `authorize(record)` | Check policy for current action | `authorize @post` |
| `authorize(record, :action?)` | Check specific action | `authorize @post, :publish?` |
| `policy(record)` | Get policy instance | `policy(@post).update?` |
| `policy_scope(Model)` | Get scoped records | `policy_scope(Post)` |
| `skip_authorization` | Skip verify_authorized | For public actions |
| `skip_policy_scope` | Skip verify_policy_scoped | When not using scope |

## View Helpers

```erb
<%# Check policy in views %>
<% if policy(@post).edit? %>
  <%= link_to "Edit", edit_post_path(@post) %>
<% end %>

<% if policy(@post).destroy? %>
  <%= button_to "Delete", @post, method: :delete %>
<% end %>

<%# For collections %>
<% policy_scope(Post).each do |post| %>
  <%= render post %>
<% end %>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Forgetting `authorize` | Action not protected | Use `verify_authorized` |
| Complex logic in controllers | Hard to test | Move to policies |
| Not using `policy_scope` | Data leakage | Always scope index queries |
| Catching errors silently | Security issues hidden | Log authorization failures |

## Related Skills

- [policies.md](./policies.md): Writing policy classes
- [scopes.md](./scopes.md): Policy scope patterns
- [testing.md](./testing.md): Testing authorization

## References

- [Pundit GitHub](https://github.com/varvet/pundit)
- [Pundit Wiki](https://github.com/varvet/pundit/wiki)
