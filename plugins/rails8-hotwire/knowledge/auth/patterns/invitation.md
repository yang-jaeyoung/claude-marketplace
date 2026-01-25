# User Invitation System

## Overview

Patterns for inviting users to your application, either using devise_invitable or a custom implementation. Supports team invitations, organization onboarding, and controlled user registration.

## When to Use

- When implementing invite-only registration
- When building team/organization features
- When admins need to onboard users
- When users should invite collaborators
- When implementing B2B SaaS with team management

## Quick Start

### Option 1: devise_invitable (Recommended)

```ruby
# Gemfile
gem "devise_invitable"

# Install
rails g devise_invitable:install
rails g devise_invitable User
rails db:migrate
```

### Option 2: Custom Implementation

```ruby
# Migration
rails g migration AddInvitationToUsers \
  invitation_token:string:uniq \
  invitation_sent_at:datetime \
  invitation_accepted_at:datetime \
  invited_by:references
```

## Main Patterns

### Pattern 1: devise_invitable Setup

```ruby
# Gemfile
gem "devise_invitable", "~> 2.0"
```

```bash
bundle install
rails generate devise_invitable:install
rails generate devise_invitable User
rails db:migrate
```

```ruby
# app/models/user.rb
class User < ApplicationRecord
  devise :invitable, :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable

  # Optional: track who invited whom
  belongs_to :invited_by, class_name: "User", optional: true
  has_many :invitations, class_name: "User", foreign_key: :invited_by_id
end
```

### Pattern 2: Custom Invitation Controller (devise_invitable)

```ruby
# app/controllers/users/invitations_controller.rb
class Users::InvitationsController < Devise::InvitationsController
  before_action :configure_permitted_parameters

  # POST /users/invitation
  def create
    # Limit invitations
    if current_user.invitations.pending.count >= invitation_limit
      redirect_to new_user_invitation_path,
        alert: "You've reached your invitation limit."
      return
    end

    super do |resource|
      if resource.persisted?
        # Additional actions after invite
        resource.update(organization: current_user.organization)
        track_invitation(resource)
      end
    end
  end

  # PUT /users/invitation - Accept invitation
  def update
    super do |resource|
      if resource.errors.empty?
        resource.update(onboarded_at: Time.current)
        WelcomeMailer.welcome(resource).deliver_later
      end
    end
  end

  protected

  def configure_permitted_parameters
    devise_parameter_sanitizer.permit(:invite, keys: [:name, :role])
    devise_parameter_sanitizer.permit(:accept_invitation, keys: [:name, :password, :password_confirmation])
  end

  def after_invite_path_for(inviter, invitee)
    team_members_path
  end

  def after_accept_path_for(resource)
    onboarding_path
  end

  private

  def invitation_limit
    current_user.admin? ? 100 : 10
  end

  def track_invitation(resource)
    Analytics.track(current_user.id, "User Invited", {
      invitee_email: resource.email,
      invitee_role: resource.role
    })
  end
end

# config/routes.rb
devise_for :users, controllers: {
  invitations: 'users/invitations'
}
```

### Pattern 3: Custom Invitation System (No Devise)

```ruby
# db/migrate/xxx_create_invitations.rb
class CreateInvitations < ActiveRecord::Migration[8.0]
  def change
    create_table :invitations do |t|
      t.string :email, null: false
      t.string :token, null: false
      t.string :role, default: "member"
      t.references :inviter, foreign_key: { to_table: :users }
      t.references :organization, foreign_key: true
      t.datetime :accepted_at
      t.datetime :expires_at, null: false

      t.timestamps
    end

    add_index :invitations, :token, unique: true
    add_index :invitations, :email
  end
end
```

