# Two-Factor Authentication (2FA)

## Overview

Implementing TOTP-based two-factor authentication using devise-two-factor. Adds an additional security layer requiring a time-based one-time password from an authenticator app.

## When to Use

- When securing sensitive user accounts
- When compliance requires MFA (PCI-DSS, SOC2, HIPAA)
- When protecting admin/privileged accounts
- When users handle financial or personal data

## Quick Start

```ruby
# Gemfile
gem "devise-two-factor"
gem "rqrcode"  # For QR code generation
```

```bash
bundle install
rails g devise_two_factor User
rails db:migrate
```

## Main Patterns

### Pattern 1: Installation

```ruby
# Gemfile
gem "devise-two-factor", "~> 5.0"
gem "rqrcode", "~> 2.0"  # QR code generation
```

```bash
bundle install
rails generate devise_two_factor User
rails db:migrate
```

Generated migration adds:
- `otp_secret` - Encrypted secret key
- `consumed_timestep` - Prevents replay attacks
- `otp_required_for_login` - Enable/disable per user

### Pattern 2: User Model Configuration

```ruby
# app/models/user.rb
class User < ApplicationRecord
  devise :two_factor_authenticatable,
         :two_factor_backupable,
         otp_backup_code_length: 16,
         otp_number_of_backup_codes: 10,
         otp_secret_encryption_key: Rails.application.credentials.otp_secret_key

  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable

  # Backup codes stored encrypted
  serialize :otp_backup_codes, coder: JSON

  def enable_two_factor!
    self.otp_secret = User.generate_otp_secret
    self.otp_required_for_login = true
    save!
  end

  def disable_two_factor!
    self.otp_secret = nil
    self.otp_required_for_login = false
    self.otp_backup_codes = nil
    save!
  end

  def two_factor_enabled?
    otp_required_for_login?
  end

  def otp_provisioning_uri
    otp_provisioning_uri(email, issuer: Rails.application.config.app_name)
  end

  def generate_new_backup_codes!
    codes = generate_otp_backup_codes!
    save!
    codes  # Return plain codes to show user once
  end
end
```

### Pattern 3: Generate OTP Secret Key

```bash
# Add to credentials
rails credentials:edit
```

```yaml
# config/credentials.yml.enc
otp_secret_key: "your-32-character-base32-secret-key"

# Generate with:
# SecureRandom.hex(32)
```

### Pattern 4: Two-Factor Setup Controller

```ruby
# app/controllers/users/two_factor_controller.rb
class Users::TwoFactorController < ApplicationController
  before_action :authenticate_user!

  # GET /users/two_factor/new - Setup page
  def new
    if current_user.two_factor_enabled?
      redirect_to edit_user_registration_path, notice: "2FA is already enabled"
      return
    end

    # Generate temporary secret (not saved yet)
    current_user.otp_secret = User.generate_otp_secret
    @qr_code = generate_qr_code
  end

  # POST /users/two_factor - Verify and enable
  def create
    current_user.otp_secret = params[:otp_secret]

    if current_user.validate_and_consume_otp!(params[:otp_attempt])
      current_user.otp_required_for_login = true
      @backup_codes = current_user.generate_new_backup_codes!
      current_user.save!

      render :backup_codes
    else
      current_user.otp_secret = User.generate_otp_secret
      @qr_code = generate_qr_code
      flash.now[:alert] = "Invalid code. Please try again."
      render :new, status: :unprocessable_entity
    end
  end

  # DELETE /users/two_factor - Disable
  def destroy
    if current_user.validate_and_consume_otp!(params[:otp_attempt])
      current_user.disable_two_factor!
      redirect_to edit_user_registration_path, notice: "2FA has been disabled"
    else
      redirect_to edit_user_registration_path, alert: "Invalid code"
    end
  end

  # POST /users/two_factor/backup_codes - Regenerate backup codes
  def regenerate_backup_codes
    if current_user.validate_and_consume_otp!(params[:otp_attempt])
      @backup_codes = current_user.generate_new_backup_codes!
      render :backup_codes
    else
      redirect_to edit_user_registration_path, alert: "Invalid code"
    end
  end

  private

  def generate_qr_code
    qr = RQRCode::QRCode.new(current_user.otp_provisioning_uri)
    qr.as_svg(
      color: "000",
      shape_rendering: "crispEdges",
      module_size: 4,
      standalone: true,
      use_path: true
    )
  end
end
```

### Pattern 5: Two-Factor Verification Controller

```ruby
# app/controllers/users/two_factor_verification_controller.rb
class Users::TwoFactorVerificationController < ApplicationController
  before_action :ensure_user_needs_two_factor

  # GET /users/two_factor_verification
  def new
    @user = User.find(session[:otp_user_id])
  end

  # POST /users/two_factor_verification
  def create
    @user = User.find(session[:otp_user_id])

    if @user.validate_and_consume_otp!(params[:otp_attempt])
      session.delete(:otp_user_id)
      sign_in(@user)
      redirect_to after_sign_in_path_for(@user)
    elsif @user.invalidate_otp_backup_code!(params[:otp_attempt])
      session.delete(:otp_user_id)
      sign_in(@user)
      flash[:warning] = "You've used a backup code. Consider generating new ones."
      redirect_to after_sign_in_path_for(@user)
    else
      flash.now[:alert] = "Invalid authentication code"
      render :new, status: :unprocessable_entity
    end
  end

  private

  def ensure_user_needs_two_factor
    redirect_to root_path unless session[:otp_user_id].present?
  end
end
```

### Pattern 6: Custom Sessions Controller

