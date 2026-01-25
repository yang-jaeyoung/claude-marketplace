# Live Data Updates

## Overview

Live updates push real-time data changes to dashboards, monitoring systems, and dynamic content displays. This pattern covers streaming metrics, stock prices, sports scores, and any continuously changing data.

## When to Use

- When building real-time dashboards
- When displaying live metrics/KPIs
- When showing stock prices or financial data
- When implementing live sports scores
- When tracking real-time analytics

## Quick Start

### Basic Live Counter

```ruby
# app/models/dashboard_metric.rb
class DashboardMetric < ApplicationRecord
  broadcasts_refreshes_to :dashboard

  def self.update_metric(name, value)
    metric = find_or_initialize_by(name: name)
    metric.update!(value: value, updated_at: Time.current)
  end
end
```

```erb
<!-- app/views/dashboards/show.html.erb -->
<%= turbo_stream_from :dashboard %>

<div class="grid grid-cols-4 gap-4">
  <% @metrics.each do |metric| %>
    <%= render "dashboards/metric", metric: metric %>
  <% end %>
</div>
```

## Main Patterns

### Pattern 1: Periodic Metric Broadcasting

```ruby
# app/jobs/broadcast_metrics_job.rb
class BroadcastMetricsJob < ApplicationJob
  queue_as :default

  def perform
    metrics = calculate_metrics

    Turbo::StreamsChannel.broadcast_update_to(
      "dashboard",
      target: "live_metrics",
      partial: "dashboards/metrics",
      locals: { metrics: metrics }
    )
  end

  private

  def calculate_metrics
    {
      active_users: User.where("last_seen_at > ?", 5.minutes.ago).count,
      orders_today: Order.where(created_at: Date.current.all_day).count,
      revenue_today: Order.where(created_at: Date.current.all_day).sum(:total),
      pending_tasks: Task.pending.count
    }
  end
end

# config/recurring.yml (Solid Queue)
broadcast_metrics:
  class: BroadcastMetricsJob
  queue: default
  schedule: every 10 seconds
```

### Pattern 2: Stock Ticker with Morph

```ruby
# app/models/stock_quote.rb
class StockQuote < ApplicationRecord
  broadcasts_refreshes_to ->(quote) { "stocks:#{quote.symbol}" }

  def self.update_price(symbol, price, change)
    quote = find_or_initialize_by(symbol: symbol)
    quote.update!(
      price: price,
      change: change,
      change_percent: (change / (price - change) * 100).round(2),
      updated_at: Time.current
    )
  end

  def trend
    change >= 0 ? :up : :down
  end
end
```

```erb
<!-- app/views/stocks/_quote.html.erb -->
<div id="<%= dom_id(quote) %>"
     class="p-4 rounded-lg border <%= quote.trend == :up ? 'bg-green-50' : 'bg-red-50' %>">
  <div class="flex justify-between items-center">
    <span class="font-bold text-lg"><%= quote.symbol %></span>
    <span class="text-2xl font-mono">
      $<%= number_with_precision(quote.price, precision: 2) %>
    </span>
  </div>

  <div class="flex items-center gap-2 mt-2">
    <% if quote.trend == :up %>
      <svg class="w-4 h-4 text-green-600"><!-- Up arrow --></svg>
    <% else %>
      <svg class="w-4 h-4 text-red-600"><!-- Down arrow --></svg>
    <% end %>

    <span class="<%= quote.trend == :up ? 'text-green-600' : 'text-red-600' %>">
      <%= number_with_precision(quote.change, precision: 2, delimiter: '') %>
      (<%= quote.change_percent %>%)
    </span>
  </div>

  <time class="text-xs text-gray-500 mt-2 block">
    Updated <%= time_ago_in_words(quote.updated_at) %> ago
  </time>
</div>
```

### Pattern 3: Real-time Analytics Chart

```ruby
# app/channels/analytics_channel.rb
class AnalyticsChannel < ApplicationCable::Channel
  def subscribed
    stream_from "analytics:#{params[:metric]}"
  end
end

# app/services/analytics_broadcaster.rb
class AnalyticsBroadcaster
  def initialize(metric)
    @metric = metric
  end

  def push_datapoint(value, timestamp: Time.current)
    ActionCable.server.broadcast(
      "analytics:#{@metric}",
      {
        type: "datapoint",
        metric: @metric,
        value: value,
        timestamp: timestamp.iso8601
      }
    )
  end
end
```

