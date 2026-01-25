# RSpec Rails Setup

## Overview
RSpec-Rails is the standard testing framework for Rails applications. Provides spec runners, generators, and Rails-specific matchers.

## When to Use
- Setting up testing infrastructure for a new Rails app
- Configuring test helpers and shared contexts
- Integrating with Factory Bot, Shoulda Matchers, and other testing gems

## Quick Start
```bash
# Gemfile
group :development, :test do
  gem "rspec-rails", "~> 6.1"
  gem "factory_bot_rails"
  gem "faker"
end

group :test do
  gem "shoulda-matchers", "~> 6.0"
  gem "capybara"
  gem "cuprite"  # Faster Chrome driver
end

bundle install
rails generate rspec:install
```

## Main Patterns

### Pattern 1: rails_helper.rb Configuration
```ruby
# spec/rails_helper.rb
require 'spec_helper'
ENV['RAILS_ENV'] ||= 'test'
require_relative '../config/environment'
abort("The Rails environment is running in production mode!") if Rails.env.production?
require 'rspec/rails'

# Auto-load support files
Dir[Rails.root.join('spec', 'support', '**', '*.rb')].sort.each { |f| require f }

# Prevent database truncation if migrations are pending
begin
  ActiveRecord::Migration.maintain_test_schema!
rescue ActiveRecord::PendingMigrationError => e
  abort e.to_s.strip
end

RSpec.configure do |config|
  # Database cleaner setup (transaction strategy by default)
  config.fixture_path = Rails.root.join('spec/fixtures')
  config.use_transactional_fixtures = true

  # Auto-detect spec type from file location
  config.infer_spec_type_from_file_location!

  # Filter Rails frames from backtrace
  config.filter_rails_from_backtrace!

  # Include Factory Bot methods (create, build, etc.)
  config.include FactoryBot::Syntax::Methods

  # Include authentication helpers
  config.include Devise::Test::IntegrationHelpers, type: :request
  config.include Devise::Test::IntegrationHelpers, type: :system
end

# Shoulda Matchers configuration
Shoulda::Matchers.configure do |config|
  config.integrate do |with|
    with.test_framework :rspec
    with.library :rails
  end
end
```

### Pattern 2: .rspec Configuration
```ruby
# .rspec
--require spec_helper
--format documentation
--color
--order random
--profile 10
```

### Pattern 3: spec_helper.rb
```ruby
# spec/spec_helper.rb
RSpec.configure do |config|
  # Use expect syntax only (not should)
  config.expect_with :rspec do |expectations|
    expectations.include_chain_clauses_in_custom_matcher_descriptions = true
    expectations.syntax = :expect
  end

  # Mock configuration
  config.mock_with :rspec do |mocks|
    mocks.verify_partial_doubles = true
  end

  # Shared context metadata behavior
  config.shared_context_metadata_behavior = :apply_to_host_groups

  # Filter lines from backtraces
  config.filter_run_when_matching :focus
  config.example_status_persistence_file_path = "spec/examples.txt"
  config.disable_monkey_patching!

  # Run specs in random order
  config.order = :random
  Kernel.srand config.seed

  # Profile slow examples
  config.profile_examples = 10
end
```

### Pattern 4: Support Files for Shared Helpers
```ruby
# spec/support/devise.rb
RSpec.configure do |config|
  config.include Devise::Test::IntegrationHelpers, type: :request
  config.include Devise::Test::IntegrationHelpers, type: :system
  config.include Warden::Test::Helpers
end

# spec/support/capybara.rb
require 'capybara/cuprite'

Capybara.register_driver :cuprite do |app|
  Capybara::Cuprite::Driver.new(app, {
    window_size: [1400, 1400],
    browser_options: { 'no-sandbox' => nil },
    process_timeout: 10,
    timeout: 5,
    js_errors: true,
    headless: !ENV['HEADLESS'].in?(['n', 'no', '0', 'false'])
  })
end

Capybara.default_driver = :cuprite
Capybara.javascript_driver = :cuprite

# spec/support/database_cleaner.rb
RSpec.configure do |config|
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

# spec/support/shoulda_matchers.rb
Shoulda::Matchers.configure do |config|
  config.integrate do |with|
    with.test_framework :rspec
    with.library :rails
  end
end
```

### Pattern 5: Generators Configuration
```ruby
# config/application.rb
module MyApp
  class Application < Rails::Application
    config.generators do |g|
      g.test_framework :rspec,
        fixtures: false,
        view_specs: false,
        helper_specs: false,
        routing_specs: false,
        request_specs: true,
        controller_specs: false
      g.fixture_replacement :factory_bot, dir: 'spec/factories'
    end
  end
end
```

### Pattern 6: Running RSpec
```bash
# All specs
bundle exec rspec

# Specific file
bundle exec rspec spec/models/user_spec.rb

# Specific line
bundle exec rspec spec/models/user_spec.rb:25

# Run only tests with :focus tag
bundle exec rspec --tag focus

# Exclude slow tests
bundle exec rspec --tag ~slow

# Run in random order with seed
bundle exec rspec --order random --seed 1234

# Format as documentation
bundle exec rspec --format documentation

# Profile slowest 20 examples
bundle exec rspec --profile 20

# Parallel execution (with parallel_tests gem)
bundle exec parallel_rspec spec/
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Using `should` syntax | Deprecated, conflicts with shoulda-matchers | Use `expect().to` syntax only |
| Not randomizing test order | Hidden dependencies between tests | Always run with `--order random` |
| Including all support files globally | Slower load times | Use spec type detection or manual includes |
| Using fixture files | Hard to maintain, slow | Use Factory Bot instead |
| Not filtering Rails backtrace | Verbose error messages | Enable `filter_rails_from_backtrace!` |

## Related Skills
- [Factory Bot](./factory-bot.md): Test data creation
- [Faker](./faker.md): Random test data
- [Database Cleaner](./database-cleaner.md): Database cleanup strategies

## References
- [RSpec Rails](https://github.com/rspec/rspec-rails)
- [Better Specs](https://www.betterspecs.org/)
- [RSpec Documentation](https://rspec.info/)
