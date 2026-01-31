# Ruby 4.0 Ractor::Port Examples
# 루비 4.0 Ractor::Port 예제

# =============================================================================
# BASIC PORT USAGE
# 기본 포트 사용법
# =============================================================================

# Simple message passing
def basic_port_example
  port = Ractor::Port.new

  # Create Ractor that sends to port
  Ractor.new(port) do |p|
    p << "Hello from Ractor!"
  end

  # Receive from port
  message = port.receive
  puts message  #=> "Hello from Ractor!"
end

# =============================================================================
# MULTIPLE MESSAGES
# 다중 메시지
# =============================================================================

def multiple_messages_example
  port = Ractor::Port.new

  Ractor.new(port) do |p|
    5.times do |i|
      p << "Message #{i}"
    end
    p << :done
  end

  loop do
    msg = port.receive
    break if msg == :done
    puts msg
  end
end

# =============================================================================
# BIDIRECTIONAL COMMUNICATION
# 양방향 통신
# =============================================================================

def bidirectional_example
  input_port = Ractor::Port.new
  output_port = Ractor::Port.new

  # Worker Ractor
  worker = Ractor.new(input_port, output_port) do |inp, out|
    loop do
      data = inp.receive
      break if data == :shutdown

      # Process and send result
      result = data * 2
      out << result
    end
    out << :finished
  end

  # Send work
  input_port << 10
  puts "Result: #{output_port.receive}"  #=> 20

  input_port << 21
  puts "Result: #{output_port.receive}"  #=> 42

  # Shutdown
  input_port << :shutdown
  puts output_port.receive  #=> :finished
end

# =============================================================================
# WORKER POOL PATTERN
# 워커 풀 패턴
# =============================================================================

class WorkerPool
  def initialize(size)
    @size = size
    @result_port = Ractor::Port.new
    @workers = create_workers
  end

  def submit(work)
    # Round-robin distribution
    @workers.sample.send(work)
    @result_port.receive
  end

  def parallel_map(items)
    items.each_with_index do |item, i|
      @workers[i % @size].send(item)
    end
    items.map { @result_port.receive }
  end

  def shutdown
    @workers.each { |w| w.send(:shutdown) }
  end

  private

  def create_workers
    @size.times.map do
      Ractor.new(@result_port) do |result_port|
        loop do
          data = Ractor.receive
          break if data == :shutdown

          result = yield_work(data)
          result_port << result
        end
      end
    end
  end

  def yield_work(data)
    # Override in subclass or use block
    data ** 2
  end
end

# Usage:
# pool = WorkerPool.new(4)
# results = pool.parallel_map([1, 2, 3, 4])
# puts results  #=> [1, 4, 9, 16]
# pool.shutdown

# =============================================================================
# PIPELINE PATTERN
# 파이프라인 패턴
# =============================================================================

class Pipeline
  def initialize
    @stages = []
  end

  def add_stage(&processor)
    @stages << Ractor.shareable_proc(&processor)
    self
  end

  def build
    ports = (@stages.size + 1).times.map { Ractor::Port.new }

    @stages.each_with_index do |processor, i|
      input = ports[i]
      output = ports[i + 1]

      Ractor.new(input, output, processor) do |inp, out, proc|
        loop do
          data = inp.receive
          break if data == :end

          result = proc.call(data)
          out << result
        end
        out << :end
      end
    end

    PipelineRunner.new(ports.first, ports.last)
  end

  class PipelineRunner
    def initialize(input, output)
      @input = input
      @output = output
    end

    def process(data)
      @input << data
      @output.receive
    end

    def close
      @input << :end
    end
  end
end

# Usage:
# pipeline = Pipeline.new
#   .add_stage { |x| x.to_s }
#   .add_stage { |x| x.upcase }
#   .add_stage { |x| "<<#{x}>>" }
#   .build
#
# puts pipeline.process(42)  #=> "<<42>>"
# pipeline.close

# =============================================================================
# MAP-REDUCE PATTERN
# 맵-리듀스 패턴
# =============================================================================

