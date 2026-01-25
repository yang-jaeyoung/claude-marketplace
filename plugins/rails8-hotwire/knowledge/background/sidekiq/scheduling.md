# Sidekiq Scheduling

## Overview

Cron-like recurring job scheduling with Sidekiq using sidekiq-cron or sidekiq-scheduler gems. Run jobs at specific times or intervals without external cron daemon.

## When to Use

- Recurring tasks (hourly, daily, weekly)
- Scheduled maintenance jobs
- Periodic data syncs
- Time-based notifications
- Cleanup operations

## Quick Start

### Install sidekiq-cron

```ruby
# Gemfile
gem "sidekiq-cron"

bundle install
```

### Basic Configuration

```ruby
# config/initializers/sidekiq.rb
require "sidekiq-cron"

Sidekiq::Cron::Job.create(
  name: "Daily Cleanup",
  cron: "0 3 * * *",  # Every day at 3 AM
  class: "CleanupJob"
)
```

## Main Patterns

### Pattern 1: Configuration File

```yaml
# config/schedule.yml
daily_cleanup:
  cron: "0 3 * * *"
  class: "CleanupJob"
  queue: low
  description: "Delete old sessions and temp files"

hourly_stats:
  cron: "0 * * * *"
  class: "UpdateStatsJob"
  queue: default

weekly_report:
  cron: "0 9 * * 1"
  class: "WeeklyReportJob"
  args: ["weekly"]
  queue: low
  description: "Send weekly summary every Monday at 9 AM"

every_15_minutes:
  cron: "*/15 * * * *"
  class: "SyncExternalDataJob"
  queue: high

monthly_billing:
  cron: "0 0 1 * *"
  class: "BillingJob"
  args:
    - monthly
  queue: critical
  description: "Process monthly billing on first day of month"
```

```ruby
# config/initializers/sidekiq.rb
require "sidekiq-cron"

schedule_file = Rails.root.join("config/schedule.yml")

if File.exist?(schedule_file)
  schedule = YAML.load_file(schedule_file)

  schedule.each do |name, config|
    Sidekiq::Cron::Job.create(
      name: name,
      cron: config["cron"],
      class: config["class"],
      queue: config.fetch("queue", "default"),
      args: config.fetch("args", []),
      description: config["description"]
    )
  end
end
```

### Pattern 2: Dynamic Schedule Creation

```ruby
# app/models/scheduled_task.rb
class ScheduledTask < ApplicationRecord
  # Columns: name, cron_expression, job_class, enabled, args

  after_save :update_sidekiq_cron
  after_destroy :remove_sidekiq_cron

  private

  def update_sidekiq_cron
    if enabled?
      Sidekiq::Cron::Job.create(
        name: name,
        cron: cron_expression,
        class: job_class,
        args: args || []
      )
    else
      remove_sidekiq_cron
    end
  end

  def remove_sidekiq_cron
    job = Sidekiq::Cron::Job.find(name)
    job&.destroy
  end
end

# Usage in admin interface
ScheduledTask.create!(
  name: "cleanup_sessions",
  cron_expression: "0 3 * * *",
  job_class: "CleanupJob",
  enabled: true
)
```

### Pattern 3: Common Cron Patterns

```ruby
# config/initializers/sidekiq.rb

# Every minute
Sidekiq::Cron::Job.create(
  name: "Health Check",
  cron: "* * * * *",
  class: "HealthCheckJob"
)

# Every 5 minutes
Sidekiq::Cron::Job.create(
  name: "Quick Sync",
  cron: "*/5 * * * *",
  class: "QuickSyncJob"
)

# Every hour at minute 30
Sidekiq::Cron::Job.create(
  name: "Hourly Report",
  cron: "30 * * * *",
  class: "HourlyReportJob"
)

# Business hours only (9 AM - 5 PM, Monday-Friday)
Sidekiq::Cron::Job.create(
  name: "Business Hours Sync",
  cron: "0 9-17 * * 1-5",
  class: "BusinessSyncJob"
)

# First day of every month
Sidekiq::Cron::Job.create(
  name: "Monthly Billing",
  cron: "0 0 1 * *",
  class: "BillingJob"
)

# Last day of every month (using special syntax)
Sidekiq::Cron::Job.create(
  name: "Month End Report",
  cron: "0 23 L * *",  # L = last day
  class: "MonthEndReportJob"
)

# Specific days: Monday and Friday at 9 AM
Sidekiq::Cron::Job.create(
  name: "Twice Weekly Check",
  cron: "0 9 * * 1,5",
  class: "CheckJob"
)
```

