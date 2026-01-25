# Collaborative Editing

## Overview

Collaborative editing allows multiple users to work on the same content simultaneously with real-time synchronization. This guide covers basic collaborative patterns, conflict handling, and operational transformation concepts.

## When to Use

- When multiple users edit the same document
- When building shared whiteboards
- When implementing collaborative forms
- When creating multiplayer applications

## Quick Start

### Basic Collaborative Document

```ruby
# app/models/document.rb
class Document < ApplicationRecord
  has_many :document_versions, dependent: :destroy
  belongs_to :owner, class_name: "User"

  broadcasts_refreshes_to :document

  def apply_change(user:, content:, version:)
    return false if version < self.version

    transaction do
      document_versions.create!(
        user: user,
        content: self.content,
        version: self.version
      )

      update!(content: content, version: version + 1)
      broadcast_change(user)
    end
  end

  private

  def broadcast_change(user)
    DocumentChannel.broadcast_to(self, {
      type: "content_update",
      content: content,
      version: version,
      user_id: user.id,
      user_name: user.name
    })
  end
end
```

## Main Patterns

### Pattern 1: Document Channel with Locking

```ruby
# app/channels/document_channel.rb
class DocumentChannel < ApplicationCable::Channel
  def subscribed
    @document = Document.find(params[:document_id])
    stream_for @document

    # Notify others of new participant
    broadcast_presence
  end

  def unsubscribed
    release_lock
    broadcast_presence
  end

  def acquire_lock(data)
    section = data["section"]

    if can_lock?(section)
      set_lock(section)
      broadcast_lock_acquired(section)
    else
      transmit(error: "Section is locked", section: section)
    end
  end

  def release_lock
    current_locks.each do |section|
      remove_lock(section)
      broadcast_lock_released(section)
    end
  end

  def update_content(data)
    return unless owns_lock?(data["section"])

    @document.apply_change(
      user: current_user,
      content: data["content"],
      version: data["version"]
    )
  end

  private

  def lock_key
    "document:#{@document.id}:locks"
  end

  def can_lock?(section)
    current_lock = Rails.cache.read("#{lock_key}:#{section}")
    current_lock.nil? || current_lock == current_user.id
  end

  def set_lock(section)
    Rails.cache.write("#{lock_key}:#{section}", current_user.id, expires_in: 5.minutes)
  end

  def remove_lock(section)
    Rails.cache.delete("#{lock_key}:#{section}")
  end

  def owns_lock?(section)
    Rails.cache.read("#{lock_key}:#{section}") == current_user.id
  end

  def current_locks
    # Track which sections this user has locked
    Rails.cache.read("user:#{current_user.id}:locks") || []
  end

  def broadcast_lock_acquired(section)
    DocumentChannel.broadcast_to(@document, {
      type: "lock_acquired",
      section: section,
      user_id: current_user.id,
      user_name: current_user.name
    })
  end

  def broadcast_lock_released(section)
    DocumentChannel.broadcast_to(@document, {
      type: "lock_released",
      section: section
    })
  end
end
```

### Pattern 2: Optimistic Locking with Conflict Detection

```ruby
# app/models/document.rb
class Document < ApplicationRecord
  def update_with_conflict_detection(user:, content:, base_version:)
    transaction do
      reload # Get latest version

      if version == base_version
        # No conflict, apply directly
        update!(content: content, version: version + 1, last_edited_by: user)
        { success: true, version: version }
      else
        # Conflict detected
        { success: false, conflict: true, server_content: self.content, server_version: version }
      end
    end
  end
end

# app/channels/document_channel.rb
class DocumentChannel < ApplicationCable::Channel
  def save(data)
    result = @document.update_with_conflict_detection(
      user: current_user,
      content: data["content"],
      base_version: data["base_version"]
    )

    if result[:success]
      # Broadcast to all
      DocumentChannel.broadcast_to(@document, {
        type: "content_saved",
        content: data["content"],
        version: result[:version],
        user_id: current_user.id
      })
    else
      # Send conflict to this user only
      transmit({
        type: "conflict",
        server_content: result[:server_content],
        server_version: result[:server_version]
      })
    end
  end
end
```

