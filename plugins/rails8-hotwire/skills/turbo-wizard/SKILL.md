---
name: turbo-wizard
description: 인터랙티브하게 Turbo Frame/Stream을 설정하는 마법사
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
---

# Turbo Wizard - Turbo Frame/Stream 설정 마법사

## Workflow

1. 대상 선택 (Frame vs Stream)
2. 사용 사례 선택
3. 코드 생성
4. 통합 가이드 제공

## Available Templates

| Template | Description |
|----------|-------------|
| 무한 스크롤 | Pagy와 Turbo Frame lazy loading |
| 라이브 검색 | Stimulus + Turbo Frame 실시간 검색 |
| 인라인 편집 | Turbo Frame을 사용한 인플레이스 편집 |
| 모달 폼 | Turbo Frame 모달 다이얼로그 |
| 드래그 앤 드롭 | Sortable.js + Turbo Stream |
| 실시간 카운터 | Turbo Stream 브로드캐스트 |

## Instructions

hotwire-specialist 에이전트를 사용하여 사용자의 요구사항에 맞는 Turbo 패턴을 구현합니다.

## Example

```
/rails8-hotwire:turbo-wizard 댓글 목록에 무한 스크롤을 추가하고 싶습니다
```
