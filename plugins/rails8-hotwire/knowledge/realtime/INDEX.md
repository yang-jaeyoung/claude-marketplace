---
name: rails8-realtime
description: Action Cable, Turbo Streams broadcasting, Solid Cable. Use when implementing real-time notifications, chat, and live updates.
triggers:
  - real-time
  - realtime
  - action cable
  - websocket
  - broadcast
  - solid cable
  - live update
  - chat
  - notification
  - 실시간
  - 액션 케이블
  - 웹소켓
  - 브로드캐스트
  - 채팅
  - 알림
summary: |
  Rails 8의 실시간 기능을 다룹니다. Action Cable, Turbo Streams 브로드캐스팅,
  Solid Cable(Redis 불필요)을 포함합니다. 실시간 알림, 채팅, 라이브 업데이트가
  필요할 때 참조하세요.
token_cost: high
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - turbo-streams/*.md
    - patterns/*.md
  deep:
    - "**/*.md"
    - "**/*.rb"
    - "**/*.js"
---

# Realtime: Real-time Features

## Overview

Covers real-time features in Rails 8. Includes Action Cable, Turbo Streams broadcasting, Solid Cable, and real-time UI patterns.

## When to Use

- When implementing real-time notifications
- When building chat features
- When live updates are needed
- When implementing collaborative features

## Core Principles

| Principle | Description |
|-----------|-------------|
| Minimal Broadcasting | Send only necessary data |
| Progressive Enhancement | Works without WebSocket |
| Permission Checks | Verify authorization on subscribe |
| Connection Management | Implement reconnection logic |

## Quick Start

### Solid Cable Setup (Rails 8 Default)

```yaml
# config/cable.yml
development:
  adapter: solid_cable
  polling_interval: 0.1
  message_retention: 1.day

production:
  adapter: solid_cable
  polling_interval: 0.1
  message_retention: 1.day
  # Or use Redis
  # adapter: redis
  # url: <%= ENV.fetch("REDIS_URL") %>
```

### Model Broadcasting

```ruby
# app/models/message.rb
class Message < ApplicationRecord
  belongs_to :room
  belongs_to :user

  # Automatic broadcast (create/update/destroy)
  broadcasts_to :room
end
```

```erb
<!-- app/views/rooms/show.html.erb -->
<%= turbo_stream_from @room %>

<div id="messages">
  <%= render @room.messages.includes(:user).recent %>
</div>

<%= form_with model: [@room, Message.new] do |f| %>
  <%= f.text_field :body %>
  <%= f.submit "Send" %>
<% end %>
```

## File Structure

```
realtime/
├── SKILL.md
├── action-cable/
│   ├── setup.md
│   ├── channels.md
│   ├── connections.md
│   └── deployment.md
├── turbo-streams/
│   ├── broadcasting.md
│   ├── model-callbacks.md
│   ├── custom-streams.md
│   └── authorization.md
├── patterns/
│   ├── chat.md
│   ├── notifications.md
│   ├── presence.md
│   ├── live-updates.md
│   └── collaborative.md
└── snippets/
    ├── notification_channel.rb
    ├── presence_channel.rb
    └── broadcastable.rb
```

## Main Patterns

### Pattern 1: Turbo Streams Broadcasting

```ruby
# app/models/comment.rb
class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user

  # Option 1: Automatic broadcast
  broadcasts_to :post

  # Option 2: Custom broadcast
  after_create_commit :broadcast_created
  after_update_commit :broadcast_updated
  after_destroy_commit :broadcast_destroyed

  private

  def broadcast_created
    broadcast_prepend_to post,
      target: "comments",
      partial: "comments/comment",
      locals: { comment: self }
  end

  def broadcast_updated
    broadcast_replace_to post,
      target: self,
      partial: "comments/comment",
      locals: { comment: self }
  end

  def broadcast_destroyed
    broadcast_remove_to post, target: self
  end
end
```

```erb
<!-- app/views/posts/show.html.erb -->
<%= turbo_stream_from @post %>

<article>
  <h1><%= @post.title %></h1>
  <p><%= @post.body %></p>
</article>

<section>
  <h2>Comments (<span id="comments_count"><%= @post.comments.count %></span>)</h2>

  <div id="comments">
    <%= render @post.comments.includes(:user) %>
  </div>

  <%= turbo_frame_tag "new_comment" do %>
    <%= render "comments/form", post: @post, comment: Comment.new %>
  <% end %>
</section>
```

### Pattern 2: Real-time Notifications

```ruby
# app/models/notification.rb
class Notification < ApplicationRecord
  belongs_to :user
  belongs_to :notifiable, polymorphic: true

  scope :unread, -> { where(read_at: nil) }
  scope :recent, -> { order(created_at: :desc).limit(20) }

  after_create_commit :broadcast_to_user

  def read!
    update(read_at: Time.current)
  end

  private

  def broadcast_to_user
    broadcast_prepend_to "notifications_#{user_id}",
      target: "notifications",
      partial: "notifications/notification"

    # Update counter
    broadcast_update_to "notifications_#{user_id}",
      target: "notifications_count",
      html: user.notifications.unread.count
  end
end
```

```erb
<!-- app/views/layouts/_notifications.html.erb -->
<div data-controller="notifications">
  <%= turbo_stream_from "notifications_#{current_user.id}" %>

  <button data-action="notifications#toggle">
    <span id="notifications_count" class="badge">
      <%= current_user.notifications.unread.count %>
    </span>
    Notifications
  </button>

  <div data-notifications-target="panel" class="hidden">
    <div id="notifications">
      <%= render current_user.notifications.recent %>
    </div>
  </div>
</div>
```