```javascript
// app/javascript/controllers/live_chart_controller.js
import { Controller } from "@hotwired/stimulus"
import consumer from "../channels/consumer"
import Chart from "chart.js/auto"

export default class extends Controller {
  static values = { metric: String, maxPoints: { type: Number, default: 60 } }

  connect() {
    this.initChart()
    this.subscribeToUpdates()
  }

  initChart() {
    this.chart = new Chart(this.element, {
      type: "line",
      data: {
        labels: [],
        datasets: [{
          label: this.metricValue,
          data: [],
          borderColor: "rgb(59, 130, 246)",
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        animation: { duration: 0 },
        scales: {
          x: { display: false }
        }
      }
    })
  }

  subscribeToUpdates() {
    consumer.subscriptions.create(
      { channel: "AnalyticsChannel", metric: this.metricValue },
      {
        received: (data) => {
          if (data.type === "datapoint") {
            this.addDatapoint(data.value, data.timestamp)
          }
        }
      }
    )
  }

  addDatapoint(value, timestamp) {
    const chart = this.chart
    chart.data.labels.push(new Date(timestamp).toLocaleTimeString())
    chart.data.datasets[0].data.push(value)

    // Keep only last N points
    if (chart.data.labels.length > this.maxPointsValue) {
      chart.data.labels.shift()
      chart.data.datasets[0].data.shift()
    }

    chart.update("none")
  }
}
```

### Pattern 4: Server-Sent Events Alternative

```ruby
# app/controllers/live_updates_controller.rb
class LiveUpdatesController < ApplicationController
  include ActionController::Live

  def stream
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"

    sse = SSE.new(response.stream, retry: 300)

    loop do
      metrics = calculate_metrics
      sse.write(metrics, event: "metrics")
      sleep 5
    end
  rescue IOError
    # Client disconnected
  ensure
    sse.close
  end

  private

  def calculate_metrics
    {
      cpu: rand(0..100),
      memory: rand(40..80),
      requests: rand(100..500)
    }
  end
end
```

### Pattern 5: Activity Feed

```ruby
# app/models/activity.rb
class Activity < ApplicationRecord
  belongs_to :user
  belongs_to :trackable, polymorphic: true

  after_create_commit :broadcast_to_feed

  scope :recent, -> { order(created_at: :desc).limit(50) }

  private

  def broadcast_to_feed
    # To global feed
    broadcast_prepend_to(
      "activity_feed",
      target: "activities",
      partial: "activities/activity"
    )

    # To user's followers
    user.followers.find_each do |follower|
      broadcast_prepend_to(
        "user:#{follower.id}:feed",
        target: "activities",
        partial: "activities/activity"
      )
    end
  end
end

# app/models/concerns/trackable.rb
module Trackable
  extend ActiveSupport::Concern

  included do
    has_many :activities, as: :trackable, dependent: :destroy
    after_create_commit :create_activity
  end

  private

  def create_activity
    activities.create!(
      user: activity_user,
      action: "created",
      data: activity_data
    )
  end

  def activity_user
    respond_to?(:user) ? user : Current.user
  end

  def activity_data
    { title: respond_to?(:title) ? title : to_s }
  end
end
```

### Pattern 6: Progress Tracking

```ruby
# app/models/job_progress.rb
class JobProgress
  include ActiveModel::Model

  attr_accessor :job_id, :progress, :status, :message

  def broadcast
    Turbo::StreamsChannel.broadcast_update_to(
      "job:#{job_id}",
      target: "job_#{job_id}_progress",
      partial: "jobs/progress",
      locals: { progress: self }
    )
  end
end

# app/jobs/import_job.rb
class ImportJob < ApplicationJob
  def perform(import_id)
    import = Import.find(import_id)
    rows = import.rows
    total = rows.count

    rows.each_with_index do |row, index|
      process_row(row)

      # Broadcast progress every 10 rows
      if (index % 10).zero?
        JobProgress.new(
          job_id: import_id,
          progress: ((index + 1).to_f / total * 100).round,
          status: "processing",
          message: "Processing row #{index + 1} of #{total}"
        ).broadcast
      end
    end

    JobProgress.new(
      job_id: import_id,
      progress: 100,
      status: "complete",
      message: "Import complete!"
    ).broadcast
  end
end
```

