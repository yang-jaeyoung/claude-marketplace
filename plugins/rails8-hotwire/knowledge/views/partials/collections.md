---
name: rails8-views-partial-collections
description: Collection rendering patterns with caching, counter variables, and empty states
---

# Collection Rendering

## Overview

Rails provides powerful collection rendering that automatically iterates over arrays and renders a partial for each item. Combined with caching, it becomes highly performant.

## When to Use

- When displaying lists of records
- When rendering arrays of objects
- When implementing cached collection views
- When you need counter or iteration variables

## Quick Start

```erb
<%# Simplest form - Rails infers everything %>
<%= render @posts %>

<%# Equivalent explicit form %>
<%= render partial: "posts/post", collection: @posts %>

<%# With caching %>
<%= render partial: "posts/post", collection: @posts, cached: true %>
```

## Main Patterns

### Pattern 1: Automatic Collection Rendering

```erb
<%# Rails determines: %>
<%# - Partial path from model class (Post -> posts/_post) %>
<%# - Local variable name from model (post) %>

<%= render @posts %>

<%# The partial receives: %>
<%# app/views/posts/_post.html.erb %>
<article id="<%= dom_id(post) %>">
  <h2><%= post.title %></h2>
  <p><%= post.body %></p>
</article>

<%# Works with any ActiveRecord collection %>
<%= render @user.comments %>     # comments/_comment.html.erb
<%= render @post.tags %>         # tags/_tag.html.erb
<%= render current_user.orders %> # orders/_order.html.erb
```

### Pattern 2: Explicit Collection Syntax

```erb
<%# Full control over rendering %>
<%= render partial: "posts/post", collection: @posts %>

<%# Rename the local variable %>
<%= render partial: "posts/post", collection: @posts, as: :article %>
<%# Partial receives `article` instead of `post` %>

<%# Specify different partial %>
<%= render partial: "posts/card", collection: @posts %>

<%# Pass additional locals %>
<%= render partial: "posts/post",
           collection: @posts,
           locals: { show_author: true, compact: false } %>
```

### Pattern 3: Counter and Iteration Variables

```erb
<%# Rails automatically provides counter variables %>

<%# app/views/posts/_post.html.erb %>
<%# Available: post_counter (0-indexed position) %>
<article class="<%= post_counter.zero? ? 'first' : '' %>">
  <span class="position"><%= post_counter + 1 %></span>
  <h2><%= post.title %></h2>
</article>

<%# Also available with explicit as: %>
<%= render partial: "posts/post", collection: @posts, as: :article %>
<%# Provides: article_counter %>

<%# Iteration object (Rails 6+) %>
<%# post_iteration provides: index, size, first?, last? %>
<article class="<%= 'border-b' unless post_iteration.last? %>">
  <span><%= post_iteration.index + 1 %> of <%= post_iteration.size %></span>
  <h2><%= post.title %></h2>
</article>
```

### Pattern 4: Cached Collections

```erb
<%# Enable collection caching %>
<%= render partial: "posts/post", collection: @posts, cached: true %>

<%# Cache key is derived from each record's cache_key_with_version %>
<%# Partial is cached individually per record %>

<%# Custom cache key %>
<%= render partial: "posts/post", collection: @posts, cached: ->(post) { [post, current_user] } %>

<%# In the partial, you can also use cache %>
<%# app/views/posts/_post.html.erb %>
<% cache post do %>
  <article>
    <h2><%= post.title %></h2>
    <p><%= post.body %></p>
  </article>
<% end %>

<%# Conditional caching %>
<%= render partial: "posts/post",
           collection: @posts,
           cached: Rails.env.production? %>
```

### Pattern 5: Empty State Handling

```erb
<%# Check for empty collection %>
<% if @posts.any? %>
  <%= render @posts %>
<% else %>
  <%= render "posts/empty_state" %>
<% end %>

<%# More elegant with presence %>
<%= render @posts.presence || "posts/empty_state" %>

<%# With wrapper %>
<div id="posts">
  <%= render @posts.presence || "posts/empty_state" %>
</div>

<%# Empty state partial %>
<%# app/views/posts/_empty_state.html.erb %>
<div class="text-center py-12">
  <svg class="mx-auto h-12 w-12 text-gray-400"><!-- icon --></svg>
  <h3 class="mt-2 text-sm font-medium text-gray-900">No posts</h3>
  <p class="mt-1 text-sm text-gray-500">Get started by creating a new post.</p>
  <%= link_to "New Post", new_post_path, class: "btn btn-primary mt-4" %>
</div>
```

