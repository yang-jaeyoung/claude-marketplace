# Google OAuth2 Configuration

## Overview

Complete guide to implementing Google Sign-In using OmniAuth in Rails 8 applications. Covers Google Cloud Console setup, scope configuration, and handling Google-specific features.

## When to Use

- When implementing "Sign in with Google"
- When accessing Google APIs on behalf of users
- When building GSuite/Google Workspace integrations
- When implementing one-tap sign-in

## Quick Start

```ruby
# Gemfile
gem "omniauth-google-oauth2"
gem "omniauth-rails_csrf_protection"
```

```ruby
# config/initializers/omniauth.rb
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :google_oauth2,
    Rails.application.credentials.dig(:google, :client_id),
    Rails.application.credentials.dig(:google, :client_secret),
    scope: "email,profile"
end
```

## Main Patterns

### Pattern 1: Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable "Google+ API" (for profile) and "Google Identity" APIs
4. Go to **APIs & Services > Credentials**
5. Click **Create Credentials > OAuth client ID**
6. Select **Web application**
7. Configure authorized redirect URIs:

```
# Development
http://localhost:3000/users/auth/google_oauth2/callback
http://localhost:3000/auth/google_oauth2/callback

# Production
https://yourapp.com/users/auth/google_oauth2/callback
https://yourapp.com/auth/google_oauth2/callback
```

### Pattern 2: Full Configuration

```ruby
# config/initializers/omniauth.rb
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :google_oauth2,
    Rails.application.credentials.dig(:google, :client_id),
    Rails.application.credentials.dig(:google, :client_secret),
    {
      # Basic scopes
      scope: "email,profile",

      # UI options
      prompt: "select_account",          # Always show account selector
      # prompt: "consent",               # Always show consent screen
      # prompt: "none",                  # Silent auth (if already authorized)

      # Image settings
      image_aspect_ratio: "square",
      image_size: 200,

      # Access type
      access_type: "offline",            # Get refresh token
      # access_type: "online",           # No refresh token (default)

      # Additional parameters
      include_granted_scopes: true,
      hd: "yourcompany.com",             # Restrict to domain (GSuite)
      login_hint: "user@example.com",    # Pre-fill email

      # OpenID Connect
      skip_jwt: false,                   # Parse ID token

      # Provider options
      provider_ignores_state: false      # Security: validate state
    }
end
```

### Pattern 3: Store Credentials Securely

```bash
# Edit credentials
EDITOR="code --wait" rails credentials:edit
```

```yaml
# config/credentials.yml.enc
google:
  client_id: "123456789.apps.googleusercontent.com"
  client_secret: "your-client-secret"
```

### Pattern 4: Common Scopes

```ruby
# Basic profile (recommended minimum)
scope: "email,profile"

# OpenID Connect (recommended)
scope: "openid,email,profile"

# Google Calendar
scope: "email,profile,https://www.googleapis.com/auth/calendar"

# Google Drive
scope: "email,profile,https://www.googleapis.com/auth/drive"

# Gmail (read only)
scope: "email,profile,https://www.googleapis.com/auth/gmail.readonly"

# YouTube
scope: "email,profile,https://www.googleapis.com/auth/youtube.readonly"

# Google Workspace Admin
scope: "email,profile,https://www.googleapis.com/auth/admin.directory.user.readonly"
```

### Pattern 5: Callback Handling

```ruby
# app/controllers/users/omniauth_callbacks_controller.rb
class Users::OmniauthCallbacksController < Devise::OmniauthCallbacksController
  def google_oauth2
    auth = request.env["omniauth.auth"]

    # Verify email is from allowed domain (optional)
    unless allowed_domain?(auth.info.email)
      redirect_to root_path, alert: "Only @yourcompany.com emails allowed"
      return
    end

    @user = User.from_google_oauth(auth)

    if @user.persisted?
      sign_in_and_redirect @user, event: :authentication
      set_flash_message(:notice, :success, kind: "Google") if is_navigational_format?
    else
      session["devise.google_data"] = auth.except(:extra)
      redirect_to new_user_registration_url,
                  alert: @user.errors.full_messages.join("\n")
    end
  end

  private

  def allowed_domain?(email)
    return true unless Rails.application.config.x.allowed_domains.present?

    domain = email.split("@").last
    Rails.application.config.x.allowed_domains.include?(domain)
  end
end
```

### Pattern 6: User Model with Google-Specific Fields

```ruby
# app/models/user.rb
class User < ApplicationRecord
  def self.from_google_oauth(auth)
    identity = Identity.find_by(provider: "google_oauth2", uid: auth.uid)
    return identity.user if identity

    user = find_or_initialize_by(email: auth.info.email)

    if user.new_record?
      user.assign_attributes(
        name: auth.info.name,
        avatar_url: auth.info.image,
        password: Devise.friendly_token[0, 20],
        # Google-specific
        google_uid: auth.uid,
        email_verified: auth.extra.raw_info["email_verified"]
      )
    end

    user.save!

    # Create identity for multi-provider support
    Identity.create!(
      user: user,
      provider: auth.provider,
      uid: auth.uid,
      token: auth.credentials.token,
      refresh_token: auth.credentials.refresh_token,
      expires_at: auth.credentials.expires_at ? Time.at(auth.credentials.expires_at) : nil
    )

    user
  end
end
```

