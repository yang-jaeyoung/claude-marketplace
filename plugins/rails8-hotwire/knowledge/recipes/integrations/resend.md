# ${file^} Integration

## Overview

Production integration with ${file^} for Rails 8 applications.

## Prerequisites

- [background/solid-queue](../../background/solid-queue.md)
- [auth/devise](../../auth/devise.md)

## Quick Start

```ruby
gem "${file}-ruby"
bundle install
```

## Implementation

### Configuration

```ruby
# config/initializers/${file}.rb
${file^}.configure do |config|
  config.api_key = Rails.application.credentials.dig(:${file}, :api_key)
end
```

### Usage

```ruby
# app/services/${file}_service.rb
class ${file^}Service
  def initialize
    @client = ${file^}::Client.new
  end

  def call
    # Implementation specific to service
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Hardcoded API keys | Security risk | Use Rails credentials |
| Synchronous API calls | Slow requests | Use background jobs |
| No error handling | Silent failures | Rescue API errors |

## Related Skills

- [background/solid-queue](../../background/solid-queue.md)
- [auth/devise](../../auth/devise.md)

## References

- [${file^} Documentation](https://${file}.com/docs)
