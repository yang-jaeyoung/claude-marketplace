# Stimulus Actions

## Overview

Actions connect DOM events to controller methods. They're defined in HTML using `data-action` attributes, providing a declarative way to handle user interactions.

## Basic Syntax

```erb
<button data-action="click->controller#method">Click me</button>
```

Format: `[event]->[controller]#[method]`

## Event Shorthand

Common elements have default events:

| Element | Default Event |
|---------|---------------|
| `<button>` | click |
| `<input type="submit">` | click |
| `<input>` | input |
| `<textarea>` | input |
| `<select>` | change |
| `<form>` | submit |
| `<a>` | click |
| `<details>` | toggle |

```erb
<!-- These are equivalent -->
<button data-action="click->dropdown#toggle">
<button data-action="dropdown#toggle">

<input data-action="input->search#perform">
<input data-action="search#perform">

<form data-action="submit->form#save">
<form data-action="form#save">
```

## Multiple Actions

```erb
<!-- Multiple actions on same element -->
<input data-action="focus->form#expand blur->form#collapse input->form#validate">

<!-- Same event, multiple handlers -->
<button data-action="click->analytics#track click->modal#open">
```

## Event Object

```javascript
export default class extends Controller {
  submit(event) {
    // Standard event object
    event.preventDefault()
    event.stopPropagation()

    // Event target
    console.log(event.target)
    console.log(event.currentTarget)

    // Custom event detail
    console.log(event.detail)
  }
}
```

## Action Parameters

Pass data from HTML to action methods:

```erb
<button data-action="item#delete"
        data-item-id-param="123"
        data-item-name-param="Test">
  Delete
</button>
```

```javascript
export default class extends Controller {
  delete({ params }) {
    // params is an object of all *-param values
    console.log(params.id)   // "123" (always string)
    console.log(params.name) // "Test"

    if (confirm(`Delete ${params.name}?`)) {
      this.removeItem(params.id)
    }
  }
}
```

### Type Conversion

```erb
<button data-action="counter#increment"
        data-counter-amount-param="5">
  +5
</button>
```

```javascript
export default class extends Controller {
  increment({ params: { amount } }) {
    // Convert to number
    this.count += Number(amount)
  }
}
```

## Global Events

### Window Events

```erb
<div data-controller="sidebar"
     data-action="resize@window->sidebar#adjust">
</div>
```

### Document Events

```erb
<div data-controller="modal"
     data-action="keydown@document->modal#handleKey">
</div>
```

### Body Events

```erb
<div data-controller="dropdown"
     data-action="click@body->dropdown#closeIfOutside">
</div>
```

## Keyboard Events

### Key Filters

```erb
<!-- Specific keys -->
<input data-action="keydown.enter->search#submit">
<input data-action="keydown.escape->search#clear">
<input data-action="keydown.tab->form#nextField">

<!-- Arrow keys -->
<div data-action="keydown.up->list#previous keydown.down->list#next">

<!-- Modifier keys -->
<input data-action="keydown.ctrl+s->form#save">
<input data-action="keydown.meta+enter->form#submit">
```

### Available Key Filters

| Filter | Keys |
|--------|------|
| `enter` | Enter/Return |
| `tab` | Tab |
| `esc` / `escape` | Escape |
| `space` | Space |
| `up` | Arrow Up |
| `down` | Arrow Down |
| `left` | Arrow Left |
| `right` | Arrow Right |
| `home` | Home |
| `end` | End |
| `page_up` | Page Up |
| `page_down` | Page Down |
| `a`-`z` | Letters |
| `0`-`9` | Numbers |

### Modifier Keys

| Modifier | Mac | Windows/Linux |
|----------|-----|---------------|
| `ctrl` | Control | Ctrl |
| `meta` | Command | Windows |
| `alt` | Option | Alt |
| `shift` | Shift | Shift |

```erb
<!-- Command/Ctrl + S to save -->
<form data-action="keydown.meta+s->form#save keydown.ctrl+s->form#save">
```

## Event Options

### Stop Propagation

```erb
<button data-action="click->modal#close:stop">
  Close (stops propagation)
</button>
```

### Prevent Default

```erb
<a href="#" data-action="click->tabs#select:prevent">
  Tab (prevents navigation)
</a>

<form data-action="submit->form#save:prevent">
  <!-- Prevents default form submission -->
</form>
```

### Combined Options

```erb
<a data-action="click->modal#open:prevent:stop">
  Open Modal
</a>
```

### Self Option

Only trigger if target is the element itself (not children):

```erb
<div data-action="click->modal#close:self">
  <!-- Only closes if clicking the div, not its children -->
  <div class="modal-content">
    Clicking here won't close
  </div>
</div>
```

### Passive Option

```erb
<div data-action="scroll->infinite#loadMore:passive">
  <!-- Passive event listener for better scroll performance -->
</div>
```

### Once Option

```erb
<button data-action="click->welcome#greet:once">
  <!-- Only triggers once -->
</button>
```

## Custom Events

### Dispatching Events

```javascript
export default class extends Controller {
  select() {
    // Dispatch custom event
    this.dispatch("selected", {
      detail: { id: this.idValue, name: this.nameValue },
      bubbles: true
    })
  }
}
```

### Listening to Custom Events

```erb
<div data-controller="parent"
     data-action="child:selected->parent#handleSelection">

  <div data-controller="child">
    <button data-action="child#select">Select</button>
  </div>
</div>
```

```javascript
// parent_controller.js
export default class extends Controller {
  handleSelection(event) {
    const { id, name } = event.detail
    console.log(`Selected: ${name} (${id})`)
  }
}
```

## Turbo Events

```erb
<div data-controller="form"
     data-action="turbo:submit-start->form#disable
                  turbo:submit-end->form#enable">
  <form>...</form>
</div>
```

Common Turbo events:
- `turbo:submit-start`
- `turbo:submit-end`
- `turbo:before-fetch-request`
- `turbo:before-fetch-response`
- `turbo:frame-load`

## Common Patterns

### Form Validation

```erb
<form data-controller="form"
      data-action="submit->form#validate">
  <input data-action="blur->form#validateField"
         data-form-target="email"
         type="email">
  <button>Submit</button>
</form>
```

### Debounced Search

```javascript
export default class extends Controller {
  static targets = ["input"]

  search() {
    clearTimeout(this.timeout)
    this.timeout = setTimeout(() => {
      this.performSearch()
    }, 300)
  }

  performSearch() {
    // Search logic
  }
}
```

```erb
<input data-controller="search"
       data-action="input->search#search">
```

### Click Outside

```javascript
export default class extends Controller {
  connect() {
    this.clickOutsideHandler = this.clickOutside.bind(this)
    document.addEventListener("click", this.clickOutsideHandler)
  }

  disconnect() {
    document.removeEventListener("click", this.clickOutsideHandler)
  }

  clickOutside(event) {
    if (!this.element.contains(event.target)) {
      this.close()
    }
  }
}
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Action not firing | Typo in controller/method name | Check naming conventions |
| Event fires on children | Need self option | Add `:self` modifier |
| Keyboard shortcut not working | Wrong key name | Check key filter names |
| Multiple fires | Event bubbling | Add `:stop` modifier |

## Related

- [conventions.md](./conventions.md): Naming conventions
- [lifecycle.md](./lifecycle.md): Lifecycle callbacks
- [targets.md](./targets.md): Target system
- [values.md](./values.md): Value system
