# Multi-Tenant SaaS

## Overview

Complete multi-tenant architecture with subdomain routing, data isolation, row-level security, and tenant-scoped queries. Build SaaS applications where each organization has isolated data.

## Prerequisites

- [core/gems](../../core/gems.md): acts_as_tenant, apartment
- [models/associations](../../models/associations.md): belongs_to relationships
- [controllers/service-objects](../../controllers/service-objects.md): tenant context

## Quick Start

```ruby
# Gemfile
gem "acts_as_tenant"

# Terminal
bundle install
rails generate migration AddAccountIdToModels
```

## Implementation

### Step 1: Account Model and Subdomain Routing

```ruby
# app/models/account.rb
class Account < ApplicationRecord
  has_many :users, dependent: :destroy
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy

  validates :subdomain, presence: true, uniqueness: { case_sensitive: false }
  validates :subdomain, format: { with: /\A[a-z0-9-]+\z/, message: "only lowercase letters, numbers, and hyphens" }
  validates :subdomain, exclusion: { in: %w[www admin api app], message: "reserved subdomain" }

  before_validation :normalize_subdomain

  private

  def normalize_subdomain
    self.subdomain = subdomain.to_s.downcase.strip
  end
end
```

```ruby
# db/migrate/20240101000001_create_accounts.rb
class CreateAccounts < ActiveRecord::Migration[8.0]
  def change
    create_table :accounts do |t|
      t.string :name, null: false
      t.string :subdomain, null: false
      t.string :plan, default: "free"
      t.timestamps
    end

    add_index :accounts, :subdomain, unique: true
  end
end

# db/migrate/20240101000002_add_account_id_to_models.rb
class AddAccountIdToModels < ActiveRecord::Migration[8.0]
  def change
    add_reference :users, :account, null: false, foreign_key: true
    add_reference :posts, :account, null: false, foreign_key: true
    add_reference :comments, :account, null: false, foreign_key: true

    # Add indexes for tenant-scoped queries
    add_index :users, [:account_id, :email], unique: true
    add_index :posts, [:account_id, :created_at]
    add_index :comments, [:account_id, :post_id]
  end
end
```

### Step 2: Tenant-Scoped Models

```ruby
# app/models/application_record.rb
class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class

  # Skip tenant scoping for models that shouldn't be scoped
  mattr_accessor :skip_tenant_scoping, default: false
end

# app/models/user.rb
class User < ApplicationRecord
  acts_as_tenant :account

  belongs_to :account
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy

  validates :email, presence: true, uniqueness: { scope: :account_id }

  # Devise or custom authentication
  has_secure_password
end

# app/models/post.rb
class Post < ApplicationRecord
  acts_as_tenant :account

  belongs_to :account
  belongs_to :user
  has_many :comments, dependent: :destroy

  validates :title, presence: true
  validates :user, presence: true

  # Turbo Streams broadcast within tenant
  broadcasts_to ->(post) { [post.account, :posts] }
end

# app/models/comment.rb
class Comment < ApplicationRecord
  acts_as_tenant :account

  belongs_to :account
  belongs_to :post
  belongs_to :user

  validates :body, presence: true

  broadcasts_to ->(comment) { [comment.account, comment.post] }
end
```

### Step 3: Subdomain Routing and Tenant Detection

```ruby
# config/routes.rb
Rails.application.routes.draw do
  # Account signup (on root domain)
  constraints subdomain: "" do
    root "marketing#index"
    resources :accounts, only: [:new, :create]
  end

  # Tenant app (on subdomains)
  constraints subdomain: /.+/ do
    root "dashboard#index"

    resource :session, only: [:new, :create, :destroy]
    resources :users
    resources :posts do
      resources :comments, only: [:create, :destroy]
    end

    namespace :settings do
      resource :account, only: [:show, :update]
      resources :members
    end
  end
end
```

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  before_action :set_current_tenant
  before_action :authenticate_user!

  helper_method :current_account

  private

  def set_current_tenant
    subdomain = request.subdomain

    if subdomain.present?
      @current_account = Account.find_by!(subdomain: subdomain)
      ActsAsTenant.current_tenant = @current_account
    end
  rescue ActiveRecord::RecordNotFound
    redirect_to root_url(subdomain: nil), alert: "Account not found"
  end

  def current_account
    @current_account
  end

  def authenticate_user!
    redirect_to new_session_path unless user_signed_in?
  end

  def user_signed_in?
    session[:user_id].present? && current_user.present?
  end

  def current_user
    return unless session[:user_id]

    @current_user ||= User.find_by(id: session[:user_id])
  end
  helper_method :current_user
