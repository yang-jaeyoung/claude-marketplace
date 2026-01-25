# Onboarding Controller

## Main Controller

```ruby
# app/controllers/onboarding_controller.rb
class OnboardingController < ApplicationController
  before_action :redirect_if_completed
  before_action :set_onboarding

  def show
    @step = params[:step] || @onboarding.step

    case @step
    when "profile"
      @user = current_user
    when "team"
      @team_members = current_account.users.where.not(id: current_user.id)
      @invitation = Invitation.new
    when "workspace"
      @workspace_data = @onboarding.workspace_data || {}
    when "preferences"
      @preferences = @onboarding.preferences_data || {}
    end

    render "onboarding/#{@step}"
  end

  def update
    step = params[:step]

    case step
    when "profile"
      update_profile
    when "team"
      invite_team_members
    when "workspace"
      update_workspace
    when "preferences"
      update_preferences
    end
  end

  def skip
    if @onboarding.next_step
      @onboarding.update!(step: @onboarding.next_step)
      redirect_to onboarding_path(step: @onboarding.step)
    else
      @onboarding.complete!
      redirect_to root_path, notice: "Welcome to #{current_account.name}!"
    end
  end

  private

  def set_onboarding
    @onboarding = current_account.onboarding
  end

  def redirect_if_completed
    if current_account.onboarding&.completed?
      redirect_to root_path
    end
  end

  def update_profile
    if current_user.update(profile_params)
      @onboarding.update!(
        step: "team",
        profile_data: { completed_at: Time.current }
      )
      redirect_to onboarding_path(step: "team"), notice: "Profile updated"
    else
      @user = current_user
      render "onboarding/profile", status: :unprocessable_entity
    end
  end

  def invite_team_members
    emails = params[:emails]&.split(",")&.map(&:strip) || []

    emails.each do |email|
      Invitation.create!(
        account: current_account,
        email: email,
        invited_by: current_user
      )
    end

    @onboarding.update!(
      step: "workspace",
      team_data: { invited_count: emails.count, completed_at: Time.current }
    )

    redirect_to onboarding_path(step: "workspace"), notice: "Invitations sent"
  end

  def update_workspace
    @onboarding.update!(
      step: "preferences",
      workspace_data: workspace_params.merge(completed_at: Time.current)
    )

    redirect_to onboarding_path(step: "preferences"), notice: "Workspace configured"
  end

  def update_preferences
    @onboarding.update!(
      step: "complete",
      preferences_data: preferences_params.merge(completed_at: Time.current)
    )

    @onboarding.complete!
    redirect_to root_path, notice: "Welcome! Your account is ready."
  end

  def profile_params
    params.require(:user).permit(:name, :title, :avatar)
  end

  def workspace_params
    params.permit(:timezone, :default_view, :notifications_enabled)
  end

  def preferences_params
    params.permit(:email_digest, :weekly_summary, :product_updates)
  end
end
```

## Routes

```ruby
# config/routes.rb
Rails.application.routes.draw do
  resource :onboarding, only: [:show, :update] do
    post :skip
  end
end
```

## Controller Flow

```
┌─────────────┐
│ GET /       │  Redirect to onboarding if incomplete
│ onboarding  │
└──────┬──────┘
       │
       v
┌─────────────┐
│ Show step   │  Render current step view
│ (profile)   │
└──────┬──────┘
       │
       v
┌─────────────┐
│ PATCH       │  Update step data
│ onboarding  │
└──────┬──────┘
       │
       v
┌─────────────┐
│ Next step   │  Redirect to next step
│ (team)      │
└──────┬──────┘
       │
       v
   [Repeat]
       │
       v
┌─────────────┐
│ Complete!   │  Trigger job, redirect to root
└─────────────┘
```

## Key Features

| Feature | Implementation |
|---------|----------------|
| **Step Navigation** | `show` action renders current step based on `@onboarding.step` |
| **Data Validation** | Each `update_*` method validates before progressing |
| **Skip Functionality** | `skip` action allows bypassing optional steps |
| **Completion Guard** | `redirect_if_completed` prevents re-entry |
| **Progress Persistence** | Each step saves data to JSONB before advancing |
| **Strong Params** | Separate param methods for each step |

## Usage Examples

```ruby
# Start onboarding
GET /onboarding
# => Shows profile step

# Submit profile
PATCH /onboarding?step=profile
params: { user: { name: "John", title: "CEO" } }
# => Redirects to team step

# Skip a step
POST /onboarding/skip
# => Advances to next step or completes

# Complete onboarding
PATCH /onboarding?step=preferences
# => Triggers OnboardingCompleteJob, redirects to root
```

## Related Files

- [model.md](./model.md): Onboarding model with state management
- [views.md](./views.md): Views rendered by this controller
- [jobs.md](./jobs.md): Jobs triggered on completion