```ruby
# app/models/invitation.rb
class Invitation < ApplicationRecord
  belongs_to :inviter, class_name: "User"
  belongs_to :organization

  has_secure_token :token

  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :email, uniqueness: { scope: :organization_id, message: "already invited" }

  before_validation :set_expiration, on: :create

  scope :pending, -> { where(accepted_at: nil).where("expires_at > ?", Time.current) }
  scope :expired, -> { where("expires_at <= ?", Time.current) }
  scope :accepted, -> { where.not(accepted_at: nil) }

  def pending?
    accepted_at.nil? && !expired?
  end

  def expired?
    expires_at <= Time.current
  end

  def accepted?
    accepted_at.present?
  end

  def accept!(user)
    return false if expired? || accepted?

    transaction do
      update!(accepted_at: Time.current)
      user.update!(organization: organization, role: role)
      organization.memberships.create!(user: user, role: role)
    end

    true
  end

  private

  def set_expiration
    self.expires_at ||= 7.days.from_now
  end
end
```

### Pattern 4: Invitation Service

```ruby
# app/services/invitations/create_service.rb
module Invitations
  class CreateService < ApplicationService
    def initialize(inviter:, email:, organization:, role: "member")
      @inviter = inviter
      @email = email.downcase.strip
      @organization = organization
      @role = role
    end

    def call
      return failure("Already a member") if existing_member?
      return failure("Already invited") if pending_invitation?

      invitation = create_invitation
      return failure(invitation.errors) unless invitation.persisted?

      send_invitation_email(invitation)
      success(invitation)
    end

    private

    attr_reader :inviter, :email, :organization, :role

    def existing_member?
      organization.users.exists?(email: email)
    end

    def pending_invitation?
      organization.invitations.pending.exists?(email: email)
    end

    def create_invitation
      organization.invitations.create(
        email: email,
        inviter: inviter,
        role: role
      )
    end

    def send_invitation_email(invitation)
      InvitationMailer.invite(invitation).deliver_later
    end
  end
end
```

### Pattern 5: Invitation Controller (Custom)

```ruby
# app/controllers/invitations_controller.rb
class InvitationsController < ApplicationController
  before_action :authenticate_user!, except: [:show, :accept]
  before_action :set_invitation, only: [:show, :accept, :destroy, :resend]

  # GET /invitations - List sent invitations
  def index
    @invitations = current_organization.invitations.includes(:inviter)
      .order(created_at: :desc)
  end

  # GET /invitations/new
  def new
    @invitation = Invitation.new
  end

  # POST /invitations
  def create
    result = Invitations::CreateService.call(
      inviter: current_user,
      email: params[:invitation][:email],
      organization: current_organization,
      role: params[:invitation][:role]
    )

    if result.success?
      redirect_to invitations_path, notice: "Invitation sent!"
    else
      @invitation = Invitation.new(invitation_params)
      @invitation.errors.add(:base, result.errors)
      render :new, status: :unprocessable_entity
    end
  end

  # GET /invitations/:token - Accept form
  def show
    if @invitation.expired?
      redirect_to root_path, alert: "This invitation has expired."
    elsif @invitation.accepted?
      redirect_to root_path, alert: "This invitation has already been used."
    else
      @user = User.new(email: @invitation.email)
    end
  end

  # POST /invitations/:token/accept
  def accept
    @user = User.new(user_params.merge(email: @invitation.email))

    if @user.save && @invitation.accept!(@user)
      sign_in(@user)
      redirect_to root_path, notice: "Welcome to #{@invitation.organization.name}!"
    else
      render :show, status: :unprocessable_entity
    end
  end

  # DELETE /invitations/:id
  def destroy
    authorize @invitation
    @invitation.destroy
    redirect_to invitations_path, notice: "Invitation cancelled."
  end

  # POST /invitations/:id/resend
  def resend
    authorize @invitation

    if @invitation.pending?
      @invitation.regenerate_token
      @invitation.update(expires_at: 7.days.from_now)
      InvitationMailer.invite(@invitation).deliver_later
      redirect_to invitations_path, notice: "Invitation resent."
    else
      redirect_to invitations_path, alert: "Cannot resend this invitation."
    end
  end

  private

  def set_invitation
    @invitation = Invitation.find_by!(token: params[:token] || params[:id])
  end

  def invitation_params
    params.require(:invitation).permit(:email, :role)
  end

  def user_params
    params.require(:user).permit(:name, :password, :password_confirmation)
  end
end
```

