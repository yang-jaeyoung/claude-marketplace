---
name: rails8-builtin-auth
description: Rails 8 built-in authentication generator. Lightweight, Turbo-compatible session-based auth without external dependencies.
triggers:
  - rails 8 authentication
  - builtin auth
  - generate authentication
  - has_secure_password
  - session authentication
  - 내장 인증
  - 레일즈8 인증
summary: |
  Rails 8 내장 인증 시스템을 다룹니다. bin/rails generate authentication으로 생성되는
  경량 인증 시스템으로, Devise 없이 세션 기반 인증을 구현합니다.
  간단한 인증이 필요하고 외부 의존성을 최소화하고 싶을 때 사용하세요.
token_cost: medium
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - setup.md
    - customization.md
  deep:
    - "**/*.md"
---

# Rails 8 Built-in Authentication

## Overview

Rails 8 introduces a built-in authentication generator that creates a lightweight, production-ready authentication system without external gems like Devise. It uses `has_secure_password` and session-based authentication.

## When to Use

| Use Built-in Auth | Use Devise Instead |
|-------------------|-------------------|
| Simple login/logout needed | Need email confirmation |
| Minimal dependencies preferred | Need account lockout |
| Full control over code desired | Need OAuth integration built-in |
| Learning Rails authentication | Need comprehensive admin features |
| Small to medium apps | Enterprise features needed |

## Quick Start

```bash
# Generate authentication
bin/rails generate authentication

# Run migrations
bin/rails db:migrate
```

## Generated Files

```
app/
├── models/
│   ├── user.rb                    # User model with has_secure_password
│   ├── session.rb                 # Session tracking model
│   └── current.rb                 # Current attributes (user, session)
├── controllers/
│   ├── sessions_controller.rb     # Login/logout
│   ├── passwords_controller.rb    # Password reset
│   └── concerns/
│       └── authentication.rb      # Authentication concern
├── views/
│   ├── sessions/
│   │   └── new.html.erb          # Login form
│   └── passwords/
│       ├── new.html.erb          # Password reset request
│       └── edit.html.erb         # Password reset form
├── mailers/
│   └── passwords_mailer.rb       # Password reset emails
db/
└── migrate/
    ├── XXXXXX_create_users.rb
    └── XXXXXX_create_sessions.rb
```

## Features Included

| Feature | Included | Notes |
|---------|----------|-------|
| Login/Logout | Yes | Session-based |
| Password Reset | Yes | Token-based email flow |
| Session Tracking | Yes | Multi-device sessions |
| Rate Limiting | Yes | 10 attempts per 3 minutes |
| Secure Password | Yes | bcrypt via has_secure_password |
| Remember Me | No | Manual implementation needed |
| Registration | No | Manual implementation needed |
| OAuth | No | Use OmniAuth separately |
| 2FA | No | Manual implementation needed |
| Email Confirmation | No | Manual implementation needed |

## Core Components

### User Model

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_secure_password
  has_many :sessions, dependent: :destroy

  normalizes :email_address, with: -> { _1.strip.downcase }

  validates :email_address, presence: true, uniqueness: true,
            format: { with: URI::MailTo::EMAIL_REGEXP }
end
```

### Session Model

```ruby
# app/models/session.rb
class Session < ApplicationRecord
  belongs_to :user

  before_create do
    self.user_agent = Current.user_agent
    self.ip_address = Current.ip_address
  end
end
```

### Authentication Concern

```ruby
# app/controllers/concerns/authentication.rb
module Authentication
  extend ActiveSupport::Concern

  included do
    before_action :require_authentication
    helper_method :authenticated?
  end

  class_methods do
    def allow_unauthenticated_access(**options)
      skip_before_action :require_authentication, **options
    end
  end

  private

  def authenticated?
    Current.session.present?
  end

  def require_authentication
    resume_session || request_authentication
  end

  def resume_session
    if session_record = find_session_by_cookie
      set_current_session(session_record)
    end
  end

  def find_session_by_cookie
    Session.find_by(id: cookies.signed[:session_id])
  end

  def request_authentication
    redirect_to new_session_path
  end

  def start_new_session_for(user)
    session_record = user.sessions.create!
    Current.session = session_record
    cookies.signed.permanent[:session_id] = { value: session_record.id, httponly: true }
  end

  def terminate_session
    Current.session&.destroy
    cookies.delete(:session_id)
  end
end
```

## File Structure

```
builtin/
├── SKILL.md           # This file
├── setup.md           # Generation and configuration
├── customization.md   # Extending the generated code
└── turbo-integration.md  # Turbo/Hotwire compatibility
```

## Comparison with Devise

| Aspect | Built-in Auth | Devise |
|--------|--------------|--------|
| Setup complexity | Very simple | Moderate |
| Lines of code | ~200 | ~10,000+ |
| Customization | Full control | Override generators |
| Dependencies | None | devise gem |
| Learning curve | Low | Moderate |
| Community support | Rails core | Large ecosystem |
| Modules | Basic | 10+ optional modules |

## Security Features

### Rate Limiting (Rails 8)

```ruby
# app/controllers/sessions_controller.rb
class SessionsController < ApplicationController
  rate_limit to: 10, within: 3.minutes, only: :create,
             with: -> { redirect_to new_session_path, alert: "Try again later" }
end
```

### Session Security

- HTTP-only cookies prevent XSS access
- Signed cookies prevent tampering
- Session records allow forced logout
- IP and User-Agent tracking for audit

## Related Documentation

- [setup.md](./setup.md): Detailed setup instructions
- [customization.md](./customization.md): Extending with registration, etc.
- [turbo-integration.md](./turbo-integration.md): Turbo compatibility patterns
- [../devise/](../devise/): When to use Devise instead

## References

- [Rails 8.0 Release Notes](https://guides.rubyonrails.org/8_0_release_notes.html)
- [has_secure_password Documentation](https://api.rubyonrails.org/classes/ActiveModel/SecurePassword/ClassMethods.html)
- [Rails Security Guide](https://guides.rubyonrails.org/security.html)
