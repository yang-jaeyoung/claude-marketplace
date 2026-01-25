# API Token Authentication

## Overview

Implementing token-based authentication for APIs using Rails' `has_secure_token`, covering token generation, validation, scoping, rate limiting, and revocation.

## When to Use

- When building REST APIs for third-party integrations
- When mobile apps need to authenticate
- When implementing personal access tokens (like GitHub)
- When services need machine-to-machine authentication
- When webhook authentication is needed

## Quick Start

```ruby
# Migration
rails g migration AddApiTokenToUsers api_token:string:uniq

# Model
class User < ApplicationRecord
  has_secure_token :api_token
end

# Controller
class Api::BaseController < ActionController::API
  before_action :authenticate_token!

  def authenticate_token!
    token = request.headers["Authorization"]&.split(" ")&.last
    @current_user = User.find_by(api_token: token)
    render json: { error: "Unauthorized" }, status: :unauthorized unless @current_user
  end
end
```

## Main Patterns

### Pattern 1: Basic Token Setup

```ruby
# db/migrate/xxx_add_api_token_to_users.rb
class AddApiTokenToUsers < ActiveRecord::Migration[8.0]
  def change
    add_column :users, :api_token, :string
    add_index :users, :api_token, unique: true
  end
end
```

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_secure_token :api_token

  def regenerate_api_token!
    regenerate_api_token
  end
end
```

### Pattern 2: Dedicated API Token Model

```ruby
# db/migrate/xxx_create_api_tokens.rb
class CreateApiTokens < ActiveRecord::Migration[8.0]
  def change
    create_table :api_tokens do |t|
      t.references :user, null: false, foreign_key: true
      t.string :token_digest, null: false
      t.string :name, null: false
      t.text :scopes, default: [], array: true
      t.datetime :last_used_at
      t.datetime :expires_at
      t.string :last_used_ip
      t.datetime :revoked_at

      t.timestamps
    end

    add_index :api_tokens, :token_digest, unique: true
  end
end
```

```ruby
# app/models/api_token.rb
class ApiToken < ApplicationRecord
  belongs_to :user

  SCOPES = %w[read write delete admin].freeze

  validates :name, presence: true
  validates :scopes, presence: true
  validate :scopes_are_valid

  scope :active, -> { where(revoked_at: nil).where("expires_at IS NULL OR expires_at > ?", Time.current) }
  scope :expired, -> { where("expires_at <= ?", Time.current) }
  scope :revoked, -> { where.not(revoked_at: nil) }

  # Generate token and return plain value (only available at creation)
  def self.generate_token(user:, name:, scopes: ["read"], expires_in: nil)
    plain_token = SecureRandom.hex(32)

    token = create!(
      user: user,
      name: name,
      token_digest: Digest::SHA256.hexdigest(plain_token),
      scopes: scopes,
      expires_at: expires_in ? Time.current + expires_in : nil
    )

    # Return token object with plain token accessible
    token.instance_variable_set(:@plain_token, plain_token)
    token.define_singleton_method(:plain_token) { @plain_token }
    token
  end

  def self.find_by_token(plain_token)
    return nil if plain_token.blank?

    digest = Digest::SHA256.hexdigest(plain_token)
    active.find_by(token_digest: digest)
  end

  def active?
    revoked_at.nil? && (expires_at.nil? || expires_at.future?)
  end

  def revoke!
    update!(revoked_at: Time.current)
  end

  def record_usage!(ip:)
    update_columns(last_used_at: Time.current, last_used_ip: ip)
  end

  def can?(scope)
    scopes.include?(scope.to_s) || scopes.include?("admin")
  end

  private

  def scopes_are_valid
    invalid = scopes - SCOPES
    errors.add(:scopes, "contains invalid scope: #{invalid.join(', ')}") if invalid.any?
  end
end
```

### Pattern 3: API Base Controller

```ruby
# app/controllers/api/v1/base_controller.rb
module Api
  module V1
    class BaseController < ActionController::API
      include ActionController::HttpAuthentication::Token::ControllerMethods

      before_action :authenticate_token!
      before_action :set_default_format

      attr_reader :current_user, :current_token

      private

      def authenticate_token!
        authenticate_with_http_token do |token, options|
          @current_token = ApiToken.find_by_token(token)

          if @current_token
            @current_token.record_usage!(ip: request.remote_ip)
            @current_user = @current_token.user
            return true
          end
        end

        render_unauthorized
      end

      def render_unauthorized
        render json: {
          error: "unauthorized",
          message: "Invalid or missing API token"
        }, status: :unauthorized
      end

      def require_scope(scope)
        unless current_token.can?(scope)
          render json: {
            error: "forbidden",
            message: "Token doesn't have required scope: #{scope}"
          }, status: :forbidden
        end
      end

      def set_default_format
        request.format = :json
      end
    end
  end
