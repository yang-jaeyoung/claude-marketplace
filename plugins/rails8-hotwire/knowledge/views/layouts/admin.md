---
name: rails8-views-admin-layout
description: Admin layout variant with sidebar navigation and different styling
---

# Admin Layout

## Overview

A separate layout for admin interfaces with sidebar navigation, different styling, and admin-specific features. Inherits from application layout or stands alone.

## When to Use

- When building admin dashboards
- When you need a sidebar-based navigation
- When admin UI differs significantly from public pages
- When implementing multi-panel layouts

## Quick Start

```erb
<%# app/views/layouts/admin.html.erb %>
<!DOCTYPE html>
<html lang="<%= I18n.locale %>">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="turbo-refresh-method" content="morph">
  <meta name="turbo-refresh-scroll" content="preserve">

  <%= csrf_meta_tags %>
  <%= csp_meta_tag %>

  <title><%= content_for(:title) || "Admin - My App" %></title>

  <%= stylesheet_link_tag "application", "data-turbo-track": "reload" %>
  <%= javascript_importmap_tags %>
</head>
<body class="bg-gray-100">
  <div class="min-h-screen flex">
    <%# Sidebar %>
    <%= render "admin/shared/sidebar" %>

    <%# Main content area %>
    <div class="flex-1 flex flex-col">
      <%# Top navbar %>
      <%= render "admin/shared/navbar" %>

      <%# Flash messages %>
      <div id="flash" class="px-6">
        <%= render "shared/flash" %>
      </div>

      <%# Page content %>
      <main class="flex-1 p-6">
        <%# Breadcrumbs %>
        <% if content_for?(:breadcrumbs) %>
          <nav class="mb-4">
            <%= content_for(:breadcrumbs) %>
          </nav>
        <% end %>

        <%# Page header %>
        <% if content_for?(:page_header) %>
          <header class="mb-6">
            <%= content_for(:page_header) %>
          </header>
        <% end %>

        <%= yield %>
      </main>
    </div>
  </div>

  <%# Modal container %>
  <%= turbo_frame_tag "modal" %>

  <%= content_for(:scripts) %>
</body>
</html>
```

## Main Patterns

### Pattern 1: Sidebar Partial

```erb
<%# app/views/admin/shared/_sidebar.html.erb %>
<aside class="w-64 bg-gray-900 text-white flex-shrink-0">
  <div class="p-4">
    <%= link_to admin_root_path, class: "text-xl font-bold" do %>
      Admin Panel
    <% end %>
  </div>

  <nav class="mt-4">
    <%= render "admin/shared/nav_section",
               title: "Dashboard",
               links: [
                 { name: "Overview", path: admin_root_path, icon: "home" },
                 { name: "Analytics", path: admin_analytics_path, icon: "chart" }
               ] %>

    <%= render "admin/shared/nav_section",
               title: "Content",
               links: [
                 { name: "Posts", path: admin_posts_path, icon: "document" },
                 { name: "Comments", path: admin_comments_path, icon: "chat" },
                 { name: "Media", path: admin_media_path, icon: "image" }
               ] %>

    <%= render "admin/shared/nav_section",
               title: "Users",
               links: [
                 { name: "All Users", path: admin_users_path, icon: "users" },
                 { name: "Roles", path: admin_roles_path, icon: "shield" }
               ] %>

    <%= render "admin/shared/nav_section",
               title: "Settings",
               links: [
                 { name: "General", path: admin_settings_path, icon: "cog" },
                 { name: "Integrations", path: admin_integrations_path, icon: "plug" }
               ] %>
  </nav>
</aside>
```

### Pattern 2: Navigation Section

```erb
<%# app/views/admin/shared/_nav_section.html.erb %>
<div class="px-4 py-2">
  <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider">
    <%= title %>
  </h3>

  <ul class="mt-2 space-y-1">
    <% links.each do |link| %>
      <li>
        <%= link_to link[:path],
            class: "flex items-center px-2 py-2 text-sm rounded-md
                   #{current_page?(link[:path]) ? 'bg-gray-800 text-white' : 'text-gray-300 hover:bg-gray-700'}" do %>
          <%= render "admin/shared/icons/#{link[:icon]}" %>
          <span class="ml-3"><%= link[:name] %></span>
        <% end %>
      </li>
    <% end %>
  </ul>
</div>
```

### Pattern 3: Admin Top Navbar

