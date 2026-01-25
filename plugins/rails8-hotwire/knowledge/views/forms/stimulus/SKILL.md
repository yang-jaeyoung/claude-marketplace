---
name: rails8-views-form-stimulus
description: Form Stimulus controllers for validation, autosave, character count, and other enhancements
triggers:
  - form stimulus
  - form controller
  - character count
  - autosave
  - client validation
  - dependent select
  - 폼 스티뮬러스
  - 폼 컨트롤러
  - 글자 수 세기
  - 자동 저장
  - 클라이언트 유효성 검사
summary: |
  폼을 위한 Stimulus 컨트롤러 패턴을 다룹니다. 클라이언트 유효성 검사, 자동 저장,
  글자 수 카운터, 의존 필드 등을 포함합니다. 프로그레시브 인핸스먼트를 유지하면서
  폼 UX를 향상시킵니다.
token_cost: low
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - "*.md"
  deep:
    - "**/*.md"
    - "**/*.js"
---

# Form Stimulus Controllers

## Overview

Stimulus controllers enhance forms with client-side behaviors while maintaining progressive enhancement. Common patterns include validation, autosave, character counting, and dependent fields.

## When to Use

- When adding client-side validation
- When implementing autosave functionality
- When creating character counters
- When building dependent/conditional fields
- When enhancing form UX without full SPA

## Quick Start

```javascript
// app/javascript/controllers/form_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["submit"]

  connect() {
    this.element.addEventListener("turbo:submit-start", () => {
      this.submitTarget.disabled = true
      this.submitTarget.value = "Saving..."
    })
  }
}
```

```erb
<%= form_with model: @post, data: { controller: "form" } do |f| %>
  <%= f.text_field :title %>
  <%= f.submit data: { form_target: "submit" } %>
<% end %>
```

## Available Patterns

| Pattern | Purpose | Link |
|---------|---------|------|
| Character Counter | Track and display character count with warnings | [character-counter.md](./character-counter.md) |
| Form Validation | Client-side validation with HTML5 validation API | [validation.md](./validation.md) |
| Autosave | Debounced auto-saving with status feedback | [autosave.md](./autosave.md) |
| Dependent Select | Dynamic dropdown population based on parent selection | [dependent-select.md](./dependent-select.md) |
| Password Strength | Visual password strength meter | [password-strength.md](./password-strength.md) |
| Auto-Resize Textarea | Auto-expanding textarea based on content | [auto-resize.md](./auto-resize.md) |
| Slug Generator | Auto-generate URL slugs from title fields | [slug-generator.md](./slug-generator.md) |
| Dirty Tracking | Warn users about unsaved changes | [dirty-tracking.md](./dirty-tracking.md) |

## Controller Registration

```javascript
// app/javascript/controllers/index.js
import { application } from "./application"

import CharacterCountController from "./character_count_controller"
import ValidateController from "./validate_controller"
import AutosaveController from "./autosave_controller"
import DependentSelectController from "./dependent_select_controller"
import PasswordStrengthController from "./password_strength_controller"
import AutoResizeController from "./auto_resize_controller"
import SlugController from "./slug_controller"
import DirtyController from "./dirty_controller"

application.register("character-count", CharacterCountController)
application.register("validate", ValidateController)
application.register("autosave", AutosaveController)
application.register("dependent-select", DependentSelectController)
application.register("password-strength", PasswordStrengthController)
application.register("auto-resize", AutoResizeController)
application.register("slug", SlugController)
application.register("dirty", DirtyController)
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Client-only validation | Server bypassed | Always validate server-side too |
| No progressive enhancement | Breaks without JS | Forms work without JS |
| Heavy client logic | Hard to maintain | Keep controllers focused |
| Bypassing Turbo | Lose integration | Work with Turbo, not against |
| No loading states | Poor UX | Show feedback during operations |

## Related Skills

- [../form-builder.md](../form-builder.md): Form basics
- [../fields.md](../fields.md): Field types
- [../../../hotwire/SKILL.md](../../../hotwire/SKILL.md): Stimulus deep dive

## References

- [Stimulus Handbook](https://stimulus.hotwired.dev/handbook/introduction)
- [Stimulus Reference](https://stimulus.hotwired.dev/reference/controllers)
