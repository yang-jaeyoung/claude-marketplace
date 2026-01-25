---
name: rails8-views-layout-partials
description: Layout partials guide for navbar, footer, sidebar, and other shared elements
---

# Layout Partials

## Overview

Layout partials are reusable view components shared across layouts. Common examples include navigation bars, footers, sidebars, and flash messages. Organized in `app/views/shared/` or `app/views/layouts/`.

## When to Use

- When building navigation components
- When creating reusable layout elements
- When standardizing headers and footers
- When implementing flash message displays

## Quick Start

```erb
<%# app/views/shared/_navbar.html.erb %>
<nav class="bg-white shadow" data-controller="navbar">
  <div class="container mx-auto px-4">
    <div class="flex items-center justify-between h-16">
      <%# Logo %>
      <%= link_to root_path, class: "flex items-center" do %>
        <%= image_tag "logo.svg", class: "h-8 w-auto", alt: "Logo" %>
      <% end %>

      <%# Desktop navigation %>
      <div class="hidden md:flex items-center space-x-8">
        <%= nav_link "Home", root_path %>
        <%= nav_link "Features", features_path %>
        <%= nav_link "Pricing", pricing_path %>
        <%= nav_link "Blog", posts_path %>
      </div>

      <%# Auth section %>
      <div class="flex items-center space-x-4">
        <% if user_signed_in? %>
          <%= render "shared/user_menu" %>
        <% else %>
          <%= link_to "Sign In", new_session_path, class: "text-gray-600 hover:text-gray-900" %>
          <%= link_to "Get Started", new_registration_path, class: "btn btn-primary" %>
        <% end %>
      </div>

      <%# Mobile menu button %>
      <button data-action="navbar#toggleMobile" class="md:hidden p-2">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
    </div>

    <%# Mobile menu %>
    <div data-navbar-target="mobileMenu" class="hidden md:hidden pb-4">
      <%= nav_link "Home", root_path, mobile: true %>
      <%= nav_link "Features", features_path, mobile: true %>
      <%= nav_link "Pricing", pricing_path, mobile: true %>
      <%= nav_link "Blog", posts_path, mobile: true %>
    </div>
  </div>
</nav>
```

## Main Patterns

### Pattern 1: Navigation Helper

```ruby
# app/helpers/navigation_helper.rb
module NavigationHelper
  def nav_link(text, path, mobile: false, **options)
    base_class = mobile ? "block py-2 px-4" : "inline-flex items-center"
    active_class = current_page?(path) ? "text-blue-600 font-medium" : "text-gray-600 hover:text-gray-900"

    link_to text, path, class: "#{base_class} #{active_class}", **options
  end

  def nav_dropdown(title, &block)
    content_tag :div, class: "relative", data: { controller: "dropdown" } do
      button = button_tag(title, type: "button",
        class: "flex items-center text-gray-600 hover:text-gray-900",
        data: { action: "dropdown#toggle" })

      menu = content_tag(:div, capture(&block),
        class: "absolute top-full right-0 mt-2 w-48 bg-white rounded-lg shadow-lg hidden",
        data: { dropdown_target: "menu" })

      button + menu
    end
  end
end
```

### Pattern 2: User Menu Dropdown

```erb
<%# app/views/shared/_user_menu.html.erb %>
<div class="relative" data-controller="dropdown">
  <button data-action="dropdown#toggle"
          class="flex items-center space-x-2 focus:outline-none">
    <%= image_tag current_user.avatar_url,
                  class: "w-8 h-8 rounded-full",
                  alt: current_user.name %>
    <span class="hidden md:block text-sm"><%= current_user.name %></span>
    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
    </svg>
  </button>

  <div data-dropdown-target="menu"
       class="hidden absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 z-50">
    <%= link_to "Your Profile", profile_path,
                class: "block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" %>
    <%= link_to "Settings", settings_path,
                class: "block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" %>

    <% if current_user.admin? %>
      <hr class="my-1">
      <%= link_to "Admin", admin_root_path,
                  class: "block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" %>
    <% end %>

    <hr class="my-1">
    <%= button_to "Sign Out", session_path, method: :delete,
                  class: "block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" %>
  </div>
</div>
```

### Pattern 3: Footer Partial

```erb
<%# app/views/shared/_footer.html.erb %>
<footer class="bg-gray-900 text-gray-300">
  <div class="container mx-auto px-4 py-12">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
      <%# Brand column %>
      <div class="md:col-span-1">
        <%= image_tag "logo-white.svg", class: "h-8 w-auto mb-4" %>
        <p class="text-sm">Building the future of web applications.</p>
        <div class="flex space-x-4 mt-4">
          <%= link_to "https://twitter.com/myapp", class: "hover:text-white" do %>
            <svg class="w-5 h-5" fill="currentColor"><!-- Twitter icon --></svg>
          <% end %>
          <%= link_to "https://github.com/myapp", class: "hover:text-white" do %>
            <svg class="w-5 h-5" fill="currentColor"><!-- GitHub icon --></svg>
          <% end %>
        </div>
      </div>

      <%# Product column %>
      <div>
        <h3 class="text-white font-semibold mb-4">Product</h3>
        <ul class="space-y-2 text-sm">
          <li><%= link_to "Features", features_path, class: "hover:text-white" %></li>
          <li><%= link_to "Pricing", pricing_path, class: "hover:text-white" %></li>
          <li><%= link_to "Changelog", changelog_path, class: "hover:text-white" %></li>
          <li><%= link_to "API Docs", docs_path, class: "hover:text-white" %></li>
        </ul>
      </div>

      <%# Company column %>
      <div>
        <h3 class="text-white font-semibold mb-4">Company</h3>
        <ul class="space-y-2 text-sm">
          <li><%= link_to "About", about_path, class: "hover:text-white" %></li>
          <li><%= link_to "Blog", posts_path, class: "hover:text-white" %></li>
          <li><%= link_to "Careers", careers_path, class: "hover:text-white" %></li>
          <li><%= link_to "Contact", contact_path, class: "hover:text-white" %></li>
        </ul>
      </div>

      <%# Legal column %>
      <div>
        <h3 class="text-white font-semibold mb-4">Legal</h3>
        <ul class="space-y-2 text-sm">
          <li><%= link_to "Privacy Policy", privacy_path, class: "hover:text-white" %></li>
          <li><%= link_to "Terms of Service", terms_path, class: "hover:text-white" %></li>
          <li><%= link_to "Cookie Policy", cookies_path, class: "hover:text-white" %></li>
        </ul>
      </div>
    </div>

    <hr class="border-gray-800 my-8">

    <div class="flex flex-col md:flex-row justify-between items-center text-sm">
      <p>&copy; <%= Date.current.year %> MyApp. All rights reserved.</p>
      <p class="mt-4 md:mt-0">Made with Ruby on Rails</p>
    </div>
  </div>
</footer>
```

