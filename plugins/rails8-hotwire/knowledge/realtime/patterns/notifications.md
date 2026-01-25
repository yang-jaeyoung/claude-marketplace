# Real-time Notifications

## Overview

Real-time notifications keep users informed of relevant events without page refresh. This guide covers implementing toast notifications, notification centers, unread counts, and notification preferences.

## When to Use

- When users need immediate awareness of events
- When building notification centers/inboxes
- When implementing mention/tagging systems
- When tracking user engagement

## Quick Start

### Notification Model

```ruby
# app/models/notification.rb
class Notification < ApplicationRecord
  belongs_to :recipient, class_name: "User"
  belongs_to :actor, class_name: "User", optional: true
  belongs_to :notifiable, polymorphic: true

  scope :unread, -> { where(read_at: nil) }
  scope :recent, -> { order(created_at: :desc).limit(20) }

  after_create_commit :broadcast_notification

  def read!
    update(read_at: Time.current) unless read?
  end

  def read?
    read_at.present?
  end

  private

  def broadcast_notification
    # Prepend to notification list
    broadcast_prepend_to(
      "notifications:#{recipient_id}",
      target: "notifications",
      partial: "notifications/notification"
    )

    # Update counter
    broadcast_update_to(
      "notifications:#{recipient_id}",
      target: "notifications_count",
      html: recipient.notifications.unread.count.to_s
    )

    # Show toast
    broadcast_append_to(
      "notifications:#{recipient_id}",
      target: "toasts",
      partial: "notifications/toast"
    )
  end
end
```

### Basic Layout Integration

```erb
<!-- app/views/layouts/application.html.erb -->
<body>
  <%= turbo_stream_from "notifications:#{current_user.id}" if user_signed_in? %>

  <!-- Toast container -->
  <div id="toasts" class="fixed top-4 right-4 space-y-2 z-50"></div>

  <!-- Navbar with notifications -->
  <nav>
    <%= render "shared/notification_dropdown" if user_signed_in? %>
  </nav>

  <%= yield %>
</body>
```

## Main Patterns

### Pattern 1: Notification Dropdown

```erb
<!-- app/views/shared/_notification_dropdown.html.erb -->
<div data-controller="dropdown" class="relative">
  <button data-action="click->dropdown#toggle" class="relative p-2">
    <svg class="w-6 h-6"><!-- Bell icon --></svg>

    <span id="notifications_count"
          class="<%= 'hidden' if current_user.notifications.unread.count.zero? %>
                 absolute -top-1 -right-1 bg-red-500 text-white text-xs
                 rounded-full w-5 h-5 flex items-center justify-center">
      <%= current_user.notifications.unread.count %>
    </span>
  </button>

  <div data-dropdown-target="menu"
       class="hidden absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border">
    <div class="p-4 border-b flex justify-between items-center">
      <h3 class="font-semibold">Notifications</h3>
      <% if current_user.notifications.unread.any? %>
        <%= button_to "Mark all read",
                      mark_all_read_notifications_path,
                      method: :post,
                      class: "text-sm text-blue-500" %>
      <% end %>
    </div>

    <div id="notifications" class="max-h-96 overflow-y-auto">
      <%= render current_user.notifications.recent %>
    </div>

    <%= link_to "View all", notifications_path, class: "block p-4 text-center border-t" %>
  </div>
</div>
```

### Pattern 2: Notification Partial

```erb
<!-- app/views/notifications/_notification.html.erb -->
<%= turbo_frame_tag dom_id(notification) do %>
  <div id="<%= dom_id(notification) %>"
       class="p-4 hover:bg-gray-50 border-b <%= 'bg-blue-50' unless notification.read? %>"
       data-controller="notification"
       data-notification-id-value="<%= notification.id %>">

    <div class="flex items-start gap-3">
      <% if notification.actor %>
        <%= image_tag notification.actor.avatar_url, class: "w-10 h-10 rounded-full" %>
      <% else %>
        <div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
          <svg class="w-5 h-5"><!-- System icon --></svg>
        </div>
      <% end %>

      <div class="flex-1 min-w-0">
        <p class="text-sm">
          <%= notification_message(notification) %>
        </p>
        <time class="text-xs text-gray-500">
          <%= time_ago_in_words(notification.created_at) %> ago
        </time>
      </div>

      <% unless notification.read? %>
        <button data-action="click->notification#markAsRead"
                class="w-2 h-2 bg-blue-500 rounded-full"
                title="Mark as read">
        </button>
      <% end %>
    </div>
  </div>
<% end %>
```

