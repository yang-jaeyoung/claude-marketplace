# Mocking and Stubbing

## Overview
Mocking external dependencies, stubbing method returns, and recording HTTP interactions with VCR and WebMock.

## When to Use
- Isolating tests from external services (APIs, payment gateways)
- Speeding up tests by avoiding network calls
- Testing error conditions (timeouts, API failures)
- Ensuring deterministic test behavior

## Quick Start
```ruby
# Gemfile
group :test do
  gem "webmock"
  gem "vcr"
end

# Simple stubbing
allow(User).to receive(:find).and_return(user)

# HTTP stubbing
stub_request(:get, "https://api.example.com/users/1")
  .to_return(status: 200, body: { name: "John" }.to_json)
```

## Main Patterns

### Pattern 1: RSpec Mocks and Stubs
```ruby
# spec/services/notification_service_spec.rb
require 'rails_helper'

RSpec.describe NotificationService do
  let(:user) { create(:user) }
  let(:mailer) { double('Mailer') }

  describe '#notify' do
    it 'sends email notification' do
      # Create a test double
      allow(UserMailer).to receive(:notification).and_return(mailer)
      allow(mailer).to receive(:deliver_later)

      NotificationService.new(user).notify

      # Verify method was called
      expect(UserMailer).to have_received(:notification).with(user)
      expect(mailer).to have_received(:deliver_later)
    end

    it 'handles delivery errors gracefully' do
      allow(UserMailer).to receive(:notification).and_raise(Net::SMTPServerBusy)

      expect {
        NotificationService.new(user).notify
      }.not_to raise_error
    end
  end
end
```

### Pattern 2: Stubbing Instance Methods
```ruby
# spec/models/user_spec.rb
require 'rails_helper'

RSpec.describe User, type: :model do
  describe '#premium?' do
    it 'checks subscription status' do
      user = build_stubbed(:user)
      subscription = double('Subscription', active?: true, premium?: true)

      allow(user).to receive(:subscription).and_return(subscription)

      expect(user).to be_premium
    end
  end

  describe '#full_name' do
    it 'combines first and last name' do
      user = build_stubbed(:user)

      # Stub attribute readers
      allow(user).to receive(:first_name).and_return('John')
      allow(user).to receive(:last_name).and_return('Doe')

      expect(user.full_name).to eq('John Doe')
    end
  end
end
```

### Pattern 3: Stubbing Class Methods
```ruby
# spec/services/weather_service_spec.rb
require 'rails_helper'

RSpec.describe WeatherService do
  describe '.fetch' do
    it 'fetches weather data from API' do
      weather_data = { temp: 72, conditions: 'sunny' }

      # Stub class method
      allow(HTTParty).to receive(:get)
        .with('https://api.weather.com/current')
        .and_return(double(success?: true, parsed_response: weather_data))

      result = WeatherService.fetch

      expect(result[:temp]).to eq(72)
    end
  end
end
```

### Pattern 4: WebMock for HTTP Requests
```ruby
# spec/support/webmock.rb
require 'webmock/rspec'

WebMock.disable_net_connect!(allow_localhost: true)

# spec/services/github_service_spec.rb
require 'rails_helper'

RSpec.describe GithubService do
  describe '.fetch_repos' do
    let(:username) { 'testuser' }
    let(:api_url) { "https://api.github.com/users/#{username}/repos" }

    context 'when API returns success' do
      before do
        stub_request(:get, api_url)
          .to_return(
            status: 200,
            body: [
              { name: 'repo1', stars: 10 },
              { name: 'repo2', stars: 20 }
            ].to_json,
            headers: { 'Content-Type' => 'application/json' }
          )
      end

      it 'returns repository names' do
        repos = GithubService.fetch_repos(username)
        expect(repos.map { |r| r['name'] }).to eq(['repo1', 'repo2'])
      end
    end

    context 'when API returns 404' do
      before do
        stub_request(:get, api_url).to_return(status: 404)
      end

      it 'handles not found error' do
        expect {
          GithubService.fetch_repos(username)
        }.to raise_error(GithubService::NotFoundError)
      end
    end

    context 'when network timeout occurs' do
      before do
        stub_request(:get, api_url).to_timeout
      end

      it 'raises timeout error' do
        expect {
          GithubService.fetch_repos(username)
        }.to raise_error(Net::OpenTimeout)
      end
    end

    context 'with request headers' do
      before do
        stub_request(:get, api_url)
          .with(headers: { 'Authorization' => 'Bearer token123' })
          .to_return(status: 200, body: '[]')
      end

      it 'includes authorization header' do
        GithubService.fetch_repos(username, token: 'token123')

        expect(a_request(:get, api_url)
          .with(headers: { 'Authorization' => 'Bearer token123' }))
          .to have_been_made.once
      end
    end
  end
end
```

