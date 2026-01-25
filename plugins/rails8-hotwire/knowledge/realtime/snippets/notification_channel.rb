# app/channels/notifications_channel.rb
# Real-time notification channel with mark as read functionality
#
# Usage:
#   # In JavaScript
#   consumer.subscriptions.create("NotificationsChannel", {
#     received(data) { ... },
#     markAsRead(id) { this.perform("mark_as_read", { id }) },
#     markAllAsRead() { this.perform("mark_all_as_read") }
#   })
#
#   # In view
#   <%= turbo_stream_from "notifications:#{current_user.id}" %>
#
# Prerequisites:
#   - User model with notifications association
#   - Notification model with read_at field
#   - ApplicationCable::Connection with current_user

class NotificationsChannel < ApplicationCable::Channel
  def subscribed
    stream_from stream_name
  end

  def unsubscribed
    # Cleanup if needed
  end

  # Mark a single notification as read
  # @param data [Hash] { "id" => notification_id }
  def mark_as_read(data)
    notification = current_user.notifications.find_by(id: data["id"])
    return unless notification

    notification.update(read_at: Time.current)
    broadcast_count_update
    broadcast_notification_update(notification)
  end

  # Mark all unread notifications as read
  def mark_all_as_read
    current_user.notifications.unread.update_all(read_at: Time.current)
    broadcast_count_update
    broadcast_list_refresh
  end

  private

  def stream_name
    "notifications:#{current_user.id}"
  end

  def broadcast_count_update
    count = current_user.notifications.unread.count

    # Via ActionCable (for JS handling)
    ActionCable.server.broadcast(stream_name, {
      type: "count_update",
      count: count
    })

    # Via Turbo Stream (for HTML update)
    Turbo::StreamsChannel.broadcast_update_to(
      stream_name,
      target: "notifications_count",
      html: count.to_s
    )

    # Hide badge if count is zero
    if count.zero?
      Turbo::StreamsChannel.broadcast_update_to(
        stream_name,
        target: "notifications_badge",
        html: ""
      )
    end
  end

  def broadcast_notification_update(notification)
    Turbo::StreamsChannel.broadcast_replace_to(
      stream_name,
      target: ActionView::RecordIdentifier.dom_id(notification),
      partial: "notifications/notification",
      locals: { notification: notification }
    )
  end

  def broadcast_list_refresh
    Turbo::StreamsChannel.broadcast_refresh_to(stream_name)
  end
end

# Supporting Notification model
#
# class Notification < ApplicationRecord
#   belongs_to :recipient, class_name: "User"
#   belongs_to :actor, class_name: "User", optional: true
#   belongs_to :notifiable, polymorphic: true
#
#   scope :unread, -> { where(read_at: nil) }
#   scope :recent, -> { order(created_at: :desc).limit(20) }
#
#   after_create_commit :broadcast_to_recipient
#
#   def read?
#     read_at.present?
#   end
#
#   private
#
#   def broadcast_to_recipient
#     broadcast_prepend_to(
#       "notifications:#{recipient_id}",
#       target: "notifications",
#       partial: "notifications/notification"
#     )
#
#     broadcast_update_to(
#       "notifications:#{recipient_id}",
#       target: "notifications_count",
#       html: recipient.notifications.unread.count.to_s
#     )
#   end
# end