### Pattern 4: Sidebar Partial

```erb
<%# app/views/shared/_sidebar.html.erb %>
<%# locals: (sections:, current_path: request.path) %>
<aside class="w-64 bg-white border-r h-full">
  <nav class="p-4 space-y-6">
    <% sections.each do |section| %>
      <div>
        <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
          <%= section[:title] %>
        </h3>
        <ul class="space-y-1">
          <% section[:links].each do |link| %>
            <li>
              <%= link_to link[:path],
                  class: "flex items-center px-3 py-2 text-sm rounded-md
                         #{current_path == link[:path] ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'}" do %>
                <% if link[:icon] %>
                  <%= render "shared/icons/#{link[:icon]}", css_class: "w-5 h-5 mr-3" %>
                <% end %>
                <%= link[:name] %>
                <% if link[:badge] %>
                  <span class="ml-auto bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs">
                    <%= link[:badge] %>
                  </span>
                <% end %>
              <% end %>
            </li>
          <% end %>
        </ul>
      </div>
    <% end %>
  </nav>
</aside>

<%# Usage %>
<%= render "shared/sidebar", sections: [
  {
    title: "Overview",
    links: [
      { name: "Dashboard", path: dashboard_path, icon: "home" },
      { name: "Analytics", path: analytics_path, icon: "chart" }
    ]
  },
  {
    title: "Content",
    links: [
      { name: "Posts", path: posts_path, icon: "document", badge: Post.draft.count },
      { name: "Media", path: media_path, icon: "image" }
    ]
  }
] %>
```

### Pattern 5: Breadcrumb Partial

```erb
<%# app/views/shared/_breadcrumbs.html.erb %>
<%# locals: (items:) %>
<nav aria-label="Breadcrumb" class="mb-4">
  <ol class="flex items-center space-x-2 text-sm text-gray-500">
    <li>
      <%= link_to root_path, class: "hover:text-gray-700" do %>
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
        </svg>
      <% end %>
    </li>
    <% items.each_with_index do |item, index| %>
      <li class="flex items-center">
        <svg class="w-4 h-4 text-gray-400 mx-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"/>
        </svg>
        <% if index == items.length - 1 %>
          <span class="text-gray-900 font-medium"><%= item[:name] %></span>
        <% else %>
          <%= link_to item[:name], item[:path], class: "hover:text-gray-700" %>
        <% end %>
      </li>
    <% end %>
  </ol>
</nav>

<%# Usage %>
<%= render "shared/breadcrumbs", items: [
  { name: "Posts", path: posts_path },
  { name: @post.title, path: nil }
] %>
```

### Pattern 6: Navbar Stimulus Controller

```javascript
// app/javascript/controllers/navbar_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["mobileMenu"]
  static classes = ["menuOpen"]

  toggleMobile() {
    this.mobileMenuTarget.classList.toggle("hidden")
  }

  closeMobile() {
    this.mobileMenuTarget.classList.add("hidden")
  }

  // Close menu when clicking outside
  clickOutside(event) {
    if (!this.element.contains(event.target)) {
      this.closeMobile()
    }
  }

  connect() {
    document.addEventListener("click", this.clickOutside.bind(this))
  }

  disconnect() {
    document.removeEventListener("click", this.clickOutside.bind(this))
  }
}
```

## Partial Organization

```
app/views/
├── layouts/
│   ├── application.html.erb
│   ├── admin.html.erb
│   └── mailer.html.erb
└── shared/
    ├── _navbar.html.erb
    ├── _footer.html.erb
    ├── _sidebar.html.erb
    ├── _flash.html.erb
    ├── _breadcrumbs.html.erb
    ├── _user_menu.html.erb
    ├── _pagination.html.erb
    └── icons/
        ├── _home.html.erb
        ├── _chart.html.erb
        └── _document.html.erb
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Logic in partials | Hard to test | Use helpers or presenters |
| Deeply nested partials | Performance hit, hard to trace | Maximum 2 levels deep |
| Hardcoded paths | Breaks on route changes | Use path helpers |
| No mobile consideration | Poor mobile UX | Always design responsive |
| Inline Tailwind everywhere | Inconsistent styling | Extract component classes |

## Related Skills

- [application.md](./application.md): Main layout structure
- [admin.md](./admin.md): Admin layout variant
- [../partials/conventions.md](../partials/conventions.md): Partial naming conventions

## References

- [Rails Partials](https://guides.rubyonrails.org/layouts_and_rendering.html#using-partials)
- [Stimulus Handbook](https://stimulus.hotwired.dev/handbook/introduction)