module ParallelMapReduce
  def self.map_reduce(data, worker_count: 4, &block)
    mapper, reducer = block.call

    # Convert to shareable procs
    map_fn = Ractor.shareable_proc(&mapper)
    reduce_fn = Ractor.shareable_proc(&reducer)

    # Split data into chunks
    chunk_size = (data.size.to_f / worker_count).ceil
    chunks = data.each_slice(chunk_size).to_a

    # Map phase
    map_port = Ractor::Port.new

    chunks.each do |chunk|
      frozen_chunk = Ractor.make_shareable(chunk.freeze)
      Ractor.new(map_port, frozen_chunk, map_fn) do |port, data, fn|
        results = data.map { |item| fn.call(item) }
        port << results
      end
    end

    # Collect mapped results
    mapped = chunks.size.times.flat_map { map_port.receive }

    # Reduce phase
    reduce_port = Ractor::Port.new
    frozen_mapped = Ractor.make_shareable(mapped.freeze)

    Ractor.new(reduce_port, frozen_mapped, reduce_fn) do |port, data, fn|
      result = data.reduce { |acc, item| fn.call(acc, item) }
      port << result
    end

    reduce_port.receive
  end
end

# Usage:
# numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# result = ParallelMapReduce.map_reduce(numbers) do
#   [
#     ->(x) { x * x },           # mapper
#     ->(acc, x) { acc + x }     # reducer
#   ]
# end
# puts result  #=> 385 (sum of squares)

# =============================================================================
# ACTOR PATTERN
# 액터 패턴
# =============================================================================

class Actor
  def initialize(&behavior)
    @behavior = Ractor.shareable_proc(&behavior)
    @result_port = Ractor::Port.new

    @ractor = Ractor.new(@result_port, @behavior) do |result_port, behavior|
      state = {}
      loop do
        msg = Ractor.receive
        break if msg[:type] == :stop

        result = behavior.call(state, msg)

        if msg[:reply_port]
          msg[:reply_port] << result
        end
      end
    end
  end

  def send(message)
    @ractor.send(message)
    self
  end

  def ask(message)
    reply_port = Ractor::Port.new
    @ractor.send(message.merge(reply_port: reply_port))
    reply_port.receive
  end

  def stop
    @ractor.send(type: :stop)
  end
end

# Usage:
# counter = Actor.new do |state, msg|
#   state[:count] ||= 0
#
#   case msg[:type]
#   when :increment
#     state[:count] += msg[:amount] || 1
#   when :get
#     state[:count]
#   else
#     :unknown
#   end
# end
#
# counter.send(type: :increment, amount: 5)
# counter.send(type: :increment)
# puts counter.ask(type: :get)  #=> 6
# counter.stop

# =============================================================================
# PARALLEL COMPUTATION EXAMPLE
# 병렬 계산 예제
# =============================================================================

def parallel_fibonacci(n, workers: 4)
  return fibonacci(n) if n < 30  # Small numbers: compute directly

  port = Ractor::Port.new

  # Split work
  chunks = workers.times.map { |i| (i * (n / workers))...((i + 1) * (n / workers)) }

  chunks.each do |range|
    Ractor.new(port, range) do |p, r|
      results = r.map { |i| fibonacci(i) }
      p << results
    end
  end

  # Collect
  workers.times.flat_map { port.receive }
end

def fibonacci(n)
  return n if n <= 1
  fibonacci(n - 1) + fibonacci(n - 2)
end

# =============================================================================
# ERROR HANDLING
# 오류 처리
# =============================================================================

def error_handling_example
  port = Ractor::Port.new
  error_port = Ractor::Port.new

  Ractor.new(port, error_port) do |success, errors|
    items = [1, "two", 3, "four", 5]

    items.each do |item|
      begin
        result = item * 2
        success << { value: result, status: :ok }
      rescue => e
        errors << { error: e.message, item: item, status: :error }
      end
    end

    success << :done
    errors << :done
  end

  # Collect successes
  loop do
    msg = port.receive
    break if msg == :done
    puts "Success: #{msg[:value]}" if msg[:status] == :ok
  end

  # Collect errors
  loop do
    msg = error_port.receive
    break if msg == :done
    puts "Error: #{msg[:error]} for #{msg[:item]}" if msg[:status] == :error
  end
end

# =============================================================================
# RUN EXAMPLES
# 예제 실행
# =============================================================================

if __FILE__ == $0
  puts "=" * 60
  puts "Ractor::Port Examples"
  puts "Ruby #{Ruby::VERSION}"
  puts "=" * 60
  puts

  puts "1. Basic Port Example:"
  basic_port_example
  puts

  puts "2. Multiple Messages:"
  multiple_messages_example
  puts

  puts "3. Bidirectional Communication:"
  bidirectional_example
  puts

  puts "4. Error Handling:"
  error_handling_example
  puts

  puts "=" * 60
  puts "Done!"
end
