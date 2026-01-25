---
description: ActiveRecord 모델 패턴, 연관 관계, 쿼리 최적화 가이드.
argument-hint: "[model_name]"
allowed-tools: ["Read", "Glob", "Grep"]
---

# /rails8-hotwire:rails8-models - Model Patterns

ActiveRecord 모델 패턴과 쿼리 최적화를 안내합니다.

## Topics

1. **마이그레이션** - 테이블 생성 및 변경
2. **연관 관계** - has_many, belongs_to
3. **검증** - validates 규칙
4. **스코프** - 재사용 가능한 쿼리
5. **N+1 방지** - includes, eager_load

## Knowledge Loading

- `knowledge/models/INDEX.md` - 모델 전체 가이드

## Key Patterns

### Model with Associations

```ruby
class Post < ApplicationRecord
  belongs_to :user
  has_many :comments, dependent: :destroy

  validates :title, presence: true

  scope :published, -> { where(published: true) }
  scope :recent, -> { order(created_at: :desc) }
end
```

### N+1 Query Prevention

```ruby
# Good - eager loading
posts = Post.includes(:user, :comments).published

# Bad - N+1 queries
posts.each { |p| p.user.name }
```

## Related

- `/rails8-hotwire:rails8-controllers` - 컨트롤러 패턴
- `/rails8-hotwire:n1-hunter` - N+1 쿼리 탐지
