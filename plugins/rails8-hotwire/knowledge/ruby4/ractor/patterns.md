# Ractor Concurrency Patterns / 동시성 패턴

> Common patterns for parallel programming with Ractors in Ruby 4.0.
> Ruby 4.0의 Ractor를 사용한 병렬 프로그래밍의 일반적인 패턴.

## 1. Worker Pool Pattern / 워커 풀 패턴

### Basic Worker Pool

```ruby
class RactorPool
  def initialize(size)
    @size = size
    @result_port = Ractor::Port.new
    @workers = create_workers
  end

  def process(items, &block)
    # Distribute work
    items.each_with_index do |item, i|
      worker = @workers[i % @size]
      worker.send([item, block])
    end

    # Collect results
    items.map { @result_port.receive }
  end

  private

  def create_workers
    @size.times.map do
      Ractor.new(@result_port) do |result_port|
        loop do
          item, block = Ractor.receive
          break if item == :shutdown

          result = block.call(item)
          result_port << result
        end
      end
    end
  end

  def shutdown
    @workers.each { |w| w.send([:shutdown, nil]) }
  end
end

# Usage
pool = RactorPool.new(4)
results = pool.process([1, 2, 3, 4, 5]) { |x| x ** 2 }
puts results #=> [1, 4, 9, 16, 25]
```

### Dynamic Worker Pool

```ruby
class DynamicPool
  def initialize(min_workers: 2, max_workers: 8)
    @min = min_workers
    @max = max_workers
    @workers = []
    @result_port = Ractor::Port.new
    @min.times { add_worker }
  end

  def add_worker
    return if @workers.size >= @max

    worker = Ractor.new(@result_port) do |port|
      loop do
        msg = Ractor.receive
        break if msg == :shutdown
        port << msg.call
      end
    end
    @workers << worker
  end

  def remove_worker
    return if @workers.size <= @min
    worker = @workers.pop
    worker.send(:shutdown)
  end

  def submit(&block)
    shareable_block = Ractor.shareable_proc(&block)
    @workers.sample.send(shareable_block)
    @result_port.receive
  end
end
```

## 2. Map-Reduce Pattern / 맵-리듀스 패턴

```ruby
module RactorMapReduce
  def self.map_reduce(data, map_fn, reduce_fn, workers: 4)
    # Prepare shareable functions
    map_proc = Ractor.shareable_proc(&map_fn)
    reduce_proc = Ractor.shareable_proc(&reduce_fn)

    # Split data
    chunk_size = (data.size.to_f / workers).ceil
    chunks = data.each_slice(chunk_size).to_a

    # Map phase
    map_port = Ractor::Port.new
    chunks.each do |chunk|
      frozen_chunk = Ractor.make_shareable(chunk.freeze)
      Ractor.new(map_port, frozen_chunk, map_proc) do |port, data, mapper|
        results = data.map { |item| mapper.call(item) }
        port << results
      end
    end

    # Collect mapped results
    mapped = chunks.size.times.flat_map { map_port.receive }

    # Reduce phase
    reduce_port = Ractor::Port.new
    frozen_mapped = Ractor.make_shareable(mapped.freeze)
    Ractor.new(reduce_port, frozen_mapped, reduce_proc) do |port, data, reducer|
      result = data.reduce { |acc, item| reducer.call(acc, item) }
      port << result
    end

    reduce_port.receive
  end
end

# Example: Word count
words = ["hello", "world", "hello", "ruby", "world", "hello"]

result = RactorMapReduce.map_reduce(
  words,
  ->(word) { { word => 1 } },                    # Map
  ->(a, b) { a.merge(b) { |_, v1, v2| v1 + v2 }} # Reduce
)

puts result #=> {"hello"=>3, "world"=>2, "ruby"=>1}
```

## 3. Pipeline Pattern / 파이프라인 패턴

```ruby
class Pipeline
  def initialize
    @stages = []
    @ports = []
  end

  def add_stage(&block)
    shareable_fn = Ractor.shareable_proc(&block)
    @stages << shareable_fn
    self
  end

  def build
    # Create ports between stages
    @ports = (@stages.size + 1).times.map { Ractor::Port.new }

    # Create Ractors for each stage
    @stages.each_with_index do |stage_fn, i|
      input_port = @ports[i]
      output_port = @ports[i + 1]

      Ractor.new(input_port, output_port, stage_fn) do |inp, out, fn|
        loop do
          data = inp.receive
          break if data == :end
          result = fn.call(data)
          out << result
        end
        out << :end
      end
    end

    self
  end

  def input_port
    @ports.first
  end

  def output_port
    @ports.last
  end

  def process(data)
    input_port << data
    output_port.receive
  end

  def finish
    input_port << :end
  end
end

# Example
pipeline = Pipeline.new
  .add_stage { |x| x.to_s }        # Stage 1: Convert to string
  .add_stage { |x| x.upcase }      # Stage 2: Uppercase
  .add_stage { |x| "<<#{x}>>" }    # Stage 3: Wrap
  .build

result = pipeline.process(42)
puts result #=> "<<42>>"

pipeline.finish
```

## 4. Actor Pattern / 액터 패턴

