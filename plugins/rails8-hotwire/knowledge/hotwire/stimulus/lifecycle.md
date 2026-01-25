# Stimulus Lifecycle

## Overview

Stimulus controllers have lifecycle callbacks that fire when controllers connect to and disconnect from the DOM. Understanding the lifecycle is crucial for proper resource management.

## Lifecycle Callbacks

| Callback | When Called |
|----------|-------------|
| `initialize()` | Once, when controller is first instantiated |
| `connect()` | Each time controller connects to DOM |
| `disconnect()` | Each time controller disconnects from DOM |

## Basic Lifecycle

```javascript
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  initialize() {
    // Called once when controller is first instantiated
    // Good for: one-time setup, initializing instance properties
    console.log("Controller initialized")
    this.clickCount = 0
  }

  connect() {
    // Called each time element appears in DOM
    // Good for: DOM setup, event listeners, starting timers
    console.log("Controller connected to DOM")
    this.startPolling()
  }

  disconnect() {
    // Called each time element is removed from DOM
    // Good for: cleanup, removing listeners, stopping timers
    console.log("Controller disconnected from DOM")
    this.stopPolling()
  }

  startPolling() {
    this.pollInterval = setInterval(() => {
      this.refresh()
    }, 5000)
  }

  stopPolling() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval)
    }
  }
}
```

## Lifecycle Flow

```
┌─────────────────────────────────────────────────────┐
│                   Page Load                          │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │    initialize()     │ ← Once per controller instance
              └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │     connect()       │ ← Element in DOM
              └─────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     ┌─────────────────┐   ┌─────────────────┐
     │  User Actions   │   │  Turbo Updates  │
     └─────────────────┘   └─────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   disconnect()      │ ← Element removed
              └─────────────────────┘
                         │
                         ▼ (if element re-added)
              ┌─────────────────────┐
              │     connect()       │ ← Re-connection
              └─────────────────────┘
```

## Target Callbacks

```javascript
export default class extends Controller {
  static targets = ["item", "output"]

  // Called when target is added to DOM
  itemTargetConnected(element) {
    console.log("Item added:", element)
    this.updateCount()
  }

  // Called when target is removed from DOM
  itemTargetDisconnected(element) {
    console.log("Item removed:", element)
    this.updateCount()
  }

  updateCount() {
    this.outputTarget.textContent = `${this.itemTargets.length} items`
  }
}
```

```erb
<div data-controller="list">
  <span data-list-target="output">0 items</span>
  <div id="items">
    <!-- Items added/removed trigger callbacks -->
  </div>
</div>
```

## Value Changed Callbacks

```javascript
export default class extends Controller {
  static values = {
    count: { type: Number, default: 0 },
    loading: { type: Boolean, default: false }
  }

  // Called when value changes
  countValueChanged(value, previousValue) {
    console.log(`Count changed from ${previousValue} to ${value}`)
    this.updateDisplay()
  }

  loadingValueChanged(isLoading) {
    this.element.classList.toggle("opacity-50", isLoading)
  }
}
```

## Outlet Callbacks

```javascript
export default class extends Controller {
  static outlets = ["modal"]

  // Called when outlet is connected
  modalOutletConnected(outlet, element) {
    console.log("Modal outlet connected:", outlet)
  }

  // Called when outlet is disconnected
  modalOutletDisconnected(outlet, element) {
    console.log("Modal outlet disconnected:", outlet)
  }
}
```

## Common Patterns

### Event Listener Management

```javascript
export default class extends Controller {
  connect() {
    // Store bound function for later removal
    this.handleResize = this.handleResize.bind(this)
    window.addEventListener("resize", this.handleResize)
  }

  disconnect() {
    window.removeEventListener("resize", this.handleResize)
  }

  handleResize() {
    // Handle window resize
  }
}
```

### AbortController Pattern

```javascript
export default class extends Controller {
  connect() {
    this.abortController = new AbortController()

    window.addEventListener("resize", this.handleResize.bind(this), {
      signal: this.abortController.signal
    })

    document.addEventListener("keydown", this.handleKeydown.bind(this), {
      signal: this.abortController.signal
    })
  }

  disconnect() {
    // Removes all event listeners at once
    this.abortController.abort()
  }
}
```

### Timer Management

```javascript
export default class extends Controller {
  static values = { interval: { type: Number, default: 1000 } }

  connect() {
    this.startTimer()
  }

  disconnect() {
    this.stopTimer()
  }

  startTimer() {
    this.timer = setInterval(() => {
      this.tick()
    }, this.intervalValue)
  }

  stopTimer() {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
    }
  }

  tick() {
    // Timer logic
  }
}
```

### Fetch Cleanup

```javascript
export default class extends Controller {
  connect() {
    this.abortController = new AbortController()
    this.loadData()
  }

  disconnect() {
    this.abortController.abort()
  }

  async loadData() {
    try {
      const response = await fetch(this.urlValue, {
        signal: this.abortController.signal
      })
      const data = await response.json()
      this.render(data)
    } catch (error) {
      if (error.name !== "AbortError") {
        console.error("Fetch error:", error)
      }
    }
  }
}
```

### Third-Party Library Integration

```javascript
import flatpickr from "flatpickr"

export default class extends Controller {
  connect() {
    this.picker = flatpickr(this.element, {
      enableTime: true,
      dateFormat: "Y-m-d H:i"
    })
  }

  disconnect() {
    this.picker.destroy()
  }
}
```

## Turbo Integration

```javascript
export default class extends Controller {
  connect() {
    console.log("Connected - works with Turbo Drive")
    // This runs on initial load AND Turbo navigations
  }

  // Avoid using these with Turbo:
  // - DOMContentLoaded (only fires once)
  // - window.onload (only fires once)
}
```

## Debugging Lifecycle

```javascript
export default class extends Controller {
  initialize() {
    console.log(`[${this.identifier}] initialize`)
  }

  connect() {
    console.log(`[${this.identifier}] connect`, this.element)
  }

  disconnect() {
    console.log(`[${this.identifier}] disconnect`, this.element)
  }
}
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Memory leaks | Not cleaning up in disconnect | Add cleanup in `disconnect()` |
| Event fires multiple times | Multiple connect calls | Track state or use AbortController |
| Controller not connecting | Turbo caching | Check for cached pages |
| State lost on navigation | Using initialize for state | Move to connect with checks |

## Related

- [conventions.md](./conventions.md): Naming conventions
- [targets.md](./targets.md): Target callbacks
- [values.md](./values.md): Value callbacks
