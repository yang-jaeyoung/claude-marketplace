# Pundit Policy Patterns

## Overview

Comprehensive guide to writing Pundit policies for authorization in Rails 8 applications. Covers common patterns, helper methods, permitted attributes, and policy organization.

## When to Use

- When defining who can access what resources
- When authorization logic differs by user role
- When resources have ownership requirements
- When implementing complex permission rules

## Quick Start

```bash
# Generate a policy for a model
rails generate pundit:policy Post
```

```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  def show?
    true
  end

  def update?
    owner_or_admin?
  end
end
```

## Main Patterns

### Pattern 1: Base Application Policy

```ruby
# app/policies/application_policy.rb
class ApplicationPolicy
  attr_reader :user, :record

  def initialize(user, record)
    @user = user
    @record = record
  end

  # Default: deny all
  def index?
    false
  end

  def show?
    false
  end

  def create?
    false
  end

  def new?
    create?
  end

  def update?
    false
  end

  def edit?
    update?
  end

  def destroy?
    false
  end

  private

  # Common helpers
  def owner?
    record.respond_to?(:user_id) && record.user_id == user&.id
  end

  def admin?
    user&.admin?
  end

  def owner_or_admin?
    owner? || admin?
  end

  def logged_in?
    user.present?
  end

  # Default scope
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

    def admin?
      user&.admin?
    end
  end
end
```

### Pattern 2: Resource Policy with Ownership

```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  # Anyone can view published posts
  def show?
    record.published? || owner_or_admin?
  end

  # Logged in users can create
  def create?
    logged_in?
  end

  # Only owner or admin can update
  def update?
    owner_or_admin?
  end

  # Only owner or admin can delete
  def destroy?
    owner_or_admin?
  end

  # Only admin can publish
  def publish?
    admin?
  end

  # Only admin can feature
  def feature?
    admin?
  end

  # Can archive own posts or admin can archive any
  def archive?
    owner_or_admin?
  end

  # Permitted attributes vary by role
  def permitted_attributes
    if admin?
      [:title, :body, :status, :featured, :published_at, :category_id, tag_ids: []]
    else
      [:title, :body, :category_id, tag_ids: []]
    end
  end

  class Scope < Scope
    def resolve
      if user&.admin?
        scope.all
      elsif user
        # User sees own posts + published posts
        scope.where(user: user).or(scope.published)
      else
        # Anonymous sees only published
        scope.published
      end
    end
  end
end
```

### Pattern 3: Role-Based Policy

```ruby
# app/policies/order_policy.rb
class OrderPolicy < ApplicationPolicy
  def show?
    owner? || staff_member? || admin?
  end

  def create?
    logged_in?
  end

  def update?
    return false unless logged_in?
    return true if admin?

    # Staff can update if not shipped
    return true if staff_member? && !record.shipped?

    # Owner can update if pending
    owner? && record.pending?
  end

  def cancel?
    return true if admin?

    owner? && record.can_cancel?
  end

  def refund?
    admin? || (staff_member? && record.refundable?)
  end

  def ship?
    staff_member? || admin?
  end

  private

  def staff_member?
    user&.role.in?(%w[staff manager])
  end

  def owner?
    record.user_id == user&.id
  end
end
```

### Pattern 4: Permitted Attributes by Action

```ruby
# app/policies/user_policy.rb
class UserPolicy < ApplicationPolicy
  def update?
    owner? || admin?
  end

  # Different attributes for different actions
  def permitted_attributes_for_create
    [:email, :password, :password_confirmation, :name]
  end

  def permitted_attributes_for_update
    if admin?
      [:email, :name, :role, :active, :avatar]
    else
      [:name, :avatar, :notification_preferences]
    end
  end

  def permitted_attributes_for_account_update
    [:email, :password, :password_confirmation, :current_password, :name]
  end
end

# Usage in controller
class UsersController < ApplicationController
  def update
    @user = User.find(params[:id])
    authorize @user

    if @user.update(permitted_attributes(@user))
      redirect_to @user
    else
      render :edit, status: :unprocessable_entity
    end
  end
end
```

### Pattern 5: Context-Dependent Authorization

