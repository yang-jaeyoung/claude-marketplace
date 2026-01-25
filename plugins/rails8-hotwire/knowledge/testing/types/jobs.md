# Background Job Tests

## Overview
Test ActiveJob background jobs including job enqueueing, execution, retries, and integration with Solid Queue or Sidekiq.

## When to Use
- Testing job execution logic
- Verifying jobs are enqueued correctly
- Testing job arguments and serialization
- Testing retry behavior and error handling

## Quick Start
```ruby
# spec/jobs/post_notification_job_spec.rb
require 'rails_helper'

RSpec.describe PostNotificationJob, type: :job do
  describe '#perform' do
    let(:post) { create(:post) }

    it 'sends notifications to followers' do
      expect {
        described_class.perform_now(post.id)
      }.to change { ActionMailer::Base.deliveries.count }
    end
  end
end
```

## Main Patterns

### Pattern 1: Testing Job Enqueueing
```ruby
# spec/models/post_spec.rb
require 'rails_helper'

RSpec.describe Post, type: :model do
  describe 'after_create callback' do
    it 'enqueues notification job' do
      expect {
        create(:post, :published)
      }.to have_enqueued_job(PostNotificationJob)
    end

    it 'enqueues job with correct arguments' do
      post = build(:post, :published)

      expect {
        post.save
      }.to have_enqueued_job(PostNotificationJob).with(post.id)
    end

    it 'enqueues job on correct queue' do
      expect {
        create(:post, :published)
      }.to have_enqueued_job(PostNotificationJob).on_queue('notifications')
    end

    it 'enqueues job with delay' do
      expect {
        create(:post, :published)
      }.to have_enqueued_job(PostNotificationJob).at(5.minutes.from_now)
    end

    it 'does not enqueue job for drafts' do
      expect {
        create(:post, published: false)
      }.not_to have_enqueued_job(PostNotificationJob)
    end
  end
end
```

### Pattern 2: Testing Job Execution
```ruby
# spec/jobs/post_notification_job_spec.rb
require 'rails_helper'

RSpec.describe PostNotificationJob, type: :job do
  include ActiveJob::TestHelper

  let(:post) { create(:post, :published) }

  describe '#perform' do
    it 'sends email to each follower' do
      followers = create_list(:user, 3)
      allow(post.author).to receive(:followers).and_return(followers)

      expect {
        described_class.perform_now(post.id)
      }.to change { ActionMailer::Base.deliveries.count }.by(3)
    end

    it 'creates notification records' do
      followers = create_list(:user, 3)
      allow(post.author).to receive(:followers).and_return(followers)

      expect {
        described_class.perform_now(post.id)
      }.to change(Notification, :count).by(3)
    end

    it 'updates post notification_sent_at' do
      described_class.perform_now(post.id)

      expect(post.reload.notification_sent_at).to be_present
    end

    context 'when post not found' do
      it 'handles gracefully' do
        expect {
          described_class.perform_now(9999)
        }.not_to raise_error
      end
    end
  end
end
```

### Pattern 3: Testing Job Arguments and Serialization
```ruby
# spec/jobs/report_generation_job_spec.rb
require 'rails_helper'

RSpec.describe ReportGenerationJob, type: :job do
  describe 'serialization' do
    let(:user) { create(:user) }
    let(:start_date) { Date.today - 30.days }
    let(:end_date) { Date.today }

    it 'serializes ActiveRecord objects' do
      expect {
        described_class.perform_later(user, start_date, end_date)
      }.to have_enqueued_job(described_class).with(user, start_date, end_date)
    end

    it 'handles hash arguments' do
      options = { format: 'pdf', include_charts: true }

      expect {
        described_class.perform_later(user, options)
      }.to have_enqueued_job(described_class).with(user, options)
    end
  end

  describe '#perform' do
    it 'generates report with correct parameters' do
      user = create(:user)
      start_date = Date.today - 30.days
      end_date = Date.today

      report_service = double('ReportService')
      allow(ReportService).to receive(:new).and_return(report_service)
      allow(report_service).to receive(:generate)

      described_class.perform_now(user, start_date, end_date)

      expect(ReportService).to have_received(:new).with(
        user: user,
        start_date: start_date,
        end_date: end_date
      )
    end
  end
end
```

### Pattern 4: Testing Job Retries and Error Handling
```ruby
# app/jobs/api_sync_job.rb
class ApiSyncJob < ApplicationJob
  queue_as :default
  retry_on NetworkError, wait: :exponentially_longer, attempts: 5
  discard_on ActiveRecord::RecordNotFound

  def perform(resource_id)
    resource = Resource.find(resource_id)
    SyncService.call(resource)
  rescue NetworkError => e
    Rails.logger.error("API sync failed: #{e.message}")
    raise
  end
end

# spec/jobs/api_sync_job_spec.rb
require 'rails_helper'

RSpec.describe ApiSyncJob, type: :job do
  let(:resource) { create(:resource) }

  describe 'retry behavior' do
    before do
      allow(SyncService).to receive(:call).and_raise(NetworkError.new("Connection timeout"))
    end

    it 'retries on NetworkError' do
      expect {
        perform_enqueued_jobs do
          described_class.perform_later(resource.id)
        end
      }.to raise_error(NetworkError)

      # Check retry was scheduled (implementation depends on queue adapter)
      expect(enqueued_jobs.size).to be > 0
    end

    it 'retries with exponential backoff' do
      # Test with ActiveJob::QueueAdapters::TestAdapter
      described_class.perform_later(resource.id)

      # First retry after 3 seconds
      # Second retry after 18 seconds
      # etc.
    end

    it 'gives up after 5 attempts' do
      # Simulate 5 failed attempts
      5.times do
        perform_enqueued_jobs(only: ApiSyncJob) rescue nil
      end

      # Job should be discarded
    end
  end

  describe 'discard behavior' do
    it 'discards job when record not found' do
      expect {
        perform_enqueued_jobs do
          described_class.perform_later(9999)
        end
      }.not_to raise_error

      # Job is discarded, no retries
      expect(enqueued_jobs).to be_empty
    end
  end

  describe 'error logging' do
    before do
      allow(SyncService).to receive(:call).and_raise(NetworkError.new("Timeout"))
      allow(Rails.logger).to receive(:error)
    end

    it 'logs errors' do
      begin
        described_class.perform_now(resource.id)
      rescue NetworkError
      end

      expect(Rails.logger).to have_received(:error).with(/API sync failed: Timeout/)
    end
  end
end
```

