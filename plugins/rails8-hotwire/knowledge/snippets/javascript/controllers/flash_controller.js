// app/javascript/controllers/flash_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["message"]
  static values = { dismissAfter: { type: Number, default: 5000 } }

  connect() {
    if (this.dismissAfterValue > 0) {
      this.timeout = setTimeout(() => this.dismissAll(), this.dismissAfterValue)
    }
  }

  disconnect() {
    if (this.timeout) clearTimeout(this.timeout)
  }

  dismiss(event) {
    const message = event.target.closest("[data-flash-target='message']")
    this.removeMessage(message)
  }

  dismissAll() {
    this.messageTargets.forEach(el => this.removeMessage(el))
  }

  removeMessage(el) {
    if (!el) return
    el.style.opacity = "0"
    el.style.transform = "translateX(100%)"
    setTimeout(() => el.remove(), 300)
  }
}
