# ActionCable Channels

## Overview

Channels are the core abstraction in ActionCable, encapsulating shared logic for WebSocket connections. They handle subscriptions, receive client data, and broadcast messages to subscribers.

## When to Use

- When implementing bidirectional communication
- When clients need to perform server actions
- When broadcasting to specific groups of users
- When implementing custom real-time features beyond Turbo Streams

## Quick Start

### Generate a Channel

```bash
bin/rails generate channel Chat speak
```

```ruby
# app/channels/chat_channel.rb
class ChatChannel < ApplicationCable::Channel
  def subscribed
    stream_from "chat_#{params[:room_id]}"
  end

  def unsubscribed
    # Cleanup when client disconnects
  end

  def speak(data)
    ActionCable.server.broadcast(
      "chat_#{params[:room_id]}",
      message: data["message"],
      user: current_user.name
    )
  end
end
```

```javascript
// app/javascript/channels/chat_channel.js
import consumer from "./consumer"

consumer.subscriptions.create(
  { channel: "ChatChannel", room_id: 1 },
  {
    received(data) {
      const messages = document.getElementById("messages")
      messages.insertAdjacentHTML("beforeend", `<p>${data.user}: ${data.message}</p>`)
    },

    speak(message) {
      this.perform("speak", { message: message })
    }
  }
)
```

## Main Patterns

### Pattern 1: Stream for Model

```ruby
# app/channels/post_channel.rb
class PostChannel < ApplicationCable::Channel
  def subscribed
    @post = Post.find(params[:id])
    stream_for @post
  end
end

# Broadcasting from anywhere
PostChannel.broadcast_to(@post, {
  action: "update",
  html: render_to_string(partial: "posts/post", locals: { post: @post })
})
```

### Pattern 2: User-specific Streams

```ruby
# app/channels/notifications_channel.rb
class NotificationsChannel < ApplicationCable::Channel
  def subscribed
    stream_for current_user
  end
end

# Broadcast to specific user
NotificationsChannel.broadcast_to(user, {
  type: "notification",
  title: "New message",
  body: "You have a new message"
})
```

### Pattern 3: Multiple Streams

```ruby
# app/channels/dashboard_channel.rb
class DashboardChannel < ApplicationCable::Channel
  def subscribed
    # Subscribe to multiple streams
    stream_from "dashboard_metrics"
    stream_from "dashboard_alerts"
    stream_from "dashboard_user_#{current_user.id}"
  end
end
```

### Pattern 4: Parameterized Subscriptions

```ruby
# app/channels/room_channel.rb
class RoomChannel < ApplicationCable::Channel
  def subscribed
    room = Room.find(params[:room_id])

    # Authorization check
    if room.member?(current_user)
      stream_for room
      @room = room
    else
      reject
    end
  end

  def receive(data)
    # Handle incoming data from client
    Message.create!(
      room: @room,
      user: current_user,
      body: data["body"]
    )
  end
end
```

### Pattern 5: Perform Actions from Client

```ruby
# app/channels/typing_channel.rb
class TypingChannel < ApplicationCable::Channel
  def subscribed
    @room = Room.find(params[:room_id])
    stream_for @room
  end

  def typing(data)
    TypingChannel.broadcast_to(
      @room,
      user_id: current_user.id,
      user_name: current_user.name,
      typing: data["typing"]
    )
  end

  def stop_typing
    TypingChannel.broadcast_to(
      @room,
      user_id: current_user.id,
      typing: false
    )
  end
end
```

```javascript
// Client-side
const channel = consumer.subscriptions.create(
  { channel: "TypingChannel", room_id: roomId },
  {
    received(data) {
      if (data.user_id !== currentUserId) {
        updateTypingIndicator(data)
      }
    },

    startTyping() {
      this.perform("typing", { typing: true })
    },

    stopTyping() {
      this.perform("stop_typing")
    }
  }
)

// Debounced typing indicator
let typingTimer
input.addEventListener("keydown", () => {
  channel.startTyping()
  clearTimeout(typingTimer)
  typingTimer = setTimeout(() => channel.stopTyping(), 1000)
})
```

### Pattern 6: Broadcasting with HTML

```ruby
# app/channels/comments_channel.rb
class CommentsChannel < ApplicationCable::Channel
  def subscribed
    @post = Post.find(params[:post_id])
    stream_for @post
  end
end

# In model or controller
class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user

  after_create_commit :broadcast_comment

  private

  def broadcast_comment
    CommentsChannel.broadcast_to(
      post,
      action: "created",
      html: ApplicationController.render(
        partial: "comments/comment",
        locals: { comment: self }
      )
    )
  end
end
```

```javascript
// Client-side with HTML insertion
consumer.subscriptions.create(
  { channel: "CommentsChannel", post_id: postId },
  {
    received(data) {
      if (data.action === "created") {
        document.getElementById("comments").insertAdjacentHTML("beforeend", data.html)
      }
    }
  }
)
```

### Pattern 7: Channel with State

```ruby
# app/channels/game_channel.rb
class GameChannel < ApplicationCable::Channel
  def subscribed
    @game = Game.find(params[:game_id])
    stream_for @game

    # Track player connection
    @game.player_connected(current_user)
    broadcast_game_state
  end

  def unsubscribed
    @game&.player_disconnected(current_user)
    broadcast_game_state if @game
  end

  def make_move(data)
    if @game.make_move(current_user, data["position"])
      broadcast_game_state
    else
      transmit(error: "Invalid move")
    end
  end

  private

  def broadcast_game_state
    GameChannel.broadcast_to(@game, @game.state)
  end
end
```

## Lifecycle Callbacks

| Callback | When Called |
|----------|-------------|
| `subscribed` | Client subscribes to channel |
| `unsubscribed` | Client disconnects or unsubscribes |

## Channel Methods

| Method | Purpose |
|--------|---------|
| `stream_from(name)` | Subscribe to named stream |
| `stream_for(model)` | Subscribe to model-based stream |
| `reject` | Reject subscription |
| `transmit(data)` | Send data to this client only |
| `stop_stream_from(name)` | Stop receiving from stream |
| `stop_all_streams` | Stop all streams |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No authorization in subscribed | Unauthorized access | Check permissions before streaming |
| Blocking operations in channel | Connection timeout | Use background jobs |
| Missing unsubscribed cleanup | Resource leaks | Clean up in unsubscribed |
| Transmitting sensitive data | Security risk | Filter data before sending |
| Not using stream_for with models | Naming conflicts | Use stream_for for model streams |

## Related Skills

- [setup.md](./setup.md): ActionCable configuration
- [connections.md](./connections.md): Connection authentication
- [../patterns/chat.md](../patterns/chat.md): Chat implementation
- [../patterns/notifications.md](../patterns/notifications.md): Notification patterns

## References

- [Action Cable Overview](https://guides.rubyonrails.org/action_cable_overview.html)
- [ActionCable Channel API](https://api.rubyonrails.org/classes/ActionCable/Channel/Base.html)
