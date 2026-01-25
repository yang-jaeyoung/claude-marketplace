---
name: rails8-turbo
description: Turbo Drive/Frame/Stream, Stimulus controller patterns. Use when implementing partial page updates, real-time UI, and client interactions.
triggers:
  - turbo
  - turbo drive
  - turbo frame
  - turbo stream
  - stimulus
  - partial update
  - real-time ui
  - hotwire pattern
  - 터보
  - 터보 드라이브
  - 터보 프레임
  - 터보 스트림
  - 스티뮬러스
  - 부분 업데이트
  - 실시간 UI
summary: |
  Hotwire의 핵심 구성요소인 Turbo와 Stimulus를 다룹니다. Turbo Drive로 페이지 전환,
  Turbo Frame으로 부분 업데이트, Turbo Stream으로 실시간 UI, Stimulus로 클라이언트
  인터랙션을 구현합니다. 최소 JS로 SPA 수준의 사용자 경험을 제공합니다.
token_cost: high
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - turbo/*.md
    - stimulus/*.md
  deep:
    - "**/*.md"
    - "**/*.js"
---

# Hotwire: Turbo + Stimulus

## Overview

Hotwire is a frontend approach that delivers SPA-level responsiveness by sending server-rendered HTML. It consists of Turbo (80%) and Stimulus (20%), implementing modern UX with minimal JavaScript.

## When to Use

- When improving page transition speed
- When partial page updates are needed
- When implementing real-time UI updates
- When adding client interactions

## Core Principles

| Principle | Description |
|-----------|-------------|
| HTML over the Wire | HTML responses instead of JSON |
| Progressive Enhancement | Basic functionality works without JS |
| Server-side First | Server rendering takes priority |
| Minimal JavaScript | Use JS only where needed |

## Quick Start

### Basic Turbo Frame

```erb
<!-- List page -->
<%= turbo_frame_tag "posts" do %>
  <%= render @posts %>
<% end %>

<!-- Individual item -->
<%= turbo_frame_tag dom_id(post) do %>
  <%= render post %>
<% end %>
```

### Turbo Stream Response

```erb
<!-- create.turbo_stream.erb -->
<%= turbo_stream.prepend "posts", @post %>
<%= turbo_stream.update "flash", partial: "shared/flash" %>
```

### Stimulus Controller

```javascript
// dropdown_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["menu"]
  static classes = ["open"]

  toggle() {
    this.menuTarget.classList.toggle(this.openClass)
  }
}
```

```erb
<div data-controller="dropdown" data-dropdown-open-class="block">
  <button data-action="dropdown#toggle">Menu</button>
  <div data-dropdown-target="menu" class="hidden">
    <!-- Menu content -->
  </div>
</div>
```

## File Structure

```
hotwire/
├── SKILL.md
├── turbo/
│   ├── overview.md
│   ├── drive.md
│   ├── frames.md
│   ├── streams.md
│   ├── morphing.md
│   └── native.md
├── stimulus/
│   ├── overview.md
│   ├── conventions.md
│   ├── lifecycle.md
│   ├── targets.md
│   ├── values.md
│   ├── actions.md
│   └── outlets.md
├── patterns/
│   ├── inline-edit.md
│   ├── live-search.md
│   ├── infinite-scroll.md
│   ├── modal.md
│   ├── tabs.md
│   └── flash-messages.md
├── anti-patterns/
│   └── common-mistakes.md
└── controllers/
    ├── dropdown_controller.js
    ├── modal_controller.js
    ├── tabs_controller.js
    └── toggle_controller.js
```

## Main Patterns

### Pattern 1: Turbo Frame - Inline Editing

```erb
<!-- show.html.erb -->
<%= turbo_frame_tag dom_id(@article) do %>
  <h1><%= @article.title %></h1>
  <p><%= @article.body %></p>
  <%= link_to "Edit", edit_article_path(@article) %>
<% end %>

<!-- edit.html.erb -->
<%= turbo_frame_tag dom_id(@article) do %>
  <%= form_with model: @article do |f| %>
    <%= f.text_field :title %>
    <%= f.text_area :body %>
    <%= f.submit "Update" %>
    <%= link_to "Cancel", @article %>
  <% end %>
<% end %>
```

### Pattern 2: Turbo Frame - Lazy Loading

