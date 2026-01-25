# Notification Jobs

## Overview

Background jobs for sending push notifications, SMS, and in-app notifications. Handle mobile push (FCM/APNs), SMS (Twilio), and real-time browser notifications.

## When to Use

- Mobile push notifications
- SMS notifications
- In-app notification feeds
- Real-time alerts
- Multi-channel notifications

## Quick Start

```ruby
# Send notification
NotificationJob.perform_later(user.id, "order_shipped", order.id)

# Job handles delivery across channels
```

## Main Patterns

### Pattern 1: Basic In-App Notification

```ruby
# app/models/notification.rb
class Notification < ApplicationRecord
  belongs_to :user
  belongs_to :notifiable, polymorphic: true

  enum notification_type: {
    info: 0,
    success: 1,
    warning: 2,
    error: 3
  }

  scope :unread, -> { where(read_at: nil) }

  def mark_as_read!
    update!(read_at: Time.current)
  end
end

# app/jobs/notification_job.rb
class NotificationJob < ApplicationJob
  queue_as :default

  def perform(user_id, notification_type, notifiable_id = nil, notifiable_type = nil)
    user = User.find(user_id)

    notification = user.notifications.create!(
      notification_type: notification_type,
      title: notification_title(notification_type),
      body: notification_body(notification_type),
      notifiable_id: notifiable_id,
      notifiable_type: notifiable_type
    )

    # Broadcast via Turbo Stream for real-time updates
    notification.broadcast_prepend_to(
      "notifications_#{user.id}",
      target: "notifications",
      partial: "notifications/notification",
      locals: { notification: notification }
    )

    # Update unread count
    broadcast_unread_count(user)
  end

  private

  def notification_title(type)
    I18n.t("notifications.#{type}.title")
  end

  def notification_body(type)
    I18n.t("notifications.#{type}.body")
  end

  def broadcast_unread_count(user)
    count = user.notifications.unread.count

    Turbo::StreamsChannel.broadcast_replace_to(
      "notifications_#{user.id}",
      target: "notification_count",
      html: count > 0 ? count : ""
    )
  end
end

# Usage
NotificationJob.perform_later(user.id, "order_shipped", order.id, "Order")
```

### Pattern 2: Push Notification (FCM)

```ruby
# Gemfile
gem "fcm"

# config/initializers/fcm.rb
FCM_CLIENT = FCM.new(ENV["FCM_SERVER_KEY"])

# app/models/device.rb
class Device < ApplicationRecord
  belongs_to :user

  enum platform: { ios: 0, android: 1, web: 2 }
end

# app/jobs/push_notification_job.rb
class PushNotificationJob < ApplicationJob
  queue_as :default

  retry_on FCM::Unauthorized, wait: 5.seconds, attempts: 3
  retry_on Net::OpenTimeout, wait: :polynomially_longer, attempts: 5
  discard_on FCM::BadRequest

  def perform(user_id, title, body, data = {})
    user = User.find(user_id)

    # Get user's devices
    tokens = user.devices.where(push_enabled: true).pluck(:fcm_token)

    return if tokens.empty?

    # Send to FCM
    response = FCM_CLIENT.send_to_topic(
      tokens,
      notification: {
        title: title,
        body: body,
        sound: "default",
        badge: user.notifications.unread.count
      },
      data: data,
      priority: "high"
    )

    # Handle invalid tokens
    handle_response(response, tokens)
  rescue => e
    Rails.logger.error "Push notification failed: #{e.message}"
    Sentry.capture_exception(e) if defined?(Sentry)
    raise
  end

  private

  def handle_response(response, tokens)
    # Remove invalid tokens
    if response[:not_registered_ids].present?
      Device.where(fcm_token: response[:not_registered_ids]).destroy_all
    end

    # Update canonical IDs (token refresh)
    if response[:canonical_ids].present?
      response[:canonical_ids].each do |old_token, new_token|
        device = Device.find_by(fcm_token: old_token)
        device&.update(fcm_token: new_token)
      end
    end
  end
end

# Usage
PushNotificationJob.perform_later(
  user.id,
  "Order Shipped",
  "Your order #123 has been shipped",
  { order_id: 123, type: "order_shipped" }
)
```

### Pattern 3: SMS Notification (Twilio)