end
```

### Pattern 4: Token Management Controller

```ruby
# app/controllers/api_tokens_controller.rb
class ApiTokensController < ApplicationController
  before_action :authenticate_user!
  before_action :set_token, only: [:show, :destroy]

  def index
    @tokens = current_user.api_tokens.order(created_at: :desc)
  end

  def new
    @token = current_user.api_tokens.build
  end

  def create
    @token = ApiToken.generate_token(
      user: current_user,
      name: token_params[:name],
      scopes: token_params[:scopes] || ["read"],
      expires_in: parse_expiration(token_params[:expires_in])
    )

    if @token.persisted?
      # Show token once - user must copy it
      @plain_token = @token.plain_token
      render :show_new_token
    else
      render :new, status: :unprocessable_entity
    end
  end

  def destroy
    @token.revoke!
    redirect_to api_tokens_path, notice: "Token revoked"
  end

  private

  def set_token
    @token = current_user.api_tokens.find(params[:id])
  end

  def token_params
    params.require(:api_token).permit(:name, :expires_in, scopes: [])
  end

  def parse_expiration(value)
    case value
    when "30_days" then 30.days
    when "90_days" then 90.days
    when "1_year" then 1.year
    else nil  # Never expires
    end
  end
end
```

### Pattern 5: Rate Limiting

```ruby
# app/controllers/concerns/api_rate_limiter.rb
module ApiRateLimiter
  extend ActiveSupport::Concern

  included do
    before_action :check_rate_limit
  end

  private

  def check_rate_limit
    key = rate_limit_key
    count = Rails.cache.increment(key, 1, expires_in: rate_limit_period)

    if count > rate_limit_max
      render json: {
        error: "rate_limited",
        message: "Rate limit exceeded. Try again in #{time_until_reset} seconds.",
        retry_after: time_until_reset
      }, status: :too_many_requests
    else
      # Add rate limit headers
      response.headers["X-RateLimit-Limit"] = rate_limit_max.to_s
      response.headers["X-RateLimit-Remaining"] = [rate_limit_max - count, 0].max.to_s
      response.headers["X-RateLimit-Reset"] = rate_limit_reset_time.to_i.to_s
    end
  end

  def rate_limit_key
    "api_rate:#{current_token&.id || request.remote_ip}:#{rate_limit_period_key}"
  end

  def rate_limit_period_key
    Time.current.strftime("%Y%m%d%H%M").to_i / 5  # 5-minute windows
  end

  def rate_limit_max
    current_token&.user&.premium? ? 1000 : 100  # Requests per 5 minutes
  end

  def rate_limit_period
    5.minutes
  end

  def rate_limit_reset_time
    next_period = ((Time.current.to_i / 300) + 1) * 300
    Time.at(next_period)
  end

  def time_until_reset
    (rate_limit_reset_time - Time.current).to_i
  end
end

# Usage
class Api::V1::BaseController < ActionController::API
  include ApiRateLimiter
end
```

### Pattern 6: Scoped Authorization

```ruby
# app/controllers/api/v1/posts_controller.rb
module Api
  module V1
    class PostsController < BaseController
      before_action :require_read_scope, only: [:index, :show]
      before_action :require_write_scope, only: [:create, :update]
      before_action :require_delete_scope, only: [:destroy]

      def index
        @posts = Post.where(user: current_user).page(params[:page])
        render json: @posts
      end

      def create
        @post = current_user.posts.build(post_params)

        if @post.save
          render json: @post, status: :created
        else
          render json: { errors: @post.errors }, status: :unprocessable_entity
        end
      end

      def destroy
        @post = current_user.posts.find(params[:id])
        @post.destroy
        head :no_content
      end

      private

      def require_read_scope
        require_scope(:read)
      end

      def require_write_scope
        require_scope(:write)
      end

      def require_delete_scope
        require_scope(:delete)
      end

      def post_params
        params.require(:post).permit(:title, :body)
      end
    end
  end
