---
name: rails8-stimulus-dirty-tracking
description: Warn users about unsaved changes before leaving
---

# Form Dirty Tracking

## Overview

Tracks form changes and warns users before leaving the page if they have unsaved modifications. Uses the browser's `beforeunload` event for protection.

## Controller Code

```javascript
// app/javascript/controllers/dirty_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { message: { type: String, default: "You have unsaved changes. Leave anyway?" } }

  connect() {
    this.originalData = new FormData(this.element)
    this.dirty = false
    window.addEventListener("beforeunload", this.handleBeforeUnload.bind(this))
  }

  disconnect() {
    window.removeEventListener("beforeunload", this.handleBeforeUnload.bind(this))
  }

  markDirty() {
    this.dirty = this.hasChanges()
  }

  hasChanges() {
    const currentData = new FormData(this.element)
    for (const [key, value] of currentData.entries()) {
      if (this.originalData.get(key) !== value) return true
    }
    return false
  }

  handleBeforeUnload(event) {
    if (this.dirty) {
      event.preventDefault()
      event.returnValue = this.messageValue
      return this.messageValue
    }
  }

  submit() {
    this.dirty = false
  }
}
```

## ERB Usage

```erb
<%= form_with model: @post,
    data: {
      controller: "dirty",
      dirty_message_value: "You have unsaved changes!",
      action: "input->dirty#markDirty submit->dirty#submit"
    } do |f| %>
  <%= f.text_field :title %>
  <%= f.text_area :body %>
  <%= f.submit %>
<% end %>
```

## Features

- **Change detection**: Compares current form state to original
- **Browser protection**: Uses `beforeunload` event to warn users
- **Submit bypass**: Automatically clears dirty flag on successful submit
- **Custom message**: Configurable warning message
- **Automatic cleanup**: Removes event listeners on disconnect

## How It Works

1. **On connect**: Captures initial form state as FormData
2. **On input**: Compares current state to original, sets dirty flag
3. **On beforeunload**: Shows browser warning if dirty flag is true
4. **On submit**: Clears dirty flag to allow navigation
5. **On disconnect**: Removes event listeners

## Advanced Version with Turbo

```javascript
// app/javascript/controllers/dirty_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { message: { type: String, default: "You have unsaved changes. Leave anyway?" } }

  connect() {
    this.originalData = new FormData(this.element)
    this.dirty = false
    this.boundBeforeUnload = this.handleBeforeUnload.bind(this)
    this.boundTurboBeforeVisit = this.handleTurboBeforeVisit.bind(this)

    window.addEventListener("beforeunload", this.boundBeforeUnload)
    document.addEventListener("turbo:before-visit", this.boundTurboBeforeVisit)
  }

  disconnect() {
    window.removeEventListener("beforeunload", this.boundBeforeUnload)
    document.removeEventListener("turbo:before-visit", this.boundTurboBeforeVisit)
  }

  markDirty() {
    this.dirty = this.hasChanges()
  }

  hasChanges() {
    const currentData = new FormData(this.element)
    for (const [key, value] of currentData.entries()) {
      if (this.originalData.get(key) !== value) return true
    }
    return false
  }

  handleBeforeUnload(event) {
    if (this.dirty) {
      event.preventDefault()
      event.returnValue = this.messageValue
      return this.messageValue
    }
  }

  handleTurboBeforeVisit(event) {
    if (this.dirty && !confirm(this.messageValue)) {
      event.preventDefault()
    }
  }

  submit() {
    this.dirty = false
  }

  reset() {
    this.originalData = new FormData(this.element)
    this.dirty = false
  }
}
```

## With Visual Indicator

```javascript
markDirty() {
  this.dirty = this.hasChanges()
  this.updateIndicator()
}

updateIndicator() {
  const indicator = this.element.querySelector("[data-dirty-indicator]")
  if (indicator) {
    indicator.classList.toggle("visible", this.dirty)
  }
}
```

```erb
<%= form_with model: @post,
    data: {
      controller: "dirty",
      action: "input->dirty#markDirty submit->dirty#submit"
    } do |f| %>

  <div class="flex justify-between items-center mb-4">
    <h1>Edit Post</h1>
    <span data-dirty-indicator class="hidden text-orange-600 text-sm">
      Unsaved changes
    </span>
  </div>

  <%= f.text_field :title %>
  <%= f.text_area :body %>
  <%= f.submit %>
<% end %>

<style>
  [data-dirty-indicator].visible {
    display: inline-block;
  }
</style>
```

## With Autosave Integration

```erb
<%= form_with model: @draft,
    data: {
      controller: "dirty autosave",
      dirty_message_value: "You have unsaved changes!",
      autosave_url_value: autosave_draft_path(@draft),
      action: "input->dirty#markDirty input->autosave#save submit->dirty#submit"
    } do |f| %>

  <%= f.text_field :title %>
  <%= f.text_area :body %>
  <span data-autosave-target="status"></span>

  <%= f.submit "Publish" %>
<% end %>
```

## Browser Behavior Notes

- Modern browsers show a generic message, not your custom text
- The `beforeunload` event only prevents closing/refreshing, not all navigation
- Turbo navigation needs separate handling via `turbo:before-visit`
- Some browsers may not show the dialog on mobile

## Related Skills

- [SKILL.md](./SKILL.md): All form Stimulus patterns
- [autosave.md](./autosave.md): Auto-saving functionality
- [validation.md](./validation.md): Client-side validation
