# ZJIT Performance / ZJIT 성능

> Performance benchmarks and optimization strategies for ZJIT.
> ZJIT의 성능 벤치마크와 최적화 전략입니다.

## Current Performance Status / 현재 성능 상태

As of Ruby 4.0.0, ZJIT is in experimental stage:

```
Interpreter  < ZJIT < YJIT

ZJIT is:
- Faster than the interpreter
- Currently slower than YJIT
- Expected to improve significantly
```

## Benchmark Comparison / 벤치마크 비교

### Synthetic Benchmarks

| Benchmark | Interpreter | YJIT | ZJIT | Notes |
|-----------|-------------|------|------|-------|
| optcarrot | 1.0x | 2.8x | 1.8x | NES emulator |
| liquid | 1.0x | 2.5x | 1.6x | Template engine |
| railsbench | 1.0x | 2.2x | 1.4x | Rails simulation |
| activerecord | 1.0x | 1.8x | 1.3x | ORM operations |

*Note: These are approximate values and may vary by workload.*

### Memory Usage

| Mode | Memory Overhead |
|------|-----------------|
| Interpreter | Baseline |
| YJIT | +50-100MB |
| ZJIT | +100-200MB |

## Running Your Own Benchmarks / 자체 벤치마크 실행

### Basic Benchmark Script

```ruby
# benchmark_jit.rb
require 'benchmark'

def fibonacci(n)
  return n if n <= 1
  fibonacci(n - 1) + fibonacci(n - 2)
end

def array_operations
  arr = (1..10000).to_a
  arr.map { |x| x * 2 }.select { |x| x > 5000 }.sum
end

def string_operations
  str = "hello world " * 1000
  str.upcase.reverse.split.join('-')
end

n = 10

Benchmark.bm(20) do |x|
  x.report("fibonacci(30):") { n.times { fibonacci(30) } }
  x.report("array_operations:") { n.times { array_operations } }
  x.report("string_operations:") { n.times { string_operations } }
end
```

### Running Comparisons

```bash
# Interpreter (no JIT)
echo "=== Interpreter ===" && ruby benchmark_jit.rb

# YJIT
echo "=== YJIT ===" && ruby --yjit benchmark_jit.rb

# ZJIT
echo "=== ZJIT ===" && ruby --zjit benchmark_jit.rb
```

### Rails Benchmark

```ruby
# lib/tasks/benchmark.rake
namespace :benchmark do
  desc "Compare JIT performance"
  task jit: :environment do
    require 'benchmark'

    puts "Ruby #{RUBY_VERSION}"
    puts "YJIT enabled: #{RubyVM::YJIT.enabled?}" if defined?(RubyVM::YJIT)
    puts "ZJIT enabled: #{RubyVM::ZJIT.enabled?}" if defined?(RubyVM::ZJIT)

    n = 100

    Benchmark.bm(25) do |x|
      x.report("User.all (#{User.count}):") do
        n.times { User.all.to_a }
      end

      x.report("User.where:") do
        n.times { User.where(active: true).to_a }
      end

      x.report("User.includes:") do
        n.times { User.includes(:posts).first(10) }
      end
    end
  end
end
```

```bash
# Run benchmark with different JITs
rake benchmark:jit
RUBY_YJIT_ENABLE=1 rake benchmark:jit
RUBY_ZJIT_ENABLE=1 rake benchmark:jit
```

## Optimization Strategies / 최적화 전략

### Code Patterns That Benefit from JIT

```ruby
# ✅ Good for JIT: Tight loops with simple operations
def sum_array(arr)
  total = 0
  arr.each { |x| total += x }
  total
end

# ✅ Good for JIT: Numeric computations
def calculate_discount(price, rate)
  price * (1 - rate / 100.0)
end

# ✅ Good for JIT: String operations
def normalize_name(name)
  name.strip.downcase.gsub(/\s+/, ' ')
end
```

### Patterns That Don't Benefit as Much

```ruby
# ⚠️ I/O bound (JIT doesn't help much)
def fetch_data
  HTTP.get("https://api.example.com/data")
end

# ⚠️ Database bound
def find_users
  User.where(active: true).includes(:posts)
end

# ⚠️ Heavy metaprogramming
def dynamic_method(name)
  define_method(name) { puts name }
end
```

## Warmup Considerations / 워밍업 고려사항

JIT compilers need warmup time to optimize hot code paths.

```ruby
# Warmup script for benchmarking
def warmup(iterations = 1000)
  iterations.times do
    # Run representative workload
    yield
  end
end

# Example usage
warmup(1000) { fibonacci(20) }

# Now benchmark with warmed-up JIT
Benchmark.measure { 100.times { fibonacci(30) } }
```

### Rails Warmup

```ruby
# config/initializers/warmup.rb
if Rails.env.production? && ENV['WARMUP_ON_BOOT']
  Rails.application.config.after_initialize do
    # Warm up common code paths
    100.times do
      User.find_by(id: 1) rescue nil
      Post.where(published: true).limit(1).to_a rescue nil
    end

    Rails.logger.info "Application warmed up"
  end
end
```

## Profiling with ZJIT / ZJIT 프로파일링

### Basic Profiling

```ruby
# profile_script.rb
require 'benchmark'

RubyVM::ZJIT.enable

# Your code here
result = Benchmark.measure do
  # ... workload ...
end

puts result
```

### Memory Profiling

```ruby
# memory_profile.rb
require 'objspace'

def memory_usage
  ObjectSpace.memsize_of_all
end

before = memory_usage
RubyVM::ZJIT.enable
after = memory_usage

puts "Memory increase: #{(after - before) / 1024 / 1024} MB"
```

## When to Use ZJIT vs YJIT / ZJIT와 YJIT 사용 시점

### Use YJIT When:

- Production deployment
- Maximum performance needed now
- Memory constrained environment
- Stability is critical

```ruby
# Production config
RubyVM::YJIT.enable if defined?(RubyVM::YJIT)
```

### Use ZJIT When:

- Experimenting with new features
- Benchmarking for research
- Development/testing environments
- Contributing to Ruby development

```ruby
# Development config
if Rails.env.development? && ENV['ENABLE_ZJIT']
  RubyVM::ZJIT.enable
end
```

## Future Expectations / 향후 전망

ZJIT is expected to improve significantly:

- Better optimization passes
- Reduced memory overhead
- Eventually surpass YJIT performance
- More configuration options

Stay updated with:
- [Ruby ZJIT GitHub](https://github.com/ruby/ruby)
- [Shopify ZJIT Blog](https://railsatscale.com)

## See Also / 참고

- [ZJIT Setup](setup.md) - Configuration options
- [Rails Integration](rails-integration.md) - Rails-specific setup
- [What's New](../overview/whats-new.md) - Ruby 4.0 features
