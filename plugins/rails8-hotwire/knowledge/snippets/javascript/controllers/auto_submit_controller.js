// app/javascript/controllers/auto_submit_controller.js
// 폼 자동 제출 컨트롤러 (실시간 검색, 필터 등)
//
// 사용법:
// <%= form_with url: search_path, method: :get,
//               data: { controller: "auto-submit",
//                       auto_submit_delay_value: 300 } do |f| %>
//   <%= f.text_field :q, data: { action: "input->auto-submit#submit" } %>
// <% end %>

import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { delay: { type: Number, default: 300 } }

  connect() {
    this.timeout = null
  }

  disconnect() {
    this.clearTimeout()
  }

  submit() {
    this.clearTimeout()
    this.timeout = setTimeout(() => {
      this.element.requestSubmit()
    }, this.delayValue)
  }

  submitNow() {
    this.clearTimeout()
    this.element.requestSubmit()
  }

  clearTimeout() {
    if (this.timeout) {
      clearTimeout(this.timeout)
      this.timeout = null
    }
  }
}
