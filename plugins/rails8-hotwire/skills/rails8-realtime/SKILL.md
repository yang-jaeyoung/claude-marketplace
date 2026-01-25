# rails8-realtime

Real-time Features Skill

## Invocation
`/rails8:realtime`

## Description
Guides ActionCable, Turbo Streams broadcasting, and real-time features.

## Topics
- ActionCable channels
- Turbo Stream broadcasting
- Solid Cable setup (Redis-free)
- Presence features
- Real-time notifications
- Chat/live feeds
- Collaborative editing

## Quick Start
```ruby
# Model with automatic broadcasting
class Message < ApplicationRecord
  broadcasts_to :room
end
```

```erb
<%%= turbo_stream_from @room %>
```

## Knowledge Reference
For comprehensive documentation, see:
- **[knowledge/realtime/SKILL.md](../../knowledge/realtime/SKILL.md)**: Full real-time patterns and ActionCable setup

## Related Agents
- `hotwire-specialist-high`: Complex real-time patterns
- `rails-architect`: Real-time architecture

## Related Skills
- [rails8-turbo](../rails8-turbo/SKILL.md): Turbo Streams basics
- [rails8-background](../rails8-background/SKILL.md): Async broadcasting
- [rails8-deploy](../rails8-deploy/SKILL.md): Redis/Solid Cable deployment
