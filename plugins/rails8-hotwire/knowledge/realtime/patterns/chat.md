# Chat Room Implementation

## Overview

Chat is the canonical real-time feature. This guide covers implementing full-featured chat rooms with message broadcasting, typing indicators, read receipts, and file attachments using Turbo Streams and ActionCable.

## When to Use

- When building messaging features
- When implementing team collaboration
- When creating customer support chat
- When adding real-time comments

## Quick Start

### Models

```ruby
# app/models/room.rb
class Room < ApplicationRecord
  has_many :messages, dependent: :destroy
  has_many :room_users, dependent: :destroy
  has_many :users, through: :room_users

  scope :for_user, ->(user) { joins(:room_users).where(room_users: { user_id: user.id }) }
end

# app/models/message.rb
class Message < ApplicationRecord
  belongs_to :room
  belongs_to :user

  broadcasts_to :room, inserts_by: :prepend

  scope :recent, -> { order(created_at: :desc).limit(50) }

  after_create_commit :touch_room

  private

  def touch_room
    room.touch
  end
end
```

### Views

```erb
<!-- app/views/rooms/show.html.erb -->
<div class="flex flex-col h-screen" data-controller="chat">
  <%= turbo_stream_from @room %>

  <header class="p-4 border-b flex justify-between items-center">
    <h1 class="text-xl font-bold"><%= @room.name %></h1>
    <span id="online_users" class="text-sm text-gray-500">
      <%= render "rooms/online_users", users: @online_users %>
    </span>
  </header>

  <div id="messages"
       class="flex-1 overflow-y-auto p-4 flex flex-col-reverse space-y-reverse space-y-4"
       data-chat-target="messages">
    <%= render @room.messages.recent.includes(:user).reverse %>
  </div>

  <div id="typing_indicator" class="px-4 py-2 text-sm text-gray-500 h-6">
  </div>

  <footer class="p-4 border-t">
    <%= turbo_frame_tag "message_form" do %>
      <%= render "messages/form", room: @room, message: Message.new %>
    <% end %>
  </footer>
</div>
```

## Main Patterns

### Pattern 1: Message Form with Optimistic UI

```erb
<!-- app/views/messages/_form.html.erb -->
<%= form_with model: [@room, message],
              data: {
                controller: "message-form",
                action: "turbo:submit-start->message-form#disable turbo:submit-end->message-form#enable"
              } do |f| %>

  <div class="flex gap-2">
    <%= f.text_field :body,
                     class: "flex-1 rounded-lg border p-2",
                     placeholder: "Type a message...",
                     autocomplete: "off",
                     data: {
                       message_form_target: "input",
                       action: "input->message-form#typing keydown.enter->message-form#submit"
                     } %>

    <%= f.submit "Send",
                 class: "px-4 py-2 bg-blue-500 text-white rounded-lg",
                 data: { message_form_target: "button" } %>
  </div>
<% end %>
```

```javascript
// app/javascript/controllers/message_form_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "button"]

  submit(event) {
    if (!event.shiftKey) {
      event.preventDefault()
      this.element.requestSubmit()
    }
  }

  disable() {
    this.buttonTarget.disabled = true
    this.inputTarget.disabled = true
  }

  enable() {
    this.buttonTarget.disabled = false
    this.inputTarget.disabled = false
    this.inputTarget.value = ""
    this.inputTarget.focus()
  }

  typing() {
    // Handled by typing channel
    if (window.typingChannel) {
      window.typingChannel.startTyping()
    }
  }
}
```

### Pattern 2: Typing Indicators

```ruby
# app/channels/typing_channel.rb
class TypingChannel < ApplicationCable::Channel
  def subscribed
    @room = Room.find(params[:room_id])
    stream_for @room
  end

  def typing(data)
    TypingChannel.broadcast_to(
      @room,
      user_id: current_user.id,
      user_name: current_user.name,
      typing: data["typing"]
    )
  end
end
```

