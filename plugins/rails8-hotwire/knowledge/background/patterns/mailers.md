# Background Mailers

## Overview

Asynchronous email sending with ActionMailer and ActiveJob. Send emails in background jobs to avoid blocking web requests and improve response times.

## When to Use

- Welcome emails after signup
- Password reset emails
- Order confirmations
- Notifications and alerts
- Newsletter campaigns
- Batch email sending

## Quick Start

```ruby
# Send async (recommended)
UserMailer.welcome_email(user).deliver_later

# Send now (blocks)
UserMailer.welcome_email(user).deliver_now

# Delayed
UserMailer.welcome_email(user).deliver_later(wait: 1.hour)
```

## Main Patterns

### Pattern 1: Basic Async Mailer

```ruby
# app/mailers/user_mailer.rb
class UserMailer < ApplicationMailer
  default from: "noreply@example.com"

  def welcome_email(user)
    @user = user
    @login_url = login_url

    mail(
      to: @user.email,
      subject: "Welcome to #{AppConfig.name}!"
    )
  end

  def password_reset(user)
    @user = user
    @reset_url = edit_password_reset_url(user.reset_token)
    @expires_at = user.reset_token_expires_at

    mail(to: @user.email, subject: "Password Reset Instructions")
  end
end

# app/controllers/users_controller.rb
class UsersController < ApplicationController
  def create
    @user = User.new(user_params)

    if @user.save
      # Send welcome email asynchronously
      UserMailer.welcome_email(@user).deliver_later

      redirect_to root_path, notice: "Account created!"
    else
      render :new, status: :unprocessable_entity
    end
  end
end
```

### Pattern 2: Delayed and Scheduled Emails

```ruby
# app/mailers/campaign_mailer.rb
class CampaignMailer < ApplicationMailer
  def follow_up(user, days_since_signup)
    @user = user
    @days = days_since_signup

    mail(
      to: @user.email,
      subject: "Day #{days_since_signup}: Getting Started Guide"
    )
  end
end

# app/models/user.rb
class User < ApplicationRecord
  after_create :schedule_onboarding_emails

  private

  def schedule_onboarding_emails
    # Day 1: Welcome
    UserMailer.welcome_email(self).deliver_later

    # Day 3: Follow up
    CampaignMailer.follow_up(self, 3).deliver_later(wait: 3.days)

    # Day 7: Tips
    CampaignMailer.follow_up(self, 7).deliver_later(wait: 7.days)

    # Day 14: Survey
    CampaignMailer.follow_up(self, 14).deliver_later(wait: 14.days)
  end
end

# Or schedule for specific time
UserMailer.weekly_digest(user).deliver_later(
  wait_until: Date.tomorrow.noon
)
```

### Pattern 3: Parameterized Mailers

```ruby
# app/mailers/notification_mailer.rb
class NotificationMailer < ApplicationMailer
  # Parameterize with user for reusability
  def with_user(user)
    @user = user
    self
  end

  def order_confirmed(order)
    @order = order

    mail(
      to: @user.email,
      subject: "Order ##{@order.number} Confirmed"
    )
  end

  def order_shipped(order)
    @order = order

    mail(
      to: @user.email,
      subject: "Order ##{@order.number} Shipped"
    )
  end

  def order_delivered(order)
    @order = order

    mail(
      to: @user.email,
      subject: "Order ##{@order.number} Delivered"
    )
  end
end

# Usage
NotificationMailer.with(user: current_user)
                  .order_confirmed(order)
                  .deliver_later

# Or chain with record
class Order < ApplicationRecord
  after_update :send_status_email

  private

  def send_status_email
    return unless saved_change_to_status?

    case status
    when "confirmed"
      NotificationMailer.with(user: user).order_confirmed(self).deliver_later
    when "shipped"
      NotificationMailer.with(user: user).order_shipped(self).deliver_later
    when "delivered"
      NotificationMailer.with(user: user).order_delivered(self).deliver_later
    end
  end
end
```

### Pattern 4: Batch Email Sending

