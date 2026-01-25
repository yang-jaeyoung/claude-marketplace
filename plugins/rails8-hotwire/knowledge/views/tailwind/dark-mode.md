---
name: rails8-views-tailwind-dark-mode
description: Dark mode implementation with system preference detection and manual toggle
---

# Dark Mode

## Overview

Tailwind CSS provides built-in dark mode support with two strategies: media-based (follows system preference) and class-based (manual toggle). This guide covers implementation patterns for Rails 8 applications.

## When to Use

- When implementing system-aware theming
- When building user-controllable dark mode
- When creating accessible color schemes
- When enhancing user experience with theme options

## Quick Start

```javascript
// config/tailwind.config.js
module.exports = {
  darkMode: 'class', // or 'media'
  // ...
}
```

```erb
<%# Dark mode classes %>
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  Content adapts to theme
</div>
```

## Main Patterns

### Pattern 1: Configuration

```javascript
// config/tailwind.config.js
module.exports = {
  // Strategy 1: Class-based (recommended for toggle)
  darkMode: 'class',

  // Strategy 2: Media-based (system preference only)
  // darkMode: 'media',

  theme: {
    extend: {
      // Custom dark colors
      colors: {
        dark: {
          bg: '#0f172a',
          surface: '#1e293b',
          border: '#334155',
          text: '#f1f5f9',
          muted: '#94a3b8',
        }
      }
    },
  },
}
```

### Pattern 2: Layout with Dark Mode

```erb
<%# app/views/layouts/application.html.erb %>
<!DOCTYPE html>
<html lang="<%= I18n.locale %>" class="<%= cookies[:theme] == 'dark' ? 'dark' : '' %>">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light dark">

  <%= csrf_meta_tags %>
  <%= csp_meta_tag %>

  <title><%= content_for(:title) || "My App" %></title>

  <%# Prevent flash of wrong theme %>
  <script>
    (function() {
      const theme = localStorage.getItem('theme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
      }
    })();
  </script>

  <%= stylesheet_link_tag "tailwind", "data-turbo-track": "reload" %>
  <%= javascript_importmap_tags %>
</head>
<body class="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
  <%= yield %>
</body>
</html>
```

### Pattern 3: Theme Toggle Controller

```javascript
// app/javascript/controllers/theme_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["icon", "label"]
  static values = { current: String }

  connect() {
    this.currentValue = this.getTheme()
    this.updateUI()

    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', this.handleSystemChange.bind(this))
  }

  toggle() {
    const newTheme = this.currentValue === 'dark' ? 'light' : 'dark'
    this.setTheme(newTheme)
  }

  setLight() {
    this.setTheme('light')
  }

  setDark() {
    this.setTheme('dark')
  }

  setSystem() {
    localStorage.removeItem('theme')
    this.applySystemPreference()
  }

  setTheme(theme) {
    localStorage.setItem('theme', theme)
    this.currentValue = theme
    this.applyTheme(theme)
    this.updateUI()
    this.saveToCookie(theme)
  }

  getTheme() {
    const stored = localStorage.getItem('theme')
    if (stored) return stored

    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  applySystemPreference() {
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    this.currentValue = systemDark ? 'dark' : 'light'
    this.applyTheme(this.currentValue)
    this.updateUI()
  }

  handleSystemChange(event) {
    if (!localStorage.getItem('theme')) {
      this.applySystemPreference()
    }
  }

  updateUI() {
    if (this.hasIconTarget) {
      this.iconTargets.forEach(icon => {
        const showFor = icon.dataset.theme
        icon.classList.toggle('hidden', showFor !== this.currentValue)
      })
    }

    if (this.hasLabelTarget) {
      this.labelTarget.textContent = this.currentValue === 'dark' ? 'Dark' : 'Light'
    }
  }

  saveToCookie(theme) {
    document.cookie = `theme=${theme};path=/;max-age=${60 * 60 * 24 * 365}`
  }
}
```

### Pattern 4: Theme Toggle Button

