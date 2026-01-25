---
name: rails8-views-tailwind-patterns
description: Common Tailwind CSS utility patterns, component classes, and @apply usage
---

# Tailwind CSS Patterns

## Overview

Tailwind's utility-first approach provides patterns for common UI elements. This guide covers reusable patterns, component extraction with @apply, and responsive design approaches.

## When to Use

- When building consistent UI components
- When implementing responsive layouts
- When creating reusable style patterns
- When balancing utilities vs component classes

## Quick Start

```erb
<%# Utility-first approach %>
<button class="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
  Save
</button>

<%# With extracted component class %>
<button class="btn btn-primary">Save</button>
```

## Main Patterns

### Pattern 1: Button Variants

```css
/* app/assets/stylesheets/application.tailwind.css */
@layer components {
  .btn {
    @apply inline-flex items-center justify-center font-medium rounded-md transition-colors;
    @apply focus:outline-none focus:ring-2 focus:ring-offset-2;
  }

  /* Size variants */
  .btn-sm { @apply px-3 py-1.5 text-sm; }
  .btn-md { @apply px-4 py-2 text-sm; }
  .btn-lg { @apply px-6 py-3 text-base; }

  /* Color variants */
  .btn-primary {
    @apply bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500;
  }

  .btn-secondary {
    @apply bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500;
  }

  .btn-danger {
    @apply bg-red-600 text-white hover:bg-red-700 focus:ring-red-500;
  }

  .btn-success {
    @apply bg-green-600 text-white hover:bg-green-700 focus:ring-green-500;
  }

  .btn-ghost {
    @apply text-gray-700 hover:bg-gray-100 focus:ring-gray-500;
  }

  .btn-link {
    @apply text-blue-600 hover:text-blue-800 hover:underline p-0 focus:ring-0;
  }

  /* States */
  .btn:disabled, .btn-disabled {
    @apply opacity-50 cursor-not-allowed pointer-events-none;
  }

  /* Icon button */
  .btn-icon {
    @apply p-2 rounded-full;
  }
}
```

```erb
<%# Usage %>
<%= link_to "Save", save_path, class: "btn btn-md btn-primary" %>
<%= link_to "Cancel", :back, class: "btn btn-md btn-secondary" %>
<%= button_to "Delete", post_path(@post), method: :delete, class: "btn btn-sm btn-danger" %>
```

### Pattern 2: Form Inputs

```css
@layer components {
  .form-group {
    @apply mb-4;
  }

  .form-label {
    @apply block text-sm font-medium text-gray-700 mb-1;
  }

  .form-input {
    @apply block w-full rounded-md border-gray-300 shadow-sm;
    @apply focus:border-blue-500 focus:ring-blue-500 sm:text-sm;
  }

  .form-input-error {
    @apply border-red-300 text-red-900 placeholder-red-300;
    @apply focus:border-red-500 focus:ring-red-500;
  }

  .form-select {
    @apply block w-full rounded-md border-gray-300 shadow-sm;
    @apply focus:border-blue-500 focus:ring-blue-500 sm:text-sm;
  }

  .form-checkbox {
    @apply h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500;
  }

  .form-radio {
    @apply h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500;
  }

  .form-hint {
    @apply mt-1 text-sm text-gray-500;
  }

  .form-error {
    @apply mt-1 text-sm text-red-600;
  }
}
```

```erb
<div class="form-group">
  <%= f.label :email, class: "form-label" %>
  <%= f.email_field :email, class: "form-input #{@user.errors[:email].any? ? 'form-input-error' : ''}" %>
  <% if @user.errors[:email].any? %>
    <p class="form-error"><%= @user.errors[:email].first %></p>
  <% else %>
    <p class="form-hint">We'll never share your email.</p>
  <% end %>
</div>
```

### Pattern 3: Card Component

```css
@layer components {
  .card {
    @apply bg-white rounded-lg shadow-sm border border-gray-200;
  }

  .card-hover {
    @apply card hover:shadow-md transition-shadow;
  }

  .card-header {
    @apply px-6 py-4 border-b border-gray-200;
  }

  .card-body {
    @apply p-6;
  }

  .card-footer {
    @apply px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-lg;
  }

  .card-title {
    @apply text-lg font-semibold text-gray-900;
  }

  .card-subtitle {
    @apply text-sm text-gray-500;
  }
}
```

```erb
<div class="card">
  <div class="card-header">
    <h3 class="card-title"><%= @post.title %></h3>
    <p class="card-subtitle">Published <%= time_ago_in_words(@post.published_at) %> ago</p>
  </div>
  <div class="card-body">
    <p><%= @post.excerpt %></p>
  </div>
  <div class="card-footer flex justify-between">
    <%= link_to "Read more", @post, class: "btn-link" %>
    <%= link_to "Edit", edit_post_path(@post), class: "btn btn-sm btn-secondary" %>
  </div>
</div>
```

