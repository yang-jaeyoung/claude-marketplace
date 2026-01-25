---
name: rails8-views-tailwind-setup
description: Tailwind CSS setup with Rails 8 using Import Maps or bundler
---

# Tailwind CSS Setup

## Overview

Tailwind CSS is the recommended styling approach for Rails 8 applications. Rails provides first-class support through the `tailwindcss-rails` gem, which can work with Import Maps (default) or a JavaScript bundler.

## When to Use

- When starting a new Rails 8 project
- When migrating from another CSS framework
- When you want utility-first CSS
- When building responsive, modern UIs

## Quick Start

```bash
# New Rails app with Tailwind
rails new myapp --css=tailwind

# Existing app
bundle add tailwindcss-rails
bin/rails tailwindcss:install
```

## Main Patterns

### Pattern 1: New Project Setup

```bash
# Create new Rails 8 app with Tailwind
rails new myapp \
  --database=postgresql \
  --css=tailwind \
  --skip-jbuilder

cd myapp

# Tailwind is already configured, just start development
bin/dev  # Runs Rails server + Tailwind watcher
```

### Pattern 2: Add to Existing Project

```bash
# Add gem
bundle add tailwindcss-rails

# Install Tailwind
bin/rails tailwindcss:install

# This creates:
# - config/tailwind.config.js
# - app/assets/stylesheets/application.tailwind.css
# - Updates Procfile.dev
```

### Pattern 3: Configuration File

```javascript
// config/tailwind.config.js
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    './public/*.html',
    './app/helpers/**/*.rb',
    './app/javascript/**/*.js',
    './app/views/**/*.{erb,haml,html,slim}',
    './app/components/**/*.{erb,rb}',  // ViewComponent
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter var', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

### Pattern 4: Main CSS File

```css
/* app/assets/stylesheets/application.tailwind.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom base styles */
@layer base {
  html {
    @apply scroll-smooth;
  }

  body {
    @apply antialiased;
  }

  h1 {
    @apply text-3xl font-bold tracking-tight;
  }

  h2 {
    @apply text-2xl font-semibold tracking-tight;
  }

  h3 {
    @apply text-xl font-semibold;
  }
}

/* Reusable component classes */
@layer components {
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2;
  }

  .btn-primary {
    @apply btn bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500;
  }

  .btn-secondary {
    @apply btn bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500;
  }

  .btn-danger {
    @apply btn bg-red-600 text-white hover:bg-red-700 focus:ring-red-500;
  }

  .input {
    @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm;
  }

  .input-error {
    @apply border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500;
  }

  .label {
    @apply block text-sm font-medium text-gray-700;
  }

  .card {
    @apply bg-white rounded-lg shadow-sm border border-gray-200;
  }

  .badge {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
  }

  .badge-gray {
    @apply badge bg-gray-100 text-gray-800;
  }

  .badge-green {
    @apply badge bg-green-100 text-green-800;
  }

  .badge-red {
    @apply badge bg-red-100 text-red-800;
  }

  .badge-blue {
    @apply badge bg-blue-100 text-blue-800;
  }

  .link {
    @apply text-primary-600 hover:text-primary-800 hover:underline;
  }
}

/* Custom utilities */
@layer utilities {
  .text-shadow {
    text-shadow: 0 2px 4px rgba(0,0,0,0.10);
  }

  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
}
```

### Pattern 5: Layout Template

```erb
<%# app/views/layouts/application.html.erb %>
<!DOCTYPE html>
<html lang="<%= I18n.locale %>" class="h-full">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="turbo-refresh-method" content="morph">
  <meta name="turbo-refresh-scroll" content="preserve">

  <%= csrf_meta_tags %>
  <%= csp_meta_tag %>

  <title><%= content_for(:title) || "My App" %></title>

  <%# Tailwind CSS %>
  <%= stylesheet_link_tag "tailwind", "inter-font", "data-turbo-track": "reload" %>
  <%= stylesheet_link_tag "application", "data-turbo-track": "reload" %>

  <%= javascript_importmap_tags %>
</head>
<body class="h-full bg-gray-50">
  <%= render "shared/navbar" %>

  <div id="flash">
    <%= render "shared/flash" %>
  </div>

  <main class="container mx-auto px-4 py-8 sm:px-6 lg:px-8">
    <%= yield %>
  </main>

  <%= render "shared/footer" %>
</body>
</html>
```

### Pattern 6: Procfile Configuration

```yaml
# Procfile.dev
web: bin/rails server -p 3000
css: bin/rails tailwindcss:watch
```

```bash
# Start development with both processes
bin/dev