```javascript
// app/javascript/controllers/collaborative_editor_controller.js
import { Controller } from "@hotwired/stimulus"
import consumer from "../channels/consumer"

export default class extends Controller {
  static values = { documentId: Number, userId: Number }
  static targets = ["editor", "conflictModal"]

  connect() {
    this.baseVersion = parseInt(this.element.dataset.version)
    this.subscribeToDocument()
  }

  subscribeToDocument() {
    this.channel = consumer.subscriptions.create(
      { channel: "DocumentChannel", document_id: this.documentIdValue },
      {
        received: (data) => this.handleReceived(data)
      }
    )
  }

  handleReceived(data) {
    switch (data.type) {
      case "content_saved":
        if (data.user_id !== this.userIdValue) {
          this.applyRemoteChange(data)
        }
        break
      case "conflict":
        this.showConflictResolution(data)
        break
    }
  }

  save() {
    this.channel.perform("save", {
      content: this.editorTarget.value,
      base_version: this.baseVersion
    })
  }

  applyRemoteChange(data) {
    // Simple: replace content (loses local changes)
    // Better: implement operational transformation
    this.editorTarget.value = data.content
    this.baseVersion = data.version
  }

  showConflictResolution(data) {
    // Show modal with both versions
    this.conflictModalTarget.classList.remove("hidden")
    document.getElementById("server_content").value = data.server_content
    document.getElementById("local_content").value = this.editorTarget.value
    this.serverVersion = data.server_version
  }

  resolveWithServer() {
    this.editorTarget.value = document.getElementById("server_content").value
    this.baseVersion = this.serverVersion
    this.conflictModalTarget.classList.add("hidden")
  }

  resolveWithLocal() {
    // User chooses to overwrite server version
    this.baseVersion = this.serverVersion
    this.save()
    this.conflictModalTarget.classList.add("hidden")
  }
}
```

### Pattern 3: Real-time Cursor Positions

```ruby
# app/channels/cursor_sync_channel.rb
class CursorSyncChannel < ApplicationCable::Channel
  def subscribed
    @document = Document.find(params[:document_id])
    stream_for @document
  end

  def cursor_moved(data)
    CursorSyncChannel.broadcast_to(@document, {
      type: "cursor",
      user_id: current_user.id,
      user_name: current_user.name,
      color: user_color,
      position: data["position"],
      selection: data["selection"]
    })
  end

  private

  def user_color
    colors = %w[#FF6B6B #4ECDC4 #45B7D1 #96CEB4 #FFEAA7 #DDA0DD #98D8C8 #F7DC6F]
    colors[current_user.id % colors.length]
  end
end
```

### Pattern 4: Shared Whiteboard

```ruby
# app/channels/whiteboard_channel.rb
class WhiteboardChannel < ApplicationCable::Channel
  def subscribed
    @whiteboard = Whiteboard.find(params[:whiteboard_id])
    stream_for @whiteboard

    # Send existing content
    transmit({
      type: "init",
      objects: @whiteboard.objects
    })
  end

  def add_object(data)
    object = @whiteboard.whiteboard_objects.create!(
      object_type: data["type"],
      properties: data["properties"],
      created_by: current_user
    )

    WhiteboardChannel.broadcast_to(@whiteboard, {
      type: "object_added",
      id: object.id,
      object_type: object.object_type,
      properties: object.properties,
      user_id: current_user.id
    })
  end

  def move_object(data)
    object = @whiteboard.whiteboard_objects.find(data["id"])
    object.update!(properties: object.properties.merge(data["properties"]))

    WhiteboardChannel.broadcast_to(@whiteboard, {
      type: "object_moved",
      id: object.id,
      properties: data["properties"],
      user_id: current_user.id
    })
  end

  def delete_object(data)
    object = @whiteboard.whiteboard_objects.find(data["id"])
    object.destroy!

    WhiteboardChannel.broadcast_to(@whiteboard, {
      type: "object_deleted",
      id: data["id"],
      user_id: current_user.id
    })
  end
end
```

### Pattern 5: Collaborative Form

```ruby
# app/channels/form_channel.rb
class FormChannel < ApplicationCable::Channel
  def subscribed
    @form_session = FormSession.find(params[:session_id])
    stream_for @form_session

    broadcast_active_users
  end

  def focus_field(data)
    set_field_focus(data["field"])

    FormChannel.broadcast_to(@form_session, {
      type: "field_focused",
      field: data["field"],
      user_id: current_user.id,
      user_name: current_user.name
    })
  end

  def update_field(data)
    @form_session.update_field(data["field"], data["value"])

    FormChannel.broadcast_to(@form_session, {
      type: "field_updated",
      field: data["field"],
      value: data["value"],
      user_id: current_user.id
    })
  end

  def blur_field(data)
    clear_field_focus(data["field"])

    FormChannel.broadcast_to(@form_session, {
      type: "field_blurred",
      field: data["field"],
      user_id: current_user.id
    })
  end

  private

  def set_field_focus(field)
    Rails.cache.write(
      "form:#{@form_session.id}:field:#{field}:editor",
      current_user.id,
      expires_in: 30.seconds
    )
  end

  def clear_field_focus(field)
    Rails.cache.delete("form:#{@form_session.id}:field:#{field}:editor")
  end
end
```

