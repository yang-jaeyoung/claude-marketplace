---
name: rails8-controllers
description: RESTful controllers, Turbo-compatible responses (303/422 status codes), service object integration, API controller patterns. Use when writing controllers.
triggers:
  - controller
  - restful
  - status code
  - turbo response
  - strong params
  - api controller
  - error handling
  - pagination
  - 컨트롤러
  - 레스트풀
  - 상태 코드
  - 터보 응답
  - 스트롱 파람
  - API 컨트롤러
  - 에러 처리
  - 페이지네이션
summary: |
  Rails 8 컨트롤러 패턴과 응답 처리를 다룹니다. RESTful 컨트롤러, Turbo 호환
  상태 코드(303/422), 서비스 객체 통합, API 컨트롤러, 에러 처리, 페이지네이션을
  포함합니다. Turbo와의 호환성을 위해 올바른 상태 코드 사용이 필수입니다.
token_cost: high
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - basics/*.md
    - responses/*.md
  deep:
    - "**/*.md"
    - "**/*.rb"
---

# Controllers: Request Handling Patterns

## Overview

Covers Rails 8 controller patterns, Turbo-compatible response handling, and service object integration. Using correct HTTP status codes is essential for Turbo behavior.

## When to Use

- When writing RESTful controllers
- When implementing Turbo Stream responses
- When integrating with service objects
- When writing API endpoints

## Core Principles

| Principle | Description |
|-----------|-------------|
| Skinny Controller | Business logic goes to services |
| RESTful | Follow 7 standard actions |
| Turbo Compatible | Correct status codes are required |
| Explicit Responses | Handle formats with respond_to |

## Turbo-Compatible Status Codes (Required)

| Situation | Status Code | Reason |
|-----------|-------------|--------|
| Redirect after success | `status: :see_other` (303) | Turbo follows redirect as GET |
| Form errors | `status: :unprocessable_entity` (422) | Turbo replaces the form |
| Delete success | `status: :see_other` (303) | Switch from POST/DELETE to GET |

> **Important:** Incorrect status codes will break Turbo Drive behavior.

## Quick Start

## Common Patterns

For reusable service object and controller patterns, see:
- [`snippets/ruby/services/application_service.rb`](../snippets/ruby/services/application_service.rb): Service base class
- [`snippets/common/policy-base.rb`](../snippets/common/policy-base.rb): Pundit policy template

### Basic RESTful Controller

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  before_action :authenticate_user!, except: [:index, :show]
  before_action :set_post, only: [:show, :edit, :update, :destroy]
  before_action :authorize_post, only: [:edit, :update, :destroy]

  def index
    @posts = PostsQuery.new.call(filter_params)
    @pagy, @posts = pagy(@posts)
  end

  def show
  end

  def new
    @post = current_user.posts.build
  end

  def create
    result = Posts::CreateService.call(
      user: current_user,
      params: post_params
    )

    if result.success?
      redirect_to result.value, notice: "Created successfully", status: :see_other
    else
      @post = current_user.posts.build(post_params)
      @post.errors.merge!(result.errors) if result.errors.respond_to?(:each)
      render :new, status: :unprocessable_entity
    end
  end

  def edit
  end

  def update
    result = Posts::UpdateService.call(post: @post, params: post_params)

    if result.success?
      redirect_to @post, notice: "Updated successfully", status: :see_other
    else
      render :edit, status: :unprocessable_entity
    end
  end

  def destroy
    @post.destroy

    respond_to do |format|
      format.html { redirect_to posts_path, notice: "Deleted successfully", status: :see_other }
      format.turbo_stream
    end
  end

  private

  def set_post
    @post = Post.find(params[:id])
  end

  def authorize_post
    authorize @post  # Pundit
  end

  def post_params
    params.require(:post).permit(:title, :body, :published, tag_ids: [])
  end

  def filter_params
    params.permit(:status, :author_id, :q, :page)
  end
