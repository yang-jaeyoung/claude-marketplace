---
name: rails8-models
description: ActiveRecord model design, validations, associations, scopes, N+1 resolution, query object patterns. Use when creating models or writing complex queries.
triggers:
  - model
  - activerecord
  - migration
  - validation
  - association
  - scope
  - query
  - n+1
  - enum
  - callback
  - 모델
  - 액티브레코드
  - 마이그레이션
  - 유효성 검사
  - 연관관계
  - 스코프
  - 쿼리
  - 콜백
summary: |
  ActiveRecord 모델 설계와 데이터 패턴을 다룹니다. 모델 생성, 유효성 검사,
  연관관계, 스코프, N+1 문제 해결, 쿼리 객체 패턴을 포함합니다.
  복잡한 쿼리나 데이터 무결성이 필요할 때 참조하세요.
token_cost: high
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - activerecord/*.md
    - queries/*.md
  deep:
    - "**/*.md"
    - "**/*.rb"
---

# Models: ActiveRecord + Data Patterns

## Overview

Covers model design, validations, associations, and query optimization patterns using Rails 8's ActiveRecord. Includes N+1 problem resolution and query object patterns.

## When to Use

- When creating new models
- When writing complex queries
- When adding data validation logic
- When designing associations

## Core Principles

| Principle | Description |
|-----------|-------------|
| Skinny Model | Complex logic goes to services/query objects |
| Eager Loading | Prevent N+1 problems proactively |
| Explicit Validations | Declare all data integrity rules |
| Scope Usage | Encapsulate reusable queries |

## Quick Start

### Model Generation

```bash
rails g model Post title:string body:text published:boolean user:references
rails g model Comment body:text post:references user:references
rails db:migrate
```

### Basic Model Structure

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  # Associations
  belongs_to :user
  has_many :comments, dependent: :destroy
  has_many :taggings, dependent: :destroy
  has_many :tags, through: :taggings

  # Validations
  validates :title, presence: true, length: { maximum: 200 }
  validates :body, presence: true
  validates :slug, uniqueness: true, allow_nil: true

  # Scopes
  scope :published, -> { where(published: true) }
  scope :recent, -> { order(created_at: :desc) }
  scope :by_author, ->(user) { where(user: user) }

  # Enum (Rails 8: default prefix)
  enum :status, { draft: 0, published: 1, archived: 2 }

  # Callbacks (keep minimal)
  before_save :generate_slug, if: -> { slug.blank? && title.present? }

  private

  def generate_slug
    self.slug = title.parameterize
  end
end
```

## File Structure

```
models/
├── SKILL.md
├── activerecord/
│   ├── migrations.md
│   ├── validations.md
│   ├── associations.md
│   ├── callbacks.md
│   ├── scopes.md
│   ├── enums.md
│   └── concerns.md
├── queries/
│   ├── basics.md
│   ├── joins.md
│   ├── aggregations.md
│   ├── n-plus-one.md
│   ├── raw-sql.md
│   └── query-object.md
├── patterns/
│   ├── soft-delete.md
│   ├── versioning.md
│   ├── tagging.md
│   ├── slugs.md
│   ├── tree-structure.md
│   └── multi-tenant.md
└── snippets/
    ├── base_model.rb
    ├── soft_deletable.rb
    ├── sluggable.rb
    └── searchable.rb
```

## Main Patterns

### Pattern 1: N+1 Query Resolution

```ruby
# Bad: N+1 problem
Post.all.each { |p| puts p.user.name }
# SELECT * FROM posts
# SELECT * FROM users WHERE id = 1  (repeated N times)

# Good: Eager Loading
Post.includes(:user).each { |p| puts p.user.name }
# SELECT * FROM posts
# SELECT * FROM users WHERE id IN (1, 2, 3...)

# Good: Select only needed columns
Post.select(:id, :title, :created_at).includes(:user).recent

