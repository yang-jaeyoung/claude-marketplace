---
name: rails8-views-form-builder
description: form_with basics, model vs URL forms, and Turbo integration
---

# Form Builder

## Overview

Rails 8 uses `form_with` as the standard form helper. It integrates seamlessly with Turbo for AJAX submissions by default. Understanding form_with options is essential for building modern Rails forms.

## When to Use

- When creating model-backed forms (CRUD)
- When building search or filter forms
- When implementing custom form submissions
- When handling file uploads

## Quick Start

```erb
<%# Model-backed form (most common) %>
<%= form_with model: @post do |f| %>
  <%= f.text_field :title %>
  <%= f.text_area :body %>
  <%= f.submit %>
<% end %>

<%# URL-based form (search, custom actions) %>
<%= form_with url: search_path, method: :get do |f| %>
  <%= f.search_field :q %>
  <%= f.submit "Search" %>
<% end %>
```

## Main Patterns

### Pattern 1: Model-Backed Forms

```erb
<%# New record - submits POST to /posts %>
<%= form_with model: @post do |f| %>
  <%= f.text_field :title %>
  <%= f.submit %>  <%# "Create Post" %>
<% end %>

<%# Existing record - submits PATCH to /posts/:id %>
<%= form_with model: @post do |f| %>
  <%= f.text_field :title %>
  <%= f.submit %>  <%# "Update Post" %>
<% end %>

<%# Rails automatically determines: %>
<%# - HTTP method (POST for new, PATCH for existing) %>
<%# - Action URL (posts_path or post_path(@post)) %>
<%# - Submit button text %>
```

### Pattern 2: Namespaced and Nested Resources

```erb
<%# Admin namespace %>
<%= form_with model: [:admin, @post] do |f| %>
  <%# Submits to admin_posts_path or admin_post_path(@post) %>
<% end %>

<%# Nested resource %>
<%= form_with model: [@post, @comment] do |f| %>
  <%# Submits to post_comments_path(@post) %>
<% end %>

<%# Multiple levels %>
<%= form_with model: [:admin, @post, @comment] do |f| %>
  <%# Submits to admin_post_comments_path(@post) %>
<% end %>
```

### Pattern 3: URL-Based Forms

```erb
<%# Search form (GET) %>
<%= form_with url: search_path, method: :get do |f| %>
  <%= f.search_field :q, placeholder: "Search..." %>
  <%= f.submit "Search" %>
<% end %>

<%# Custom action %>
<%= form_with url: publish_post_path(@post), method: :post do |f| %>
  <%= f.submit "Publish" %>
<% end %>

<%# External URL %>
<%= form_with url: "https://api.example.com/webhook", method: :post do |f| %>
  <%= hidden_field_tag :token, @token %>
  <%= f.submit "Send" %>
<% end %>
```

### Pattern 4: Turbo Integration

```erb
<%# By default, form_with submits via Turbo (fetch) %>
<%= form_with model: @post do |f| %>
  <%# Turbo handles response %>
<% end %>

<%# Disable Turbo for specific form %>
<%= form_with model: @post, data: { turbo: false } do |f| %>
  <%# Regular form submission %>
<% end %>

<%# Target specific Turbo Frame %>
<%= form_with model: @post, data: { turbo_frame: "posts" } do |f| %>
  <%# Response replaces the "posts" frame %>
<% end %>

<%# Turbo Stream response %>
<%= form_with model: @post do |f| %>
  <%# Controller returns turbo_stream format %>
<% end %>

<%# Controller %>
def create
  @post = Post.new(post_params)
  if @post.save
    respond_to do |format|
      format.turbo_stream
      format.html { redirect_to @post }
    end
  else
    render :new, status: :unprocessable_entity
  end
end
```

### Pattern 5: Form Options

```erb
<%# Full options example %>
<%= form_with(
  model: @post,
  url: custom_path,           # Override action URL
  method: :patch,             # Override HTTP method
  local: false,               # Deprecated, use data: { turbo: false }
  id: "post-form",            # Form ID
  class: "space-y-4",         # CSS classes
  data: {
    controller: "form",       # Stimulus controller
    turbo: true,              # Enable/disable Turbo
    turbo_frame: "results",   # Target frame
    turbo_confirm: "Sure?"    # Confirmation dialog
  },
  html: {
    novalidate: true,         # Disable HTML5 validation
    autocomplete: "off"       # Disable autocomplete
  }
) do |f| %>
  <%= f.text_field :title %>
  <%= f.submit %>
<% end %>
```

### Pattern 6: Scope for Non-Model Forms

```erb
<%# Create params hash without model %>
<%= form_with url: search_path, scope: :search, method: :get do |f| %>
  <%= f.text_field :query %>
  <%= f.select :category, Category.pluck(:name, :id) %>
  <%= f.check_box :include_drafts %>
  <%= f.submit "Search" %>
<% end %>

<%# Produces params: { search: { query: "...", category: "...", include_drafts: "1" } } %>

<%# Controller %>
def search
  query = params.dig(:search, :query)
  category = params.dig(:search, :category)
end
```

