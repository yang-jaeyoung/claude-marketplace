# Turbo Streams Authorization

## Overview

Securing Turbo Streams is critical to prevent unauthorized access to real-time data. Rails uses signed stream names and channel verification to ensure only authorized users receive broadcasts.

## When to Use

- When streams contain private/user-specific data
- When implementing multi-tenant applications
- When role-based stream access is needed
- When preventing stream enumeration attacks

## Quick Start

### Signed Streams (Default Security)

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
      User.find_by(id: cookies.encrypted[:user_id]) ||
        reject_unauthorized_connection
    end
  end
end
```

```erb
<!-- Signed stream (default with turbo_stream_from) -->
<%= turbo_stream_from @room %>

<!-- This generates a signed stream name that can't be tampered with -->
```

## Main Patterns

### Pattern 1: Custom Turbo::StreamsChannel Verification

```ruby
# app/channels/turbo/streams_channel.rb
class Turbo::StreamsChannel < ApplicationCable::Channel
  extend Turbo::Streams::StreamName
  include Turbo::Streams::Broadcasts

  def subscribed
    if verified_stream_name = Turbo::Streams::StreamName.verified_stream_name(params[:signed_stream_name])
      if authorized_to_stream?(verified_stream_name)
        stream_from verified_stream_name
      else
        reject
      end
    else
      reject
    end
  end

  private

  def authorized_to_stream?(stream_name)
    # Parse stream name and check authorization
    case stream_name
    when /^room:/
      room_id = stream_name.split(":").last
      Room.find(room_id).member?(current_user)
    when /^user:(\d+)/
      $1.to_i == current_user.id
    when /^admin/
      current_user.admin?
    else
      true # Public streams
    end
  end
end
```

### Pattern 2: Model-Level Authorization

```ruby
# app/models/room.rb
class Room < ApplicationRecord
  has_many :room_users
  has_many :users, through: :room_users

  def stream_name_for(user)
    return nil unless member?(user)
    "room:#{id}"
  end

  def member?(user)
    users.include?(user)
  end
end

# app/helpers/streams_helper.rb
module StreamsHelper
  def authorized_stream_from(room, user: current_user)
    stream_name = room.stream_name_for(user)
    turbo_stream_from(stream_name) if stream_name
  end
end
```

```erb
<%= authorized_stream_from(@room) %>
```

### Pattern 3: Custom Channel with Authorization

```ruby
# app/channels/secure_room_channel.rb
class SecureRoomChannel < ApplicationCable::Channel
  def subscribed
    @room = Room.find(params[:room_id])

    if authorized?
      stream_for @room
    else
      reject
    end
  end

  private

  def authorized?
    @room.member?(current_user) ||
      @room.public? ||
      current_user.admin?
  end
end
```

```erb
<!-- Subscribe via custom channel -->
<%= turbo_stream_from @room, channel: SecureRoomChannel %>
```

### Pattern 4: Policy-Based Authorization (Pundit)

```ruby
# app/policies/room_policy.rb
class RoomPolicy < ApplicationPolicy
  def subscribe?
    record.public? ||
      record.member?(user) ||
      user.admin?
  end
end

# app/channels/turbo/streams_channel.rb
class Turbo::StreamsChannel < ApplicationCable::Channel
  include Pundit::Authorization

  def subscribed
    verified_stream_name = verify_stream_name
    return reject unless verified_stream_name

    record = find_record_from_stream(verified_stream_name)
    return reject unless record

    if Pundit.policy(current_user, record).subscribe?
      stream_from verified_stream_name
    else
      reject
    end
  rescue Pundit::NotAuthorizedError
    reject
  end

  private

  def verify_stream_name
    Turbo::Streams::StreamName.verified_stream_name(params[:signed_stream_name])
  end

  def find_record_from_stream(stream_name)
    # Parse "rooms:Z2lkOi8v..." format
    parts = stream_name.split(":")
    return nil unless parts.length == 2

    model_name = parts.first.singularize.classify
    signed_id = parts.last

    model_name.constantize.find_signed(signed_id)
  rescue NameError, ActiveRecord::RecordNotFound
    nil
  end
end
```

### Pattern 5: Multi-Tenant Stream Isolation

```ruby
# app/models/concerns/tenant_scoped.rb
module TenantScoped
  extend ActiveSupport::Concern

  included do
    belongs_to :tenant

    # Override stream name to include tenant
    def to_gid_param
      "#{tenant_id}/#{super}"
    end
  end
