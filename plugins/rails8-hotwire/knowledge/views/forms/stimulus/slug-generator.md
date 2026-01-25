---
name: rails8-stimulus-slug-generator
description: Auto-generate URL slugs from title fields
---

# Slug Generator

## Overview

Automatically generates URL-friendly slugs from title or name fields, with the ability to lock and manually edit.

## Controller Code

```javascript
// app/javascript/controllers/slug_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["source", "slug"]
  static values = { locked: { type: Boolean, default: false } }

  generate() {
    if (this.lockedValue) return

    const text = this.sourceTarget.value
    const slug = text
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .trim()

    this.slugTarget.value = slug
  }

  lock() {
    this.lockedValue = true
    this.slugTarget.readOnly = false
  }
}
```

## ERB Usage

```erb
<div data-controller="slug">
  <div class="mb-4">
    <%= f.label :title %>
    <%= f.text_field :title,
        data: {
          slug_target: "source",
          action: "input->slug#generate"
        } %>
  </div>

  <div class="mb-4">
    <%= f.label :slug %>
    <div class="flex gap-2">
      <%= f.text_field :slug,
          readonly: @post.new_record?,
          data: { slug_target: "slug" } %>
      <button type="button" data-action="slug#lock" class="btn btn-secondary">
        Edit
      </button>
    </div>
  </div>
</div>
```

## Features

- **Auto-generation**: Creates slug as user types title
- **URL-safe**: Removes special characters, converts spaces to hyphens
- **Lock mechanism**: Prevents auto-generation once manually edited
- **Readonly by default**: Prevents accidental edits
- **Edit button**: Unlocks for manual editing when needed

## Slug Transformation

| Input | Output |
|-------|--------|
| "Hello World" | "hello-world" |
| "Rails 8 Guide" | "rails-8-guide" |
| "API Development" | "api-development" |
| "Test & Debug" | "test-debug" |
| "Multiple   Spaces" | "multiple-spaces" |

## Transformation Rules

1. Convert to lowercase
2. Remove non-word characters (except spaces and hyphens)
3. Replace spaces with hyphens
4. Replace multiple hyphens with single hyphen
5. Trim leading/trailing whitespace

## Advanced Version with Preview

```javascript
// app/javascript/controllers/slug_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["source", "slug", "preview"]
  static values = {
    locked: { type: Boolean, default: false },
    baseUrl: String
  }

  generate() {
    if (this.lockedValue) return

    const text = this.sourceTarget.value
    const slug = this.slugify(text)

    this.slugTarget.value = slug
    this.updatePreview(slug)
  }

  slugify(text) {
    return text
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .trim()
  }

  updatePreview(slug) {
    if (this.hasPreviewTarget) {
      this.previewTarget.textContent = `${this.baseUrlValue}/${slug}`
    }
  }

  lock() {
    this.lockedValue = true
    this.slugTarget.readOnly = false
  }

  unlock() {
    this.lockedValue = false
  }
}
```

```erb
<div data-controller="slug" data-slug-base-url-value="<%= root_url %>posts">
  <%= f.text_field :title,
      data: { slug_target: "source", action: "input->slug#generate" } %>

  <div class="flex gap-2">
    <%= f.text_field :slug,
        readonly: true,
        data: { slug_target: "slug" } %>
    <button type="button" data-action="slug#lock">Edit</button>
  </div>

  <p class="text-sm text-gray-500">
    URL: <span data-slug-target="preview"></span>
  </p>
</div>
```

## With Server-Side Uniqueness Check

```javascript
async checkUniqueness() {
  const slug = this.slugTarget.value

  const response = await fetch(`/posts/check_slug?slug=${slug}`)
  const data = await response.json()

  if (!data.available) {
    this.showError("Slug already taken")
    this.suggestAlternative(data.alternative)
  }
}

suggestAlternative(alternative) {
  if (confirm(`Slug taken. Use "${alternative}" instead?`)) {
    this.slugTarget.value = alternative
  }
}
```

## Controller for Uniqueness Check

```ruby
# app/controllers/posts_controller.rb
def check_slug
  slug = params[:slug]
  available = !Post.exists?(slug: slug)

  alternative = if !available
    counter = 1
    counter += 1 while Post.exists?(slug: "#{slug}-#{counter}")
    "#{slug}-#{counter}"
  end

  render json: { available: available, alternative: alternative }
end
```

## Related Skills

- [SKILL.md](./SKILL.md): All form Stimulus patterns
- [validation.md](./validation.md): Client-side validation
- [character-counter.md](./character-counter.md): Character counting
