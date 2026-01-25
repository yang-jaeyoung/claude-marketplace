---
name: rails8-stimulus-autosave
description: Debounced autosave with status feedback
---

# Autosave

## Overview

Automatically saves form data after a configurable delay, with visual status feedback for saving, success, and errors.

## Controller Code

```javascript
// app/javascript/controllers/autosave_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["status", "form"]
  static values = {
    delay: { type: Number, default: 2000 },
    url: String
  }

  connect() {
    this.timeout = null
  }

  save() {
    clearTimeout(this.timeout)
    this.timeout = setTimeout(() => this.performSave(), this.delayValue)
  }

  async performSave() {
    this.showStatus("Saving...")

    const formData = new FormData(this.hasFormTarget ? this.formTarget : this.element)

    try {
      const response = await fetch(this.urlValue || this.element.action, {
        method: "PATCH",
        body: formData,
        headers: {
          "Accept": "application/json",
          "X-CSRF-Token": document.querySelector("[name='csrf-token']").content
        }
      })

      if (response.ok) {
        this.showStatus("Saved", "success")
      } else {
        this.showStatus("Save failed", "error")
      }
    } catch (error) {
      this.showStatus("Connection error", "error")
    }
  }

  showStatus(message, type = "info") {
    if (this.hasStatusTarget) {
      this.statusTarget.textContent = message
      this.statusTarget.className = `autosave-status autosave-${type}`

      if (type === "success") {
        setTimeout(() => {
          this.statusTarget.textContent = ""
        }, 2000)
      }
    }
  }
}
```

## ERB Usage

```erb
<%= form_with model: @draft,
    data: {
      controller: "autosave",
      autosave_url_value: autosave_draft_path(@draft),
      autosave_delay_value: 3000
    } do |f| %>

  <div class="flex justify-between items-center mb-4">
    <h1>Edit Draft</h1>
    <span data-autosave-target="status" class="text-sm text-gray-500"></span>
  </div>

  <%= f.text_field :title,
      data: { action: "input->autosave#save" } %>

  <%= f.text_area :body,
      data: { action: "input->autosave#save" } %>

  <%= f.submit "Publish" %>
<% end %>
```

## Controller Setup

```ruby
# app/controllers/drafts_controller.rb
class DraftsController < ApplicationController
  def autosave
    @draft = Draft.find(params[:id])

    if @draft.update(draft_params)
      render json: { status: "saved" }
    else
      render json: { status: "error", errors: @draft.errors }, status: :unprocessable_entity
    end
  end

  private

  def draft_params
    params.require(:draft).permit(:title, :body)
  end
end
```

## Routes

```ruby
# config/routes.rb
resources :drafts do
  member do
    patch :autosave
  end
end
```

## Features

- **Debounced saving**: Waits for typing to stop before saving
- **Status feedback**: Shows "Saving...", "Saved", or error messages
- **Configurable delay**: Default 2 seconds, customizable via data attribute
- **Custom URL**: Optional separate endpoint for autosave
- **CSRF protection**: Automatically includes Rails CSRF token

## Styling Example

```css
/* app/assets/stylesheets/autosave.css */
.autosave-status {
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.autosave-info {
  color: #6b7280;
}

.autosave-success {
  color: #059669;
  background-color: #d1fae5;
}

.autosave-error {
  color: #dc2626;
  background-color: #fee2e2;
}
```

## Related Skills

- [SKILL.md](./SKILL.md): All form Stimulus patterns
- [dirty-tracking.md](./dirty-tracking.md): Unsaved changes warning
- [validation.md](./validation.md): Client-side validation