```ruby
# app/jobs/batch_email_job.rb
class BatchEmailJob < ApplicationJob
  queue_as :low

  def perform(user_ids, email_type)
    User.where(id: user_ids).find_each do |user|
      send_email(user, email_type)
    end
  end

  private

  def send_email(user, email_type)
    case email_type
    when "newsletter"
      NewsletterMailer.weekly(user).deliver_now
    when "digest"
      DigestMailer.daily(user).deliver_now
    when "announcement"
      AnnouncementMailer.new_feature(user).deliver_now
    end
  end
end

# Usage: Send to 10,000 users
user_ids = User.subscribed.pluck(:id)

user_ids.each_slice(100) do |batch|
  BatchEmailJob.perform_later(batch, "newsletter")
end
```

### Pattern 5: Email with Attachments

```ruby
# app/mailers/invoice_mailer.rb
class InvoiceMailer < ApplicationMailer
  def monthly_invoice(user, invoice)
    @user = user
    @invoice = invoice

    # Attach Active Storage file
    if invoice.pdf.attached?
      attachments[invoice.pdf.filename.to_s] = invoice.pdf.download
    end

    # Or generate PDF inline
    pdf = InvoicePdf.new(invoice).render
    attachments["invoice_#{invoice.number}.pdf"] = {
      mime_type: "application/pdf",
      content: pdf
    }

    mail(
      to: @user.email,
      subject: "Your Invoice for #{invoice.period}"
    )
  end
end

# app/jobs/send_invoices_job.rb
class SendInvoicesJob < ApplicationJob
  queue_as :low

  def perform(billing_period)
    Invoice.where(period: billing_period).find_each do |invoice|
      InvoiceMailer.monthly_invoice(invoice.user, invoice).deliver_later
    end
  end
end
```

### Pattern 6: Inline Image Attachments

```ruby
# app/mailers/marketing_mailer.rb
class MarketingMailer < ApplicationMailer
  def campaign(user)
    @user = user

    # Inline images
    attachments.inline["logo.png"] = File.read(
      Rails.root.join("app/assets/images/logo.png")
    )

    attachments.inline["banner.jpg"] = File.read(
      Rails.root.join("app/assets/images/campaign-banner.jpg")
    )

    mail(
      to: @user.email,
      subject: "Special Offer Inside!"
    )
  end
end

# app/views/marketing_mailer/campaign.html.erb
<img src="<%= attachments['logo.png'].url %>" alt="Logo">
<img src="<%= attachments['banner.jpg'].url %>" alt="Banner">
```

### Pattern 7: Error Handling and Retries

```ruby
# app/mailers/application_mailer.rb
class ApplicationMailer < ActionMailer::Base
  default from: "noreply@example.com"
  layout "mailer"

  # Retry on temporary failures
  rescue_from Net::SMTPServerBusy, with: :retry_email
  rescue_from Net::SMTPSyntaxError, with: :log_permanent_failure

  private

  def retry_email(exception)
    # Will be retried by ActiveJob
    raise exception
  end

  def log_permanent_failure(exception)
    Rails.logger.error "Permanent email failure: #{exception.message}"
    # Don't retry
  end
end

# app/jobs/send_email_job.rb
class SendEmailJob < ApplicationJob
  queue_as :high

  retry_on Net::SMTPServerBusy, wait: :polynomially_longer, attempts: 5
  discard_on Net::SMTPSyntaxError  # Invalid email address

  def perform(mailer_class, mailer_method, *args)
    mailer_class.constantize.public_send(mailer_method, *args).deliver_now
  end
end
```

### Pattern 8: Email Preferences and Unsubscribe

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_many :email_preferences

  def email_enabled?(category)
    preference = email_preferences.find_by(category: category)
    preference.nil? ? true : preference.enabled
  end
end

# app/mailers/newsletter_mailer.rb
class NewsletterMailer < ApplicationMailer
  def weekly(user)
    return unless user.email_enabled?(:newsletter)

    @user = user
    @unsubscribe_url = unsubscribe_url(
      token: user.unsubscribe_token,
      category: "newsletter"
    )

    mail(
      to: @user.email,
      subject: "Weekly Newsletter",
      "List-Unsubscribe": "<#{@unsubscribe_url}>"
    )
  end
end

# app/controllers/unsubscribe_controller.rb
class UnsubscribeController < ApplicationController
  skip_before_action :authenticate_user!

  def show
    user = User.find_by!(unsubscribe_token: params[:token])
    category = params[:category]

    user.email_preferences.find_or_create_by(category: category).update!(
      enabled: false
    )

    render :unsubscribed
  end
