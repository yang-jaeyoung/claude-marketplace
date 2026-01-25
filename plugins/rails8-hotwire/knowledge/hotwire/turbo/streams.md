# Turbo Streams

## Overview

Turbo Streams deliver page changes as fragments of HTML wrapped in `<turbo-stream>` elements. They can update multiple parts of a page simultaneously in response to form submissions or over WebSocket.

## 8 Stream Actions

| Action | Description | Target |
|--------|-------------|--------|
| `append` | Add to end of target | Container element |
| `prepend` | Add to start of target | Container element |
| `replace` | Replace entire element | Target element |
| `update` | Replace inner HTML only | Target element |
| `remove` | Delete element | Target element |
| `before` | Insert before target | Target element |
| `after` | Insert after target | Target element |
| `refresh` | Refresh the page | N/A (Rails 8) |

## Basic Usage

### Controller Response

```ruby
# app/controllers/posts_controller.rb
def create
  @post = Post.create(post_params)

  respond_to do |format|
    format.turbo_stream
    format.html { redirect_to @post }
  end
end
```

### Stream Template

```erb
<!-- app/views/posts/create.turbo_stream.erb -->
<%= turbo_stream.prepend "posts", @post %>
<%= turbo_stream.update "posts_count", Post.count %>
```

## All Actions Examples

```erb
<!-- Append to end -->
<%= turbo_stream.append "messages", @message %>

<!-- Prepend to start -->
<%= turbo_stream.prepend "notifications" do %>
  <div class="notification"><%= @notification.text %></div>
<% end %>

<!-- Replace entire element -->
<%= turbo_stream.replace @post %>
<%= turbo_stream.replace dom_id(@post), partial: "posts/post", locals: { post: @post } %>

<!-- Update inner content only -->
<%= turbo_stream.update "counter", "5" %>
<%= turbo_stream.update "flash", partial: "shared/flash" %>

<!-- Remove element -->
<%= turbo_stream.remove @post %>
<%= turbo_stream.remove "temporary_message" %>

<!-- Insert before target -->
<%= turbo_stream.before @post do %>
  <div class="separator"></div>
<% end %>

<!-- Insert after target -->
<%= turbo_stream.after @post, partial: "posts/comments_summary" %>

<!-- Refresh page (Rails 8) -->
<%= turbo_stream.refresh %>
```

## Multiple Updates

```ruby
# Controller
def create
  @comment = @post.comments.create(comment_params)

  respond_to do |format|
    format.turbo_stream do
      render turbo_stream: [
        turbo_stream.append("comments", @comment),
        turbo_stream.update("comments_count", @post.comments.count),
        turbo_stream.update("flash", partial: "shared/flash"),
        turbo_stream.replace("comment_form", partial: "comments/form", locals: { comment: Comment.new })
      ]
    end
  end
end
```

## Inline Stream Responses

```ruby
def destroy
  @post.destroy

  respond_to do |format|
    format.turbo_stream { render turbo_stream: turbo_stream.remove(@post) }
    format.html { redirect_to posts_path }
  end
end
```

## Custom Targets

```erb
<!-- Target by DOM ID -->
<%= turbo_stream.append "posts", @post %>

<!-- Target uses dom_id automatically -->
<%= turbo_stream.replace @post %>
<!-- Equivalent to: turbo_stream.replace dom_id(@post), @post -->

<!-- Custom target ID -->
<%= turbo_stream.update "sidebar_stats" do %>
  <span><%= @stats.total %> items</span>
<% end %>
```

## Streaming from Model Callbacks

```ruby
# app/models/message.rb
class Message < ApplicationRecord
  belongs_to :conversation

  after_create_commit -> {
    broadcast_append_to conversation, target: "messages"
  }

  after_update_commit -> {
    broadcast_replace_to conversation
  }

  after_destroy_commit -> {
    broadcast_remove_to conversation
  }
end
```

```erb
<!-- Subscribe to broadcasts -->
<%= turbo_stream_from @conversation %>

<div id="messages">
  <%= render @messages %>
</div>
```

## Broadcast Methods

```ruby
# Available broadcast methods
@message.broadcast_append_to(streamable, **options)
@message.broadcast_prepend_to(streamable, **options)
@message.broadcast_replace_to(streamable, **options)
@message.broadcast_update_to(streamable, **options)
@message.broadcast_remove_to(streamable)
@message.broadcast_refresh_to(streamable)

# With custom partial
@message.broadcast_append_to(
  @conversation,
  target: "messages",
  partial: "messages/message",
  locals: { message: @message, show_timestamp: true }
)

# Later broadcast (async)
@message.broadcast_append_later_to(@conversation, target: "messages")
```

## Accept Header

Turbo automatically sends the correct Accept header:

```
Accept: text/vnd.turbo-stream.html, text/html, application/xhtml+xml
```

Rails `respond_to` handles this automatically.

## JavaScript Events

```javascript
// Before stream element is rendered
document.addEventListener("turbo:before-stream-render", (event) => {
  const fallbackToDefaultActions = event.detail.render

  event.detail.render = (streamElement) => {
    // Custom rendering logic
    fallbackToDefaultActions(streamElement)
  }
})
```

## Custom Actions

```javascript
// Register custom stream action
Turbo.StreamActions.highlight = function() {
  this.targetElements.forEach(element => {
    element.classList.add("highlight")
    setTimeout(() => element.classList.remove("highlight"), 2000)
  })
}
```

```erb
<!-- Use custom action -->
<turbo-stream action="highlight" target="post_1"></turbo-stream>
```

## Common Patterns

### Flash Messages

```erb
<!-- layout -->
<div id="flash">
  <%= render "shared/flash" %>
</div>

<!-- In stream response -->
<%= turbo_stream.update "flash", partial: "shared/flash" %>
```

### Counter Updates

```erb
<span id="unread_count"><%= current_user.unread_count %></span>

<!-- In stream response -->
<%= turbo_stream.update "unread_count", current_user.unread_count %>
```

### Empty State

```erb
<div id="posts">
  <% if @posts.empty? %>
    <div id="empty_state">No posts yet</div>
  <% else %>
    <%= render @posts %>
  <% end %>
</div>

<!-- After creating first post -->
<%= turbo_stream.remove "empty_state" %>
<%= turbo_stream.append "posts", @post %>
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Stream not rendering | Wrong response format | Check `respond_to` includes `format.turbo_stream` |
| Target not found | ID mismatch | Verify target ID exists in DOM |
| Partial not rendering | Missing locals | Pass all required locals |
| Broadcast not received | Not subscribed | Add `turbo_stream_from` |

## Related

- [drive.md](./drive.md): Full page navigation
- [frames.md](./frames.md): Frame-based updates
- [../../realtime/](../../realtime/): WebSocket integration
