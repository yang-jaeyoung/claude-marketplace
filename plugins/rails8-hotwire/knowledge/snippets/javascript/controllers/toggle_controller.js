// app/javascript/controllers/toggle_controller.js
// 토글 기능을 제공하는 Stimulus 컨트롤러
//
// 사용법:
//   <div data-controller="toggle"
//        data-toggle-hidden-class="hidden"
//        data-toggle-open-value="false">
//     <button data-action="toggle#toggle">Toggle</button>
//     <div data-toggle-target="content" class="hidden">
//       Hidden content
//     </div>
//   </div>

import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["content"]
  static classes = ["hidden"]
  static values = {
    open: { type: Boolean, default: false }
  }

  toggle() {
    this.openValue = !this.openValue
  }

  show() {
    this.openValue = true
  }

  hide() {
    this.openValue = false
  }

  openValueChanged(isOpen) {
    if (this.hasContentTarget) {
      this.contentTarget.classList.toggle(this.hiddenClass, !isOpen)
    }
  }
}
