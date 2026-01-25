// app/javascript/controllers/dropdown_controller.js
// 드롭다운 메뉴 Stimulus 컨트롤러
//
// 사용법:
//   <div data-controller="dropdown"
//        data-dropdown-open-class="block"
//        data-action="click@window->dropdown#closeOnClickOutside
//                    keydown.escape->dropdown#close">
//     <button data-action="dropdown#toggle">메뉴</button>
//     <div data-dropdown-target="menu" class="hidden">
//       <a href="#">항목 1</a>
//       <a href="#">항목 2</a>
//     </div>
//   </div>

import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["menu", "button"]
  static classes = ["open"]
  static values = {
    open: { type: Boolean, default: false }
  }

  toggle() {
    this.openValue = !this.openValue
  }

  open() {
    this.openValue = true
  }

  close() {
    this.openValue = false
  }

  closeOnClickOutside(event) {
    if (this.openValue && !this.element.contains(event.target)) {
      this.close()
    }
  }

  openValueChanged(isOpen) {
    if (this.hasMenuTarget) {
      if (isOpen) {
        this.menuTarget.classList.remove("hidden")
        this.menuTarget.classList.add(this.openClass)
      } else {
        this.menuTarget.classList.add("hidden")
        this.menuTarget.classList.remove(this.openClass)
      }
    }
  }
}
