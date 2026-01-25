---
name: rails8-recipes-subscription
title: Subscription Payments
description: Complete subscription billing with payment providers
triggers:
  - subscription
  - payment
  - stripe
  - lemon squeezy
  - billing
  - plan
  - pricing
  - checkout
  - 구독
  - 결제
  - 스트라이프
  - 레몬 스퀴지
  - 빌링
  - 요금제
  - 가격
  - 체크아웃
summary: |
  완전한 구독 결제 시스템을 다룹니다. Stripe, Lemon Squeezy 등 결제 제공자 통합,
  요금제 관리, 웹훅 처리, 고객 포털을 포함합니다. 프로덕션 준비된 결제 통합을
  구현합니다.
token_cost: high
prerequisites:
  - core/gems
  - background/solid-queue
  - auth/devise
related:
  - background/solid-queue
  - auth/pundit
  - recipes/multi-tenant
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - "*.md"
  deep:
    - "**/*.md"
---

## Overview

Complete subscription billing system supporting multiple payment providers. Handle plans, trials, upgrades/downgrades, webhooks, and customer portals. Production-ready payment integration.

## Prerequisites

- [core/gems](../../core/gems.md): stripe or lemonSqueezy
- [background/solid-queue](../../background/solid-queue.md): Webhook processing
- [auth/devise](../../auth/devise.md): User authentication

## Quick Start

### Stripe Implementation

```ruby
# Gemfile
gem "stripe"
gem "stripe_event"  # Webhook handling

# Terminal
bundle install
rails generate migration AddSubscriptionToAccounts
rails db:migrate
```

See [stripe.md](./stripe.md) for full Stripe implementation.

### Alternative: Lemon Squeezy

For Lemon Squeezy implementation, see [lemon-squeezy.md](./lemon-squeezy.md).

## Architecture

All payment provider implementations share common components:

1. **Shared Models** - Account subscription fields and helpers ([shared.md](./shared.md))
2. **Provider-Specific** - API integration, webhooks, portal
3. **Feature Gating** - Subscription-based access control

## Provider Options

| Provider | Complexity | Fees | Best For |
|----------|------------|------|----------|
| **Stripe** | Medium | 2.9% + 30¢ | Standard SaaS, full control |
| **Lemon Squeezy** | Low | 5% + 50¢ | Merchant of record, less compliance |

## Implementation Files

1. [shared.md](./shared.md) - Account model with subscription fields and feature gating
2. [stripe.md](./stripe.md) - Complete Stripe implementation
3. [lemon-squeezy.md](./lemon-squeezy.md) - Lemon Squeezy alternative

## Testing

```ruby
# spec/services/subscriptions/update_service_spec.rb
require "rails_helper"

RSpec.describe Subscriptions::UpdateService do
  let(:account) { create(:account, :with_subscription) }

  it "upgrades subscription plan" do
    VCR.use_cassette("stripe/upgrade_plan") do
      service = described_class.new(account)
      service.change_plan("professional")

      expect(account.reload.plan).to eq("professional")
    end
  end

  it "handles proration correctly" do
    VCR.use_cassette("stripe/proration") do
      service = described_class.new(account)
      service.change_plan("professional")

      # Check that Stripe created proration invoice item
      subscription = account.stripe_subscription
      expect(subscription.items.data[0].price.id).to eq(
        Rails.application.credentials.dig(:stripe, :prices, :pro_monthly)
      )
    end
  end
end

# spec/requests/webhooks/stripe_spec.rb
require "rails_helper"

RSpec.describe "Stripe webhooks" do
  it "handles subscription.created" do
    account = create(:account, stripe_customer_id: "cus_test123")

    payload = {
      id: "sub_test123",
      customer: "cus_test123",
      items: {
        data: [{
          price: {
            id: Rails.application.credentials.dig(:stripe, :prices, :starter_monthly),
            recurring: { interval: "month" }
          }
        }]
      },
      current_period_end: 1.month.from_now.to_i
    }

    post "/webhooks/stripe",
         params: { type: "customer.subscription.created", data: { object: payload } }.to_json,
         headers: { "Content-Type" => "application/json" }

    expect(account.reload.stripe_subscription_id).to eq("sub_test123")
    expect(account.plan).to eq("starter")
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Storing prices in DB | Prices change, data gets stale | Store provider price IDs, fetch current prices from API |
| Synchronous webhook processing | Slow request, timeouts | Use Solid Queue for background processing |
| No idempotency | Duplicate webhooks cause issues | Use `event.id` to prevent duplicate processing |
| Missing error handling | Silent payment failures | Log errors, send notifications, retry failed webhooks |
| No subscription status check | Users access paid features after cancellation | Check `subscription_active?` before feature access |

## Related Skills

- [background/solid-queue](../../background/solid-queue.md): Webhook processing
- [auth/pundit](../../auth/pundit.md): Authorization
- [recipes/multi-tenant](./multi-tenant.md): SaaS architecture

## References

- [Stripe Checkout](https://stripe.com/docs/payments/checkout): Hosted checkout flow
- [Stripe Billing](https://stripe.com/docs/billing): Subscription management
- [stripe_event](https://github.com/integrallis/stripe_event): Rails webhook handler
- [Lemon Squeezy](https://www.lemonsqueezy.com/): Alternative payment processor
- [Rails Credentials](https://guides.rubyonrails.org/security.html#custom-credentials): Secure API keys
