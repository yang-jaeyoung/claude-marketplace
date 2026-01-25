# Pundit Policy Scopes

## Overview

Guide to implementing Pundit policy scopes for filtering collections based on user permissions. Scopes ensure users only see records they're authorized to access.

## When to Use

- When filtering index/list actions by user permissions
- When preventing data leakage in collections
- When different users should see different subsets of data
- When implementing multi-tenant data isolation

## Quick Start

```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      if user&.admin?
        scope.all
      else
        scope.published
      end
    end
  end
end

# Controller usage
@posts = policy_scope(Post)
```

## Main Patterns

### Pattern 1: Basic Scope Structure

```ruby
# app/policies/application_policy.rb
class ApplicationPolicy
  class Scope
    attr_reader :user, :scope

    def initialize(user, scope)
      @user = user
      @scope = scope
    end

    def resolve
      raise NotImplementedError, "You must define #resolve in #{self.class}"
    end

    private

    # Helper methods available to all scopes
    def admin?
      user&.admin?
    end

    def logged_in?
      user.present?
    end
  end
end
```

### Pattern 2: Role-Based Scoping

```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      case
      when admin?
        # Admins see everything
        scope.all
      when logged_in?
        # Users see own posts + published posts
        scope.where(user: user).or(scope.published)
      else
        # Anonymous users see only published
        scope.published
      end
    end
  end
end
```

### Pattern 3: Organization/Tenant Scoping

```ruby
# app/policies/project_policy.rb
class ProjectPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      return scope.none unless user

      if user.super_admin?
        scope.all
      else
        scope.where(organization: user.organization)
      end
    end
  end
end

# app/policies/document_policy.rb
class DocumentPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      return scope.none unless user

      base_scope = scope.where(organization: user.organization)

      if user.admin?
        base_scope
      elsif user.manager?
        base_scope.where(department: user.department)
      else
        base_scope.where(user: user)
                  .or(base_scope.where(visibility: "team"))
      end
    end
  end
end
```

### Pattern 4: Membership-Based Scoping

```ruby
# app/policies/team_policy.rb
class TeamPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      return scope.none unless user

      if admin?
        scope.all
      else
        scope.joins(:memberships).where(memberships: { user: user })
      end
    end
  end
end

# app/policies/task_policy.rb
class TaskPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      return scope.none unless user

      if admin?
        scope.all
      else
        # Tasks in user's teams + tasks assigned to user
        team_ids = user.teams.pluck(:id)
        scope.where(team_id: team_ids)
             .or(scope.where(assignee: user))
      end
    end
  end
end
```

### Pattern 5: Complex Visibility Rules

```ruby
# app/policies/document_policy.rb
class DocumentPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      return scope.where(visibility: "public") unless user

      if admin?
        scope.all
      else
        # Complex OR conditions
        scope.where(visibility: "public")
             .or(scope.where(user: user))  # Own documents
             .or(scope.where(visibility: "organization", organization: user.organization))
             .or(shared_with_user)
      end
    end

    private

    def shared_with_user
      scope.joins(:shares).where(shares: { user: user })
    end
  end
end
```

### Pattern 6: Soft Delete Scoping

```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      base = if admin?
        scope.all  # Admins see deleted posts too
      else
        scope.active  # Non-admins don't see deleted
      end

      apply_visibility_scope(base)
    end

    private

    def apply_visibility_scope(base)
      if admin?
        base
      elsif logged_in?
        base.where(user: user).or(base.published)
      else
        base.published
      end
    end
  end
end
```

### Pattern 7: Scoping with Eager Loading

```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      base_scope.includes(:user, :category, :tags)
    end

    private

    def base_scope
      if admin?
        scope.all
      elsif logged_in?
        scope.where(user: user).or(scope.published)
      else
        scope.published
      end
    end
  end
end

# Controller - eager loading is already applied
@posts = policy_scope(Post).order(created_at: :desc)
```

### Pattern 8: Conditional Admin Scoping

```ruby
# app/policies/order_policy.rb
class OrderPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      return scope.none unless user

      case user.role
      when "super_admin"
        scope.all
      when "admin"
        # Admins see their organization's orders
        scope.joins(:store).where(stores: { organization: user.organization })
      when "store_manager"
        # Store managers see their store's orders
        scope.where(store: user.managed_stores)
      when "staff"
        # Staff see orders they've handled
        scope.where(store: user.store)
             .or(scope.where(handled_by: user))
      else
        # Customers see only their own orders
        scope.where(user: user)
      end
    end
  end
end
```

## Controller Usage

### Basic Usage

```ruby
class PostsController < ApplicationController
  def index
    @posts = policy_scope(Post).order(created_at: :desc)
  end
end
```

### With Additional Filtering

```ruby
class PostsController < ApplicationController
  def index
    @posts = policy_scope(Post)
      .where(category: params[:category])
      .order(created_at: :desc)
      .page(params[:page])
  end
end
```

### With Custom Scope Method

```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      standard_scope
    end

    def resolve_for_dashboard
      standard_scope.recent.limit(5)
    end

    def resolve_for_feed
      standard_scope.published.includes(:user).order(published_at: :desc)
    end

    private

    def standard_scope
      admin? ? scope.all : scope.where(user: user).or(scope.published)
    end
  end
end

# Controller
class DashboardController < ApplicationController
  def index
    @recent_posts = PostPolicy::Scope.new(current_user, Post).resolve_for_dashboard
  end
end
```

### Nested Resource Scoping

```ruby
class CommentsController < ApplicationController
  def index
    @post = Post.find(params[:post_id])
    authorize @post, :show?

    @comments = policy_scope(@post.comments)
      .includes(:user)
      .order(created_at: :desc)
  end
end

# app/policies/comment_policy.rb
class CommentPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      if admin?
        scope.all
      else
        scope.visible  # Hide flagged comments from non-admins
      end
    end
  end
end
```

## View Usage

```erb
<%# Use policy_scope in views %>
<% policy_scope(Post).featured.each do |post| %>
  <%= render post %>
<% end %>

<%# Or use helper %>
<%= render policy_scope(current_user.posts.draft) %>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Returning `nil` | Causes NoMethodError | Return `scope.none` |
| Not handling nil user | Crashes for guests | Check `user.present?` |
| Complex joins without indexes | Slow queries | Add database indexes |
| Duplicating scope logic | Hard to maintain | Extract to model scopes |
| Not using `policy_scope` | Data leakage | Always scope collections |

## Performance Tips

```ruby
class PostPolicy < ApplicationPolicy
  class Scope < Scope
    def resolve
      # Use exists? for subqueries instead of pluck
      # BAD: scope.where(team_id: user.teams.pluck(:id))
      # GOOD: scope.where(team_id: user.teams.select(:id))

      # Use single query with OR instead of multiple queries
      scope.where(user: user).or(scope.published)
    end
  end
end
```

## Related Skills

- [pundit.md](./pundit.md): Pundit setup
- [policies.md](./policies.md): Policy patterns
- [testing.md](./testing.md): Testing scopes

## References

- [Pundit Scopes](https://github.com/varvet/pundit#scopes)
- [ActiveRecord OR queries](https://guides.rubyonrails.org/active_record_querying.html#or-conditions)