```ruby
class Actor
  def initialize(&behavior)
    @port = Ractor::Port.new
    @behavior = Ractor.shareable_proc(&behavior)

    @ractor = Ractor.new(@port, @behavior) do |port, behavior|
      state = {}
      loop do
        message = Ractor.receive
        break if message[:type] == :stop

        result = behavior.call(state, message)
        if message[:reply_port]
          message[:reply_port] << result
        end
      end
    end
  end

  def send(message)
    @ractor.send(message)
  end

  def call(message)
    reply_port = Ractor::Port.new
    @ractor.send(message.merge(reply_port: reply_port))
    reply_port.receive
  end

  def stop
    @ractor.send(type: :stop)
  end
end

# Example: Counter Actor
counter = Actor.new do |state, message|
  state[:count] ||= 0

  case message[:type]
  when :increment
    state[:count] += message[:amount] || 1
  when :decrement
    state[:count] -= message[:amount] || 1
  when :get
    state[:count]
  end
end

counter.send(type: :increment, amount: 5)
counter.send(type: :increment)
count = counter.call(type: :get)
puts count #=> 6
counter.stop
```

## 5. Supervisor Pattern / 감독자 패턴

```ruby
class Supervisor
  def initialize
    @workers = {}
    @result_port = Ractor::Port.new
  end

  def spawn(name, &block)
    shareable_fn = Ractor.shareable_proc(&block)
    port = Ractor::Port.new

    worker = Ractor.new(port, @result_port, shareable_fn, name) do |work_port, result_port, fn, worker_name|
      loop do
        begin
          msg = work_port.receive
          break if msg == :shutdown
          result = fn.call(msg)
          result_port << { worker: worker_name, result: result, status: :ok }
        rescue => e
          result_port << { worker: worker_name, error: e.message, status: :error }
        end
      end
    end

    @workers[name] = { ractor: worker, port: port }
  end

  def send_to(name, message)
    @workers[name][:port] << message
  end

  def wait_result
    @result_port.receive
  end

  def restart(name)
    old = @workers[name]
    old[:port] << :shutdown

    # Recreate with same behavior
    # In practice, store the block for recreation
  end

  def shutdown_all
    @workers.each { |_, w| w[:port] << :shutdown }
  end
end

# Usage
supervisor = Supervisor.new

supervisor.spawn(:calculator) { |x| x * 2 }
supervisor.spawn(:formatter) { |x| "Result: #{x}" }

supervisor.send_to(:calculator, 21)
result = supervisor.wait_result
puts result #=> {:worker=>:calculator, :result=>42, :status=>:ok}
```

## 6. Scatter-Gather Pattern / 분산-수집 패턴

```ruby
def scatter_gather(items, worker_count: 4)
  # Scatter
  ports = worker_count.times.map { Ractor::Port.new }
  items.each_with_index do |item, i|
    port = ports[i % worker_count]
    frozen_item = Ractor.make_shareable(item.freeze) rescue item
    Ractor.new(port, frozen_item, i) do |p, data, idx|
      result = yield(data)
      p << { index: idx, result: result }
    end
  end

  # Gather
  results = Array.new(items.size)
  items.size.times do |i|
    port = ports[i % worker_count]
    msg = port.receive
    results[msg[:index]] = msg[:result]
  end

  results
end

# Usage
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
squared = scatter_gather(numbers) { |n| n ** 2 }
puts squared #=> [1, 4, 9, 16, 25, 36, 49, 64]
```

## 7. Batch Processing Pattern / 배치 처리 패턴

```ruby
class BatchProcessor
  def initialize(batch_size: 100, workers: 4)
    @batch_size = batch_size
    @workers = workers
    @result_port = Ractor::Port.new
  end

  def process(items, &block)
    shareable_block = Ractor.shareable_proc(&block)

    # Split into batches
    batches = items.each_slice(@batch_size).to_a

    # Process batches in parallel
    batches.each_slice(@workers) do |batch_group|
      batch_group.each do |batch|
        frozen_batch = Ractor.make_shareable(batch.freeze)
        Ractor.new(@result_port, frozen_batch, shareable_block) do |port, data, fn|
          results = data.map { |item| fn.call(item) }
          port << results
        end
      end
    end

    # Collect all results
    batches.flat_map { @result_port.receive }
  end
end

# Usage
processor = BatchProcessor.new(batch_size: 10, workers: 4)
items = (1..100).to_a

results = processor.process(items) { |x| x * 2 }
puts results.size #=> 100
```

## Performance Tips / 성능 팁

### 1. Minimize Message Copying

```ruby
# ❌ Large objects copied every time
Ractor.new(port, large_array) { |p, arr| ... }

# ✅ Use shareable frozen objects
frozen_array = Ractor.make_shareable(large_array.freeze)
Ractor.new(port, frozen_array) { |p, arr| ... }
```

### 2. Batch Small Operations

```ruby
# ❌ Too many small Ractors
items.each { |i| Ractor.new { process(i) } }

# ✅ Batch operations
items.each_slice(100) do |batch|
  Ractor.new(batch) { |b| b.map { |i| process(i) } }
end
```

### 3. Right Number of Workers

```ruby
# CPU-bound: match CPU cores
worker_count = Etc.nprocessors

# I/O-bound: can exceed core count
# But for I/O, prefer Threads/Fibers over Ractors
```

## See Also / 참고

- [Ractor Overview](INDEX.md)
- [Ractor::Port](port.md)
- [Migration Guide](migration.md)
