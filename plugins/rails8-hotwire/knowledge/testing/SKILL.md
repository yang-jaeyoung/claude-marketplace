---
name: rails8-testing
description: RSpec, Factory Bot, system tests, Turbo/Stimulus testing. Use for TDD, regression testing, and CI/CD pipeline setup.
triggers:
  - test
  - rspec
  - factory bot
  - capybara
  - system test
  - tdd
  - integration test
  - unit test
  - spec
  - 테스트
  - 알스펙
  - 팩토리 봇
  - 카피바라
  - 시스템 테스트
  - TDD
  - 통합 테스트
  - 단위 테스트
summary: |
  Rails 8 애플리케이션의 테스트 전략을 다룹니다. RSpec, Factory Bot, Capybara,
  시스템 테스트, Turbo/Stimulus 테스팅 패턴을 포함합니다. TDD, 회귀 테스트,
  CI/CD 파이프라인 구축 시 참조하세요.
token_cost: high
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - setup/*.md
    - types/*.md
  deep:
    - "**/*.md"
    - "**/*.rb"
---

# Testing: Testing Strategy

## Overview

Covers testing strategy for Rails 8 applications. Includes RSpec, Factory Bot, system tests, and Turbo/Stimulus testing patterns.

## When to Use

- When developing new features (TDD)
- When fixing bugs (regression tests)
- When refactoring (safety net)
- When building CI/CD pipelines

## Core Principles

| Principle | Description |
|-----------|-------------|
| Test Pyramid | Unit > Integration > E2E |
| Fast Feedback | Prioritize fast tests |
| Isolation | Ensure independence between tests |
| Readability | Tests serve as documentation |

## Quick Start

### RSpec Setup

```bash
# Gemfile
group :development, :test do
  gem "rspec-rails"
  gem "factory_bot_rails"
  gem "faker"
end

group :test do
  gem "capybara"
  gem "cuprite"  # Chrome driver (30% faster)
  gem "shoulda-matchers"
  gem "webmock"
  gem "vcr"
end

# Installation
bundle install
rails generate rspec:install
```

```ruby
# spec/rails_helper.rb
require 'spec_helper'
ENV['RAILS_ENV'] ||= 'test'
require_relative '../config/environment'
abort("The Rails environment is running in production mode!") if Rails.env.production?
require 'rspec/rails'

Dir[Rails.root.join('spec', 'support', '**', '*.rb')].sort.each { |f| require f }

RSpec.configure do |config|
  config.fixture_path = Rails.root.join('spec/fixtures')
  config.use_transactional_fixtures = true
  config.infer_spec_type_from_file_location!
  config.filter_rails_from_backtrace!

  config.include FactoryBot::Syntax::Methods
  config.include Devise::Test::IntegrationHelpers, type: :request
  config.include Devise::Test::IntegrationHelpers, type: :system
end

Shoulda::Matchers.configure do |config|
  config.integrate do |with|
    with.test_framework :rspec
    with.library :rails
  end
end
```

## File Structure

```
testing/
├── SKILL.md
├── setup/
│   ├── rspec.md
│   ├── factory-bot.md
│   ├── faker.md
│   └── database-cleaner.md
├── types/
│   ├── models.md
│   ├── requests.md
│   ├── system.md
│   ├── services.md
│   ├── policies.md
│   └── jobs.md
├── patterns/
│   ├── factories.md
│   ├── shared-examples.md
│   ├── mocking.md
│   └── turbo.md
└── snippets/
    ├── rails_helper.rb
    ├── support/
    │   ├── devise.rb
    │   ├── pundit.rb
    │   └── turbo.rb
    └── factories/
        └── users.rb
```

## Main Patterns

### Pattern 1: Model Tests

```ruby
# spec/models/post_spec.rb
require 'rails_helper'

RSpec.describe Post, type: :model do
  describe 'associations' do
    it { should belong_to(:user) }
    it { should have_many(:comments).dependent(:destroy) }
    it { should have_many(:tags).through(:taggings) }
  end

  describe 'validations' do
    it { should validate_presence_of(:title) }
    it { should validate_length_of(:title).is_at_most(200) }
    it { should validate_presence_of(:body) }

    context 'uniqueness' do
      subject { create(:post) }
      it { should validate_uniqueness_of(:slug).allow_nil }
    end
  end

  describe 'scopes' do
    let!(:published_post) { create(:post, published: true) }
    let!(:draft_post) { create(:post, published: false) }

    describe '.published' do
      it 'returns only published posts' do
        expect(Post.published).to include(published_post)
        expect(Post.published).not_to include(draft_post)
      end
    end

    describe '.recent' do
      let!(:old_post) { create(:post, created_at: 1.week.ago) }
      let!(:new_post) { create(:post, created_at: 1.hour.ago) }

      it 'returns posts in descending order' do
        expect(Post.recent.first).to eq(new_post)
      end
    end
  end

  describe '#generate_slug' do
    it 'generates slug from title on save' do
      post = create(:post, title: 'Hello World', slug: nil)
      expect(post.slug).to eq('hello-world')
    end

    it 'does not override existing slug' do
      post = create(:post, title: 'Hello World', slug: 'custom-slug')
      expect(post.slug).to eq('custom-slug')
    end
  end
end
```

