# Service Object Tests

## Overview
Service object tests verify business logic encapsulated in service classes. Services coordinate models, external APIs, and complex operations.

## When to Use
- Testing multi-step business operations
- Testing external API integrations
- Testing complex data transformations
- Testing transactional workflows

## Quick Start
```ruby
# spec/services/posts/create_service_spec.rb
require 'rails_helper'

RSpec.describe Posts::CreateService do
  describe '.call' do
    let(:user) { create(:user) }
    let(:params) { { title: "Test", body: "Content" } }

    it 'creates a post' do
      result = described_class.call(user: user, params: params)

      expect(result).to be_success
      expect(result.value).to be_a(Post)
    end
  end
end
```

## Common Setup

For standard RSpec configuration including Factory Bot, Devise helpers, and Turbo Stream test helpers, see:
- [`snippets/common/rspec-setup.rb`](../../snippets/common/rspec-setup.rb): RSpec configuration
- [`snippets/common/factory-base.rb`](../../snippets/common/factory-base.rb): FactoryBot patterns

## Main Patterns

### Pattern 1: Testing Service with Result Object
```ruby
# app/services/posts/create_service.rb
module Posts
  class CreateService
    def self.call(user:, params:)
      new(user: user, params: params).call
    end

    def initialize(user:, params:)
      @user = user
      @params = params
    end

    def call
      post = user.posts.build(params)

      if post.save
        notify_followers(post)
        Result.success(post)
      else
        Result.failure(post.errors)
      end
    end

    private

    attr_reader :user, :params

    def notify_followers(post)
      PostNotificationJob.perform_later(post.id)
    end
  end
end

# spec/services/posts/create_service_spec.rb
require 'rails_helper'

RSpec.describe Posts::CreateService do
  let(:user) { create(:user) }
  let(:valid_params) { { title: "Test Post", body: "Content" } }
  let(:invalid_params) { { title: "", body: "" } }

  describe '.call' do
    context 'with valid params' do
      it 'returns success result' do
        result = described_class.call(user: user, params: valid_params)

        expect(result).to be_success
        expect(result).not_to be_failure
      end

      it 'creates a post' do
        result = described_class.call(user: user, params: valid_params)

        expect(result.value).to be_a(Post)
        expect(result.value).to be_persisted
        expect(result.value.title).to eq("Test Post")
      end

      it 'associates post with user' do
        result = described_class.call(user: user, params: valid_params)

        expect(result.value.user).to eq(user)
      end

      it 'enqueues notification job' do
        expect {
          described_class.call(user: user, params: valid_params)
        }.to have_enqueued_job(PostNotificationJob)
      end
    end

    context 'with invalid params' do
      it 'returns failure result' do
        result = described_class.call(user: user, params: invalid_params)

        expect(result).to be_failure
        expect(result).not_to be_success
      end

      it 'does not create a post' do
        expect {
          described_class.call(user: user, params: invalid_params)
        }.not_to change(Post, :count)
      end

      it 'returns validation errors' do
        result = described_class.call(user: user, params: invalid_params)

        expect(result.errors).to be_present
        expect(result.errors[:title]).to include("can't be blank")
      end

      it 'does not enqueue notification job' do
        expect {
          described_class.call(user: user, params: invalid_params)
        }.not_to have_enqueued_job(PostNotificationJob)
      end
    end
  end
end
```

