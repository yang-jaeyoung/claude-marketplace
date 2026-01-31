# Ruby 4.0 for Rails 8 Developers

> Ruby 4.0 was released on December 25, 2025, marking Ruby's 30th anniversary.
> This knowledge base covers key features, migration guides, and Rails 8 integration.

## Quick Links / 빠른 링크

| Topic | Description | Status |
|-------|-------------|--------|
| [What's New](overview/whats-new.md) | New features overview | Stable |
| [ZJIT](zjit/INDEX.md) | Next-gen JIT compiler | Experimental |
| [Ruby::Box](ruby-box/INDEX.md) | Namespace isolation | Experimental |
| [Ractor](ractor/INDEX.md) | Improved concurrency | Stable |
| [Upgrade Guide](overview/upgrade-guide.md) | Migration from Ruby 3.x | - |

## Version Information / 버전 정보

| Version | Release Date | Notes |
|---------|--------------|-------|
| 4.0.0 | 2025-12-25 | Initial release (30th anniversary) |
| 4.0.1 | 2026-01-13 | Bug fixes |

## Rails 8 Compatibility / Rails 8 호환성

```
Rails 8.0.x: Ruby 3.2.0+ required, Ruby 4.0 compatible
Rails 8.1.x: Ruby 3.2.0+ required, Ruby 4.0 recommended
```

## Key Features Summary / 주요 기능 요약

### 1. ZJIT (Zero-overhead JIT)
```ruby
# Enable at runtime
RubyVM::ZJIT.enable

# Or via command line
# ruby --zjit your_app.rb
```
- SSA IR-based next-generation JIT compiler
- Developed by the YJIT team
- Currently experimental, not recommended for production

### 2. Ruby::Box (Namespace Isolation)
```ruby
# Enable with environment variable: RUBY_BOX=1
box = Ruby::Box.new
box.require("some_library")
# Library's definitions are isolated within the box
```
- Process-internal isolated spaces
- Isolates monkey patches, global/class variables, module/class definitions

### 3. Ractor::Port (Improved Concurrency)
```ruby
port = Ractor::Port.new

Ractor.new(port) do |p|
  p << "message"
end

port.receive #=> "message"
```
- New synchronization mechanism replacing `Ractor.yield` and `Ractor#take`

### 4. Core Class Promotions
```ruby
# Set is now a core class (no require needed)
set = Set[1, 2, 3]

# Pathname is now a core class
path = Pathname("/usr/local")

# New Ruby module
Ruby::VERSION      #=> "4.0.0"
Ruby::PLATFORM     #=> "x86_64-darwin24"
```

## Document Structure / 문서 구조

```
ruby4/
├── INDEX.md                 # This file
├── SKILL.md                 # Skill definition
├── overview/
│   ├── whats-new.md        # Feature overview
│   ├── upgrade-guide.md    # Migration guide
│   └── compatibility.md    # Rails compatibility
├── zjit/
│   ├── INDEX.md            # ZJIT overview
│   ├── setup.md            # Activation methods
│   ├── performance.md      # Benchmarks
│   └── rails-integration.md
├── ruby-box/
│   ├── INDEX.md            # Ruby::Box overview
│   ├── basics.md           # Basic usage
│   ├── isolation.md        # Isolation patterns
│   └── use-cases.md        # Practical examples
├── ractor/
│   ├── INDEX.md            # Ractor overview
│   ├── port.md             # Ractor::Port usage
│   ├── patterns.md         # Concurrency patterns
│   └── migration.md        # 3.x to 4.0 migration
├── core-changes/
│   ├── set-pathname.md     # Core promotions
│   ├── ruby-module.md      # Ruby module
│   └── language-changes.md # Syntax changes
├── breaking-changes/
│   ├── removed-features.md # Removed features
│   └── deprecations.md     # Deprecated features
└── snippets/
    ├── zjit_config.rb
    ├── ruby_box_example.rb
    └── ractor_port_example.rb
```

## References / 참고 자료

- [Official Release Notes](https://www.ruby-lang.org/en/news/2025/12/25/ruby-4-0-0-released/)
- [Ruby 4.0 NEWS](https://docs.ruby-lang.org/en/master/NEWS/NEWS-4_0_0_md.html)
- [Ruby::Box Documentation](https://docs.ruby-lang.org/en/4.0/doc/language/box_md)
- [ZJIT at Shopify](https://railsatscale.com/2025-12-24-launch-zjit/)
