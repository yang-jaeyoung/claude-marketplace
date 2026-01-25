# Multi-Channel Notification Job with Retry Logic
#
# Features:
# - In-app notifications via database
# - Push notifications via FCM (Firebase Cloud Messaging)
# - Email notifications
# - SMS notifications via Twilio
# - User preference checking
# - Retry logic for external services
# - Error handling and fallbacks
# - Real-time updates via Turbo Streams
#
# Usage:
#   NotificationJob.perform_later(
#     user.id,
#     "order_shipped",
#     { order_id: 123, tracking_number: "ABC123" }
#   )

class NotificationJob < ApplicationJob
  queue_as :default

  # Retry on network errors
  retry_on Net::OpenTimeout, wait: :polynomially_longer, attempts: 5
  retry_on Net::ReadTimeout, wait: :polynomially_longer, attempts: 5

  # Don't retry on permanent failures
  discard_on ActiveRecord::RecordNotFound
  discard_on ArgumentError

  def perform(user_id, notification_type, data = {})
    @user = User.find(user_id)
    @notification_type = notification_type
    @data = data

    # Always create in-app notification
    create_in_app_notification

    # Send via other channels based on user preferences
    send_push_notification if should_send_push?
    send_email_notification if should_send_email?
    send_sms_notification if should_send_sms?

    Rails.logger.info "Notification sent: #{notification_type} to user #{user_id}"
  rescue => e
    Rails.logger.error "Notification failed: #{e.message}"
    Sentry.capture_exception(e) if defined?(Sentry)
    raise  # Re-raise for retry
  end

  private

  # In-App Notification
  def create_in_app_notification
    notification = @user.notifications.create!(
      notification_type: @notification_type,
      title: notification_title,
      body: notification_body,
      data: @data,
      read_at: nil
    )

    # Broadcast via Turbo Stream for real-time updates
    broadcast_notification(notification)

    notification
  end

  def broadcast_notification(notification)
    # Prepend to notification list
    notification.broadcast_prepend_to(
      "notifications_#{@user.id}",
      target: "notifications_list",
      partial: "notifications/notification",
      locals: { notification: notification }
    )

    # Update unread count badge
    unread_count = @user.notifications.unread.count
    Turbo::StreamsChannel.broadcast_replace_to(
      "notifications_#{@user.id}",
      target: "notification_badge",
      html: unread_count > 0 ? unread_count : ""
    )
  end

  # Push Notification (FCM)
  def send_push_notification
    tokens = @user.devices.where(push_enabled: true).pluck(:fcm_token).compact

    return if tokens.empty?

    response = fcm_client.send_to_topic(
      tokens,
      notification: {
        title: notification_title,
        body: notification_body,
        sound: notification_sound,
        badge: @user.notifications.unread.count,
        icon: notification_icon
      },
      data: @data.merge(type: @notification_type),
      priority: notification_priority,
      time_to_live: 24.hours.to_i
    )

    # Handle failed tokens
    handle_fcm_response(response, tokens)
  rescue FCM::Unauthorized
    Rails.logger.error "FCM unauthorized - check server key"
  rescue => e
    Rails.logger.error "Push notification failed: #{e.message}"
    raise  # Retry
  end

  def handle_fcm_response(response, tokens)
    # Remove invalid/unregistered tokens
    if response[:not_registered_ids].present?
      Device.where(fcm_token: response[:not_registered_ids]).destroy_all
      Rails.logger.info "Removed #{response[:not_registered_ids].size} invalid FCM tokens"
    end

    # Update canonical IDs (refreshed tokens)
    if response[:canonical_ids].present?
      response[:canonical_ids].each do |old_token, new_token|
        device = Device.find_by(fcm_token: old_token)
        device&.update(fcm_token: new_token)
      end
    end
  end

  # Email Notification
  def send_email_notification
    mailer_class = "#{@notification_type.camelize}Mailer".constantize
    mailer_class.notification(@user, @data).deliver_later
  rescue NameError
    # Fallback to generic notification mailer
    NotificationMailer.send_notification(@user, notification_title, notification_body).deliver_later
  end

  # SMS Notification
  def send_sms_notification
    return if @user.phone.blank?

    twilio_client.messages.create(
      from: ENV["TWILIO_PHONE_NUMBER"],
      to: normalize_phone(@user.phone),
      body: sms_message
    )
  rescue Twilio::REST::RestError => e
    if e.code == 21211  # Invalid phone number
      Rails.logger.warn "Invalid phone number for user #{@user.id}"
      # Don't retry
    else
      Rails.logger.error "SMS failed: #{e.message}"
      raise  # Retry
    end
  end

  # Preference Checks
  def should_send_push?
    @user.notification_preferences.push_enabled?(@notification_type) &&
      @user.devices.where(push_enabled: true).exists?
  end

  def should_send_email?
    @user.notification_preferences.email_enabled?(@notification_type)
  end

  def should_send_sms?
    @user.notification_preferences.sms_enabled?(@notification_type) &&
      @user.phone.present?
  end

  # Content Helpers
  def notification_title
    I18n.t("notifications.#{@notification_type}.title", **@data.symbolize_keys)
  rescue I18n::MissingTranslationData
    @notification_type.titleize
  end

  def notification_body
    I18n.t("notifications.#{@notification_type}.body", **@data.symbolize_keys)
  rescue I18n::MissingTranslationData
    "You have a new notification"
  end

  def sms_message
    I18n.t("notifications.#{@notification_type}.sms", **@data.symbolize_keys)
  rescue I18n::MissingTranslationData
    notification_body.truncate(160)  # SMS length limit
  end

  def notification_sound
    case @notification_type
    when /urgent|critical|alert/
      "alarm.mp3"
    when /message|chat/
      "message.mp3"
    else
      "default"
    end
  end

  def notification_icon
    case @notification_type
    when /order/
      "order_icon"
    when /message/
      "message_icon"
    when /payment/
      "payment_icon"
    else
      "default_icon"
    end
  end

  def notification_priority
    case @notification_type
    when /urgent|critical|payment/
      "high"
    else
      "normal"
    end
  end

  # Utilities
  def fcm_client
    @fcm_client ||= FCM.new(ENV["FCM_SERVER_KEY"])
  end

  def twilio_client
    @twilio_client ||= Twilio::REST::Client.new(
      ENV["TWILIO_ACCOUNT_SID"],
      ENV["TWILIO_AUTH_TOKEN"]
    )
  end

  def normalize_phone(phone)
    # Remove non-digits
    digits = phone.gsub(/\D/, "")

    # Add US country code if 10 digits
    digits.length == 10 ? "+1#{digits}" : "+#{digits}"
  end
