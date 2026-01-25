// app/javascript/controllers/tabs_controller.js
// 탭 네비게이션 Stimulus 컨트롤러
//
// 사용법:
//   <div data-controller="tabs" data-tabs-active-class="border-blue-500">
//     <div role="tablist">
//       <button data-tabs-target="tab" data-action="tabs#select" data-index="0">탭 1</button>
//       <button data-tabs-target="tab" data-action="tabs#select" data-index="1">탭 2</button>
//       <button data-tabs-target="tab" data-action="tabs#select" data-index="2">탭 3</button>
//     </div>
//
//     <div data-tabs-target="panel">탭 1 내용</div>
//     <div data-tabs-target="panel" class="hidden">탭 2 내용</div>
//     <div data-tabs-target="panel" class="hidden">탭 3 내용</div>
//   </div>

import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["tab", "panel"]
  static classes = ["active"]
  static values = {
    index: { type: Number, default: 0 }
  }

  connect() {
    this.showTab(this.indexValue)
  }

  select(event) {
    const index = parseInt(event.currentTarget.dataset.index, 10)
    this.indexValue = index
  }

  indexValueChanged(index) {
    this.showTab(index)
  }

  showTab(index) {
    // 모든 탭 비활성화
    this.tabTargets.forEach((tab, i) => {
      if (i === index) {
        tab.classList.add(this.activeClass)
        tab.setAttribute("aria-selected", "true")
      } else {
        tab.classList.remove(this.activeClass)
        tab.setAttribute("aria-selected", "false")
      }
    })

    // 해당 패널만 표시
    this.panelTargets.forEach((panel, i) => {
      if (i === index) {
        panel.classList.remove("hidden")
        panel.setAttribute("aria-hidden", "false")
      } else {
        panel.classList.add("hidden")
        panel.setAttribute("aria-hidden", "true")
      }
    })
  }

  // 키보드 네비게이션
  next() {
    if (this.indexValue < this.tabTargets.length - 1) {
      this.indexValue++
    }
  }

  prev() {
    if (this.indexValue > 0) {
      this.indexValue--
    }
  }
}