end

# app/channels/application_cable/connection.rb
module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user, :current_tenant

    def connect
      self.current_user = find_verified_user
      self.current_tenant = current_user.tenant
    end
  end
end

# app/channels/turbo/streams_channel.rb
class Turbo::StreamsChannel < ApplicationCable::Channel
  def subscribed
    verified_stream_name = verify_stream_name
    return reject unless verified_stream_name

    # Verify tenant matches
    if stream_belongs_to_tenant?(verified_stream_name)
      stream_from verified_stream_name
    else
      reject
    end
  end

  private

  def stream_belongs_to_tenant?(stream_name)
    # Extract tenant from stream name
    tenant_id = stream_name.split("/").first.to_i
    tenant_id == current_tenant.id
  end
end
```

### Pattern 6: Time-Limited Stream Access

```ruby
# app/models/stream_token.rb
class StreamToken
  include ActiveModel::Model

  attr_accessor :stream_name, :user_id, :expires_at

  def self.generate(stream_name:, user:, expires_in: 1.hour)
    token_data = {
      stream_name: stream_name,
      user_id: user.id,
      expires_at: expires_in.from_now.to_i
    }

    Rails.application.message_verifier(:stream_tokens).generate(token_data)
  end

  def self.verify(token)
    data = Rails.application.message_verifier(:stream_tokens).verify(token)
    return nil if Time.at(data[:expires_at]) < Time.current
    new(data)
  rescue ActiveSupport::MessageVerifier::InvalidSignature
    nil
  end
end

# Controller
def show
  @room = Room.find(params[:id])
  @stream_token = StreamToken.generate(
    stream_name: "room:#{@room.id}",
    user: current_user,
    expires_in: 2.hours
  )
end
```

### Pattern 7: Read-Only vs Write Streams

```ruby
# app/channels/document_channel.rb
class DocumentChannel < ApplicationCable::Channel
  def subscribed
    @document = Document.find(params[:document_id])

    if can_view?
      stream_for @document
      @access_level = can_edit? ? :write : :read
    else
      reject
    end
  end

  def update_content(data)
    return unless @access_level == :write

    @document.update!(content: data["content"])
    # Broadcast update
  end

  private

  def can_view?
    @document.public? || @document.shared_with?(current_user)
  end

  def can_edit?
    @document.owner?(current_user) || @document.editor?(current_user)
  end
end
```

### Pattern 8: Logging Stream Access

```ruby
# app/channels/turbo/streams_channel.rb
class Turbo::StreamsChannel < ApplicationCable::Channel
  def subscribed
    verified_stream_name = verify_stream_name
    return reject_with_log("Invalid stream signature") unless verified_stream_name

    if authorized?(verified_stream_name)
      log_subscription(verified_stream_name, :success)
      stream_from verified_stream_name
    else
      reject_with_log("Unauthorized access to #{verified_stream_name}")
    end
  end

  private

  def reject_with_log(reason)
    log_subscription(params[:signed_stream_name], :rejected, reason)
    reject
  end

  def log_subscription(stream_name, status, reason = nil)
    Rails.logger.info({
      event: "stream_subscription",
      stream: stream_name,
      user_id: current_user&.id,
      status: status,
      reason: reason,
      ip: connection.env["REMOTE_ADDR"]
    }.compact.to_json)
  end
end
```

## Security Checklist

| Check | Implementation |
|-------|----------------|
| Stream names signed | Use `turbo_stream_from` helper |
| Connection authenticated | Implement `find_verified_user` |
| Channel authorization | Override `Turbo::StreamsChannel` |
| Tenant isolation | Include tenant in stream name |
| Audit logging | Log subscription attempts |
| Rate limiting | Implement in Connection |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Unsigned stream names | Stream enumeration | Use signed helpers |
| No authorization check | Data leakage | Verify in subscribed |
| Client-controlled stream names | Injection attacks | Server-side stream names |
| Missing tenant checks | Cross-tenant data | Include tenant in stream |
| No logging | Can't detect attacks | Add audit logging |

## Related Skills

- [../action-cable/connections.md](../action-cable/connections.md): Connection authentication
- [../../auth/SKILL.md](../../auth/SKILL.md): Authorization patterns
- [broadcasting.md](./broadcasting.md): Broadcasting basics

## References

- [Turbo Streams Security](https://turbo.hotwired.dev/handbook/streams#security)
- [Action Cable Security](https://guides.rubyonrails.org/action_cable_overview.html#consumer-side)