# Good: Nested associations
Post.includes(comments: :user).find(params[:id])
```

### Pattern 2: Query Object

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
      .then { |s| by_date_range(s, filters[:from], filters[:to]) }
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
    return scope if query.blank?
    scope.where("title ILIKE ? OR body ILIKE ?", "%#{query}%", "%#{query}%")
  end

  def by_date_range(scope, from, to)
    scope = scope.where("created_at >= ?", from) if from.present?
    scope = scope.where("created_at <= ?", to) if to.present?
    scope
  end
end

# Usage
@posts = PostsQuery.new.call(params.permit(:status, :author_id, :q, :from, :to))
```

### Pattern 3: Soft Delete (Concern)

```ruby
# app/models/concerns/soft_deletable.rb
module SoftDeletable
  extend ActiveSupport::Concern

  included do
    scope :kept, -> { where(deleted_at: nil) }
    scope :deleted, -> { where.not(deleted_at: nil) }

    default_scope { kept }
  end

  def soft_delete
    update(deleted_at: Time.current)
  end

  def restore
    update(deleted_at: nil)
  end

  def deleted?
    deleted_at.present?
  end
end

# Usage
class Post < ApplicationRecord
  include SoftDeletable
end

@post.soft_delete  # Soft delete
Post.unscoped.deleted  # Query deleted items
```

### Pattern 4: Validation Patterns

```ruby
class User < ApplicationRecord
  # Presence validation
  validates :email, presence: true

  # Format validation
  validates :email, format: { with: URI::MailTo::EMAIL_REGEXP }

  # Uniqueness validation (case insensitive)
  validates :email, uniqueness: { case_sensitive: false }

  # Length validation
  validates :username, length: { minimum: 3, maximum: 30 }

  # Conditional validation
  validates :phone, presence: true, if: :phone_required?

  # Custom validation
  validate :password_complexity

  private

  def password_complexity
    return if password.blank?

    unless password.match?(/\A(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
      errors.add(:password, "must include uppercase, lowercase, and digit")
    end
  end

  def phone_required?
    verified? && phone_verification_enabled?
  end
end
```

### Pattern 5: Scope Chaining

```ruby
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
  scope :recent, -> { order(created_at: :desc) }
  scope :popular, -> { order(views_count: :desc) }
  scope :this_week, -> { where(created_at: 1.week.ago..) }
  scope :by_tag, ->(tag) { joins(:tags).where(tags: { name: tag }) }

  # Complex scope
  scope :featured, -> {
    published
      .where(featured: true)
      .where("views_count > ?", 100)
      .recent
      .limit(5)
  }
end

# Chaining usage
Post.published.recent.this_week.by_tag("ruby")
```

### Pattern 6: Callback Considerations

```ruby
class Post < ApplicationRecord
  # Good: Appropriate callback usage
  before_validation :normalize_title
  before_save :generate_slug, if: :slug_needed?
  after_create_commit :broadcast_to_followers

  # Bad: Patterns to avoid
  # Calling external APIs in after_save (delays transaction)
  # Modifying other models in after_create (unexpected rollback)

  private

  def normalize_title
    self.title = title&.strip&.titleize
  end

  def slug_needed?
    slug.blank? && title.present?
  end

  def generate_slug
    self.slug = title.parameterize
  end

  def broadcast_to_followers
    # after_commit: Runs after transaction completes
    BroadcastJob.perform_later(self)
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Callback abuse | Hard to debug, side effects | Use explicit service objects |
| default_scope abuse | Unexpected queries | Call scopes explicitly |
| Models without validation | Data integrity risk | Validate all required fields |
| Fat Model | Hard to test/maintain | Separate concerns, services |

## Related Skills

- [core/patterns](../core/patterns/): Service/query objects
- [controllers](../controllers/SKILL.md): Using query results
- [testing](../testing/): Model testing (Phase 3)

## References

- [Active Record Basics](https://guides.rubyonrails.org/active_record_basics.html)
- [Active Record Validations](https://guides.rubyonrails.org/active_record_validations.html)
- [Active Record Associations](https://guides.rubyonrails.org/association_basics.html)
- [Active Record Query Interface](https://guides.rubyonrails.org/active_record_querying.html)