### Pattern 2: Request Tests

```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  let(:user) { create(:user) }
  let(:post_record) { create(:post, user: user) }

  describe "GET /posts" do
    before { create_list(:post, 3, published: true) }

    it "returns published posts" do
      get posts_path
      expect(response).to have_http_status(:success)
      expect(response.body).to include("Post")
    end
  end

  describe "GET /posts/:id" do
    context "when post is published" do
      let(:post_record) { create(:post, published: true) }

      it "returns the post" do
        get post_path(post_record)
        expect(response).to have_http_status(:success)
      end
    end

    context "when post is draft" do
      let(:post_record) { create(:post, published: false) }

      it "returns 404 for guest" do
        get post_path(post_record)
        expect(response).to have_http_status(:not_found)
      end

      it "returns 200 for owner" do
        sign_in post_record.user
        get post_path(post_record)
        expect(response).to have_http_status(:success)
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

      it "creates a post with valid params" do
        expect {
          post posts_path, params: valid_params
        }.to change(Post, :count).by(1)

        expect(response).to redirect_to(Post.last)
      end

      it "returns 422 with invalid params" do
        post posts_path, params: invalid_params
        expect(response).to have_http_status(:unprocessable_entity)
      end
    end
  end

  describe "Turbo Stream responses" do
    before { sign_in user }

    it "responds with turbo_stream on create" do
      post posts_path,
           params: { post: attributes_for(:post) },
           headers: { "Accept" => "text/vnd.turbo-stream.html" }

      expect(response.media_type).to eq("text/vnd.turbo-stream.html")
    end

    it "responds with turbo_stream on destroy" do
      delete post_path(post_record),
             headers: { "Accept" => "text/vnd.turbo-stream.html" }

      expect(response.media_type).to eq("text/vnd.turbo-stream.html")
      expect(response.body).to include("turbo-stream")
    end
  end
end
```

### Pattern 3: System (E2E) Tests

```ruby
# spec/system/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :system do
  let(:user) { create(:user) }

  before do
    driven_by(:cuprite)
  end

  describe "Creating a post" do
    before { sign_in user }

    it "creates a new post with Turbo" do
      visit new_post_path

      fill_in "Title", with: "My New Post"
      fill_in "Body", with: "This is the content"
      check "Published"

      click_button "Create Post"

      expect(page).to have_content("My New Post")
      expect(page).to have_current_path(post_path(Post.last))
    end

    it "shows validation errors" do
      visit new_post_path

      click_button "Create Post"

      expect(page).to have_content("Title can't be blank")
      expect(page).to have_current_path(posts_path)
    end
  end

  describe "Inline editing" do
    let!(:post_record) { create(:post, user: user) }

    before { sign_in user }

    it "edits post inline with Turbo Frame" do
      visit post_path(post_record)

      within("##{dom_id(post_record)}") do
        click_link "Edit"
      end

      # Form loads within Turbo Frame
      expect(page).to have_field("Title", with: post_record.title)

      fill_in "Title", with: "Updated Title"
      click_button "Update"

      # Updates without page refresh
      expect(page).to have_content("Updated Title")
      expect(page).not_to have_field("Title")
    end
  end

  describe "Real-time updates", :js do
    let!(:post_record) { create(:post, user: user) }

    it "receives new comments via Turbo Stream" do
      visit post_path(post_record)

      # Simulate another user adding a comment
      comment = create(:comment, post: post_record, body: "New comment!")

      # Turbo Stream broadcast
      expect(page).to have_content("New comment!", wait: 5)
    end
  end
end
```

### Pattern 4: Service Object Tests

