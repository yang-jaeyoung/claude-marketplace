# Request Specs

## Overview
Request specs test HTTP endpoints including routing, authentication, authorization, response formats, and Turbo Stream responses.

## When to Use
- Testing controller actions and responses
- Verifying authentication/authorization
- Testing API endpoints (JSON responses)
- Testing Turbo Stream responses
- Verifying redirects and status codes

## Quick Start
```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  let(:user) { create(:user) }

  describe "GET /posts" do
    it "returns success" do
      get posts_path
      expect(response).to have_http_status(:success)
    end
  end

  describe "POST /posts" do
    before { sign_in user }

    it "creates a post" do
      expect {
        post posts_path, params: { post: attributes_for(:post) }
      }.to change(Post, :count).by(1)
    end
  end
end
```

## Common Setup

For standard RSpec configuration including Factory Bot, Devise helpers, and Turbo Stream test helpers, see:
- [`snippets/common/rspec-setup.rb`](../../snippets/common/rspec-setup.rb): RSpec configuration
- [`snippets/common/factory-base.rb`](../../snippets/common/factory-base.rb): FactoryBot patterns

## Main Patterns

### Pattern 1: Testing CRUD Actions
```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  let(:user) { create(:user) }
  let(:post_record) { create(:post, user: user) }

  describe "GET /posts" do
    before { create_list(:post, 3, :published) }

    it "returns successful response" do
      get posts_path
      expect(response).to have_http_status(:ok)
    end

    it "renders index template" do
      get posts_path
      expect(response).to render_template(:index)
    end
  end

  describe "GET /posts/:id" do
    it "returns the post" do
      get post_path(post_record)
      expect(response).to have_http_status(:ok)
      expect(response.body).to include(post_record.title)
    end

    context "when post not found" do
      it "returns 404" do
        get post_path(id: 'nonexistent')
        expect(response).to have_http_status(:not_found)
      end
    end
  end

  describe "POST /posts" do
    let(:valid_params) { { post: attributes_for(:post) } }
    let(:invalid_params) { { post: { title: "" } } }

    context "when not signed in" do
      it "redirects to login" do
        post posts_path, params: valid_params
        expect(response).to redirect_to(new_session_path)
      end
    end

    context "when signed in" do
      before { sign_in user }

      context "with valid params" do
        it "creates a post" do
          expect {
            post posts_path, params: valid_params
          }.to change(Post, :count).by(1)
        end

        it "redirects to post show page" do
          post posts_path, params: valid_params
          expect(response).to redirect_to(Post.last)
        end

        it "sets flash notice" do
          post posts_path, params: valid_params
          expect(flash[:notice]).to eq("Post was successfully created.")
        end
      end

      context "with invalid params" do
        it "does not create a post" do
          expect {
            post posts_path, params: invalid_params
          }.not_to change(Post, :count)
        end

        it "returns unprocessable_entity status" do
          post posts_path, params: invalid_params
          expect(response).to have_http_status(:unprocessable_entity)
        end

        it "renders new template" do
          post posts_path, params: invalid_params
          expect(response).to render_template(:new)
        end
      end
    end
  end

  describe "PATCH /posts/:id" do
    before { sign_in user }

    context "with valid params" do
      it "updates the post" do
        patch post_path(post_record), params: { post: { title: "Updated Title" } }
        expect(post_record.reload.title).to eq("Updated Title")
      end

      it "redirects to post" do
        patch post_path(post_record), params: { post: { title: "Updated" } }
        expect(response).to redirect_to(post_record)
      end
    end

    context "with invalid params" do
      it "does not update the post" do
        original_title = post_record.title
        patch post_path(post_record), params: { post: { title: "" } }
        expect(post_record.reload.title).to eq(original_title)
      end

      it "returns unprocessable_entity" do
        patch post_path(post_record), params: { post: { title: "" } }
        expect(response).to have_http_status(:unprocessable_entity)
      end
    end
  end

  describe "DELETE /posts/:id" do
    before { sign_in user }

    it "destroys the post" do
      post_record  # Create the post
      expect {
        delete post_path(post_record)
      }.to change(Post, :count).by(-1)
    end

    it "redirects to posts index" do
      delete post_path(post_record)
      expect(response).to redirect_to(posts_path)
    end
  end
end
```

### Pattern 2: Testing Authentication
```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  let(:user) { create(:user) }

  describe "authentication" do
    context "when not signed in" do
      it "redirects to login for new" do
        get new_post_path
        expect(response).to redirect_to(new_session_path)
      end

      it "redirects to login for create" do
        post posts_path, params: { post: attributes_for(:post) }
        expect(response).to redirect_to(new_session_path)
      end
    end

    context "when signed in" do
      before { sign_in user }

      it "allows access to new" do
        get new_post_path
        expect(response).to have_http_status(:ok)
      end

      it "allows post creation" do
        post posts_path, params: { post: attributes_for(:post) }
        expect(response).to have_http_status(:redirect)
      end
    end
  end
end
```