```ruby
# Gemfile
gem "twilio-ruby"

# config/initializers/twilio.rb
TWILIO_CLIENT = Twilio::REST::Client.new(
  ENV["TWILIO_ACCOUNT_SID"],
  ENV["TWILIO_AUTH_TOKEN"]
)

# app/jobs/sms_notification_job.rb
class SmsNotificationJob < ApplicationJob
  queue_as :default

  retry_on Twilio::REST::RestError, wait: :polynomially_longer, attempts: 5

  def perform(phone_number, message, options = {})
    TWILIO_CLIENT.messages.create(
      from: ENV["TWILIO_PHONE_NUMBER"],
      to: normalize_phone(phone_number),
      body: message,
      status_callback: options[:callback_url]
    )
  rescue Twilio::REST::RestError => e
    if e.code == 21211  # Invalid phone number
      Rails.logger.warn "Invalid phone number: #{phone_number}"
      # Don't retry
    else
      Rails.logger.error "SMS failed: #{e.message}"
      raise  # Retry
    end
  end

  private

  def normalize_phone(phone)
    # Add country code if missing
    phone = phone.gsub(/\D/, "")  # Remove non-digits
    phone = "+1#{phone}" if phone.length == 10  # US number
    phone
  end
end

# Usage
SmsNotificationJob.perform_later(
  user.phone,
  "Your verification code is: 123456"
)
```

### Pattern 4: Multi-Channel Notification

```ruby
# app/jobs/multi_channel_notification_job.rb
class MultiChannelNotificationJob < ApplicationJob
  queue_as :default

  def perform(user_id, event_type, data = {})
    user = User.find(user_id)
    preferences = user.notification_preferences

    # In-app notification (always send)
    send_in_app(user, event_type, data)

    # Email (if enabled)
    if preferences.email_enabled?(event_type)
      send_email(user, event_type, data)
    end

    # Push notification (if enabled and has devices)
    if preferences.push_enabled?(event_type) && user.devices.any?
      send_push(user, event_type, data)
    end

    # SMS (if enabled and has phone)
    if preferences.sms_enabled?(event_type) && user.phone.present?
      send_sms(user, event_type, data)
    end
  end

  private

  def send_in_app(user, event_type, data)
    NotificationJob.perform_later(
      user.id,
      event_type,
      data[:record_id],
      data[:record_type]
    )
  end

  def send_email(user, event_type, data)
    NotificationMailer.public_send(event_type, user, data).deliver_later
  end

  def send_push(user, event_type, data)
    PushNotificationJob.perform_later(
      user.id,
      notification_title(event_type),
      notification_body(event_type, data),
      data
    )
  end

  def send_sms(user, event_type, data)
    SmsNotificationJob.perform_later(
      user.phone,
      sms_message(event_type, data)
    )
  end

  def notification_title(type)
    I18n.t("notifications.#{type}.title")
  end

  def notification_body(type, data)
    I18n.t("notifications.#{type}.body", **data)
  end

  def sms_message(type, data)
    I18n.t("notifications.#{type}.sms", **data)
  end
end

# Usage
MultiChannelNotificationJob.perform_later(
  user.id,
  "order_shipped",
  { order_number: "12345", tracking_url: "https://..." }
)
```

### Pattern 5: Batch Notifications

```ruby
# app/jobs/batch_notification_job.rb
class BatchNotificationJob < ApplicationJob
  queue_as :low

  def perform(user_ids, notification_type, data = {})
    User.where(id: user_ids).find_in_batches(batch_size: 100) do |batch|
      batch.each do |user|
        send_notification(user, notification_type, data)
      end

      # Rate limiting
      sleep 0.1
    end
  end

  private

  def send_notification(user, type, data)
    # Check user preferences
    return unless user.notification_preferences.enabled?(type)

    MultiChannelNotificationJob.perform_later(user.id, type, data)
  end
end

# Usage: Notify all users about system maintenance
user_ids = User.active.pluck(:id)
BatchNotificationJob.perform_later(
  user_ids,
  "system_maintenance",
  { start_time: "2024-01-01 02:00 UTC", duration: "2 hours" }
)
```

### Pattern 6: Scheduled Reminder Notifications

```ruby
# app/jobs/reminder_notification_job.rb
class ReminderNotificationJob < ApplicationJob
  queue_as :default

  def perform(reminder_id)
    reminder = Reminder.find(reminder_id)

    return if reminder.sent?

    MultiChannelNotificationJob.perform_later(
      reminder.user_id,
      "reminder",
      {
        title: reminder.title,
        body: reminder.body,
        due_at: reminder.due_at
      }
    )

    reminder.update!(sent_at: Time.current)
  end
end

# app/models/reminder.rb
class Reminder < ApplicationRecord
  belongs_to :user

  after_create :schedule_notification

  private

  def schedule_notification
    # Schedule for reminder time
    ReminderNotificationJob.set(wait_until: remind_at).perform_later(id)
  end
end

# Usage
Reminder.create!(
  user: current_user,
  title: "Meeting with Bob",
  remind_at: 1.hour.from_now
)
```

