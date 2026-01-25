---
name: rails8-views
description: Layouts, partials, form_with, ViewComponent, Tailwind CSS patterns. Use when designing view structure or implementing forms.
triggers:
  - view
  - layout
  - partial
  - form
  - form_with
  - view component
  - tailwind
  - erb
  - helper
  - 뷰
  - 레이아웃
  - 파셜
  - 폼
  - 뷰 컴포넌트
  - 테일윈드
  - 헬퍼
summary: |
  Rails 8 뷰 레이어를 다룹니다. 레이아웃 구조, 파셜 재사용, form_with 폼 빌더,
  ViewComponent, Tailwind CSS 패턴을 포함합니다. UI 구조 설계나 복잡한 폼
  구현 시 참조하세요.
token_cost: medium
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - forms/*.md
    - partials/*.md
  deep:
    - "**/*.md"
    - "**/*.erb"
---

# Views: View Components & Forms

## Overview

Covers the Rails 8 view layer. Includes layouts, partials, form builders, ViewComponent, and Tailwind CSS integration patterns.

## When to Use

- When designing layout structure
- When writing reusable partials
- When implementing complex forms
- When extracting UI components

## Core Principles

| Principle | Description |
|-----------|-------------|
| DRY Views | Remove duplication with partials/components |
| Presenter Pattern | Separate complex view logic |
| Form Objects | Extract complex forms into objects |
| Semantic HTML | Accessible markup |

## Quick Start

### Basic Layout

```erb
<!-- app/views/layouts/application.html.erb -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="turbo-refresh-method" content="morph">
  <meta name="turbo-refresh-scroll" content="preserve">

  <%= csrf_meta_tags %>
  <%= csp_meta_tag %>

  <title><%= content_for(:title) || "My App" %></title>

  <%= stylesheet_link_tag "application", "data-turbo-track": "reload" %>
  <%= javascript_importmap_tags %>
</head>
<body class="min-h-screen bg-gray-50">
  <%= render "shared/navbar" %>

  <div id="flash">
    <%= render "shared/flash" %>
  </div>

  <main class="container mx-auto px-4 py-8">
    <%= yield %>
  </main>

  <%= render "shared/footer" %>
</body>
</html>
```

### Collection Rendering with Partials

```erb
<!-- Collection rendering -->
<%= render @posts %>
<!-- Or explicitly -->
<%= render partial: "posts/post", collection: @posts, as: :post %>

<!-- With caching -->
<%= render partial: "posts/post", collection: @posts, cached: true %>

<!-- Empty state handling -->
<%= render @posts.presence || "posts/empty" %>
```

## File Structure

```
views/
├── SKILL.md
├── layouts/
│   ├── application.md
│   ├── admin.md
│   └── partials.md
├── partials/
│   ├── conventions.md
│   ├── collections.md
│   ├── locals.md
│   └── turbo-frames.md
├── forms/
│   ├── form-builder.md
│   ├── fields.md
│   ├── errors.md
│   ├── nested.md
│   └── stimulus.md
├── components/
│   ├── view-component.md
│   ├── phlex.md
│   └── helpers.md
├── tailwind/
│   ├── setup.md
│   ├── patterns.md
│   └── dark-mode.md
└── templates/
    ├── _flash.html.erb
    ├── _pagination.html.erb
    ├── _empty_state.html.erb
    └── _form_errors.html.erb
```

## Main Patterns

### Pattern 1: Basic form_with

```erb
<%= form_with model: @post, class: "space-y-6" do |f| %>
  <%= render "shared/form_errors", model: @post %>

  <div>
    <%= f.label :title, class: "block text-sm font-medium" %>
    <%= f.text_field :title,
        class: "mt-1 block w-full rounded border-gray-300",
        data: { controller: "character-count",
               character_count_limit_value: 200 } %>
  </div>

  <div>
    <%= f.label :body, class: "block text-sm font-medium" %>
    <%= f.text_area :body, rows: 10, class: "mt-1 block w-full rounded" %>
  </div>

  <div class="flex items-center gap-2">
    <%= f.check_box :published, class: "rounded" %>
    <%= f.label :published, "Public" %>
  </div>

  <div class="flex gap-4">
    <%= f.submit class: "btn btn-primary" %>
    <%= link_to "Cancel", :back, class: "btn btn-secondary" %>
  </div>
<% end %>
```

### Pattern 2: Nested Forms (accepts_nested_attributes)

```ruby
# Model
class Post < ApplicationRecord
  has_many :images, dependent: :destroy
  accepts_nested_attributes_for :images,
    allow_destroy: true,
    reject_if: :all_blank
end
```

