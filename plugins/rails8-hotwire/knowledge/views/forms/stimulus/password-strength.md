---
name: rails8-stimulus-password-strength
description: Visual password strength meter with scoring
---

# Password Strength

## Overview

Displays a visual meter and text feedback showing password strength based on length, character variety, and complexity.

## Controller Code

```javascript
// app/javascript/controllers/password_strength_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "meter", "text"]

  check() {
    const password = this.inputTarget.value
    const strength = this.calculateStrength(password)

    this.meterTarget.value = strength.score
    this.meterTarget.className = `password-meter strength-${strength.level}`
    this.textTarget.textContent = strength.text
    this.textTarget.className = `text-sm strength-${strength.level}`
  }

  calculateStrength(password) {
    let score = 0

    if (password.length >= 8) score++
    if (password.length >= 12) score++
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++
    if (/\d/.test(password)) score++
    if (/[^a-zA-Z0-9]/.test(password)) score++

    const levels = {
      0: { level: "weak", text: "Very weak" },
      1: { level: "weak", text: "Weak" },
      2: { level: "fair", text: "Fair" },
      3: { level: "good", text: "Good" },
      4: { level: "strong", text: "Strong" },
      5: { level: "strong", text: "Very strong" }
    }

    return { score, ...levels[score] }
  }
}
```

## ERB Usage

```erb
<div data-controller="password-strength">
  <%= f.label :password %>
  <%= f.password_field :password,
      minlength: 8,
      data: {
        password_strength_target: "input",
        action: "input->password-strength#check"
      } %>
  <meter data-password-strength-target="meter" max="5" value="0" class="w-full h-2 mt-1"></meter>
  <p data-password-strength-target="text" class="text-sm mt-1"></p>
</div>

<style>
  .strength-weak { color: #ef4444; }
  .strength-fair { color: #f59e0b; }
  .strength-good { color: #10b981; }
  .strength-strong { color: #059669; }
</style>
```

## Features

- **Real-time feedback**: Updates as user types
- **Multi-factor scoring**: Checks length, case, numbers, special chars
- **Visual meter**: HTML5 `<meter>` element with color coding
- **Text labels**: "Weak", "Fair", "Good", "Strong" feedback

## Scoring Criteria

| Criteria | Points |
|----------|--------|
| 8+ characters | +1 |
| 12+ characters | +1 |
| Mixed case (a-z, A-Z) | +1 |
| Contains numbers | +1 |
| Contains special characters | +1 |

## Strength Levels

| Score | Level | Color | Text |
|-------|-------|-------|------|
| 0 | weak | Red | "Very weak" |
| 1 | weak | Red | "Weak" |
| 2 | fair | Orange | "Fair" |
| 3 | good | Green | "Good" |
| 4 | strong | Dark Green | "Strong" |
| 5 | strong | Dark Green | "Very strong" |

## Custom Styling

```css
/* app/assets/stylesheets/password_strength.css */
.password-meter {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.password-meter.strength-weak {
  accent-color: #ef4444;
}

.password-meter.strength-fair {
  accent-color: #f59e0b;
}

.password-meter.strength-good {
  accent-color: #10b981;
}

.password-meter.strength-strong {
  accent-color: #059669;
}

.strength-weak {
  color: #ef4444;
}

.strength-fair {
  color: #f59e0b;
}

.strength-good {
  color: #10b981;
}

.strength-strong {
  color: #059669;
}
```

## Advanced Version with Requirements

```javascript
check() {
  const password = this.inputTarget.value
  const strength = this.calculateStrength(password)

  this.meterTarget.value = strength.score
  this.textTarget.textContent = strength.text

  // Update requirement checkboxes
  this.updateRequirement("length", password.length >= 8)
  this.updateRequirement("uppercase", /[A-Z]/.test(password))
  this.updateRequirement("lowercase", /[a-z]/.test(password))
  this.updateRequirement("number", /\d/.test(password))
  this.updateRequirement("special", /[^a-zA-Z0-9]/.test(password))
}

updateRequirement(name, met) {
  const element = this.element.querySelector(`[data-requirement="${name}"]`)
  if (element) {
    element.classList.toggle("requirement-met", met)
    element.classList.toggle("requirement-unmet", !met)
  }
}
```

```erb
<div data-controller="password-strength">
  <%= f.password_field :password, data: { password_strength_target: "input", action: "input->password-strength#check" } %>
  <meter data-password-strength-target="meter" max="5" value="0"></meter>
  <p data-password-strength-target="text"></p>

  <ul class="text-sm mt-2">
    <li data-requirement="length" class="requirement-unmet">At least 8 characters</li>
    <li data-requirement="uppercase" class="requirement-unmet">Uppercase letter</li>
    <li data-requirement="lowercase" class="requirement-unmet">Lowercase letter</li>
    <li data-requirement="number" class="requirement-unmet">Number</li>
    <li data-requirement="special" class="requirement-unmet">Special character</li>
  </ul>
</div>
```

## Related Skills

- [SKILL.md](./SKILL.md): All form Stimulus patterns
- [validation.md](./validation.md): Client-side validation
- [character-counter.md](./character-counter.md): Character counting
