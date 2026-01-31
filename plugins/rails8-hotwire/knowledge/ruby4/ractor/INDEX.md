# Ractor in Ruby 4.0 / Ruby 4.0의 Ractor

> Ractor provides true parallel execution in Ruby through actor-based concurrency.
> Ractor는 액터 기반 동시성을 통해 Ruby에서 진정한 병렬 실행을 제공합니다.

## Overview / 개요

Ractor (Ruby Actor) enables parallel execution by creating isolated execution contexts that don't share mutable state.

### Key Changes in Ruby 4.0 / Ruby 4.0의 주요 변경사항

| Change | Description |
|--------|-------------|
| **Ractor::Port** | New synchronization mechanism |
| **Removed** | `Ractor.yield`, `Ractor#take` |
| **Removed** | `Ractor#close_incoming`, `Ractor#close_outgoing` |
| **Added** | `Ractor.shareable_proc`, `Ractor.shareable_lambda` |

## What is Ractor? / Ractor란?

Ractors are isolated execution units that:
- Run in parallel (utilizing multiple CPU cores)
- Don't share mutable objects
- Communicate via message passing
- Provide thread-safety without locks

## Quick Comparison: Ruby 3.x vs 4.0 / Ruby 3.x와 4.0 비교

### Ruby 3.x Style (Deprecated)

```ruby
# ❌ No longer works in Ruby 4.0
r = Ractor.new do
  Ractor.yield 42
end
value = r.take #=> 42
```

### Ruby 4.0 Style (New)

```ruby
# ✅ Ruby 4.0 approach
port = Ractor::Port.new

r = Ractor.new(port) do |p|
  p << 42
end

value = port.receive #=> 42
```

## Basic Concepts / 기본 개념

### 1. Ractor Creation

```ruby
# Create a Ractor with a block
r = Ractor.new do
  "Hello from Ractor"
end
```

### 2. Message Passing with Port

```ruby
port = Ractor::Port.new

Ractor.new(port) do |p|
  p << "message"  # Send to port
end

port.receive  #=> "message"  # Receive from port
```

### 3. Parallel Execution

```ruby
results = 4.times.map do |i|
  port = Ractor::Port.new
  Ractor.new(port, i) do |p, n|
    p << (n ** 2)
  end
  port
end

sums = results.map(&:receive)
puts sums #=> [0, 1, 4, 9]
```

## In This Section / 이 섹션의 내용

| Document | Description |
|----------|-------------|
| [Ractor::Port](port.md) | New communication mechanism |
| [Patterns](patterns.md) | Common concurrency patterns |
| [Migration](migration.md) | Upgrading from Ruby 3.x |

## When to Use Ractor / Ractor 사용 시점

### Good Use Cases ✅

- CPU-intensive computations
- Parallel data processing
- Isolated background tasks
- Actor-model architectures

### Not Recommended ❌

- I/O-bound operations (use Threads/Fibers)
- Shared state requirements
- Simple sequential tasks
- Quick scripts

## Shareable Objects / 공유 가능 객체

Ractors can only share certain types of objects:

| Type | Shareable? | Notes |
|------|------------|-------|
| Integers | ✅ | Immutable |
| Symbols | ✅ | Immutable |
| true/false/nil | ✅ | Immutable |
| Frozen strings | ✅ | `"str".freeze` |
| Frozen arrays | ✅ | If contents are shareable |
| Ractor::Port | ✅ | Thread-safe |
| Mutable strings | ❌ | Copy is sent |
| Mutable arrays | ❌ | Copy is sent |
| Most objects | ❌ | Copy is sent |

```ruby
# Make object shareable
shareable = Ractor.make_shareable({ a: 1, b: 2 }.freeze)
```

## New in Ruby 4.0 / Ruby 4.0 신규 기능

### Ractor.shareable_proc

```ruby
# Create a shareable proc
proc = Ractor.shareable_proc { |x| x * 2 }

# Use in multiple Ractors
Ractor.new(proc) do |p|
  p.call(21) #=> 42
end
```

### Ractor.shareable_lambda

```ruby
# Create a shareable lambda
lam = Ractor.shareable_lambda { |x, y| x + y }

Ractor.new(lam) do |l|
  l.call(1, 2) #=> 3
end
```

## Rails Considerations / Rails 고려사항

### Current Limitations

- ActiveRecord connections are not shareable
- Most Rails objects are mutable
- Request context can't cross Ractor boundaries

### Potential Use Cases in Rails

```ruby
# CPU-intensive background job
class HeavyComputationJob < ApplicationJob
  def perform(data)
    # Prepare immutable data
    frozen_data = Ractor.make_shareable(data.freeze)

    # Parallel processing
    ports = 4.times.map { Ractor::Port.new }
    chunks = frozen_data.each_slice(frozen_data.size / 4).to_a

    chunks.zip(ports).each do |chunk, port|
      Ractor.new(port, chunk) do |p, c|
        result = c.map { |item| heavy_compute(item) }
        p << result
      end
    end

    # Collect results
    results = ports.flat_map(&:receive)
    save_results(results)
  end
end
```

## See Also / 참고

- [Ractor::Port](port.md) - New Port-based communication
- [Concurrency Patterns](patterns.md) - Common patterns
- [Migration Guide](migration.md) - Upgrading from 3.x
- [Ruby 4.0 Overview](../overview/whats-new.md)
