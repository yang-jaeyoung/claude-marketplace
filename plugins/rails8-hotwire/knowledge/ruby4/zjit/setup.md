# ZJIT Setup and Configuration / ZJIT 설정

> Complete guide to enabling and configuring ZJIT in Ruby 4.0.
> Ruby 4.0에서 ZJIT를 활성화하고 설정하는 완전 가이드입니다.

## Activation Methods / 활성화 방법

### Method 1: Runtime Activation (Recommended for Development)

```ruby
# config/initializers/zjit.rb (Rails)
if Rails.env.development? || Rails.env.test?
  RubyVM::ZJIT.enable
  Rails.logger.info "ZJIT enabled: #{RubyVM::ZJIT.enabled?}"
end
```

```ruby
# Standalone Ruby application
RubyVM::ZJIT.enable

# Verify activation
puts "ZJIT enabled: #{RubyVM::ZJIT.enabled?}"
```

### Method 2: Command Line Flag

```bash
# Enable ZJIT for a single script
ruby --zjit your_script.rb

# Enable ZJIT for Rails server
bundle exec ruby --zjit bin/rails server

# Enable ZJIT for tests
bundle exec ruby --zjit -S rspec
```

### Method 3: Environment Variable

```bash
# Set for current session
export RUBY_ZJIT_ENABLE=1
ruby your_script.rb

# Set for single command
RUBY_ZJIT_ENABLE=1 bundle exec rails server

# In .bashrc/.zshrc for persistent setting
echo 'export RUBY_ZJIT_ENABLE=1' >> ~/.bashrc
```

### Method 4: Procfile (Heroku/Foreman)

```procfile
# Procfile
web: RUBY_ZJIT_ENABLE=1 bundle exec puma -C config/puma.rb
worker: RUBY_ZJIT_ENABLE=1 bundle exec sidekiq
```

## Configuration Options / 설정 옵션

### Available Options

```ruby
# Currently ZJIT has limited configuration options
# as it's in experimental stage

RubyVM::ZJIT.enable
# No additional configuration options in Ruby 4.0.0
```

### Checking ZJIT Status

```ruby
# Check if ZJIT is enabled
RubyVM::ZJIT.enabled?  #=> true or false

# Get ZJIT statistics (if available)
if RubyVM::ZJIT.respond_to?(:stats)
  puts RubyVM::ZJIT.stats
end
```

## Build Requirements / 빌드 요구사항

### Rust Installation

ZJIT requires Rust 1.85.0 or later for building Ruby from source.

```bash
# Install Rust via rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Update to the latest version
rustup update

# Verify installation
rustc --version
# rustc 1.85.0 (yyyy-mm-dd)
```

### Building Ruby with ZJIT Support

```bash
# Clone Ruby source
git clone https://github.com/ruby/ruby.git
cd ruby

# Configure with ZJIT
./autogen.sh
./configure --enable-zjit

# Build
make -j$(nproc)

# Install
sudo make install
```

## Rails Application Setup / Rails 애플리케이션 설정

### Development Environment

```ruby
# config/environments/development.rb
Rails.application.configure do
  # ... other config ...

  config.after_initialize do
    if ENV['ENABLE_ZJIT'] == '1'
      RubyVM::ZJIT.enable
      Rails.logger.info "ZJIT enabled for development"
    end
  end
end
```

### Using with Spring

```ruby
# config/spring.rb
Spring.after_fork do
  if ENV['ENABLE_ZJIT'] == '1'
    RubyVM::ZJIT.enable
  end
end
```

### Conditional Activation

```ruby
# config/initializers/jit.rb

# Prefer YJIT for production, ZJIT for experimentation
if Rails.env.production?
  # YJIT is more stable for production
  RubyVM::YJIT.enable if defined?(RubyVM::YJIT)
elsif ENV['ENABLE_ZJIT'] == '1'
  # ZJIT for development experimentation
  RubyVM::ZJIT.enable
  Rails.logger.info "ZJIT enabled"
end
```

## Docker Configuration / 도커 설정

```dockerfile
# Dockerfile
FROM ruby:4.0

# Set ZJIT environment variable
ENV RUBY_ZJIT_ENABLE=1

# ... rest of Dockerfile ...
```

```yaml
# docker-compose.yml
services:
  web:
    build: .
    environment:
      - RUBY_ZJIT_ENABLE=1
```

## Verification / 검증

### Ruby Script

```ruby
#!/usr/bin/env ruby
# zjit_check.rb

puts "Ruby version: #{RUBY_VERSION}"

if defined?(RubyVM::ZJIT)
  puts "ZJIT available: yes"
  puts "ZJIT enabled: #{RubyVM::ZJIT.enabled?}"

  # Enable and verify
  RubyVM::ZJIT.enable
  puts "ZJIT enabled after enable call: #{RubyVM::ZJIT.enabled?}"
else
  puts "ZJIT available: no"
end
```

### Rails Console Check

```ruby
# In Rails console
rails console

# Check ZJIT status
RubyVM::ZJIT.enabled?

# Enable if needed
RubyVM::ZJIT.enable
```

## Troubleshooting / 문제 해결

### ZJIT Not Available

```ruby
# Error: undefined method 'enable' for RubyVM::ZJIT
```

**Cause:** Ruby was not built with ZJIT support.

**Solution:** Rebuild Ruby with `--enable-zjit` or use an official Ruby 4.0 build.

### Performance Not Improved

ZJIT is currently slower than YJIT for most workloads. This is expected during the experimental phase.

**Recommendation:** Use YJIT for production workloads until ZJIT matures.

### Memory Usage Increase

ZJIT uses more memory than the interpreter or YJIT.

**Solution:** Monitor memory usage and revert to YJIT if memory constraints are tight.

## Comparison with YJIT Setup / YJIT 설정과 비교

| Aspect | YJIT | ZJIT |
|--------|------|------|
| Enable (runtime) | `RubyVM::YJIT.enable` | `RubyVM::ZJIT.enable` |
| Enable (flag) | `--yjit` | `--zjit` |
| Enable (env) | `RUBY_YJIT_ENABLE=1` | `RUBY_ZJIT_ENABLE=1` |
| Production | ✅ Recommended | ❌ Not recommended |

## See Also / 참고

- [Performance](performance.md) - Benchmark comparisons
- [Rails Integration](rails-integration.md) - Rails-specific patterns
- [ZJIT Overview](INDEX.md) - Feature overview
