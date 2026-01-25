# Customizing Rails 8 Built-in Authentication

The built-in generator provides a foundation. Here's how to extend it for common requirements.

## Adding User Registration

### Routes

```ruby
# config/routes.rb
Rails.application.routes.draw do
  resource :session
  resources :passwords, param: :token
  resource :registration, only: [:new, :create]  # Add this

  # Convenience routes
  get "signup", to: "registrations#new"
  get "login", to: "sessions#new"
end
```

### Controller

```ruby
# app/controllers/registrations_controller.rb
class RegistrationsController < ApplicationController
  allow_unauthenticated_access

  before_action :redirect_if_authenticated

  def new
    @user = User.new
  end

  def create
    @user = User.new(user_params)

    if @user.save
      start_new_session_for(@user)
      redirect_to root_path, notice: "Welcome! Your account has been created."
    else
      render :new, status: :unprocessable_entity
    end
  end

  private

  def user_params
    params.require(:user).permit(:email_address, :password, :password_confirmation, :name)
  end

  def redirect_if_authenticated
    redirect_to root_path if authenticated?
  end
end
```

### View

```erb
<!-- app/views/registrations/new.html.erb -->
<div class="max-w-md mx-auto mt-8">
  <h1 class="text-2xl font-bold mb-6">Create an Account</h1>

  <%= form_with model: @user, url: registration_path, class: "space-y-4" do |f| %>
    <% if @user.errors.any? %>
      <div class="bg-red-50 text-red-500 p-4 rounded">
        <ul>
          <% @user.errors.full_messages.each do |message| %>
            <li><%= message %></li>
          <% end %>
        </ul>
      </div>
    <% end %>

    <div>
      <%= f.label :name, class: "block text-sm font-medium" %>
      <%= f.text_field :name, class: "mt-1 block w-full rounded border-gray-300", autofocus: true %>
    </div>

    <div>
      <%= f.label :email_address, class: "block text-sm font-medium" %>
      <%= f.email_field :email_address, class: "mt-1 block w-full rounded border-gray-300", required: true %>
    </div>

    <div>
      <%= f.label :password, class: "block text-sm font-medium" %>
      <%= f.password_field :password, class: "mt-1 block w-full rounded border-gray-300", required: true %>
      <p class="text-sm text-gray-500 mt-1">Minimum 8 characters</p>
    </div>

    <div>
      <%= f.label :password_confirmation, class: "block text-sm font-medium" %>
      <%= f.password_field :password_confirmation, class: "mt-1 block w-full rounded border-gray-300", required: true %>
    </div>

    <%= f.submit "Create Account", class: "w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700" %>
  <% end %>

  <p class="mt-4 text-center text-sm text-gray-600">
    Already have an account? <%= link_to "Sign in", new_session_path, class: "text-blue-600 hover:underline" %>
  </p>
</div>
```

### User Model Updates

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_secure_password
  has_many :sessions, dependent: :destroy

  normalizes :email_address, with: -> { _1.strip.downcase }

  validates :email_address, presence: true, uniqueness: true,
            format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :password, length: { minimum: 8 }, if: -> { password.present? }
  validates :name, presence: true, length: { maximum: 100 }
end
```

### Migration for Name Field

```bash
bin/rails generate migration AddNameToUsers name:string
bin/rails db:migrate
```

## Adding Remember Me

### Migration

```bash
bin/rails generate migration AddRememberTokenToUsers remember_token:string:index
bin/rails db:migrate
```

### User Model

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_secure_password
  has_secure_token :remember_token

  # ... existing code ...

  def remember_me!
    regenerate_remember_token
  end

  def forget_me!
    update!(remember_token: nil)
  end
end
```

### Authentication Concern Updates

```ruby
# app/controllers/concerns/authentication.rb
module Authentication
  extend ActiveSupport::Concern

  # ... existing code ...

  private

  def resume_session
    if session_record = find_session_by_cookie
      set_current_session(session_record)
    elsif user = find_user_by_remember_token
      start_new_session_for(user)
      user
    end
  end

  def find_user_by_remember_token
    if token = cookies.signed[:remember_token]
      User.find_by(remember_token: token)
    end
  end

  def remember(user)
    user.remember_me!
    cookies.signed.permanent[:remember_token] = {
      value: user.remember_token,
      httponly: true,
      secure: Rails.env.production?
    }
  end

  def forget(user)
    user.forget_me!
    cookies.delete(:remember_token)
  end

  def terminate_session
    forget(Current.user) if Current.user
    Current.session&.destroy
    cookies.delete(:session_id)
  end
end
```

### Sessions Controller Updates

```ruby
# app/controllers/sessions_controller.rb
class SessionsController < ApplicationController
  allow_unauthenticated_access only: [:new, :create]

  rate_limit to: 10, within: 3.minutes, only: :create,
             with: -> { redirect_to new_session_path, alert: "Too many attempts. Try again later." }

  def new
  end

  def create
    if user = User.authenticate_by(email_address: params[:email_address], password: params[:password])
      start_new_session_for(user)
      remember(user) if params[:remember_me] == "1"
      redirect_to after_sign_in_path, notice: "Signed in successfully"
    else
      flash.now[:alert] = "Invalid email or password"
      render :new, status: :unprocessable_entity
    end
  end

  def destroy
    terminate_session
    redirect_to root_path, notice: "Signed out successfully"
  end

  private

  def after_sign_in_path
    stored_location || root_path
  end

  def stored_location
    session.delete(:return_to)
  end
end
```

