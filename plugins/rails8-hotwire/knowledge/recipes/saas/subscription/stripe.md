# Stripe Subscription Implementation

Complete Stripe implementation including configuration, checkout, webhooks, and customer portal.

## Prerequisites

- [shared.md](./shared.md) - Shared subscription components

## Setup

```ruby
# Gemfile
gem "stripe"
gem "stripe_event"  # Webhook handling

# Terminal
bundle install
```

## Configuration

```ruby
# config/initializers/stripe.rb
Stripe.api_key = Rails.application.credentials.dig(:stripe, :secret_key)

StripeEvent.signing_secret = Rails.application.credentials.dig(:stripe, :webhook_secret)

StripeEvent.configure do |events|
  events.subscribe "customer.subscription.created", Subscriptions::CreatedHandler
  events.subscribe "customer.subscription.updated", Subscriptions::UpdatedHandler
  events.subscribe "customer.subscription.deleted", Subscriptions::DeletedHandler
  events.subscribe "invoice.payment_succeeded", Subscriptions::PaymentSucceededHandler
  events.subscribe "invoice.payment_failed", Subscriptions::PaymentFailedHandler
end

# config/routes.rb
Rails.application.routes.draw do
  mount StripeEvent::Engine, at: "/webhooks/stripe"

  resources :subscriptions, only: [:new, :create, :edit, :update, :destroy] do
    collection do
      get :success
      get :cancel
    end
  end

  namespace :billing do
    resource :portal, only: [:create]
  end
end
```

## Checkout Controller

```ruby
# app/controllers/subscriptions_controller.rb
class SubscriptionsController < ApplicationController
  before_action :require_owner!

  def new
    @plans = Account::PLANS.reject { |k, _| k == :free }
  end

  def create
    plan = params[:plan]
    interval = params[:interval] || "monthly"

    session = create_checkout_session(plan, interval)

    redirect_to session.url, allow_other_host: true
  rescue Stripe::StripeError => e
    redirect_to new_subscription_path, alert: "Payment error: #{e.message}"
  end

  def edit
    @subscription = current_account.stripe_subscription
    @plans = Account::PLANS.reject { |k, _| k == :free }
  end

  def update
    new_plan = params[:plan]

    service = Subscriptions::UpdateService.new(current_account)
    service.change_plan(new_plan)

    redirect_to edit_subscription_path, notice: "Plan updated successfully"
  rescue Stripe::StripeError => e
    redirect_to edit_subscription_path, alert: "Update failed: #{e.message}"
  end

  def destroy
    service = Subscriptions::CancelService.new(current_account)
    service.cancel

    redirect_to root_path, notice: "Subscription cancelled"
  rescue Stripe::StripeError => e
    redirect_to edit_subscription_path, alert: "Cancellation failed: #{e.message}"
  end

  def success
    # Stripe redirects here after successful checkout
    session_id = params[:session_id]
    checkout_session = Stripe::Checkout::Session.retrieve(session_id)

    # Subscription is set up via webhook, just show success
    redirect_to root_path, notice: "Subscription activated!"
  end

  def cancel
    # Stripe redirects here if user cancels checkout
    redirect_to new_subscription_path, alert: "Checkout cancelled"
  end

  private

  def create_checkout_session(plan, interval)
    price_id = stripe_price_id(plan, interval)

    Stripe::Checkout::Session.create(
      customer: find_or_create_customer.id,
      mode: "subscription",
      line_items: [{
        price: price_id,
        quantity: 1
      }],
      success_url: success_subscriptions_url(session_id: "{CHECKOUT_SESSION_ID}"),
      cancel_url: cancel_subscriptions_url,
      subscription_data: {
        trial_period_days: 14,
        metadata: {
          account_id: current_account.id
        }
      }
    )
  end

  def find_or_create_customer
    if current_account.stripe_customer_id.present?
      Stripe::Customer.retrieve(current_account.stripe_customer_id)
    else
      customer = Stripe::Customer.create(
        email: current_user.email,
        name: current_account.name,
        metadata: {
          account_id: current_account.id
        }
      )

      current_account.update!(stripe_customer_id: customer.id)
      customer
    end
  end

  def stripe_price_id(plan, interval)
    # Store these in Rails credentials or ENV
    prices = {
      "starter" => {
        "monthly" => Rails.application.credentials.dig(:stripe, :prices, :starter_monthly),
        "yearly" => Rails.application.credentials.dig(:stripe, :prices, :starter_yearly)
      },
      "professional" => {
        "monthly" => Rails.application.credentials.dig(:stripe, :prices, :pro_monthly),
        "yearly" => Rails.application.credentials.dig(:stripe, :prices, :pro_yearly)
      }
    }

    prices.dig(plan, interval)
  end

  def require_owner!
    unless current_user.owner?
      redirect_to root_path, alert: "Only account owners can manage subscriptions"
    end
  end
end
```

## Service Objects