```erb
<%= turbo_frame_tag "activity_feed",
    src: activity_feed_path,
    loading: :lazy do %>
  <div class="skeleton-loader">Loading...</div>
<% end %>
```

### Pattern 3: Turbo Stream - Multiple Updates

```ruby
# Controller
def create
  @message = Message.create(message_params)

  respond_to do |format|
    format.turbo_stream do
      render turbo_stream: [
        turbo_stream.prepend("messages", @message),
        turbo_stream.update("message_count", Message.count),
        turbo_stream.update("flash", partial: "shared/flash")
      ]
    end
    format.html { redirect_to @message }
  end
end
```

### Pattern 4: Turbo Morphing (Rails 8)

```html
<!-- app/views/layouts/application.html.erb -->
<head>
  <meta name="turbo-refresh-method" content="morph">
  <meta name="turbo-refresh-scroll" content="preserve">
</head>
```

```erb
<!-- Preserve permanent elements -->
<div id="video-player" data-turbo-permanent>
  <video src="..." controls></video>
</div>
```

### Pattern 5: Stimulus - Toggle Controller

```javascript
// toggle_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["content"]
  static classes = ["hidden"]
  static values = { open: { type: Boolean, default: false } }

  toggle() {
    this.openValue = !this.openValue
  }

  openValueChanged(isOpen) {
    this.contentTarget.classList.toggle(this.hiddenClass, !isOpen)
  }
}
```

```erb
<div data-controller="toggle"
     data-toggle-hidden-class="hidden"
     data-toggle-open-value="false">
  <button data-action="toggle#toggle">Toggle</button>
  <div data-toggle-target="content" class="hidden">
    Hidden content
  </div>
</div>
```

### Pattern 6: Infinite Scroll

```erb
<div id="posts">
  <%= render @posts %>
</div>

<% if @pagy.next %>
  <%= turbo_frame_tag "page_#{@pagy.next}",
                      src: posts_path(page: @pagy.next),
                      loading: :lazy %>
<% end %>
```

## Turbo Stream 8 Actions

| Action | Description | Example |
|--------|-------------|---------|
| `append` | Add to end of target | `turbo_stream.append "posts", @post` |
| `prepend` | Add to start of target | `turbo_stream.prepend "posts", @post` |
| `replace` | Replace entire element | `turbo_stream.replace @post` |
| `update` | Change inner content only | `turbo_stream.update "count", "5"` |
| `remove` | Delete element | `turbo_stream.remove @post` |
| `before` | Insert before target | `turbo_stream.before @post, partial: "..." ` |
| `after` | Insert after target | `turbo_stream.after @post, partial: "..."` |
| `refresh` | Refresh page | `turbo_stream.refresh` |

## Pattern Selection Guide

| Requirement | Pattern |
|-------------|---------|
| Replace part of page | Turbo Frame |
| Update multiple elements simultaneously | Turbo Stream |
| Real-time updates | Turbo Stream + ActionCable |
| Client interactions | Stimulus |
| Complex state management | Stimulus Values |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Using Stream without Frame | Target ID mismatch | Define `turbo_frame_tag` first |
| Missing status code | Full page replacement on form errors | Use `status: :unprocessable_entity` |
| Storing state in JS | State lost on page navigation | Use `data-*-value` |
| Overusing nested Frames | Increased complexity, hard to debug | Maximum 2 levels of nesting |
| Using Stimulus everywhere | Unnecessary complexity | Solve 80% with Turbo |
| Overusing `turbo: false` | Lose Turbo benefits | Apply incrementally |

### Correct Status Code Usage

```ruby
# Bad example: No status code
def create
  @post = Post.new(post_params)
  if @post.save
    redirect_to @post
  else
    render :new  # Turbo won't work!
  end
end

# Good example
def create
  @post = Post.new(post_params)
  if @post.save
    redirect_to @post, status: :see_other  # 303
  else
    render :new, status: :unprocessable_entity  # 422
  end
end
```

## Related Skills

- [core](../core/SKILL.md): Project setup
- [controllers](../controllers/SKILL.md): Turbo response handling
- [realtime](../realtime/): WebSocket broadcasting (Phase 2)

## References

- [Turbo Handbook](https://turbo.hotwired.dev/handbook/introduction)
- [Stimulus Handbook](https://stimulus.hotwired.dev/handbook/introduction)
- [Hotwire Official](https://hotwired.dev/)
- [Hotrails Tutorial](https://www.hotrails.dev/turbo-rails)