### Pattern 6: Spacer Templates

```erb
<%# Insert content between items %>
<%= render partial: "posts/post",
           collection: @posts,
           spacer_template: "posts/spacer" %>

<%# app/views/posts/_spacer.html.erb %>
<hr class="my-4 border-gray-200">

<%# Conditional spacer with iteration %>
<%# Use partial directly if you need conditions %>
<% @posts.each_with_index do |post, index| %>
  <%= render post %>
  <% unless index == @posts.length - 1 %>
    <hr class="my-4">
  <% end %>
<% end %>
```

### Pattern 7: Layout Wrapper

```erb
<%# Wrap each rendered item in a layout %>
<%= render partial: "posts/post",
           collection: @posts,
           layout: "posts/post_wrapper" %>

<%# app/views/posts/_post_wrapper.html.erb %>
<div class="bg-white shadow rounded-lg p-4 mb-4">
  <%= yield %>
</div>

<%# Layout receives the same locals as partial %>
<%# Plus: object (the current item) %>
```

### Pattern 8: Nested Collections

```erb
<%# Render posts with their comments %>
<% @posts.each do |post| %>
  <%= render post %>
  <div class="comments ml-8">
    <%= render post.comments %>
  </div>
<% end %>

<%# Or in the post partial %>
<%# app/views/posts/_post.html.erb %>
<article id="<%= dom_id(post) %>">
  <h2><%= post.title %></h2>
  <p><%= post.body %></p>

  <div class="comments">
    <%= render post.comments.presence || "comments/empty" %>
  </div>
</article>
```

### Pattern 9: Collection with Turbo Frames

```erb
<%# Wrap collection in Turbo Frame for updates %>
<%= turbo_frame_tag "posts" do %>
  <div id="posts_list">
    <%= render @posts %>
  </div>
  <%= render "shared/pagination", pagy: @pagy %>
<% end %>

<%# Each item can be a Turbo Frame for inline editing %>
<%# app/views/posts/_post.html.erb %>
<%= turbo_frame_tag dom_id(post) do %>
  <article class="p-4 border rounded">
    <h2><%= post.title %></h2>
    <%= link_to "Edit", edit_post_path(post) %>
  </article>
<% end %>
```

### Pattern 10: Grouped Collections

```erb
<%# Group posts by date %>
<% @posts.group_by { |p| p.created_at.to_date }.each do |date, posts| %>
  <h3 class="text-lg font-bold mt-6 mb-2"><%= date.to_fs(:long) %></h3>
  <%= render posts %>
<% end %>

<%# Group by category %>
<% @posts.group_by(&:category).each do |category, posts| %>
  <section class="mb-8">
    <h2 class="text-xl font-bold"><%= category.name %></h2>
    <%= render partial: "posts/card", collection: posts %>
  </section>
<% end %>
```

## Performance Tips

```ruby
# Always eager load associations for collections
@posts = Post.includes(:author, :tags).order(created_at: :desc)

# Use counter cache for counts
class Comment < ApplicationRecord
  belongs_to :post, counter_cache: true
end

# Limit collection size for pagination
@posts = Post.page(params[:page]).per(20)

# Use strict_loading to catch N+1
@posts = Post.strict_loading.includes(:author)
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| N+1 queries | Each item triggers queries | Use `includes` or `preload` |
| No caching on lists | Slow page loads | Add `cached: true` |
| Inline each loop | Miss Rails optimizations | Use collection rendering |
| No empty state | Confusing blank page | Always handle empty collections |
| Counter without need | Extra overhead | Only use when needed |

## Related Skills

- [conventions.md](./conventions.md): Naming conventions
- [locals.md](./locals.md): Local variables
- [turbo-frames.md](./turbo-frames.md): Turbo Frame integration
- [../templates/_pagination.html.erb](../templates/_pagination.html.erb): Pagination template

## References

- [Rails Collection Rendering](https://guides.rubyonrails.org/layouts_and_rendering.html#rendering-collections)
- [Collection Caching](https://guides.rubyonrails.org/caching_with_rails.html#collection-caching)