### Pattern 2: Testing External API Integration
```ruby
# app/services/github/fetch_repos_service.rb
module Github
  class FetchReposService
    def self.call(username:)
      new(username: username).call
    end

    def initialize(username:)
      @username = username
    end

    def call
      response = HTTParty.get("https://api.github.com/users/#{username}/repos")

      if response.success?
        repos = response.parsed_response.map { |r| r['name'] }
        Result.success(repos)
      else
        Result.failure("Failed to fetch repositories")
      end
    end

    private

    attr_reader :username
  end
end

# spec/services/github/fetch_repos_service_spec.rb
require 'rails_helper'

RSpec.describe Github::FetchReposService do
  describe '.call' do
    let(:username) { 'testuser' }

    context 'when API request succeeds' do
      before do
        stub_request(:get, "https://api.github.com/users/testuser/repos")
          .to_return(
            status: 200,
            body: [
              { name: 'repo1', description: 'First repo' },
              { name: 'repo2', description: 'Second repo' }
            ].to_json,
            headers: { 'Content-Type' => 'application/json' }
          )
      end

      it 'returns success result with repository names' do
        result = described_class.call(username: username)

        expect(result).to be_success
        expect(result.value).to eq(['repo1', 'repo2'])
      end
    end

    context 'when API request fails' do
      before do
        stub_request(:get, "https://api.github.com/users/testuser/repos")
          .to_return(status: 404)
      end

      it 'returns failure result' do
        result = described_class.call(username: username)

        expect(result).to be_failure
        expect(result.errors).to eq("Failed to fetch repositories")
      end
    end

    context 'when network error occurs' do
      before do
        stub_request(:get, "https://api.github.com/users/testuser/repos")
          .to_timeout
      end

      it 'handles timeout gracefully' do
        expect {
          described_class.call(username: username)
        }.to raise_error(Net::OpenTimeout)
      end
    end
  end
end
```

### Pattern 3: Testing Transactional Service
```ruby
# app/services/subscriptions/cancel_service.rb
module Subscriptions
  class CancelService
    def self.call(subscription:)
      new(subscription: subscription).call
    end

    def initialize(subscription:)
      @subscription = subscription
    end

    def call
      ActiveRecord::Base.transaction do
        subscription.update!(status: :cancelled, cancelled_at: Time.current)
        refund_payment if subscription.refundable?
        send_cancellation_email
        Result.success(subscription)
      end
    rescue ActiveRecord::RecordInvalid => e
      Result.failure(e.record.errors)
    end

    private

    attr_reader :subscription

    def refund_payment
      PaymentService.refund(subscription.latest_payment)
    end

    def send_cancellation_email
      SubscriptionMailer.cancellation(subscription).deliver_later
    end
  end
end

# spec/services/subscriptions/cancel_service_spec.rb
require 'rails_helper'

RSpec.describe Subscriptions::CancelService do
  let(:subscription) { create(:subscription, status: :active) }

  describe '.call' do
    context 'when cancellation succeeds' do
      it 'updates subscription status' do
        result = described_class.call(subscription: subscription)

        expect(subscription.reload.status).to eq('cancelled')
        expect(subscription.cancelled_at).to be_present
      end

      it 'returns success result' do
        result = described_class.call(subscription: subscription)

        expect(result).to be_success
        expect(result.value).to eq(subscription)
      end

      it 'sends cancellation email' do
        expect {
          described_class.call(subscription: subscription)
        }.to have_enqueued_job.on_queue('mailers')
      end
    end

    context 'when subscription is refundable' do
      let(:subscription) { create(:subscription, :refundable) }
      let(:payment_service) { double('PaymentService') }

      before do
        allow(PaymentService).to receive(:refund)
      end

      it 'processes refund' do
        described_class.call(subscription: subscription)

        expect(PaymentService).to have_received(:refund).with(subscription.latest_payment)
      end
    end

    context 'when transaction fails' do
      before do
        allow(subscription).to receive(:update!).and_raise(ActiveRecord::RecordInvalid.new(subscription))
      end

      it 'returns failure result' do
        result = described_class.call(subscription: subscription)

        expect(result).to be_failure
      end

      it 'does not send email' do
        expect {
          described_class.call(subscription: subscription)
        }.not_to have_enqueued_job
      end

      it 'rolls back changes' do
        original_status = subscription.status

        described_class.call(subscription: subscription)

        expect(subscription.reload.status).to eq(original_status)
      end
    end
  end
end
```

