# Notification System

## Overview

In-app notifications with real-time Turbo Stream updates, preferences management, read/unread states, and email digest integration. Build notification systems like GitHub, Twitter, or Linear.

## Prerequisites

- [hotwire/turbo-streams](../../hotwire/turbo-streams.md): Live updates
- [background/solid-queue](../../background/solid-queue.md): Email digests
- [models/polymorphic](../../models/polymorphic.md): Notifiable resources

## Quick Start

```ruby
# Gemfile
gem "noticed"

# Terminal
bundle install
rails noticed:install:migrations
rails db:migrate
```

## Implementation

### Step 1: Notification Model

```ruby
# app/models/notification.rb
class Notification < ApplicationRecord
  include Noticed::Model

  belongs_to :recipient, polymorphic: true
  belongs_to :record, polymorphic: true, optional: true

  scope :unread, -> { where(read_at: nil) }
  scope :recent, -> { order(created_at: :desc) }

  broadcasts_to :recipient

  def mark_as_read!
    update(read_at: Time.current) unless read?
  end

  def read?
    read_at.present?
  end
end

# app/notifications/comment_notification.rb
class CommentNotification < Noticed::Base
  deliver_by :database
  deliver_by :email, if: :email_notifications_enabled?

  param :comment

  def message
    "#{params[:comment].user.name} commented on your post"
  end

  def url
    post_path(params[:comment].post, anchor: dom_id(params[:comment]))
  end

  private

  def email_notifications_enabled?
    recipient.email_notifications_enabled?
  end
end

# app/models/user.rb
class User < ApplicationRecord
  has_many :notifications, as: :recipient, dependent: :destroy

  def unread_notifications_count
    notifications.unread.count
  end
end
```

### Step 2: Notification Controller

```ruby
# app/controllers/notifications_controller.rb
class NotificationsController < ApplicationController
  before_action :authenticate_user!

  def index
    @notifications = current_user
      .notifications
      .includes(:record)
      .recent
      .page(params[:page])

    # Mark visible notifications as read
    current_user.notifications.unread.limit(20).update_all(read_at: Time.current)
  end

  def mark_as_read
    notification = current_user.notifications.find(params[:id])
    notification.mark_as_read!

    redirect_to notification.url
  end

  def mark_all_as_read
    current_user.notifications.unread.update_all(read_at: Time.current)

    respond_to do |format|
      format.turbo_stream
      format.html { redirect_to notifications_path, notice: "All notifications marked as read" }
    end
  end
end
```

### Step 3: Real-time Notification UI

```erb
<!-- app/views/layouts/application.html.erb -->
<header>
  <%= turbo_stream_from current_user, :notifications %>

  <div class="notifications" data-controller="notifications">
    <button data-action="click->notifications#toggle">
      <svg class="w-6 h-6"><!-- Bell icon --></svg>
      <% if current_user.unread_notifications_count > 0 %>
        <span class="badge"><%= current_user.unread_notifications_count %></span>
      <% end %>
    </button>

    <%= turbo_frame_tag "notifications_dropdown", class: "hidden" do %>
      <%= render "notifications/dropdown" %>
    <% end %>
  </div>
</header>

<!-- app/views/notifications/_dropdown.html.erb -->
<div class="dropdown-content">
  <h3>Notifications</h3>

  <%= link_to "Mark all as read", mark_all_as_read_notifications_path, method: :post %>

  <div id="notifications_list">
    <%= render current_user.notifications.unread.limit(10) %>
  </div>

  <%= link_to "View all", notifications_path %>
</div>

<!-- app/views/notifications/_notification.html.erb -->
<%= link_to notification.url, class: "notification #{notification.read? ? 'read' : 'unread'}" do %>
  <div class="flex items-start gap-3 p-3">
    <%= image_tag notification.params[:actor]&.avatar_url, class: "w-10 h-10 rounded-full" %>
    <div class="flex-1">
      <p><%= notification.message %></p>
      <span class="text-sm text-gray-500"><%= time_ago_in_words(notification.created_at) %> ago</span>
    </div>
    <% unless notification.read? %>
      <div class="w-2 h-2 bg-blue-600 rounded-full"></div>
    <% end %>
  </div>
<% end %>
```

### Step 4: Usage in Models

```ruby
# app/models/comment.rb
class Comment < ApplicationRecord
  after_create :notify_post_author

  private

  def notify_post_author
    return if user == post.user

    CommentNotification.with(comment: self).deliver(post.user)
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Eager email sending | Notification spam | Use preferences and digest emails |
| No read tracking | Can't clear badge | Track `read_at` timestamp |
| Missing indexes | Slow queries | Index `recipient_id`, `read_at`, `created_at` |

## Related Skills

- [hotwire/turbo-streams](../../hotwire/turbo-streams.md): Real-time updates
- [background/solid-queue](../../background/solid-queue.md): Email processing
- [recipes/comments](./comments.md): Trigger notifications

## References

- [noticed](https://github.com/excid3/noticed): Notification system for Rails