end
```

## File Structure

```
controllers/
├── SKILL.md
├── basics/
│   ├── restful.md
│   ├── strong-params.md
│   ├── filters.md
│   ├── error-handling.md
│   └── status-codes.md
├── responses/
│   ├── html.md
│   ├── turbo-stream.md
│   ├── json.md
│   └── redirects.md
├── patterns/
│   ├── service-integration.md
│   ├── form-objects.md
│   ├── pagination.md
│   ├── filtering.md
│   ├── sorting.md
│   └── namespacing.md
├── api/
│   ├── api-mode.md
│   ├── serialization.md
│   ├── versioning.md
│   └── authentication.md
└── snippets/
    ├── base_controller.rb
    ├── api_controller.rb
    └── concerns/
        ├── error_handling.rb
        └── pagination.rb
```

## Main Patterns

### Pattern 1: Turbo Stream Response

```ruby
# Controller
def create
  @message = current_user.messages.create(message_params)

  respond_to do |format|
    format.turbo_stream
    format.html { redirect_to messages_path }
  end
end

def destroy
  @post.destroy

  respond_to do |format|
    format.turbo_stream
    format.html { redirect_to posts_path, status: :see_other }
  end
end
```

```erb
<!-- app/views/messages/create.turbo_stream.erb -->
<%= turbo_stream.prepend "messages", @message %>
<%= turbo_stream.update "message_count", Message.count %>
<%= turbo_stream.update "flash", partial: "shared/flash" %>
<%= turbo_stream.update "message_form" do %>
  <%= render "form", message: Message.new %>
<% end %>

<!-- app/views/posts/destroy.turbo_stream.erb -->
<%= turbo_stream.remove @post %>
<%= turbo_stream.update "posts_count", Post.count %>
```

### Pattern 2: Service Object Integration

```ruby
# app/services/posts/create_service.rb
module Posts
  class CreateService < ApplicationService
    def initialize(user:, params:)
      @user = user
      @params = params
    end

    def call
      post = @user.posts.build(@params)

      if post.save
        notify_followers(post)
        Result.success(post)
      else
        Result.failure(post.errors)
      end
    end

    private

    def notify_followers(post)
      NotifyFollowersJob.perform_later(post.id)
    end
  end
end

# Usage in controller
def create
  result = Posts::CreateService.call(
    user: current_user,
    params: post_params
  )

  if result.success?
    respond_to do |format|
      format.html { redirect_to result.value, notice: "Created successfully", status: :see_other }
      format.turbo_stream { @post = result.value }
    end
  else
    @post = current_user.posts.build(post_params)
    flash.now[:alert] = "Save failed"
    render :new, status: :unprocessable_entity
  end
end
```

### Pattern 3: Error Handling Concern

```ruby
# app/controllers/concerns/error_handling.rb
module ErrorHandling
  extend ActiveSupport::Concern

  included do
    rescue_from ActiveRecord::RecordNotFound, with: :not_found
    rescue_from Pundit::NotAuthorizedError, with: :forbidden
    rescue_from ActionController::ParameterMissing, with: :bad_request
  end

  private

  def not_found
    respond_to do |format|
      format.html { render "errors/not_found", status: :not_found }
      format.json { render json: { error: "Not found" }, status: :not_found }
      format.turbo_stream { render turbo_stream: turbo_stream.update("flash", partial: "shared/flash", locals: { alert: "Not found" }) }
    end
  end

  def forbidden
    respond_to do |format|
      format.html { redirect_to root_path, alert: "You don't have permission" }
      format.json { render json: { error: "Forbidden" }, status: :forbidden }
    end
  end

  def bad_request(exception)
    respond_to do |format|
      format.html { redirect_back fallback_location: root_path, alert: exception.message }
      format.json { render json: { error: exception.message }, status: :bad_request }
    end
  end
end

# Include in ApplicationController
class ApplicationController < ActionController::Base
  include ErrorHandling
  include Pagy::Backend