### Pattern 3: Toast Notifications

```erb
<!-- app/views/notifications/_toast.html.erb -->
<div id="<%= dom_id(notification, :toast) %>"
     class="bg-white rounded-lg shadow-lg border p-4 max-w-sm animate-slide-in"
     data-controller="toast"
     data-toast-timeout-value="5000">

  <div class="flex items-start gap-3">
    <div class="flex-1">
      <p class="font-medium text-sm"><%= notification_title(notification) %></p>
      <p class="text-sm text-gray-600"><%= notification_message(notification) %></p>
    </div>

    <button data-action="click->toast#dismiss" class="text-gray-400 hover:text-gray-600">
      <svg class="w-5 h-5"><!-- X icon --></svg>
    </button>
  </div>

  <%= link_to "View",
              notification_path(notification),
              class: "mt-2 text-sm text-blue-500",
              data: { action: "click->toast#dismiss" } %>
</div>
```

```javascript
// app/javascript/controllers/toast_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { timeout: { type: Number, default: 5000 } }

  connect() {
    this.timeout = setTimeout(() => this.dismiss(), this.timeoutValue)
  }

  disconnect() {
    clearTimeout(this.timeout)
  }

  dismiss() {
    this.element.classList.add("animate-slide-out")
    setTimeout(() => this.element.remove(), 300)
  }
}
```

### Pattern 4: Notification Service

```ruby
# app/services/notification_service.rb
class NotificationService
  def self.notify(recipient:, actor: nil, notifiable:, type:, data: {})
    new(recipient:, actor:, notifiable:, type:, data:).call
  end

  def initialize(recipient:, actor:, notifiable:, type:, data:)
    @recipient = recipient
    @actor = actor
    @notifiable = notifiable
    @type = type
    @data = data
  end

  def call
    return if should_skip?

    Notification.create!(
      recipient: @recipient,
      actor: @actor,
      notifiable: @notifiable,
      notification_type: @type,
      data: @data
    )
  end

  private

  def should_skip?
    # Don't notify yourself
    @actor == @recipient ||
    # Check user preferences
    !@recipient.notification_enabled?(@type) ||
    # Check recent duplicate
    recent_duplicate_exists?
  end

  def recent_duplicate_exists?
    Notification.where(
      recipient: @recipient,
      notifiable: @notifiable,
      notification_type: @type,
      created_at: 5.minutes.ago..
    ).exists?
  end
end

# Usage in models
class Comment < ApplicationRecord
  after_create_commit :notify_post_author

  private

  def notify_post_author
    return if post.user == user

    NotificationService.notify(
      recipient: post.user,
      actor: user,
      notifiable: self,
      type: "comment",
      data: { post_title: post.title }
    )
  end
end
```

### Pattern 5: Notification Preferences

```ruby
# app/models/notification_preference.rb
class NotificationPreference < ApplicationRecord
  belongs_to :user

  TYPES = %w[comment mention follow message system].freeze

  TYPES.each do |type|
    define_method("#{type}?") { send("#{type}_enabled") }
  end
end

# app/models/user.rb
class User < ApplicationRecord
  has_one :notification_preference, dependent: :destroy
  after_create :create_notification_preference

  def notification_enabled?(type)
    notification_preference&.send("#{type}?") != false
  end
end
```

### Pattern 6: ActionCable Channel for Rich Interactions

