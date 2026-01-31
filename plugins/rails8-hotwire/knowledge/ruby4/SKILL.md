---
name: ruby4
description: Ruby 4.0 features, ZJIT compiler, Ruby::Box isolation, and Ractor improvements for Rails 8 applications
triggers:
  - ruby 4
  - ruby4
  - ruby 4.0
  - zjit
  - ruby box
  - ractor port
  - 루비 4
  - 루비4
  - 지짓
  - 루비박스
  - 랙터 포트
---

# Ruby 4.0 Knowledge Base

This skill provides comprehensive documentation for Ruby 4.0 features and their integration with Rails 8 applications.

## Scope

### What This Covers
- ZJIT: Next-generation JIT compiler (experimental)
- Ruby::Box: Namespace isolation for libraries (experimental)
- Ractor::Port: Improved concurrency primitives
- Core class promotions: Set, Pathname
- Language changes and syntax updates
- Breaking changes and migration guides
- Rails 8 compatibility information

### Related Skills
- `core`: Rails 8 project setup and patterns
- `background`: Background jobs (Ractor use cases)
- `deploy`: Deployment configuration (ZJIT settings)
- `testing`: Test isolation (Ruby::Box potential)

## Quick Reference

### Enable ZJIT
```ruby
# Runtime activation
RubyVM::ZJIT.enable

# Command line
ruby --zjit app.rb

# Environment variable
RUBY_ZJIT_ENABLE=1
```

### Ruby::Box (Experimental)
```bash
# Enable the feature
RUBY_BOX=1 ruby your_app.rb
```

```ruby
box = Ruby::Box.new
box.require("library")
# Library is isolated within box
```

### Ractor::Port
```ruby
port = Ractor::Port.new

r = Ractor.new(port) do |p|
  p << 42
end

port.receive #=> 42
```

### Core Class Promotions
```ruby
# No require needed for Set
set = Set[1, 2, 3]

# No require needed for Pathname
path = Pathname("/home")

# New Ruby module
Ruby::VERSION #=> "4.0.0"
```

## When to Load This Skill

Load this skill when:
1. User asks about Ruby 4.0 features
2. User wants to upgrade from Ruby 3.x to 4.0
3. User mentions ZJIT, Ruby::Box, or Ractor::Port
4. User asks about Ruby/Rails version compatibility
5. User encounters breaking changes after Ruby upgrade

## Load Depth Guidelines

### Shallow (SKILL.md only)
- Quick feature overview
- Basic syntax examples
- Simple compatibility checks

### Standard (+ overview/, zjit/, ruby-box/)
- Feature explanations with examples
- Setup instructions
- Rails integration patterns
- Common migration scenarios

### Deep (All files including snippets)
- Complete migration guides
- Performance optimization
- Advanced patterns
- All code examples and snippets
