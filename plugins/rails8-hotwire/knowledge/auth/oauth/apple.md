# Apple Sign In Configuration

## Overview

Complete guide to implementing Sign in with Apple using OmniAuth in Rails 8 applications. Covers Apple Developer setup, private key handling, and Apple-specific considerations like user data restrictions.

## When to Use

- When offering Sign in with Apple (required for iOS apps with third-party login)
- When building cross-platform applications
- When users prefer privacy-focused authentication
- When complying with App Store requirements

## Quick Start

```ruby
# Gemfile
gem "omniauth-apple"
gem "omniauth-rails_csrf_protection"
```

```ruby
# config/initializers/omniauth.rb
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :apple,
    Rails.application.credentials.dig(:apple, :client_id),
    "",
    {
      scope: "email name",
      team_id: Rails.application.credentials.dig(:apple, :team_id),
      key_id: Rails.application.credentials.dig(:apple, :key_id),
      pem: Rails.application.credentials.dig(:apple, :private_key)
    }
end
```

## Main Patterns

### Pattern 1: Apple Developer Setup

1. Go to [Apple Developer Portal](https://developer.apple.com/account)
2. Navigate to **Certificates, Identifiers & Profiles**

#### Create App ID:
1. **Identifiers** > **App IDs** > **+**
2. Select "App IDs" and continue
3. Enter Description and Bundle ID
4. Enable "Sign in with Apple" capability
5. Click Continue and Register

#### Create Service ID:
1. **Identifiers** > **+** > "Services IDs"
2. Enter Description and Identifier (this is your `client_id`)
3. Enable "Sign in with Apple"
4. Configure domains and return URLs:
```
Domains: yourapp.com
Return URLs: https://yourapp.com/users/auth/apple/callback
```

#### Create Key:
1. **Keys** > **+**
2. Enter Key Name
3. Enable "Sign in with Apple"
4. Configure: Select your App ID
5. Register and download the `.p8` file
6. Note the Key ID

### Pattern 2: Full Configuration

```ruby
# config/initializers/omniauth.rb
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :apple,
    Rails.application.credentials.dig(:apple, :client_id),
    "",  # Empty string for client_secret (generated from private key)
    {
      scope: "email name",
      team_id: Rails.application.credentials.dig(:apple, :team_id),
      key_id: Rails.application.credentials.dig(:apple, :key_id),
      pem: Rails.application.credentials.dig(:apple, :private_key),

      # Optional settings
      # authorized_client_ids: ["com.yourapp.ios", "com.yourapp.web"],

      # Provider options
      provider_ignores_state: false
    }
end
```

### Pattern 3: Storing Apple Credentials

```bash
# Edit credentials
EDITOR="code --wait" rails credentials:edit
```

```yaml
# config/credentials.yml.enc
apple:
  client_id: "com.yourapp.service"      # Service ID Identifier
  team_id: "XXXXXXXXXX"                  # 10-character Team ID
  key_id: "XXXXXXXXXX"                   # 10-character Key ID
  private_key: |
    -----BEGIN PRIVATE KEY-----
    MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...
    ...
    -----END PRIVATE KEY-----
```

**Important:** The private key must be the contents of the `.p8` file with preserved newlines.

### Pattern 4: Callback Controller

```ruby
# app/controllers/users/omniauth_callbacks_controller.rb
class Users::OmniauthCallbacksController < Devise::OmniauthCallbacksController
  skip_before_action :verify_authenticity_token, only: :apple

  def apple
    auth = request.env["omniauth.auth"]

    # Apple provides name only on FIRST authorization
    # Store it immediately as it won't be available again
    @user = User.from_apple_oauth(auth, user_params_from_apple)

    if @user.persisted?
      sign_in_and_redirect @user, event: :authentication
      set_flash_message(:notice, :success, kind: "Apple") if is_navigational_format?
    else
      redirect_to new_user_registration_url,
                  alert: "Could not authenticate with Apple"
    end
  end

  private

  # Apple sends user info as form data on first auth
  def user_params_from_apple
    return {} unless params[:user].present?

    user_data = JSON.parse(params[:user]) rescue {}
    {
      first_name: user_data.dig("name", "firstName"),
      last_name: user_data.dig("name", "lastName"),
      email: user_data["email"]
    }
  end
end
```

### Pattern 5: User Model with Apple Support

```ruby
# app/models/user.rb
class User < ApplicationRecord
  def self.from_apple_oauth(auth, apple_params = {})
    identity = Identity.find_by(provider: "apple", uid: auth.uid)
    return identity.user if identity

    # Apple may hide real email - use relay email if needed
    email = auth.info.email || apple_params[:email]

    user = find_or_initialize_by(email: email) if email.present?
    user ||= new

    if user.new_record?
      user.assign_attributes(
        email: email,
        name: build_name(auth, apple_params),
        password: Devise.friendly_token[0, 20],
        apple_user: true
      )
    end

    user.save!

    Identity.create!(
      user: user,
      provider: auth.provider,
      uid: auth.uid,
      token: auth.credentials&.token
    )

    user
  end

  def self.build_name(auth, apple_params)
    # Try auth hash first, then apple_params
    first = auth.info.first_name || apple_params[:first_name]
    last = auth.info.last_name || apple_params[:last_name]

    [first, last].compact.join(" ").presence || "Apple User"
  end
end
```

### Pattern 6: Handling Private Relay Email

```ruby
# Apple may provide a relay email like: abc123@privaterelay.appleid.com
# This email forwards to user's real email

class User < ApplicationRecord
  def apple_relay_email?
    email&.ends_with?("@privaterelay.appleid.com")
  end

  def can_receive_email?
    # Apple relay emails work, but you can't verify ownership
    # Consider this when sending sensitive emails
    !apple_relay_email? || verified_apple_user?
  end
end
```

### Pattern 7: Web Button Implementation

```erb
<%# Apple requires specific styling for the button %>
<div id="appleid-signin"
     class="signin-button"
     data-controller="apple-signin"
     data-color="black"
     data-border="false"
     data-type="sign in"
     data-width="100%"
     data-height="44">
</div>

<%# Or use a form button (recommended for Rails) %>
<%= button_to user_apple_omniauth_authorize_path,
    method: :post,
    data: { turbo: false },
    class: "w-full flex items-center justify-center gap-3 px-4 py-2 bg-black text-white rounded-md hover:bg-gray-800" do %>
  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
    <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
  </svg>
  <span>Sign in with Apple</span>
<% end %>
```

### Pattern 8: iOS Native Integration

For iOS apps using ASAuthorizationController:

```ruby
# app/controllers/api/apple_auth_controller.rb
class Api::AppleAuthController < Api::BaseController
  skip_before_action :authenticate!

  def callback
    # Verify identity token from iOS app
    payload = verify_apple_token(params[:identity_token])

    unless payload
      render json: { error: "Invalid token" }, status: :unauthorized
      return
    end

    user = User.from_apple_payload(
      uid: payload["sub"],
      email: payload["email"],
      name: params[:full_name]  # From iOS
    )

    render json: {
      user: UserSerializer.new(user),
      token: user.generate_api_token
    }
  end

  private

  def verify_apple_token(token)
    require 'jwt'

    # Fetch Apple's public keys
    response = Faraday.get("https://appleid.apple.com/auth/keys")
    jwks = JSON.parse(response.body)

    # Decode and verify
    JWT.decode(
      token,
      nil,
      true,
      {
        algorithms: ["RS256"],
        jwks: jwks,
        iss: "https://appleid.apple.com",
        aud: Rails.application.credentials.dig(:apple, :client_id),
        verify_iss: true,
        verify_aud: true
      }
    ).first
  rescue JWT::DecodeError => e
    Rails.logger.error "Apple token verification failed: #{e.message}"
    nil
  end
end
```

## Auth Hash Structure

```ruby
# request.env["omniauth.auth"]
{
  provider: "apple",
  uid: "001234.abc123xyz.5678",  # Apple's unique user ID
  info: {
    sub: "001234.abc123xyz.5678",
    email: "abc123@privaterelay.appleid.com",  # Or real email
    first_name: "John",   # Only on first auth!
    last_name: "Doe",     # Only on first auth!
    name: "John Doe"      # Only on first auth!
  },
  credentials: {
    token: "access_token_here",
    refresh_token: "refresh_token_here",
    expires_at: 1234567890,
    expires: true
  },
  extra: {
    raw_info: {
      iss: "https://appleid.apple.com",
      aud: "com.yourapp.service",
      exp: 1234567890,
      iat: 1234567890,
      sub: "001234.abc123xyz.5678",
      email: "abc123@privaterelay.appleid.com",
      email_verified: "true",
      is_private_email: "true",
      auth_time: 1234567890
    }
  }
}
```

## Apple-Specific Considerations

| Consideration | Details |
|---------------|---------|
| Name only once | Apple sends name ONLY on first authorization |
| Private relay | Users can hide real email |
| Required styling | Must follow Apple's Human Interface Guidelines |
| Real device testing | Web flow works, but test iOS native too |
| Token refresh | Tokens expire, handle refresh |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Not storing name on first auth | Name lost forever | Parse and store `params[:user]` immediately |
| Requiring real email | Users can't use relay | Support private relay emails |
| Wrong button styling | App Store rejection | Follow Apple HIG |
| Hardcoded private key | Security risk | Use Rails credentials |

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "invalid_client" | Wrong Service ID | Verify Service ID matches callback URL |
| No email received | First auth with Hide Email | Email in relay format is valid |
| Name is empty | Not first authorization | Only sent once, cannot retrieve again |
| Key error | Invalid private key format | Ensure newlines preserved in credentials |

## Related Skills

- [omniauth.md](./omniauth.md): Base OmniAuth setup
- [../devise/controllers.md](../devise/controllers.md): Devise integration

## References

- [omniauth-apple](https://github.com/nhosoya/omniauth-apple)
- [Sign in with Apple Documentation](https://developer.apple.com/documentation/sign_in_with_apple)
- [Apple HIG - Sign in with Apple](https://developer.apple.com/design/human-interface-guidelines/sign-in-with-apple)
