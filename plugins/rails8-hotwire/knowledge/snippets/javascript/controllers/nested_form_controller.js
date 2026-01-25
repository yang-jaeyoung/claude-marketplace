// app/javascript/controllers/nested_form_controller.js
// 중첩 폼(accepts_nested_attributes_for) 컨트롤러

import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["container", "template"]
  static values = { wrapperSelector: { type: String, default: ".nested-fields" } }

  add(event) {
    event.preventDefault()
    const content = this.templateTarget.innerHTML
    const uniqueId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const newContent = content.replace(/NEW_RECORD/g, uniqueId)
    this.containerTarget.insertAdjacentHTML("beforeend", newContent)
  }

  remove(event) {
    event.preventDefault()
    const wrapper = event.target.closest(this.wrapperSelectorValue)
    if (!wrapper) return

    const destroyInput = wrapper.querySelector("input[name*='_destroy']")
    const isNew = !wrapper.querySelector("input[name*='[id]']")?.value

    if (isNew) {
      wrapper.remove()
    } else if (destroyInput) {
      destroyInput.value = "1"
      wrapper.style.display = "none"
    }
  }
}
