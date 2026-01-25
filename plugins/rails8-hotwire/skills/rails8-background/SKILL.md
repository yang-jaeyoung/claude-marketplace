# rails8-background

Background Jobs Skill

## Invocation
`/rails8:background`

## Description
Guides Solid Queue, ActiveJob, and background processing.

## Topics
- Solid Queue setup (Rails 8 default)
- ActiveJob basics
- Job scheduling
- Retry strategies
- Job priorities
- Job monitoring
- Async email sending

## Quick Start
```ruby
# config/application.rb
config.active_job.queue_adapter = :solid_queue

# Job definition
class ProcessOrderJob < ApplicationJob
  queue_as :default
  retry_on StandardError, wait: :polynomially_longer, attempts: 5

  def perform(order_id)
    Order.find(order_id).process!
  end
end

# Invocation
ProcessOrderJob.perform_later(order.id)
```

## Knowledge Reference
For comprehensive documentation, see:
- **[knowledge/background/SKILL.md](../../knowledge/background/SKILL.md)**: Full job patterns, Solid Queue, and Sidekiq setup

## Related Agents
- `rails-executor`: Job implementation
- `rails-architect`: Queue architecture

## Related Skills
- [rails8-realtime](../rails8-realtime/SKILL.md): Real-time notifications from jobs
- [rails8-deploy](../rails8-deploy/SKILL.md): Production queue setup
