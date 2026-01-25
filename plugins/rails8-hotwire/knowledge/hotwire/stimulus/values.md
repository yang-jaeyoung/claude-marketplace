# Stimulus Values

## Overview

Values let you read and write data attributes on your controller's element, with automatic type casting and change callbacks. They're the primary way to pass configuration from HTML to JavaScript.

## Defining Values

```javascript
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = {
    url: String,
    count: Number,
    enabled: Boolean,
    items: Array,
    config: Object
  }
}
```

## Supported Types

| Type | HTML Value | JavaScript Value |
|------|------------|------------------|
| `String` | `"hello"` | `"hello"` |
| `Number` | `"42"` | `42` |
| `Boolean` | `"true"` / `"false"` | `true` / `false` |
| `Array` | `"[1, 2, 3]"` | `[1, 2, 3]` |
| `Object` | `'{"key": "value"}'` | `{ key: "value" }` |

## HTML Syntax

```erb
<div data-controller="slideshow"
     data-slideshow-url-value="/api/slides"
     data-slideshow-count-value="5"
     data-slideshow-enabled-value="true"
     data-slideshow-items-value='["a", "b", "c"]'
     data-slideshow-config-value='{"autoplay": true, "delay": 3000}'>
</div>
```

## Value Properties

For each value, Stimulus creates a property:

```javascript
export default class extends Controller {
  static values = { count: Number }

  connect() {
    // Read value
    console.log(this.countValue) // 5

    // Write value (updates data attribute too)
    this.countValue = 10
  }
}
```

## Default Values

```javascript
export default class extends Controller {
  static values = {
    // Long form with defaults
    interval: { type: Number, default: 1000 },
    enabled: { type: Boolean, default: true },
    items: { type: Array, default: [] },
    config: { type: Object, default: { theme: "light" } }
  }
}
```

## has[Name]Value

Check if a value has been set:

```javascript
export default class extends Controller {
  static values = {
    url: String,
    timeout: { type: Number, default: 5000 }
  }

  connect() {
    // Check if value exists (not just default)
    if (this.hasUrlValue) {
      this.load()
    }
  }
}
```

## Value Changed Callbacks

```javascript
export default class extends Controller {
  static values = {
    count: { type: Number, default: 0 },
    loading: Boolean
  }

  // Called whenever count changes
  countValueChanged(value, previousValue) {
    console.log(`Count changed: ${previousValue} -> ${value}`)
    this.updateDisplay()
  }

  // Called whenever loading changes
  loadingValueChanged(isLoading) {
    this.element.classList.toggle("loading", isLoading)
  }

  updateDisplay() {
    // Update UI
  }
}
```

### Callback Parameters

| Parameter | Description |
|-----------|-------------|
| `value` | New value |
| `previousValue` | Previous value (undefined on first call) |

## Reactive UI Pattern

```javascript
export default class extends Controller {
  static targets = ["output"]
  static values = { count: { type: Number, default: 0 } }

  increment() {
    this.countValue++
  }

  decrement() {
    this.countValue--
  }

  // Automatically updates UI when value changes
  countValueChanged() {
    this.outputTarget.textContent = this.countValue
  }
}
```

```erb
<div data-controller="counter" data-counter-count-value="0">
  <button data-action="counter#decrement">-</button>
  <span data-counter-target="output">0</span>
  <button data-action="counter#increment">+</button>
</div>
```

## Complex Values

### Arrays

```erb
<div data-controller="tags"
     data-tags-selected-value='["ruby", "rails"]'>
</div>
```

```javascript
export default class extends Controller {
  static values = { selected: Array }

  add(tag) {
    this.selectedValue = [...this.selectedValue, tag]
  }

  remove(tag) {
    this.selectedValue = this.selectedValue.filter(t => t !== tag)
  }

  selectedValueChanged() {
    this.render()
  }
}
```

### Objects

```erb
<div data-controller="chart"
     data-chart-options-value='{"type": "line", "animate": true}'>
</div>
```

```javascript
export default class extends Controller {
  static values = {
    options: { type: Object, default: { type: "bar", animate: false } }
  }

  connect() {
    this.initChart(this.optionsValue)
  }
}
```

## Rails Helpers

```erb
<%# Pass Ruby objects as JSON %>
<div data-controller="user"
     data-user-data-value="<%= { name: @user.name, id: @user.id }.to_json %>">
</div>

<%# Using content_tag %>
<%= content_tag :div,
      data: {
        controller: "chart",
        chart_data_value: @chart_data.to_json,
        chart_options_value: { type: "line" }.to_json
      } do %>
  <canvas></canvas>
<% end %>

<%# Using tag helper %>
<%= tag.div data: {
      controller: "map",
      map_coordinates_value: [@lat, @lng].to_json
    } %>
```

## Common Patterns

### Configuration Object

```javascript
export default class extends Controller {
  static values = {
    config: {
      type: Object,
      default: {
        animation: true,
        duration: 300,
        easing: "ease-in-out"
      }
    }
  }

  animate() {
    if (this.configValue.animation) {
      this.element.style.transition =
        `all ${this.configValue.duration}ms ${this.configValue.easing}`
    }
  }
}
```

### State Machine

```javascript
export default class extends Controller {
  static values = {
    state: { type: String, default: "idle" }
  }

  static states = ["idle", "loading", "success", "error"]

  async submit() {
    this.stateValue = "loading"

    try {
      await this.sendRequest()
      this.stateValue = "success"
    } catch {
      this.stateValue = "error"
    }
  }

  stateValueChanged(state) {
    // Remove all state classes
    this.constructor.states.forEach(s =>
      this.element.classList.remove(`state-${s}`)
    )
    // Add current state class
    this.element.classList.add(`state-${state}`)
  }
}
```

### Polling with Configurable Interval

```javascript
export default class extends Controller {
  static values = {
    url: String,
    interval: { type: Number, default: 5000 }
  }

  connect() {
    this.poll()
  }

  disconnect() {
    this.stopPolling()
  }

  poll() {
    this.timer = setInterval(() => this.refresh(), this.intervalValue)
  }

  stopPolling() {
    clearInterval(this.timer)
  }

  // Changing interval restarts polling
  intervalValueChanged() {
    this.stopPolling()
    this.poll()
  }

  async refresh() {
    const response = await fetch(this.urlValue)
    const html = await response.text()
    // Use safe DOM update methods - avoid direct innerHTML assignment
    this.updateContent(html)
  }

  updateContent(html) {
    // For trusted HTML from your own server, parse and replace safely
    const template = document.createElement("template")
    template.innerHTML = html
    this.element.replaceChildren(template.content)
  }
}
```

## Bidirectional Sync

Values sync bidirectionally between HTML and JavaScript:

```javascript
export default class extends Controller {
  static values = { count: Number }

  increment() {
    this.countValue++ // Updates data-*-count-value attribute
  }
}
```

External changes to the attribute also trigger callbacks:

```javascript
// External JavaScript
element.dataset.counterCountValue = "100"
// Triggers countValueChanged callback
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Value is string | Wrong type declaration | Check `static values` type |
| Callback fires twice | Setting value in callback | Use guard condition |
| Array/Object not updating | Mutating instead of replacing | Create new array/object |
| JSON parse error | Invalid JSON syntax | Validate JSON, use single quotes |

## Related

- [conventions.md](./conventions.md): Naming conventions
- [lifecycle.md](./lifecycle.md): Lifecycle callbacks
- [targets.md](./targets.md): Target system
- [actions.md](./actions.md): Action system
