# Turbo Frames

## Overview

Turbo Frames decompose pages into independent contexts that can be lazily loaded and updated independently. They enable partial page updates without full page reloads.

## Basic Usage

```erb
<!-- Define a frame -->
<%= turbo_frame_tag "posts" do %>
  <%= render @posts %>
<% end %>

<!-- Links inside frame update only the frame -->
<%= turbo_frame_tag "post_1" do %>
  <h2>Post Title</h2>
  <%= link_to "Edit", edit_post_path(@post) %>
<% end %>
```

## Frame Matching

When a link inside a frame is clicked, Turbo looks for a matching frame ID in the response.

```erb
<!-- posts/show.html.erb -->
<%= turbo_frame_tag dom_id(@post) do %>
  <h1><%= @post.title %></h1>
  <%= link_to "Edit", edit_post_path(@post) %>
<% end %>

<!-- posts/edit.html.erb -->
<%= turbo_frame_tag dom_id(@post) do %>
  <%= form_with model: @post do |f| %>
    <%= f.text_field :title %>
    <%= f.submit %>
    <%= link_to "Cancel", @post %>
  <% end %>
<% end %>
```

## Breaking Out of Frames

```erb
<!-- Target the whole page -->
<%= link_to "Full Page", post_path(@post), data: { turbo_frame: "_top" } %>

<!-- Target a different frame -->
<%= link_to "Load Here", other_path, data: { turbo_frame: "sidebar" } %>

<!-- Target parent frame -->
<%= link_to "Parent", parent_path, data: { turbo_frame: "_parent" } %>
```

## Lazy Loading

```erb
<!-- Load content on demand -->
<%= turbo_frame_tag "comments",
    src: post_comments_path(@post),
    loading: :lazy do %>
  <p>Loading comments...</p>
<% end %>

<!-- Eager loading (default) -->
<%= turbo_frame_tag "stats",
    src: stats_path,
    loading: :eager do %>
  <div class="skeleton">Loading...</div>
<% end %>
```

## Frame with Form

```erb
<%= turbo_frame_tag "new_comment" do %>
  <%= form_with model: [@post, Comment.new] do |f| %>
    <%= f.text_area :body %>
    <%= f.submit "Add Comment" %>
  <% end %>
<% end %>
```

Controller response after successful create:

```erb
<!-- comments/create.turbo_stream.erb -->
<%= turbo_stream.append "comments", @comment %>
<%= turbo_stream.replace "new_comment" do %>
  <%= render "form", post: @post, comment: Comment.new %>
<% end %>
```

## Frame Navigation

```erb
<!-- Promote frame navigation to browser URL -->
<%= turbo_frame_tag "main",
    data: { turbo_action: "advance" } do %>
  <!-- Content updates browser URL -->
<% end %>
```

## Refreshing Frames

```erb
<!-- Auto-refresh frame -->
<%= turbo_frame_tag "notifications",
    src: notifications_path,
    refresh: :morph do %>
<% end %>
```

```javascript
// Manual refresh via JavaScript
const frame = document.querySelector("turbo-frame#notifications")
frame.reload()
```

## Frame Events

```javascript
// Frame load started
document.addEventListener("turbo:frame-load", (event) => {
  console.log("Frame loaded:", event.target.id)
})

// Frame render complete
document.addEventListener("turbo:frame-render", (event) => {
  console.log("Frame rendered:", event.target.id)
})

// Frame missing (no matching frame in response)
document.addEventListener("turbo:frame-missing", (event) => {
  event.preventDefault()
  // Handle missing frame
})
```

## Patterns

### Inline Editing

```erb
<!-- show.html.erb -->
<%= turbo_frame_tag dom_id(@article) do %>
  <article>
    <h1><%= @article.title %></h1>
    <p><%= @article.body %></p>
    <%= link_to "Edit", edit_article_path(@article) %>
  </article>
<% end %>

<!-- edit.html.erb -->
<%= turbo_frame_tag dom_id(@article) do %>
  <%= form_with model: @article do |f| %>
    <%= f.text_field :title %>
    <%= f.text_area :body %>
    <%= f.submit "Save" %>
    <%= link_to "Cancel", @article %>
  <% end %>
<% end %>
```

### Modal in Frame

```erb
<!-- Main page -->
<%= turbo_frame_tag "modal" %>

<%= link_to "Open Modal", new_post_path, data: { turbo_frame: "modal" } %>

<!-- new.html.erb -->
<%= turbo_frame_tag "modal" do %>
  <div class="modal">
    <%= form_with model: @post do |f| %>
      <!-- form fields -->
    <% end %>
  </div>
<% end %>
```

### Pagination

```erb
<%= turbo_frame_tag "posts" do %>
  <%= render @posts %>
  <%= paginate @posts %>
<% end %>
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Frame not updating | ID mismatch | Check frame IDs match |
| Links navigate whole page | Outside frame context | Wrap in turbo_frame_tag |
| Form errors don't show | Missing status code | Return `status: :unprocessable_entity` |
| Nested frames conflict | Incorrect targeting | Use explicit `data-turbo-frame` |

## Related

- [drive.md](./drive.md): Full page navigation
- [streams.md](./streams.md): Multiple updates
- [../stimulus/](../stimulus/): Client-side interactions