end
```

### Pattern 4: Pagination

```ruby
# Gemfile
gem "pagy"

# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  include Pagy::Backend

  def index
    @pagy, @posts = pagy(
      PostsQuery.new.call(filter_params),
      items: 20
    )
  end
end

# app/helpers/application_helper.rb
module ApplicationHelper
  include Pagy::Frontend
end
```

```erb
<!-- app/views/posts/index.html.erb -->
<div id="posts">
  <%= render @posts %>
</div>

<%== pagy_nav(@pagy) %>

<!-- Or infinite scroll -->
<% if @pagy.next %>
  <%= turbo_frame_tag "page_#{@pagy.next}",
                      src: posts_path(page: @pagy.next, **filter_params),
                      loading: :lazy %>
<% end %>
```

### Pattern 5: Namespaced Controller

```ruby
# config/routes.rb
Rails.application.routes.draw do
  namespace :admin do
    resources :posts
    resources :users
    root to: "dashboard#index"
  end

  namespace :api do
    namespace :v1 do
      resources :posts, only: [:index, :show, :create]
    end
  end
end

# app/controllers/admin/base_controller.rb
module Admin
  class BaseController < ApplicationController
    before_action :authenticate_user!
    before_action :require_admin

    layout "admin"

    private

    def require_admin
      redirect_to root_path, alert: "Admin access only" unless current_user.admin?
    end
  end
end

# app/controllers/admin/posts_controller.rb
module Admin
  class PostsController < BaseController
    def index
      @posts = Post.includes(:user).order(created_at: :desc)
      @pagy, @posts = pagy(@posts)
    end
  end
end
```

### Pattern 6: API Controller

```ruby
# app/controllers/api/v1/base_controller.rb
module Api
  module V1
    class BaseController < ActionController::API
      include ActionController::HttpAuthentication::Token::ControllerMethods

      before_action :authenticate_api_user!

      private

      def authenticate_api_user!
        authenticate_or_request_with_http_token do |token, _options|
          @current_api_user = User.find_by(api_token: token)
        end
      end

      def current_api_user
        @current_api_user
      end
    end
  end
end

# app/controllers/api/v1/posts_controller.rb
module Api
  module V1
    class PostsController < BaseController
      def index
        posts = PostsQuery.new(Post.published).call(filter_params)
        render json: posts, each_serializer: PostSerializer
      end

      def show
        post = Post.published.find(params[:id])
        render json: post, serializer: PostSerializer
      end

      def create
        result = Posts::CreateService.call(
          user: current_api_user,
          params: post_params
        )

        if result.success?
          render json: result.value, serializer: PostSerializer, status: :created
        else
          render json: { errors: result.errors }, status: :unprocessable_entity
        end
      end

      private

      def post_params
        params.require(:post).permit(:title, :body, :published)
      end

      def filter_params
        params.permit(:status, :q, :page, :per_page)
      end
    end
  end
end
```

## Service Integration Response by Result

| Result | HTML Response | Turbo Stream Response |
|--------|---------------|----------------------|
| Success | `redirect_to ..., status: :see_other` | Render turbo_stream template |
| Failure | `render :form, status: :unprocessable_entity` | Show errors via turbo_stream |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Fat Controller | Hard to test/reuse | Extract to service objects |
| Missing status code | Turbo behavior fails | Specify 303, 422 explicitly |
| Duplicate code | Hard to maintain | Extract to concerns |
| Missing Strong Params | Security vulnerability | Always use permit |

## Related Skills

- [core/patterns](../core/patterns/): Service/form objects
- [hotwire](../hotwire/SKILL.md): Turbo Stream details
- [models](../models/SKILL.md): Query objects

## References

- [Action Controller Overview](https://guides.rubyonrails.org/action_controller_overview.html)
- [Rails Routing](https://guides.rubyonrails.org/routing.html)
- [Working with Turbo](https://turbo.hotwired.dev/handbook/introduction)