```ruby
# app/policies/comment_policy.rb
class CommentPolicy < ApplicationPolicy
  def create?
    return false unless logged_in?

    # Can't comment on locked posts
    return false if record.post.locked?

    # Can't comment if user is banned
    !user.banned?
  end

  def update?
    return false if record.post.locked?

    owner? && record.editable?
  end

  def destroy?
    return true if admin?
    return true if record.post.user == user  # Post owner can delete comments

    owner? && record.recent?  # Can only delete recent own comments
  end

  def report?
    logged_in? && !owner?  # Can't report own comment
  end

  private

  def owner?
    record.user_id == user&.id
  end
end
```

### Pattern 6: Multi-Tenant Policy

```ruby
# app/policies/project_policy.rb
class ProjectPolicy < ApplicationPolicy
  def show?
    same_organization? && (member? || admin?)
  end

  def create?
    same_organization? && (manager? || admin?)
  end

  def update?
    same_organization? && (owner? || manager? || admin?)
  end

  def destroy?
    same_organization? && admin?
  end

  def invite_member?
    same_organization? && (owner? || manager? || admin?)
  end

  private

  def same_organization?
    user&.organization_id == record.organization_id
  end

  def member?
    record.members.include?(user)
  end

  def manager?
    user&.role == "manager" || record.managers.include?(user)
  end

  def owner?
    record.owner_id == user&.id
  end

  class Scope < Scope
    def resolve
      if user&.admin?
        scope.where(organization: user.organization)
      else
        scope.where(organization: user.organization)
             .joins(:memberships)
             .where(memberships: { user: user })
      end
    end
  end
end
```

### Pattern 7: Policy with External Service Check

```ruby
# app/policies/premium_feature_policy.rb
class PremiumFeaturePolicy < ApplicationPolicy
  def use?
    return true if admin?

    user&.subscription&.active? && user.subscription.includes_feature?(record.name)
  end

  def trial?
    logged_in? && !user.used_trial?(record.name)
  end
end

# app/policies/export_policy.rb
class ExportPolicy < ApplicationPolicy
  def create?
    return false unless logged_in?
    return true if admin?

    # Check rate limit
    user.exports.today.count < user.export_limit
  end

  def download?
    owner? || admin?
  end

  private

  def owner?
    record.user_id == user.id
  end
end
```

### Pattern 8: Composite Policies

```ruby
# app/policies/document_policy.rb
class DocumentPolicy < ApplicationPolicy
  def show?
    public_document? || shared_with_user? || owner_or_admin?
  end

  def download?
    show? && record.downloadable?
  end

  def share?
    owner? || admin?
  end

  def update?
    return false if record.locked?

    owner_or_admin? || editor?
  end

  private

  def public_document?
    record.visibility == "public"
  end

  def shared_with_user?
    return false unless user

    record.shares.exists?(user: user)
  end

  def editor?
    return false unless user

    record.shares.exists?(user: user, permission: "edit")
  end

  class Scope < Scope
    def resolve
      return scope.where(visibility: "public") unless user

      scope.where(visibility: "public")
           .or(scope.where(user: user))
           .or(scope.joins(:shares).where(shares: { user: user }))
    end
  end
end
```

## Policy Method Naming Conventions

| Method | Convention | Example |
|--------|------------|---------|
| CRUD actions | Match controller action + `?` | `show?`, `create?`, `update?`, `destroy?` |
| Custom actions | Action name + `?` | `publish?`, `archive?`, `export?` |
| Attributes | `permitted_attributes` | Returns array of symbols |
| Role-based attributes | `permitted_attributes_for_*` | `permitted_attributes_for_admin` |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Logic in controllers | Duplicated, hard to test | Move to policy |
| Too many conditions | Hard to understand | Extract helper methods |
| Not using `Scope` | Leaking unauthorized data | Always scope queries |
| Returning nil | Confusing results | Always return boolean |

## Related Skills

- [pundit.md](./pundit.md): Pundit setup
- [scopes.md](./scopes.md): Policy scope patterns
- [testing.md](./testing.md): Testing policies
- [../snippets/policies/](../snippets/policies/): Copy-ready policy examples

## References

- [Pundit README](https://github.com/varvet/pundit#policies)
- [Pundit Custom Policy Class](https://github.com/varvet/pundit#custom-policy-class)
