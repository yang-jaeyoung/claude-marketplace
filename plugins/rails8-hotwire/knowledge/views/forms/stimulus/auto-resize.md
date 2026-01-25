---
name: rails8-stimulus-auto-resize
description: Auto-expanding textarea based on content
---

# Auto-Resize Textarea

## Overview

Automatically expands a textarea as content grows, with configurable min/max heights and overflow handling.

## Controller Code

```javascript
// app/javascript/controllers/auto_resize_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = {
    minHeight: { type: Number, default: 100 },
    maxHeight: { type: Number, default: 500 }
  }

  connect() {
    this.resize()
  }

  resize() {
    const textarea = this.element

    // Reset height to auto to get accurate scrollHeight
    textarea.style.height = "auto"

    // Calculate new height
    let newHeight = textarea.scrollHeight

    // Apply constraints
    newHeight = Math.max(newHeight, this.minHeightValue)
    newHeight = Math.min(newHeight, this.maxHeightValue)

    textarea.style.height = `${newHeight}px`

    // Add scrollbar if at max height
    textarea.style.overflowY = newHeight >= this.maxHeightValue ? "auto" : "hidden"
  }
}
```

## ERB Usage

```erb
<%= f.text_area :body,
    data: {
      controller: "auto-resize",
      auto_resize_min_height_value: 100,
      auto_resize_max_height_value: 400,
      action: "input->auto-resize#resize"
    },
    class: "w-full resize-none" %>
```

## Features

- **Dynamic height**: Grows with content
- **Min/max constraints**: Prevents too small or too large
- **Overflow handling**: Adds scrollbar when max height reached
- **Initial sizing**: Resizes on page load to fit existing content
- **Disabled manual resize**: Uses `resize-none` class

## Configuration Options

| Value | Default | Purpose |
|-------|---------|---------|
| `minHeight` | 100 | Minimum height in pixels |
| `maxHeight` | 500 | Maximum height in pixels |

## Usage Examples

### Basic Auto-Resize

```erb
<%= f.text_area :comment,
    data: {
      controller: "auto-resize",
      action: "input->auto-resize#resize"
    },
    class: "resize-none" %>
```

### Custom Height Constraints

```erb
<!-- Small textarea (50-200px) -->
<%= f.text_area :short_note,
    data: {
      controller: "auto-resize",
      auto_resize_min_height_value: 50,
      auto_resize_max_height_value: 200,
      action: "input->auto-resize#resize"
    },
    class: "resize-none" %>

<!-- Large textarea (150-800px) -->
<%= f.text_area :long_description,
    data: {
      controller: "auto-resize",
      auto_resize_min_height_value: 150,
      auto_resize_max_height_value: 800,
      action: "input->auto-resize#resize"
    },
    class: "resize-none" %>
```

### With Character Counter

```erb
<div data-controller="character-count auto-resize"
     data-character-count-max-value="500">
  <%= f.text_area :body,
      data: {
        character_count_target: "input",
        auto_resize_min_height_value: 100,
        auto_resize_max_height_value: 300,
        action: "input->character-count#update input->auto-resize#resize"
      },
      class: "resize-none" %>
  <span data-character-count-target="count">0</span>/500
</div>
```

## Styling

```css
/* Disable manual resizing */
.resize-none {
  resize: none;
}

/* Optional: smooth transitions */
textarea[data-controller~="auto-resize"] {
  transition: height 0.1s ease;
}
```

## How It Works

1. **Initial connect**: Resizes on mount to fit existing content
2. **On input**: Temporarily sets height to `auto` to measure content
3. **Calculate**: Gets actual scroll height needed
4. **Apply constraints**: Clamps between min and max
5. **Set height**: Applies calculated height
6. **Overflow**: Shows scrollbar only if at max height

## Related Skills

- [SKILL.md](./SKILL.md): All form Stimulus patterns
- [character-counter.md](./character-counter.md): Character counting
- [validation.md](./validation.md): Client-side validation