```erb
<%# Simple toggle button %>
<button data-controller="theme"
        data-action="theme#toggle"
        class="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
  <%# Sun icon (shown in dark mode) %>
  <svg data-theme-target="icon" data-theme="dark" class="h-5 w-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"/>
  </svg>

  <%# Moon icon (shown in light mode) %>
  <svg data-theme-target="icon" data-theme="light" class="hidden h-5 w-5 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
  </svg>
</button>

<%# Dropdown with system option %>
<div data-controller="theme dropdown" class="relative">
  <button data-action="dropdown#toggle" class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
    <span data-theme-target="label">Light</span>
    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
    </svg>
  </button>

  <div data-dropdown-target="menu" class="hidden absolute right-0 mt-2 w-36 bg-white dark:bg-gray-800 rounded-lg shadow-lg border dark:border-gray-700">
    <button data-action="theme#setLight" class="block w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700">
      Light
    </button>
    <button data-action="theme#setDark" class="block w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700">
      Dark
    </button>
    <button data-action="theme#setSystem" class="block w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700">
      System
    </button>
  </div>
</div>
```

### Pattern 5: Component Dark Mode Styles

```css
/* app/assets/stylesheets/application.tailwind.css */
@layer components {
  .card {
    @apply bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm;
  }

  .btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white;
    @apply dark:bg-blue-500 dark:hover:bg-blue-600;
  }

  .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-900;
    @apply dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white;
  }

  .input {
    @apply bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600;
    @apply text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400;
    @apply focus:border-blue-500 dark:focus:border-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400;
  }

  .nav-link {
    @apply text-gray-700 dark:text-gray-200 hover:text-gray-900 dark:hover:text-white;
  }

  .nav-link-active {
    @apply text-blue-600 dark:text-blue-400;
  }

  .divider {
    @apply border-gray-200 dark:border-gray-700;
  }

  .text-muted {
    @apply text-gray-500 dark:text-gray-400;
  }

  .bg-surface {
    @apply bg-gray-50 dark:bg-gray-900;
  }

  .bg-elevated {
    @apply bg-white dark:bg-gray-800;
  }
}
```

### Pattern 6: Image Dark Mode

```erb
<%# Different images for light/dark %>
<picture>
  <source srcset="<%= asset_path('logo-dark.svg') %>" media="(prefers-color-scheme: dark)">
  <img src="<%= asset_path('logo-light.svg') %>" alt="Logo" class="h-8">
</picture>

<%# With class-based dark mode %>
<img src="<%= asset_path('logo-light.svg') %>"
     alt="Logo"
     class="h-8 dark:hidden">
<img src="<%= asset_path('logo-dark.svg') %>"
     alt="Logo"
     class="h-8 hidden dark:block">

<%# Invert/filter for simple cases %>
<img src="<%= asset_path('icon.svg') %>"
     alt="Icon"
     class="dark:invert">
```

### Pattern 7: Charts and Graphs

```javascript
// app/javascript/controllers/chart_controller.js
import { Controller } from "@hotwired/stimulus"
import Chart from 'chart.js/auto'

export default class extends Controller {
  static values = { data: Object }

  connect() {
    this.initChart()
    this.observeTheme()
  }

  initChart() {
    const isDark = document.documentElement.classList.contains('dark')

    this.chart = new Chart(this.element, {
      type: 'line',
      data: this.dataValue,
      options: {
        plugins: {
          legend: {
            labels: { color: isDark ? '#e5e7eb' : '#374151' }
          }
        },
        scales: {
          x: {
            ticks: { color: isDark ? '#9ca3af' : '#6b7280' },
            grid: { color: isDark ? '#374151' : '#e5e7eb' }
          },
          y: {
            ticks: { color: isDark ? '#9ca3af' : '#6b7280' },
            grid: { color: isDark ? '#374151' : '#e5e7eb' }
          }
        }
      }
    })
  }

  observeTheme() {
    const observer = new MutationObserver(() => {
      this.chart.destroy()
      this.initChart()
    })

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    })
  }
}
```