```ruby
# app/channels/notifications_channel.rb
class NotificationsChannel < ApplicationCable::Channel
  def subscribed
    stream_from "notifications:#{current_user.id}"
  end

  def mark_as_read(data)
    notification = current_user.notifications.find_by(id: data["id"])
    return unless notification

    notification.read!

    # Update UI
    Turbo::StreamsChannel.broadcast_update_to(
      "notifications:#{current_user.id}",
      target: ActionView::RecordIdentifier.dom_id(notification),
      partial: "notifications/notification",
      locals: { notification: notification }
    )

    broadcast_count
  end

  def mark_all_as_read
    current_user.notifications.unread.update_all(read_at: Time.current)
    broadcast_count

    # Refresh notification list
    Turbo::StreamsChannel.broadcast_refresh_to("notifications:#{current_user.id}")
  end

  private

  def broadcast_count
    Turbo::StreamsChannel.broadcast_update_to(
      "notifications:#{current_user.id}",
      target: "notifications_count",
      html: current_user.notifications.unread.count.to_s
    )
  end
end
```

### Pattern 7: Email + Push + In-app

```ruby
# app/services/multi_channel_notifier.rb
class MultiChannelNotifier
  def initialize(notification)
    @notification = notification
    @user = notification.recipient
  end

  def deliver
    deliver_in_app
    deliver_email if should_email?
    deliver_push if should_push?
  end

  private

  def deliver_in_app
    # Already handled by Notification model callback
  end

  def deliver_email
    NotificationMailer.notify(@notification).deliver_later
  end

  def deliver_push
    WebPushJob.perform_later(@user, notification_payload)
  end

  def should_email?
    @user.notification_preference&.email_enabled? &&
      !@user.recently_active?
  end

  def should_push?
    @user.push_subscriptions.any? &&
      @user.notification_preference&.push_enabled?
  end

  def notification_payload
    {
      title: notification_title(@notification),
      body: notification_message(@notification),
      url: notification_url(@notification)
    }
  end
end
```

### Pattern 8: Notification Helper

```ruby
# app/helpers/notifications_helper.rb
module NotificationsHelper
  def notification_message(notification)
    case notification.notification_type
    when "comment"
      "#{notification.actor.name} commented on #{notification.data['post_title']}"
    when "mention"
      "#{notification.actor.name} mentioned you in a #{notification.notifiable_type.downcase}"
    when "follow"
      "#{notification.actor.name} started following you"
    when "like"
      "#{notification.actor.name} liked your #{notification.notifiable_type.downcase}"
    else
      notification.data["message"] || "You have a new notification"
    end
  end

  def notification_title(notification)
    case notification.notification_type
    when "comment" then "New Comment"
    when "mention" then "You were mentioned"
    when "follow" then "New Follower"
    when "like" then "New Like"
    else "Notification"
    end
  end

  def notification_icon(notification)
    case notification.notification_type
    when "comment" then "chat-bubble"
    when "mention" then "at-symbol"
    when "follow" then "user-plus"
    when "like" then "heart"
    else "bell"
    end
  end
end
```

## Database Schema

```ruby
# db/migrate/xxx_create_notifications.rb
class CreateNotifications < ActiveRecord::Migration[8.0]
  def change
    create_table :notifications do |t|
      t.references :recipient, null: false, foreign_key: { to_table: :users }
      t.references :actor, foreign_key: { to_table: :users }
      t.references :notifiable, polymorphic: true, null: false
      t.string :notification_type, null: false
      t.jsonb :data, default: {}
      t.datetime :read_at

      t.timestamps
    end

    add_index :notifications, [:recipient_id, :read_at]
    add_index :notifications, [:recipient_id, :created_at]
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No notification deduplication | Spam | Check recent duplicates |
| Synchronous email sending | Slow | Use background jobs |
| No user preferences | Annoyance | Add preference settings |
| Unbounded notification list | Performance | Paginate and archive |
| Missing actor null check | Errors | Handle system notifications |

## Related Skills

- [../turbo-streams/broadcasting.md](../turbo-streams/broadcasting.md): Broadcasting basics
- [chat.md](./chat.md): Chat implementation
- [../../background/SKILL.md](../../background/SKILL.md): Background jobs

## References

- [Turbo Streams Handbook](https://turbo.hotwired.dev/handbook/streams)
- [Web Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