### Pattern 4: Badge/Tag

```css
@layer components {
  .badge {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
  }

  .badge-gray { @apply bg-gray-100 text-gray-800; }
  .badge-red { @apply bg-red-100 text-red-800; }
  .badge-yellow { @apply bg-yellow-100 text-yellow-800; }
  .badge-green { @apply bg-green-100 text-green-800; }
  .badge-blue { @apply bg-blue-100 text-blue-800; }
  .badge-purple { @apply bg-purple-100 text-purple-800; }

  /* Dot indicator */
  .badge-dot {
    @apply flex items-center;
  }

  .badge-dot::before {
    content: '';
    @apply w-1.5 h-1.5 rounded-full mr-1.5;
  }

  .badge-dot-green::before { @apply bg-green-400; }
  .badge-dot-red::before { @apply bg-red-400; }
  .badge-dot-yellow::before { @apply bg-yellow-400; }
}
```

```erb
<span class="badge badge-green">Published</span>
<span class="badge badge-yellow">Draft</span>
<span class="badge badge-dot badge-dot-green badge-gray">Online</span>
```

### Pattern 5: Navigation

```erb
<%# Horizontal nav %>
<nav class="flex space-x-4">
  <%= link_to "Home", root_path,
      class: "px-3 py-2 rounded-md text-sm font-medium
             #{current_page?(root_path) ? 'bg-gray-900 text-white' : 'text-gray-700 hover:bg-gray-100'}" %>
  <%= link_to "Posts", posts_path,
      class: "px-3 py-2 rounded-md text-sm font-medium
             #{current_page?(posts_path) ? 'bg-gray-900 text-white' : 'text-gray-700 hover:bg-gray-100'}" %>
</nav>

<%# Vertical sidebar nav %>
<nav class="space-y-1">
  <% [
    { name: "Dashboard", path: dashboard_path, icon: "home" },
    { name: "Posts", path: posts_path, icon: "document" },
    { name: "Settings", path: settings_path, icon: "cog" }
  ].each do |item| %>
    <%= link_to item[:path],
        class: "flex items-center px-3 py-2 text-sm font-medium rounded-md
               #{current_page?(item[:path]) ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}" do %>
      <%= render "shared/icons/#{item[:icon]}", class: "mr-3 h-5 w-5" %>
      <%= item[:name] %>
    <% end %>
  <% end %>
</nav>
```

### Pattern 6: Table

```erb
<div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
  <table class="min-w-full divide-y divide-gray-300">
    <thead class="bg-gray-50">
      <tr>
        <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
          Name
        </th>
        <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
          Email
        </th>
        <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
          Status
        </th>
        <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
          <span class="sr-only">Actions</span>
        </th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200 bg-white">
      <% @users.each do |user| %>
        <tr class="hover:bg-gray-50">
          <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
            <%= user.name %>
          </td>
          <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
            <%= user.email %>
          </td>
          <td class="whitespace-nowrap px-3 py-4 text-sm">
            <span class="badge <%= user.active? ? 'badge-green' : 'badge-gray' %>">
              <%= user.active? ? 'Active' : 'Inactive' %>
            </span>
          </td>
          <td class="whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
            <%= link_to "Edit", edit_user_path(user), class: "text-blue-600 hover:text-blue-900" %>
          </td>
        </tr>
      <% end %>
    </tbody>
  </table>
</div>
```

### Pattern 7: Alert/Notice

```erb
<%# app/views/shared/_flash.html.erb %>
<% flash.each do |type, message| %>
  <%
    styles = {
      notice: "bg-green-50 text-green-800 border-green-200",
      alert: "bg-red-50 text-red-800 border-red-200",
      warning: "bg-yellow-50 text-yellow-800 border-yellow-200",
      info: "bg-blue-50 text-blue-800 border-blue-200"
    }
    icon_colors = {
      notice: "text-green-400",
      alert: "text-red-400",
      warning: "text-yellow-400",
      info: "text-blue-400"
    }
  %>
  <div class="rounded-md border p-4 mb-4 <%= styles[type.to_sym] %>"
       data-controller="dismissible"
       data-dismissible-remove-delay-value="5000">
    <div class="flex">
      <div class="flex-shrink-0">
        <svg class="h-5 w-5 <%= icon_colors[type.to_sym] %>" viewBox="0 0 20 20" fill="currentColor">
          <!-- Icon path based on type -->
        </svg>
      </div>
      <div class="ml-3 flex-1">
        <p class="text-sm font-medium"><%= message %></p>
      </div>
      <div class="ml-auto pl-3">
        <button data-action="dismissible#dismiss" class="-m-1.5 p-1.5 rounded-md hover:bg-black/5 focus:outline-none">
          <span class="sr-only">Dismiss</span>
          <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
<% end %>
```

