---
name: rails8-recipes-comments
description: Threaded comment system with replies, reactions, @mentions, and real-time updates
triggers:
  - comment
  - threaded comment
  - nested comment
  - reply
  - reaction
  - mention
  - discussion
  - 댓글
  - 대댓글
  - 중첩 댓글
  - 답글
  - 반응
  - 멘션
  - 토론
summary: |
  실시간 대댓글 시스템을 다룹니다. ancestry 젬을 사용한 중첩 댓글, 이모지 반응,
  @멘션, Turbo Streams 라이브 업데이트를 포함합니다. Reddit, Discourse, GitHub
  이슈와 같은 토론 기능을 구축합니다.
token_cost: medium
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - "*.md"
  deep:
    - "**/*.md"
---

# Threaded Comment System

Complete real-time comment system with threaded replies, reactions, @mentions, and live updates via Turbo Streams. Build discussion features like Reddit, Discourse, or GitHub issues.

## Overview

This skill provides a production-ready threaded comment system featuring:

- **Threaded Replies**: Nested comments using ancestry gem (up to 5 levels deep)
- **Real-time Updates**: Live comment creation/deletion via Turbo Streams
- **Reactions**: Toggle emoji reactions (👍 ❤️ 😂 🎉 😕 🚀)
- **@Mentions**: Mention users with autocomplete
- **Notifications**: Notify users when mentioned or replied to
- **Progressive Enhancement**: Works without JavaScript, enhanced with Stimulus

## Prerequisites

- [hotwire/turbo-streams](../../../hotwire/turbo-streams.md): Real-time updates
- [models/associations](../../../models/associations.md): Self-referential relationships
- [realtime/action-cable](../../../realtime/action-cable.md): Broadcasting
- [hotwire/stimulus](../../../hotwire/stimulus.md): Interactive UI

## Quick Start

```ruby
# Gemfile
gem "ancestry"

# Terminal
bundle install
rails generate model Comment post:references user:references body:text ancestry:string
rails db:migrate
```

## File Structure

```
comments/
├── SKILL.md           # This file - overview and index
├── model.md           # Comment and Reaction models
├── controller.md      # CommentsController and ReactionsController
├── views.md           # ERB templates and partials
└── realtime.md        # Stimulus controllers and Turbo Streams
```

## Implementation Steps

1. **[Models](model.md)**: Set up Comment and Reaction models with ancestry gem
2. **[Controllers](controller.md)**: Handle comment CRUD and reaction toggling
3. **[Views](views.md)**: Render threaded comments with forms
4. **[Real-time](realtime.md)**: Add Stimulus controllers and Turbo Stream templates

## Testing

```ruby
# spec/models/comment_spec.rb
require "rails_helper"

RSpec.describe Comment, type: :model do
  it "creates threaded comments" do
    post = create(:post)
    parent = create(:comment, post: post)
    reply = create(:comment, post: post, parent: parent)

    expect(reply.parent).to eq(parent)
    expect(parent.children).to include(reply)
    expect(reply.depth).to eq(1)
  end

  it "limits nesting depth" do
    post = create(:post)
    comment = create(:comment, post: post)

    5.times do
      comment = create(:comment, post: post, parent: comment)
    end

    expect(comment.max_depth_reached?).to be true
  end

  it "broadcasts to post channel" do
    post = create(:post)

    expect {
      create(:comment, post: post)
    }.to have_broadcasted_to(post)
  end
end

# spec/requests/comments_spec.rb
require "rails_helper"

RSpec.describe "Comments", type: :request do
  let(:user) { create(:user) }
  let(:post_record) { create(:post) }

  before { sign_in user }

  it "creates a comment" do
    expect {
      post post_comments_path(post_record), params: {
        comment: { body: "Great post!" }
      }
    }.to change(Comment, :count).by(1)

    expect(Comment.last.user).to eq(user)
  end

  it "creates nested replies" do
    parent = create(:comment, post: post_record)

    post post_comments_path(post_record, parent_id: parent.id), params: {
      comment: { body: "I agree!" }
    }

    reply = Comment.last
    expect(reply.parent).to eq(parent)
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Unlimited nesting | Deep threads unreadable | Limit to 5 levels max |
| No counter caches | N+1 queries for reaction counts | Use counter_culture gem |
| Synchronous notifications | Slow comment creation | Use background jobs for notifications |
| Missing ancestry indexes | Slow threaded queries | Ensure ancestry column is indexed |
| No mention validation | Mention non-existent users | Validate mentioned_user_ids exist |

## Related Skills

- [hotwire/turbo-streams](../../../hotwire/turbo-streams.md): Real-time updates
- [realtime/action-cable](../../../realtime/action-cable.md): Broadcasting
- [background/solid-queue](../../../background/solid-queue.md): Notifications
- [recipes/notifications](../notifications.md): User notifications

## References

- [ancestry](https://github.com/stefankroes/ancestry): Gem for threaded comments
- [Turbo Streams](https://turbo.hotwired.dev/handbook/streams): Real-time DOM updates
- [counter_culture](https://github.com/magnusvk/counter_culture): Counter caching
