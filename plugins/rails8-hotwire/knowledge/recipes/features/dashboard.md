# Dashboard with Charts

## Overview

Real-time dashboard with Chartkick charts, counter caches, Russian doll caching, and Turbo Stream updates.

## Prerequisites

- [hotwire/turbo-streams](../../hotwire/turbo-streams.md)
- [models/queries](../../models/queries.md)

## Quick Start

```ruby
gem "chartkick"
gem "groupdate"
```

## Implementation

### Dashboard Controller

```ruby
# app/controllers/dashboards_controller.rb
class DashboardsController < ApplicationController
  def show
    @stats = DashboardStats.new(current_account)
  end
end

# app/services/dashboard_stats.rb
class DashboardStats
  def initialize(account)
    @account = account
  end

  def total_users
    Rails.cache.fetch("#{cache_key}/total_users", expires_in: 1.hour) do
      @account.users.count
    end
  end

  def revenue_by_month
    Rails.cache.fetch("#{cache_key}/revenue", expires_in: 1.day) do
      @account.payments.group_by_month(:created_at).sum(:amount)
    end
  end

  def signups_by_day
    @account.users.group_by_day(:created_at, last: 30).count
  end

  private

  def cache_key
    "dashboard/#{@account.id}/#{@account.updated_at.to_i}"
  end
end
```

### Dashboard View

```erb
<!-- app/views/dashboards/show.html.erb -->
<div class="grid grid-cols-4 gap-4 mb-8">
  <div class="stat-card">
    <h3>Total Users</h3>
    <p class="text-3xl"><%= @stats.total_users %></p>
  </div>
</div>

<div class="mb-8">
  <%= line_chart @stats.signups_by_day, curve: false %>
</div>

<div class="mb-8">
  <%= column_chart @stats.revenue_by_month, prefix: "$" %>
</div>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No caching | Slow queries | Use fragment caching |
| N+1 queries | Poor performance | Eager load associations |
| Client-side charting | Slow rendering | Use server-side Chartkick |

## Related Skills

- [hotwire/turbo-frames](../../hotwire/turbo-frames.md)
- [models/queries](../../models/queries.md)

## References

- [Chartkick](https://chartkick.com/): Simple charts
- [Groupdate](https://github.com/ankane/groupdate): Time-based grouping
