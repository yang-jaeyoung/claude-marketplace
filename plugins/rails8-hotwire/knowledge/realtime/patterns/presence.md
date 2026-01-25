# Online Status & Presence Tracking

## Overview

Presence tracking shows which users are online in real-time. This pattern is essential for chat applications, collaborative tools, and any feature requiring awareness of active users.

## When to Use

- When showing online/offline status indicators
- When displaying "X users viewing this page"
- When building collaborative editing features
- When showing typing indicators

## Quick Start

### Basic Presence Channel

```ruby
# app/channels/presence_channel.rb
class PresenceChannel < ApplicationCable::Channel
  def subscribed
    @room = Room.find(params[:room_id])
    stream_for @room

    add_user
    broadcast_presence
  end

  def unsubscribed
    remove_user
    broadcast_presence
  end

  private

  def add_user
    online_user_ids << current_user.id
    Rails.cache.write(presence_key, online_user_ids.uniq, expires_in: 5.minutes)
  end

  def remove_user
    Rails.cache.write(presence_key, online_user_ids - [current_user.id], expires_in: 5.minutes)
  end

  def online_user_ids
    Rails.cache.read(presence_key) || []
  end

  def presence_key
    "room:#{@room.id}:presence"
  end

  def broadcast_presence
    users = User.where(id: online_user_ids).select(:id, :name, :avatar_url)

    PresenceChannel.broadcast_to(@room, {
      type: "presence",
      users: users.map { |u| { id: u.id, name: u.name, avatar_url: u.avatar_url } },
      count: users.size
    })
  end
end
```

## Main Patterns

### Pattern 1: Redis-based Presence (Production-Ready)

```ruby
# app/services/presence_tracker.rb
class PresenceTracker
  HEARTBEAT_INTERVAL = 30.seconds
  PRESENCE_TIMEOUT = 2.minutes

  def initialize(scope:)
    @scope = scope
    @key = "presence:#{scope}"
  end

  def join(user)
    redis.zadd(@key, Time.current.to_f, user.id)
    cleanup_stale
    broadcast
  end

  def leave(user)
    redis.zrem(@key, user.id)
    broadcast
  end

  def heartbeat(user)
    redis.zadd(@key, Time.current.to_f, user.id)
    cleanup_stale
  end

  def online_users
    user_ids = redis.zrangebyscore(
      @key,
      (Time.current - PRESENCE_TIMEOUT).to_f,
      "+inf"
    )
    User.where(id: user_ids)
  end

  def online_count
    redis.zcount(
      @key,
      (Time.current - PRESENCE_TIMEOUT).to_f,
      "+inf"
    )
  end

  private

  def redis
    @redis ||= Redis.new
  end

  def cleanup_stale
    cutoff = (Time.current - PRESENCE_TIMEOUT).to_f
    redis.zremrangebyscore(@key, "-inf", cutoff)
  end

  def broadcast
    ActionCable.server.broadcast(@key, {
      type: "presence_update",
      users: online_users.map { |u| serialize_user(u) },
      count: online_count
    })
  end

  def serialize_user(user)
    { id: user.id, name: user.name, avatar: user.avatar_url }
  end
end
```

### Pattern 2: Presence Channel with Heartbeat

```ruby
# app/channels/presence_channel.rb
class PresenceChannel < ApplicationCable::Channel
  def subscribed
    @tracker = PresenceTracker.new(scope: "room:#{params[:room_id]}")
    stream_from "presence:room:#{params[:room_id]}"

    @tracker.join(current_user)
  end

  def unsubscribed
    @tracker&.leave(current_user)
  end

  def heartbeat
    @tracker&.heartbeat(current_user)
  end
end
```

```javascript
// app/javascript/channels/presence_channel.js
import consumer from "./consumer"

export function createPresenceChannel(roomId, onPresenceUpdate) {
  let heartbeatInterval

  const channel = consumer.subscriptions.create(
    { channel: "PresenceChannel", room_id: roomId },
    {
      connected() {
        heartbeatInterval = setInterval(() => {
          this.perform("heartbeat")
        }, 25000) // 25 seconds
      },

      disconnected() {
        clearInterval(heartbeatInterval)
      },

      received(data) {
        if (data.type === "presence_update") {
          onPresenceUpdate(data.users, data.count)
        }
      }
    }
  )

  return channel
}
```

### Pattern 3: Turbo Streams Presence Updates