### Pattern 4: Testing Service with Dependencies (Dependency Injection)
```ruby
# app/services/reports/generate_service.rb
module Reports
  class GenerateService
    def self.call(user:, notifier: EmailNotifier.new)
      new(user: user, notifier: notifier).call
    end

    def initialize(user:, notifier:)
      @user = user
      @notifier = notifier
    end

    def call
      report = build_report

      if report.save
        notifier.notify(user, report)
        Result.success(report)
      else
        Result.failure(report.errors)
      end
    end

    private

    attr_reader :user, :notifier

    def build_report
      Report.new(user: user, data: generate_data)
    end

    def generate_data
      # Complex data generation
    end
  end
end

# spec/services/reports/generate_service_spec.rb
require 'rails_helper'

RSpec.describe Reports::GenerateService do
  let(:user) { create(:user) }
  let(:notifier) { double('Notifier', notify: true) }

  describe '.call' do
    it 'creates a report' do
      result = described_class.call(user: user, notifier: notifier)

      expect(result).to be_success
      expect(result.value).to be_a(Report)
    end

    it 'sends notification via injected notifier' do
      result = described_class.call(user: user, notifier: notifier)

      expect(notifier).to have_received(:notify).with(user, kind_of(Report))
    end

    context 'when save fails' do
      before do
        allow_any_instance_of(Report).to receive(:save).and_return(false)
      end

      it 'does not send notification' do
        described_class.call(user: user, notifier: notifier)

        expect(notifier).not_to have_received(:notify)
      end
    end
  end
end
```

### Pattern 5: Testing Service with Multiple Steps
```ruby
# spec/services/orders/process_service_spec.rb
require 'rails_helper'

RSpec.describe Orders::ProcessService do
  let(:order) { create(:order, :pending) }

  describe '.call' do
    it 'processes order through all steps' do
      result = described_class.call(order: order)

      expect(result).to be_success
      expect(order.reload.status).to eq('completed')
    end

    it 'validates inventory' do
      allow_any_instance_of(described_class).to receive(:validate_inventory).and_return(false)

      result = described_class.call(order: order)

      expect(result).to be_failure
      expect(result.errors).to include("Insufficient inventory")
    end

    it 'charges payment' do
      payment_service = double('PaymentService', charge: true)
      allow(PaymentService).to receive(:new).and_return(payment_service)

      described_class.call(order: order)

      expect(payment_service).to have_received(:charge)
    end

    it 'updates inventory on success' do
      expect {
        described_class.call(order: order)
      }.to change { order.line_items.first.product.reload.stock }.by(-1)
    end

    it 'sends confirmation email' do
      expect {
        described_class.call(order: order)
      }.to have_enqueued_job(OrderMailer)
    end

    context 'when payment fails' do
      before do
        allow_any_instance_of(PaymentService).to receive(:charge).and_raise(PaymentError)
      end

      it 'does not update inventory' do
        expect {
          described_class.call(order: order) rescue nil
        }.not_to change { order.line_items.first.product.reload.stock }
      end

      it 'does not send email' do
        expect {
          described_class.call(order: order) rescue nil
        }.not_to have_enqueued_job
      end
    end
  end
end
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Testing implementation details | Brittle tests | Test public interface only |
| Not mocking external services | Slow, unreliable tests | Use WebMock, VCR, or test doubles |
| Not testing edge cases | Production bugs | Test failure paths, timeouts, errors |
| Fat service objects | Hard to test | Break into smaller services |
| Not using dependency injection | Hard to mock dependencies | Inject dependencies via initializer |

## Related Skills
- [Mocking](../patterns/mocking.md): Stubbing and mocking
- [Jobs](./jobs.md): Testing background jobs
- [Request Specs](./requests.md): Integration testing

## References
- [Service Objects in Rails](https://www.toptal.com/ruby-on-rails/rails-service-objects-tutorial)
- [Result Pattern](https://dry-rb.org/gems/dry-monads/)
- [Dependency Injection](https://thoughtbot.com/blog/testing-with-dependency-injection)