### Pattern 7: File Uploads

```erb
<%# File upload requires multipart %>
<%= form_with model: @post, multipart: true do |f| %>
  <%= f.file_field :image %>
  <%= f.submit %>
<% end %>

<%# Or it's automatic with file_field %>
<%= form_with model: @post do |f| %>
  <%= f.file_field :image %>  <%# Adds multipart automatically %>
  <%= f.submit %>
<% end %>

<%# Active Storage direct upload %>
<%= form_with model: @post do |f| %>
  <%= f.file_field :image, direct_upload: true %>
<% end %>

<%# Disable Turbo for file uploads (traditional submission) %>
<%= form_with model: @post, data: { turbo: false } do |f| %>
  <%= f.file_field :document %>
  <%= f.submit %>
<% end %>
```

### Pattern 8: Form Builder Object

```erb
<%# The block variable (f) is a FormBuilder %>
<%= form_with model: @post do |f| %>
  <%# f.object returns the model %>
  <% if f.object.new_record? %>
    <h2>Create New Post</h2>
  <% else %>
    <h2>Edit: <%= f.object.title %></h2>
  <% end %>

  <%# f.object_name returns the param key %>
  <%# => "post" %>

  <%= f.text_field :title %>
  <%= f.submit %>
<% end %>
```

### Pattern 9: Custom Form Builder

```ruby
# app/form_builders/tailwind_form_builder.rb
class TailwindFormBuilder < ActionView::Helpers::FormBuilder
  def text_field(method, options = {})
    options[:class] = "#{options[:class]} block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
    super
  end

  def submit(value = nil, options = {})
    options[:class] = "#{options[:class]} inline-flex justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500"
    super
  end

  def error_messages
    return unless object.errors.any?

    @template.content_tag(:div, class: "bg-red-50 border border-red-200 rounded-md p-4 mb-4") do
      @template.content_tag(:ul, class: "list-disc list-inside text-sm text-red-600") do
        object.errors.full_messages.map { |msg| @template.content_tag(:li, msg) }.join.html_safe
      end
    end
  end
end
```

```erb
<%# Use custom builder %>
<%= form_with model: @post, builder: TailwindFormBuilder do |f| %>
  <%= f.error_messages %>
  <%= f.text_field :title %>
  <%= f.submit "Save" %>
<% end %>

<%# Set as default in application %>
<%# config/initializers/form_builder.rb %>
ActionView::Base.default_form_builder = TailwindFormBuilder
```

### Pattern 10: Turbo Confirm and Disable

```erb
<%# Confirmation before submit %>
<%= form_with model: @post, data: { turbo_confirm: "Are you sure?" } do |f| %>
  <%= f.submit "Delete", formmethod: :delete %>
<% end %>

<%# Disable button during submission %>
<%= form_with model: @post do |f| %>
  <%= f.submit "Save", data: { turbo_submits_with: "Saving..." } %>
<% end %>

<%# Combined %>
<%= form_with model: @post do |f| %>
  <%= f.submit "Save",
      data: {
        turbo_submits_with: "Saving...",
        turbo_confirm: "Save changes?"
      } %>
<% end %>
```

## Controller Response Patterns

```ruby
class PostsController < ApplicationController
  def create
    @post = Post.new(post_params)

    if @post.save
      respond_to do |format|
        format.turbo_stream  # Renders create.turbo_stream.erb
        format.html { redirect_to @post, notice: "Created!" }
      end
    else
      # IMPORTANT: status must be 422 for Turbo to show errors
      render :new, status: :unprocessable_entity
    end
  end

  def update
    @post = Post.find(params[:id])

    if @post.update(post_params)
      # Use 303 for redirects after POST/PATCH/DELETE
      redirect_to @post, status: :see_other, notice: "Updated!"
    else
      render :edit, status: :unprocessable_entity
    end
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Missing status code | Turbo doesn't show errors | Use `status: :unprocessable_entity` |
| Wrong redirect status | Browser issues | Use `status: :see_other` (303) |
| `form_tag` / `form_for` | Deprecated | Use `form_with` |
| Disabling Turbo everywhere | Lose SPA benefits | Only disable when necessary |
| No error handling | Silent failures | Always handle validation errors |

## Related Skills

- [fields.md](./fields.md): Field types and options
- [errors.md](./errors.md): Error display patterns
- [nested.md](./nested.md): Nested forms
- [../../hotwire/SKILL.md](../../hotwire/SKILL.md): Turbo integration

## References

- [Rails Form Helpers Guide](https://guides.rubyonrails.org/form_helpers.html)
- [form_with API](https://api.rubyonrails.org/classes/ActionView/Helpers/FormHelper.html#method-i-form_with)
- [Turbo Forms](https://turbo.hotwired.dev/handbook/drive#form-submissions)