### Pattern 5: VCR for Recording HTTP Interactions
```ruby
# spec/support/vcr.rb
require 'vcr'

VCR.configure do |config|
  config.cassette_library_dir = 'spec/fixtures/vcr_cassettes'
  config.hook_into :webmock
  config.configure_rspec_metadata!
  config.ignore_localhost = true

  # Filter sensitive data
  config.filter_sensitive_data('<API_KEY>') { ENV['API_KEY'] }
  config.filter_sensitive_data('<AUTH_TOKEN>') { ENV['AUTH_TOKEN'] }

  # Allow real requests in development
  config.allow_http_connections_when_no_cassette = false
end

# spec/services/stripe_service_spec.rb
require 'rails_helper'

RSpec.describe StripeService, :vcr do
  describe '.create_charge' do
    it 'creates a charge in Stripe' do
      VCR.use_cassette('stripe/create_charge') do
        result = StripeService.create_charge(
          amount: 1000,
          currency: 'usd',
          source: 'tok_visa'
        )

        expect(result.status).to eq('succeeded')
      end
    end
  end

  # Use metadata for automatic cassette naming
  it 'processes refund', vcr: { cassette_name: 'stripe/refund' } do
    result = StripeService.refund(charge_id: 'ch_123')
    expect(result.status).to eq('succeeded')
  end
end

# Re-record cassettes
# VCR_RECORD_MODE=all bundle exec rspec
```

### Pattern 6: Partial Stubbing (Spy Pattern)
```ruby
# spec/services/order_processor_spec.rb
require 'rails_helper'

RSpec.describe OrderProcessor do
  let(:order) { create(:order) }

  describe '#process' do
    it 'calls payment gateway and sends confirmation' do
      processor = OrderProcessor.new(order)

      # Allow real implementation but track calls
      allow(processor).to receive(:charge_payment).and_call_original
      allow(processor).to receive(:send_confirmation).and_call_original

      processor.process

      expect(processor).to have_received(:charge_payment)
      expect(processor).to have_received(:send_confirmation)
    end

    it 'does not send confirmation if payment fails' do
      processor = OrderProcessor.new(order)

      allow(processor).to receive(:charge_payment).and_return(false)
      spy_on_confirmation = allow(processor).to receive(:send_confirmation)

      processor.process

      expect(spy_on_confirmation).not_to have_received(:send_confirmation)
    end
  end
end
```

### Pattern 7: Stubbing Time and Dates
```ruby
# spec/models/subscription_spec.rb
require 'rails_helper'

RSpec.describe Subscription, type: :model do
  describe '#expired?' do
    let(:subscription) { build(:subscription, expires_at: 1.month.from_now) }

    it 'returns false when not expired' do
      freeze_time do
        expect(subscription).not_to be_expired
      end
    end

    it 'returns true when expired' do
      travel_to 2.months.from_now do
        expect(subscription).to be_expired
      end
    end

    it 'handles edge case at exact expiration time' do
      travel_to subscription.expires_at do
        expect(subscription).to be_expired
      end
    end
  end

  describe '.expiring_soon' do
    it 'returns subscriptions expiring in next 7 days' do
      freeze_time do
        expiring = create(:subscription, expires_at: 5.days.from_now)
        not_expiring = create(:subscription, expires_at: 10.days.from_now)

        expect(Subscription.expiring_soon).to include(expiring)
        expect(Subscription.expiring_soon).not_to include(not_expiring)
      end
    end
  end
end
```

