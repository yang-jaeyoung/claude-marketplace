# ZJIT Rails Integration / Rails 통합

> How to use ZJIT with Rails 8 applications.
> Rails 8 애플리케이션에서 ZJIT를 사용하는 방법입니다.

## Overview / 개요

While ZJIT is experimental and not recommended for production, it can be useful for development, testing, and performance experimentation in Rails applications.

## Development Setup / 개발 환경 설정

### Initializer Configuration

```ruby
# config/initializers/jit.rb

# Development: Allow optional ZJIT for experimentation
if Rails.env.development?
  case ENV['JIT_MODE']
  when 'zjit'
    RubyVM::ZJIT.enable
    Rails.logger.info "ZJIT enabled for development"
  when 'yjit'
    RubyVM::YJIT.enable if defined?(RubyVM::YJIT)
    Rails.logger.info "YJIT enabled for development"
  else
    Rails.logger.info "No JIT enabled (set JIT_MODE=zjit or JIT_MODE=yjit)"
  end
end

# Production: Always use YJIT (stable)
if Rails.env.production?
  RubyVM::YJIT.enable if defined?(RubyVM::YJIT)
end
```

### Procfile.dev

```procfile
# Procfile.dev

# Without JIT
web: bin/rails server -p 3000

# With ZJIT (commented out, enable for testing)
# web: JIT_MODE=zjit bin/rails server -p 3000
```

### bin/dev Script

```bash
#!/bin/bash
# bin/dev-zjit

export JIT_MODE=zjit
exec foreman start -f Procfile.dev
```

## Environment-Based Configuration / 환경별 설정

### config/environments/development.rb

```ruby
Rails.application.configure do
  # ... other configuration ...

  # Optional JIT warmup in development
  config.after_initialize do
    if ENV['JIT_MODE'].present?
      puts "JIT Mode: #{ENV['JIT_MODE']}"
      puts "ZJIT enabled: #{RubyVM::ZJIT.enabled?}" if defined?(RubyVM::ZJIT)
      puts "YJIT enabled: #{RubyVM::YJIT.enabled?}" if defined?(RubyVM::YJIT)
    end
  end
end
```

### config/environments/test.rb

```ruby
Rails.application.configure do
  # ... other configuration ...

  # Allow JIT testing
  config.after_initialize do
    if ENV['JIT_MODE'] == 'zjit' && defined?(RubyVM::ZJIT)
      RubyVM::ZJIT.enable
    end
  end
end
```

## Testing with ZJIT / ZJIT로 테스트

### Running Tests with ZJIT

```bash
# Run all tests with ZJIT
JIT_MODE=zjit bundle exec rspec

# Run specific tests
JIT_MODE=zjit bundle exec rspec spec/models

# Compare with YJIT
JIT_MODE=yjit bundle exec rspec
```

### RSpec Configuration

```ruby
# spec/spec_helper.rb

RSpec.configure do |config|
  config.before(:suite) do
    if ENV['JIT_MODE'].present?
      puts "Running tests with JIT: #{ENV['JIT_MODE']}"
    end
  end
end
```

### Performance Test Helper

```ruby
# spec/support/performance_helper.rb

module PerformanceHelper
  def measure_time(&block)
    start = Process.clock_gettime(Process::CLOCK_MONOTONIC)
    yield
    Process.clock_gettime(Process::CLOCK_MONOTONIC) - start
  end

  def benchmark_operation(name, iterations: 100, &block)
    # Warmup
    10.times { block.call }

    # Measure
    time = measure_time do
      iterations.times { block.call }
    end

    puts "#{name}: #{(time * 1000).round(2)}ms for #{iterations} iterations"
    time
  end
end
```

### Performance Spec

```ruby
# spec/performance/jit_comparison_spec.rb

require 'rails_helper'

RSpec.describe "JIT Performance", type: :performance do
  include PerformanceHelper

  describe "ActiveRecord queries" do
    before do
      # Create test data
      10.times { create(:user, :with_posts) }
    end

    it "benchmarks User.all" do
      benchmark_operation("User.all", iterations: 100) do
        User.all.to_a
      end
    end

    it "benchmarks User.includes(:posts)" do
      benchmark_operation("User.includes(:posts)", iterations: 100) do
        User.includes(:posts).to_a
      end
    end
  end

  describe "View rendering" do
    let(:users) { create_list(:user, 10) }

    it "benchmarks partial rendering" do
      benchmark_operation("render users", iterations: 50) do
        ApplicationController.render(
          partial: 'users/user',
          collection: users
        )
      end
    end
  end
end
```

