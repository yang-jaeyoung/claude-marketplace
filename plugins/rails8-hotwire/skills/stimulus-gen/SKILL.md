---
name: stimulus-gen
description: Stimulus 컨트롤러를 생성합니다
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
---

# Stimulus Generator - Stimulus 컨트롤러 생성

## Usage

```
/rails8-hotwire:stimulus-gen dropdown
/rails8-hotwire:stimulus-gen modal --targets="content,backdrop" --values="open:Boolean"
```

## Generated Files

- `app/javascript/controllers/{name}_controller.js`
- 사용 예제 HTML

## Instructions

1. 사용자가 요청한 컨트롤러 이름과 옵션 분석
2. stimulus-designer 에이전트를 사용하여 컨트롤러 생성
3. 타겟, 값, 액션을 올바르게 설정
4. 사용 예제 HTML 제공

## Common Patterns

| Pattern | Description |
|---------|-------------|
| dropdown | 드롭다운 메뉴 |
| modal | 모달 다이얼로그 |
| tabs | 탭 네비게이션 |
| accordion | 아코디언 |
| clipboard | 클립보드 복사 |
| form-validation | 폼 유효성 검사 |