```ruby
# app/channels/presence_channel.rb
class PresenceChannel < ApplicationCable::Channel
  def subscribed
    @room = Room.find(params[:room_id])
    stream_for @room

    add_user
    broadcast_presence_html
  end

  private

  def broadcast_presence_html
    users = User.where(id: online_user_ids)

    Turbo::StreamsChannel.broadcast_update_to(
      @room,
      target: "online_users",
      partial: "rooms/online_users",
      locals: { users: users }
    )

    Turbo::StreamsChannel.broadcast_update_to(
      @room,
      target: "online_count",
      html: users.size.to_s
    )
  end
end
```

```erb
<!-- app/views/rooms/_online_users.html.erb -->
<div class="flex -space-x-2">
  <% users.limit(5).each do |user| %>
    <div class="relative" title="<%= user.name %>">
      <%= image_tag user.avatar_url,
                    class: "w-8 h-8 rounded-full border-2 border-white",
                    alt: user.name %>
      <span class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></span>
    </div>
  <% end %>

  <% if users.size > 5 %>
    <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium">
      +<%= users.size - 5 %>
    </div>
  <% end %>
</div>
```

### Pattern 4: User Status Indicators

```ruby
# app/models/user.rb
class User < ApplicationRecord
  enum status: { offline: 0, online: 1, away: 2, busy: 3 }

  def update_presence(status)
    update(status: status, last_seen_at: Time.current)
    broadcast_status_change
  end

  def online?
    last_seen_at && last_seen_at > 2.minutes.ago
  end

  private

  def broadcast_status_change
    # Broadcast to all friends/contacts
    friends.each do |friend|
      Turbo::StreamsChannel.broadcast_update_to(
        "user:#{friend.id}:contacts",
        target: "user_#{id}_status",
        partial: "users/status_indicator",
        locals: { user: self }
      )
    end
  end
end
```

```erb
<!-- app/views/users/_status_indicator.html.erb -->
<span id="user_<%= user.id %>_status"
      class="inline-flex items-center gap-1">
  <span class="w-2 h-2 rounded-full
    <%= case user.status
        when 'online' then 'bg-green-500'
        when 'away' then 'bg-yellow-500'
        when 'busy' then 'bg-red-500'
        else 'bg-gray-400'
        end %>">
  </span>
  <span class="text-xs text-gray-500">
    <%= user.status.humanize %>
  </span>
</span>
```

### Pattern 5: Page Viewer Count

```ruby
# app/channels/page_presence_channel.rb
class PagePresenceChannel < ApplicationCable::Channel
  def subscribed
    @page_key = "page:#{params[:path]}"
    stream_from @page_key

    increment_viewers
    broadcast_count
  end

  def unsubscribed
    decrement_viewers
    broadcast_count
  end

  private

  def increment_viewers
    Rails.cache.increment(@page_key, 1, initial: 0, expires_in: 1.hour)
  end

  def decrement_viewers
    count = Rails.cache.decrement(@page_key, 1)
    Rails.cache.delete(@page_key) if count && count <= 0
  end

  def viewer_count
    Rails.cache.read(@page_key) || 0
  end

  def broadcast_count
    ActionCable.server.broadcast(@page_key, {
      type: "viewer_count",
      count: viewer_count
    })
  end
end
```

```erb
<!-- In any page -->
<div data-controller="page-presence"
     data-page-presence-path-value="<%= request.path %>">
  <span id="viewer_count" data-page-presence-target="count">0</span> viewing
</div>
```

### Pattern 6: Collaborative Cursor Tracking

```ruby
# app/channels/cursor_channel.rb
class CursorChannel < ApplicationCable::Channel
  def subscribed
    @document = Document.find(params[:document_id])
    stream_for @document
  end

  def move(data)
    CursorChannel.broadcast_to(@document, {
      type: "cursor_move",
      user_id: current_user.id,
      user_name: current_user.name,
      user_color: user_color,
      x: data["x"],
      y: data["y"]
    })
  end

  def selection(data)
    CursorChannel.broadcast_to(@document, {
      type: "selection",
      user_id: current_user.id,
      user_name: current_user.name,
      user_color: user_color,
      start: data["start"],
      end: data["end"]
    })
  end

  private

  def user_color
    # Consistent color per user
    colors = %w[#ef4444 #f97316 #eab308 #22c55e #14b8a6 #3b82f6 #8b5cf6 #ec4899]
    colors[current_user.id % colors.length]
  end
end
```

