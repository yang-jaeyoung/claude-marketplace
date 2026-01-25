# ActionCable Connections

## Overview

The Connection class handles WebSocket authentication and identification. It verifies user credentials and establishes the identity used throughout channel subscriptions.

## When to Use

- When authenticating WebSocket connections
- When identifying connected users
- When rejecting unauthorized connections
- When implementing custom authentication (JWT, API tokens)

## Quick Start

### Basic Session-based Authentication

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      self.current_user = find_verified_user
    end

    private

    def find_verified_user
      if verified_user = User.find_by(id: cookies.encrypted[:user_id])
        verified_user
      else
        reject_unauthorized_connection
      end
    end
  end
end
```

### Rails 8 Built-in Authentication

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      self.current_user = find_verified_user
    end

    private

    def find_verified_user
      if session = Session.find_by(id: cookies.signed[:session_id])
        session.user
      else
        reject_unauthorized_connection
      end
    end
  end
end
```

## Main Patterns

### Pattern 1: Devise Integration

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      self.current_user = find_verified_user
    end

    private

    def find_verified_user
      if verified_user = env["warden"].user
        verified_user
      else
        reject_unauthorized_connection
      end
    end
  end
end
```

### Pattern 2: JWT Token Authentication

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      self.current_user = find_verified_user
    end

    private

    def find_verified_user
      token = request.params[:token]

      if token.present?
        decoded = decode_jwt(token)
        User.find_by(id: decoded["user_id"])
      else
        reject_unauthorized_connection
      end
    rescue JWT::DecodeError, JWT::ExpiredSignature
      reject_unauthorized_connection
    end

    def decode_jwt(token)
      JWT.decode(
        token,
        Rails.application.credentials.secret_key_base,
        true,
        { algorithm: "HS256" }
      ).first
    end
  end
end
```

```javascript
// Client-side with JWT
import { createConsumer } from "@rails/actioncable"

const token = localStorage.getItem("jwt_token")
export default createConsumer(`/cable?token=${token}`)
```

### Pattern 3: API Token Authentication

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      self.current_user = find_verified_user
    end

    private

    def find_verified_user
      token = request.params[:api_token] ||
              request.headers["Authorization"]&.split(" ")&.last

      if user = User.find_by(api_token: token)
        user
      else
        reject_unauthorized_connection
      end
    end
  end
end
```

### Pattern 4: Multiple Identifiers

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user, :current_tenant

    def connect
      self.current_user = find_verified_user
      self.current_tenant = find_tenant
    end

    private

    def find_verified_user
      if verified_user = User.find_by(id: cookies.encrypted[:user_id])
        verified_user
      else
        reject_unauthorized_connection
      end
    end

    def find_tenant
      subdomain = request.subdomain
      Tenant.find_by(subdomain: subdomain) || Tenant.default
    end
  end
end
```

### Pattern 5: Anonymous Connections (Guest Access)

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :connection_identifier

    def connect
      self.connection_identifier = find_or_create_identifier
    end

    private

    def find_or_create_identifier
      # Prefer authenticated user
      if user = User.find_by(id: cookies.encrypted[:user_id])
        "user_#{user.id}"
      else
        # Fall back to guest identifier
        cookies.encrypted[:guest_id] ||= SecureRandom.uuid
        "guest_#{cookies.encrypted[:guest_id]}"
      end
    end
  end
end

# Usage in channels
class PublicChannel < ApplicationCable::Channel
  def subscribed
    if connection_identifier.start_with?("user_")
      stream_from "public_authenticated"
    else
      stream_from "public_guest"
    end
  end
end
```

### Pattern 6: Connection Logging

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      self.current_user = find_verified_user
      logger.add_tags "ActionCable", "User:#{current_user.id}"
    end

    def disconnect
      logger.info "User #{current_user&.id} disconnected"
    end

    private

    def find_verified_user
      if verified_user = User.find_by(id: cookies.encrypted[:user_id])
        logger.info "User #{verified_user.id} connected from #{request.remote_ip}"
        verified_user
      else
        logger.warn "Unauthorized connection attempt from #{request.remote_ip}"
        reject_unauthorized_connection
      end
    end
  end
end
```

### Pattern 7: Connection with Rate Limiting

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      check_rate_limit!
      self.current_user = find_verified_user
      record_connection
    end

    private

    def check_rate_limit!
      key = "cable_connections:#{request.remote_ip}"
      count = Rails.cache.increment(key, 1, expires_in: 1.minute)

      if count > 10 # Max 10 connections per minute per IP
        reject_unauthorized_connection
      end
    end

    def record_connection
      Rails.cache.write(
        "user_#{current_user.id}_connected",
        true,
        expires_in: 5.minutes
      )
    end

    def find_verified_user
      User.find_by(id: cookies.encrypted[:user_id]) ||
        reject_unauthorized_connection
    end
  end
end
```

### Pattern 8: Custom Headers Authentication

```ruby
# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      self.current_user = find_verified_user
    end

    private

    def find_verified_user
      # Access request headers
      auth_header = request.headers["X-Auth-Token"]

      if auth_header && (user = User.find_by(auth_token: auth_header))
        user
      else
        reject_unauthorized_connection
      end
    end
  end
end
```

## Available Request Data

```ruby
# In Connection class, you have access to:
request.params        # Query parameters
request.headers       # HTTP headers
request.session       # Session data (if using session store)
request.remote_ip     # Client IP
request.uuid          # Request UUID
cookies              # Cookie jar
env                  # Rack environment
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No authentication | Unauthorized access | Always verify user |
| Blocking database calls | Connection delays | Cache user data |
| Missing reject call | Undefined behavior | Call reject_unauthorized_connection |
| Storing secrets in cookies | Security risk | Use encrypted cookies |
| No connection logging | Debugging difficulty | Add tagged logging |

## Related Skills

- [setup.md](./setup.md): ActionCable configuration
- [channels.md](./channels.md): Channel patterns
- [../../auth/SKILL.md](../../auth/SKILL.md): Authentication patterns

## References

- [Action Cable Connections](https://guides.rubyonrails.org/action_cable_overview.html#connection-setup)
- [ActionCable Connection API](https://api.rubyonrails.org/classes/ActionCable/Connection/Base.html)
