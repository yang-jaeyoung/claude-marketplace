---
name: rails8-stimulus-character-counter
description: Character counter with warnings for form inputs
---

# Character Counter

## Overview

Displays character count and remaining characters for text fields and textareas, with visual warnings as limits approach.

## Controller Code

```javascript
// app/javascript/controllers/character_count_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "count", "remaining"]
  static values = { max: { type: Number, default: 280 } }
  static classes = ["warning", "danger"]

  connect() {
    this.update()
  }

  update() {
    const length = this.inputTarget.value.length
    const remaining = this.maxValue - length

    if (this.hasCountTarget) {
      this.countTarget.textContent = length
    }

    if (this.hasRemainingTarget) {
      this.remainingTarget.textContent = remaining
    }

    // Update classes based on remaining
    this.element.classList.remove(this.warningClass, this.dangerClass)

    if (remaining < 0) {
      this.element.classList.add(this.dangerClass)
    } else if (remaining < 20) {
      this.element.classList.add(this.warningClass)
    }
  }
}
```

## ERB Usage

```erb
<div data-controller="character-count"
     data-character-count-max-value="280"
     data-character-count-warning-class="text-yellow-600"
     data-character-count-danger-class="text-red-600">
  <%= f.text_area :body,
      data: {
        character_count_target: "input",
        action: "input->character-count#update"
      } %>
  <p class="text-sm text-gray-500 mt-1">
    <span data-character-count-target="count">0</span>/<span data-character-count-target="remaining">280</span> characters
  </p>
</div>
```

## Features

- **Real-time counting**: Updates on every keystroke
- **Visual warnings**: Yellow warning at 20 chars remaining, red when over limit
- **Configurable limits**: Set max via data attribute
- **Flexible display**: Show count, remaining, or both

## Customization

```erb
<!-- Show only count -->
<div data-controller="character-count" data-character-count-max-value="100">
  <%= f.text_field :title, data: { character_count_target: "input", action: "input->character-count#update" } %>
  <span data-character-count-target="count">0</span>/100
</div>

<!-- Custom warning thresholds -->
<div data-controller="character-count"
     data-character-count-max-value="500"
     data-character-count-warning-class="bg-orange-100"
     data-character-count-danger-class="bg-red-100">
  <%= f.text_area :description, data: { character_count_target: "input", action: "input->character-count#update" } %>
  <span data-character-count-target="remaining">500</span> remaining
</div>
```

## Related Skills

- [SKILL.md](./SKILL.md): All form Stimulus patterns
- [validation.md](./validation.md): Client-side validation
- [auto-resize.md](./auto-resize.md): Auto-expanding textareas