end
```

### Pattern 7: Token Display UI

```erb
<%# app/views/api_tokens/index.html.erb %>
<div class="max-w-4xl mx-auto py-8">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-2xl font-bold">API Tokens</h1>
    <%= link_to "New Token", new_api_token_path,
        class: "px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700" %>
  </div>

  <div class="bg-white shadow rounded-lg divide-y">
    <% @tokens.each do |token| %>
      <div class="p-4 flex items-center justify-between">
        <div>
          <h3 class="font-medium"><%= token.name %></h3>
          <div class="text-sm text-gray-500 space-x-4">
            <span>Scopes: <%= token.scopes.join(", ") %></span>
            <span>
              <% if token.last_used_at %>
                Last used <%= time_ago_in_words(token.last_used_at) %> ago
              <% else %>
                Never used
              <% end %>
            </span>
            <% if token.expires_at %>
              <span class="<%= token.expires_at.past? ? 'text-red-600' : '' %>">
                <%= token.expires_at.past? ? 'Expired' : 'Expires' %>
                <%= time_ago_in_words(token.expires_at) %> <%= token.expires_at.past? ? 'ago' : 'from now' %>
              </span>
            <% end %>
          </div>
        </div>

        <% if token.active? %>
          <%= button_to "Revoke", api_token_path(token),
              method: :delete,
              data: { turbo_confirm: "Are you sure? This cannot be undone." },
              class: "px-3 py-1 text-red-600 hover:bg-red-50 rounded" %>
        <% else %>
          <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded text-sm">
            <%= token.revoked_at ? 'Revoked' : 'Expired' %>
          </span>
        <% end %>
      </div>
    <% end %>
  </div>
</div>
```

```erb
<%# app/views/api_tokens/show_new_token.html.erb %>
<div class="max-w-lg mx-auto py-8">
  <h1 class="text-2xl font-bold mb-6">Your New API Token</h1>

  <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
    <p class="text-yellow-800">
      <strong>Important:</strong> Copy your token now. You won't be able to see it again.
    </p>
  </div>

  <div class="bg-white shadow rounded-lg p-6">
    <label class="block text-sm font-medium text-gray-700 mb-2">API Token</label>
    <div class="flex">
      <input type="text"
             value="<%= @plain_token %>"
             readonly
             class="flex-1 rounded-l-md border-gray-300 bg-gray-50 font-mono text-sm"
             id="token-value">
      <button onclick="copyToken()"
              class="px-4 py-2 bg-gray-800 text-white rounded-r-md hover:bg-gray-700">
        Copy
      </button>
    </div>

    <div class="mt-4">
      <h3 class="font-medium mb-2">Usage Example</h3>
      <pre class="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
curl -H "Authorization: Bearer <%= @plain_token %>" \
     https://api.yourapp.com/v1/posts</pre>
    </div>
  </div>

  <div class="mt-6">
    <%= link_to "Back to Tokens", api_tokens_path,
        class: "text-indigo-600 hover:text-indigo-500" %>
  </div>
</div>

<script>
function copyToken() {
  const input = document.getElementById('token-value');
  input.select();
  document.execCommand('copy');
  alert('Token copied to clipboard');
}
</script>
```

### Pattern 8: Webhook Token Authentication

```ruby
# app/controllers/webhooks_controller.rb
class WebhooksController < ApplicationController
  skip_before_action :verify_authenticity_token
  before_action :verify_webhook_signature

  def receive
    payload = JSON.parse(request.body.read)

    WebhookProcessor.perform_later(
      event: payload["event"],
      data: payload["data"]
    )

    head :ok
  end

  private

  def verify_webhook_signature
    signature = request.headers["X-Webhook-Signature"]
    payload = request.body.read

    expected = OpenSSL::HMAC.hexdigest(
      "SHA256",
      Rails.application.credentials.webhook_secret,
      payload
    )

    unless ActiveSupport::SecurityUtils.secure_compare(signature.to_s, expected)
      render json: { error: "Invalid signature" }, status: :unauthorized
    end

    request.body.rewind
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Storing plain tokens | Token theft | Store hashed/digested tokens |
| No expiration option | Stale tokens accumulate | Offer expiration options |
| No revocation | Can't disable compromised tokens | Implement revoke feature |
| No rate limiting | API abuse | Implement rate limits |
| Token in URL | Token logged in access logs | Use Authorization header |

## Related Skills

- [../devise/setup.md](../devise/setup.md): User authentication
- [two-factor.md](./two-factor.md): Additional security
- [../../controllers/SKILL.md](../../controllers/SKILL.md): Controller patterns

## References

- [has_secure_token](https://api.rubyonrails.org/classes/ActiveRecord/SecureToken/ClassMethods.html)
- [HTTP Token Authentication](https://api.rubyonrails.org/classes/ActionController/HttpAuthentication/Token.html)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)
