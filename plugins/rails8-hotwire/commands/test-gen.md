---
description: 모델/컨트롤러에 대한 RSpec 테스트를 자동 생성합니다.
argument-hint: "<target> [model|request|system]"
allowed-tools: ["Read", "Write", "Glob", "Grep"]
context: fork
---

# /rails8-hotwire:test-gen - Test Generator

기존 모델이나 컨트롤러에 대한 RSpec 테스트를 자동으로 생성합니다.

## Test Types

- **model** - 모델 스펙 (검증, 연관, 스코프)
- **request** - 요청 스펙 (API/컨트롤러)
- **system** - 시스템 스펙 (E2E 브라우저)

## What It Generates

### Model Spec
- Validation tests
- Association tests
- Scope tests
- Method tests

### Request Spec
- CRUD action tests
- Turbo response tests
- Authorization tests

### System Spec
- User flow tests
- Turbo interaction tests
- JavaScript behavior tests

## Example

```
/rails8-hotwire:test-gen Post model request
```

## Output

```ruby
# spec/models/post_spec.rb
RSpec.describe Post, type: :model do
  describe "validations" do
    it { is_expected.to validate_presence_of(:title) }
  end
end
```