end
```

### Step 4: Account Signup Flow

```ruby
# app/controllers/accounts_controller.rb
class AccountsController < ApplicationController
  skip_before_action :set_current_tenant
  skip_before_action :authenticate_user!

  def new
    @account = Account.new
    @account.users.build
  end

  def create
    @account = Account.new(account_params)

    ActiveRecord::Base.transaction do
      if @account.save
        # Create first user as account owner
        user = @account.users.first
        user.role = "owner"
        user.save!

        # Sign in the user
        session[:user_id] = user.id

        redirect_to root_url(subdomain: @account.subdomain),
                    notice: "Welcome to #{@account.name}!"
      else
        render :new, status: :unprocessable_entity
      end
    end
  end

  private

  def account_params
    params.require(:account).permit(
      :name, :subdomain,
      users_attributes: [:name, :email, :password, :password_confirmation]
    )
  end
end
```

```erb
<!-- app/views/accounts/new.html.erb -->
<div class="max-w-md mx-auto mt-8">
  <h1 class="text-2xl font-bold mb-6">Create Your Account</h1>

  <%= form_with model: @account, url: accounts_path do |f| %>
    <%= render "shared/form_errors", model: @account %>

    <div class="mb-4">
      <%= f.label :name, "Company Name" %>
      <%= f.text_field :name, class: "w-full border rounded p-2" %>
    </div>

    <div class="mb-4">
      <%= f.label :subdomain %>
      <div class="flex items-center">
        <%= f.text_field :subdomain, class: "border rounded-l p-2" %>
        <span class="bg-gray-100 border border-l-0 rounded-r p-2">
          .yourapp.com
        </span>
      </div>
      <p class="text-sm text-gray-600">Choose your unique subdomain</p>
    </div>

    <%= f.fields_for :users, @account.users.first || @account.users.build do |user_fields| %>
      <h2 class="text-lg font-semibold mb-4">Your Account</h2>

      <div class="mb-4">
        <%= user_fields.label :name %>
        <%= user_fields.text_field :name, class: "w-full border rounded p-2" %>
      </div>

      <div class="mb-4">
        <%= user_fields.label :email %>
        <%= user_fields.email_field :email, class: "w-full border rounded p-2" %>
      </div>

      <div class="mb-4">
        <%= user_fields.label :password %>
        <%= user_fields.password_field :password, class: "w-full border rounded p-2" %>
      </div>

      <div class="mb-4">
        <%= user_fields.label :password_confirmation %>
        <%= user_fields.password_field :password_confirmation, class: "w-full border rounded p-2" %>
      </div>
    <% end %>

    <%= f.submit "Create Account", class: "w-full btn btn-primary" %>
  <% end %>
</div>
```

### Step 5: Tenant-Aware Controllers

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  before_action :set_post, only: [:show, :edit, :update, :destroy]

  def index
    # Automatically scoped to current_account
    @posts = Post.includes(:user).order(created_at: :desc)
  end

  def create
    @post = current_user.posts.build(post_params)

    if @post.save
      redirect_to @post, notice: "Post created"
    else
      render :new, status: :unprocessable_entity
    end
  end

  private

  def set_post
    # ActsAsTenant automatically scopes this query
    @post = Post.find(params[:id])
  end

  def post_params
    params.require(:post).permit(:title, :body)
  end
end
```

### Step 6: Account Settings