```erb
<%# app/views/admin/shared/_navbar.html.erb %>
<header class="bg-white shadow-sm border-b">
  <div class="flex items-center justify-between px-6 py-3">
    <%# Mobile menu toggle %>
    <button data-controller="sidebar" data-action="sidebar#toggle"
            class="lg:hidden p-2 rounded-md hover:bg-gray-100">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"/>
      </svg>
    </button>

    <%# Search %>
    <div class="flex-1 max-w-md ml-4">
      <%= form_with url: admin_search_path, method: :get,
                    data: { turbo_frame: "search_results" } do |f| %>
        <%= f.search_field :q, placeholder: "Search...",
            class: "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" %>
      <% end %>
    </div>

    <%# User menu %>
    <div class="flex items-center space-x-4" data-controller="dropdown">
      <%# Notifications %>
      <button class="p-2 rounded-full hover:bg-gray-100 relative">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
        </svg>
        <% if current_user.unread_notifications_count > 0 %>
          <span class="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
        <% end %>
      </button>

      <%# Profile dropdown %>
      <button data-action="dropdown#toggle" class="flex items-center space-x-2">
        <%= image_tag current_user.avatar_url, class: "w-8 h-8 rounded-full" %>
        <span class="hidden md:block"><%= current_user.name %></span>
      </button>

      <div data-dropdown-target="menu" class="hidden absolute right-0 mt-32 w-48 bg-white rounded-md shadow-lg">
        <%= link_to "Profile", admin_profile_path, class: "block px-4 py-2 hover:bg-gray-100" %>
        <%= link_to "Settings", admin_settings_path, class: "block px-4 py-2 hover:bg-gray-100" %>
        <hr class="my-1">
        <%= button_to "Sign Out", destroy_session_path, method: :delete,
                      class: "block w-full text-left px-4 py-2 hover:bg-gray-100" %>
      </div>
    </div>
  </div>
</header>
```

### Pattern 4: Page Header Component

```erb
<%# In admin view %>
<% content_for(:page_header) do %>
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Posts</h1>
      <p class="text-gray-600">Manage all blog posts</p>
    </div>
    <div class="flex space-x-3">
      <%= link_to "Export", admin_posts_path(format: :csv),
                  class: "btn btn-secondary" %>
      <%= link_to "New Post", new_admin_post_path,
                  class: "btn btn-primary" %>
    </div>
  </div>
<% end %>
```

### Pattern 5: Breadcrumbs

```erb
<%# In admin view %>
<% content_for(:breadcrumbs) do %>
  <ol class="flex items-center space-x-2 text-sm text-gray-500">
    <li><%= link_to "Dashboard", admin_root_path, class: "hover:text-gray-700" %></li>
    <li><span class="mx-2">/</span></li>
    <li><%= link_to "Posts", admin_posts_path, class: "hover:text-gray-700" %></li>
    <li><span class="mx-2">/</span></li>
    <li class="text-gray-900 font-medium"><%= @post.title %></li>
  </ol>
<% end %>
```

### Pattern 6: Controller Layout Selection

```ruby
# app/controllers/admin/base_controller.rb
module Admin
  class BaseController < ApplicationController
    layout "admin"

    before_action :authenticate_admin!

    private

    def authenticate_admin!
      redirect_to root_path unless current_user&.admin?
    end
  end
end

# app/controllers/admin/posts_controller.rb
module Admin
  class PostsController < BaseController
    def index
      @posts = Post.order(created_at: :desc).page(params[:page])
    end
  end
end
```

### Pattern 7: Responsive Sidebar with Stimulus

```javascript
// app/javascript/controllers/sidebar_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["sidebar", "overlay"]
  static classes = ["open"]

  toggle() {
    this.sidebarTarget.classList.toggle(this.openClass)
    this.overlayTarget.classList.toggle("hidden")
  }

  close() {
    this.sidebarTarget.classList.remove(this.openClass)
    this.overlayTarget.classList.add("hidden")
  }
}
```

```erb
<div data-controller="sidebar" data-sidebar-open-class="translate-x-0">
  <%# Mobile overlay %>
  <div data-sidebar-target="overlay"
       data-action="click->sidebar#close"
       class="hidden fixed inset-0 bg-black/50 lg:hidden z-40"></div>

  <%# Sidebar %>
  <aside data-sidebar-target="sidebar"
         class="fixed inset-y-0 left-0 w-64 bg-gray-900 transform -translate-x-full
                lg:translate-x-0 lg:static transition-transform z-50">
    <%# Sidebar content %>
  </aside>
</div>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Copy-paste from application layout | Maintenance burden | Use shared partials or inheritance |
| Inline admin authentication | Security risk | Use before_action in base controller |
| Fixed sidebar on mobile | Poor mobile UX | Make sidebar collapsible |
| No breadcrumbs | Users get lost | Always provide navigation context |

## Related Skills

- [application.md](./application.md): Main layout structure
- [partials.md](./partials.md): Shared partial patterns
- [../../auth/SKILL.md](../../auth/SKILL.md): Authorization setup

## References

- [Rails Layouts](https://guides.rubyonrails.org/layouts_and_rendering.html#using-layouts)
- [Tailwind Admin Templates](https://tailwindui.com/templates/application-ui)
