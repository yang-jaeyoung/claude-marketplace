---
description: 기존 뷰에 Turbo Frame/Stream을 추가하는 마법사입니다.
argument-hint: "<view_path>"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep"]
context: fork
---

# /rails8-hotwire:turbo-wizard - Turbo Integration Wizard

기존 Rails 뷰를 Hotwire로 업그레이드합니다.

## What It Does

1. 기존 뷰 분석
2. Turbo Frame 추가 위치 제안
3. 컨트롤러 Turbo 응답 추가
4. Stimulus 컨트롤러 생성 (필요시)

## Patterns Applied

- **Inline Edit** - 인라인 편집 폼
- **Lazy Load** - 지연 로딩 프레임
- **Live Search** - 실시간 검색
- **Modal** - 모달 다이얼로그
- **Infinite Scroll** - 무한 스크롤

## Example

```
/rails8-hotwire:turbo-wizard app/views/posts/index.html.erb
```

## Output

- 수정된 뷰 파일
- Turbo Stream 템플릿 (필요시)
- Stimulus 컨트롤러 (필요시)
