# Ruby Module / Ruby 모듈

> Ruby 4.0 introduces a new top-level `Ruby` module for version and platform information.
> Ruby 4.0은 버전 및 플랫폼 정보를 위한 새로운 최상위 `Ruby` 모듈을 도입합니다.

## Overview / 개요

The new `Ruby` module provides a cleaner, more organized way to access Ruby version and platform information.

## Ruby Module Constants / Ruby 모듈 상수

### Ruby::VERSION

```ruby
Ruby::VERSION
#=> "4.0.0"

# Compare versions
if Gem::Version.new(Ruby::VERSION) >= Gem::Version.new("4.0.0")
  puts "Running Ruby 4.0+"
end
```

### Ruby::RELEASE_DATE

```ruby
Ruby::RELEASE_DATE
#=> "2025-12-25"
```

### Ruby::PLATFORM

```ruby
Ruby::PLATFORM
#=> "x86_64-darwin24"       # macOS Intel
#=> "arm64-darwin24"        # macOS Apple Silicon
#=> "x86_64-linux"          # Linux
#=> "x86_64-mingw32"        # Windows
```

### Ruby::DESCRIPTION

```ruby
Ruby::DESCRIPTION
#=> "ruby 4.0.0 (2025-12-25 revision abc123) [x86_64-darwin24]"
```

## Comparison with Legacy Constants / 레거시 상수와 비교

| Legacy | New (Ruby 4.0) | Notes |
|--------|----------------|-------|
| `RUBY_VERSION` | `Ruby::VERSION` | Still available |
| `RUBY_RELEASE_DATE` | `Ruby::RELEASE_DATE` | Still available |
| `RUBY_PLATFORM` | `Ruby::PLATFORM` | Still available |
| `RUBY_DESCRIPTION` | `Ruby::DESCRIPTION` | Still available |

### Backward Compatibility

```ruby
# Both old and new work in Ruby 4.0
RUBY_VERSION      #=> "4.0.0"
Ruby::VERSION     #=> "4.0.0"

# They are equal
RUBY_VERSION == Ruby::VERSION  #=> true
```

## Usage Examples / 사용 예제

### Version Checking

```ruby
# Simple version check
if Ruby::VERSION >= "4.0.0"
  # Use Ruby 4.0 features
end

# More robust version comparison
require 'rubygems'

ruby_version = Gem::Version.new(Ruby::VERSION)

if ruby_version >= Gem::Version.new("4.0.0")
  puts "Ruby 4.0+ features available"
elsif ruby_version >= Gem::Version.new("3.2.0")
  puts "Ruby 3.2+ features available"
end
```

### Platform Detection

```ruby
case Ruby::PLATFORM
when /darwin/
  puts "Running on macOS"
when /linux/
  puts "Running on Linux"
when /mingw|mswin/
  puts "Running on Windows"
else
  puts "Unknown platform: #{Ruby::PLATFORM}"
end
```

### In Rails Applications

```ruby
# config/initializers/ruby_info.rb

Rails.logger.info "Ruby #{Ruby::VERSION} on #{Ruby::PLATFORM}"

# Enable features based on Ruby version
if Gem::Version.new(Ruby::VERSION) >= Gem::Version.new("4.0.0")
  # Enable ZJIT in development
  if Rails.env.development? && ENV['ENABLE_ZJIT']
    RubyVM::ZJIT.enable
  end
end
```

### Gemspec Version Requirements

```ruby
# my_gem.gemspec
Gem::Specification.new do |spec|
  spec.name = "my_gem"
  spec.version = "1.0.0"

  # Require Ruby 4.0+
  spec.required_ruby_version = ">= 4.0.0"

  # Or support range
  spec.required_ruby_version = ">= 3.2.0", "< 5.0.0"
end
```

### Health Check Endpoint

```ruby
# app/controllers/health_controller.rb
class HealthController < ApplicationController
  def show
    render json: {
      status: 'ok',
      ruby: {
        version: Ruby::VERSION,
        platform: Ruby::PLATFORM,
        release_date: Ruby::RELEASE_DATE
      },
      rails: {
        version: Rails::VERSION::STRING
      }
    }
  end
end
```

### Conditional Feature Loading

```ruby
# lib/features.rb
module Features
  def self.zjit_available?
    defined?(RubyVM::ZJIT) &&
    Gem::Version.new(Ruby::VERSION) >= Gem::Version.new("4.0.0")
  end

  def self.ruby_box_available?
    defined?(Ruby::Box) &&
    Gem::Version.new(Ruby::VERSION) >= Gem::Version.new("4.0.0")
  end

  def self.ractor_port_available?
    defined?(Ractor::Port) &&
    Gem::Version.new(Ruby::VERSION) >= Gem::Version.new("4.0.0")
  end
end

# Usage
if Features.zjit_available? && Rails.env.development?
  RubyVM::ZJIT.enable
end
```

## Module Inspection / 모듈 검사

```ruby
# List all constants in Ruby module
Ruby.constants
#=> [:VERSION, :RELEASE_DATE, :PLATFORM, :DESCRIPTION, ...]

# Check if Ruby module exists (for conditional code)
if defined?(Ruby) && defined?(Ruby::VERSION)
  puts "Ruby module available"
end
```

## Why This Change? / 이 변경의 이유

### 1. Namespace Organization

```ruby
# Before: Global constants
RUBY_VERSION
RUBY_PLATFORM
RUBY_DESCRIPTION

# After: Organized under Ruby module
Ruby::VERSION
Ruby::PLATFORM
Ruby::DESCRIPTION
```

### 2. Future Extensibility

The `Ruby` module can hold additional functionality:

```ruby
# Potential future additions
Ruby::FEATURES     # Feature flags
Ruby::BUILD_INFO   # Build configuration
Ruby::Box          # Already added in 4.0
```

### 3. Consistency

Follows the pattern of other language modules:

```ruby
Ruby::VERSION    # Like...
Rails::VERSION   # In Rails
Gem::VERSION     # In RubyGems
```

## Best Practices / 모범 사례

### Prefer New Style in New Code

```ruby
# ✅ Recommended for new code
Ruby::VERSION
Ruby::PLATFORM

# ⚠️ Still works, but consider updating
RUBY_VERSION
RUBY_PLATFORM
```

### Use Gem::Version for Comparisons

```ruby
# ❌ String comparison can be wrong
Ruby::VERSION >= "4.0.0"  # "4.10.0" < "4.9.0" as strings!

# ✅ Use Gem::Version
Gem::Version.new(Ruby::VERSION) >= Gem::Version.new("4.0.0")
```

### Document Ruby Version Requirements

```ruby
# In your code
# Requires Ruby 4.0+ for Ruby::Box support
raise "Ruby 4.0+ required" unless Gem::Version.new(Ruby::VERSION) >= Gem::Version.new("4.0.0")
```

## See Also / 참고

- [Set and Pathname](set-pathname.md)
- [Language Changes](language-changes.md)
- [What's New in Ruby 4.0](../overview/whats-new.md)
