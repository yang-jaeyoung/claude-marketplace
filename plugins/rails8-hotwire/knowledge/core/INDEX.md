---
name: rails8-core
description: Rails 8 project setup, folder structure, Gemfile, service/form/query object patterns. Use when starting a new project or extending structure.
triggers:
  - project setup
  - new project
  - rails new
  - gemfile
  - folder structure
  - service object
  - form object
  - query object
  - 프로젝트 생성
  - 프로젝트 설정
  - 젬파일
  - 폴더 구조
  - 서비스 객체
  - 폼 객체
  - 쿼리 객체
summary: |
  Rails 8 프로젝트 초기 설정과 구조를 다룹니다. 프로젝트 생성, 폴더 구조,
  필수 젬 설정, 서비스/폼/쿼리 객체 패턴을 포함합니다. 새 프로젝트를
  시작하거나 기존 구조를 확장할 때 사용하세요.
token_cost: medium
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - setup/*.md
    - patterns/*.md
  deep:
    - "**/*.md"
    - "**/*.rb"
---

# Core: Project Setup & Structure

## Overview

Covers initial setup for Rails 8 projects, folder structure, essential gems, and core patterns like service objects and form objects.

## When to Use

- When starting a new Rails 8 project
- When extending project structure
- When applying service/form/query object patterns

## Core Principles

| Principle | Description |
|-----------|-------------|
| Convention over Configuration | Minimize configuration by following Rails conventions |
| Fat Model, Skinny Controller | Business logic goes in models/services |
| Single Responsibility | Each class has one responsibility |

## Quick Start

### Project Creation

```bash
# Rails 8 recommended setup
rails new myapp \
  --database=postgresql \
  --css=tailwind \
  --skip-jbuilder \
  --skip-action-mailbox

cd myapp
```

### Recommended Gemfile Additions

```ruby
# Add to Gemfile

# Core
gem "pagy"                    # Pagination
gem "pundit"                  # Authorization
gem "faraday"                 # HTTP client

group :development, :test do
  gem "rspec-rails"
  gem "factory_bot_rails"
  gem "faker"
end

group :development do
  gem "rubocop-rails-omakase"  # Rails 8 default linter
  gem "annotate"               # Model schema annotations
  gem "bullet"                 # N+1 query detection
end
```

```bash
bundle install
```

### Extending Folder Structure

```bash
mkdir -p app/services
mkdir -p app/forms
mkdir -p app/queries
mkdir -p app/presenters
mkdir -p app/policies
```

### Quick Authentication Setup (Rails 8 Built-in)

```bash
# Generate basic authentication without Devise
bin/rails generate authentication
bin/rails db:migrate
```

**Included:** Login/logout, password reset, session management
**Not included:** Registration, OAuth, 2FA - see auth

## File Structure

```
core/
├── SKILL.md
├── setup/
│   ├── new-project.md
│   ├── gemfile.md
│   ├── credentials.md
│   └── docker.md
├── structure/
│   ├── folder-structure.md
│   ├── naming-conventions.md
│   └── code-organization.md
├── patterns/
│   ├── service-object.md
│   ├── form-object.md
│   ├── query-object.md
│   ├── presenter.md
│   └── result-object.md
├── configuration/
│   ├── database.md
│   ├── environments.md
│   ├── initializers.md
│   └── routes.md
└── snippets/
    ├── application_service.rb
    ├── application_form.rb
    ├── application_query.rb
    └── result.rb
```

## Main Patterns

### Pattern 1: Service Object

Separates complex business logic from controllers.

```ruby
# app/services/application_service.rb
class ApplicationService
  def self.call(...)
    new(...).call
  end
end

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
        Result.success(post)
      else
        Result.failure(post.errors)
      end
    end
  end
end
```

### Pattern 2: Result Object

Returns service results consistently.

```ruby
# app/services/result.rb
class Result
  attr_reader :value, :errors

  def initialize(success:, value: nil, errors: nil)
    @success = success
    @value = value
    @errors = errors
  end

  def success? = @success
  def failure? = !@success

  def self.success(value) = new(success: true, value: value)
  def self.failure(errors) = new(success: false, errors: errors)
end
```

### Pattern 3: Query Object

Encapsulates complex queries for reusability.

```ruby
# app/queries/posts_query.rb
class PostsQuery
  def initialize(scope = Post.all)
    @scope = scope
  end

  def call(filters = {})
    @scope
      .then { |s| by_status(s, filters[:status]) }
      .then { |s| by_author(s, filters[:author_id]) }
      .then { |s| search(s, filters[:q]) }
      .includes(:user, :tags)
      .order(created_at: :desc)
  end

  private

  def by_status(scope, status)
    status.present? ? scope.where(status: status) : scope
  end

  def by_author(scope, author_id)
    author_id.present? ? scope.where(user_id: author_id) : scope
  end

  def search(scope, query)
    query.present? ? scope.where("title ILIKE ?", "%#{query}%") : scope
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Fat Controller | Hard to test, not reusable | Extract to service objects |
| God Object | Violates single responsibility | Separate classes by role |
| Hardcoded settings | Cannot manage by environment | Use credentials, ENV |

## Related Skills

- [hotwire](../hotwire/SKILL.md): Turbo/Stimulus setup
- [models](../models/SKILL.md): Model creation and patterns
- [auth](../auth/): Detailed authentication setup (Phase 2)

## References

- [Rails Guides - Getting Started](https://guides.rubyonrails.org/getting_started.html)
- [Rails 8.0 Release Notes](https://guides.rubyonrails.org/8_0_release_notes.html)
