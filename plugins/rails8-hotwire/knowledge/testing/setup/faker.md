# Faker for Test Data

## Overview
Faker generates realistic fake data for testing. Prevents hardcoded test values and reduces brittleness from fixture data.

## When to Use
- Generating unique emails, names, addresses in factories
- Creating realistic test content (lorem ipsum, sentences)
- Populating seed data for development
- Avoiding hardcoded test data that causes false positives

## Quick Start
```ruby
# Gemfile
group :development, :test do
  gem "faker"
end

# Usage in factories
FactoryBot.define do
  factory :user do
    name { Faker::Name.name }
    email { Faker::Internet.email }
    phone { Faker::PhoneNumber.phone_number }
  end
end
```

## Main Patterns

### Pattern 1: Common Faker Methods
```ruby
# Names and people
Faker::Name.name          # => "John Doe"
Faker::Name.first_name    # => "John"
Faker::Name.last_name     # => "Doe"
Faker::Name.name_with_middle  # => "John William Doe"

# Internet
Faker::Internet.email     # => "john@example.com"
Faker::Internet.username  # => "johndoe123"
Faker::Internet.password(min_length: 8, max_length: 20)
Faker::Internet.url       # => "http://example.com"
Faker::Internet.domain_name  # => "example.com"
Faker::Internet.slug      # => "foo-bar"

# Addresses
Faker::Address.street_address  # => "123 Main St"
Faker::Address.city            # => "New York"
Faker::Address.state           # => "California"
Faker::Address.zip_code        # => "12345"
Faker::Address.country         # => "United States"

# Lorem (text content)
Faker::Lorem.word          # => "voluptate"
Faker::Lorem.sentence      # => "Voluptate et eos."
Faker::Lorem.paragraph     # => "Voluptate et eos..."
Faker::Lorem.paragraphs(number: 3)
Faker::Lorem.words(number: 5)  # => ["voluptate", "et", ...]

# Numbers
Faker::Number.digit        # => "5"
Faker::Number.number(digits: 10)  # => "1234567890"
Faker::Number.between(from: 1, to: 100)
Faker::Number.decimal(l_digits: 2, r_digits: 2)  # => "12.34"

# Dates
Faker::Date.backward(days: 14)  # 2 weeks ago
Faker::Date.forward(days: 23)   # 3 weeks from now
Faker::Date.between(from: 2.days.ago, to: Date.today)
Faker::Time.backward(days: 14, period: :evening)

# Boolean
Faker::Boolean.boolean  # => true or false

# Company
Faker::Company.name     # => "Acme Corp"
Faker::Company.industry # => "Technology"
Faker::Company.bs       # => "revolutionize scalable solutions"

# Phone
Faker::PhoneNumber.phone_number  # => "555-123-4567"
Faker::PhoneNumber.cell_phone    # => "555-987-6543"
```

### Pattern 2: Sequences with Faker
```ruby
# spec/factories/users.rb
FactoryBot.define do
  factory :user do
    sequence(:email) { |n| "user#{n}@example.com" }
    name { Faker::Name.name }
    bio { Faker::Lorem.paragraph }
    phone { Faker::PhoneNumber.phone_number }
  end
end

# Or use Faker::Internet.unique for guaranteed uniqueness
FactoryBot.define do
  factory :user do
    email { Faker::Internet.unique.email }
    username { Faker::Internet.unique.username }
  end
end
```

### Pattern 3: Locale-Specific Data
```ruby
# Set locale globally
Faker::Config.locale = :es  # Spanish

# Or use locale for specific calls
Faker::Name.name  # => "Juan García"
Faker::Address.city  # => "Madrid"

# Available locales: en, es, fr, de, pt-BR, ja, zh-CN, etc.
```

### Pattern 4: Custom Faker Providers
```ruby
# lib/faker/custom.rb
module Faker
  class CustomProvider < Base
    class << self
      def status
        fetch('custom.status')
      end

      def priority
        sample(['low', 'medium', 'high'])
      end
    end
  end
end

# config/locales/faker.en.yml
en:
  faker:
    custom:
      status:
        - pending
        - active
        - completed
        - archived

# Usage
Faker::CustomProvider.status  # => "pending"
Faker::CustomProvider.priority  # => "high"
```

### Pattern 5: Unique Values
```ruby
# Ensure uniqueness (raises exception after 10,000 attempts)
10.times do
  Faker::Internet.unique.email
end

# Clear unique cache
Faker::Internet.unique.clear

# Use with sequences for guaranteed uniqueness
sequence(:email) { |n| "user#{n}@#{Faker::Internet.domain_name}" }
```

### Pattern 6: Realistic Content for Posts/Articles
```ruby
# spec/factories/posts.rb
FactoryBot.define do
  factory :post do
    user
    title { Faker::Lorem.sentence(word_count: 5, supplemental: true) }
    body { Faker::Lorem.paragraphs(number: 3).join("\n\n") }
    tags { Faker::Lorem.words(number: 3).join(', ') }
    published_at { Faker::Date.backward(days: 30) }
  end

  factory :article do
    author { Faker::Name.name }
    headline { Faker::Lorem.sentence(word_count: 8) }
    content { Faker::Markdown.sandwich(sentences: 10) }
  end
end
```

### Pattern 7: Deterministic Random Data (for CI)
```ruby
# spec/rails_helper.rb or spec/spec_helper.rb
RSpec.configure do |config|
  config.before(:suite) do
    Faker::Config.random = Random.new(12345)  # Seed for reproducibility
  end
end

# Or set seed based on RSpec seed
Faker::Config.random = Random.new(RSpec.configuration.seed)
```

### Pattern 8: File and Image URLs
```ruby
# Files
Faker::File.file_name(dir: 'path/to')  # => "path/to/file.pdf"
Faker::File.extension  # => "pdf"
Faker::File.mime_type  # => "application/pdf"

# Images (placeholder services)
Faker::LoremFlickr.image  # => "https://loremflickr.com/300/300"
Faker::LoremFlickr.image(size: "500x500", search_terms: ['cat'])

# Avatar
Faker::Avatar.image  # => "https://robohash.org/..."
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Not using unique for emails | Duplicate key errors in tests | Use `Faker::Internet.unique.email` or sequences |
| Hardcoding faker calls in specs | Duplicated logic | Define in factories instead |
| Over-relying on Faker for critical tests | Hides edge cases | Mix Faker with explicit edge case values |
| Not seeding random data in CI | Flaky tests | Set deterministic seed via `Faker::Config.random` |

## Related Skills
- [Factory Bot](./factory-bot.md): Test data factories
- [RSpec Setup](./rspec.md): RSpec configuration
- [Model Tests](../types/models.md): Testing models

## References
- [Faker Documentation](https://github.com/faker-ruby/faker)
- [Available Generators](https://github.com/faker-ruby/faker#generators)
- [Locales](https://github.com/faker-ruby/faker#localization)
