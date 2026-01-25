---
name: test-gen
description: 기존 코드를 분석하여 RSpec 테스트를 생성합니다
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
---

# Test Generator - RSpec 테스트 생성

## Usage

```
/rails8-hotwire:test-gen app/models/post.rb
/rails8-hotwire:test-gen app/controllers/posts_controller.rb
/rails8-hotwire:test-gen app/services/
```

## Features

- 모델 유효성 검사 테스트
- 관계(associations) 테스트
- 스코프 테스트
- 컨트롤러 액션 테스트
- 서비스 객체 테스트

## Instructions

1. 대상 파일/디렉토리 분석
2. rspec-tester 에이전트를 사용하여 테스트 생성
3. FactoryBot 팩토리 생성
4. 엣지 케이스 포함

## Generated Files

- `spec/models/{name}_spec.rb`
- `spec/requests/{name}_spec.rb`
- `spec/services/{name}_spec.rb`
- `spec/factories/{name}.rb`
