---
description: Hotwire 관련 문제를 디버깅합니다.
argument-hint: "[turbo|stimulus|cable]"
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
---

# /rails8-hotwire:hotwire-debug - Hotwire Debugger

Turbo, Stimulus, ActionCable 관련 문제를 디버깅합니다.

## Common Issues

### Turbo
- Frame ID 불일치
- 상태 코드 누락 (422, 303)
- turbo:false 누락
- 중복 Frame

### Stimulus
- 컨트롤러 미등록
- 타겟 미발견
- 값 타입 불일치
- 이벤트 바인딩 오류

### ActionCable
- 연결 실패
- 구독 오류
- 브로드캐스트 미수신

## Example

```
/rails8-hotwire:hotwire-debug turbo
```

## Debugging Tips

```javascript
// Turbo 이벤트 디버깅
document.addEventListener("turbo:before-frame-render", (e) => {
  console.log("Frame render:", e.detail)
})

document.addEventListener("turbo:frame-missing", (e) => {
  console.log("Frame not found:", e.detail)
})
```

```javascript
// Stimulus 디버깅
Stimulus.debug = true
```