```ruby
# app/controllers/users/sessions_controller.rb
class Users::SessionsController < Devise::SessionsController
  def create
    self.resource = warden.authenticate(auth_options)

    if resource && resource.two_factor_enabled?
      # Don't sign in yet, redirect to 2FA
      session[:otp_user_id] = resource.id
      redirect_to new_users_two_factor_verification_path
    elsif resource
      sign_in(resource_name, resource)
      respond_with resource, location: after_sign_in_path_for(resource)
    else
      flash[:alert] = "Invalid email or password"
      redirect_to new_user_session_path
    end
  end
end
```

### Pattern 7: Setup Views

```erb
<%# app/views/users/two_factor/new.html.erb %>
<div class="max-w-md mx-auto py-8">
  <h1 class="text-2xl font-bold mb-6">Set Up Two-Factor Authentication</h1>

  <div class="bg-white shadow rounded-lg p-6 space-y-6">
    <div>
      <h2 class="font-medium mb-2">1. Scan QR Code</h2>
      <p class="text-sm text-gray-600 mb-4">
        Scan this QR code with your authenticator app (Google Authenticator, Authy, 1Password, etc.)
      </p>
      <div class="flex justify-center p-4 bg-white border rounded">
        <%= @qr_code.html_safe %>
      </div>
    </div>

    <div>
      <h2 class="font-medium mb-2">2. Enter Verification Code</h2>
      <%= form_with url: users_two_factor_path, method: :post, class: "space-y-4" do |f| %>
        <%= hidden_field_tag :otp_secret, current_user.otp_secret %>

        <div>
          <%= f.label :otp_attempt, "6-digit code", class: "block text-sm font-medium text-gray-700" %>
          <%= f.text_field :otp_attempt,
              autofocus: true,
              autocomplete: "one-time-code",
              inputmode: "numeric",
              pattern: "[0-9]*",
              maxlength: 6,
              class: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-center text-2xl tracking-widest" %>
        </div>

        <%= f.submit "Verify and Enable",
            class: "w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700" %>
      <% end %>
    </div>

    <p class="text-sm text-gray-500">
      Can't scan? Enter this code manually: <code class="bg-gray-100 px-2 py-1 rounded"><%= current_user.otp_secret %></code>
    </p>
  </div>
</div>
```

```erb
<%# app/views/users/two_factor/backup_codes.html.erb %>
<div class="max-w-md mx-auto py-8">
  <h1 class="text-2xl font-bold mb-6">Save Your Backup Codes</h1>

  <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
    <p class="text-yellow-800">
      <strong>Important:</strong> Save these backup codes in a secure place.
      Each code can only be used once. You won't see them again.
    </p>
  </div>

  <div class="bg-white shadow rounded-lg p-6">
    <div class="grid grid-cols-2 gap-2 font-mono text-sm">
      <% @backup_codes.each do |code| %>
        <div class="bg-gray-100 p-2 rounded text-center"><%= code %></div>
      <% end %>
    </div>

    <div class="mt-6 flex gap-4">
      <button onclick="copyBackupCodes()" class="flex-1 py-2 px-4 border rounded-md hover:bg-gray-50">
        Copy Codes
      </button>
      <%= link_to "Download", backup_codes_download_path, class: "flex-1 py-2 px-4 border rounded-md hover:bg-gray-50 text-center" %>
    </div>
  </div>

  <div class="mt-6 text-center">
    <%= link_to "I've saved my codes", root_path,
        class: "inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700" %>
  </div>
</div>

<script>
function copyBackupCodes() {
  const codes = <%= @backup_codes.to_json.html_safe %>;
  navigator.clipboard.writeText(codes.join('\n'));
  alert('Backup codes copied to clipboard');
}
</script>
```

### Pattern 8: Verification View

```erb
<%# app/views/users/two_factor_verification/new.html.erb %>
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
  <div class="max-w-md w-full">
    <h2 class="text-center text-3xl font-extrabold text-gray-900 mb-8">
      Two-Factor Authentication
    </h2>

    <%= form_with url: users_two_factor_verification_path, method: :post, class: "space-y-6" do |f| %>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Enter the 6-digit code from your authenticator app
        </label>
        <%= f.text_field :otp_attempt,
            autofocus: true,
            autocomplete: "one-time-code",
            inputmode: "numeric",
            pattern: "[0-9]*",
            maxlength: 6,
            class: "block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-center text-2xl tracking-widest" %>
      </div>

      <%= f.submit "Verify",
          class: "w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700" %>
    <% end %>

    <p class="mt-4 text-center text-sm text-gray-600">
      Lost your device? Use a
      <button onclick="showBackupForm()" class="text-indigo-600 hover:text-indigo-500">
        backup code
      </button>
    </p>
  </div>
</div>
```

## Routes

```ruby
# config/routes.rb
devise_for :users, controllers: {
  sessions: 'users/sessions'
}

namespace :users do
  resource :two_factor, only: [:new, :create, :destroy] do
    post :regenerate_backup_codes
  end
  resource :two_factor_verification, only: [:new, :create]
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Storing plain OTP secret | Secret theft | Use encrypted column |
| No backup codes | Users locked out | Generate 10 backup codes |
| Skipping rate limiting | Brute force attacks | Limit attempts |
| No session expiry | Session hijacking | Short 2FA session timeout |

## Related Skills

- [../devise/setup.md](../devise/setup.md): Devise setup
- [../devise/configuration.md](../devise/configuration.md): Devise config
- [api-tokens.md](./api-tokens.md): API authentication

## References

- [devise-two-factor](https://github.com/devise-two-factor/devise-two-factor)
- [rqrcode](https://github.com/whomwah/rqrcode)
- [TOTP RFC 6238](https://tools.ietf.org/html/rfc6238)