```erb
<!-- View -->
<%= form_with model: @post do |f| %>
  <%= f.text_field :title %>

  <div data-controller="nested-form"
       data-nested-form-wrapper-selector-value=".nested-fields">

    <template data-nested-form-target="template">
      <%= f.fields_for :images, Image.new, child_index: "NEW_RECORD" do |img| %>
        <%= render "image_fields", f: img %>
      <% end %>
    </template>

    <div data-nested-form-target="container">
      <%= f.fields_for :images do |img| %>
        <%= render "image_fields", f: img %>
      <% end %>
    </div>

    <button type="button" data-action="nested-form#add">
      Add Image
    </button>
  </div>

  <%= f.submit %>
<% end %>

<!-- _image_fields.html.erb -->
<div class="nested-fields" data-new-record="<%= f.object.new_record? %>">
  <%= f.file_field :file %>
  <%= f.hidden_field :_destroy %>
  <button type="button" data-action="nested-form#remove">Remove</button>
</div>
```

### Pattern 3: ViewComponent

```ruby
# app/components/card_component.rb
class CardComponent < ViewComponent::Base
  def initialize(title:, description: nil, footer: nil)
    @title = title
    @description = description
    @footer = footer
  end

  def render?
    @title.present?
  end
end
```

```erb
<!-- app/components/card_component.html.erb -->
<div class="bg-white rounded-lg shadow p-6">
  <h3 class="text-lg font-semibold"><%= @title %></h3>

  <% if @description %>
    <p class="text-gray-600 mt-2"><%= @description %></p>
  <% end %>

  <% if content.present? %>
    <div class="mt-4"><%= content %></div>
  <% end %>

  <% if @footer %>
    <div class="mt-4 pt-4 border-t"><%= @footer %></div>
  <% end %>
</div>
```

```erb
<!-- Usage -->
<%= render CardComponent.new(title: "Title", description: "Description") do %>
  <p>Card body content</p>
<% end %>
```

### Pattern 4: Empty State Handling

```erb
<!-- app/views/posts/_empty_state.html.erb -->
<div class="text-center py-12">
  <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
  <h3 class="mt-2 text-sm font-medium text-gray-900">No posts yet</h3>
  <p class="mt-1 text-sm text-gray-500">Create a new post to get started.</p>
  <div class="mt-6">
    <%= link_to "New Post", new_post_path, class: "btn btn-primary" %>
  </div>
</div>

<!-- Usage -->
<% if @posts.any? %>
  <%= render @posts %>
<% else %>
  <%= render "posts/empty_state" %>
<% end %>

<!-- Or simply -->
<%= render @posts.presence || "posts/empty_state" %>
```

### Pattern 5: Turbo Frame Partials

```erb
<!-- List -->
<%= turbo_frame_tag "posts" do %>
  <div id="posts_list">
    <%= render @posts %>
  </div>

  <%= render "shared/pagination", pagy: @pagy %>
<% end %>

<!-- Individual item (editable) -->
<%= turbo_frame_tag dom_id(post) do %>
  <article class="p-4 border rounded">
    <h2><%= link_to post.title, post %></h2>
    <p><%= truncate(post.body, length: 200) %></p>
    <%= link_to "Edit", edit_post_path(post) %>
  </article>
<% end %>
```

### Pattern 6: Tailwind Button Helper

```ruby
# app/helpers/button_helper.rb
module ButtonHelper
  def btn_classes(variant = :primary, size: :md)
    base = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"

    sizes = {
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-sm",
      lg: "px-6 py-3 text-base"
    }

    variants = {
      primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
      secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500",
      danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
      ghost: "text-gray-700 hover:bg-gray-100 focus:ring-gray-500"
    }

    [base, sizes[size], variants[variant]].join(" ")
  end
end
```

```erb
<%= link_to "Save", post_path, class: btn_classes(:primary) %>
<%= link_to "Cancel", :back, class: btn_classes(:secondary) %>
<%= button_to "Delete", post_path, method: :delete, class: btn_classes(:danger, size: :sm) %>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Business logic in views | Hard to test/reuse | Separate to Presenter, Helper |
| Inline style abuse | Hard to maintain | Use Tailwind classes |
| Excessive partial nesting | Performance degradation, hard to trace | Maximum 2 levels of nesting |
| Not passing local variables | Implicit dependencies | Use explicit locals |

## Related Skills

- [hotwire](../hotwire/SKILL.md): Turbo Frame/Stream
- [controllers](../controllers/SKILL.md): Response handling
- [snippets/views](../snippets/views/): View templates

## References

- [Action View Overview](https://guides.rubyonrails.org/action_view_overview.html)
- [Form Helpers](https://guides.rubyonrails.org/form_helpers.html)
- [ViewComponent](https://viewcomponent.org/)
- [Tailwind CSS](https://tailwindcss.com/docs)
