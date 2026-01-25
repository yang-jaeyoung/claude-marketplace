# Real-time Comment Features

Stimulus controllers and Turbo Stream templates for interactive comment features.

## Stimulus Controllers

### Comment Controller

```javascript
// app/javascript/controllers/comment_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["replyForm"]

  toggleReply(event) {
    event.preventDefault()
    this.replyFormTarget.classList.toggle("hidden")

    if (!this.replyFormTarget.classList.contains("hidden")) {
      const textarea = this.replyFormTarget.querySelector("textarea")
      textarea?.focus()
    }
  }
}
```

### Mentions Controller

```javascript
// app/javascript/controllers/mentions_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input"]

  connect() {
    this.setupMentions()
  }

  setupMentions() {
    // Simple @mention detection
    this.inputTarget.addEventListener("input", (e) => {
      const value = e.target.value
      const atPosition = value.lastIndexOf("@")

      if (atPosition !== -1) {
        const query = value.slice(atPosition + 1)

        if (query.length > 0) {
          this.searchUsers(query)
        }
      }
    })
  }

  searchUsers(query) {
    fetch(`/api/users/search?q=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(users => this.showUserSuggestions(users))
  }

  showUserSuggestions(users) {
    // Show dropdown with user suggestions
    // Implementation depends on your UI library
    console.log("User suggestions:", users)
  }

  reset() {
    this.inputTarget.value = ""
  }
}
```

## Turbo Stream Templates

### Create Comment

```erb
<!-- app/views/comments/create.turbo_stream.erb -->
<% if @comment.parent %>
  <%# Insert reply into parent's replies section %>
  <%= turbo_stream.append dom_id(@comment.parent, :replies), @comment %>
  <%= turbo_stream.update dom_id(@comment.parent, :reply_form) do %>
    <%= render "comments/form", post: @post, comment: Comment.new, parent: @comment.parent %>
  <% end %>
<% else %>
  <%# Insert top-level comment %>
  <%= turbo_stream.prepend "comments_list", @comment %>
  <%= turbo_stream.update "comment_form" do %>
    <%= render "comments/form", post: @post, comment: Comment.new, parent: nil %>
  <% end %>
<% end %>

<!-- Update comment count -->
<%= turbo_stream.update dom_id(@post, :comment_count) do %>
  <%= @post.comments.count %>
<% end %>
```

### Update Comment

```erb
<!-- app/views/comments/update.turbo_stream.erb -->
<%= turbo_stream.replace @comment %>
```

### Destroy Comment

```erb
<!-- app/views/comments/destroy.turbo_stream.erb -->
<%= turbo_stream.remove @comment %>
<%= turbo_stream.update dom_id(@post, :comment_count) do %>
  <%= @post.comments.count %>
<% end %>
```

## Broadcasting Configuration

### Model Setup

```ruby
# app/models/comment.rb
class Comment < ApplicationRecord
  # Broadcasts changes to post channel
  broadcasts_to :post

  # This generates these automatic broadcasts:
  # - after_create: append to stream
  # - after_update: replace in stream
  # - after_destroy: remove from stream
end
```

### View Setup

```erb
<!-- app/views/posts/show.html.erb -->
<section id="comments">
  <%# Subscribe to post's Turbo Stream channel %>
  <%= turbo_stream_from @post %>

  <!-- Comments will update automatically -->
</section>
```

## Advanced Mentions

### User Search API

```ruby
# app/controllers/api/users_controller.rb
module Api
  class UsersController < ApplicationController
    def search
      users = User.where("name ILIKE ?", "%#{params[:q]}%")
                  .limit(10)
                  .select(:id, :name, :avatar_url)

      render json: users
    end
  end
end

# config/routes.rb
namespace :api do
  resources :users, only: [] do
    collection do
      get :search
    end
  end