```ruby
# app/controllers/settings/accounts_controller.rb
class Settings::AccountsController < ApplicationController
  before_action :require_owner!

  def show
    @account = current_account
  end

  def update
    @account = current_account

    if @account.update(account_params)
      redirect_to settings_account_path, notice: "Account updated"
    else
      render :show, status: :unprocessable_entity
    end
  end

  private

  def require_owner!
    unless current_user.owner?
      redirect_to root_path, alert: "Only account owners can access this"
    end
  end

  def account_params
    params.require(:account).permit(:name, :plan)
  end
end
```

## Testing

```ruby
# spec/models/account_spec.rb
require "rails_helper"

RSpec.describe Account, type: :model do
  it "validates subdomain uniqueness" do
    create(:account, subdomain: "acme")
    duplicate = build(:account, subdomain: "acme")

    expect(duplicate).not_to be_valid
    expect(duplicate.errors[:subdomain]).to include("has already been taken")
  end

  it "rejects reserved subdomains" do
    account = build(:account, subdomain: "www")

    expect(account).not_to be_valid
    expect(account.errors[:subdomain]).to include("reserved subdomain")
  end

  it "normalizes subdomain" do
    account = create(:account, subdomain: "  ACME-Corp  ")
    expect(account.subdomain).to eq("acme-corp")
  end
end

# spec/requests/tenant_scoping_spec.rb
require "rails_helper"

RSpec.describe "Tenant scoping", type: :request do
  let(:account1) { create(:account, subdomain: "acme") }
  let(:account2) { create(:account, subdomain: "beta") }
  let(:user1) { create(:user, account: account1) }
  let(:user2) { create(:user, account: account2) }

  it "isolates data between accounts" do
    post1 = create(:post, account: account1, user: user1)
    post2 = create(:post, account: account2, user: user2)

    host! "acme.example.com"
    sign_in user1
    get posts_path

    expect(response.body).to include(post1.title)
    expect(response.body).not_to include(post2.title)
  end

  it "prevents cross-tenant access" do
    post2 = create(:post, account: account2, user: user2)

    host! "acme.example.com"
    sign_in user1

    expect {
      get post_path(post2)
    }.to raise_error(ActiveRecord::RecordNotFound)
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Manual account filtering | `Post.where(account_id: current_account.id)` | Use `acts_as_tenant` for automatic scoping |
| Forgetting indexes | Slow queries on large datasets | Add composite indexes on `[account_id, ...]` |
| Cross-tenant queries | Security vulnerability | Always use ActsAsTenant.current_tenant |
| Skipping validation | Allow invalid subdomains | Strict subdomain validation and normalization |
| Missing transaction | User created but account fails | Wrap account + user creation in transaction |

## Performance Optimizations

```ruby
# app/models/concerns/tenant_analytics.rb
module TenantAnalytics
  extend ActiveSupport::Concern

  included do
    # Counter caches for dashboard
    has_many :posts, dependent: :destroy
    has_many :users, dependent: :destroy

    # Cached counts
    def posts_count
      Rails.cache.fetch("#{cache_key}/posts_count", expires_in: 1.hour) do
        posts.count
      end
    end

    def active_users_count
      Rails.cache.fetch("#{cache_key}/active_users", expires_in: 5.minutes) do
        users.where("last_sign_in_at > ?", 30.days.ago).count
      end
    end
  end
end

# app/models/account.rb
class Account < ApplicationRecord
  include TenantAnalytics

  # Preload associations for dashboard
  scope :with_stats, -> {
    left_joins(:users, :posts)
      .select("accounts.*, COUNT(DISTINCT users.id) as users_count, COUNT(DISTINCT posts.id) as posts_count")
      .group("accounts.id")
  }
end
```

## Related Skills

- [core/structure](../../core/structure.md): App organization
- [models/associations](../../models/associations.md): Relationships
- [controllers/service-objects](../../controllers/service-objects.md): Business logic
- [auth/devise](../../auth/devise.md): Authentication
- [recipes/subscription](./subscription.md): Billing integration

## References

- [acts_as_tenant](https://github.com/ErwinM/acts_as_tenant): Row-level multitenancy
- [apartment](https://github.com/influitive/apartment): Schema-based multitenancy (alternative)
- [Rails Guide: Routing](https://guides.rubyonrails.org/routing.html#advanced-constraints)
