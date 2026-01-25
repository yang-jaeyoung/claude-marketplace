---
name: hotwire-debug
description: Hotwire 관련 문제를 진단하고 해결합니다
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
---

# Hotwire Debug - Turbo/Stimulus 디버깅

## Diagnostics

| Issue | Common Cause |
|-------|--------------|
| Turbo Drive 비활성화 | `data-turbo="false"` 또는 JS 오류 |
| Turbo Frame 매칭 실패 | Frame ID 불일치 |
| Turbo Stream 적용 안됨 | Content-Type 미설정 |
| Stimulus 연결 실패 | 컨트롤러 미등록 또는 오타 |

## Workflow

1. 증상 설명 듣기
2. 로그/네트워크 분석
3. 원인 진단
4. 해결책 제시 및 적용

## Instructions

turbo-debugger 에이전트를 사용하여 문제를 진단합니다.

## Example

```
/rails8-hotwire:hotwire-debug Turbo Frame이 업데이트되지 않습니다
/rails8-hotwire:hotwire-debug Stimulus 컨트롤러가 동작하지 않습니다
```

## Debug Checklist

- [ ] 브라우저 콘솔 오류 확인
- [ ] 네트워크 탭에서 응답 확인
- [ ] Content-Type: text/vnd.turbo-stream.html 확인
- [ ] Turbo Frame ID 일치 확인
- [ ] Stimulus 컨트롤러 등록 확인
