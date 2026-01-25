---
name: rails8-stimulus-validation
description: Client-side form validation with HTML5 validation API
---

# Form Validation

## Overview

Client-side form validation using the HTML5 Constraint Validation API with custom error messages and real-time feedback.

## Controller Code

```javascript
// app/javascript/controllers/validate_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["field", "error", "submit"]
  static classes = ["invalid"]

  connect() {
    this.validateAll()
  }

  validate(event) {
    const field = event.target
    this.validateField(field)
    this.updateSubmitButton()
  }

  validateField(field) {
    const errorElement = this.element.querySelector(`[data-error-for="${field.name}"]`)

    if (field.validity.valid) {
      field.classList.remove(this.invalidClass)
      if (errorElement) errorElement.textContent = ""
      return true
    } else {
      field.classList.add(this.invalidClass)
      if (errorElement) errorElement.textContent = this.errorMessage(field)
      return false
    }
  }

  validateAll() {
    let valid = true
    this.fieldTargets.forEach(field => {
      if (!this.validateField(field)) valid = false
    })
    return valid
  }

  updateSubmitButton() {
    if (this.hasSubmitTarget) {
      this.submitTarget.disabled = !this.validateAll()
    }
  }

  submit(event) {
    if (!this.validateAll()) {
      event.preventDefault()
      this.fieldTargets.find(f => !f.validity.valid)?.focus()
    }
  }

  errorMessage(field) {
    if (field.validity.valueMissing) return "This field is required"
    if (field.validity.typeMismatch) return `Please enter a valid ${field.type}`
    if (field.validity.tooShort) return `Minimum ${field.minLength} characters`
    if (field.validity.tooLong) return `Maximum ${field.maxLength} characters`
    if (field.validity.patternMismatch) return field.dataset.patternError || "Invalid format"
    return field.validationMessage
  }
}
```

## ERB Usage

```erb
<%= form_with model: @user,
    data: {
      controller: "validate",
      validate_invalid_class: "border-red-500",
      action: "submit->validate#submit"
    } do |f| %>

  <div class="mb-4">
    <%= f.label :email %>
    <%= f.email_field :email,
        required: true,
        data: {
          validate_target: "field",
          action: "blur->validate#validate input->validate#validate"
        } %>
    <p data-error-for="user[email]" class="text-red-600 text-sm mt-1"></p>
  </div>

  <div class="mb-4">
    <%= f.label :password %>
    <%= f.password_field :password,
        required: true,
        minlength: 8,
        data: {
          validate_target: "field",
          action: "blur->validate#validate"
        } %>
    <p data-error-for="user[password]" class="text-red-600 text-sm mt-1"></p>
  </div>

  <%= f.submit "Sign Up", data: { validate_target: "submit" } %>
<% end %>
```

## Features

- **HTML5 validation**: Uses built-in browser validation
- **Custom error messages**: Human-friendly messages for all validation states
- **Real-time feedback**: Validates on blur and input events
- **Submit prevention**: Disables submit and prevents submission when invalid
- **Pattern validation**: Support for regex patterns with custom messages

## Pattern Validation Example

```erb
<%= f.text_field :phone,
    pattern: "\\d{3}-\\d{3}-\\d{4}",
    data: {
      validate_target: "field",
      action: "blur->validate#validate",
      pattern_error: "Phone must be in format: 123-456-7890"
    } %>
<p data-error-for="user[phone]" class="text-red-600 text-sm mt-1"></p>
```

## Validation States

| Validity Property | Meaning | Message |
|-------------------|---------|---------|
| `valueMissing` | Required field is empty | "This field is required" |
| `typeMismatch` | Type doesn't match (email, url, etc.) | "Please enter a valid {type}" |
| `tooShort` | Below minlength | "Minimum {n} characters" |
| `tooLong` | Above maxlength | "Maximum {n} characters" |
| `patternMismatch` | Doesn't match pattern | Custom or "Invalid format" |

## Related Skills

- [SKILL.md](./SKILL.md): All form Stimulus patterns
- [password-strength.md](./password-strength.md): Password strength checking
- [character-counter.md](./character-counter.md): Character counting