**Cron Syntax Reference:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-6, Sun=0, or names: SUN-SAT)
│ │ │ └─── Month (1-12, or names: JAN-DEC)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)

Special characters:
* = Any value
*/5 = Every 5 units
1-5 = Range from 1 to 5
1,3,5 = Values 1, 3, and 5
L = Last day of month (day field only)
```

### Pattern 4: Job with Arguments

```ruby
# app/jobs/report_job.rb
class ReportJob < ApplicationJob
  queue_as :default

  def perform(report_type, recipient_email = nil)
    report = generate_report(report_type)

    if recipient_email
      ReportMailer.send_report(recipient_email, report).deliver_now
    else
      # Send to all admins
      User.admin.each do |admin|
        ReportMailer.send_report(admin.email, report).deliver_now
      end
    end
  end

  private

  def generate_report(type)
    case type
    when "daily"
      DailyReport.new.generate
    when "weekly"
      WeeklyReport.new.generate
    when "monthly"
      MonthlyReport.new.generate
    end
  end
end

# config/schedule.yml
daily_report:
  cron: "0 8 * * *"
  class: "ReportJob"
  args:
    - "daily"
    - "reports@example.com"

weekly_report:
  cron: "0 8 * * 1"
  class: "ReportJob"
  args:
    - "weekly"
    # No email - sends to all admins
```

### Pattern 5: Conditional Scheduling

```ruby
# app/jobs/business_hours_job.rb
class BusinessHoursJob < ApplicationJob
  queue_as :default

  def perform
    # Double-check we're in business hours
    return unless Time.current.on_weekday? && Time.current.hour.between?(9, 17)

    # Run business logic
    BusinessLogic.process
  end
end

# Schedule every hour, but job checks if it should run
Sidekiq::Cron::Job.create(
  name: "Business Hours Check",
  cron: "0 * * * *",
  class: "BusinessHoursJob"
)
```

### Pattern 6: Timezone-Aware Scheduling

```ruby
# config/application.rb
config.time_zone = "America/New_York"

# config/initializers/sidekiq.rb
Sidekiq::Cron::Job.create(
  name: "Daily Report (EST)",
  cron: "0 9 * * *",  # 9 AM Eastern
  class: "DailyReportJob"
)

# For multiple timezones
Sidekiq::Cron::Job.create(
  name: "Daily Report (PST)",
  cron: "0 9 * * *",
  class: "DailyReportJob",
  args: ["America/Los_Angeles"]
)

# app/jobs/daily_report_job.rb
class DailyReportJob < ApplicationJob
  def perform(timezone = "America/New_York")
    Time.use_zone(timezone) do
      # Generate report in specified timezone
      Report.generate_daily
    end
  end
end
```

### Pattern 7: Monitoring and Management

```ruby
# List all scheduled jobs
Sidekiq::Cron::Job.all

# Find specific job
job = Sidekiq::Cron::Job.find("daily_cleanup")

# Check job details
job.name              # "daily_cleanup"
job.cron              # "0 3 * * *"
job.last_enqueue_time # Last run timestamp
job.enabled?          # true/false

# Manually trigger job
job.enque!

# Disable job
job.disable!

# Enable job
job.enable!

# Delete job
job.destroy

# Get next scheduled time
job.next_enqueue_time
```

```ruby
# Admin dashboard helper
class ScheduledJobsController < ApplicationController
  def index
    @jobs = Sidekiq::Cron::Job.all.map do |job|
      {
        name: job.name,
        cron: job.cron,
        last_run: job.last_enqueue_time,
        next_run: job.next_enqueue_time,
        enabled: job.enabled?
      }
    end
  end

  def trigger
    job = Sidekiq::Cron::Job.find(params[:id])
    job.enque!
    redirect_to scheduled_jobs_path, notice: "Job triggered"
  end
