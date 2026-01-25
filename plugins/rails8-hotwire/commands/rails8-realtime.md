---
description: ActionCable, Turbo Streams 실시간 기능 가이드.
argument-hint: "[feature]"
allowed-tools: ["Read", "Glob", "Grep"]
---

# /rails8-hotwire:rails8-realtime - Real-time Features

ActionCable과 Turbo Streams 실시간 기능을 안내합니다.

## Topics

1. **Turbo Broadcasts** - 모델 변경 자동 브로드캐스트
2. **ActionCable** - WebSocket 채널
3. **Solid Cable** - Redis 없는 WebSocket
4. **알림** - 실시간 알림 시스템

## Knowledge Loading

- `knowledge/realtime/INDEX.md` - 실시간 기능 전체 가이드

## Key Patterns

### Turbo Broadcasts

```ruby
class Post < ApplicationRecord
  broadcasts_to ->(post) { :posts }, inserts_by: :prepend
end
```

```erb
<%= turbo_stream_from :posts %>
<div id="posts">
  <%= render @posts %>
</div>
```

### ActionCable Channel

```ruby
class ChatChannel < ApplicationCable::Channel
  def subscribed
    stream_from "chat_#{params[:room]}"
  end

  def speak(data)
    ActionCable.server.broadcast("chat_#{params[:room]}", data)
  end
end
```

## Related

- `/rails8-hotwire:rails8-turbo` - Turbo 패턴
- `/rails8-hotwire:hotwire-debug` - Hotwire 디버깅
