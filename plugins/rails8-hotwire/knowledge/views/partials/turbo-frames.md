---
name: rails8-views-partial-turbo-frames
description: Turbo Frame partial patterns, dom_id usage, and frame-based updates
---

# Turbo Frame Partials

## Overview

Turbo Frames enable partial page updates by replacing specific DOM regions. Combining Turbo Frames with Rails partials creates powerful, maintainable patterns for dynamic UIs.

## When to Use

- When implementing inline editing
- When creating lazy-loaded sections
- When building tab interfaces
- When paginating within a frame
- When creating modal dialogs

## Quick Start

```erb
<%# List with framed items %>
<div id="posts">
  <% @posts.each do |post| %>
    <%= turbo_frame_tag dom_id(post) do %>
      <%= render post %>
    <% end %>
  <% end %>
</div>

<%# Partial that can be edited inline %>
<%# app/views/posts/_post.html.erb %>
<article class="p-4 border rounded">
  <h2><%= link_to post.title, post %></h2>
  <p><%= post.body %></p>
  <%= link_to "Edit", edit_post_path(post) %>
</article>
```

## Main Patterns

### Pattern 1: dom_id Helper

```erb
<%# dom_id generates unique IDs from records %>
<%= dom_id(@post) %>           # => "post_123"
<%= dom_id(@post, :edit) %>    # => "edit_post_123"
<%= dom_id(Post.new) %>        # => "new_post"

<%# Use with turbo_frame_tag %>
<%= turbo_frame_tag dom_id(@post) do %>
  <%# content %>
<% end %>

<%# Generates: <turbo-frame id="post_123">...</turbo-frame> %>

<%# For nested resources %>
<%= dom_id([@post, @comment]) %>  # => "post_123_comment_456"

<%# Custom prefix %>
<%= dom_id(@post, :card) %>       # => "card_post_123"
```

### Pattern 2: Inline Editing Pattern

```erb
<%# app/views/posts/_post.html.erb %>
<%= turbo_frame_tag dom_id(post) do %>
  <article class="p-4 border rounded">
    <h2 class="text-xl font-bold"><%= post.title %></h2>
    <p class="text-gray-600 mt-2"><%= post.body %></p>
    <div class="mt-4">
      <%= link_to "Edit", edit_post_path(post),
                  class: "text-blue-600 hover:underline" %>
    </div>
  </article>
<% end %>

<%# app/views/posts/edit.html.erb %>
<%= turbo_frame_tag dom_id(@post) do %>
  <%= form_with model: @post, class: "p-4 border rounded bg-gray-50" do |f| %>
    <div class="mb-4">
      <%= f.label :title, class: "block font-medium" %>
      <%= f.text_field :title, class: "input w-full" %>
    </div>

    <div class="mb-4">
      <%= f.label :body, class: "block font-medium" %>
      <%= f.text_area :body, rows: 4, class: "input w-full" %>
    </div>

    <div class="flex gap-2">
      <%= f.submit "Save", class: "btn btn-primary" %>
      <%= link_to "Cancel", @post, class: "btn btn-secondary" %>
    </div>
  <% end %>
<% end %>

<%# Controller %>
def update
  @post = Post.find(params[:id])
  if @post.update(post_params)
    redirect_to @post, status: :see_other
  else
    render :edit, status: :unprocessable_entity
  end
end
```

### Pattern 3: Lazy Loading Pattern

```erb
<%# Initial page - show placeholder %>
<%= turbo_frame_tag "recent_activity",
                    src: recent_activity_path,
                    loading: :lazy do %>
  <div class="animate-pulse">
    <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div class="h-4 bg-gray-200 rounded w-1/2"></div>
  </div>
<% end %>

<%# app/views/activity/recent.html.erb %>
<%= turbo_frame_tag "recent_activity" do %>
  <ul class="divide-y">
    <% @activities.each do |activity| %>
      <li class="py-2"><%= activity.description %></li>
    <% end %>
  </ul>
<% end %>
```

### Pattern 4: Tab Interface

```erb
<%# Tab navigation (outside frame, targets frame) %>
<div class="border-b">
  <nav class="flex space-x-4">
    <%= link_to "Details", post_path(@post, tab: "details"),
                data: { turbo_frame: "tab_content" },
                class: tab_class("details") %>
    <%= link_to "Comments", post_comments_path(@post),
                data: { turbo_frame: "tab_content" },
                class: tab_class("comments") %>
    <%= link_to "History", post_history_path(@post),
                data: { turbo_frame: "tab_content" },
                class: tab_class("history") %>
  </nav>
</div>

<%# Tab content frame %>
<%= turbo_frame_tag "tab_content" do %>
  <%= render "posts/details", post: @post %>
<% end %>

<%# Each tab response must wrap in same frame %>
<%# app/views/posts/comments.html.erb %>
<%= turbo_frame_tag "tab_content" do %>
  <%= render @post.comments %>
  <%= render "comments/form", post: @post %>
<% end %>
```

### Pattern 5: Pagination in Frame

