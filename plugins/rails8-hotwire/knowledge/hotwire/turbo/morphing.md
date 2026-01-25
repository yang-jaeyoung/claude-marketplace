# Turbo Morphing (Rails 8)

## Overview

Turbo 8 introduces page refresh with morphing, which intelligently updates the DOM by comparing the current page with the new one and only changing what's different. This preserves scroll position, form state, and element focus.

## Enabling Morphing

```erb
<!-- app/views/layouts/application.html.erb -->
<head>
  <meta name="turbo-refresh-method" content="morph">
  <meta name="turbo-refresh-scroll" content="preserve">
  <%= yield :head %>
</head>
```

## Refresh Methods

| Method | Description |
|--------|-------------|
| `replace` | Replace entire body (default Turbo behavior) |
| `morph` | Intelligently diff and patch DOM |

## Scroll Behavior

| Behavior | Description |
|----------|-------------|
| `reset` | Scroll to top (default) |
| `preserve` | Keep current scroll position |

## Per-Page Configuration

```erb
<!-- Override for specific page -->
<% content_for :head do %>
  <meta name="turbo-refresh-method" content="replace">
<% end %>
```

## Permanent Elements

Elements with `data-turbo-permanent` are never replaced during morphing.

```erb
<!-- Video player that shouldn't restart -->
<div id="video-player" data-turbo-permanent>
  <video src="<%= @video.url %>" controls></video>
</div>

<!-- Sidebar with user state -->
<aside id="sidebar" data-turbo-permanent>
  <%= render "sidebar" %>
</aside>
```

## Turbo Stream Refresh

```erb
<!-- Trigger page refresh from stream -->
<%= turbo_stream.refresh %>

<!-- Refresh with specific ID (deduplication) -->
<%= turbo_stream.refresh id: "unique_refresh_id" %>
```

```ruby
# From controller
def update
  @post.update(post_params)

  respond_to do |format|
    format.turbo_stream { render turbo_stream: turbo_stream.refresh }
  end
end
```

## Broadcasting Refresh

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  after_update_commit -> { broadcast_refresh }
  after_destroy_commit -> { broadcast_refresh }

  # Or with specific stream
  after_update_commit -> { broadcast_refresh_to "posts" }
end
```

```erb
<!-- Subscribe to refreshes -->
<%= turbo_stream_from "posts" %>
```

## Suppressing Refreshes

```ruby
# Temporarily suppress broadcasts
Post.suppressing_turbo_broadcasts do
  # These changes won't trigger broadcasts
  Post.update_all(views_count: 0)
end
```

## Morphing vs Replace

### When to Use Morphing

- Real-time collaborative editing
- Live dashboards with frequent updates
- Pages with media players
- Forms with unsaved data
- Infinite scroll lists

### When to Use Replace

- Full page navigations
- Pages with complex JavaScript state
- Authentication state changes
- Major layout changes

## Idiomorph Library

Turbo 8 uses [Idiomorph](https://github.com/bigskysoftware/idiomorph) for DOM diffing.

### How It Works

1. Compares old and new DOM trees
2. Identifies nodes by `id` attribute
3. Moves, updates, or removes nodes as needed
4. Preserves focus and scroll position

### Best Practices

```erb
<!-- Always use IDs for morphing efficiency -->
<div id="<%= dom_id(post) %>">
  <%= render post %>
</div>

<!-- Use dom_id helper consistently -->
<%= turbo_frame_tag dom_id(@post) do %>
  <!-- content -->
<% end %>
```

## Form Preservation

Forms in morphed pages preserve their state:

```erb
<%= form_with model: @post, id: "post_form" do |f| %>
  <!-- User's typed content preserved during refresh -->
  <%= f.text_field :title %>
  <%= f.text_area :body %>
  <%= f.submit %>
<% end %>
```

## JavaScript Integration

```javascript
// Listen for morph events
document.addEventListener("turbo:morph", (event) => {
  console.log("Page morphed")
})

document.addEventListener("turbo:morph-element", (event) => {
  const { target, newElement } = event.detail
  console.log("Element morphed:", target.id)
})
```

## Excluding Elements from Morph

```erb
<!-- Never morph this element, but still replace it -->
<div data-turbo-permanent="false" id="temp_state">
  <!-- This gets replaced, not morphed -->
</div>
```

## Common Patterns

### Live Counter

```erb
<div id="live_stats" data-controller="polling" data-polling-interval-value="5000">
  <span id="visitor_count"><%= @visitor_count %></span> visitors
</div>
```

### Collaborative Editing

```ruby
# When any user saves
after_save_commit -> { broadcast_refresh_to document }
```

```erb
<%= turbo_stream_from @document %>

<div id="editor" data-turbo-permanent>
  <!-- Editor preserves cursor position -->
</div>

<div id="content">
  <!-- This gets morphed with latest content -->
  <%= @document.content %>
</div>
```

## Debugging Morphing

```javascript
// Log all morph operations
document.addEventListener("turbo:before-morph-element", (event) => {
  console.log("Will morph:", event.target.id)
  // event.preventDefault() to skip morphing this element
})

document.addEventListener("turbo:before-morph-attribute", (event) => {
  const { attributeName, mutationType } = event.detail
  console.log(`Attribute ${mutationType}: ${attributeName}`)
})
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Element flickering | Missing ID | Add stable `id` attribute |
| State lost | No permanent marker | Add `data-turbo-permanent` |
| Scroll jumping | Missing scroll preserve | Add meta tag |
| Form reset | Morphing conflict | Mark form permanent or use frames |

## Related

- [drive.md](./drive.md): Page navigation
- [streams.md](./streams.md): Stream updates
- [../../realtime/](../../realtime/): Real-time broadcasting