```javascript
// app/javascript/controllers/collaborative_cursor_controller.js
import { Controller } from "@hotwired/stimulus"
import consumer from "../channels/consumer"

export default class extends Controller {
  static values = { documentId: Number, currentUserId: Number }

  connect() {
    this.cursors = new Map()
    this.channel = this.createChannel()
    this.element.addEventListener("mousemove", this.handleMouseMove.bind(this))
  }

  createChannel() {
    return consumer.subscriptions.create(
      { channel: "CursorChannel", document_id: this.documentIdValue },
      {
        received: (data) => this.handleReceived(data)
      }
    )
  }

  handleMouseMove(event) {
    const rect = this.element.getBoundingClientRect()
    this.channel.perform("move", {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    })
  }

  handleReceived(data) {
    if (data.user_id === this.currentUserIdValue) return

    if (data.type === "cursor_move") {
      this.updateCursor(data)
    }
  }

  updateCursor(data) {
    let cursor = this.cursors.get(data.user_id)

    if (!cursor) {
      cursor = this.createCursorElement(data)
      this.cursors.set(data.user_id, cursor)
    }

    cursor.style.transform = `translate(${data.x}px, ${data.y}px)`
  }

  createCursorElement(data) {
    const cursor = document.createElement("div")
    cursor.className = "absolute pointer-events-none transition-transform duration-75"
    cursor.style.color = data.user_color

    // Create SVG element safely
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
    svg.setAttribute("class", "w-4 h-4")
    svg.setAttribute("viewBox", "0 0 24 24")
    svg.setAttribute("fill", "currentColor")

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path")
    path.setAttribute("d", "M4 4l16 8-8 4-4 8-4-20z")
    svg.appendChild(path)

    // Create label safely
    const label = document.createElement("span")
    label.className = "text-xs text-white px-1 rounded"
    label.style.background = data.user_color
    label.textContent = data.user_name

    cursor.appendChild(svg)
    cursor.appendChild(label)
    this.element.appendChild(cursor)

    return cursor
  }
}
```

### Pattern 7: Activity Status with Solid Cache

```ruby
# app/models/concerns/trackable_presence.rb
module TrackablePresence
  extend ActiveSupport::Concern

  included do
    after_commit :update_presence_cache, on: [:create, :update]
  end

  class_methods do
    def online
      online_ids = Rails.cache.read("online_users") || []
      where(id: online_ids)
    end
  end

  def mark_as_online
    online_ids = Rails.cache.read("online_users") || []
    online_ids = (online_ids + [id]).uniq
    Rails.cache.write("online_users", online_ids, expires_in: 5.minutes)
    Rails.cache.write("user:#{id}:last_seen", Time.current, expires_in: 5.minutes)
  end

  def last_seen_at
    Rails.cache.read("user:#{id}:last_seen")
  end

  private

  def update_presence_cache
    mark_as_online if Current.user == self
  end
end
```

## Cleanup Strategies

```ruby
# app/jobs/presence_cleanup_job.rb
class PresenceCleanupJob < ApplicationJob
  queue_as :low

  def perform
    # Clean stale presence entries from Redis
    pattern = "presence:*"

    Redis.new.scan_each(match: pattern) do |key|
      cutoff = (Time.current - 5.minutes).to_f
      Redis.new.zremrangebyscore(key, "-inf", cutoff)
    end
  end
end

# Schedule with Solid Queue
# config/recurring.yml
cleanup_presence:
  class: PresenceCleanupJob
  queue: low
  schedule: every 5 minutes
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Database-backed presence | Too many writes | Use Redis/cache |
| No heartbeat | Stale presence data | Implement heartbeat |
| Broadcasting on every move | Excessive traffic | Throttle/debounce |
| No cleanup | Memory leaks | Periodic cleanup job |
| Global presence tracking | Privacy concerns | Scope to rooms/contexts |

## Related Skills

- [chat.md](./chat.md): Chat implementation
- [collaborative.md](./collaborative.md): Collaborative editing
- [../action-cable/channels.md](../action-cable/channels.md): Channel patterns

## References

- [Action Cable Overview](https://guides.rubyonrails.org/action_cable_overview.html)
- [Redis Sorted Sets](https://redis.io/docs/data-types/sorted-sets/)
