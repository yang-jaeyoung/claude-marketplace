# Devise Controller Customization

## Overview

Guide to overriding Devise controllers for custom authentication logic, additional actions, strong parameters handling, and callback customization.

## When to Use

- When adding custom fields to registration
- When implementing custom after-sign-in logic
- When handling authentication events (sign in, sign out)
- When integrating with external services on authentication

## Quick Start

```bash
# Generate controllers for customization
rails generate devise:controllers users

# Generate specific controllers only
rails generate devise:controllers users -c=sessions registrations
```

```ruby
# config/routes.rb
devise_for :users, controllers: {
  sessions: 'users/sessions',
  registrations: 'users/registrations'
}
```

## Main Patterns

### Pattern 1: Custom Registrations Controller

```ruby
# app/controllers/users/registrations_controller.rb
class Users::RegistrationsController < Devise::RegistrationsController
  before_action :configure_sign_up_params, only: [:create]
  before_action :configure_account_update_params, only: [:update]

  protected

  # Permit additional parameters for sign up
  def configure_sign_up_params
    devise_parameter_sanitizer.permit(:sign_up, keys: [:name, :phone, :avatar])
  end

  # Permit additional parameters for account update
  def configure_account_update_params
    devise_parameter_sanitizer.permit(:account_update, keys: [:name, :phone, :avatar])
  end

  # Redirect path after sign up
  def after_sign_up_path_for(resource)
    onboarding_path
  end

  # Redirect path after sign up (when confirmable is enabled)
  def after_inactive_sign_up_path_for(resource)
    new_user_session_path
  end
end
```

### Pattern 2: Custom Sessions Controller

```ruby
# app/controllers/users/sessions_controller.rb
class Users::SessionsController < Devise::SessionsController
  after_action :track_login, only: :create

  # Custom logic after sign in
  def after_sign_in_path_for(resource)
    stored_location_for(resource) || dashboard_path
  end

  # Custom logic after sign out
  def after_sign_out_path_for(resource_or_scope)
    new_user_session_path
  end

  protected

  def track_login
    return unless user_signed_in?

    current_user.update_columns(
      last_login_at: Time.current,
      login_count: current_user.login_count.to_i + 1
    )

    # Track with analytics
    Analytics.track(current_user.id, "User Signed In")
  end

  # Respond to failed authentication
  def auth_options
    { scope: resource_name, recall: "#{controller_path}#new" }
  end
end
```

### Pattern 3: Custom Passwords Controller

```ruby
# app/controllers/users/passwords_controller.rb
class Users::PasswordsController < Devise::PasswordsController
  # Log password reset requests for security
  def create
    super do |resource|
      SecurityLog.create!(
        event: 'password_reset_requested',
        email: resource.email,
        ip_address: request.remote_ip,
        user_agent: request.user_agent
      )
    end
  end

  # Custom redirect after password reset
  def after_resetting_password_path_for(resource)
    flash[:notice] = "Password successfully updated!"
    dashboard_path
  end
end
```

### Pattern 4: Custom Confirmations Controller

```ruby
# app/controllers/users/confirmations_controller.rb
class Users::ConfirmationsController < Devise::ConfirmationsController
  # Redirect after confirmation
  def after_confirmation_path_for(resource_name, resource)
    sign_in(resource)
    onboarding_path
  end

  # Handle expired confirmation tokens
  def show
    super do |resource|
      if resource.errors[:confirmation_token].include?("has expired")
        resource.send_confirmation_instructions
        flash[:notice] = "Confirmation link expired. A new link has been sent."
      end
    end
  end
end
```

### Pattern 5: Application Controller Integration

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  before_action :configure_permitted_parameters, if: :devise_controller?
  before_action :authenticate_user!

  protected

  # Global parameter configuration
  def configure_permitted_parameters
    added_attrs = [:name, :phone, :avatar, :time_zone]
    devise_parameter_sanitizer.permit(:sign_up, keys: added_attrs)
    devise_parameter_sanitizer.permit(:account_update, keys: added_attrs)
  end

  # Global after sign in path
  def after_sign_in_path_for(resource)
    stored_location_for(resource) || root_path
  end

  # Global after sign out path
  def after_sign_out_path_for(resource_or_scope)
    new_user_session_path
  end

  # Store location for redirect after sign in
  def store_location
    store_location_for(:user, request.fullpath) if request.get? && !devise_controller?
  end