## Puma Configuration / Puma 설정

### config/puma.rb

```ruby
# config/puma.rb

# Enable JIT in forked workers
on_worker_fork do
  if ENV['JIT_MODE'] == 'zjit' && defined?(RubyVM::ZJIT)
    RubyVM::ZJIT.enable
  end
end

# Log JIT status
after_worker_fork do
  if defined?(RubyVM::ZJIT) && RubyVM::ZJIT.enabled?
    puts "[Worker #{Process.pid}] ZJIT enabled"
  end
end
```

## Docker Setup / 도커 설정

### Dockerfile

```dockerfile
FROM ruby:4.0-slim

# ... base setup ...

# Set JIT mode (default to yjit for production)
ARG JIT_MODE=yjit
ENV JIT_MODE=$JIT_MODE

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

# Different CMD based on JIT mode
CMD ["./bin/rails", "server", "-b", "0.0.0.0"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - JIT_MODE=yjit  # Production default

  web-zjit:
    build: .
    ports:
      - "3001:3000"
    environment:
      - JIT_MODE=zjit  # For testing
    profiles:
      - testing
```

### Running with ZJIT in Docker

```bash
# Normal (YJIT)
docker-compose up web

# With ZJIT for testing
docker-compose --profile testing up web-zjit
```

## Monitoring JIT in Rails / Rails에서 JIT 모니터링

### Health Check Endpoint

```ruby
# app/controllers/health_controller.rb
class HealthController < ApplicationController
  def show
    render json: {
      status: 'ok',
      ruby_version: RUBY_VERSION,
      jit: jit_status
    }
  end

  private

  def jit_status
    {
      yjit_available: defined?(RubyVM::YJIT),
      yjit_enabled: defined?(RubyVM::YJIT) && RubyVM::YJIT.enabled?,
      zjit_available: defined?(RubyVM::ZJIT),
      zjit_enabled: defined?(RubyVM::ZJIT) && RubyVM::ZJIT.enabled?
    }
  end
end
```

### Rake Task for JIT Status

```ruby
# lib/tasks/jit.rake

namespace :jit do
  desc "Show JIT status"
  task status: :environment do
    puts "Ruby Version: #{RUBY_VERSION}"
    puts ""
    puts "YJIT:"
    puts "  Available: #{defined?(RubyVM::YJIT) ? 'Yes' : 'No'}"
    if defined?(RubyVM::YJIT)
      puts "  Enabled: #{RubyVM::YJIT.enabled?}"
    end
    puts ""
    puts "ZJIT:"
    puts "  Available: #{defined?(RubyVM::ZJIT) ? 'Yes' : 'No'}"
    if defined?(RubyVM::ZJIT)
      puts "  Enabled: #{RubyVM::ZJIT.enabled?}"
    end
  end

  desc "Enable ZJIT and show status"
  task enable_zjit: :environment do
    if defined?(RubyVM::ZJIT)
      RubyVM::ZJIT.enable
      puts "ZJIT enabled: #{RubyVM::ZJIT.enabled?}"
    else
      puts "ZJIT not available in this Ruby build"
    end
  end
end
```

## Best Practices / 모범 사례

### 1. Never Use ZJIT in Production

```ruby
# ❌ Wrong
if Rails.env.production?
  RubyVM::ZJIT.enable
end

# ✅ Correct
if Rails.env.production?
  RubyVM::YJIT.enable if defined?(RubyVM::YJIT)
end
```

### 2. Make JIT Optional in Development

```ruby
# ✅ Let developers choose
if ENV['ENABLE_ZJIT'] == '1' && defined?(RubyVM::ZJIT)
  RubyVM::ZJIT.enable
end
```

### 3. Log JIT Status on Boot

```ruby
# ✅ Good for debugging
Rails.application.config.after_initialize do
  Rails.logger.info "JIT Status:"
  Rails.logger.info "  YJIT: #{defined?(RubyVM::YJIT) && RubyVM::YJIT.enabled?}"
  Rails.logger.info "  ZJIT: #{defined?(RubyVM::ZJIT) && RubyVM::ZJIT.enabled?}"
end
```

## See Also / 참고

- [ZJIT Overview](INDEX.md)
- [ZJIT Setup](setup.md)
- [Performance](performance.md)
- [Rails Compatibility](../overview/compatibility.md)
