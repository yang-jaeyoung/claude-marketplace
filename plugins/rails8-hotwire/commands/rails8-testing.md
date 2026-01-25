---
description: RSpec, Factory Bot, 시스템 테스트 가이드.
argument-hint: "[test_type]"
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
---

# /rails8-hotwire:rails8-testing - Testing Patterns

RSpec 기반 테스트 패턴을 안내합니다.

## Topics

1. **RSpec 설정** - 프로젝트 설정
2. **모델 스펙** - 검증, 연관 관계 테스트
3. **요청 스펙** - API/컨트롤러 테스트
4. **시스템 스펙** - E2E 브라우저 테스트

## Knowledge Loading

- `knowledge/testing/INDEX.md` - 테스트 전체 가이드

## Quick Setup

```bash
bundle add rspec-rails factory_bot_rails faker --group development,test
rails generate rspec:install
```

## Key Patterns

### Model Spec

```ruby
RSpec.describe Post, type: :model do
  describe "validations" do
    it { is_expected.to validate_presence_of(:title) }
  end

  describe "associations" do
    it { is_expected.to belong_to(:user) }
    it { is_expected.to have_many(:comments) }
  end
end
```

### System Spec with Turbo

```ruby
RSpec.describe "Posts", type: :system do
  it "creates a post with Turbo" do
    visit new_post_path
    fill_in "Title", with: "Test"
    click_button "Save"

    expect(page).to have_text("Test")
  end
end
```

## Related

- `/rails8-hotwire:test-gen` - 테스트 자동 생성
- `/rails8-hotwire:rails8-models` - 모델 패턴
