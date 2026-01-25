---
description: 뷰 템플릿, ViewComponent, 폼 헬퍼 가이드.
argument-hint: "[component_name]"
allowed-tools: ["Read", "Glob", "Grep"]
---

# /rails8-hotwire:rails8-views - View Patterns

뷰 템플릿과 컴포넌트 패턴을 안내합니다.

## Topics

1. **레이아웃** - application.html.erb
2. **부분 템플릿** - 재사용 가능한 뷰 조각
3. **ViewComponent** - 객체지향 컴포넌트
4. **폼 헬퍼** - form_with

## Knowledge Loading

- `knowledge/views/INDEX.md` - 뷰 전체 가이드

## Key Patterns

### ViewComponent

```ruby
# app/components/button_component.rb
class ButtonComponent < ViewComponent::Base
  def initialize(label:, variant: "primary")
    @label = label
    @variant = variant
  end
end
```

```erb
<!-- app/components/button_component.html.erb -->
<button class="btn btn-<%= @variant %>">
  <%= @label %>
</button>
```

### Form with Turbo

```erb
<%= form_with model: @post, data: { turbo: true } do |f| %>
  <%= f.text_field :title %>
  <%= f.submit "Save" %>
<% end %>
```

## Related

- `/rails8-hotwire:rails8-turbo` - Turbo 패턴
- `/rails8-hotwire:stimulus-gen` - Stimulus 생성