```erb
<!-- app/views/jobs/_progress.html.erb -->
<div class="space-y-2">
  <div class="flex justify-between text-sm">
    <span><%= progress.message %></span>
    <span><%= progress.progress %>%</span>
  </div>

  <div class="w-full bg-gray-200 rounded-full h-2">
    <div class="<%= progress.status == 'complete' ? 'bg-green-500' : 'bg-blue-500' %>
                h-2 rounded-full transition-all duration-300"
         style="width: <%= progress.progress %>%">
    </div>
  </div>
</div>
```

### Pattern 7: Server Health Dashboard

```ruby
# app/services/system_monitor.rb
class SystemMonitor
  def self.broadcast_stats
    stats = collect_stats

    Turbo::StreamsChannel.broadcast_update_to(
      "system_health",
      target: "system_stats",
      partial: "admin/dashboards/system_stats",
      locals: { stats: stats }
    )
  end

  def self.collect_stats
    {
      ruby_version: RUBY_VERSION,
      rails_version: Rails.version,
      database_pool: ActiveRecord::Base.connection_pool.stat,
      memory_mb: `ps -o rss= -p #{Process.pid}`.to_i / 1024,
      cpu_percent: calculate_cpu,
      uptime: Time.current - Rails.application.config.boot_time,
      jobs_pending: SolidQueue::Job.where(finished_at: nil).count,
      cache_stats: Rails.cache.stats
    }
  end

  def self.calculate_cpu
    # Simplified CPU calculation
    `ps -o %cpu= -p #{Process.pid}`.strip.to_f
  end
end

# Scheduled job
# config/recurring.yml
system_health:
  class: SystemMonitor
  method: broadcast_stats
  schedule: every 30 seconds
```

### Pattern 8: Multi-tenant Dashboard Updates

```ruby
# app/services/tenant_dashboard_broadcaster.rb
class TenantDashboardBroadcaster
  def initialize(tenant)
    @tenant = tenant
  end

  def broadcast_kpis
    Turbo::StreamsChannel.broadcast_update_to(
      "tenant:#{@tenant.id}:dashboard",
      target: "kpi_container",
      partial: "dashboards/kpis",
      locals: { kpis: calculate_kpis }
    )
  end

  private

  def calculate_kpis
    {
      total_revenue: @tenant.orders.sum(:total),
      active_subscriptions: @tenant.subscriptions.active.count,
      new_users_today: @tenant.users.where(created_at: Date.current.all_day).count,
      support_tickets_open: @tenant.support_tickets.open.count
    }
  end
end

# Subscribe in view with tenant scoping
<%= turbo_stream_from "tenant:#{current_tenant.id}:dashboard" %>
```

## Performance Optimization

```ruby
# app/services/batched_broadcaster.rb
class BatchedBroadcaster
  def initialize(stream, batch_size: 10, interval: 1.second)
    @stream = stream
    @batch_size = batch_size
    @interval = interval
    @buffer = []
    @mutex = Mutex.new
  end

  def add(data)
    @mutex.synchronize do
      @buffer << data

      if @buffer.size >= @batch_size
        flush
      else
        schedule_flush unless @flush_scheduled
      end
    end
  end

  private

  def flush
    return if @buffer.empty?

    ActionCable.server.broadcast(@stream, {
      type: "batch",
      data: @buffer.dup
    })

    @buffer.clear
    @flush_scheduled = false
  end

  def schedule_flush
    @flush_scheduled = true
    Thread.new do
      sleep @interval
      @mutex.synchronize { flush }
    end
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Broadcasting every DB change | Overwhelming clients | Batch/throttle updates |
| No rate limiting | Resource exhaustion | Limit broadcast frequency |
| Sending full datasets | Bandwidth waste | Send deltas only |
| Synchronous broadcasting | Slow responses | Use background jobs |
| No client-side buffering | UI jank | Batch DOM updates |

## Related Skills

- [../turbo-streams/broadcasting.md](../turbo-streams/broadcasting.md): Broadcasting basics
- [notifications.md](./notifications.md): Notification patterns
- [../../background/SKILL.md](../../background/SKILL.md): Background jobs

## References

- [Turbo Streams Handbook](https://turbo.hotwired.dev/handbook/streams)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [Chart.js](https://www.chartjs.org/)