### Pattern 3: Testing Authorization (Pundit)
```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  let(:user) { create(:user) }
  let(:other_user) { create(:user) }
  let(:admin) { create(:user, :admin) }
  let(:post_record) { create(:post, user: user) }

  describe "authorization" do
    describe "PATCH /posts/:id" do
      context "as owner" do
        before { sign_in user }

        it "allows update" do
          patch post_path(post_record), params: { post: { title: "Updated" } }
          expect(response).to have_http_status(:redirect)
        end
      end

      context "as other user" do
        before { sign_in other_user }

        it "denies update" do
          patch post_path(post_record), params: { post: { title: "Updated" } }
          expect(response).to have_http_status(:forbidden)
        end
      end

      context "as admin" do
        before { sign_in admin }

        it "allows update" do
          patch post_path(post_record), params: { post: { title: "Updated" } }
          expect(response).to have_http_status(:redirect)
        end
      end
    end
  end
end
```

### Pattern 4: Testing Turbo Stream Responses
```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  let(:user) { create(:user) }

  before { sign_in user }

  describe "POST /posts" do
    let(:headers) { { "Accept" => "text/vnd.turbo-stream.html" } }

    it "responds with turbo_stream format" do
      post posts_path,
           params: { post: attributes_for(:post) },
           headers: headers

      expect(response.media_type).to eq("text/vnd.turbo-stream.html")
    end

    it "includes turbo-stream tags" do
      post posts_path,
           params: { post: attributes_for(:post) },
           headers: headers

      expect(response.body).to include('<turbo-stream')
      expect(response.body).to include('action="append"')
      expect(response.body).to include('target="posts"')
    end

    it "appends the new post" do
      post posts_path,
           params: { post: attributes_for(:post, title: "New Post") },
           headers: headers

      expect(response.body).to include("New Post")
    end
  end

  describe "DELETE /posts/:id" do
    let!(:post_record) { create(:post, user: user) }
    let(:headers) { { "Accept" => "text/vnd.turbo-stream.html" } }

    it "responds with turbo_stream remove action" do
      delete post_path(post_record), headers: headers

      expect(response.media_type).to eq("text/vnd.turbo-stream.html")
      expect(response.body).to include('action="remove"')
      expect(response.body).to include("target=\"#{dom_id(post_record)}\"")
    end
  end
end
```

### Pattern 5: Testing JSON API Responses
```ruby
# spec/requests/api/posts_spec.rb
require 'rails_helper'

RSpec.describe "API::Posts", type: :request do
  let(:user) { create(:user) }
  let(:headers) { { "Authorization" => "Bearer #{user.api_token}" } }

  describe "GET /api/posts" do
    let!(:posts) { create_list(:post, 3, :published) }

    it "returns posts as JSON" do
      get api_posts_path, headers: headers

      expect(response).to have_http_status(:ok)
      expect(response.content_type).to match(/application\/json/)
    end

    it "returns correct structure" do
      get api_posts_path, headers: headers

      json = JSON.parse(response.body)
      expect(json).to have_key("posts")
      expect(json["posts"].size).to eq(3)
    end
  end

  describe "POST /api/posts" do
    let(:valid_params) do
      { post: { title: "API Post", body: "Content" } }
    end

    context "with valid params" do
      it "creates a post" do
        expect {
          post api_posts_path, params: valid_params, headers: headers
        }.to change(Post, :count).by(1)
      end

      it "returns created status" do
        post api_posts_path, params: valid_params, headers: headers
        expect(response).to have_http_status(:created)
      end

      it "returns post JSON" do
        post api_posts_path, params: valid_params, headers: headers

        json = JSON.parse(response.body)
        expect(json["post"]["title"]).to eq("API Post")
      end
    end

    context "with invalid params" do
      let(:invalid_params) { { post: { title: "" } } }

      it "returns unprocessable_entity" do
        post api_posts_path, params: invalid_params, headers: headers
        expect(response).to have_http_status(:unprocessable_entity)
      end

      it "returns errors" do
        post api_posts_path, params: invalid_params, headers: headers

        json = JSON.parse(response.body)
        expect(json).to have_key("errors")
      end
    end
  end
end
```

### Pattern 6: Testing Query Parameters and Filters
```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  describe "GET /posts" do
    let!(:published) { create(:post, :published) }
    let!(:draft) { create(:post, published: false) }

    it "filters by status" do
      get posts_path, params: { status: 'published' }

      expect(response).to have_http_status(:ok)
      expect(response.body).to include(published.title)
      expect(response.body).not_to include(draft.title)
    end

    it "searches by title" do
      get posts_path, params: { q: published.title }

      expect(response.body).to include(published.title)
      expect(response.body).not_to include(draft.title)
    end

    it "paginates results" do
      create_list(:post, 30)
      get posts_path, params: { page: 2 }

      expect(response).to have_http_status(:ok)
    end
  end
end
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Testing view logic in request specs | Slow, brittle | Use system specs for view interactions |
| Not using `let` for shared setup | Duplicated code | Use `let` or `let!` for test data |
| Hardcoding URLs | Brittle tests | Use path helpers (`posts_path`) |
| Not testing edge cases | Bugs in production | Test invalid params, missing records |
| Testing private methods | Implementation coupling | Test public interface only |

## Related Skills
- [Models](./models.md): Testing models
- [System Tests](./system.md): End-to-end testing
- [Turbo Testing](../patterns/turbo.md): Turbo-specific tests

## References
- [RSpec Request Specs](https://rspec.info/features/6-0/rspec-rails/request-specs/)
- [Rails Testing Guide](https://guides.rubyonrails.org/testing.html#integration-testing)
- [HTTP Status Codes](https://httpstatuses.com/)