end
```

### Pattern 6: OmniAuth Callbacks Controller

```ruby
# app/controllers/users/omniauth_callbacks_controller.rb
class Users::OmniauthCallbacksController < Devise::OmniauthCallbacksController
  skip_before_action :verify_authenticity_token, only: [:google_oauth2, :github]

  def google_oauth2
    handle_oauth("Google")
  end

  def github
    handle_oauth("GitHub")
  end

  def failure
    redirect_to root_path, alert: "Authentication failed: #{failure_message}"
  end

  private

  def handle_oauth(provider)
    @user = User.from_omniauth(request.env["omniauth.auth"])

    if @user.persisted?
      sign_in_and_redirect @user, event: :authentication
      set_flash_message(:notice, :success, kind: provider) if is_navigational_format?
    else
      session["devise.oauth_data"] = request.env["omniauth.auth"].except(:extra)
      redirect_to new_user_registration_url, alert: @user.errors.full_messages.join("\n")
    end
  end

  def failure_message
    exception = request.env["omniauth.error"]
    exception.respond_to?(:message) ? exception.message : exception.to_s
  end
end
```

### Pattern 7: Invitations Controller (devise_invitable)

```ruby
# app/controllers/users/invitations_controller.rb
class Users::InvitationsController < Devise::InvitationsController
  before_action :configure_permitted_parameters

  # POST /users/invitation
  def create
    super do |resource|
      if resource.errors.empty?
        InvitationMailer.custom_welcome(resource).deliver_later
      end
    end
  end

  # PUT /users/invitation
  def update
    super do |resource|
      if resource.errors.empty?
        resource.update(onboarded: true)
      end
    end
  end

  protected

  def configure_permitted_parameters
    devise_parameter_sanitizer.permit(:invite, keys: [:name, :role])
    devise_parameter_sanitizer.permit(:accept_invitation, keys: [:name, :phone])
  end

  def after_accept_path_for(resource)
    onboarding_path
  end
end
```

### Pattern 8: Turbo-Compatible Controller

```ruby
# app/controllers/users/sessions_controller.rb
class Users::SessionsController < Devise::SessionsController
  # Handle Turbo Stream responses
  def create
    self.resource = warden.authenticate!(auth_options)
    set_flash_message!(:notice, :signed_in)
    sign_in(resource_name, resource)

    respond_to do |format|
      format.turbo_stream do
        render turbo_stream: turbo_stream.action(:redirect, after_sign_in_path_for(resource))
      end
      format.html { redirect_to after_sign_in_path_for(resource) }
    end
  end

  # Handle failed authentication with Turbo
  def respond_to_on_destroy
    respond_to do |format|
      format.turbo_stream do
        render turbo_stream: turbo_stream.action(:redirect, after_sign_out_path_for(resource_name))
      end
      format.html { redirect_to after_sign_out_path_for(resource_name), status: :see_other }
    end
  end
end
```

## Routes Configuration

```ruby
# config/routes.rb
devise_for :users, controllers: {
  sessions: 'users/sessions',
  registrations: 'users/registrations',
  passwords: 'users/passwords',
  confirmations: 'users/confirmations',
  unlocks: 'users/unlocks',
  omniauth_callbacks: 'users/omniauth_callbacks'
}, path: '', path_names: {
  sign_in: 'login',
  sign_out: 'logout',
  sign_up: 'register'
}

# Custom routes within devise scope
devise_scope :user do
  get 'profile', to: 'users/registrations#edit'
  delete 'sessions/other', to: 'users/sessions#destroy_other'
end
```

## Strong Parameters Reference

```ruby
# Available keys for devise_parameter_sanitizer
devise_parameter_sanitizer.permit(:sign_up, keys: [...])
devise_parameter_sanitizer.permit(:sign_in, keys: [...])
devise_parameter_sanitizer.permit(:account_update, keys: [...])

# Default permitted parameters:
# sign_in: [:email, :password, :remember_me]
# sign_up: [:email, :password, :password_confirmation]
# account_update: [:email, :password, :password_confirmation, :current_password]
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Overriding all methods | Hard to maintain | Override only needed methods |
| Forgetting super call | Breaks Devise functionality | Call `super` or use block form |
| Not updating routes | Controller not used | Update `devise_for` with controllers |
| Skipping CSRF in all actions | Security vulnerability | Only skip for specific OAuth callbacks |

## Related Skills

- [setup.md](./setup.md): Installation guide
- [turbo.md](./turbo.md): Turbo compatibility
- [views.md](./views.md): View customization

## References

- [Devise Controller Customization](https://github.com/heartcombo/devise#configuring-controllers)
- [Devise Wiki - Controllers](https://github.com/heartcombo/devise/wiki)