### Pattern 8: Server-Side Theme

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  before_action :set_theme

  private

  def set_theme
    @theme = cookies[:theme] || 'light'
  end

  helper_method :dark_mode?
  def dark_mode?
    @theme == 'dark'
  end
end

# app/controllers/themes_controller.rb
class ThemesController < ApplicationController
  def update
    cookies[:theme] = {
      value: params[:theme],
      expires: 1.year.from_now,
      path: '/'
    }

    head :ok
  end
end
```

### Pattern 9: Color Palette

```css
/* Define semantic colors for both themes */
@layer base {
  :root {
    --color-bg-primary: 255 255 255;
    --color-bg-secondary: 249 250 251;
    --color-text-primary: 17 24 39;
    --color-text-secondary: 107 114 128;
    --color-border: 229 231 235;
    --color-accent: 59 130 246;
  }

  .dark {
    --color-bg-primary: 17 24 39;
    --color-bg-secondary: 31 41 55;
    --color-text-primary: 243 244 246;
    --color-text-secondary: 156 163 175;
    --color-border: 55 65 81;
    --color-accent: 96 165 250;
  }
}
```

```javascript
// config/tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        bg: {
          primary: 'rgb(var(--color-bg-primary) / <alpha-value>)',
          secondary: 'rgb(var(--color-bg-secondary) / <alpha-value>)',
        },
        text: {
          primary: 'rgb(var(--color-text-primary) / <alpha-value>)',
          secondary: 'rgb(var(--color-text-secondary) / <alpha-value>)',
        },
        border: 'rgb(var(--color-border) / <alpha-value>)',
        accent: 'rgb(var(--color-accent) / <alpha-value>)',
      }
    }
  }
}
```

```erb
<%# Usage - no dark: prefix needed %>
<div class="bg-bg-primary text-text-primary border-border">
  <p class="text-text-secondary">Automatically adapts to theme</p>
</div>
```

### Pattern 10: Accessibility Considerations

```css
/* Ensure sufficient contrast in both modes */
@layer components {
  /* Links */
  .link {
    @apply text-blue-600 dark:text-blue-400;
    @apply hover:text-blue-800 dark:hover:text-blue-300;
    @apply underline decoration-blue-600/30 dark:decoration-blue-400/30;
  }

  /* Focus rings visible in both modes */
  .focus-ring {
    @apply focus:outline-none focus:ring-2 focus:ring-offset-2;
    @apply focus:ring-blue-500 dark:focus:ring-blue-400;
    @apply focus:ring-offset-white dark:focus:ring-offset-gray-900;
  }

  /* Error states */
  .error-text {
    @apply text-red-600 dark:text-red-400;
  }

  /* Success states */
  .success-text {
    @apply text-green-600 dark:text-green-400;
  }
}
```

## Testing Dark Mode

```ruby
# spec/system/dark_mode_spec.rb
require "rails_helper"

RSpec.describe "Dark Mode", type: :system do
  it "toggles dark mode" do
    visit root_path

    # Start in light mode
    expect(page).not_to have_css("html.dark")

    # Toggle to dark
    click_button "Toggle theme"
    expect(page).to have_css("html.dark")

    # Persists after reload
    visit root_path
    expect(page).to have_css("html.dark")
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Forgetting dark variants | Broken dark UI | Add dark: for all color classes |
| Pure black backgrounds | Eye strain | Use dark gray (gray-900) |
| Low contrast text | Accessibility issues | Test contrast ratios |
| Flash of wrong theme | Poor UX | Add inline theme script in head |
| Not testing both modes | Hidden bugs | Test UI in both themes |

## Related Skills

- [setup.md](./setup.md): Tailwind installation
- [patterns.md](./patterns.md): Component patterns
- [../layouts/application.md](../layouts/application.md): Layout setup

## References

- [Tailwind Dark Mode](https://tailwindcss.com/docs/dark-mode)
- [prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