end
```

## Advanced Patterns

### Email Preview Classes

```ruby
# test/mailers/previews/user_mailer_preview.rb
class UserMailerPreview < ActionMailer::Preview
  def welcome_email
    UserMailer.welcome_email(User.first)
  end

  def password_reset
    user = User.first
    user.reset_token = "sample-token-123"
    UserMailer.password_reset(user)
  end

  def order_confirmation
    order = Order.includes(:user, :items).first
    NotificationMailer.with(user: order.user).order_confirmed(order)
  end
end

# Visit: http://localhost:3000/rails/mailers
```

### Testing Async Emails

```ruby
# spec/requests/users_spec.rb
RSpec.describe "Users", type: :request do
  describe "POST /users" do
    it "sends welcome email asynchronously" do
      expect {
        post users_path, params: { user: valid_attributes }
      }.to have_enqueued_job(ActionMailer::MailDeliveryJob)
        .with("UserMailer", "welcome_email", "deliver_now", args: [kind_of(User)])

      # Or check email was sent in job
      perform_enqueued_jobs do
        post users_path, params: { user: valid_attributes }
      end

      expect(ActionMailer::Base.deliveries.count).to eq(1)
      email = ActionMailer::Base.deliveries.last
      expect(email.to).to include(User.last.email)
      expect(email.subject).to eq("Welcome to MyApp!")
    end
  end
end
```

### Email Rate Limiting

```ruby
# app/jobs/rate_limited_email_job.rb
class RateLimitedEmailJob < ApplicationJob
  queue_as :low

  # Use sidekiq-rate-limiter or custom implementation
  def perform(user_ids, email_type)
    user_ids.each do |user_id|
      user = User.find(user_id)

      # Rate limit: 10 emails per minute
      RateLimiter.throttle("email_send", limit: 10, period: 1.minute) do
        send_email(user, email_type)
      end
    end
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| `deliver_now` in controllers | Blocks request | Use `deliver_later` |
| No error handling | Silent failures | Add retry logic |
| Sending without checking preferences | Spam/unsubscribes | Check email_enabled? |
| Large attachments inline | Memory/timeout issues | Use background job |
| No unsubscribe link | Legal/UX issues | Always include unsubscribe |

```ruby
# Bad: Blocks request for 2-5 seconds
def create
  user.save
  UserMailer.welcome_email(user).deliver_now
  redirect_to root_path
end

# Good: Async, instant response
def create
  user.save
  UserMailer.welcome_email(user).deliver_later
  redirect_to root_path
end

# Bad: No preference check
NewsletterMailer.weekly(user).deliver_later

# Good: Respect preferences
NewsletterMailer.weekly(user).deliver_later if user.email_enabled?(:newsletter)
```

## Configuration Tips

```ruby
# config/environments/development.rb
config.action_mailer.delivery_method = :letter_opener
config.action_mailer.perform_deliveries = true

# config/environments/test.rb
config.action_mailer.delivery_method = :test
config.action_mailer.perform_deliveries = true

# config/environments/production.rb
config.action_mailer.delivery_method = :smtp
config.action_mailer.smtp_settings = {
  address: ENV["SMTP_ADDRESS"],
  port: ENV["SMTP_PORT"],
  user_name: ENV["SMTP_USERNAME"],
  password: ENV["SMTP_PASSWORD"],
  authentication: :plain,
  enable_starttls_auto: true
}

# Or use service like Postmark, SendGrid, Mailgun
config.action_mailer.delivery_method = :postmark
config.action_mailer.postmark_settings = {
  api_token: ENV["POSTMARK_API_TOKEN"]
}
```

## Related Skills

- [solid-queue/jobs](../solid-queue/jobs.md): Job queue basics
- [sidekiq/jobs](../sidekiq/jobs.md): Advanced job patterns
- [notifications](./notifications.md): Push notifications
- [exports](./exports.md): Email reports with attachments

## References

- [Action Mailer Basics](https://guides.rubyonrails.org/action_mailer_basics.html)
- [Active Job Integration](https://guides.rubyonrails.org/active_job_basics.html)
- [Email Testing](https://guides.rubyonrails.org/testing.html#testing-your-mailers)
- [CAN-SPAM Compliance](https://www.ftc.gov/tips-advice/business-center/guidance/can-spam-act-compliance-guide-business)
