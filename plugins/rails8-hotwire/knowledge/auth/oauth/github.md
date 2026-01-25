# GitHub OAuth Configuration

## Overview

Complete guide to implementing GitHub authentication using OmniAuth in Rails 8 applications. Covers OAuth App creation, scope configuration, organization access, and GitHub-specific features.

## When to Use

- When implementing "Sign in with GitHub"
- When building developer tools or platforms
- When requiring GitHub organization membership
- When accessing GitHub APIs on behalf of users

## Quick Start

```ruby
# Gemfile
gem "omniauth-github", "~> 2.0"
gem "omniauth-rails_csrf_protection"
```

```ruby
# config/initializers/omniauth.rb
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :github,
    Rails.application.credentials.dig(:github, :client_id),
    Rails.application.credentials.dig(:github, :client_secret),
    scope: "user:email"
end
```

## Main Patterns

### Pattern 1: GitHub OAuth App Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **OAuth Apps** > **New OAuth App**
3. Fill in application details:

```
Application name: Your App Name
Homepage URL: https://yourapp.com
Authorization callback URL: https://yourapp.com/users/auth/github/callback
```

4. After creation, copy **Client ID** and generate **Client Secret**

### Pattern 2: Full Configuration

```ruby
# config/initializers/omniauth.rb
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :github,
    Rails.application.credentials.dig(:github, :client_id),
    Rails.application.credentials.dig(:github, :client_secret),
    {
      # Scopes
      scope: "user:email,read:user,read:org",

      # Callback URL (optional, uses default)
      # callback_url: "https://yourapp.com/auth/github/callback",

      # Allow signup (default: true)
      # allow_signup: false,

      # Redirect options
      # redirect_uri: "...",

      # Provider options
      provider_ignores_state: false
    }
end
```

### Pattern 3: Available Scopes

```ruby
# Basic user info (default - no scope needed)
scope: ""

# Email access (recommended)
scope: "user:email"

# Full user profile
scope: "user"

# Read user profile
scope: "read:user"

# Organization membership
scope: "read:org"

# Repository access
scope: "repo"                      # Full access to repos
scope: "public_repo"               # Public repos only

# Gist access
scope: "gist"

# Combined scopes (comma or space separated)
scope: "user:email,read:user,read:org"
scope: "user:email read:user read:org"
```

### Pattern 4: Callback Controller

```ruby
# app/controllers/users/omniauth_callbacks_controller.rb
class Users::OmniauthCallbacksController < Devise::OmniauthCallbacksController
  def github
    auth = request.env["omniauth.auth"]

    # Optional: Verify organization membership
    unless authorized_organization?(auth)
      redirect_to root_path, alert: "You must be a member of our organization"
      return
    end

    @user = User.from_github_oauth(auth)

    if @user.persisted?
      sign_in_and_redirect @user, event: :authentication
      set_flash_message(:notice, :success, kind: "GitHub") if is_navigational_format?
    else
      session["devise.github_data"] = auth.except(:extra)
      redirect_to new_user_registration_url,
                  alert: @user.errors.full_messages.join("\n")
    end
  end

  private

  def authorized_organization?(auth)
    return true unless Rails.application.config.x.required_github_org.present?

    token = auth.credentials.token
    orgs = fetch_user_organizations(token)

    orgs.any? { |org| org["login"] == Rails.application.config.x.required_github_org }
  end

  def fetch_user_organizations(token)
    response = Faraday.get("https://api.github.com/user/orgs") do |req|
      req.headers["Authorization"] = "Bearer #{token}"
      req.headers["Accept"] = "application/vnd.github.v3+json"
    end

    response.success? ? JSON.parse(response.body) : []
  end
end
```

### Pattern 5: User Model with GitHub Fields

```ruby
# app/models/user.rb
class User < ApplicationRecord
  def self.from_github_oauth(auth)
    identity = Identity.find_by(provider: "github", uid: auth.uid)
    return identity.user if identity

    # GitHub may not provide email in info if private
    email = auth.info.email || fetch_primary_email(auth.credentials.token)

    user = find_or_initialize_by(email: email)

    if user.new_record?
      user.assign_attributes(
        name: auth.info.name || auth.info.nickname,
        avatar_url: auth.info.image,
        password: Devise.friendly_token[0, 20],
        github_username: auth.info.nickname
      )
    end

    user.save!

    Identity.create!(
      user: user,
      provider: auth.provider,
      uid: auth.uid,
      token: auth.credentials.token
    )

    user
  end

  def self.fetch_primary_email(token)
    response = Faraday.get("https://api.github.com/user/emails") do |req|
      req.headers["Authorization"] = "Bearer #{token}"
      req.headers["Accept"] = "application/vnd.github.v3+json"
    end

    return nil unless response.success?

    emails = JSON.parse(response.body)
    primary = emails.find { |e| e["primary"] && e["verified"] }
    primary&.dig("email")
  end
end
```