end

# Supporting Models:

# app/models/notification.rb
# class Notification < ApplicationRecord
#   belongs_to :user
#
#   scope :unread, -> { where(read_at: nil) }
#   scope :read, -> { where.not(read_at: nil) }
#
#   def mark_as_read!
#     update!(read_at: Time.current)
#   end
# end

# app/models/notification_preference.rb
# class NotificationPreference < ApplicationRecord
#   belongs_to :user
#
#   def push_enabled?(notification_type)
#     return true unless respond_to?("#{notification_type}_push")
#     public_send("#{notification_type}_push")
#   end
#
#   def email_enabled?(notification_type)
#     return true unless respond_to?("#{notification_type}_email")
#     public_send("#{notification_type}_email")
#   end
#
#   def sms_enabled?(notification_type)
#     return false unless respond_to?("#{notification_type}_sms")
#     public_send("#{notification_type}_sms")
#   end
# end

# app/models/device.rb
# class Device < ApplicationRecord
#   belongs_to :user
#
#   enum platform: { ios: 0, android: 1, web: 2 }
#
#   validates :fcm_token, presence: true, uniqueness: true
# end

# Migrations:
# create_table :notifications do |t|
#   t.references :user, null: false, foreign_key: true
#   t.string :notification_type, null: false
#   t.string :title
#   t.text :body
#   t.jsonb :data
#   t.datetime :read_at
#   t.timestamps
# end
#
# create_table :devices do |t|
#   t.references :user, null: false, foreign_key: true
#   t.string :fcm_token, null: false
#   t.integer :platform, null: false
#   t.boolean :push_enabled, default: true
#   t.timestamps
# end
#
# add_index :devices, :fcm_token, unique: true

# Locale file (config/locales/notifications.en.yml):
# en:
#   notifications:
#     order_shipped:
#       title: "Order Shipped!"
#       body: "Your order %{order_id} has been shipped. Tracking: %{tracking_number}"
#       sms: "Order %{order_id} shipped! Track: %{tracking_number}"
#     payment_received:
#       title: "Payment Received"
#       body: "Payment of $%{amount} received for order %{order_id}"
#       sms: "Payment received: $%{amount}"
