# Custom Turbo Streams

## Overview

When the built-in broadcasting helpers are insufficient, custom stream patterns provide flexibility for complex real-time scenarios including conditional updates, computed content, and multi-step workflows.

## When to Use

- When broadcasting requires complex logic
- When updates depend on computed values
- When broadcasting to dynamic stream combinations
- When implementing multi-user collaboration features

## Quick Start

### Custom Broadcasting Service

```ruby
# app/services/stream_broadcaster.rb
class StreamBroadcaster
  def initialize(stream_name)
    @stream_name = stream_name
  end

  def append(target:, partial:, locals: {})
    Turbo::StreamsChannel.broadcast_append_to(
      @stream_name,
      target: target,
      partial: partial,
      locals: locals
    )
  end

  def update(target:, content: nil, partial: nil, locals: {})
    options = { target: target }

    if content
      options[:html] = content
    else
      options[:partial] = partial
      options[:locals] = locals
    end

    Turbo::StreamsChannel.broadcast_update_to(@stream_name, **options)
  end
end
```

## Main Patterns

### Pattern 1: Computed Content Broadcasting

```ruby
class LeaderboardBroadcaster
  def initialize(competition)
    @competition = competition
  end

  def broadcast_update
    rankings = calculate_rankings

    Turbo::StreamsChannel.broadcast_replace_to(
      @competition,
      target: "leaderboard",
      partial: "competitions/leaderboard",
      locals: {
        rankings: rankings,
        updated_at: Time.current
      }
    )
  end

  private

  def calculate_rankings
    @competition.participants
      .includes(:scores)
      .map { |p| { user: p.user, score: p.total_score } }
      .sort_by { |r| -r[:score] }
      .each_with_index.map { |r, i| r.merge(rank: i + 1) }
  end
end

# Usage
LeaderboardBroadcaster.new(@competition).broadcast_update
```

### Pattern 2: Multi-Stream Broadcasting

```ruby
class OrderStatusBroadcaster
  def initialize(order)
    @order = order
  end

  def broadcast
    broadcast_to_customer
    broadcast_to_restaurant
    broadcast_to_driver if @order.driver
    broadcast_to_admin
  end

  private

  def broadcast_to_customer
    Turbo::StreamsChannel.broadcast_replace_to(
      "customer:#{@order.customer_id}",
      target: dom_id(@order),
      partial: "orders/customer_order",
      locals: { order: @order }
    )
  end

  def broadcast_to_restaurant
    Turbo::StreamsChannel.broadcast_replace_to(
      "restaurant:#{@order.restaurant_id}",
      target: dom_id(@order),
      partial: "orders/restaurant_order",
      locals: { order: @order }
    )
  end

  def broadcast_to_driver
    Turbo::StreamsChannel.broadcast_update_to(
      "driver:#{@order.driver_id}",
      target: "current_delivery",
      partial: "deliveries/current",
      locals: { order: @order }
    )
  end

  def broadcast_to_admin
    Turbo::StreamsChannel.broadcast_replace_to(
      "admin_dashboard",
      target: dom_id(@order),
      partial: "admin/orders/row",
      locals: { order: @order }
    )
  end

  def dom_id(record)
    ActionView::RecordIdentifier.dom_id(record)
  end
end
```

### Pattern 3: Conditional Broadcasting Based on User Role

```ruby
class AnnouncementBroadcaster
  def initialize(announcement)
    @announcement = announcement
  end

  def broadcast_to_authorized_users
    User.find_each do |user|
      next unless authorized?(user)

      Turbo::StreamsChannel.broadcast_prepend_to(
        "user:#{user.id}:announcements",
        target: "announcements",
        partial: partial_for(user),
        locals: { announcement: @announcement }
      )
    end
  end

  private

  def authorized?(user)
    case @announcement.visibility
    when "public" then true
    when "members" then user.member?
    when "admins" then user.admin?
    else false
    end
  end

  def partial_for(user)
    if user.admin?
      "announcements/admin_announcement"
    else
      "announcements/announcement"
    end
  end
end
```

### Pattern 4: Aggregate Updates

```ruby
class DashboardAggregator
  def initialize(organization)
    @organization = organization
  end

  def broadcast_metrics
    metrics = calculate_metrics

    Turbo::StreamsChannel.broadcast_update_to(
      "org:#{@organization.id}:dashboard",
      target: "metrics",
      partial: "dashboards/metrics",
      locals: { metrics: metrics }
    )
  end

  private

  def calculate_metrics
    {
      total_users: @organization.users.count,
      active_users: @organization.users.active.count,
      revenue_today: @organization.orders.today.sum(:total),
      orders_pending: @organization.orders.pending.count,
      satisfaction: calculate_satisfaction
    }
  end

  def calculate_satisfaction
    recent = @organization.reviews.recent
    return 0 if recent.empty?
    (recent.average(:rating) * 20).round
  end
end

# Trigger periodically
DashboardRefreshJob.perform_later(@organization)
```

### Pattern 5: Streaming with Actions

