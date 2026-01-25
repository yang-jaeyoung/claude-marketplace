# frozen_string_literal: true

# Example resource policy demonstrating common authorization patterns
# Copy and adapt for your own models
#
# Assumes Post model has:
#   - belongs_to :user
#   - scope :published, -> { where(published: true) }
#   - column :published (boolean)
#
# Controller usage:
#   def show
#     @post = Post.find(params[:id])
#     authorize @post
#   end
#
#   def index
#     @posts = policy_scope(Post)
#   end
#
#   def update
#     @post = Post.find(params[:id])
#     authorize @post
#     @post.update(permitted_attributes(@post))
#   end
#
class PostPolicy < ApplicationPolicy
  # Anyone can view index (scope handles filtering)
  def index?
    true
  end

  # Published posts are public; drafts visible to owner/admin
  def show?
    record.published? || owner_or_admin?
  end

  # Any logged-in user can create posts
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

  # Only admin can publish posts
  def publish?
    admin?
  end

  # Only admin can unpublish posts
  def unpublish?
    admin?
  end

  # Only admin can feature posts
  def feature?
    admin?
  end

  # Owner or admin can archive
  def archive?
    owner_or_admin?
  end

  # Define permitted attributes based on user role
  # Used with permitted_attributes(@post) in controller
  #
  # @return [Array<Symbol>]
  def permitted_attributes
    if admin?
      # Admins can set all attributes including publication status
      [:title, :body, :published, :featured, :published_at, :category_id, tag_ids: []]
    else
      # Regular users can only set content fields
      [:title, :body, :category_id, tag_ids: []]
    end
  end

  # Alternative: different attributes for different actions
  def permitted_attributes_for_create
    [:title, :body, :category_id, tag_ids: []]
  end

  def permitted_attributes_for_update
    attrs = [:title, :body, :category_id, tag_ids: []]
    attrs += [:published, :featured, :published_at] if admin?
    attrs
  end

  # Scope class - filters Post collections based on user permissions
  # Ensures users only see posts they're allowed to see
  #
  # Usage in controller:
  #   @posts = policy_scope(Post).recent.page(params[:page])
  #
  class Scope < Scope
    # @return [ActiveRecord::Relation] Filtered posts
    def resolve
      if admin?
        # Admins see all posts including drafts
        scope.all
      elsif logged_in?
        # Logged-in users see published posts + their own drafts
        scope.where(user: user).or(scope.where(published: true))
      else
        # Anonymous users only see published posts
        scope.where(published: true)
      end
    end

    # Alternative scope for dashboard showing only user's own posts
    def resolve_own
      return scope.none unless logged_in?

      scope.where(user: user)
    end

    # Scope for admin dashboard showing posts needing review
    def resolve_for_review
      return scope.none unless admin?

      scope.where(published: false).order(created_at: :desc)
    end
  end
end
