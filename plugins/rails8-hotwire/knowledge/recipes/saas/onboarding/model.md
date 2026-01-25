# Onboarding Model and State Management

## Onboarding Model

```ruby
# app/models/onboarding.rb
class Onboarding < ApplicationRecord
  belongs_to :account

  STEPS = %w[profile team workspace preferences complete].freeze

  validates :step, inclusion: { in: STEPS }

  store_accessor :data, :profile_data, :team_data, :workspace_data, :preferences_data

  def current_step_index
    STEPS.index(step) || 0
  end

  def progress_percentage
    ((current_step_index.to_f / STEPS.length) * 100).round
  end

  def next_step
    current_index = STEPS.index(step)
    return nil if current_index.nil? || current_index >= STEPS.length - 1

    STEPS[current_index + 1]
  end

  def previous_step
    current_index = STEPS.index(step)
    return nil if current_index.nil? || current_index <= 0

    STEPS[current_index - 1]
  end

  def complete!
    update!(step: "complete", completed: true)
    OnboardingCompleteJob.perform_later(account.id)
  end
end
```

## Account Association

```ruby
# app/models/account.rb
class Account < ApplicationRecord
  has_one :onboarding, dependent: :destroy

  after_create :create_onboarding_record

  private

  def create_onboarding_record
    create_onboarding!(step: "profile", completed: false)
  end
end
```

## Key Features

| Feature | Implementation |
|---------|----------------|
| **JSONB Storage** | `store_accessor :data` for flexible step data |
| **Step Validation** | `validates :step, inclusion: { in: STEPS }` |
| **Progress Tracking** | `progress_percentage` calculates completion % |
| **Navigation** | `next_step` and `previous_step` helpers |
| **Auto-creation** | Account `after_create` hook creates onboarding |
| **Completion** | `complete!` marks done and triggers job |

## Database Schema

```ruby
# db/migrate/[timestamp]_create_onboardings.rb
class CreateOnboardings < ActiveRecord::Migration[8.0]
  def change
    create_table :onboardings do |t|
      t.references :account, null: false, foreign_key: true
      t.string :step, null: false, default: "profile"
      t.boolean :completed, null: false, default: false
      t.jsonb :data, null: false, default: {}

      t.timestamps
    end

    add_index :onboardings, :step
    add_index :onboardings, :completed
  end
end
```

## Usage Examples

```ruby
# Create onboarding for new account
account = Account.create!(name: "Acme Corp")
account.onboarding.step # => "profile"

# Store step data
onboarding = account.onboarding
onboarding.update!(
  profile_data: { name: "John Doe", title: "CEO" },
  step: "team"
)

# Check progress
onboarding.progress_percentage # => 20
onboarding.next_step # => "workspace"

# Complete onboarding
onboarding.complete! # Triggers OnboardingCompleteJob
```

## Related Files

- [controller.md](./controller.md): Controller using this model
- [views.md](./views.md): Views displaying model data
- [jobs.md](./jobs.md): Background jobs triggered by model
