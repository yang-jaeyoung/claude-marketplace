# Ruby::Box: Namespace Isolation

> Ruby::Box is an experimental feature for isolating library code within a Ruby process.
> Ruby::Box는 Ruby 프로세스 내에서 라이브러리 코드를 격리하는 실험적 기능입니다.

## Overview / 개요

Ruby::Box provides isolated spaces within a single Ruby process, allowing libraries to be loaded without affecting the global namespace.

### Key Benefits / 주요 이점

| Benefit | Description |
|---------|-------------|
| **Isolation** | Libraries loaded in a box don't affect global state |
| **Conflict Resolution** | Multiple versions of same gem can coexist |
| **Testing** | Better test isolation without process forks |
| **Security** | Limit what loaded code can access |

### Current Status / 현재 상태

```
Status:       Experimental
Activation:   RUBY_BOX=1 environment variable
Stability:    APIs may change
Production:   Not recommended
```

## Quick Start / 빠른 시작

### Enable Ruby::Box

```bash
# Enable the feature via environment variable
RUBY_BOX=1 ruby your_script.rb
```

### Basic Usage

```ruby
# Create an isolated box
box = Ruby::Box.new

# Load library inside the box
box.require("some_library")

# Library's definitions are isolated within the box
# They don't pollute the global namespace
```

## What Gets Isolated / 격리되는 것

| Item | Isolated? | Description |
|------|-----------|-------------|
| Monkey patches | ✅ | Core class extensions stay in box |
| Global variables | ✅ | `$var` stays in box |
| Class variables | ✅ | `@@var` stays in box |
| Constants | ✅ | Classes/modules stay in box |
| Module definitions | ✅ | New modules stay in box |
| Class definitions | ✅ | New classes stay in box |
| Instance variables | ❌ | Attached to objects, not namespace |
| Method definitions | ✅ | On isolated classes only |

## In This Section / 이 섹션의 내용

| Document | Description |
|----------|-------------|
| [Basics](basics.md) | Basic usage patterns |
| [Isolation](isolation.md) | Isolation mechanisms and behavior |
| [Use Cases](use-cases.md) | Practical applications |

## Example Scenario / 예시 시나리오

### Problem: Conflicting Monkey Patches

```ruby
# Library A adds a method to String
class String
  def greet
    "Hello from A: #{self}"
  end
end

# Library B adds a different method with same name
class String
  def greet
    "Greetings from B: #{self}"
  end
end

# Conflict! Only B's version exists
"world".greet #=> "Greetings from B: world"
```

### Solution: Ruby::Box

```ruby
# Enable: RUBY_BOX=1

box_a = Ruby::Box.new
box_a.instance_eval do
  class String
    def greet
      "Hello from A: #{self}"
    end
  end
end

box_b = Ruby::Box.new
box_b.instance_eval do
  class String
    def greet
      "Greetings from B: #{self}"
    end
  end
end

# No conflict in global namespace
"world".greet #=> NoMethodError (not defined globally)

# Each box has its own version
box_a.instance_eval { "world".greet } #=> "Hello from A: world"
box_b.instance_eval { "world".greet } #=> "Greetings from B: world"
```

## Potential Use Cases / 잠재적 활용 사례

### 1. Test Isolation

Run tests in isolated boxes to prevent state leakage:

```ruby
RSpec.describe "Isolated tests" do
  around(:each) do |example|
    box = Ruby::Box.new
    box.instance_eval { example.run }
  end

  it "doesn't leak state" do
    # Test runs in isolation
  end
end
```

### 2. Multi-tenant Applications

Different tenants could have different library configurations:

```ruby
class TenantContext
  def initialize(tenant)
    @box = Ruby::Box.new
    @box.require(tenant.custom_library)
  end

  def execute(&block)
    @box.instance_eval(&block)
  end
end
```

### 3. Plugin Systems

Load plugins without risking conflicts:

```ruby
class PluginManager
  def load_plugin(path)
    box = Ruby::Box.new
    box.require(path)
    @plugins << box
  end
end
```

## Limitations / 제한사항

1. **Experimental**: APIs may change in future Ruby versions
2. **Memory**: Each box has memory overhead
3. **Complexity**: Adds complexity to application architecture
4. **Rails Integration**: Not yet well-defined for Rails applications

## Requirements / 요구사항

| Requirement | Details |
|-------------|---------|
| Ruby Version | 4.0.0 or later |
| Environment | `RUBY_BOX=1` must be set |
| Build | Standard Ruby 4.0 build |

## See Also / 참고

- [Basics](basics.md) - Getting started
- [Isolation Patterns](isolation.md) - How isolation works
- [Use Cases](use-cases.md) - Practical examples
- [What's New in Ruby 4.0](../overview/whats-new.md)
