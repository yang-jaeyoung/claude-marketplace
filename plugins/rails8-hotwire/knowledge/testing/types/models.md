# Model Specs

## Overview
Model specs test ActiveRecord models including validations, associations, scopes, callbacks, and business logic methods.

## When to Use
- Testing model validations and constraints
- Verifying associations are correctly defined
- Testing custom scopes and queries
- Testing callbacks and state transitions
- Testing business logic methods on models

## Quick Start
```ruby
# spec/models/user_spec.rb
require 'rails_helper'

RSpec.describe User, type: :model do
  describe 'validations' do
    it { should validate_presence_of(:email) }
    it { should validate_uniqueness_of(:email).case_insensitive }
  end

  describe 'associations' do
    it { should have_many(:posts).dependent(:destroy) }
  end

  describe '#full_name' do
    it 'returns first and last name' do
      user = build_stubbed(:user, first_name: 'John', last_name: 'Doe')
      expect(user.full_name).to eq('John Doe')
    end
  end
end
```

## Common Setup

For standard RSpec configuration including Factory Bot, Devise helpers, and Turbo Stream test helpers, see:
- [`snippets/common/rspec-setup.rb`](../../snippets/common/rspec-setup.rb): RSpec configuration
- [`snippets/common/factory-base.rb`](../../snippets/common/factory-base.rb): FactoryBot patterns

## Main Patterns

### Pattern 1: Testing Validations with Shoulda Matchers
```ruby
# spec/models/post_spec.rb
require 'rails_helper'

RSpec.describe Post, type: :model do
  describe 'validations' do
    # Presence
    it { should validate_presence_of(:title) }
    it { should validate_presence_of(:body) }

    # Length
    it { should validate_length_of(:title).is_at_most(200) }
    it { should validate_length_of(:title).is_at_least(3) }

    # Uniqueness (requires subject with existing record)
    context 'uniqueness' do
      subject { create(:post) }
      it { should validate_uniqueness_of(:slug).case_insensitive }
    end

    # Numericality
    it { should validate_numericality_of(:views_count).only_integer }
    it { should validate_numericality_of(:rating).is_greater_than_or_equal_to(0) }

    # Inclusion
    it { should validate_inclusion_of(:status).in_array(%w[draft published archived]) }

    # Custom validations
    it 'is invalid without published_at when published' do
      post = build(:post, published: true, published_at: nil)
      expect(post).not_to be_valid
      expect(post.errors[:published_at]).to include("can't be blank when published")
    end
  end
end
```

### Pattern 2: Testing Associations
```ruby
# spec/models/user_spec.rb
require 'rails_helper'

RSpec.describe User, type: :model do
  describe 'associations' do
    # One-to-many
    it { should have_many(:posts).dependent(:destroy) }
    it { should have_many(:comments).dependent(:nullify) }

    # Has many through
    it { should have_many(:tags).through(:taggings) }

    # Belongs to
    it { should belong_to(:organization).optional }

    # Has one
    it { should have_one(:profile).dependent(:destroy) }

    # With conditions
    it { should have_many(:published_posts).class_name('Post') }
  end

  # Testing association behavior
  describe 'post deletion' do
    it 'destroys associated posts when user is deleted' do
      user = create(:user)
      create_list(:post, 3, user: user)

      expect { user.destroy }.to change(Post, :count).by(-3)
    end
  end
end
```

### Pattern 3: Testing Scopes
```ruby
# spec/models/post_spec.rb
require 'rails_helper'

RSpec.describe Post, type: :model do
  describe 'scopes' do
    describe '.published' do
      let!(:published_post) { create(:post, :published) }
      let!(:draft_post) { create(:post, published: false) }

      it 'returns only published posts' do
        expect(Post.published).to include(published_post)
        expect(Post.published).not_to include(draft_post)
      end
    end

    describe '.recent' do
      let!(:old_post) { create(:post, created_at: 1.week.ago) }
      let!(:new_post) { create(:post, created_at: 1.hour.ago) }

      it 'returns posts in descending order by created_at' do
        expect(Post.recent.first).to eq(new_post)
        expect(Post.recent.last).to eq(old_post)
      end
    end

    describe '.by_author' do
      let(:user) { create(:user) }
      let!(:user_post) { create(:post, user: user) }
      let!(:other_post) { create(:post) }

      it 'returns posts by specific author' do
        expect(Post.by_author(user)).to include(user_post)
        expect(Post.by_author(user)).not_to include(other_post)
      end
    end

    # Chained scopes
    describe 'chaining scopes' do
      let(:user) { create(:user) }
      let!(:published_by_user) { create(:post, :published, user: user) }
      let!(:draft_by_user) { create(:post, user: user) }
      let!(:published_by_other) { create(:post, :published) }

      it 'chains published and by_author scopes' do
        result = Post.published.by_author(user)
        expect(result).to include(published_by_user)
        expect(result).not_to include(draft_by_user, published_by_other)
      end
    end
  end
end
```

