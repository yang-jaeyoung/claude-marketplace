# Turbo Streams Model Callbacks

## Overview

Rails 8 provides declarative broadcasting helpers that automatically broadcast Turbo Stream updates when models are created, updated, or destroyed. These helpers simplify real-time features by eliminating boilerplate callback code.

## When to Use

- When models should automatically broadcast changes
- When implementing real-time CRUD updates
- When simplifying broadcast logic
- When using Rails 8 page refresh/morphing

## Quick Start

### broadcasts_to (Full CRUD)

```ruby
# app/models/message.rb
class Message < ApplicationRecord
  belongs_to :room

  # Broadcasts create, update, and destroy
  broadcasts_to :room
end
```

```erb
<!-- app/views/rooms/show.html.erb -->
<%= turbo_stream_from @room %>

<div id="messages">
  <%= render @room.messages %>
</div>
```

### broadcasts_refreshes (Rails 8 Morphing)

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  # Triggers page refresh for all subscribers
  broadcasts_refreshes
end
```

## Main Patterns

### Pattern 1: Basic broadcasts_to

```ruby
class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user

  # Stream to post (post_comments stream)
  broadcasts_to :post

  # This automatically does:
  # after_create_commit -> { broadcast_append_to(post) }
  # after_update_commit -> { broadcast_replace_to(post) }
  # after_destroy_commit -> { broadcast_remove_to(post) }
end
```

### Pattern 2: Custom Target Container

```ruby
class Task < ApplicationRecord
  belongs_to :project

  # Specify target container
  broadcasts_to :project, target: "project_tasks"

  # DOM should have:
  # <div id="project_tasks">...</div>
end
```

### Pattern 3: Custom Partial

```ruby
class Notification < ApplicationRecord
  belongs_to :user

  broadcasts_to ->(notification) { "notifications:#{notification.user_id}" },
                partial: "notifications/toast",
                target: "toasts"
end
```

### Pattern 4: Prepend Instead of Append

```ruby
class Message < ApplicationRecord
  belongs_to :room

  # New messages appear at top
  broadcasts_to :room, inserts_by: :prepend
end
```

### Pattern 5: broadcasts_refreshes for Morphing

```ruby
# app/models/dashboard_metric.rb
class DashboardMetric < ApplicationRecord
  # Triggers full page morph on any change
  broadcasts_refreshes

  # Or scope to specific stream
  broadcasts_refreshes_to :dashboard
end
```

```erb
<!-- Layout with morphing enabled -->
<head>
  <meta name="turbo-refresh-method" content="morph">
  <meta name="turbo-refresh-scroll" content="preserve">
</head>

<body>
  <%= turbo_stream_from :dashboard %>
  <!-- ... -->
</body>
```

### Pattern 6: Multiple Broadcast Targets

```ruby
class Article < ApplicationRecord
  belongs_to :author, class_name: "User"
  belongs_to :category

  # Broadcast to multiple streams
  broadcasts_to :category, target: "category_articles"
  broadcasts_to ->(article) { "user:#{article.author_id}:articles" },
                target: "my_articles"
end
```

### Pattern 7: Conditional Broadcasting

```ruby
class Post < ApplicationRecord
  broadcasts_to :blog, if: :published?

  # Or use lambda for complex conditions
  broadcasts_to :blog,
                if: -> { published? && !draft? }
end
```

### Pattern 8: Custom Callback Methods

```ruby
class Order < ApplicationRecord
  belongs_to :user

  # Override default behavior
  after_create_commit :broadcast_order_created
  after_update_commit :broadcast_order_status, if: :saved_change_to_status?
  after_destroy_commit :broadcast_order_removed

  private

  def broadcast_order_created
    # Notify user
    broadcast_prepend_to(
      user,
      target: "orders",
      partial: "orders/order"
    )

    # Notify admin
    broadcast_prepend_to(
      "admin_orders",
      target: "pending_orders",
      partial: "admin/orders/order"
    )
  end

  def broadcast_order_status
    broadcast_replace_to(user)

    if completed?
      broadcast_remove_to("admin_orders", target: dom_id(self))
      broadcast_append_to("admin_completed", target: "completed_orders")
    end
  end

  def broadcast_order_removed
    broadcast_remove_to(user)
    broadcast_remove_to("admin_orders")
  end
end
```

### Pattern 9: Broadcasting with Locals

```ruby
class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user

  after_create_commit :broadcast_with_context

  private

  def broadcast_with_context
    broadcast_prepend_to(
      post,
      target: "comments",
      partial: "comments/comment",
      locals: {
        comment: self,
        show_actions: true,
        highlight: true
      }
    )
  end
end
```

### Pattern 10: Later Broadcasting with Jobs

```ruby
class Report < ApplicationRecord
  broadcasts_to :dashboard

  # For heavy computations, use later
  after_create_commit :schedule_broadcast

  private

  def schedule_broadcast
    BroadcastReportJob.perform_later(self)
  end
end

# app/jobs/broadcast_report_job.rb
class BroadcastReportJob < ApplicationJob
  def perform(report)
    # After heavy computation
    report.broadcast_replace_to(
      report.dashboard,
      target: dom_id(report),
      partial: "reports/report",
      locals: { report: report, computed_data: compute_data(report) }
    )
  end
end
```

## Broadcast Helper Methods

All these methods are available on models including `Turbo::Broadcastable`:

```ruby
# Instance methods
broadcast_append_to(stream, **options)
broadcast_prepend_to(stream, **options)
broadcast_replace_to(stream, **options)
broadcast_update_to(stream, **options)
broadcast_remove_to(stream, **options)
broadcast_before_to(stream, **options)
broadcast_after_to(stream, **options)
broadcast_refresh_to(stream)

# Shorthand (uses model as stream)
broadcast_append(**options)
broadcast_prepend(**options)
broadcast_replace(**options)
broadcast_update(**options)
broadcast_remove
broadcast_refresh
```

## Options Reference

| Option | Type | Description |
|--------|------|-------------|
| `target` | String | DOM element ID to target |
| `targets` | String | CSS selector for multiple targets |
| `partial` | String | Partial path to render |
| `locals` | Hash | Variables for partial |
| `inserts_by` | Symbol | `:append` (default) or `:prepend` |
| `if` | Proc/Symbol | Condition for broadcasting |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Broadcasting in before_save | Record not persisted | Use after_commit |
| Broadcasting without transaction safety | Inconsistent state | Use after_commit |
| Rendering expensive partials | Slow broadcasts | Cache or simplify |
| Missing stream subscription | No updates received | Add turbo_stream_from |
| Circular broadcasts | Infinite loops | Check for cycles |

## Related Skills

- [broadcasting.md](./broadcasting.md): Manual broadcasting patterns
- [custom-streams.md](./custom-streams.md): Complex broadcasting logic
- [../../hotwire/SKILL.md](../../hotwire/SKILL.md): Turbo Streams basics

## References

- [Turbo Rails Broadcastable](https://github.com/hotwired/turbo-rails/blob/main/app/models/concerns/turbo/broadcastable.rb)
- [Rails 8 Page Refresh](https://turbo.hotwired.dev/handbook/page_refreshes)