### Pattern 6: Simple Operational Transform

```ruby
# app/services/text_transform.rb
class TextTransform
  # Transform operation against another operation
  def self.transform(op1, op2)
    return op1 if op2.nil?

    case [op1[:type], op2[:type]]
    when [:insert, :insert]
      transform_insert_insert(op1, op2)
    when [:insert, :delete]
      transform_insert_delete(op1, op2)
    when [:delete, :insert]
      transform_delete_insert(op1, op2)
    when [:delete, :delete]
      transform_delete_delete(op1, op2)
    else
      op1
    end
  end

  def self.transform_insert_insert(op1, op2)
    if op1[:position] <= op2[:position]
      op1
    else
      op1.merge(position: op1[:position] + op2[:text].length)
    end
  end

  def self.transform_insert_delete(op1, op2)
    if op1[:position] <= op2[:position]
      op1
    elsif op1[:position] > op2[:position] + op2[:length]
      op1.merge(position: op1[:position] - op2[:length])
    else
      op1.merge(position: op2[:position])
    end
  end

  # ... other transform methods
end

# app/services/document_operations.rb
class DocumentOperations
  def initialize(document)
    @document = document
  end

  def apply_operation(operation, base_version)
    # Get all operations since base_version
    pending_ops = @document.operations.where("version > ?", base_version).order(:version)

    # Transform operation against all pending operations
    transformed_op = operation
    pending_ops.each do |pending|
      transformed_op = TextTransform.transform(transformed_op, pending.data)
    end

    # Apply transformed operation
    new_content = apply_to_content(@document.content, transformed_op)

    @document.transaction do
      @document.operations.create!(
        data: transformed_op,
        version: @document.version + 1,
        user: Current.user
      )
      @document.update!(content: new_content, version: @document.version + 1)
    end

    transformed_op
  end

  private

  def apply_to_content(content, operation)
    case operation[:type]
    when :insert
      content.insert(operation[:position], operation[:text])
    when :delete
      content.slice!(operation[:position], operation[:length])
    end
    content
  end
end
```

### Pattern 7: Presence with Edit Indicators

```erb
<!-- app/views/documents/_editor.html.erb -->
<div data-controller="collaborative-editor"
     data-collaborative-editor-document-id-value="<%= @document.id %>"
     data-version="<%= @document.version %>">

  <!-- Active editors indicator -->
  <div id="active_editors" class="flex -space-x-2 mb-4">
    <!-- Populated via broadcast -->
  </div>

  <!-- Editor with field highlights -->
  <div class="relative">
    <textarea data-collaborative-editor-target="editor"
              class="w-full h-96 p-4 font-mono">
      <%= @document.content %>
    </textarea>

    <!-- Remote cursor overlay -->
    <div data-collaborative-editor-target="cursors"
         class="absolute inset-0 pointer-events-none">
    </div>
  </div>

  <!-- Version info -->
  <div class="text-xs text-gray-500 mt-2">
    Version <%= @document.version %> |
    Last edited by <%= @document.last_edited_by&.name || "Unknown" %>
  </div>

  <!-- Conflict resolution modal -->
  <div data-collaborative-editor-target="conflictModal"
       class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
    <!-- Modal content -->
  </div>
</div>
```

## Conflict Resolution Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| Last Write Wins | Latest change overwrites | Low-conflict scenarios |
| Pessimistic Locking | Lock before edit | Documents/forms |
| Optimistic Locking | Detect on save | Most collaborative apps |
| Operational Transform | Transform operations | Real-time text editing |
| CRDT | Conflict-free data types | Complex distributed systems |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No version tracking | Lost updates | Implement versioning |
| Full document sync | Bandwidth waste | Send deltas/operations |
| No conflict handling | Data corruption | Implement OT or CRDT |
| Tight coupling to UI | Hard to test | Separate sync logic |
| No undo support | Poor UX | Store operation history |

## Related Skills

- [presence.md](./presence.md): Online status tracking
- [../action-cable/channels.md](../action-cable/channels.md): Channel patterns
- [chat.md](./chat.md): Real-time messaging

## References

- [Operational Transformation](https://en.wikipedia.org/wiki/Operational_transformation)
- [CRDTs](https://crdt.tech/)
- [Y.js](https://docs.yjs.dev/) - CRDT implementation
- [Automerge](https://automerge.org/) - CRDT library