### Pattern 5: Testing Scheduled Jobs
```ruby
# spec/jobs/cleanup_job_spec.rb
require 'rails_helper'

RSpec.describe CleanupJob, type: :job do
  describe '.schedule' do
    it 'schedules job for midnight' do
      travel_to Time.zone.parse('2024-01-15 10:00:00') do
        expect {
          CleanupJob.set(wait_until: Date.tomorrow.midnight).perform_later
        }.to have_enqueued_job(CleanupJob).at(Time.zone.parse('2024-01-16 00:00:00'))
      end
    end
  end

  describe '#perform' do
    it 'deletes old records' do
      old_records = create_list(:log_entry, 3, created_at: 31.days.ago)
      recent_records = create_list(:log_entry, 2, created_at: 1.day.ago)

      described_class.perform_now

      expect(LogEntry.exists?(old_records.map(&:id))).to be false
      expect(LogEntry.exists?(recent_records.map(&:id))).to be true
    end
  end
end
```

### Pattern 6: Testing Job Performance and Timeouts
```ruby
# spec/jobs/heavy_processing_job_spec.rb
require 'rails_helper'

RSpec.describe HeavyProcessingJob, type: :job do
  describe '#perform' do
    it 'completes within timeout' do
      dataset = create(:dataset, size: 1000)

      expect {
        Timeout.timeout(5) do
          described_class.perform_now(dataset.id)
        end
      }.not_to raise_error
    end

    it 'processes in batches to avoid memory issues' do
      dataset = create(:dataset, size: 10000)

      expect_any_instance_of(Dataset).to receive(:find_in_batches).and_call_original

      described_class.perform_now(dataset.id)
    end
  end
end
```

### Pattern 7: Testing Job Callbacks
```ruby
# app/jobs/export_job.rb
class ExportJob < ApplicationJob
  before_perform :log_start
  after_perform :log_completion
  around_perform :measure_time

  def perform(export_id)
    export = Export.find(export_id)
    ExportService.call(export)
  end

  private

  def log_start(job)
    Rails.logger.info("Starting export: #{job.arguments.first}")
  end

  def log_completion(job)
    Rails.logger.info("Completed export: #{job.arguments.first}")
  end

  def measure_time
    start_time = Time.current
    yield
    duration = Time.current - start_time
    Rails.logger.info("Export took #{duration} seconds")
  end
end

# spec/jobs/export_job_spec.rb
require 'rails_helper'

RSpec.describe ExportJob, type: :job do
  let(:export) { create(:export) }

  describe 'callbacks' do
    before do
      allow(Rails.logger).to receive(:info)
    end

    it 'logs start before performing' do
      described_class.perform_now(export.id)

      expect(Rails.logger).to have_received(:info).with(/Starting export: #{export.id}/)
    end

    it 'logs completion after performing' do
      described_class.perform_now(export.id)

      expect(Rails.logger).to have_received(:info).with(/Completed export: #{export.id}/)
    end

    it 'measures execution time' do
      described_class.perform_now(export.id)

      expect(Rails.logger).to have_received(:info).with(/Export took .* seconds/)
    end
  end
end
```

### Pattern 8: Testing Solid Queue Integration (Rails 8)
```ruby
# spec/jobs/batch_processing_job_spec.rb
require 'rails_helper'

RSpec.describe BatchProcessingJob, type: :job do
  describe 'Solid Queue integration' do
    it 'enqueues to correct queue' do
      expect(described_class.new.queue_name).to eq('batch')
    end

    it 'processes jobs in order' do
      order = []

      3.times do |i|
        described_class.perform_later(i)
      end

      perform_enqueued_jobs do
        # Jobs processed in FIFO order
      end
    end

    it 'supports priority queues' do
      high_priority = described_class.set(priority: 10).perform_later(1)
      low_priority = described_class.set(priority: 1).perform_later(2)

      # High priority job processed first
    end
  end
end
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Not testing job enqueueing | Jobs never run | Test `have_enqueued_job` in models/controllers |
| Using `perform_now` in production code | Blocks requests | Always use `perform_later` |
| Not testing error handling | Jobs fail silently | Test retry and discard behavior |
| Testing implementation details | Brittle tests | Test outcomes, not internal calls |
| Not cleaning up enqueued jobs | Test pollution | Use `clear_enqueued_jobs` or `perform_enqueued_jobs` |

## Related Skills
- [Models](./models.md): Testing callbacks that enqueue jobs
- [Services](./services.md): Testing service objects called by jobs
- [Mocking](../patterns/mocking.md): Stubbing external dependencies

## References
- [ActiveJob Testing](https://guides.rubyonrails.org/testing.html#testing-jobs)
- [RSpec ActiveJob](https://rspec.info/features/6-0/rspec-rails/job-specs/)
- [Solid Queue](https://github.com/basecamp/solid_queue)