```ruby
# spec/services/posts/create_service_spec.rb
require 'rails_helper'

RSpec.describe Posts::CreateService do
  let(:user) { create(:user) }
  let(:valid_params) { { title: "Test", body: "Content" } }
  let(:invalid_params) { { title: "", body: "" } }

  describe ".call" do
    context "with valid params" do
      it "creates a post" do
        result = described_class.call(user: user, params: valid_params)

        expect(result).to be_success
        expect(result.value).to be_a(Post)
        expect(result.value).to be_persisted
      end

      it "associates post with user" do
        result = described_class.call(user: user, params: valid_params)

        expect(result.value.user).to eq(user)
      end
    end

    context "with invalid params" do
      it "returns failure" do
        result = described_class.call(user: user, params: invalid_params)

        expect(result).to be_failure
        expect(result.errors).to be_present
      end

      it "does not create a post" do
        expect {
          described_class.call(user: user, params: invalid_params)
        }.not_to change(Post, :count)
      end
    end
  end
end
```

### Pattern 5: Policy Tests

```ruby
# spec/policies/post_policy_spec.rb
require 'rails_helper'

RSpec.describe PostPolicy, type: :policy do
  let(:user) { create(:user) }
  let(:admin) { create(:user, :admin) }
  let(:post_record) { create(:post, user: user) }

  subject { described_class }

  permissions :show? do
    context "published post" do
      let(:post_record) { create(:post, published: true) }

      it "permits anyone" do
        expect(subject).to permit(nil, post_record)
        expect(subject).to permit(user, post_record)
      end
    end

    context "draft post" do
      let(:post_record) { create(:post, published: false) }

      it "denies guest" do
        expect(subject).not_to permit(nil, post_record)
      end

      it "permits owner" do
        expect(subject).to permit(post_record.user, post_record)
      end

      it "permits admin" do
        expect(subject).to permit(admin, post_record)
      end
    end
  end

  permissions :update?, :destroy? do
    it "denies guest" do
      expect(subject).not_to permit(nil, post_record)
    end

    it "denies other users" do
      other_user = create(:user)
      expect(subject).not_to permit(other_user, post_record)
    end

    it "permits owner" do
      expect(subject).to permit(user, post_record)
    end

    it "permits admin" do
      expect(subject).to permit(admin, post_record)
    end
  end

  describe "Scope" do
    let!(:published_post) { create(:post, published: true) }
    let!(:user_draft) { create(:post, user: user, published: false) }
    let!(:other_draft) { create(:post, published: false) }

    it "returns published posts for guest" do
      scope = Pundit.policy_scope(nil, Post)
      expect(scope).to include(published_post)
      expect(scope).not_to include(user_draft, other_draft)
    end

    it "returns published + own posts for user" do
      scope = Pundit.policy_scope(user, Post)
      expect(scope).to include(published_post, user_draft)
      expect(scope).not_to include(other_draft)
    end

    it "returns all posts for admin" do
      scope = Pundit.policy_scope(admin, Post)
      expect(scope).to include(published_post, user_draft, other_draft)
    end
  end
end
```

### Pattern 6: Factory Definitions

```ruby
# spec/factories/users.rb
FactoryBot.define do
  factory :user do
    sequence(:email) { |n| "user#{n}@example.com" }
    name { Faker::Name.name }
    password { "password123" }

    trait :admin do
      admin { true }
    end

    trait :with_posts do
      transient do
        posts_count { 3 }
      end

      after(:create) do |user, evaluator|
        create_list(:post, evaluator.posts_count, user: user)
      end
    end
  end
end

# spec/factories/posts.rb
FactoryBot.define do
  factory :post do
    user
    title { Faker::Lorem.sentence }
    body { Faker::Lorem.paragraphs(number: 3).join("\n\n") }
    published { false }

    trait :published do
      published { true }
    end

    trait :with_comments do
      transient do
        comments_count { 5 }
      end

      after(:create) do |post, evaluator|
        create_list(:comment, evaluator.comments_count, post: post)
      end
    end
  end
end
```

## Running Tests

```bash
# All tests
bundle exec rspec

# Specific file
bundle exec rspec spec/models/post_spec.rb

# Specific line
bundle exec rspec spec/models/post_spec.rb:25

# Tag-based
bundle exec rspec --tag focus
bundle exec rspec --tag ~slow

# Parallel execution
bundle exec parallel_rspec spec/
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Slow tests | Delayed feedback | Prioritize unit tests |
| Test dependencies | Flaky tests | Isolated setup |
| Excessive mocking | Can't verify real behavior | Combine with integration tests |
| Hardcoded data | Hard to maintain | Use Factory, Faker |

## Related Skills

- [core](../core/SKILL.md): Service objects
- [auth](../auth/SKILL.md): Policy testing
- [background](../background/SKILL.md): Job testing

## References

- [RSpec Rails](https://rspec.info/features/6-0/rspec-rails/)
- [Factory Bot](https://github.com/thoughtbot/factory_bot)
- [Capybara](https://github.com/teamcapybara/capybara)
- [Rails Testing Guide](https://guides.rubyonrails.org/testing.html)
