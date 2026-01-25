# test-gen

기존 코드에 RSpec 테스트 생성

## Invocation
`/rails8:test-gen`

## Description
기존 코드를 분석하여 RSpec 테스트를 생성합니다.

## Usage
```
/rails8:test-gen app/models/post.rb
/rails8:test-gen app/controllers/posts_controller.rb
/rails8:test-gen app/services/
```

## Features
- 모델 유효성 검사 테스트
- 관계 테스트
- 스코프 테스트
- 컨트롤러 액션 테스트
- 서비스 객체 테스트
