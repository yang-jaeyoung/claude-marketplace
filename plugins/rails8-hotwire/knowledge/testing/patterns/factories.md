# Advanced Factory Patterns

## Overview
Advanced Factory Bot patterns including traits, transient attributes, callbacks, sequences, and complex associations.

## When to Use
- Creating complex test data scenarios
- Building reusable factory variations
- Managing associations efficiently
- Generating realistic test data at scale

## Quick Start
```ruby
# spec/factories/posts.rb
FactoryBot.define do
  factory :post do
    user
    title { Faker::Lorem.sentence }
    body { Faker::Lorem.paragraphs(number: 3).join("\n\n") }

    trait :published do
      published { true }
      published_at { 1.day.ago }
    end

    trait :with_comments do
      after(:create) do |post|
        create_list(:comment, 3, post: post)
      end
    end
  end
end
```

## Main Patterns

### Pattern 1: Traits for Variations
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

    trait :confirmed do
      confirmed_at { Time.current }
    end

    trait :unconfirmed do
      confirmed_at { nil }
    end

    trait :with_avatar do
      after(:create) do |user|
        user.avatar.attach(
          io: File.open(Rails.root.join('spec', 'fixtures', 'avatar.jpg')),
          filename: 'avatar.jpg'
        )
      end
    end

    trait :with_posts do
      transient do
        posts_count { 5 }
      end

      after(:create) do |user, evaluator|
        create_list(:post, evaluator.posts_count, user: user)
      end
    end

    # Named factories combining traits
    factory :admin_user, traits: [:admin, :confirmed]
    factory :user_with_content, traits: [:confirmed, :with_posts]
  end
end

# Usage
user = create(:user, :admin, :confirmed)
user = create(:admin_user)  # Same as above
user = create(:user, :with_posts, posts_count: 10)
```

### Pattern 2: Transient Attributes
```ruby
# spec/factories/posts.rb
FactoryBot.define do
  factory :post do
    user
    title { Faker::Lorem.sentence }
    body { Faker::Lorem.paragraph }

    transient do
      # Transient attributes don't map to model attributes
      comments_count { 0 }
      tags_count { 0 }
      likes_count { 0 }
      published { false }
    end

    after(:create) do |post, evaluator|
      if evaluator.comments_count > 0
        create_list(:comment, evaluator.comments_count, post: post)
      end

      if evaluator.tags_count > 0
        post.tags = create_list(:tag, evaluator.tags_count)
      end

      if evaluator.likes_count > 0
        create_list(:like, evaluator.likes_count, post: post)
      end

      if evaluator.published
        post.update(published: true, published_at: Time.current)
      end
    end
  end
end

# Usage
post = create(:post, comments_count: 5, tags_count: 3, published: true)
```

### Pattern 3: Advanced Sequences
```ruby
# spec/factories/users.rb
FactoryBot.define do
  # Global sequence
  sequence :email do |n|
    "user#{n}@example.com"
  end

  # Sequence with custom format
  sequence :username do |n|
    "user_#{n.to_s.rjust(4, '0')}"  # user_0001, user_0002
  end

  # Date sequence
  sequence :created_at do |n|
    n.days.ago
  end

  # Enum sequence
  sequence :status, %i[pending active suspended].cycle

  factory :user do
    email
    username
    name { Faker::Name.name }

    trait :recent do
      created_at { rand(1..7).days.ago }
    end
  end

  # Reset sequence (useful for tests requiring specific values)
  after(:create) do
    FactoryBot.rewind_sequences
  end
end

# Usage
user1 = create(:user)  # user_0001@example.com
user2 = create(:user)  # user_0002@example.com
FactoryBot.rewind_sequences
user3 = create(:user)  # user_0001@example.com (restarted)
```

### Pattern 4: Callbacks (before/after hooks)
```ruby
# spec/factories/posts.rb
FactoryBot.define do
  factory :post do
    user
    title { "Draft Title" }
    body { "Draft body" }

    # Runs after building (build and create)
    after(:build) do |post|
      post.slug = post.title.parameterize if post.slug.nil?
    end

    # Runs after creating (create only)
    after(:create) do |post|
      post.update_columns(view_count: rand(0..1000))
    end

    # Runs before stubbing (build_stubbed only)
    before(:stub) do |post|
      post.id ||= rand(1..10000)
    end

    trait :with_analytics do
      after(:create) do |post|
        Analytics.track('post_created', post_id: post.id)
      end
    end

    trait :with_initial_view do
      after(:create) do |post|
        create(:view, post: post, user: post.user)
      end
    end
  end
end
```

### Pattern 5: Polymorphic Associations
```ruby
# spec/factories/comments.rb
FactoryBot.define do
  factory :comment do
    user
    body { Faker::Lorem.paragraph }

    # Default commentable
    for_post

    trait :for_post do
      association :commentable, factory: :post
    end

    trait :for_article do
      association :commentable, factory: :article
    end

    trait :for_photo do
      association :commentable, factory: :photo
    end
  end
end

