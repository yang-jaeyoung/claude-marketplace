---
name: rails8-views-partial-locals
description: Local variables, strict locals (Ruby 3.2+), optional locals, and defaults
---

# Partial Local Variables

## Overview

Partials receive data through local variables. Rails 7.1+ supports strict locals with the magic comment, enabling type-like enforcement and IDE support.

## When to Use

- When passing data to partials
- When enforcing required parameters
- When providing default values
- When documenting partial interfaces

## Quick Start

```erb
<%# Passing locals %>
<%= render "posts/card", post: @post, show_author: true %>

<%# Strict locals (Rails 7.1+, Ruby 3.2+) %>
<%# app/views/posts/_card.html.erb %>
<%# locals: (post:, show_author: true, compact: false) %>
<article class="<%= 'compact' if compact %>">
  <h2><%= post.title %></h2>
  <% if show_author %>
    <p>By <%= post.author.name %></p>
  <% end %>
</article>
```

## Main Patterns

### Pattern 1: Basic Local Variables

```erb
<%# Passing locals with render %>
<%= render "posts/card", post: @post %>
<%= render "posts/card", post: @post, featured: true %>

<%# Explicit locals syntax (equivalent) %>
<%= render partial: "posts/card", locals: { post: @post } %>

<%# In the partial, access directly %>
<%# app/views/posts/_card.html.erb %>
<article>
  <h2><%= post.title %></h2>
  <% if defined?(featured) && featured %>
    <span class="badge">Featured</span>
  <% end %>
</article>
```

### Pattern 2: Strict Locals (Rails 7.1+)

```erb
<%# Define required and optional locals at top of partial %>
<%# app/views/posts/_card.html.erb %>
<%# locals: (post:, show_author: true, show_date: true, compact: false) %>

<article class="<%= 'p-2' if compact %>">
  <h2><%= post.title %></h2>

  <% if show_author %>
    <p class="author">By <%= post.author.name %></p>
  <% end %>

  <% if show_date %>
    <time><%= post.created_at.to_fs(:short) %></time>
  <% end %>
</article>

<%# Now these work: %>
<%= render "posts/card", post: @post %>                     # Uses defaults
<%= render "posts/card", post: @post, compact: true %>      # Override default
<%= render "posts/card", post: @post, show_author: false %> # Override default

<%# This raises an error (missing required local): %>
<%= render "posts/card" %>  # ArgumentError: missing keyword: :post
```

### Pattern 3: Strict Locals Syntax Variations

```erb
<%# Required parameter (no default) %>
<%# locals: (post:) %>

<%# Optional with default %>
<%# locals: (post:, featured: false) %>

<%# Multiple required %>
<%# locals: (post:, user:) %>

<%# Mixed required and optional %>
<%# locals: (post:, user:, show_actions: true, class_name: "card") %>

<%# Allow any additional locals with ** %>
<%# locals: (post:, **) %>

<%# Explicitly deny additional locals %>
<%# locals: (post:) %>  # Raises error if extra locals passed
```

### Pattern 4: Type-like Annotations (Documentation)

```erb
<%# locals: (post:, show_author: true, max_length: 200) %>
<%#
  @param post [Post] The post to display (required)
  @param show_author [Boolean] Whether to show author info (default: true)
  @param max_length [Integer] Truncate body at this length (default: 200)
%>

<article>
  <h2><%= post.title %></h2>
  <p><%= truncate(post.body, length: max_length) %></p>
  <% if show_author %>
    <span>By <%= post.author.name %></span>
  <% end %>
</article>
```

### Pattern 5: Object Local (Collection Rendering)

```erb
<%# When rendering collections, Rails sets a local matching the partial name %>
<%= render @posts %>
<%# Each iteration gets: post (singular of posts) %>

<%# Override with as: %>
<%= render partial: "posts/card", collection: @posts, as: :article %>
<%# Each iteration gets: article %>

<%# Also provides counter: %>
<%# post_counter or article_counter %>

<%# app/views/posts/_card.html.erb %>
<%# locals: (post:) %>
<article>
  <span class="number"><%= post_counter + 1 %></span>
  <h2><%= post.title %></h2>
</article>
```

### Pattern 6: Optional Locals (Pre-strict)