### Pattern 4: Testing Instance Methods
```ruby
# spec/models/user_spec.rb
require 'rails_helper'

RSpec.describe User, type: :model do
  describe '#full_name' do
    it 'combines first and last name' do
      user = build_stubbed(:user, first_name: 'John', last_name: 'Doe')
      expect(user.full_name).to eq('John Doe')
    end

    it 'handles missing last name' do
      user = build_stubbed(:user, first_name: 'John', last_name: nil)
      expect(user.full_name).to eq('John')
    end
  end

  describe '#admin?' do
    it 'returns true for admin users' do
      admin = build_stubbed(:user, :admin)
      expect(admin).to be_admin
    end

    it 'returns false for regular users' do
      user = build_stubbed(:user)
      expect(user).not_to be_admin
    end
  end

  describe '#posts_count' do
    it 'returns the number of posts' do
      user = create(:user)
      create_list(:post, 3, user: user)

      expect(user.posts_count).to eq(3)
    end
  end
end
```

### Pattern 5: Testing Callbacks
```ruby
# spec/models/post_spec.rb
require 'rails_helper'

RSpec.describe Post, type: :model do
  describe 'callbacks' do
    describe 'before_save' do
      it 'generates slug from title' do
        post = create(:post, title: 'Hello World', slug: nil)
        expect(post.slug).to eq('hello-world')
      end

      it 'does not override existing slug' do
        post = create(:post, title: 'Hello World', slug: 'custom-slug')
        expect(post.slug).to eq('custom-slug')
      end
    end

    describe 'after_create' do
      it 'sends notification email' do
        expect {
          create(:post, :published)
        }.to have_enqueued_job(PostNotificationJob)
      end
    end

    describe 'before_destroy' do
      it 'prevents deletion if post has approved comments' do
        post = create(:post)
        create(:comment, :approved, post: post)

        expect(post.destroy).to be_falsey
        expect(post.errors[:base]).to include('Cannot delete post with approved comments')
      end
    end
  end
end
```

### Pattern 6: Testing Enums
```ruby
# spec/models/post_spec.rb
require 'rails_helper'

RSpec.describe Post, type: :model do
  describe 'enums' do
    it { should define_enum_for(:status).with_values(draft: 0, published: 1, archived: 2) }

    it 'sets default status to draft' do
      post = Post.new
      expect(post.status).to eq('draft')
    end

    describe 'status transitions' do
      let(:post) { create(:post, status: :draft) }

      it 'can transition from draft to published' do
        post.published!
        expect(post.status).to eq('published')
      end

      it 'sets published_at when publishing' do
        post.published!
        expect(post.published_at).to be_present
      end
    end
  end
end
```

### Pattern 7: Testing Class Methods
```ruby
# spec/models/post_spec.rb
require 'rails_helper'

RSpec.describe Post, type: :model do
  describe '.search' do
    let!(:match) { create(:post, title: 'Rails Testing Guide') }
    let!(:no_match) { create(:post, title: 'Unrelated Topic') }

    it 'finds posts by title' do
      results = Post.search('Rails')
      expect(results).to include(match)
      expect(results).not_to include(no_match)
    end
  end

  describe '.trending' do
    it 'returns posts with high engagement' do
      trending = create(:post, views_count: 1000, likes_count: 100)
      regular = create(:post, views_count: 10, likes_count: 1)

      expect(Post.trending).to include(trending)
      expect(Post.trending).not_to include(regular)
    end
  end
end
```

### Pattern 8: Testing Complex Queries
```ruby
# spec/models/post_spec.rb
require 'rails_helper'

RSpec.describe Post, type: :model do
  describe 'complex queries' do
    describe '.with_recent_comments' do
      let!(:post_with_recent) { create(:post) }
      let!(:post_without_recent) { create(:post) }

      before do
        create(:comment, post: post_with_recent, created_at: 1.hour.ago)
        create(:comment, post: post_without_recent, created_at: 1.week.ago)
      end

      it 'includes posts with comments from last 24 hours' do
        result = Post.with_recent_comments(24.hours)
        expect(result).to include(post_with_recent)
        expect(result).not_to include(post_without_recent)
      end
    end

    describe '.popular_in_category' do
      let(:category) { create(:category) }
      let!(:popular) { create(:post, category: category, views_count: 1000) }
      let!(:unpopular) { create(:post, category: category, views_count: 10) }

      it 'returns top posts by views in category' do
        result = Post.popular_in_category(category, limit: 1)
        expect(result).to eq([popular])
      end
    end
  end
end
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Using `create` instead of `build_stubbed` | Slow tests | Use `build_stubbed` for unit tests that don't need persistence |
| Testing Rails internals | Not testing your code | Test custom behavior, not `has_many` implementation |
| Overly complex factory setup | Hard to understand test | Use traits and keep factories simple |
| Testing multiple behaviors in one test | Hard to debug failures | One expectation per test |
| Not testing edge cases | Bugs in production | Test nil, empty, boundary values |

## Related Skills
- [Factory Bot](../setup/factory-bot.md): Creating test data
- [Shoulda Matchers](../setup/rspec.md): Validation/association matchers
- [Request Specs](./requests.md): Testing controllers

## References
- [RSpec Rails](https://rspec.info/features/6-0/rspec-rails/model-specs/)
- [Shoulda Matchers](https://github.com/thoughtbot/shoulda-matchers)
- [Better Specs](https://www.betterspecs.org/)
