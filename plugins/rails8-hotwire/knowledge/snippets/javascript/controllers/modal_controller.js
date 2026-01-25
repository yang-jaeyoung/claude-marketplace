// app/javascript/controllers/modal_controller.js
// 모달 다이얼로그 Stimulus 컨트롤러
//
// 사용법:
//   <div data-controller="modal"
//        data-modal-open-class="opacity-100"
//        data-modal-backdrop-class="bg-black/50"
//        data-action="keydown.escape->modal#close">
//
//     <button data-action="modal#open">모달 열기</button>
//
//     <div data-modal-target="container"
//          class="fixed inset-0 hidden flex items-center justify-center">
//       <div data-modal-target="backdrop"
//            data-action="click->modal#close"
//            class="absolute inset-0"></div>
//       <div data-modal-target="panel" class="relative bg-white p-6 rounded">
//         <h2>모달 제목</h2>
//         <p>모달 내용</p>
//         <button data-action="modal#close">닫기</button>
//       </div>
//     </div>
//   </div>

import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["container", "backdrop", "panel"]
  static classes = ["open", "backdrop"]
  static values = {
    open: { type: Boolean, default: false },
    closeOnBackdrop: { type: Boolean, default: true }
  }

  connect() {
    // ESC 키로 닫기
    this.boundKeydown = this.handleKeydown.bind(this)
  }

  disconnect() {
    document.removeEventListener("keydown", this.boundKeydown)
    this.unlockScroll()
  }

  open() {
    this.openValue = true
  }

  close() {
    this.openValue = false
  }

  toggle() {
    this.openValue = !this.openValue
  }

  closeOnBackdropClick(event) {
    if (this.closeOnBackdropValue && event.target === this.backdropTarget) {
      this.close()
    }
  }

  openValueChanged(isOpen) {
    if (isOpen) {
      this.show()
    } else {
      this.hide()
    }
  }

  show() {
    if (this.hasContainerTarget) {
      this.containerTarget.classList.remove("hidden")
      this.lockScroll()
      document.addEventListener("keydown", this.boundKeydown)

      // 애니메이션
      requestAnimationFrame(() => {
        if (this.hasBackdropTarget && this.hasBackdropClass) {
          this.backdropTarget.classList.add(this.backdropClass)
        }
        if (this.hasPanelTarget && this.hasOpenClass) {
          this.panelTarget.classList.add(this.openClass)
        }
      })
    }
  }

  hide() {
    if (this.hasContainerTarget) {
      document.removeEventListener("keydown", this.boundKeydown)

      // 애니메이션 후 숨김
      if (this.hasBackdropTarget && this.hasBackdropClass) {
        this.backdropTarget.classList.remove(this.backdropClass)
      }
      if (this.hasPanelTarget && this.hasOpenClass) {
        this.panelTarget.classList.remove(this.openClass)
      }

      setTimeout(() => {
        this.containerTarget.classList.add("hidden")
        this.unlockScroll()
      }, 150)
    }
  }

  handleKeydown(event) {
    if (event.key === "Escape") {
      this.close()
    }
  }

  lockScroll() {
    document.body.style.overflow = "hidden"
  }

  unlockScroll() {
    document.body.style.overflow = ""
  }
}