### Login Form with Remember Me

```erb
<!-- app/views/sessions/new.html.erb -->
<%= form_with url: session_path, class: "space-y-4" do |f| %>
  <div>
    <%= f.label :email_address %>
    <%= f.email_field :email_address, required: true, autofocus: true %>
  </div>

  <div>
    <%= f.label :password %>
    <%= f.password_field :password, required: true %>
  </div>

  <div class="flex items-center">
    <%= f.check_box :remember_me, class: "rounded" %>
    <%= f.label :remember_me, "Remember me", class: "ml-2 text-sm" %>
  </div>

  <%= f.submit "Sign in" %>
<% end %>
```

## Adding Account Management

### Routes

```ruby
# config/routes.rb
resource :account, only: [:show, :edit, :update, :destroy]
```

### Controller

```ruby
# app/controllers/accounts_controller.rb
class AccountsController < ApplicationController
  before_action :set_user

  def show
  end

  def edit
  end

  def update
    if @user.update(user_params)
      redirect_to account_path, notice: "Account updated successfully"
    else
      render :edit, status: :unprocessable_entity
    end
  end

  def destroy
    @user.sessions.destroy_all
    @user.destroy
    terminate_session
    redirect_to root_path, notice: "Account deleted successfully"
  end

  private

  def set_user
    @user = Current.user
  end

  def user_params
    params.require(:user).permit(:name, :email_address)
  end
end
```

## Adding Password Change

```ruby
# app/controllers/account_passwords_controller.rb
class AccountPasswordsController < ApplicationController
  def edit
  end

  def update
    if Current.user.authenticate(params[:current_password])
      if Current.user.update(password_params)
        # Invalidate other sessions
        Current.user.sessions.where.not(id: Current.session.id).destroy_all
        redirect_to account_path, notice: "Password changed successfully"
      else
        flash.now[:alert] = "Could not update password"
        render :edit, status: :unprocessable_entity
      end
    else
      flash.now[:alert] = "Current password is incorrect"
      render :edit, status: :unprocessable_entity
    end
  end

  private

  def password_params
    params.permit(:password, :password_confirmation)
  end
end
```

## Adding Session Management (View All Sessions)

```ruby
# app/controllers/sessions_management_controller.rb
class SessionsManagementController < ApplicationController
  def index
    @sessions = Current.user.sessions.order(created_at: :desc)
    @current_session = Current.session
  end

  def destroy
    session = Current.user.sessions.find(params[:id])

    if session == Current.session
      redirect_to sessions_management_path, alert: "Cannot revoke current session"
    else
      session.destroy
      redirect_to sessions_management_path, notice: "Session revoked"
    end
  end

  def destroy_all
    Current.user.sessions.where.not(id: Current.session.id).destroy_all
    redirect_to sessions_management_path, notice: "All other sessions revoked"
  end
end
```

```erb
<!-- app/views/sessions_management/index.html.erb -->
<h1>Active Sessions</h1>

<% @sessions.each do |session| %>
  <div class="<%= 'bg-green-50' if session == @current_session %>">
    <p><strong>IP:</strong> <%= session.ip_address %></p>
    <p><strong>Browser:</strong> <%= session.user_agent&.truncate(50) %></p>
    <p><strong>Created:</strong> <%= time_ago_in_words(session.created_at) %> ago</p>

    <% if session == @current_session %>
      <span class="text-green-600">Current session</span>
    <% else %>
      <%= button_to "Revoke", session_management_path(session), method: :delete,
          class: "text-red-600", data: { turbo_confirm: "Revoke this session?" } %>
    <% end %>
  </div>
<% end %>

<%= button_to "Sign out everywhere else", destroy_all_sessions_management_path,
    method: :delete, data: { turbo_confirm: "Sign out of all other sessions?" } %>
```

## Adding Roles/Admin Flag

```bash
bin/rails generate migration AddAdminToUsers admin:boolean
```

```ruby
# db/migrate/XXXXXX_add_admin_to_users.rb
class AddAdminToUsers < ActiveRecord::Migration[8.0]
  def change
    add_column :users, :admin, :boolean, default: false, null: false
  end
end
```

```ruby
# app/models/user.rb
class User < ApplicationRecord
  # ... existing code ...

  def admin?
    admin
  end
end

# app/controllers/admin/base_controller.rb
module Admin
  class BaseController < ApplicationController
    before_action :require_admin

    private

    def require_admin
      unless Current.user&.admin?
        redirect_to root_path, alert: "Access denied"
      end
    end
  end
end
```

## Next Steps

- [turbo-integration.md](./turbo-integration.md): Ensure all forms work with Turbo
- [../patterns/two-factor.md](../patterns/two-factor.md): Add 2FA
- [../oauth/omniauth.md](../oauth/omniauth.md): Add social login
