// app/javascript/controllers/{name}_controller.js
// Stimulus 컨트롤러 기본 템플릿
//
// 사용법:
//   <div data-controller="{name}">
//     <input data-{name}-target="input">
//     <button data-action="{name}#submit">Submit</button>
//   </div>

import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  // 타겟 정의: data-{controller}-target="{name}"
  static targets = ["input", "output"]

  // 값 정의: data-{controller}-{name}-value="{value}"
  static values = {
    url: String,
    delay: { type: Number, default: 300 }
  }

  // CSS 클래스 정의: data-{controller}-{name}-class="{class}"
  static classes = ["active", "loading"]

  // 컨트롤러가 DOM에 연결될 때
  connect() {
    // 초기화 로직
  }

  // 컨트롤러가 DOM에서 분리될 때
  disconnect() {
    // 정리 로직 (이벤트 리스너 제거 등)
  }

  // 값이 변경될 때 호출되는 콜백
  urlValueChanged(value, previousValue) {
    // 값 변경 처리
  }

  // 타겟이 DOM에 추가될 때
  inputTargetConnected(element) {
    // 타겟 연결 처리
  }

  // 액션 메서드: data-action="{controller}#{method}"
  submit(event) {
    event.preventDefault()
    // 액션 로직
  }
}
