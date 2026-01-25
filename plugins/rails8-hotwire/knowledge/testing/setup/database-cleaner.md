# Database Cleaner Strategies

## Overview
Database Cleaner provides strategies for cleaning test databases between test runs. Ensures test isolation and prevents state leakage.

## When to Use
- Configuring database cleanup for RSpec
- Handling system/feature tests that require truncation
- Working with multiple databases
- Debugging test pollution issues

## Quick Start
```ruby
# Gemfile
group :test do
  gem "database_cleaner-active_record"
end

# spec/rails_helper.rb
RSpec.configure do |config|
  config.use_transactional_fixtures = false

  config.before(:suite) do
    DatabaseCleaner.clean_with(:truncation)
  end

  config.before(:each) do
    DatabaseCleaner.strategy = :transaction
  end

  config.before(:each, type: :system) do
    DatabaseCleaner.strategy = :truncation
  end

  config.before(:each) do
    DatabaseCleaner.start
  end

  config.after(:each) do
    DatabaseCleaner.clean
  end
end
```

## Main Patterns

### Pattern 1: Transaction Strategy (Default)
```ruby
# Fastest strategy - wraps each test in a transaction and rolls back
RSpec.configure do |config|
  config.before(:each) do
    DatabaseCleaner.strategy = :transaction
    DatabaseCleaner.start
  end

  config.after(:each) do
    DatabaseCleaner.clean
  end
end

# Use for: Unit tests, request tests, most specs
# Pros: Fast, automatic rollback
# Cons: Doesn't work with system tests (JS-driven), multi-threaded scenarios
```

### Pattern 2: Truncation Strategy
```ruby
# Slower but works across threads/processes
RSpec.configure do |config|
  config.before(:each, type: :system) do
    DatabaseCleaner.strategy = :truncation
    DatabaseCleaner.start
  end

  config.after(:each, type: :system) do
    DatabaseCleaner.clean
  end
end

# Use for: System tests, feature tests with JavaScript
# Pros: Works across threads, cleans entire database
# Cons: Slower than transactions
```

### Pattern 3: Deletion Strategy
```ruby
# Similar to truncation but uses DELETE instead of TRUNCATE
RSpec.configure do |config|
  config.before(:each, type: :system) do
    DatabaseCleaner.strategy = :deletion
    DatabaseCleaner.start
  end
end

# Use for: When TRUNCATE causes issues (foreign key constraints, permissions)
# Pros: More compatible than truncation
# Cons: Slower than truncation
```

### Pattern 4: Combined Strategy (Transaction + Truncation)
```ruby
# spec/support/database_cleaner.rb
RSpec.configure do |config|
  # Disable transactional fixtures (conflicts with DatabaseCleaner)
  config.use_transactional_fixtures = false

  config.before(:suite) do
    DatabaseCleaner.clean_with(:truncation)
  end

  config.before(:each) do
    DatabaseCleaner.strategy = :transaction
  end

  # Use truncation for system tests
  config.before(:each, type: :system) do
    DatabaseCleaner.strategy = :truncation
  end

  # Use truncation for JS-enabled tests
  config.before(:each, js: true) do
    DatabaseCleaner.strategy = :truncation
  end

  config.before(:each) do
    DatabaseCleaner.start
  end

  config.append_after(:each) do
    DatabaseCleaner.clean
  end
end
```

### Pattern 5: Multiple Databases
```ruby
# spec/support/database_cleaner.rb
RSpec.configure do |config|
  config.before(:suite) do
    DatabaseCleaner[:active_record, db: :primary].clean_with(:truncation)
    DatabaseCleaner[:active_record, db: :analytics].clean_with(:truncation)
  end

  config.before(:each) do
    DatabaseCleaner[:active_record, db: :primary].strategy = :transaction
    DatabaseCleaner[:active_record, db: :analytics].strategy = :transaction
  end

  config.before(:each, type: :system) do
    DatabaseCleaner[:active_record, db: :primary].strategy = :truncation
    DatabaseCleaner[:active_record, db: :analytics].strategy = :truncation
  end

  config.before(:each) do
    DatabaseCleaner[:active_record, db: :primary].start
    DatabaseCleaner[:active_record, db: :analytics].start
  end

  config.append_after(:each) do
    DatabaseCleaner[:active_record, db: :primary].clean
    DatabaseCleaner[:active_record, db: :analytics].clean
  end
end
```

### Pattern 6: Excluding Tables from Truncation
```ruby
# Preserve reference data or spatial tables
RSpec.configure do |config|
  config.before(:suite) do
    DatabaseCleaner.clean_with(:truncation, except: %w[spatial_ref_sys])
  end

  config.before(:each, type: :system) do
    DatabaseCleaner.strategy = :truncation, { except: %w[countries states] }
  end
end
```

### Pattern 7: Custom Cleaning (Pre/Post Hooks)
```ruby
RSpec.configure do |config|
  config.before(:each) do
    DatabaseCleaner.strategy = :transaction
    DatabaseCleaner.start
  end

  config.after(:each) do
    DatabaseCleaner.clean
  end

  # Additional cleanup for Redis, Elasticsearch, etc.
  config.after(:each) do
    Redis.current.flushdb
    Post.__elasticsearch__.refresh_index!
  end
end
```

### Pattern 8: Rails 7.1+ Multi-DB with Transactions
```ruby
# Rails 7.1+ supports transactional fixtures across multiple DBs
RSpec.configure do |config|
  config.use_transactional_fixtures = true

  # No DatabaseCleaner needed for simple multi-DB setups
  # Rails handles transactions across all configured databases
end

# Only use DatabaseCleaner if you need truncation for system tests
```

## Strategy Comparison

| Strategy | Speed | Use Case | Thread Safe |
|----------|-------|----------|-------------|
| Transaction | Fastest | Unit, request specs | No |
| Truncation | Slow | System specs (JS) | Yes |
| Deletion | Medium | Foreign key issues | Yes |

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Using `transactional_fixtures = true` with DatabaseCleaner | Conflicts, tests fail | Disable transactional fixtures |
| Using transaction strategy for system tests | Database not shared across threads | Use truncation for system specs |
| Not cleaning before suite | Stale data from previous runs | Add `clean_with(:truncation)` in `before(:suite)` |
| Truncating all tables for every test | Slow test suite | Only truncate for system/JS tests |
| Hardcoding database names | Breaks on rename | Use Rails database config |

## Related Skills
- [RSpec Setup](./rspec.md): RSpec configuration
- [System Tests](../types/system.md): Capybara setup
- [Factory Bot](./factory-bot.md): Test data creation

## References
- [Database Cleaner](https://github.com/DatabaseCleaner/database_cleaner)
- [DatabaseCleaner Active Record](https://github.com/DatabaseCleaner/database_cleaner-active_record)
- [Rails Testing Guide](https://guides.rubyonrails.org/testing.html)
