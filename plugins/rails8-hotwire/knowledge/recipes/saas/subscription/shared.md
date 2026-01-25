# Shared Subscription Components

Provider-agnostic subscription model and feature gating components used across all payment providers.

## Database Schema

```ruby
# db/migrate/20240101000001_add_subscription_to_accounts.rb
class AddSubscriptionToAccounts < ActiveRecord::Migration[8.0]
  def change
    add_column :accounts, :stripe_customer_id, :string
    add_column :accounts, :stripe_subscription_id, :string
    add_column :accounts, :plan, :string, default: "free"
    add_column :accounts, :plan_interval, :string # monthly, yearly
    add_column :accounts, :trial_ends_at, :datetime
    add_column :accounts, :subscription_ends_at, :datetime
    add_column :accounts, :payment_method_last4, :string
    add_column :accounts, :payment_method_brand, :string

    add_index :accounts, :stripe_customer_id
    add_index :accounts, :stripe_subscription_id
  end
end
```

**Note:** For Lemon Squeezy, replace `stripe_customer_id` and `stripe_subscription_id` with `lemonsqueezy_customer_id` and `lemonsqueezy_subscription_id`.

## Account Model

```ruby
# app/models/account.rb
class Account < ApplicationRecord
  PLANS = {
    free: { name: "Free", price: 0, features: ["5 users", "Basic support"] },
    starter: { name: "Starter", price: 29, features: ["25 users", "Email support", "API access"] },
    professional: { name: "Professional", price: 99, features: ["Unlimited users", "Priority support", "Advanced features"] }
  }.freeze

  validates :plan, inclusion: { in: PLANS.keys.map(&:to_s) }

  # Plan helpers
  def free_plan?
    plan == "free"
  end

  def on_trial?
    trial_ends_at.present? && trial_ends_at > Time.current
  end

  def subscription_active?
    return true if free_plan?
    return true if on_trial?

    subscription_ends_at.present? && subscription_ends_at > Time.current
  end

  def can_access_feature?(feature)
    return false unless subscription_active?

    PLANS[plan.to_sym][:features].include?(feature)
  end

  # Stripe helpers
  def stripe_customer
    return unless stripe_customer_id

    @stripe_customer ||= Stripe::Customer.retrieve(stripe_customer_id)
  end

  def stripe_subscription
    return unless stripe_subscription_id

    @stripe_subscription ||= Stripe::Subscription.retrieve(stripe_subscription_id)
  end
end
```

## Feature Access Control

```ruby
# app/controllers/concerns/subscription_gating.rb
module SubscriptionGating
  extend ActiveSupport::Concern

  included do
    before_action :check_subscription
  end

  private

  def check_subscription
    unless current_account.subscription_active?
      redirect_to new_subscription_path, alert: "Please subscribe to access this feature"
    end
  end

  def require_feature(feature)
    unless current_account.can_access_feature?(feature)
      redirect_to new_subscription_path, alert: "Upgrade your plan to access #{feature}"
    end
  end
end

# Usage in controllers
class ApiKeysController < ApplicationController
  include SubscriptionGating
  before_action -> { require_feature("API access") }

  def index
    @api_keys = current_account.api_keys
  end
end
```

## Plan Configuration

Customize the `PLANS` constant in your Account model:

```ruby
PLANS = {
  free: {
    name: "Free",
    price: 0,
    features: ["5 users", "Basic support"]
  },
  starter: {
    name: "Starter",
    price: 29,
    features: ["25 users", "Email support", "API access"]
  },
  professional: {
    name: "Professional",
    price: 99,
    features: ["Unlimited users", "Priority support", "Advanced features"]
  }
}.freeze
```

## Usage

1. **Migration** - Add subscription fields to accounts table
2. **Model** - Add plan helpers and feature access methods
3. **Gating** - Include `SubscriptionGating` concern in controllers that require subscription
4. **Provider** - Integrate specific payment provider (see [stripe.md](./stripe.md) or [lemon-squeezy.md](./lemon-squeezy.md))

## Related

- [stripe.md](./stripe.md) - Stripe implementation
- [lemon-squeezy.md](./lemon-squeezy.md) - Lemon Squeezy implementation