```erb
<%# app/views/posts/index.html.erb %>
<%= turbo_frame_tag "posts_list" do %>
  <div class="space-y-4">
    <%= render @posts %>
  </div>

  <%# Pagination links stay in frame %>
  <nav class="mt-6">
    <%= render "shared/pagination", pagy: @pagy %>
  </nav>
<% end %>

<%# Infinite scroll variant %>
<div id="posts" class="space-y-4">
  <%= render @posts %>
</div>

<% if @pagy.next %>
  <%= turbo_frame_tag "page_#{@pagy.next}",
                      src: posts_path(page: @pagy.next),
                      loading: :lazy do %>
    <div class="text-center py-4">
      <span class="loading">Loading more...</span>
    </div>
  <% end %>
<% end %>
```

### Pattern 6: Modal with Turbo Frame

```erb
<%# Layout contains empty modal frame %>
<%= turbo_frame_tag "modal" %>

<%# Link that opens in modal %>
<%= link_to "New Post", new_post_path, data: { turbo_frame: "modal" } %>

<%# app/views/posts/new.html.erb %>
<%= turbo_frame_tag "modal" do %>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center"
       data-controller="modal"
       data-action="keydown.esc->modal#close click->modal#closeOnBackdrop">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4"
         data-modal-target="content">
      <div class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">New Post</h2>
          <%= link_to posts_path, class: "text-gray-400 hover:text-gray-600",
                      data: { turbo_frame: "modal" } do %>
            <svg class="w-6 h-6"><!-- X icon --></svg>
          <% end %>
        </div>

        <%= render "form" %>
      </div>
    </div>
  </div>
<% end %>
```

### Pattern 7: Search with Frame

```erb
<%# Search form targets results frame %>
<%= form_with url: search_path, method: :get,
              data: { turbo_frame: "search_results" } do |f| %>
  <%= f.search_field :q, placeholder: "Search...",
      class: "input",
      data: { controller: "debounce",
              action: "input->debounce#search",
              debounce_url_value: search_path } %>
<% end %>

<%# Results frame %>
<%= turbo_frame_tag "search_results" do %>
  <% if @results.any? %>
    <ul class="divide-y">
      <% @results.each do |result| %>
        <li class="py-2"><%= link_to result.title, result %></li>
      <% end %>
    </ul>
  <% elsif params[:q].present? %>
    <p class="text-gray-500">No results found</p>
  <% end %>
<% end %>
```

### Pattern 8: Frame with Fallback (Progressive Enhancement)

```erb
<%# If JavaScript disabled, link works normally %>
<%= turbo_frame_tag dom_id(@post), target: "_top" do %>
  <article>
    <h2><%= link_to post.title, post %></h2>
    <%= link_to "Edit", edit_post_path(post) %>
  </article>
<% end %>

<%# target: "_top" means if frame breaks, full page navigation %>
<%# Links inside can override: %>
<%= link_to "View Full", post_path(post), data: { turbo_frame: "_top" } %>
```

### Pattern 9: Nested Frames

```erb
<%# Outer frame for post %>
<%= turbo_frame_tag dom_id(@post) do %>
  <article>
    <h2><%= @post.title %></h2>

    <%# Inner frame for comments %>
    <%= turbo_frame_tag "post_#{@post.id}_comments" do %>
      <%= render @post.comments %>
      <%= render "comments/form", post: @post %>
    <% end %>
  </article>
<% end %>

<%# Warning: Avoid more than 2 levels of nesting %>
```

### Pattern 10: Frame Lifecycle Events

```javascript
// app/javascript/controllers/frame_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  connect() {
    this.element.addEventListener("turbo:frame-load", this.onLoad.bind(this))
    this.element.addEventListener("turbo:frame-render", this.onRender.bind(this))
  }

  onLoad(event) {
    // Frame content loaded
    console.log("Frame loaded:", event.target.id)
  }

  onRender(event) {
    // Frame about to render
    // Can modify event.detail.render for custom rendering
  }
}
```

```erb
<%= turbo_frame_tag "posts", data: { controller: "frame" } do %>
  <%= render @posts %>
<% end %>
```

## Frame Best Practices

```erb
<%# 1. Always use dom_id for model-based frames %>
<%= turbo_frame_tag dom_id(@post) %>

<%# 2. Match frame IDs between request and response %>
<%# Request has frame "post_123", response MUST have "post_123" %>

<%# 3. Use descriptive IDs for static frames %>
<%= turbo_frame_tag "sidebar" %>
<%= turbo_frame_tag "search_results" %>
<%= turbo_frame_tag "notifications" %>

<%# 4. Provide loading states for lazy frames %>
<%= turbo_frame_tag "stats", src: stats_path, loading: :lazy do %>
  <div class="skeleton">Loading...</div>
<% end %>

<%# 5. Handle missing frames gracefully in controller %>
def show
  @post = Post.find(params[:id])
  # Works for both full page and frame requests
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Mismatched frame IDs | Content not replaced | Ensure IDs match exactly |
| Too many nested frames | Complex, hard to debug | Maximum 2 levels |
| No loading state | User sees nothing | Add skeleton/spinner |
| Frame without fallback | Breaks without JS | Add `target: "_top"` |
| Hardcoded IDs | Collision risk | Use `dom_id` helper |

## Related Skills

- [../../hotwire/SKILL.md](../../hotwire/SKILL.md): Turbo Frames deep dive
- [collections.md](./collections.md): Collection rendering
- [../forms/form-builder.md](../forms/form-builder.md): Forms in frames

## References

- [Turbo Frames Handbook](https://turbo.hotwired.dev/handbook/frames)
- [dom_id Helper](https://api.rubyonrails.org/classes/ActionView/RecordIdentifier.html)
