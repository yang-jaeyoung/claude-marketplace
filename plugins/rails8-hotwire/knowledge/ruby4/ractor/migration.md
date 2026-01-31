# Ractor Migration: Ruby 3.x to 4.0 / 마이그레이션 가이드

> Guide for updating Ractor code from Ruby 3.x to Ruby 4.0.
> Ruby 3.x에서 Ruby 4.0으로 Ractor 코드를 업데이트하는 가이드.

## API Changes Overview / API 변경 개요

| Ruby 3.x | Ruby 4.0 | Status |
|----------|----------|--------|
| `Ractor.yield(value)` | `port << value` | Removed |
| `ractor.take` | `port.receive` | Removed |
| `ractor.close_incoming` | - | Removed |
| `ractor.close_outgoing` | - | Removed |
| - | `Ractor::Port.new` | New |
| - | `Ractor.shareable_proc` | New |
| - | `Ractor.shareable_lambda` | New |

## Migration Patterns / 마이그레이션 패턴

### Pattern 1: Basic Ractor.yield → Port

**Ruby 3.x:**
```ruby
# ❌ No longer works in Ruby 4.0
r = Ractor.new do
  result = heavy_computation
  Ractor.yield result  # Deprecated
end

value = r.take  # Deprecated
puts value
```

**Ruby 4.0:**
```ruby
# ✅ Ruby 4.0 approach
port = Ractor::Port.new

r = Ractor.new(port) do |p|
  result = heavy_computation
  p << result  # Send to port
end

value = port.receive  # Receive from port
puts value
```

### Pattern 2: Multiple Yields → Multiple Sends

**Ruby 3.x:**
```ruby
# ❌ Multiple yields
r = Ractor.new do
  3.times do |i|
    Ractor.yield i
  end
end

3.times { puts r.take }
```

**Ruby 4.0:**
```ruby
# ✅ Multiple sends to port
port = Ractor::Port.new

r = Ractor.new(port) do |p|
  3.times do |i|
    p << i
  end
end

3.times { puts port.receive }
```

### Pattern 3: Producer-Consumer with take → Port-based

**Ruby 3.x:**
```ruby
# ❌ Producer-consumer with take
producer = Ractor.new do
  loop do
    item = produce_item
    Ractor.yield item
    break if item.nil?
  end
end

consumer = Ractor.new(producer) do |prod|
  loop do
    item = prod.take  # Deprecated
    break if item.nil?
    process(item)
  end
end
```

**Ruby 4.0:**
```ruby
# ✅ Port-based producer-consumer
item_port = Ractor::Port.new

producer = Ractor.new(item_port) do |port|
  loop do
    item = produce_item
    port << item
    break if item.nil?
  end
end

consumer = Ractor.new(item_port) do |port|
  loop do
    item = port.receive
    break if item.nil?
    process(item)
  end
end
```

### Pattern 4: Bidirectional Communication

**Ruby 3.x:**
```ruby
# ❌ Using Ractor.receive + Ractor.yield
r = Ractor.new do
  while msg = Ractor.receive
    break if msg == :stop
    result = process(msg)
    Ractor.yield result
  end
end

r.send(data)
result = r.take
r.send(:stop)
```

**Ruby 4.0:**
```ruby
# ✅ Two ports for bidirectional communication
input_port = Ractor::Port.new
output_port = Ractor::Port.new

r = Ractor.new(input_port, output_port) do |inp, out|
  loop do
    msg = inp.receive
    break if msg == :stop
    result = process(msg)
    out << result
  end
end

# Send work and get results
input_port << data
result = output_port.receive

# Stop worker
input_port << :stop
```

### Pattern 5: close_incoming/close_outgoing Removal

**Ruby 3.x:**
```ruby
# ❌ Closing channels
r = Ractor.new do
  # Process all incoming
  while msg = Ractor.receive
    process(msg)
  end
end

r.send(:data1)
r.send(:data2)
r.close_incoming  # Signal no more input
```

