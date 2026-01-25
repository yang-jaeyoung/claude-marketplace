---
name: rails8-turbo
description: Hotwire 스택 (Turbo + Stimulus) 사용 패턴 가이드
allowed-tools: Read, Glob, Grep
---

# Rails 8 Turbo - Turbo Drive/Frame/Stream and Stimulus

## Topics

- Turbo Drive (page navigation)
- Turbo Frame (partial updates)
- Turbo Stream (real-time updates)
- Turbo Morphing (Rails 8)
- Stimulus controllers
- Common interaction patterns

## Patterns

| Pattern | Technology |
|---------|------------|
| Infinite scroll | Turbo Frame lazy loading |
| Live search | Stimulus + Turbo Frame |
| Partial form submission | Turbo Frame |
| Modal/dropdown | Stimulus |
| Drag and drop | Sortable.js + Turbo Stream |
| Inline editing | Turbo Frame |

## Knowledge Reference

For comprehensive documentation, see:
- **[knowledge/hotwire/SKILL.md](../../knowledge/hotwire/SKILL.md)**: Full Turbo/Stimulus patterns and examples

## Related Agents

- `hotwire-specialist`: Turbo/Stimulus expert
- `hotwire-specialist-high`: Complex Hotwire patterns
- `stimulus-designer`: Stimulus controller design
- `turbo-debugger`: Debugging Turbo issues

## Related Skills

- [rails8-controllers](../rails8-controllers/SKILL.md): Turbo response handling
- [rails8-views](../rails8-views/SKILL.md): View integration
- [rails8-realtime](../rails8-realtime/SKILL.md): WebSocket broadcasting