### Pattern 3: Chat Room

```ruby
# app/models/room.rb
class Room < ApplicationRecord
  has_many :messages, dependent: :destroy
  has_many :room_users, dependent: :destroy
  has_many :users, through: :room_users
end

# app/models/message.rb
class Message < ApplicationRecord
  belongs_to :room
  belongs_to :user

  broadcasts_to :room

  scope :recent, -> { order(created_at: :desc).limit(50) }

  after_create_commit :update_room_timestamp

  private

  def update_room_timestamp
    room.touch
  end
end
```

```ruby
# app/controllers/messages_controller.rb
class MessagesController < ApplicationController
  before_action :authenticate_user!
  before_action :set_room

  def create
    @message = @room.messages.build(message_params)
    @message.user = current_user

    respond_to do |format|
      if @message.save
        format.turbo_stream
        format.html { redirect_to @room }
      else
        format.turbo_stream do
          render turbo_stream: turbo_stream.replace(
            "message_form",
            partial: "messages/form",
            locals: { room: @room, message: @message }
          )
        end
      end
    end
  end

  private

  def set_room
    @room = Room.find(params[:room_id])
  end

  def message_params
    params.require(:message).permit(:body)
  end
end
```

```erb
<!-- app/views/rooms/show.html.erb -->
<div class="flex flex-col h-screen">
  <%= turbo_stream_from @room %>

  <header class="p-4 border-b">
    <h1><%= @room.name %></h1>
  </header>

  <div id="messages"
       class="flex-1 overflow-y-auto p-4 flex flex-col-reverse"
       data-controller="scroll-bottom">
    <%= render @room.messages.recent.includes(:user).reverse %>
  </div>

  <footer class="p-4 border-t">
    <div id="message_form">
      <%= render "messages/form", room: @room, message: Message.new %>
    </div>
  </footer>
</div>
```

### Pattern 4: Presence (Online Status)

```ruby
# app/channels/presence_channel.rb
class PresenceChannel < ApplicationCable::Channel
  def subscribed
    @room = Room.find(params[:room_id])
    stream_from "presence_#{@room.id}"

    # Store online status in Redis or memory
    add_user_to_room
    broadcast_presence
  end

  def unsubscribed
    remove_user_from_room
    broadcast_presence
  end

  private

  def add_user_to_room
    Rails.cache.write(
      presence_key,
      online_users.push(current_user.id).uniq,
      expires_in: 5.minutes
    )
  end

  def remove_user_from_room
    Rails.cache.write(
      presence_key,
      online_users - [current_user.id],
      expires_in: 5.minutes
    )
  end

  def online_users
    Rails.cache.read(presence_key) || []
  end

  def presence_key
    "room_#{@room.id}_presence"
  end

  def broadcast_presence
    users = User.where(id: online_users)

    ActionCable.server.broadcast(
      "presence_#{@room.id}",
      { type: "presence", users: users.map { |u| { id: u.id, name: u.name } } }
    )
  end
end
```

### Pattern 5: Custom Action Cable Channel

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      self.current_user = find_verified_user
    end

    private

    def find_verified_user
      if verified_user = User.find_by(id: cookies.encrypted[:user_id])
        verified_user
      else
        reject_unauthorized_connection
      end
    end
  end
end

# app/channels/notifications_channel.rb
class NotificationsChannel < ApplicationCable::Channel
  def subscribed
    stream_from "notifications_#{current_user.id}"
  end

  def mark_as_read(data)
    notification = current_user.notifications.find(data["id"])
    notification.read!

    # Broadcast counter update
    broadcast_unread_count
  end

  def mark_all_as_read
    current_user.notifications.unread.update_all(read_at: Time.current)
    broadcast_unread_count
  end

  private

  def broadcast_unread_count
    ActionCable.server.broadcast(
      "notifications_#{current_user.id}",
      { type: "count", count: current_user.notifications.unread.count }
    )
  end
end
```

```javascript
// app/javascript/channels/notifications_channel.js
import consumer from "./consumer"

consumer.subscriptions.create("NotificationsChannel", {
  received(data) {
    if (data.type === "count") {
      document.getElementById("notifications_count").textContent = data.count
    }
  },

  markAsRead(id) {
    this.perform("mark_as_read", { id: id })
  },

  markAllAsRead() {
    this.perform("mark_all_as_read")
  }
})
```

## Solid Cable vs Redis

| Criteria | Solid Cable | Redis |
|----------|-------------|-------|
| Setup | Zero configuration | Redis server required |
| Cost | Free | Redis hosting costs |
| Latency | ~100ms polling | ~1ms real-time |
| Scalability | Single server | Multi-server |
| Best for | Small apps | Large scale/low latency needed |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Subscribe without authorization | Data exposure | Check permissions in channel |
| Excessive broadcasting | Performance degradation | Send only necessary data |
| Synchronous broadcast | Response delay | Use after_commit |
| Connection leaks | Memory growth | Cleanup in unsubscribed |

## Related Skills

- [hotwire](../hotwire/SKILL.md): Turbo Streams basics
- [background](../background/): Async broadcasting (Phase 3)
- [deploy](../deploy/SKILL.md): Redis deployment

## References

- [Action Cable Overview](https://guides.rubyonrails.org/action_cable_overview.html)
- [Turbo Streams](https://turbo.hotwired.dev/handbook/streams)
- [Solid Cable GitHub](https://github.com/rails/solid_cable)