### Pattern 8: Modal Dialog

```erb
<%# Modal container %>
<div class="fixed inset-0 z-50 overflow-y-auto" data-controller="modal">
  <%# Backdrop %>
  <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
       data-action="click->modal#close"></div>

  <%# Modal panel %>
  <div class="flex min-h-full items-center justify-center p-4">
    <div class="relative w-full max-w-lg transform overflow-hidden rounded-lg bg-white shadow-xl transition-all"
         data-modal-target="content">
      <%# Header %>
      <div class="flex items-center justify-between px-6 py-4 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Modal Title</h3>
        <button type="button" data-action="modal#close"
                class="text-gray-400 hover:text-gray-500">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <%# Body %>
      <div class="px-6 py-4">
        <p class="text-sm text-gray-500">Modal content goes here.</p>
      </div>

      <%# Footer %>
      <div class="flex justify-end gap-3 px-6 py-4 bg-gray-50">
        <button type="button" class="btn btn-md btn-secondary" data-action="modal#close">
          Cancel
        </button>
        <button type="button" class="btn btn-md btn-primary">
          Confirm
        </button>
      </div>
    </div>
  </div>
</div>
```

### Pattern 9: Responsive Grid

```erb
<%# Auto-fit grid %>
<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
  <% @items.each do |item| %>
    <div class="card">
      <%= render item %>
    </div>
  <% end %>
</div>

<%# Sidebar layout %>
<div class="lg:grid lg:grid-cols-12 lg:gap-8">
  <main class="lg:col-span-8">
    <%# Main content %>
  </main>
  <aside class="mt-8 lg:mt-0 lg:col-span-4">
    <%# Sidebar %>
  </aside>
</div>

<%# Holy grail layout %>
<div class="min-h-screen flex flex-col">
  <header class="bg-white shadow">
    <%# Header %>
  </header>
  <div class="flex-1 flex">
    <nav class="w-64 bg-gray-50 hidden lg:block">
      <%# Sidebar %>
    </nav>
    <main class="flex-1 p-6">
      <%# Content %>
    </main>
  </div>
  <footer class="bg-gray-800 text-white">
    <%# Footer %>
  </footer>
</div>
```

### Pattern 10: Loading States

```css
@layer components {
  .skeleton {
    @apply animate-pulse bg-gray-200 rounded;
  }

  .spinner {
    @apply animate-spin rounded-full border-2 border-gray-300 border-t-blue-600;
  }

  .spinner-sm { @apply h-4 w-4; }
  .spinner-md { @apply h-6 w-6; }
  .spinner-lg { @apply h-8 w-8; }
}

@layer utilities {
  .loading-overlay {
    @apply absolute inset-0 bg-white/75 flex items-center justify-center;
  }
}
```

```erb
<%# Skeleton loader %>
<div class="card">
  <div class="card-body space-y-4">
    <div class="skeleton h-4 w-3/4"></div>
    <div class="skeleton h-4 w-full"></div>
    <div class="skeleton h-4 w-5/6"></div>
  </div>
</div>

<%# Spinner button %>
<button type="submit" class="btn btn-primary" data-turbo-submits-with="...">
  <span class="spinner spinner-sm mr-2 hidden" data-loading></span>
  Submit
</button>
```

## Responsive Breakpoints

| Prefix | Minimum width | CSS |
|--------|---------------|-----|
| `sm:` | 640px | `@media (min-width: 640px)` |
| `md:` | 768px | `@media (min-width: 768px)` |
| `lg:` | 1024px | `@media (min-width: 1024px)` |
| `xl:` | 1280px | `@media (min-width: 1280px)` |
| `2xl:` | 1536px | `@media (min-width: 1536px)` |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Too much @apply | Defeats utility purpose | Use utilities directly for unique styles |
| Dynamic class strings | Classes get purged | Use complete class names |
| Inconsistent spacing | Visual inconsistency | Use spacing scale consistently |
| !important abuse | Specificity wars | Fix cascade instead |
| Ignoring hover/focus | Poor accessibility | Always add interactive states |

## Related Skills

- [setup.md](./setup.md): Tailwind installation
- [dark-mode.md](./dark-mode.md): Dark mode patterns
- [../components/view-component.md](../components/view-component.md): Component styling

## References

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind UI Components](https://tailwindui.com/)
- [Headless UI](https://headlessui.dev/)