**Ruby 4.0:**
```ruby
# ✅ Use sentinel value
port = Ractor::Port.new

r = Ractor.new(port) do |p|
  loop do
    msg = Ractor.receive
    break if msg == :done  # Sentinel value
    p << process(msg)
  end
  p << :finished
end

r.send(:data1)
r.send(:data2)
r.send(:done)  # Signal completion

# Collect results until finished
loop do
  result = port.receive
  break if result == :finished
  use(result)
end
```

### Pattern 6: Using shareable_proc

**Ruby 3.x:**
```ruby
# ❌ Blocks aren't shareable
block = proc { |x| x * 2 }

Ractor.new(block) do |b|
  b.call(21)  # Error: can't share Proc
end
```

**Ruby 4.0:**
```ruby
# ✅ Use shareable_proc
shareable_block = Ractor.shareable_proc { |x| x * 2 }

port = Ractor::Port.new
Ractor.new(port, shareable_block) do |p, b|
  result = b.call(21)
  p << result
end

puts port.receive #=> 42
```

## Complete Migration Example / 완전한 마이그레이션 예제

### Ruby 3.x Worker Pool

```ruby
# ❌ Ruby 3.x style - won't work in Ruby 4.0
class WorkerPool
  def initialize(size)
    @workers = size.times.map do
      Ractor.new do
        loop do
          msg = Ractor.receive
          break if msg == :stop
          Ractor.yield process(msg)
        end
      end
    end
  end

  def submit(work)
    worker = @workers.sample
    worker.send(work)
    worker.take
  end

  def shutdown
    @workers.each do |w|
      w.send(:stop)
      w.close_incoming
    end
  end

  private

  def process(work)
    work ** 2
  end
end
```

### Ruby 4.0 Worker Pool

```ruby
# ✅ Ruby 4.0 style
class WorkerPool
  def initialize(size)
    @result_port = Ractor::Port.new
    @workers = size.times.map do
      Ractor.new(@result_port) do |port|
        loop do
          msg = Ractor.receive
          break if msg == :stop
          port << process(msg)
        end
      end
    end
  end

  def submit(work)
    worker = @workers.sample
    worker.send(work)
    @result_port.receive
  end

  def shutdown
    @workers.each { |w| w.send(:stop) }
  end

  private

  def process(work)
    work ** 2
  end
end

# Usage
pool = WorkerPool.new(4)
result = pool.submit(10)
puts result #=> 100
pool.shutdown
```

## Migration Checklist / 마이그레이션 체크리스트

### Step 1: Find Deprecated Usage

```bash
# Search for deprecated patterns
grep -r "Ractor.yield" .
grep -r "\.take" . | grep -i ractor
grep -r "close_incoming" .
grep -r "close_outgoing" .
```

### Step 2: Create Ports

```ruby
# For each Ractor that uses yield/take, create a Port
port = Ractor::Port.new

# Pass port to Ractor
Ractor.new(port) do |p|
  # ...
end
```

### Step 3: Replace yield with Port Send

```ruby
# Before
Ractor.yield(value)

# After
port << value
```

### Step 4: Replace take with Port Receive

```ruby
# Before
ractor.take

# After
port.receive
```

### Step 5: Replace Close with Sentinel

```ruby
# Before
ractor.close_incoming

# After
ractor.send(:done)  # In Ractor, check for :done
```

### Step 6: Update Proc Usage

```ruby
# Before (didn't work anyway)
proc { |x| x }

# After
Ractor.shareable_proc { |x| x }
# or
Ractor.shareable_lambda { |x| x }
```

### Step 7: Test Thoroughly

```ruby
# Run tests with verbose output
bundle exec rspec --format documentation
```

## Common Errors and Solutions / 일반적인 오류와 해결책

### Error: undefined method 'yield' for Ractor

```ruby
# Cause: Using deprecated Ractor.yield
# Solution: Use Ractor::Port
```

### Error: undefined method 'take'

```ruby
# Cause: Using deprecated ractor.take
# Solution: Use port.receive
```

### Error: can't share Proc

```ruby
# Cause: Passing regular Proc to Ractor
# Solution: Use Ractor.shareable_proc
```

## See Also / 참고

- [Ractor Overview](INDEX.md)
- [Ractor::Port](port.md)
- [Concurrency Patterns](patterns.md)
- [Ruby 4.0 Upgrade Guide](../overview/upgrade-guide.md)