end
```

### Enhanced Mentions Controller

```javascript
// app/javascript/controllers/mentions_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "suggestions"]
  static values = {
    url: { type: String, default: "/api/users/search" }
  }

  connect() {
    this.mentioning = false
    this.mentionStart = 0
  }

  handleInput(event) {
    const { value, selectionStart } = event.target

    // Find @ before cursor
    const textBeforeCursor = value.substring(0, selectionStart)
    const match = textBeforeCursor.match(/@(\w*)$/)

    if (match) {
      this.mentioning = true
      this.mentionStart = selectionStart - match[1].length - 1
      this.searchUsers(match[1])
    } else {
      this.mentioning = false
      this.hideSuggestions()
    }
  }

  async searchUsers(query) {
    if (query.length < 1) {
      this.hideSuggestions()
      return
    }

    const response = await fetch(`${this.urlValue}?q=${encodeURIComponent(query)}`)
    const users = await response.json()

    this.showSuggestions(users)
  }

  showSuggestions(users) {
    if (!this.hasSuggestionsTarget) return

    // Clear existing suggestions
    this.suggestionsTarget.textContent = ''

    // Create suggestion elements safely
    users.forEach(user => {
      const div = document.createElement('div')
      div.className = 'suggestion'
      div.dataset.action = 'click->mentions#selectUser'
      div.dataset.userId = user.id

      const img = document.createElement('img')
      img.src = user.avatar_url
      img.className = 'avatar'

      const span = document.createElement('span')
      span.textContent = user.name

      div.appendChild(img)
      div.appendChild(span)
      this.suggestionsTarget.appendChild(div)
    })

    this.suggestionsTarget.classList.remove('hidden')
  }

  hideSuggestions() {
    if (this.hasSuggestionsTarget) {
      this.suggestionsTarget.classList.add('hidden')
    }
  }

  selectUser(event) {
    const userId = event.currentTarget.dataset.userId
    const userName = event.currentTarget.querySelector('span').textContent

    // Replace @query with @username
    const textarea = this.inputTarget
    const before = textarea.value.substring(0, this.mentionStart)
    const after = textarea.value.substring(textarea.selectionStart)

    textarea.value = `${before}@${userName} ${after}`
    textarea.selectionStart = textarea.selectionEnd = before.length + userName.length + 2

    // Store mentioned user ID in hidden field
    this.addMentionedUserId(userId)

    this.hideSuggestions()
    this.mentioning = false
  }

  addMentionedUserId(userId) {
    const form = this.element.closest('form')
    const input = document.createElement('input')
    input.type = 'hidden'
    input.name = 'comment[mentioned_user_ids][]'
    input.value = userId
    form.appendChild(input)
  }

  reset() {
    this.inputTarget.value = ""
    this.hideSuggestions()
  }
}
```

### Mentions View

```erb
<!-- app/views/comments/_form.html.erb -->
<%= turbo_frame_tag (parent ? dom_id(parent, :reply_form) : "comment_form") do %>
  <%= form_with model: [post, comment],
                url: post_comments_path(post, parent_id: parent&.id),
                data: { controller: "mentions",
                       action: "turbo:submit-end->mentions#reset" } do |f| %>

    <div class="mb-3 relative">
      <%= f.text_area :body,
          rows: 3,
          placeholder: parent ? "Write a reply..." : "Add a comment...",
          class: "w-full border rounded-lg p-3",
          data: {
            mentions_target: "input",
            action: "input->mentions#handleInput"
          } %>

      <!-- Mention suggestions dropdown -->
      <div data-mentions-target="suggestions"
           class="hidden absolute bg-white border shadow-lg rounded-lg mt-1 max-h-60 overflow-y-auto z-10">
      </div>

      <p class="text-xs text-gray-500 mt-1">
        Type @ to mention someone
      </p>
    </div>

    <div class="flex gap-2">
      <%= f.submit parent ? "Reply" : "Comment", class: "btn btn-primary" %>
      <% if parent %>
        <button type="button"
                data-action="click->comment#toggleReply"
                class="btn btn-secondary">
          Cancel
        </button>
      <% end %>
    </div>
  <% end %>
<% end %>
```

## Key Features

### Turbo Stream Targeting

Create template targets different elements based on context:
- **Reply**: Appends to parent's replies section
- **Top-level**: Prepends to main comments list
- **Both**: Update form and comment count

### Automatic Broadcasting

`broadcasts_to :post` generates automatic real-time updates:
- All users viewing the post see new comments
- No manual ActionCable setup needed
- Works with Turbo Stream's built-in subscription

### Progressive Enhancement

Features work without JavaScript:
- Reply form submits normally
- Mentions can be typed manually
- Reactions use POST requests

### Stimulus Actions

- `click->comment#toggleReply`: Show/hide reply form
- `input->mentions#handleInput`: Detect @ mentions
- `turbo:submit-end->mentions#reset`: Clear form after submit

### XSS Protection

The enhanced mentions controller uses safe DOM methods:
- `document.createElement()` for elements
- `textContent` for user-generated content
- Prevents XSS attacks from malicious usernames

## Related

- [Back to Index](SKILL.md)
- [Previous: Views](views.md)