```javascript
// app/javascript/channels/typing_channel.js
import consumer from "./consumer"

let typingTimer = null

export function createTypingChannel(roomId, currentUserId) {
  return consumer.subscriptions.create(
    { channel: "TypingChannel", room_id: roomId },
    {
      received(data) {
        if (data.user_id !== currentUserId) {
          this.updateTypingIndicator(data)
        }
      },

      updateTypingIndicator(data) {
        const indicator = document.getElementById("typing_indicator")
        if (data.typing) {
          indicator.textContent = `${data.user_name} is typing...`
        } else {
          indicator.textContent = ""
        }
      },

      startTyping() {
        this.perform("typing", { typing: true })
        clearTimeout(typingTimer)
        typingTimer = setTimeout(() => {
          this.perform("typing", { typing: false })
        }, 2000)
      }
    }
  )
}
```

### Pattern 3: Message Partial with Sender Detection

```erb
<!-- app/views/messages/_message.html.erb -->
<%
  is_own_message = message.user == current_user
  alignment = is_own_message ? "justify-end" : "justify-start"
  bg_color = is_own_message ? "bg-blue-500 text-white" : "bg-gray-200"
%>

<%= turbo_frame_tag dom_id(message) do %>
  <div id="<%= dom_id(message) %>" class="flex <%= alignment %>">
    <div class="max-w-xs lg:max-w-md">
      <% unless is_own_message %>
        <div class="text-xs text-gray-500 mb-1"><%= message.user.name %></div>
      <% end %>

      <div class="<%= bg_color %> rounded-lg px-4 py-2">
        <%= simple_format(message.body, {}, wrapper_tag: "span") %>
      </div>

      <div class="text-xs text-gray-400 mt-1 flex gap-2">
        <time><%= message.created_at.strftime("%H:%M") %></time>
        <% if is_own_message %>
          <span id="<%= dom_id(message, :status) %>">
            <%= message.read? ? "Read" : "Sent" %>
          </span>
        <% end %>
      </div>
    </div>
  </div>
<% end %>
```

### Pattern 4: Read Receipts

```ruby
# app/models/read_receipt.rb
class ReadReceipt < ApplicationRecord
  belongs_to :message
  belongs_to :user

  after_create_commit :broadcast_read_status

  private

  def broadcast_read_status
    return unless message.user != user # Don't notify sender reading their own

    Turbo::StreamsChannel.broadcast_update_to(
      message.room,
      target: "#{ActionView::RecordIdentifier.dom_id(message)}_status",
      html: "Read"
    )
  end
end

# app/controllers/messages_controller.rb
class MessagesController < ApplicationController
  def mark_read
    @room = Room.find(params[:room_id])
    @room.messages.unread_by(current_user).find_each do |message|
      message.read_receipts.find_or_create_by(user: current_user)
    end

    head :ok
  end
end
```

### Pattern 5: Auto-scroll to New Messages

```javascript
// app/javascript/controllers/chat_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["messages"]

  connect() {
    this.scrollToBottom()
    this.observeNewMessages()
  }

  scrollToBottom() {
    this.messagesTarget.scrollTop = this.messagesTarget.scrollHeight
  }

  observeNewMessages() {
    const observer = new MutationObserver((mutations) => {
      const shouldScroll = this.isNearBottom()

      mutations.forEach((mutation) => {
        if (mutation.addedNodes.length > 0 && shouldScroll) {
          this.scrollToBottom()
        }
      })
    })

    observer.observe(this.messagesTarget, { childList: true })
  }

  isNearBottom() {
    const threshold = 100
    const position = this.messagesTarget.scrollHeight -
                     this.messagesTarget.scrollTop -
                     this.messagesTarget.clientHeight
    return position < threshold
  }
}
```

### Pattern 6: File Attachments with Active Storage

```ruby
# app/models/message.rb
class Message < ApplicationRecord
  belongs_to :room
  belongs_to :user

  has_one_attached :attachment

  broadcasts_to :room, inserts_by: :prepend

  validate :attachment_size

  private

  def attachment_size
    if attachment.attached? && attachment.byte_size > 10.megabytes
      errors.add(:attachment, "is too large (max 10MB)")
    end
  end
end
```