### Pattern 6: Invitation Mailer

```ruby
# app/mailers/invitation_mailer.rb
class InvitationMailer < ApplicationMailer
  def invite(invitation)
    @invitation = invitation
    @inviter = invitation.inviter
    @organization = invitation.organization
    @accept_url = invitation_url(token: invitation.token)

    mail(
      to: invitation.email,
      subject: "#{@inviter.name} invited you to join #{@organization.name}"
    )
  end
end
```

```erb
<%# app/views/invitation_mailer/invite.html.erb %>
<!DOCTYPE html>
<html>
<body>
  <h1>You've been invited!</h1>

  <p>
    <strong><%= @inviter.name %></strong> has invited you to join
    <strong><%= @organization.name %></strong>.
  </p>

  <p>
    <a href="<%= @accept_url %>" style="display: inline-block; padding: 12px 24px; background-color: #4F46E5; color: white; text-decoration: none; border-radius: 6px;">
      Accept Invitation
    </a>
  </p>

  <p>
    This invitation will expire in 7 days.
  </p>

  <hr>
  <p style="color: #666; font-size: 12px;">
    If you don't want to join, you can ignore this email.
  </p>
</body>
</html>
```

### Pattern 7: Bulk Invitations

```ruby
# app/services/invitations/bulk_create_service.rb
module Invitations
  class BulkCreateService < ApplicationService
    def initialize(inviter:, emails:, organization:, role: "member")
      @inviter = inviter
      @emails = emails.map { |e| e.downcase.strip }.uniq
      @organization = organization
      @role = role
    end

    def call
      results = { sent: [], failed: [] }

      emails.each do |email|
        result = CreateService.call(
          inviter: inviter,
          email: email,
          organization: organization,
          role: role
        )

        if result.success?
          results[:sent] << email
        else
          results[:failed] << { email: email, reason: result.errors }
        end
      end

      success(results)
    end

    private

    attr_reader :inviter, :emails, :organization, :role
  end
end

# Controller usage
def bulk_create
  emails = params[:emails].split(/[\s,]+/)

  result = Invitations::BulkCreateService.call(
    inviter: current_user,
    emails: emails,
    organization: current_organization
  )

  redirect_to invitations_path,
    notice: "Sent #{result.value[:sent].count} invitations. #{result.value[:failed].count} failed."
end
```

### Pattern 8: Team Invitation with Roles

```erb
<%# app/views/invitations/new.html.erb %>
<div class="max-w-lg mx-auto py-8">
  <h1 class="text-2xl font-bold mb-6">Invite Team Member</h1>

  <%= form_with model: @invitation, url: invitations_path, class: "space-y-6" do |f| %>
    <%= render "shared/form_errors", model: @invitation %>

    <div>
      <%= f.label :email, class: "block text-sm font-medium text-gray-700" %>
      <%= f.email_field :email,
          required: true,
          placeholder: "colleague@example.com",
          class: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" %>
    </div>

    <div>
      <%= f.label :role, class: "block text-sm font-medium text-gray-700" %>
      <%= f.select :role,
          [["Member", "member"], ["Admin", "admin"], ["Viewer", "viewer"]],
          {},
          class: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" %>
      <p class="mt-1 text-sm text-gray-500">
        Admins can invite others and manage settings.
      </p>
    </div>

    <div>
      <%= f.submit "Send Invitation",
          class: "w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" %>
    </div>
  <% end %>
</div>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No expiration | Security risk | 7-day max expiration |
| Reusable tokens | Multiple uses | Mark accepted immediately |
| Unlimited invites | Spam/abuse | Rate limit per user |
| No role validation | Privilege escalation | Validate inviter can assign role |

## Related Skills

- [../devise/setup.md](../devise/setup.md): Devise setup
- [magic-link.md](./magic-link.md): Passwordless auth
- [../../controllers/SKILL.md](../../controllers/SKILL.md): Controller patterns

## References

- [devise_invitable](https://github.com/scambra/devise_invitable)
- [has_secure_token](https://api.rubyonrails.org/classes/ActiveRecord/SecureToken/ClassMethods.html)