```ruby
class TaskBroadcaster
  include ActionView::RecordIdentifier

  def initialize(task)
    @task = task
  end

  def broadcast_state_change(action)
    case action
    when :create then broadcast_create
    when :start then broadcast_start
    when :complete then broadcast_complete
    when :archive then broadcast_archive
    end
  end

  private

  def broadcast_create
    broadcast_prepend("pending_tasks")
  end

  def broadcast_start
    broadcast_move(from: "pending_tasks", to: "in_progress_tasks")
  end

  def broadcast_complete
    broadcast_move(from: "in_progress_tasks", to: "completed_tasks")
    broadcast_celebration
  end

  def broadcast_archive
    Turbo::StreamsChannel.broadcast_remove_to(
      @task.project,
      target: dom_id(@task)
    )
  end

  def broadcast_move(from:, to:)
    Turbo::StreamsChannel.broadcast_remove_to(
      @task.project,
      target: dom_id(@task)
    )

    Turbo::StreamsChannel.broadcast_append_to(
      @task.project,
      target: to,
      partial: "tasks/task",
      locals: { task: @task }
    )
  end

  def broadcast_prepend(target)
    Turbo::StreamsChannel.broadcast_prepend_to(
      @task.project,
      target: target,
      partial: "tasks/task",
      locals: { task: @task }
    )
  end

  def broadcast_celebration
    Turbo::StreamsChannel.broadcast_append_to(
      @task.project,
      target: "celebrations",
      partial: "shared/celebration",
      locals: { message: "Task completed!", user: @task.assignee }
    )
  end
end
```

### Pattern 6: Streaming Turbo Stream Tags

```ruby
class CustomStreamRenderer
  include Turbo::Streams::ActionHelper

  def broadcast_multi_action(stream, actions)
    html = actions.map do |action|
      send("render_#{action[:type]}", action)
    end.join

    ActionCable.server.broadcast(stream, html)
  end

  private

  def render_append(action)
    turbo_stream_action_tag(
      :append,
      target: action[:target],
      template: render_partial(action[:partial], action[:locals])
    )
  end

  def render_remove(action)
    turbo_stream_action_tag(:remove, target: action[:target])
  end

  def render_partial(partial, locals)
    ApplicationController.render(partial: partial, locals: locals || {})
  end
end

# Usage
CustomStreamRenderer.new.broadcast_multi_action(
  "project_updates",
  [
    { type: :append, target: "tasks", partial: "tasks/task", locals: { task: @task } },
    { type: :remove, target: "empty_state" }
  ]
)
```

### Pattern 7: Debounced Broadcasting

```ruby
class DebouncedBroadcaster
  def initialize(stream_name, delay: 1.second)
    @stream_name = stream_name
    @delay = delay
  end

  def broadcast(target:, partial:, locals: {})
    key = "debounce:#{@stream_name}:#{target}"

    # Cancel previous scheduled broadcast
    Sidekiq::ScheduledSet.new.each do |job|
      job.delete if job.args.first == key
    end

    # Schedule new broadcast
    DebouncedBroadcastJob.set(wait: @delay).perform_later(
      key,
      @stream_name,
      target,
      partial,
      locals
    )
  end
end

# app/jobs/debounced_broadcast_job.rb
class DebouncedBroadcastJob < ApplicationJob
  def perform(_key, stream_name, target, partial, locals)
    Turbo::StreamsChannel.broadcast_update_to(
      stream_name,
      target: target,
      partial: partial,
      locals: locals.symbolize_keys
    )
  end
end
```

### Pattern 8: Streaming with Presence Data

```ruby
class PresenceAwareBroadcaster
  def initialize(room)
    @room = room
  end

  def broadcast_message(message)
    online_users = get_online_users

    Turbo::StreamsChannel.broadcast_append_to(
      @room,
      target: "messages",
      partial: "messages/message",
      locals: {
        message: message,
        read_by: online_users
      }
    )

    # Update read receipts for online users
    mark_as_read(message, online_users)
  end

  private

  def get_online_users
    key = "room:#{@room.id}:presence"
    user_ids = Rails.cache.read(key) || []
    User.where(id: user_ids)
  end

  def mark_as_read(message, users)
    users.each do |user|
      message.read_receipts.find_or_create_by(user: user)
    end
  end
end
```

## Testing Custom Streams

```ruby
# test/services/task_broadcaster_test.rb
require "test_helper"

class TaskBroadcasterTest < ActiveSupport::TestCase
  include Turbo::Broadcastable::TestHelper

  test "broadcasts task creation" do
    project = projects(:one)
    task = tasks(:pending)

    assert_broadcast_on project, stream: Turbo::StreamsChannel do
      TaskBroadcaster.new(task).broadcast_state_change(:create)
    end
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| N+1 broadcasts | Performance issues | Batch and aggregate |
| Synchronous heavy computation | Slow response | Use background jobs |
| Broadcasting to too many streams | Confusion | Consolidate streams |
| Not testing broadcasts | Bugs in production | Use test helpers |

## Related Skills

- [broadcasting.md](./broadcasting.md): Basic broadcasting
- [model-callbacks.md](./model-callbacks.md): Declarative broadcasting
- [authorization.md](./authorization.md): Securing streams

## References

- [Turbo Streams API](https://github.com/hotwired/turbo-rails)
- [Action Cable Testing](https://guides.rubyonrails.org/testing.html#testing-action-cable)