# Or use foreman directly
gem install foreman
foreman start -f Procfile.dev
```

### Pattern 7: Production Build

```bash
# Compile Tailwind for production
bin/rails tailwindcss:build

# Or with assets precompile (automatic)
bin/rails assets:precompile

# Dockerfile snippet
RUN bin/rails tailwindcss:build
RUN bin/rails assets:precompile
```

### Pattern 8: Plugin Installation

```bash
# Install official Tailwind plugins
yarn add @tailwindcss/forms @tailwindcss/typography @tailwindcss/aspect-ratio

# Or with npm
npm install @tailwindcss/forms @tailwindcss/typography @tailwindcss/aspect-ratio
```

```javascript
// config/tailwind.config.js
module.exports = {
  // ...
  plugins: [
    require('@tailwindcss/forms'),        // Better form styling
    require('@tailwindcss/typography'),    // Prose styling
    require('@tailwindcss/aspect-ratio'),  // Aspect ratio utilities
    require('@tailwindcss/container-queries'), // Container queries
  ],
}
```

### Pattern 9: Custom Inter Font

```css
/* app/assets/stylesheets/inter-font.css */
@import url('https://rsms.me/inter/inter.css');

/* Or self-host */
@font-face {
  font-family: 'Inter var';
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  src: url('/fonts/Inter-roman.var.woff2') format('woff2');
}

@font-face {
  font-family: 'Inter var';
  font-style: italic;
  font-weight: 100 900;
  font-display: swap;
  src: url('/fonts/Inter-italic.var.woff2') format('woff2');
}
```

### Pattern 10: VS Code Configuration

```json
// .vscode/settings.json
{
  "editor.quickSuggestions": {
    "strings": true
  },
  "tailwindCSS.includeLanguages": {
    "erb": "html",
    "ruby": "html"
  },
  "tailwindCSS.experimental.classRegex": [
    ["class:\\s*\"([^\"]*)\"", "([^\"\\s]*)"],
    ["class:\\s*'([^']*)'", "([^'\\s]*)"]
  ],
  "files.associations": {
    "*.html.erb": "erb"
  }
}
```

```json
// .vscode/extensions.json
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "austenc.tailwind-docs"
  ]
}
```

## Directory Structure

```
app/
├── assets/
│   └── stylesheets/
│       ├── application.css           # Import statements
│       ├── application.tailwind.css  # Tailwind directives + custom CSS
│       └── inter-font.css            # Custom font
├── javascript/
│   └── controllers/                  # Stimulus controllers
└── views/
    └── layouts/
        └── application.html.erb      # Main layout

config/
├── tailwind.config.js                # Tailwind configuration
└── importmap.rb                      # Import map pins

Procfile.dev                          # Development processes
```

## Common Issues

### Issue: Styles Not Updating

```bash
# Restart the Tailwind watcher
bin/rails tailwindcss:watch

# Clear cache
bin/rails tmp:cache:clear

# Check content paths in tailwind.config.js
```

### Issue: Production Missing Styles

```bash
# Ensure build runs before assets:precompile
bin/rails tailwindcss:build
bin/rails assets:precompile

# Check RAILS_ENV
RAILS_ENV=production bin/rails assets:precompile
```

### Issue: PurgeCSS Removing Classes

```javascript
// config/tailwind.config.js
module.exports = {
  content: [
    // Add all template paths
    './app/views/**/*.{erb,haml,html,slim}',
    './app/helpers/**/*.rb',
    './app/components/**/*.{erb,rb}',
    './app/javascript/**/*.js',

    // Safelist dynamic classes
    // Note: prefer explicit classes over dynamic generation
  ],
  safelist: [
    'bg-red-500',
    'bg-green-500',
    { pattern: /bg-(red|green|blue)-(100|500|900)/ },
  ],
}
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Dynamic class strings | Classes get purged | Use complete class names |
| Too many @apply | Defeats utility purpose | Use utilities directly or components |
| Not using config | Inconsistent design | Define colors/spacing in config |
| Ignoring responsive | Poor mobile experience | Design mobile-first |
| Custom CSS overuse | Maintenance burden | Prefer Tailwind utilities |

## Related Skills

- [patterns.md](./patterns.md): Common Tailwind patterns
- [dark-mode.md](./dark-mode.md): Dark mode setup
- [../layouts/application.md](../layouts/application.md): Layout structure

## References

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [tailwindcss-rails Gem](https://github.com/rails/tailwindcss-rails)
- [Tailwind UI](https://tailwindui.com/)
