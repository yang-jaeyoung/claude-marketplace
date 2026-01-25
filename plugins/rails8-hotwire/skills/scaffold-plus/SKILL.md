---
name: scaffold-plus
description: 표준 Rails scaffold에 Turbo, RSpec, 서비스 객체를 추가하는 향상된 스캐폴딩
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
---

# Scaffold Plus - 향상된 스캐폴딩

## Features

- Turbo Frame/Stream 통합
- RSpec request/system specs
- 서비스 객체 (Create, Update, Destroy)
- 페이지네이션 (Pagy)
- 검색/필터링

## Usage

```
/rails8-hotwire:scaffold-plus Post title:string body:text published:boolean
```

## Generated Files

- `app/models/post.rb`
- `app/controllers/posts_controller.rb`
- `app/views/posts/*.erb` (Turbo 통합)
- `app/views/posts/*.turbo_stream.erb`
- `app/services/posts/create_service.rb`
- `spec/requests/posts_spec.rb`
- `spec/system/posts_spec.rb`

## Instructions

1. 사용자가 제공한 모델명과 속성을 분석
2. rails-executor 에이전트를 사용하여 파일 생성
3. Turbo Frame으로 뷰 래핑
4. 서비스 객체 패턴 적용
5. RSpec 테스트 생성
