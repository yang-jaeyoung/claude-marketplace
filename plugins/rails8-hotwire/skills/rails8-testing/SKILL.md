---
name: rails8-testing
description: RSpec, Factory Bot, 시스템 테스트 가이드
allowed-tools: Read, Glob, Grep
---

# Rails 8 Testing - Testing Skill

## Topics

- RSpec setup and configuration
- Factory Bot factories
- Request specs
- System specs (Capybara)
- Model testing
- Service object testing
- Policy testing
- Test coverage
- Turbo/Stimulus testing

## Quick Start

```bash
# Gemfile
group :development, :test do
  gem "rspec-rails"
  gem "factory_bot_rails"
  gem "faker"
end

group :test do
  gem "capybara"
  gem "cuprite"
  gem "shoulda-matchers"
end

# Install
rails generate rspec:install
```

## Knowledge Reference

For comprehensive documentation, see:
- **[knowledge/testing/SKILL.md](../../knowledge/testing/SKILL.md)**: Full testing patterns, factories, and examples

## Related Agents

- `rspec-tester`: Test writing
- `rspec-tester-low`: Quick test suggestions

## Related Skills

- [rails8-models](../rails8-models/SKILL.md): Model under test
- [rails8-auth](../rails8-auth/SKILL.md): Policy testing
- [rails8-turbo](../rails8-turbo/SKILL.md): Turbo response testing