```erb
<%# Before strict locals, check with local_assigns %>
<%# app/views/posts/_card.html.erb %>
<% show_author = local_assigns.fetch(:show_author, true) %>
<% compact = local_assigns.fetch(:compact, false) %>

<article class="<%= 'compact' if compact %>">
  <h2><%= post.title %></h2>
  <% if show_author %>
    <p>By <%= post.author.name %></p>
  <% end %>
</article>

<%# Or with defined? %>
<% if defined?(featured) && featured %>
  <span class="badge">Featured</span>
<% end %>
```

### Pattern 7: Passing Objects vs Primitives

```erb
<%# Prefer passing objects over multiple primitives %>

<%# Bad: Too many primitives %>
<%= render "posts/header",
           title: @post.title,
           author_name: @post.author.name,
           created_at: @post.created_at,
           category: @post.category.name %>

<%# Good: Pass the object %>
<%= render "posts/header", post: @post %>

<%# The partial can access what it needs %>
<%# locals: (post:) %>
<header>
  <h1><%= post.title %></h1>
  <p>By <%= post.author.name %> in <%= post.category.name %></p>
  <time><%= post.created_at.to_fs(:long) %></time>
</header>
```

### Pattern 8: Form Builder as Local

```erb
<%# Pass form builder to nested partials %>
<%= form_with model: @post do |f| %>
  <%= render "posts/form_fields", f: f %>
<% end %>

<%# app/views/posts/_form_fields.html.erb %>
<%# locals: (f:) %>
<div class="space-y-4">
  <div>
    <%= f.label :title %>
    <%= f.text_field :title, class: "input" %>
  </div>

  <div>
    <%= f.label :body %>
    <%= f.text_area :body, class: "input" %>
  </div>
</div>

<%# For nested attributes %>
<%= f.fields_for :comments do |comment_form| %>
  <%= render "comments/fields", f: comment_form %>
<% end %>
```

### Pattern 9: Conditional Rendering Based on Locals

```erb
<%# app/views/shared/_button.html.erb %>
<%# locals: (text:, path:, variant: :primary, size: :md, icon: nil, method: :get) %>

<%= link_to path,
    method: method,
    class: button_classes(variant, size) do %>
  <% if icon %>
    <%= render "shared/icons/#{icon}", class: "w-4 h-4 mr-2" %>
  <% end %>
  <%= text %>
<% end %>

<%# Usage %>
<%= render "shared/button", text: "Save", path: post_path(@post), variant: :primary %>
<%= render "shared/button", text: "Delete", path: post_path(@post), variant: :danger, method: :delete, icon: "trash" %>
```

### Pattern 10: Splat Locals for Wrapper Partials

```erb
<%# Pass through additional locals %>
<%# app/views/shared/_card.html.erb %>
<%# locals: (title:, **options) %>

<div class="card <%= options[:class] %>" id="<%= options[:id] %>">
  <h3><%= title %></h3>
  <%= yield if block_given? %>
</div>

<%# Usage (options passed through) %>
<%= render "shared/card", title: "My Card", class: "featured", id: "main-card" do %>
  <p>Card content here</p>
<% end %>
```

## Debugging Locals

```erb
<%# See all available locals %>
<%= debug local_assigns %>

<%# Check if local is defined %>
<% if local_assigns.key?(:featured) %>
  ...
<% end %>

<%# List local names %>
<%= local_assigns.keys.join(", ") %>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Relying on instance vars | Implicit coupling | Always pass as locals |
| Too many locals | Complex interface | Group into object or use component |
| No defaults for optional | Requires checks everywhere | Use strict locals with defaults |
| defined? checks | Error-prone, verbose | Use strict locals or local_assigns |
| Passing whole controller | Breaks encapsulation | Pass only needed data |

## Related Skills

- [conventions.md](./conventions.md): Partial naming
- [collections.md](./collections.md): Collection rendering
- [../components/view-component.md](../components/view-component.md): Typed component alternative

## References

- [Rails 7.1 Strict Locals](https://blog.saeloun.com/2023/09/14/rails-strict-locals/)
- [Partial Rendering](https://guides.rubyonrails.org/layouts_and_rendering.html#passing-local-variables)