end
```

### Pattern 8: Alternative - sidekiq-scheduler

```ruby
# Gemfile
gem "sidekiq-scheduler"

# config/sidekiq.yml
:schedule:
  daily_cleanup:
    cron: "0 3 * * *"
    class: CleanupJob
    queue: low

  every_5_minutes:
    every: "5m"
    class: QuickSyncJob

  once_per_day:
    every: 1d
    class: DailyTaskJob
    at: "09:00"

  interval_with_args:
    interval: 3600  # Every hour in seconds
    class: HourlyJob
    args:
      - "arg1"
      - "arg2"
```

## Advanced Patterns

### Retry Failed Scheduled Jobs

```ruby
# app/jobs/resilient_scheduled_job.rb
class ResilientScheduledJob < ApplicationJob
  queue_as :default

  retry_on StandardError, wait: 5.minutes, attempts: 3

  sidekiq_retries_exhausted do |job, exception|
    # Notify admins when scheduled job fails
    AdminMailer.scheduled_job_failed(
      job.class.name,
      exception.message
    ).deliver_now
  end

  def perform
    # Critical scheduled task
  end
end
```

### Preventing Overlapping Jobs

```ruby
# Use sidekiq-unique-jobs with scheduled jobs
class NonOverlappingJob < ApplicationJob
  queue_as :default

  sidekiq_options(
    lock: :while_executing,
    on_conflict: :log
  )

  def perform
    # Long-running task that shouldn't overlap
    # If job is still running when next cron triggers, skip
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Hardcoding schedules | Hard to change without deploy | Use config file or database |
| No timezone consideration | Wrong execution time | Set explicit timezone |
| Overlapping jobs | Resource contention | Use unique jobs or checks |
| Missing error handling | Silent failures | Add retries and notifications |
| No monitoring | Can't detect if jobs stop running | Monitor last_enqueue_time |

```ruby
# Bad: Hardcoded in initializer
Sidekiq::Cron::Job.create(cron: "0 3 * * *", ...)

# Good: Config file
schedule = YAML.load_file("config/schedule.yml")

# Bad: No timezone awareness
cron: "0 9 * * *"  # Which timezone?

# Good: Explicit timezone in job
Time.use_zone("America/New_York") { ... }
```

## Testing Scheduled Jobs

```ruby
# spec/jobs/cleanup_job_spec.rb
RSpec.describe CleanupJob do
  describe "#perform" do
    it "deletes old sessions" do
      old_session = create(:session, updated_at: 31.days.ago)
      new_session = create(:session, updated_at: 1.day.ago)

      CleanupJob.perform_now

      expect(Session.exists?(old_session.id)).to be false
      expect(Session.exists?(new_session.id)).to be true
    end
  end
end

# spec/features/scheduled_jobs_spec.rb
RSpec.describe "Scheduled jobs" do
  it "creates daily cleanup job" do
    job = Sidekiq::Cron::Job.find("daily_cleanup")

    expect(job).to be_present
    expect(job.cron).to eq("0 3 * * *")
    expect(job.klass).to eq("CleanupJob")
  end
end
```

## Related Skills

- [setup](./setup.md): Sidekiq installation
- [jobs](./jobs.md): Creating job classes
- [monitoring](./monitoring.md): Dashboard and alerts
- [solid-queue/configuration](../solid-queue/configuration.md): Alternative scheduling

## References

- [sidekiq-cron](https://github.com/sidekiq-cron/sidekiq-cron)
- [sidekiq-scheduler](https://github.com/sidekiq-scheduler/sidekiq-scheduler)
- [Crontab Guru](https://crontab.guru/) (cron expression tester)
- [Sidekiq Scheduling Best Practices](https://github.com/sidekiq/sidekiq/wiki/Scheduled-Jobs)
