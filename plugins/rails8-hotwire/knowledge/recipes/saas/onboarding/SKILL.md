---
name: rails8-recipes-onboarding
description: Multi-step onboarding wizard with progress tracking and welcome email sequences
triggers:
  - onboarding
  - wizard
  - multi-step
  - welcome flow
  - user setup
  - account setup
  - 온보딩
  - 마법사
  - 다단계
  - 웰컴 플로우
  - 사용자 설정
  - 계정 설정
summary: |
  다단계 온보딩 마법사를 다룹니다. 진행률 추적, 데이터 유효성 검사,
  Turbo Frame 네비게이션, 이메일 웰컴 시퀀스를 포함합니다. 전환율을
  최적화한 부드러운 사용자 설정 경험을 제공합니다.
token_cost: medium
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - "*.md"
  deep:
    - "**/*.md"
---

# User Onboarding Flow

## Overview

Multi-step onboarding wizard with progress tracking, data validation, Turbo Frame navigation, and email welcome sequences. Guide new users through account setup with a smooth, conversion-optimized experience.

## Prerequisites

- [hotwire/turbo-frames](../../../hotwire/turbo-frames.md): Page navigation
- [hotwire/stimulus](../../../hotwire/stimulus.md): Progress tracking
- [background/solid-queue](../../../background/solid-queue.md): Email sequences
- [models/validations](../../../models/validations.md): Step validation

## Quick Start

```ruby
# Terminal
rails generate model Onboarding account:references step:string completed:boolean data:jsonb
rails db:migrate
```

## Implementation Files

| File | Description |
|------|-------------|
| [model.md](./model.md) | Onboarding model with state management and Account association |
| [controller.md](./controller.md) | OnboardingController with step navigation and updates |
| [views.md](./views.md) | Layout with progress bar and all step views |
| [jobs.md](./jobs.md) | Background jobs, email sequences, mailers, and Stimulus |

## Implementation Flow

1. **[Model Setup](./model.md)**: Create Onboarding model with JSONB data storage and state transitions
2. **[Controller](./controller.md)**: Implement step-by-step controller actions with validation
3. **[Views](./views.md)**: Build layout with progress bar and individual step forms
4. **[Jobs & Email](./jobs.md)**: Set up completion jobs, email sequences, and progress tracking

## Testing

```ruby
# spec/models/onboarding_spec.rb
require "rails_helper"

RSpec.describe Onboarding, type: :model do
  let(:onboarding) { create(:onboarding, step: "team") }

  it "calculates progress percentage" do
    expect(onboarding.progress_percentage).to eq(20) # 1/5 steps
  end

  it "returns next step" do
    expect(onboarding.next_step).to eq("workspace")
  end

  it "completes onboarding" do
    expect {
      onboarding.complete!
    }.to have_enqueued_job(OnboardingCompleteJob)

    expect(onboarding.reload).to be_completed
  end
end

# spec/requests/onboarding_spec.rb
require "rails_helper"

RSpec.describe "Onboarding flow", type: :request do
  let(:account) { create(:account) }
  let(:user) { create(:user, account: account) }

  before { sign_in user }

  it "progresses through steps" do
    # Profile step
    patch onboarding_path(step: "profile"), params: {
      user: { name: "John Doe", title: "Developer" }
    }
    expect(response).to redirect_to(onboarding_path(step: "team"))

    # Team step
    patch onboarding_path(step: "team"), params: {
      emails: "colleague@example.com"
    }
    expect(response).to redirect_to(onboarding_path(step: "workspace"))

    # Workspace step
    patch onboarding_path(step: "workspace"), params: {
      timezone: "UTC", default_view: "list"
    }
    expect(response).to redirect_to(onboarding_path(step: "preferences"))

    # Preferences step
    patch onboarding_path(step: "preferences"), params: {
      email_digest: "1"
    }
    expect(response).to redirect_to(root_path)
    expect(account.onboarding.reload).to be_completed
  end

  it "allows skipping steps" do
    post skip_onboarding_path
    expect(account.onboarding.reload.step).to eq("team")
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Too many steps | User abandonment | Keep to 4-5 steps max, make optional |
| Required fields | Blocks completion | Make most fields optional, allow skipping |
| No progress indicator | User doesn't know how long | Show clear progress bar and step count |
| No data persistence | Lose progress on refresh | Save to JSONB column on each step |
| Blocking workflow | Users can't access app | Allow "Skip for now" and access app immediately |

## Related Skills

- [hotwire/turbo-frames](../../../hotwire/turbo-frames.md): Step navigation
- [hotwire/stimulus](../../../hotwire/stimulus.md): Interactive elements
- [background/solid-queue](../../../background/solid-queue.md): Email sequences
- [recipes/multi-tenant](../multi-tenant.md): Account setup

## References

- [Turbo Handbook](https://turbo.hotwired.dev/handbook/frames): Frame navigation
- [User Onboarding](https://www.useronboard.com/): Best practices
- [Rails ActionMailer](https://guides.rubyonrails.org/action_mailer_basics.html): Email delivery
