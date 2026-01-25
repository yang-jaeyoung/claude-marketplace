# Stimulus Targets

## Overview

Targets are Stimulus's way of referencing important elements within a controller's scope. They provide a clean alternative to manual DOM queries.

## Defining Targets

```javascript
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "output", "submitButton"]

  greet() {
    this.outputTarget.textContent = `Hello, ${this.inputTarget.value}!`
  }
}
```

## Target Properties

For each target name, Stimulus creates three properties:

| Property | Type | Description |
|----------|------|-------------|
| `this.[name]Target` | Element | First matching element (throws if missing) |
| `this.[name]Targets` | Element[] | All matching elements |
| `this.has[Name]Target` | Boolean | Whether target exists |

```javascript
export default class extends Controller {
  static targets = ["item"]

  connect() {
    // Single target (throws if not found)
    console.log(this.itemTarget)

    // All targets (empty array if none)
    console.log(this.itemTargets)

    // Check existence
    if (this.hasItemTarget) {
      this.itemTarget.focus()
    }
  }
}
```

## HTML Syntax

```erb
<div data-controller="search">
  <!-- Target syntax: data-[controller]-target="[name]" -->
  <input data-search-target="input" type="text">
  <button data-search-target="submitButton">Search</button>
  <div data-search-target="results"></div>
</div>
```

## Multiple Targets

```erb
<ul data-controller="list">
  <li data-list-target="item">Item 1</li>
  <li data-list-target="item">Item 2</li>
  <li data-list-target="item">Item 3</li>
</ul>
```

```javascript
export default class extends Controller {
  static targets = ["item"]

  removeAll() {
    this.itemTargets.forEach(item => item.remove())
  }

  count() {
    return this.itemTargets.length
  }
}
```

## Multiple Target Types on Same Element

```erb
<input data-controller="form"
       data-form-target="input email">
```

```javascript
export default class extends Controller {
  static targets = ["input", "email"]

  validate() {
    // Both targets point to the same element
    console.log(this.inputTarget === this.emailTarget) // true
  }
}
```

## Target Callbacks

### Connected Callback

```javascript
export default class extends Controller {
  static targets = ["item"]

  // Called when a target element is added to DOM
  itemTargetConnected(element) {
    console.log("New item added:", element)
    this.updateCount()
  }
}
```

### Disconnected Callback

```javascript
export default class extends Controller {
  static targets = ["item"]

  // Called when a target element is removed from DOM
  itemTargetDisconnected(element) {
    console.log("Item removed:", element)
    this.updateCount()
  }
}
```

## Dynamic Targets

Targets work automatically with dynamically added content:

```erb
<div data-controller="todos">
  <ul id="todo-list">
    <!-- Turbo Stream appends here -->
  </ul>
</div>
```

```javascript
export default class extends Controller {
  static targets = ["item"]

  // Automatically called when Turbo adds new items
  itemTargetConnected(element) {
    element.classList.add("animate-fade-in")
  }
}
```

## Scoped Queries

Targets are scoped to the controller element:

```erb
<div data-controller="outer">
  <div data-outer-target="box">Outer box</div>

  <div data-controller="inner">
    <div data-inner-target="box">Inner box</div>
  </div>
</div>
```

Each controller only sees its own targets.

## Optional Targets

```javascript
export default class extends Controller {
  static targets = ["optional"]

  connect() {
    // Safe way to handle optional targets
    if (this.hasOptionalTarget) {
      this.optionalTarget.textContent = "Found!"
    }

    // Or use optional chaining
    this.optionalTarget?.focus()
  }
}
```

## Target vs Query

```javascript
// Using targets (preferred)
export default class extends Controller {
  static targets = ["input"]

  clear() {
    this.inputTarget.value = ""
  }
}

// Using querySelector (avoid when possible)
export default class extends Controller {
  clear() {
    this.element.querySelector("input").value = ""
  }
}
```

| Approach | Pros | Cons |
|----------|------|------|
| Targets | Declarative, clear intent, callbacks | Requires data attribute |
| querySelector | No setup needed | Brittle, no callbacks |

## Common Patterns

### Form with Multiple Inputs

```erb
<form data-controller="form">
  <input data-form-target="name" name="name">
  <input data-form-target="email" name="email">
  <textarea data-form-target="message" name="message"></textarea>
  <button data-form-target="submit">Send</button>
</form>
```

```javascript
export default class extends Controller {
  static targets = ["name", "email", "message", "submit"]

  validate() {
    const isValid = this.nameTarget.value &&
                    this.emailTarget.value &&
                    this.messageTarget.value

    this.submitTarget.disabled = !isValid
  }
}
```

### Tabs

```erb
<div data-controller="tabs">
  <button data-tabs-target="tab" data-action="tabs#select">Tab 1</button>
  <button data-tabs-target="tab" data-action="tabs#select">Tab 2</button>

  <div data-tabs-target="panel">Panel 1</div>
  <div data-tabs-target="panel" hidden>Panel 2</div>
</div>
```

```javascript
export default class extends Controller {
  static targets = ["tab", "panel"]

  select(event) {
    const index = this.tabTargets.indexOf(event.currentTarget)

    this.tabTargets.forEach((tab, i) => {
      tab.classList.toggle("active", i === index)
    })

    this.panelTargets.forEach((panel, i) => {
      panel.hidden = i !== index
    })
  }
}
```

### Nested Targets

```erb
<div data-controller="accordion">
  <div data-accordion-target="section">
    <button data-accordion-target="header" data-action="accordion#toggle">
      Section 1
    </button>
    <div data-accordion-target="content">Content 1</div>
  </div>
  <div data-accordion-target="section">
    <button data-accordion-target="header" data-action="accordion#toggle">
      Section 2
    </button>
    <div data-accordion-target="content" hidden>Content 2</div>
  </div>
</div>
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Target not found | Typo in target name | Check spelling matches |
| Wrong target selected | Nested controllers | Check scope |
| Target undefined | Accessed before connect | Use `has[Name]Target` check |
| Callbacks not firing | Not using static targets | Declare in `static targets` |

## Related

- [conventions.md](./conventions.md): Naming conventions
- [lifecycle.md](./lifecycle.md): Lifecycle callbacks
- [values.md](./values.md): Value system
- [actions.md](./actions.md): Action system