### Pattern 8: Mocking External Services with Test Doubles
```ruby
# spec/services/payment_service_spec.rb
require 'rails_helper'

RSpec.describe PaymentService do
  let(:gateway) { instance_double(Stripe::ChargeService) }
  let(:order) { create(:order) }

  before do
    allow(Stripe::ChargeService).to receive(:new).and_return(gateway)
  end

  describe '#charge' do
    context 'when payment succeeds' do
      before do
        allow(gateway).to receive(:create)
          .with(amount: order.total_cents, currency: 'usd', source: anything)
          .and_return(double(id: 'ch_123', status: 'succeeded'))
      end

      it 'returns successful result' do
        result = PaymentService.new(order).charge

        expect(result).to be_success
        expect(result.charge_id).to eq('ch_123')
      end
    end

    context 'when payment fails' do
      before do
        allow(gateway).to receive(:create)
          .and_raise(Stripe::CardError.new('Card declined', nil, code: 'card_declined'))
      end

      it 'returns failure result' do
        result = PaymentService.new(order).charge

        expect(result).to be_failure
        expect(result.error_message).to eq('Card declined')
      end
    end
  end
end
```

### Pattern 9: Testing File Uploads
```ruby
# spec/services/avatar_upload_service_spec.rb
require 'rails_helper'

RSpec.describe AvatarUploadService do
  let(:user) { create(:user) }
  let(:file) do
    fixture_file_upload(
      Rails.root.join('spec', 'fixtures', 'files', 'avatar.jpg'),
      'image/jpeg'
    )
  end

  describe '#upload' do
    it 'attaches avatar to user' do
      service = AvatarUploadService.new(user, file)
      service.upload

      expect(user.avatar).to be_attached
      expect(user.avatar.filename.to_s).to eq('avatar.jpg')
    end

    it 'validates file type' do
      invalid_file = fixture_file_upload(
        Rails.root.join('spec', 'fixtures', 'files', 'document.pdf'),
        'application/pdf'
      )

      service = AvatarUploadService.new(user, invalid_file)

      expect(service.upload).to be_falsey
      expect(service.errors).to include('File must be an image')
    end
  end
end
```

### Pattern 10: Stubbing Environment Variables
```ruby
# spec/services/config_service_spec.rb
require 'rails_helper'

RSpec.describe ConfigService do
  describe '.api_key' do
    it 'returns API key from environment' do
      stub_const('ENV', ENV.to_hash.merge('API_KEY' => 'test_key'))

      expect(ConfigService.api_key).to eq('test_key')
    end

    it 'raises error when API key missing' do
      stub_const('ENV', ENV.to_hash.except('API_KEY'))

      expect {
        ConfigService.api_key
      }.to raise_error(ConfigService::MissingKeyError)
    end
  end
end
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Over-mocking | Tests don't verify real behavior | Mock only external dependencies |
| Not using VCR for slow APIs | Tests make real API calls | Use VCR to record/replay |
| Mocking ActiveRecord | Bypasses validation logic | Use real models with factories |
| Not verifying mock calls | Mocks called incorrectly | Use `expect().to have_received()` |
| Hardcoding mock data | Brittle tests | Use realistic fixtures or Faker |

## Related Skills
- [Services](../types/services.md): Testing service objects
- [Jobs](../types/jobs.md): Testing background jobs
- [RSpec Setup](../setup/rspec.md): Configuring WebMock and VCR

## References
- [RSpec Mocks](https://rspec.info/features/3-12/rspec-mocks/)
- [WebMock](https://github.com/bblimke/webmock)
- [VCR](https://github.com/vcr/vcr)
- [Test Doubles](https://martinfowler.com/bliki/TestDouble.html)
