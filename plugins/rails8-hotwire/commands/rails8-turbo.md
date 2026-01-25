---
description: Turbo Drive/Frame/Stream 및 Stimulus 패턴 가이드.
argument-hint: "[pattern]"
allowed-tools: ["Read", "Glob", "Grep"]
---

# /rails8-hotwire:rails8-turbo - Hotwire Patterns

Turbo와 Stimulus 패턴을 안내합니다.

## Topics

1. **Turbo Drive** - SPA 스타일 페이지 전환
2. **Turbo Frame** - 부분 페이지 업데이트
3. **Turbo Stream** - 실시간 다중 요소 업데이트
4. **Stimulus** - JavaScript 컨트롤러

## Knowledge Loading

- `knowledge/hotwire/INDEX.md` - Hotwire 전체 가이드

## Key Patterns

### Turbo Frame Inline Edit

```erb
<%= turbo_frame_tag dom_id(@article) do %>
  <h1><%= @article.title %></h1>
  <%= link_to "Edit", edit_article_path(@article) %>
<% end %>
```

### Turbo Stream Response

```ruby
def create
  @post = Post.new(post_params)
  if @post.save
    respond_to do |format|
      format.turbo_stream
      format.html { redirect_to @post }
    end
  else
    render :new, status: :unprocessable_entity
  end
end
```

## Related

- `/rails8-hotwire:rails8-views` - 뷰 패턴
- `/rails8-hotwire:rails8-realtime` - 실시간 기능