# Usage
comment = create(:comment)  # Commentable is a post
comment = create(:comment, :for_article)
comment = create(:comment, commentable: specific_photo)
```

### Pattern 6: Nested Factories (Inheritance)
```ruby
# spec/factories/users.rb
FactoryBot.define do
  factory :user do
    sequence(:email) { |n| "user#{n}@example.com" }
    name { Faker::Name.name }
    role { :member }

    factory :moderator do
      role { :moderator }

      factory :admin do
        role { :admin }
        permissions { :all }
      end
    end

    factory :premium_user do
      subscription { :premium }
      subscription_expires_at { 1.year.from_now }

      factory :lifetime_user do
        subscription { :lifetime }
        subscription_expires_at { nil }
      end
    end
  end
end

# Usage
user = create(:user)           # role: member
mod = create(:moderator)       # role: moderator
admin = create(:admin)         # role: admin, permissions: all
premium = create(:premium_user)
```

### Pattern 7: Conditional Attributes
```ruby
# spec/factories/subscriptions.rb
FactoryBot.define do
  factory :subscription do
    user
    plan { 'free' }

    transient do
      active { true }
    end

    # Conditional attribute based on transient
    status { active ? 'active' : 'cancelled' }
    cancelled_at { active ? nil : 1.day.ago }
    expires_at { active ? 1.month.from_now : nil }

    trait :premium do
      plan { 'premium' }
      price { 9.99 }
    end

    trait :enterprise do
      plan { 'enterprise' }
      price { 99.99 }
      features { { api_access: true, support: true } }
    end

    # Conditional callbacks
    after(:create) do |subscription, evaluator|
      if evaluator.active && subscription.premium?
        create(:invoice, subscription: subscription)
      end
    end
  end
end

# Usage
subscription = create(:subscription, active: false)
subscription = create(:subscription, :premium, active: true)  # Creates invoice
```

### Pattern 8: Self-Referential Associations
```ruby
# spec/factories/users.rb
FactoryBot.define do
  factory :user do
    sequence(:email) { |n| "user#{n}@example.com" }
    name { Faker::Name.name }

    trait :with_followers do
      transient do
        followers_count { 3 }
      end

      after(:create) do |user, evaluator|
        create_list(:user, evaluator.followers_count).each do |follower|
          create(:follow, follower: follower, followee: user)
        end
      end
    end

    trait :with_following do
      transient do
        following_count { 3 }
      end

      after(:create) do |user, evaluator|
        create_list(:user, evaluator.following_count).each do |followee|
          create(:follow, follower: user, followee: followee)
        end
      end
    end
  end

  # Follow join model
  factory :follow do
    association :follower, factory: :user
    association :followee, factory: :user
  end
end

# Usage
user = create(:user, :with_followers, followers_count: 5)
user = create(:user, :with_following, following_count: 10)
```

### Pattern 9: File Attachments (ActiveStorage)
```ruby
# spec/factories/posts.rb
FactoryBot.define do
  factory :post do
    user
    title { Faker::Lorem.sentence }
    body { Faker::Lorem.paragraph }

    trait :with_cover_image do
      after(:build) do |post|
        post.cover_image.attach(
          io: File.open(Rails.root.join('spec', 'fixtures', 'files', 'image.jpg')),
          filename: 'cover.jpg',
          content_type: 'image/jpeg'
        )
      end
    end

    trait :with_attachments do
      transient do
        attachments_count { 2 }
      end

      after(:build) do |post, evaluator|
        evaluator.attachments_count.times do |i|
          post.attachments.attach(
            io: StringIO.new("file content #{i}"),
            filename: "file_#{i}.pdf",
            content_type: 'application/pdf'
          )
        end
      end
    end
  end
end

# Usage
post = create(:post, :with_cover_image)
post = create(:post, :with_attachments, attachments_count: 5)
```

### Pattern 10: Time Travel in Factories
```ruby
# spec/factories/posts.rb
FactoryBot.define do
  factory :post do
    user
    title { Faker::Lorem.sentence }

    trait :from_last_week do
      created_at { 1.week.ago }
      updated_at { 1.week.ago }
    end

    trait :scheduled do
      published { false }
      publish_at { 1.day.from_now }
    end

    trait :archived do
      archived { true }
      archived_at { 6.months.ago }
    end

    # Create posts across a time range
    trait :with_view_history do
      after(:create) do |post|
        7.times do |i|
          travel_to (7 - i).days.ago do
            create(:view, post: post, count: rand(10..100))
          end
        end
      end
    end
  end
end
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Creating too much data in factories | Slow tests | Use `build` or `build_stubbed` when possible |
| Hardcoding timestamps | Tests fail on specific dates | Use relative times (`1.day.ago`) |
| Creating unnecessary associations | Database bloat | Use `association :user, strategy: :build` |
| Duplicating factory logic | Hard to maintain | Use traits and inheritance |
| Not using sequences | Uniqueness violations | Always use sequences for unique fields |

## Related Skills
- [Factory Bot Setup](../setup/factory-bot.md): Basic factory configuration
- [Faker](../setup/faker.md): Realistic test data
- [Models](../types/models.md): Testing models with factories

## References
- [Factory Bot Documentation](https://github.com/thoughtbot/factory_bot)
- [Getting Started](https://github.com/thoughtbot/factory_bot/blob/master/GETTING_STARTED.md)
- [Best Practices](https://thoughtbot.com/blog/factories-should-be-the-bare-minimum)