### Pattern 6: Organization Membership Check

```ruby
# app/services/github_org_checker.rb
class GithubOrgChecker
  def initialize(token)
    @token = token
  end

  def member_of?(organization)
    response = Faraday.get("https://api.github.com/user/memberships/orgs/#{organization}") do |req|
      req.headers["Authorization"] = "Bearer #{@token}"
      req.headers["Accept"] = "application/vnd.github.v3+json"
    end

    return false unless response.success?

    membership = JSON.parse(response.body)
    membership["state"] == "active"
  end

  def organizations
    response = Faraday.get("https://api.github.com/user/orgs") do |req|
      req.headers["Authorization"] = "Bearer #{@token}"
      req.headers["Accept"] = "application/vnd.github.v3+json"
    end

    return [] unless response.success?

    JSON.parse(response.body).map { |org| org["login"] }
  end
end
```

### Pattern 7: GitHub App vs OAuth App

For GitHub Apps (more granular permissions):

```ruby
# Gemfile
gem "omniauth-github-app"

# config/initializers/omniauth.rb
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :github_app,
    Rails.application.credentials.dig(:github_app, :client_id),
    Rails.application.credentials.dig(:github_app, :client_secret),
    scope: "user:email",
    setup: ->(env) {
      env['omniauth.strategy'].options[:client_options][:site] = 'https://github.com'
    }
end
```

### Pattern 8: Handling Private Emails

```ruby
# app/services/github_email_fetcher.rb
class GithubEmailFetcher
  def initialize(token)
    @token = token
  end

  def fetch_verified_email
    response = Faraday.get("https://api.github.com/user/emails") do |req|
      req.headers["Authorization"] = "Bearer #{@token}"
      req.headers["Accept"] = "application/vnd.github.v3+json"
    end

    return nil unless response.success?

    emails = JSON.parse(response.body)

    # Priority: primary verified > any verified > primary > any
    primary_verified = emails.find { |e| e["primary"] && e["verified"] }
    return primary_verified["email"] if primary_verified

    any_verified = emails.find { |e| e["verified"] }
    return any_verified["email"] if any_verified

    primary = emails.find { |e| e["primary"] }
    return primary["email"] if primary

    emails.first&.dig("email")
  end
end
```

## Auth Hash Structure

```ruby
# request.env["omniauth.auth"]
{
  provider: "github",
  uid: "12345",
  info: {
    nickname: "johndoe",
    email: "john@example.com",  # May be nil if email is private
    name: "John Doe",
    image: "https://avatars.githubusercontent.com/u/12345?v=4",
    urls: {
      GitHub: "https://github.com/johndoe",
      Blog: "https://johndoe.dev"
    }
  },
  credentials: {
    token: "gho_xxxxxxxxxxxx",
    expires: false
  },
  extra: {
    raw_info: {
      login: "johndoe",
      id: 12345,
      avatar_url: "https://avatars.githubusercontent.com/u/12345?v=4",
      html_url: "https://github.com/johndoe",
      name: "John Doe",
      company: "ACME Corp",
      blog: "https://johndoe.dev",
      location: "San Francisco, CA",
      email: "john@example.com",
      bio: "Software developer",
      public_repos: 42,
      followers: 100,
      following: 50,
      created_at: "2015-01-01T00:00:00Z"
    }
  }
}
```

## Enterprise GitHub

```ruby
# For GitHub Enterprise
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :github,
    Rails.application.credentials.dig(:github, :client_id),
    Rails.application.credentials.dig(:github, :client_secret),
    {
      scope: "user:email,read:org",
      client_options: {
        site: "https://github.yourcompany.com/api/v3",
        authorize_url: "https://github.yourcompany.com/login/oauth/authorize",
        token_url: "https://github.yourcompany.com/login/oauth/access_token"
      }
    }
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No email scope | Email may be nil | Always request `user:email` |
| Trusting nickname as unique | Can be changed | Use `uid` as identifier |
| Not handling private email | User creation fails | Fetch from `/user/emails` API |
| Storing token insecurely | Token theft | Encrypt in database |

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Email is nil | Private email | Add `user:email` scope, fetch from API |
| "Bad credentials" | Invalid/expired token | Check client ID/secret |
| Org check fails | Missing scope | Add `read:org` scope |
| Callback mismatch | Wrong URL | Verify in GitHub settings |

## Related Skills

- [omniauth.md](./omniauth.md): Base OmniAuth setup
- [../devise/controllers.md](../devise/controllers.md): Devise integration

## References

- [omniauth-github](https://github.com/omniauth/omniauth-github)
- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [GitHub API Scopes](https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps)
