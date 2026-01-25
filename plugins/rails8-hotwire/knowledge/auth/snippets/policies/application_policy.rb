# frozen_string_literal: true

# Base policy class for Pundit authorization
# All policies inherit from this class
#
# Usage:
#   rails generate pundit:policy Post
#   # Creates app/policies/post_policy.rb inheriting from ApplicationPolicy
#
# Controller usage:
#   authorize @post           # Uses current action (e.g., update?)
#   authorize @post, :publish? # Explicit action
#   policy_scope(Post)        # Scoped query
#
class ApplicationPolicy
  attr_reader :user, :record

  # @param user [User, nil] The current user (can be nil for guests)
  # @param record [Object] The record being authorized
  def initialize(user, record)
    @user = user
    @record = record
  end

  # Index action - typically allows viewing lists
  def index?
    false
  end

  # Show action - viewing a single record
  def show?
    false
  end

  # Create action - creating new records
  def create?
    false
  end

  # New action - displaying create form (delegates to create?)
  def new?
    create?
  end

  # Update action - modifying existing records
  def update?
    false
  end

  # Edit action - displaying edit form (delegates to update?)
  def edit?
    update?
  end

  # Destroy action - deleting records
  def destroy?
    false
  end

  private

  # Check if user is logged in
  # @return [Boolean]
  def logged_in?
    user.present?
  end

  # Check if user is an admin
  # Assumes User model has an admin? method or role column
  # @return [Boolean]
  def admin?
    user&.admin?
  end

  # Check if user is a moderator
  # @return [Boolean]
  def moderator?
    user&.moderator? || admin?
  end

  # Check if user owns the record
  # Assumes record has a user_id or user association
  # @return [Boolean]
  def owner?
    return false unless user && record

    if record.respond_to?(:user_id)
      record.user_id == user.id
    elsif record.respond_to?(:user)
      record.user == user
    else
      false
    end
  end

  # Check if user is owner or admin
  # Most common permission pattern
  # @return [Boolean]
  def owner_or_admin?
    owner? || admin?
  end

  # Check if user is owner or moderator
  # @return [Boolean]
  def owner_or_moderator?
    owner? || moderator?
  end

  # Check if user belongs to the same organization as the record
  # Assumes both User and record have organization_id
  # @return [Boolean]
  def same_organization?
    return false unless user && record

    user.organization_id == record.organization_id
  end

  # Base scope class - all policy scopes inherit from this
  # Scopes filter collections based on user permissions
  #
  # Usage:
  #   policy_scope(Post)  # Returns Post::Scope.new(current_user, Post).resolve
  #
  class Scope
    attr_reader :user, :scope

    # @param user [User, nil] The current user
    # @param scope [ActiveRecord::Relation] The base scope to filter
    def initialize(user, scope)
      @user = user
      @scope = scope
    end

    # Override in subclasses to filter the scope
    # @return [ActiveRecord::Relation]
    def resolve
      raise NotImplementedError, "You must define #resolve in #{self.class}"
    end

    private

    def logged_in?
      user.present?
    end

    def admin?
      user&.admin?
    end

    def moderator?
      user&.moderator? || admin?
    end
  end
end
