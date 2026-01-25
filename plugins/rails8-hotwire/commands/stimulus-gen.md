---
description: Stimulus 컨트롤러를 생성합니다.
argument-hint: "<controller_name> [targets...] [values...]"
allowed-tools: ["Read", "Write", "Glob"]
context: fork
---

# /rails8-hotwire:stimulus-gen - Stimulus Controller Generator

Stimulus 컨트롤러와 관련 HTML을 생성합니다.

## Supported Patterns

- **Toggle** - 요소 표시/숨김
- **Dropdown** - 드롭다운 메뉴
- **Modal** - 모달 다이얼로그
- **Tabs** - 탭 컴포넌트
- **Form Validation** - 클라이언트 검증
- **Auto Submit** - 자동 폼 제출
- **Clipboard** - 클립보드 복사

## Example

```
/rails8-hotwire:stimulus-gen dropdown open:boolean items:array
```

## Output

```javascript
// app/javascript/controllers/dropdown_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["menu"]
  static values = { open: { type: Boolean, default: false } }

  toggle() {
    this.openValue = !this.openValue
  }

  openValueChanged(isOpen) {
    this.menuTarget.classList.toggle("hidden", !isOpen)
  }
}
```
