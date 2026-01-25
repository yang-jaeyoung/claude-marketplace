# Turbo Streams Broadcasting

## Overview

Turbo Streams broadcasting enables real-time HTML updates via WebSockets. Instead of managing ActionCable channels directly, you broadcast HTML fragments that automatically update the DOM on connected clients.

## When to Use

- When pushing live updates to multiple users
- When implementing real-time lists (chat, notifications, feeds)
- When updating shared UI elements across sessions
- When using models as broadcast sources

## Quick Start

### Basic Broadcasting

```ruby
# Broadcasting from anywhere
Turbo::StreamsChannel.broadcast_append_to(
  "messages",
  target: "messages",
  partial: "messages/message",
  locals: { message: @message }
)
```

```erb
<!-- Subscribe in view -->
<%= turbo_stream_from "messages" %>

<div id="messages">
  <%= render @messages %>
</div>
```

## Main Patterns

### Pattern 1: broadcast_to Methods

```ruby
# Available broadcast methods
Turbo::StreamsChannel.broadcast_append_to(stream, target:, **options)
Turbo::StreamsChannel.broadcast_prepend_to(stream, target:, **options)
Turbo::StreamsChannel.broadcast_replace_to(stream, target:, **options)
Turbo::StreamsChannel.broadcast_update_to(stream, target:, **options)
Turbo::StreamsChannel.broadcast_remove_to(stream, target:)
Turbo::StreamsChannel.broadcast_before_to(stream, target:, **options)
Turbo::StreamsChannel.broadcast_after_to(stream, target:, **options)
Turbo::StreamsChannel.broadcast_refresh_to(stream)

# Options for content methods
# - partial: "path/to/partial"
# - locals: { key: value }
# - html: "<p>Raw HTML</p>"
```

### Pattern 2: Model-Scoped Streams

```ruby
# Broadcast to a model-based stream
class Comment < ApplicationRecord
  belongs_to :post

  after_create_commit :broadcast_create

  private

  def broadcast_create
    # Stream name becomes "posts:123" for post with id 123
    Turbo::StreamsChannel.broadcast_append_to(
      post,  # Model as stream identifier
      target: "comments",
      partial: "comments/comment",
      locals: { comment: self }
    )
  end
end
```

```erb
<!-- Subscribe to model stream -->
<%= turbo_stream_from @post %>

<div id="comments">
  <%= render @post.comments %>
</div>
```

### Pattern 3: Multiple Streams

```ruby
# Broadcast to multiple streams simultaneously
class Notification < ApplicationRecord
  belongs_to :user

  after_create_commit :broadcast_notification

  private

  def broadcast_notification
    # To user-specific stream
    Turbo::StreamsChannel.broadcast_prepend_to(
      "notifications:#{user_id}",
      target: "notifications",
      partial: "notifications/notification",
      locals: { notification: self }
    )

    # To admin dashboard
    Turbo::StreamsChannel.broadcast_update_to(
      "admin_dashboard",
      target: "notification_count",
      html: Notification.unread.count.to_s
    )
  end
end
```

### Pattern 4: Controller Broadcasting

```ruby
class MessagesController < ApplicationController
  def create
    @message = @room.messages.create!(message_params.merge(user: current_user))

    respond_to do |format|
      format.turbo_stream do
        # Broadcast to all room subscribers
        Turbo::StreamsChannel.broadcast_append_to(
          @room,
          target: "messages",
          partial: "messages/message",
          locals: { message: @message }
        )

        # Response for current user (form reset)
        render turbo_stream: turbo_stream.replace(
          "message_form",
          partial: "messages/form",
          locals: { room: @room, message: Message.new }
        )
      end
      format.html { redirect_to @room }
    end
  end
end
```

### Pattern 5: Broadcasting with Targeting

