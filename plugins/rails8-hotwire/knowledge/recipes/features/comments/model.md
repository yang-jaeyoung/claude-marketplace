# Comment Models

Models for threaded comments and reactions with real-time broadcasting.

## Comment Model

```ruby
# app/models/comment.rb
class Comment < ApplicationRecord
  has_ancestry cache_depth: true

  belongs_to :post
  belongs_to :user
  has_many :reactions, dependent: :destroy

  validates :body, presence: true, length: { minimum: 1, maximum: 10_000 }

  # Real-time broadcasting
  broadcasts_to :post

  # Scopes
  scope :top_level, -> { where(ancestry: nil) }
  scope :recent, -> { order(created_at: :desc) }

  # Virtual attributes for mentions
  attr_accessor :mentioned_user_ids

  after_create :notify_mentioned_users
  after_create :notify_parent_author

  def depth_level
    depth || 0
  end

  def max_depth_reached?
    depth_level >= 5 # Limit nesting to 5 levels
  end

  private

  def notify_mentioned_users
    return unless mentioned_user_ids.present?

    mentioned_user_ids.each do |user_id|
      CommentMentionNotification.with(comment: self).deliver(User.find(user_id))
    end
  end

  def notify_parent_author
    return unless parent.present?
    return if parent.user_id == user_id # Don't notify self

    CommentReplyNotification.with(comment: self).deliver(parent.user)
  end
end
```

## Reaction Model

```ruby
# app/models/reaction.rb
class Reaction < ApplicationRecord
  belongs_to :comment
  belongs_to :user

  validates :emoji, presence: true, inclusion: { in: %w[👍 ❤️ 😂 🎉 😕 🚀] }
  validates :user_id, uniqueness: { scope: [:comment_id, :emoji] }

  broadcasts_to :comment

  # Counter cache
  counter_culture :comment, column_name: proc { |reaction| "#{reaction.emoji}_count" }
end
```

## Migrations

```ruby
# db/migrate/20240101000001_create_comments.rb
class CreateComments < ActiveRecord::Migration[8.0]
  def change
    create_table :comments do |t|
      t.references :post, null: false, foreign_key: true
      t.references :user, null: false, foreign_key: true
      t.text :body, null: false
      t.string :ancestry, index: true
      t.integer :ancestry_depth, default: 0

      # Reaction counters
      t.integer :thumbs_up_count, default: 0
      t.integer :heart_count, default: 0
      t.integer :laugh_count, default: 0
      t.integer :celebration_count, default: 0
      t.integer :confused_count, default: 0
      t.integer :rocket_count, default: 0

      t.timestamps
    end

    add_index :comments, [:post_id, :created_at]
  end
end

# db/migrate/20240101000002_create_reactions.rb
class CreateReactions < ActiveRecord::Migration[8.0]
  def change
    create_table :reactions do |t|
      t.references :comment, null: false, foreign_key: true
      t.references :user, null: false, foreign_key: true
      t.string :emoji, null: false

      t.timestamps
    end

    add_index :reactions, [:comment_id, :user_id, :emoji], unique: true
  end
end
```

## Key Features

### Ancestry Gem

The `ancestry` gem provides:
- Self-referential tree structure
- Efficient queries for ancestors/descendants
- Cached depth calculation
- `parent`, `children`, `siblings`, `root` methods

### Broadcasting

Both models use `broadcasts_to`:
- Comment broadcasts to `:post` channel
- Reaction broadcasts to `:comment` channel
- Automatic Turbo Stream updates on create/update/destroy

### Notifications

Comments trigger two types of notifications:
1. **Mention notifications**: When users are @mentioned
2. **Reply notifications**: When someone replies to your comment

### Counter Caching

The `counter_culture` gem maintains reaction counts:
- Denormalized emoji counts on Comment table
- Avoids N+1 queries when displaying reactions
- Auto-updates on reaction create/destroy

## Related

- [Back to Index](SKILL.md)
- [Next: Controllers](controller.md)
