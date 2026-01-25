# Background Jobs and Email Sequences

## Completion Job

```ruby
# app/jobs/onboarding_complete_job.rb
class OnboardingCompleteJob < ApplicationJob
  queue_as :default

  def perform(account_id)
    account = Account.find(account_id)

    # Send welcome email
    account.users.each do |user|
      OnboardingMailer.welcome(user).deliver_now
    end

    # Schedule follow-up emails
    OnboardingSequenceJob.set(wait: 3.days).perform_later(account_id)

    # Track completion event (analytics)
    Analytics.track(
      user_id: account.users.first.id,
      event: "Onboarding Completed",
      properties: {
        account_id: account.id,
        team_size: account.users.count
      }
    )
  end
end
```

## Email Sequence Job

```ruby
# app/jobs/onboarding_sequence_job.rb
class OnboardingSequenceJob < ApplicationJob
  queue_as :default

  def perform(account_id, day = 1)
    account = Account.find(account_id)
    owner = account.users.find_by(role: "owner")

    return unless owner

    case day
    when 1
      OnboardingMailer.day_3_tips(owner).deliver_now
      OnboardingSequenceJob.set(wait: 4.days).perform_later(account_id, 2)
    when 2
      OnboardingMailer.day_7_checkin(owner).deliver_now
      OnboardingSequenceJob.set(wait: 7.days).perform_later(account_id, 3)
    when 3
      OnboardingMailer.day_14_feedback(owner).deliver_now
    end
  end
end
```

## Onboarding Mailer

```ruby
# app/mailers/onboarding_mailer.rb
class OnboardingMailer < ApplicationMailer
  def welcome(user)
    @user = user
    @account = user.account

    mail(to: @user.email, subject: "Welcome to #{@account.name}!")
  end

  def day_3_tips(user)
    @user = user
    mail(to: @user.email, subject: "3 tips to get the most out of your workspace")
  end

  def day_7_checkin(user)
    @user = user
    mail(to: @user.email, subject: "How's it going?")
  end

  def day_14_feedback(user)
    @user = user
    mail(to: @user.email, subject: "We'd love your feedback")
  end
end
```

## Email Templates

```erb
<!-- app/views/onboarding_mailer/welcome.html.erb -->
<h1>Welcome to <%= @account.name %>, <%= @user.name %>! 🎉</h1>

<p>You're all set up and ready to go. Here are a few things to try:</p>

<ul>
  <li>Invite your team members</li>
  <li>Create your first project</li>
  <li>Explore the dashboard</li>
</ul>

<%= link_to "Get Started", root_url, class: "button" %>
```

```erb
<!-- app/views/onboarding_mailer/day_3_tips.html.erb -->
<h1>3 Tips to Master <%= @account.name %></h1>

<div class="tip">
  <h2>1. Use keyboard shortcuts</h2>
  <p>Press <kbd>?</kbd> anywhere to see available shortcuts.</p>
</div>

<div class="tip">
  <h2>2. Customize your workspace</h2>
  <p>Drag and drop to rearrange your dashboard widgets.</p>
</div>

<div class="tip">
  <h2>3. Set up integrations</h2>
  <p>Connect your favorite tools in Settings → Integrations.</p>
</div>
```

## Progress Tracking Stimulus Controller

```javascript
// app/javascript/controllers/onboarding_progress_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  connect() {
    // Auto-save progress on visibility change
    document.addEventListener("visibilitychange", this.saveProgress.bind(this))

    // Track time spent on each step
    this.startTime = Date.now()
  }

  disconnect() {
    document.removeEventListener("visibilitychange", this.saveProgress.bind(this))
    this.saveProgress()
  }

  saveProgress() {
    const timeSpent = Math.floor((Date.now() - this.startTime) / 1000)

    fetch("/api/onboarding/progress", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": document.querySelector("[name='csrf-token']").content
      },
      body: JSON.stringify({
        step: this.element.dataset.currentStep,
        time_spent: timeSpent
      })
    })
  }
}
```

## Email Sequence Timeline

```
Day 0:  Complete onboarding
        ↓
        [OnboardingCompleteJob]
        - Send welcome email
        - Schedule day 3 email
        ↓
Day 3:  [OnboardingSequenceJob day=1]
        - Send tips email
        - Schedule day 7 email
        ↓
Day 7:  [OnboardingSequenceJob day=2]
        - Send check-in email
        - Schedule day 14 email
        ↓
Day 14: [OnboardingSequenceJob day=3]
        - Send feedback request
```

## Job Queue Configuration

```ruby
# config/environments/production.rb
Rails.application.configure do
  # Use Solid Queue (Rails 8 default)
  config.active_job.queue_adapter = :solid_queue

  # Or use Sidekiq
  # config.active_job.queue_adapter = :sidekiq
end
```

```yaml
# config/queue.yml (Solid Queue)
production:
  dispatchers:
    - polling_interval: 1
      batch_size: 500
  workers:
    - queues: default
      threads: 3
      processes: 2
```

## Testing Jobs

```ruby
# spec/jobs/onboarding_complete_job_spec.rb
require "rails_helper"

RSpec.describe OnboardingCompleteJob, type: :job do
  let(:account) { create(:account) }
  let(:user) { create(:user, account: account) }

  it "sends welcome email to all users" do
    expect {
      OnboardingCompleteJob.perform_now(account.id)
    }.to change { ActionMailer::Base.deliveries.count }.by(1)
  end

  it "schedules follow-up sequence" do
    OnboardingCompleteJob.perform_now(account.id)

    expect(OnboardingSequenceJob)
      .to have_been_enqueued
      .with(account.id, 1)
      .at(3.days.from_now)
  end
end

# spec/jobs/onboarding_sequence_job_spec.rb
require "rails_helper"

RSpec.describe OnboardingSequenceJob, type: :job do
  let(:account) { create(:account) }
  let(:owner) { create(:user, account: account, role: "owner") }

  it "sends day 3 tips email" do
    expect {
      OnboardingSequenceJob.perform_now(account.id, 1)
    }.to change { ActionMailer::Base.deliveries.count }.by(1)
  end

  it "chains to next email" do
    OnboardingSequenceJob.perform_now(account.id, 1)

    expect(OnboardingSequenceJob)
      .to have_been_enqueued
      .with(account.id, 2)
      .at(4.days.from_now)
  end
end
```

## Key Features

| Feature | Implementation |
|---------|----------------|
| **Welcome Email** | Sent immediately on completion |
| **Drip Sequence** | Day 3, 7, 14 follow-up emails |
| **Analytics Tracking** | Record completion events |
| **Progress Tracking** | Stimulus controller tracks time spent |
| **Auto-scheduling** | Jobs chain themselves for future delivery |
| **Solid Queue** | Rails 8 default, no Redis needed |

## Related Files

- [model.md](./model.md): Onboarding model triggering jobs
- [controller.md](./controller.md): Controller completing onboarding
- [views.md](./views.md): Views using Stimulus controller
