# Lemon Squeezy Subscription Implementation

Lemon Squeezy implementation for subscription billing. Alternative to Stripe with merchant of record benefits.

## Overview

Lemon Squeezy acts as the merchant of record, handling:
- Sales tax calculation and remittance
- EU VAT compliance
- PCI compliance
- Fraud prevention

**Trade-offs:**
- Higher fees (5% + 50¢ vs Stripe's 2.9% + 30¢)
- Less customization than Stripe
- Simpler compliance requirements

## Prerequisites

- [shared.md](./shared.md) - Shared subscription components (adapt field names)

## Setup

```ruby
# Gemfile
gem "lemonsqueezy"

# Terminal
bundle install
```

## Implementation

**Note:** This is a placeholder for Lemon Squeezy implementation. The implementation follows a similar pattern to Stripe with these key differences:

1. **Field names** - Use `lemonsqueezy_customer_id` instead of `stripe_customer_id`
2. **Webhook handling** - Lemon Squeezy uses different event types
3. **Checkout** - Lemon Squeezy has a different checkout flow
4. **Portal** - Customer portal is hosted by Lemon Squeezy

## Migration Differences

```ruby
# db/migrate/..._add_subscription_to_accounts.rb
class AddSubscriptionToAccounts < ActiveRecord::Migration[8.0]
  def change
    add_column :accounts, :lemonsqueezy_customer_id, :string
    add_column :accounts, :lemonsqueezy_subscription_id, :string
    add_column :accounts, :plan, :string, default: "free"
    add_column :accounts, :plan_interval, :string
    add_column :accounts, :trial_ends_at, :datetime
    add_column :accounts, :subscription_ends_at, :datetime
    add_column :accounts, :payment_method_last4, :string
    add_column :accounts, :payment_method_brand, :string

    add_index :accounts, :lemonsqueezy_customer_id
    add_index :accounts, :lemonsqueezy_subscription_id
  end
end
```

## Key Differences from Stripe

| Feature | Stripe | Lemon Squeezy |
|---------|--------|---------------|
| Merchant of Record | You | Lemon Squeezy |
| Tax Handling | Manual | Automatic |
| Fees | 2.9% + 30¢ | 5% + 50¢ |
| Customization | High | Medium |
| Checkout | Self-hosted | Hosted |
| Customer Portal | Self-hosted | Hosted |

## Resources

- [Lemon Squeezy Documentation](https://docs.lemonsqueezy.com/)
- [Lemon Squeezy API](https://docs.lemonsqueezy.com/api)
- [Lemon Squeezy Webhooks](https://docs.lemonsqueezy.com/help/webhooks)

## Related

- [shared.md](./shared.md) - Shared subscription components
- [stripe.md](./stripe.md) - Stripe implementation (reference)
- [integrations/lemon-squeezy](../integrations/lemon-squeezy.md) - Detailed Lemon Squeezy guide

## Contributing

Full Lemon Squeezy implementation coming soon. Contributions welcome!
