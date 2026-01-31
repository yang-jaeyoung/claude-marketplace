# Ractor::Port / 랙터 포트

> Ractor::Port is the new communication mechanism in Ruby 4.0.
> Ractor::Port는 Ruby 4.0의 새로운 통신 메커니즘입니다.

## Overview / 개요

`Ractor::Port` replaces the deprecated `Ractor.yield` and `Ractor#take` methods. It provides a cleaner, more flexible way for Ractors to communicate.

## Basic Usage / 기본 사용법

### Creating a Port

```ruby
port = Ractor::Port.new
```

### Sending Messages

```ruby
port = Ractor::Port.new

Ractor.new(port) do |p|
  p << "Hello"      # Send using << operator
  p.send("World")   # Alternative: send method
end
```

### Receiving Messages

```ruby
port = Ractor::Port.new

Ractor.new(port) do |p|
  p << "message"
end

msg = port.receive  # Blocking receive
puts msg #=> "message"
```

## Port vs Old API / Port와 기존 API 비교

### Old Way (Ruby 3.x) - Deprecated

```ruby
# ❌ These no longer work in Ruby 4.0

# Sending from Ractor
r = Ractor.new do
  Ractor.yield "value"  # Deprecated
end

# Receiving in main
value = r.take  # Deprecated

# Sending to Ractor
r = Ractor.new do
  msg = Ractor.receive
end
r.send("message")  # Still works, but...

# Closing
r.close_incoming   # Deprecated
r.close_outgoing   # Deprecated
```

### New Way (Ruby 4.0)

```ruby
# ✅ Ruby 4.0 approach

# Sending from Ractor
port = Ractor::Port.new
r = Ractor.new(port) do |p|
  p << "value"  # Send to port
end
value = port.receive  # Receive from port

# Sending to Ractor (can still use Ractor.receive)
r = Ractor.new do
  msg = Ractor.receive
end
r.send("message")  # This still works
```

## Multiple Ports / 여러 포트 사용

### Separate Channels

```ruby
input_port = Ractor::Port.new
output_port = Ractor::Port.new

worker = Ractor.new(input_port, output_port) do |inp, out|
  loop do
    data = inp.receive
    break if data == :stop

    result = data * 2
    out << result
  end
end

# Send work
input_port << 10
input_port << 20
input_port << 30

# Receive results
output_port.receive #=> 20
output_port.receive #=> 40
output_port.receive #=> 60

# Stop worker
input_port << :stop
```

### Multiple Workers, One Output

```ruby
result_port = Ractor::Port.new
workers = []

4.times do |i|
  workers << Ractor.new(result_port, i) do |port, id|
    # Do work
    sleep(rand)  # Simulate work
    port << "Worker #{id} done"
  end
end

# Collect all results
4.times do
  puts result_port.receive
end
```

## Port Patterns / 포트 패턴

### Request-Response Pattern

```ruby
class RactorService
  def initialize
    @request_port = Ractor::Port.new
    @response_port = Ractor::Port.new

    @worker = Ractor.new(@request_port, @response_port) do |req, res|
      loop do
        request = req.receive
        break if request == :shutdown

        # Process request
        result = process(request)
        res << result
      end
    end
  end

  def call(request)
    @request_port << request
    @response_port.receive
  end

  def shutdown
    @request_port << :shutdown
  end

  private

  def process(request)
    # Processing logic
    request.upcase
  end
end

service = RactorService.new
result = service.call("hello") #=> "HELLO"
service.shutdown
```

### Fan-Out Pattern

```ruby
def parallel_map(items, worker_count: 4, &block)
  # Create ports for each worker
  ports = worker_count.times.map { Ractor::Port.new }

  # Distribute items to workers
  items.each_with_index do |item, i|
    port = ports[i % worker_count]
    Ractor.new(port, item, block) do |p, it, blk|
      result = blk.call(it)
      p << { index: i, result: result }
    end
  end

  # Collect results
  results = Array.new(items.size)
  items.size.times do
    # Receive from any port
    ports.each do |port|
      begin
        msg = port.receive_if_not_empty rescue nil
        if msg
          results[msg[:index]] = msg[:result]
        end
      rescue
        # Port empty, try next
      end
    end
  end

  results
end
```

### Pipeline Pattern

```ruby
def create_pipeline
  stage1_out = Ractor::Port.new
  stage2_out = Ractor::Port.new
  final_out = Ractor::Port.new

  # Stage 1: Parse
  Ractor.new(stage1_out) do |out|
    loop do
      data = Ractor.receive
      break if data == :stop
      out << { parsed: data.to_i }
    end
    out << :done
  end

  # Stage 2: Transform
  Ractor.new(stage1_out, stage2_out) do |inp, out|
    loop do
      data = inp.receive
      break if data == :done
      out << { transformed: data[:parsed] * 2 }
    end
    out << :done
  end

  # Stage 3: Format
  Ractor.new(stage2_out, final_out) do |inp, out|
    loop do
      data = inp.receive
      break if data == :done
      out << "Result: #{data[:transformed]}"
    end
    out << :complete
  end

  # Return entry point and exit point
  [Ractor.current, final_out]
end
```

## Error Handling / 오류 처리

### Errors in Ractors

```ruby
port = Ractor::Port.new

Ractor.new(port) do |p|
  begin
    raise "Something went wrong"
  rescue => e
    p << { error: e.message }
  end
end

result = port.receive
if result[:error]
  puts "Error: #{result[:error]}"
end
```

### Timeout Pattern

```ruby
require 'timeout'

port = Ractor::Port.new

Ractor.new(port) do |p|
  sleep 5  # Long operation
  p << "done"
end

begin
  Timeout.timeout(2) do
    result = port.receive
  end
rescue Timeout::Error
  puts "Operation timed out"
end
```

## Port API Reference / 포트 API 참조

### Creating Port

```ruby
port = Ractor::Port.new
```

### Sending

```ruby
port << value       # Send (aliases: push)
port.send(value)    # Alternative
```

### Receiving

```ruby
port.receive        # Blocking receive
port.receive_if { } # Conditional receive (if available)
```

## Best Practices / 모범 사례

### 1. Create Ports Before Ractors

```ruby
# ✅ Good
port = Ractor::Port.new
Ractor.new(port) { |p| p << "data" }

# ❌ Bad - can't pass port created inside
Ractor.new do
  port = Ractor::Port.new  # Can't share this!
end
```

### 2. Use Separate Ports for Separate Concerns

```ruby
# ✅ Clear separation
data_port = Ractor::Port.new
error_port = Ractor::Port.new
status_port = Ractor::Port.new

Ractor.new(data_port, error_port, status_port) do |data, err, status|
  status << :started
  begin
    result = heavy_work
    data << result
  rescue => e
    err << e.message
  end
  status << :finished
end
```

### 3. Handle Port Lifecycle

```ruby
class WorkerPool
  def initialize(size)
    @result_port = Ractor::Port.new
    @workers = size.times.map do
      Ractor.new(@result_port) do |port|
        loop do
          work = Ractor.receive
          break if work == :shutdown
          port << process(work)
        end
      end
    end
  end

  def submit(work)
    @workers.sample.send(work)
    @result_port.receive
  end

  def shutdown
    @workers.each { |w| w.send(:shutdown) }
  end
end
```

## See Also / 참고

- [Ractor Overview](INDEX.md)
- [Concurrency Patterns](patterns.md)
- [Migration Guide](migration.md)
