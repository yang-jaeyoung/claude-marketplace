# scaffold-plus

향상된 스캐폴딩

## Invocation
`/rails8:scaffold-plus`

## Description
표준 Rails scaffold에 Turbo, RSpec, 서비스 객체를 추가합니다.

## Features
- Turbo Frame/Stream 통합
- RSpec request/system specs
- 서비스 객체 (Create, Update, Destroy)
- 페이지네이션 (Pagy)
- 검색/필터링

## Usage
```
/rails8:scaffold-plus Post title:string body:text published:boolean
```

## Generated Files
- app/models/post.rb
- app/controllers/posts_controller.rb
- app/views/posts/*.erb (Turbo 통합)
- app/views/posts/*.turbo_stream.erb
- app/services/posts/create_service.rb
- spec/requests/posts_spec.rb
- spec/system/posts_spec.rb