### Pattern 7: Refreshing Access Tokens

```ruby
# app/models/identity.rb
class Identity < ApplicationRecord
  def token_expired?
    expires_at.present? && expires_at < Time.current
  end

  def refresh_google_token!
    return unless provider == "google_oauth2" && refresh_token.present?

    response = Faraday.post("https://oauth2.googleapis.com/token") do |req|
      req.body = {
        client_id: Rails.application.credentials.dig(:google, :client_id),
        client_secret: Rails.application.credentials.dig(:google, :client_secret),
        refresh_token: refresh_token,
        grant_type: "refresh_token"
      }
    end

    if response.success?
      data = JSON.parse(response.body)
      update!(
        token: data["access_token"],
        expires_at: Time.current + data["expires_in"].to_i.seconds
      )
    else
      Rails.logger.error "Failed to refresh Google token: #{response.body}"
      false
    end
  end

  def fresh_token
    refresh_google_token! if token_expired?
    token
  end
end
```

### Pattern 8: Google One Tap Sign-In

```erb
<%# app/views/layouts/application.html.erb %>
<head>
  <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>

<%# app/views/shared/_google_one_tap.html.erb %>
<div id="g_id_onload"
     data-client_id="<%= Rails.application.credentials.dig(:google, :client_id) %>"
     data-login_uri="<%= google_one_tap_callback_url %>"
     data-auto_prompt="true"
     data-context="signin"
     data-ux_mode="popup"
     data-callback="handleCredentialResponse">
</div>

<script>
function handleCredentialResponse(response) {
  fetch('<%= google_one_tap_callback_path %>', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': document.querySelector('[name="csrf-token"]').content
    },
    body: JSON.stringify({ credential: response.credential })
  }).then(res => {
    if (res.ok) {
      window.location.reload();
    }
  });
}
</script>
```

```ruby
# app/controllers/google_one_tap_controller.rb
class GoogleOneTapController < ApplicationController
  skip_before_action :authenticate_user!

  def callback
    payload = verify_google_token(params[:credential])

    if payload
      user = User.find_or_create_by(email: payload["email"]) do |u|
        u.name = payload["name"]
        u.google_uid = payload["sub"]
        u.avatar_url = payload["picture"]
        u.password = SecureRandom.hex(16)
      end

      sign_in(user)
      render json: { success: true }
    else
      render json: { error: "Invalid token" }, status: :unauthorized
    end
  end

  private

  def verify_google_token(token)
    require 'google-id-token'

    validator = GoogleIDToken::Validator.new
    validator.check(
      token,
      Rails.application.credentials.dig(:google, :client_id)
    )
  rescue GoogleIDToken::ValidationError => e
    Rails.logger.error "Google token validation failed: #{e.message}"
    nil
  end
end
```

## Auth Hash Structure

```ruby
# request.env["omniauth.auth"]
{
  provider: "google_oauth2",
  uid: "123456789",
  info: {
    name: "John Doe",
    email: "john@gmail.com",
    first_name: "John",
    last_name: "Doe",
    image: "https://lh3.googleusercontent.com/...",
    email_verified: true
  },
  credentials: {
    token: "ya29.access_token_here",
    refresh_token: "1//refresh_token_here",  # Only with access_type: "offline"
    expires_at: 1234567890,
    expires: true
  },
  extra: {
    id_token: "eyJhbGciOiJSUzI1NiIs...",  # JWT
    raw_info: {
      sub: "123456789",
      email: "john@gmail.com",
      email_verified: true,
      name: "John Doe",
      picture: "https://lh3.googleusercontent.com/...",
      given_name: "John",
      family_name: "Doe",
      locale: "en",
      hd: "yourcompany.com"  # Hosted domain (GSuite)
    }
  }
}
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Hardcoded credentials | Security risk | Use Rails credentials |
| Missing `hd` check | Non-domain users can sign in | Verify `hd` claim for GSuite |
| No refresh token | API calls fail after 1 hour | Use `access_type: "offline"` |
| Trusting email blindly | Email might not be verified | Check `email_verified` claim |

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "redirect_uri_mismatch" | URI not in allowed list | Add exact URI in Google Console |
| "invalid_client" | Wrong credentials | Check client ID/secret |
| No refresh token | Already authorized | Revoke access, use `prompt: "consent"` |
| "access_denied" | User declined | Handle gracefully in failure |

## Related Skills

- [omniauth.md](./omniauth.md): Base OmniAuth setup
- [../devise/controllers.md](../devise/controllers.md): Devise integration

## References

- [omniauth-google-oauth2](https://github.com/zquestz/omniauth-google-oauth2)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Sign-In for Websites](https://developers.google.com/identity/sign-in/web)
