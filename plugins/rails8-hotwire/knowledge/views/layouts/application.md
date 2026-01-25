---
name: rails8-views-application-layout
description: Main application layout structure with Turbo meta tags and content_for patterns
---

# Application Layout

## Overview

The main layout file defines the HTML structure shared across all pages. In Rails 8 with Hotwire, proper meta tags and Turbo integration are essential for optimal performance.

## When to Use

- When setting up a new Rails 8 application
- When configuring Turbo Drive behavior
- When implementing content_for patterns for dynamic page sections
- When adding global assets and meta tags

## Quick Start

```erb
<%# app/views/layouts/application.html.erb %>
<!DOCTYPE html>
<html lang="<%= I18n.locale %>">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <%# Turbo 8 morphing configuration %>
  <meta name="turbo-refresh-method" content="morph">
  <meta name="turbo-refresh-scroll" content="preserve">

  <%# Rails security tags %>
  <%= csrf_meta_tags %>
  <%= csp_meta_tag %>

  <%# Dynamic title with fallback %>
  <title><%= content_for(:title) || "My App" %></title>

  <%# Meta description for SEO %>
  <% if content_for?(:description) %>
    <meta name="description" content="<%= content_for(:description) %>">
  <% end %>

  <%# Additional head content (OG tags, custom scripts) %>
  <%= content_for(:head) %>

  <%# Assets %>
  <%= stylesheet_link_tag "application", "data-turbo-track": "reload" %>
  <%= javascript_importmap_tags %>
</head>
<body class="<%= content_for(:body_class) || 'bg-gray-50 min-h-screen' %>">
  <%# Navigation %>
  <%= render "shared/navbar" %>

  <%# Flash messages with Turbo Stream target %>
  <div id="flash">
    <%= render "shared/flash" %>
  </div>

  <%# Main content %>
  <main class="<%= content_for(:main_class) || 'container mx-auto px-4 py-8' %>">
    <%= yield %>
  </main>

  <%# Footer %>
  <%= render "shared/footer" %>

  <%# Modal container for Turbo Frame modals %>
  <%= turbo_frame_tag "modal" %>

  <%# Page-specific scripts %>
  <%= content_for(:scripts) %>
</body>
</html>
```

## Main Patterns

### Pattern 1: content_for Usage

```erb
<%# In any view file %>

<%# Set page title %>
<% content_for(:title) { "Dashboard - My App" } %>

<%# Set meta description %>
<% content_for(:description) { "View your personalized dashboard" } %>

<%# Add Open Graph tags %>
<% content_for(:head) do %>
  <meta property="og:title" content="Dashboard">
  <meta property="og:image" content="<%= asset_url('og-image.png') %>">
<% end %>

<%# Change body class %>
<% content_for(:body_class) { "bg-white" } %>

<%# Add page-specific scripts %>
<% content_for(:scripts) do %>
  <script>
    // Page-specific initialization
  </script>
<% end %>
```

### Pattern 2: Turbo Meta Tags

```erb
<%# Enable morphing (smoother updates, preserves focus/scroll) %>
<meta name="turbo-refresh-method" content="morph">

<%# Preserve scroll position on refresh %>
<meta name="turbo-refresh-scroll" content="preserve">

<%# Per-page override: disable morphing %>
<% content_for(:head) do %>
  <meta name="turbo-refresh-method" content="replace">
<% end %>
```

### Pattern 3: Conditional Layout Sections

```erb
<%# In layout %>
<% if content_for?(:sidebar) %>
  <div class="flex">
    <aside class="w-64 flex-shrink-0">
      <%= content_for(:sidebar) %>
    </aside>
    <main class="flex-1">
      <%= yield %>
    </main>
  </div>
<% else %>
  <main>
    <%= yield %>
  </main>
<% end %>

<%# In view %>
<% content_for(:sidebar) do %>
  <%= render "posts/sidebar" %>
<% end %>
```

### Pattern 4: Asset Tracking with Turbo

```erb
<%# Reload page when assets change %>
<%= stylesheet_link_tag "application", "data-turbo-track": "reload" %>
<%= javascript_importmap_tags %>

<%# Version-specific asset with cache busting %>
<%= stylesheet_link_tag "admin", "data-turbo-track": "reload" if admin_layout? %>
```

### Pattern 5: Permanent Elements

```erb
<%# Elements preserved across page navigations %>
<div id="audio-player" data-turbo-permanent>
  <audio src="<%= @track.url %>" controls></audio>
</div>

<%# Video player that persists %>
<div id="video-player" data-turbo-permanent>
  <%= render "shared/video_player" %>
</div>
```

### Pattern 6: Layout Helper Methods

```ruby
# app/helpers/layout_helper.rb
module LayoutHelper
  def page_title(title = nil)
    if title.present?
      content_for(:title) { "#{title} - #{app_name}" }
    else
      content_for(:title) || app_name
    end
  end

  def app_name
    Rails.application.class.module_parent_name
  end

  def body_class(*classes)
    content_for(:body_class) { classes.join(" ") }
  end

  def admin_layout?
    controller_path.start_with?("admin")
  end
end
```

```erb
<%# Usage in views %>
<% page_title "Dashboard" %>
<% body_class "bg-gray-100", "dashboard-page" %>
```

## Turbo Drive Configuration

### Disable Turbo for Specific Links

```erb
<%# Disable for single link %>
<%= link_to "External", "https://example.com", data: { turbo: false } %>

<%# Disable for form %>
<%= form_with model: @upload, data: { turbo: false } do |f| %>
  <%= f.file_field :document %>
<% end %>

<%# Disable for section %>
<div data-turbo="false">
  <%# All links/forms in here bypass Turbo %>
</div>
```

### Progress Bar Configuration

```erb
<%# In application.html.erb head %>
<style>
  .turbo-progress-bar {
    height: 3px;
    background-color: #3b82f6;
  }
</style>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Missing viewport meta | Mobile display issues | Always include viewport tag |
| Hardcoded title | No page-specific titles | Use `content_for(:title)` |
| Missing CSRF meta | Form submissions fail | Always include `csrf_meta_tags` |
| No Turbo track on assets | Stale CSS/JS after deploy | Add `data-turbo-track: "reload"` |
| Inline styles in layout | Hard to maintain | Use Tailwind classes or CSS files |

## Related Skills

- [admin.md](./admin.md): Admin layout variant
- [partials.md](./partials.md): Layout partials (_navbar, _footer)
- [../hotwire/SKILL.md](../../hotwire/SKILL.md): Turbo configuration details

## References

- [Action View Layouts](https://guides.rubyonrails.org/layouts_and_rendering.html)
- [Turbo Handbook](https://turbo.hotwired.dev/handbook/drive)
- [content_for API](https://api.rubyonrails.org/classes/ActionView/Helpers/CaptureHelper.html)