### Pattern 7: Real-Time Browser Notifications

```ruby
# app/jobs/browser_notification_job.rb
class BrowserNotificationJob < ApplicationJob
  queue_as :default

  def perform(user_id, title, body, options = {})
    user = User.find(user_id)

    # Create in-app notification
    notification = user.notifications.create!(
      notification_type: options[:type] || "info",
      title: title,
      body: body
    )

    # Broadcast via Turbo Stream
    Turbo::StreamsChannel.broadcast_append_to(
      "notifications_#{user.id}",
      target: "notifications",
      partial: "notifications/notification",
      locals: { notification: notification }
    )

    # Trigger browser notification via Stimulus
    Turbo::StreamsChannel.broadcast_action_to(
      "notifications_#{user.id}",
      action: :dispatch,
      event_name: "browser:notify",
      detail: {
        title: title,
        body: body,
        icon: options[:icon],
        badge: options[:badge],
        tag: options[:tag],
        url: options[:url]
      }
    )
  end
end

# app/javascript/controllers/notification_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  connect() {
    this.requestPermission()

    document.addEventListener("browser:notify", this.showNotification.bind(this))
  }

  async requestPermission() {
    if ("Notification" in window && Notification.permission === "default") {
      await Notification.requestPermission()
    }
  }

  showNotification(event) {
    if (Notification.permission === "granted") {
      const { title, body, icon, badge, tag, url } = event.detail

      const notification = new Notification(title, {
        body: body,
        icon: icon || "/icon.png",
        badge: badge || "/badge.png",
        tag: tag,
        requireInteraction: false
      })

      if (url) {
        notification.onclick = () => {
          window.focus()
          window.location.href = url
          notification.close()
        }
      }
    }
  }
}
```

### Pattern 8: Notification Digest

```ruby
# app/jobs/notification_digest_job.rb
class NotificationDigestJob < ApplicationJob
  queue_as :low

  def perform
    User.with_digest_enabled.find_each do |user|
      send_digest(user)
    end
  end

  private

  def send_digest(user)
    # Get unread notifications since last digest
    notifications = user.notifications
                        .unread
                        .where("created_at > ?", user.last_digest_sent_at || 24.hours.ago)
                        .order(created_at: :desc)

    return if notifications.empty?

    # Group by type
    grouped = notifications.group_by(&:notification_type)

    # Send digest email
    NotificationMailer.daily_digest(user, grouped).deliver_later

    # Update last digest time
    user.update!(last_digest_sent_at: Time.current)
  end
end

# config/schedule.yml
daily_notification_digest:
  cron: "0 9 * * *"  # 9 AM daily
  class: "NotificationDigestJob"
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Sending to all users | Spam, no targeting | Check preferences |
| No retry logic | Lost notifications | Configure retries |
| Blocking on failures | Job delays | Discard unrecoverable errors |
| No rate limiting | API throttling | Add delays for batches |
| Missing unsubscribe | Legal issues | Always allow opt-out |

```ruby
# Bad: No preference check
users.each { |user| send_notification(user) }

# Good: Respect preferences
users.each do |user|
  if user.notification_preferences.enabled?(:marketing)
    send_notification(user)
  end
end

# Bad: No error handling
def perform(user_id)
  send_push_notification(user_id)  # Could fail
end

# Good: Handle errors
def perform(user_id)
  send_push_notification(user_id)
rescue FCM::Unauthorized
  # Token expired, remove device
  cleanup_invalid_device(user_id)
end
```

## Testing Notification Jobs

```ruby
# spec/jobs/push_notification_job_spec.rb
RSpec.describe PushNotificationJob do
  let(:user) { create(:user) }
  let(:device) { create(:device, user: user, fcm_token: "test_token") }

  before do
    allow(FCM_CLIENT).to receive(:send_to_topic).and_return({ success: 1 })
  end

  it "sends push notification" do
    PushNotificationJob.perform_now(user.id, "Test", "Message")

    expect(FCM_CLIENT).to have_received(:send_to_topic).with(
      ["test_token"],
      hash_including(notification: hash_including(title: "Test"))
    )
  end
end
```

## Related Skills

- [solid-queue/jobs](../solid-queue/jobs.md): Job queue basics
- [mailers](./mailers.md): Email notifications
- [realtime](../../realtime/SKILL.md): Turbo Streams
- [cleanup](./cleanup.md): Cleanup old notifications

## References

- [FCM Documentation](https://firebase.google.com/docs/cloud-messaging)
- [Twilio SMS](https://www.twilio.com/docs/sms)
- [Web Push Notifications](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API)
- [Turbo Streams](https://turbo.hotwired.dev/handbook/streams)
