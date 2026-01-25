// app/javascript/controllers/clipboard_controller.js
// 클립보드 복사 컨트롤러
//
// 사용법:
// <div data-controller="clipboard" data-clipboard-success-class="text-green-500">
//   <input data-clipboard-target="source" value="복사할 텍스트" readonly>
//   <button data-action="clipboard#copy">
//     <span data-clipboard-target="button">복사</span>
//   </button>
// </div>

import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["source", "button"]
  static classes = ["success"]
  static values = {
    successDuration: { type: Number, default: 2000 },
    successText: { type: String, default: "복사됨!" }
  }

  async copy() {
    const text = this.sourceTarget.value || this.sourceTarget.textContent

    try {
      await navigator.clipboard.writeText(text)
      this.showSuccess()
    } catch (error) {
      console.error("클립보드 복사 실패:", error)
    }
  }

  showSuccess() {
    const originalText = this.buttonTarget.textContent

    this.buttonTarget.textContent = this.successTextValue
    this.element.classList.add(this.successClass)

    setTimeout(() => {
      this.buttonTarget.textContent = originalText
      this.element.classList.remove(this.successClass)
    }, this.successDurationValue)
  }
}