```ruby
# app/services/subscriptions/update_service.rb
module Subscriptions
  class UpdateService
    def initialize(account)
      @account = account
    end

    def change_plan(new_plan)
      subscription = Stripe::Subscription.retrieve(@account.stripe_subscription_id)

      new_price = stripe_price_id(new_plan, @account.plan_interval)

      Stripe::Subscription.update(
        subscription.id,
        items: [{
          id: subscription.items.data[0].id,
          price: new_price
        }],
        proration_behavior: "create_prorations"
      )

      @account.update!(plan: new_plan)
    end

    private

    def stripe_price_id(plan, interval)
      # Same as controller helper
      prices = {
        "starter" => {
          "monthly" => Rails.application.credentials.dig(:stripe, :prices, :starter_monthly),
          "yearly" => Rails.application.credentials.dig(:stripe, :prices, :starter_yearly)
        },
        "professional" => {
          "monthly" => Rails.application.credentials.dig(:stripe, :prices, :pro_monthly),
          "yearly" => Rails.application.credentials.dig(:stripe, :prices, :pro_yearly)
        }
      }

      prices.dig(plan, interval)
    end
  end
end

# app/services/subscriptions/cancel_service.rb
module Subscriptions
  class CancelService
    def initialize(account)
      @account = account
    end

    def cancel(at_period_end: true)
      subscription = Stripe::Subscription.retrieve(@account.stripe_subscription_id)

      if at_period_end
        # Cancel at end of billing period
        Stripe::Subscription.update(
          subscription.id,
          cancel_at_period_end: true
        )

        @account.update!(
          subscription_ends_at: Time.at(subscription.current_period_end)
        )
      else
        # Cancel immediately
        Stripe::Subscription.cancel(subscription.id)

        @account.update!(
          plan: "free",
          subscription_ends_at: Time.current
        )
      end
    end
  end
end
```

## Webhook Handlers

```ruby
# app/handlers/subscriptions/created_handler.rb
module Subscriptions
  class CreatedHandler
    def call(event)
      subscription = event.data.object
      account = Account.find_by!(stripe_customer_id: subscription.customer)

      account.update!(
        stripe_subscription_id: subscription.id,
        plan: plan_from_price(subscription.items.data[0].price.id),
        plan_interval: subscription.items.data[0].price.recurring.interval,
        trial_ends_at: subscription.trial_end ? Time.at(subscription.trial_end) : nil,
        subscription_ends_at: Time.at(subscription.current_period_end)
      )
    end

    private

    def plan_from_price(price_id)
      # Map Stripe price ID to your plan names
      case price_id
      when Rails.application.credentials.dig(:stripe, :prices, :starter_monthly),
           Rails.application.credentials.dig(:stripe, :prices, :starter_yearly)
        "starter"
      when Rails.application.credentials.dig(:stripe, :prices, :pro_monthly),
           Rails.application.credentials.dig(:stripe, :prices, :pro_yearly)
        "professional"
      else
        "free"
      end
    end
  end
end

# app/handlers/subscriptions/updated_handler.rb
module Subscriptions
  class UpdatedHandler
    def call(event)
      subscription = event.data.object
      account = Account.find_by!(stripe_subscription_id: subscription.id)

      account.update!(
        plan: plan_from_price(subscription.items.data[0].price.id),
        plan_interval: subscription.items.data[0].price.recurring.interval,
        subscription_ends_at: Time.at(subscription.current_period_end)
      )
    end

    private

    def plan_from_price(price_id)
      # Same as CreatedHandler
      case price_id
      when Rails.application.credentials.dig(:stripe, :prices, :starter_monthly),
           Rails.application.credentials.dig(:stripe, :prices, :starter_yearly)
        "starter"
      when Rails.application.credentials.dig(:stripe, :prices, :pro_monthly),
           Rails.application.credentials.dig(:stripe, :prices, :pro_yearly)
        "professional"
      else
        "free"
      end
    end
  end
end

# app/handlers/subscriptions/deleted_handler.rb
module Subscriptions
  class DeletedHandler
    def call(event)
      subscription = event.data.object
      account = Account.find_by!(stripe_subscription_id: subscription.id)

      account.update!(
        plan: "free",
        subscription_ends_at: Time.current
      )
    end
  end
end

# app/handlers/subscriptions/payment_succeeded_handler.rb
module Subscriptions
  class PaymentSucceededHandler
    def call(event)
      invoice = event.data.object
      account = Account.find_by!(stripe_customer_id: invoice.customer)

      # Update payment method info
      if invoice.payment_intent
        payment_intent = Stripe::PaymentIntent.retrieve(invoice.payment_intent)
        payment_method = Stripe::PaymentMethod.retrieve(payment_intent.payment_method)

        account.update!(
          payment_method_last4: payment_method.card.last4,
          payment_method_brand: payment_method.card.brand
        )
      end

      # Send receipt email
      SubscriptionMailer.payment_receipt(account, invoice).deliver_later
    end
  end
end

# app/handlers/subscriptions/payment_failed_handler.rb
module Subscriptions
  class PaymentFailedHandler
    def call(event)
      invoice = event.data.object
      account = Account.find_by!(stripe_customer_id: invoice.customer)

      # Send payment failed notification
      SubscriptionMailer.payment_failed(account, invoice).deliver_later
    end
  end
end
```

## Customer Portal

```ruby
# app/controllers/billing/portals_controller.rb
class Billing::PortalsController < ApplicationController
  before_action :require_owner!

  def create
    session = Stripe::BillingPortal::Session.create(
      customer: current_account.stripe_customer_id,
      return_url: root_url
    )

    redirect_to session.url, allow_other_host: true
  end

  private

  def require_owner!
    unless current_user.owner?
      redirect_to root_path, alert: "Only account owners can access billing"
    end
  end
end
```

## Credentials Setup

```bash
# Edit credentials
EDITOR="code --wait" rails credentials:edit

# Add:
stripe:
  publishable_key: pk_test_...
  secret_key: sk_test_...
  webhook_secret: whsec_...
  prices:
    starter_monthly: price_...
    starter_yearly: price_...
    pro_monthly: price_...
    pro_yearly: price_...
```

## Testing Webhooks Locally

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:3000/webhooks/stripe

# Trigger test event
stripe trigger customer.subscription.created
```

## Related

- [shared.md](./shared.md) - Shared subscription components
- [background/solid-queue](../../background/solid-queue.md) - Webhook processing