```ruby
class Task < ApplicationRecord
  belongs_to :project

  after_update_commit :broadcast_update

  private

  def broadcast_update
    # Replace entire element
    Turbo::StreamsChannel.broadcast_replace_to(
      project,
      target: dom_id(self),
      partial: "tasks/task",
      locals: { task: self }
    )

    # Also update project progress
    Turbo::StreamsChannel.broadcast_update_to(
      project,
      target: "project_progress",
      partial: "projects/progress",
      locals: { project: project }
    )
  end
end
```

### Pattern 6: Conditional Broadcasting

```ruby
class Post < ApplicationRecord
  after_update_commit :broadcast_if_published

  private

  def broadcast_if_published
    return unless saved_change_to_published? && published?

    # Broadcast only when post becomes published
    Turbo::StreamsChannel.broadcast_prepend_to(
      "public_posts",
      target: "posts",
      partial: "posts/post",
      locals: { post: self }
    )
  end
end
```

### Pattern 7: Broadcasting Raw HTML

```ruby
# When you don't have a partial
Turbo::StreamsChannel.broadcast_update_to(
  "dashboard",
  target: "online_count",
  html: "<span class='badge'>#{User.online.count}</span>"
)

# With turbo_stream helper
Turbo::StreamsChannel.broadcast_render_to(
  "dashboard",
  turbo_stream: turbo_stream.update("status", html: "Online")
)
```

### Pattern 8: Rendering in Background Jobs

```ruby
# app/jobs/broadcast_job.rb
class BroadcastJob < ApplicationJob
  queue_as :default

  def perform(stream, action, target, partial, locals)
    Turbo::StreamsChannel.public_send(
      "broadcast_#{action}_to",
      stream,
      target: target,
      partial: partial,
      locals: locals
    )
  end
end

# Usage
BroadcastJob.perform_later(
  "dashboard",
  "update",
  "metrics",
  "dashboard/metrics",
  { metrics: calculate_metrics }
)
```

### Pattern 9: Broadcast Refresh (Rails 8 Morphing)

```ruby
# Trigger a full page morph for all subscribers
Turbo::StreamsChannel.broadcast_refresh_to("dashboard")

# In view with morphing enabled
<head>
  <meta name="turbo-refresh-method" content="morph">
  <meta name="turbo-refresh-scroll" content="preserve">
</head>

<%= turbo_stream_from "dashboard" %>
```

### Pattern 10: Scoped Streams with Parameters

```ruby
# Create parameterized stream names
def stream_for_user_notifications(user)
  "notifications:user:#{user.id}"
end

def stream_for_project_tasks(project, filter = "all")
  "tasks:project:#{project.id}:#{filter}"
end

# Subscribe
<%= turbo_stream_from stream_for_user_notifications(current_user) %>
<%= turbo_stream_from stream_for_project_tasks(@project, @filter) %>
```

## Broadcast Methods Summary

| Method | Action | Use Case |
|--------|--------|----------|
| `broadcast_append_to` | Add to end | New items in list |
| `broadcast_prepend_to` | Add to start | New messages, notifications |
| `broadcast_replace_to` | Replace element | Updated item |
| `broadcast_update_to` | Update inner HTML | Counters, status |
| `broadcast_remove_to` | Delete element | Deleted item |
| `broadcast_before_to` | Insert before | Ordered insertion |
| `broadcast_after_to` | Insert after | Ordered insertion |
| `broadcast_refresh_to` | Full page morph | Complex updates |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Broadcasting synchronously in request | Slow response | Use after_commit callbacks |
| Large HTML in broadcasts | Bandwidth waste | Use targeted partials |
| No target ID check | Silent failures | Verify target exists in DOM |
| Hardcoded stream names | Inflexible | Use model-based streams |
| Missing stream subscription | Updates not received | Add turbo_stream_from |

## Related Skills

- [model-callbacks.md](./model-callbacks.md): Automatic model broadcasting
- [authorization.md](./authorization.md): Securing streams
- [../action-cable/channels.md](../action-cable/channels.md): Custom channels

## References

- [Turbo Streams Handbook](https://turbo.hotwired.dev/handbook/streams)
- [Turbo Rails Broadcasting](https://github.com/hotwired/turbo-rails#broadcasting)