```erb
<!-- app/views/messages/_message.html.erb (with attachment) -->
<div id="<%= dom_id(message) %>" class="message">
  <% if message.attachment.attached? %>
    <div class="attachment">
      <% if message.attachment.image? %>
        <%= image_tag message.attachment, class: "rounded-lg max-w-sm" %>
      <% else %>
        <%= link_to message.attachment.filename,
                    rails_blob_path(message.attachment, disposition: "attachment"),
                    class: "text-blue-500 underline" %>
      <% end %>
    </div>
  <% end %>

  <% if message.body.present? %>
    <p><%= message.body %></p>
  <% end %>
</div>
```

### Pattern 7: Infinite Scroll for History

```ruby
# app/controllers/messages_controller.rb
class MessagesController < ApplicationController
  def index
    @room = Room.find(params[:room_id])
    @messages = @room.messages
                     .where("id < ?", params[:before])
                     .order(created_at: :desc)
                     .limit(20)
                     .includes(:user)

    respond_to do |format|
      format.turbo_stream
      format.html
    end
  end
end
```

```erb
<!-- app/views/messages/index.turbo_stream.erb -->
<%= turbo_stream.prepend "messages" do %>
  <%= render @messages.reverse %>
<% end %>

<% if @messages.size == 20 %>
  <%= turbo_stream.replace "load_more" do %>
    <%= turbo_frame_tag "load_more",
                        src: room_messages_path(@room, before: @messages.last.id),
                        loading: :lazy do %>
      <div class="text-center py-4">Loading...</div>
    <% end %>
  <% end %>
<% end %>
```

### Pattern 8: Direct Messages

```ruby
# app/models/room.rb
class Room < ApplicationRecord
  enum room_type: { group: 0, direct: 1 }

  def self.direct_room_for(user1, user2)
    # Find existing or create new direct room
    existing = joins(:room_users)
      .where(room_type: :direct)
      .where(room_users: { user_id: [user1.id, user2.id] })
      .group("rooms.id")
      .having("COUNT(DISTINCT room_users.user_id) = 2")
      .first

    existing || create_direct_room(user1, user2)
  end

  private_class_method def self.create_direct_room(user1, user2)
    transaction do
      room = create!(room_type: :direct, name: nil)
      room.room_users.create!(user: user1)
      room.room_users.create!(user: user2)
      room
    end
  end

  def display_name(for_user:)
    if direct?
      users.where.not(id: for_user.id).first&.name || "Direct Message"
    else
      name
    end
  end
end
```

## Complete Controller

```ruby
# app/controllers/messages_controller.rb
class MessagesController < ApplicationController
  before_action :authenticate_user!
  before_action :set_room
  before_action :authorize_room_access

  def create
    @message = @room.messages.build(message_params)
    @message.user = current_user

    respond_to do |format|
      if @message.save
        format.turbo_stream do
          render turbo_stream: turbo_stream.replace(
            "message_form",
            partial: "messages/form",
            locals: { room: @room, message: Message.new }
          )
        end
        format.html { redirect_to @room }
      else
        format.turbo_stream do
          render turbo_stream: turbo_stream.replace(
            "message_form",
            partial: "messages/form",
            locals: { room: @room, message: @message }
          ), status: :unprocessable_entity
        end
        format.html { redirect_to @room, alert: @message.errors.full_messages.join(", ") }
      end
    end
  end

  private

  def set_room
    @room = Room.find(params[:room_id])
  end

  def authorize_room_access
    unless @room.member?(current_user)
      redirect_to rooms_path, alert: "Access denied"
    end
  end

  def message_params
    params.require(:message).permit(:body, :attachment)
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Fetching all messages | Memory/performance | Paginate with infinite scroll |
| Synchronous broadcasts | Slow response | Use after_commit callbacks |
| No room membership check | Unauthorized access | Verify in controller and channel |
| Missing typing debounce | Excessive broadcasts | Debounce typing events |
| No message sanitization | XSS vulnerability | Use `simple_format` or sanitize |

## Related Skills

- [../turbo-streams/broadcasting.md](../turbo-streams/broadcasting.md): Broadcasting basics
- [notifications.md](./notifications.md): Notification patterns
- [presence.md](./presence.md): Online status

## References

- [Turbo Streams Handbook](https://turbo.hotwired.dev/handbook/streams)
- [HotWired Chat Example](https://github.com/hotwired/turbo-rails/tree/main/test/dummy)
