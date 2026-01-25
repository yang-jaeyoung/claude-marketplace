# Factory Bot Setup

## Overview
Factory Bot provides a DSL for defining test data factories. Replaces Rails fixtures with flexible, maintainable object creation.

## When to Use
- Creating test data for specs
- Building complex object graphs with associations
- Generating multiple variations of test objects (traits)
- Avoiding database writes with `build` and `build_stubbed`

## Quick Start
```ruby
# Gemfile
group :development, :test do
  gem "factory_bot_rails"
  gem "faker"
end

# spec/rails_helper.rb
RSpec.configure do |config|
  config.include FactoryBot::Syntax::Methods
end
```

## Main Patterns

### Pattern 1: Basic Factory Definition
```ruby
# spec/factories/users.rb
FactoryBot.define do
  factory :user do
    sequence(:email) { |n| "user#{n}@example.com" }
    name { "John Doe" }
    password { "password123" }
    confirmed_at { Time.current }
  end
end

# Usage in specs
user = create(:user)  # Persisted to database
user = build(:user)   # Not persisted
user = build_stubbed(:user)  # Not persisted, faster, read-only
```

### Pattern 2: Associations
```ruby
# spec/factories/posts.rb
FactoryBot.define do
  factory :post do
    user  # Automatically creates associated user
    title { "Sample Post" }
    body { "Post content here" }
    published { false }

    # Explicit association with custom factory
    association :author, factory: :user

    # Override association attributes
    factory :post_with_admin do
      association :user, :admin
    end
  end
end

# Usage
post = create(:post)  # Creates user + post
post = create(:post, user: existing_user)  # Reuses existing user
```

### Pattern 3: Traits
```ruby
# spec/factories/posts.rb
FactoryBot.define do
  factory :post do
    user
    title { "Sample Post" }
    body { "Content" }
    published { false }

    trait :published do
      published { true }
      published_at { 1.day.ago }
    end

    trait :with_comments do
      after(:create) do |post|
        create_list(:comment, 3, post: post)
      end
    end

    trait :with_tags do
      after(:create) do |post, evaluator|
        post.tags << create_list(:tag, 2)
      end
    end

    # Combine traits in named factories
    factory :published_post, traits: [:published]
  end
end

# Usage
create(:post, :published)
create(:post, :published, :with_comments)
create(:published_post)
```

### Pattern 4: Sequences
```ruby
FactoryBot.define do
  sequence :email do |n|
    "user#{n}@example.com"
  end

  sequence :username do |n|
    "user_#{n}"
  end

  sequence :created_at do |n|
    n.days.ago
  end

  factory :user do
    email
    username
    name { "User #{username}" }
  end
end
```

### Pattern 5: Transient Attributes
```ruby
# spec/factories/users.rb
FactoryBot.define do
  factory :user do
    email
    name { "John Doe" }

    transient do
      posts_count { 0 }
      admin { false }
    end

    after(:create) do |user, evaluator|
      create_list(:post, evaluator.posts_count, user: user) if evaluator.posts_count > 0
      user.update(admin: true) if evaluator.admin
    end
  end
end

# Usage
user = create(:user, posts_count: 5)
user = create(:user, admin: true)
```

### Pattern 6: Callbacks
```ruby
FactoryBot.define do
  factory :user do
    email
    name { "John Doe" }

    # Runs after building (build/create)
    after(:build) do |user|
      user.slug = user.name.parameterize
    end

    # Runs after creating (create only)
    after(:create) do |user|
      user.send_welcome_email
    end

    # Runs before stubbing (build_stubbed only)
    before(:stub) do |user|
      user.id = rand(1..10000)
    end
  end
end
```

### Pattern 7: create vs build vs build_stubbed
```ruby
# create - Persisted to database (slowest)
user = create(:user)
user.persisted?  # => true

# build - Not persisted (faster)
user = build(:user)
user.persisted?  # => false
user.save  # Can be saved later

# build_stubbed - Not persisted, read-only (fastest)
user = build_stubbed(:user)
user.persisted?  # => true (stubbed)
user.readonly?  # => true
user.save  # Raises error

# Best practice: Use build_stubbed for unit tests
describe User do
  it "formats full name" do
    user = build_stubbed(:user, first_name: "John", last_name: "Doe")
    expect(user.full_name).to eq("John Doe")
  end
end
```

### Pattern 8: create_list and build_list
```ruby
# Create multiple objects
users = create_list(:user, 5)
posts = create_list(:post, 3, :published, user: user)

# Build multiple objects
drafts = build_list(:post, 10)

# Create with varying attributes
users = create_list(:user, 3) do |user, i|
  user.name = "User #{i}"
end
```

### Pattern 9: attributes_for (for controller tests)
```ruby
# Returns hash of attributes (no ID, no associations)
user_attrs = attributes_for(:user)
# => { email: "user1@example.com", name: "John Doe", password: "..." }

# Usage in request specs
post users_path, params: { user: attributes_for(:user) }

# With overrides
post users_path, params: { user: attributes_for(:user, name: "Jane") }
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Overusing `create` | Slow tests due to DB writes | Use `build` or `build_stubbed` when possible |
| Hardcoded values | Brittle tests | Use `Faker` or sequences for dynamic data |
| Duplicating factories | Hard to maintain | Use traits and inheritance |
| Creating unnecessary associations | Slow tests | Only create associations when needed |
| Using `create` in unit tests | Testing DB instead of logic | Use `build_stubbed` for pure unit tests |

## Related Skills
- [RSpec Setup](./rspec.md): RSpec configuration
- [Faker](./faker.md): Dynamic test data generation
- [Model Tests](../types/models.md): Testing ActiveRecord models

## References
- [Factory Bot Documentation](https://github.com/thoughtbot/factory_bot)
- [Factory Bot Rails](https://github.com/thoughtbot/factory_bot_rails)
- [Getting Started](https://github.com/thoughtbot/factory_bot/blob/master/GETTING_STARTED.md)
