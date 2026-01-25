# Comment Views

ERB templates and partials for rendering threaded comments.

## Post Show Page

```erb
<!-- app/views/posts/show.html.erb -->
<article class="max-w-4xl mx-auto p-6">
  <h1 class="text-3xl font-bold mb-4"><%= @post.title %></h1>
  <div class="prose max-w-none mb-8">
    <%= @post.body %>
  </div>

  <!-- Comments Section -->
  <section id="comments" class="mt-12">
    <%= turbo_stream_from @post %>

    <h2 class="text-2xl font-bold mb-6">
      Comments
      <span class="text-gray-500 text-lg">(<%= @post.comments.count %>)</span>
    </h2>

    <!-- New Comment Form -->
    <div id="comment_form" class="mb-8">
      <%= render "comments/form", post: @post, comment: Comment.new, parent: nil %>
    </div>

    <!-- Comments List -->
    <div id="comments_list">
      <%= render @post.comments.top_level.includes(:user, :reactions).recent %>
    </div>
  </section>
</article>
```

## Comment Partial

```erb
<!-- app/views/comments/_comment.html.erb -->
<%= turbo_frame_tag dom_id(comment) do %>
  <div class="comment mb-4 <%= 'ml-12' if comment.depth > 0 %>"
       style="margin-left: <%= comment.depth * 3 %>rem"
       data-controller="comment">

    <div class="border-l-2 border-gray-200 pl-4">
      <!-- Comment Header -->
      <div class="flex items-center gap-2 mb-2">
        <%= image_tag comment.user.avatar_url, class: "w-8 h-8 rounded-full" %>
        <strong class="font-semibold"><%= comment.user.name %></strong>
        <span class="text-gray-500 text-sm">
          <%= time_ago_in_words(comment.created_at) %> ago
        </span>

        <% if policy(comment).update? %>
          <%= link_to "Edit",
              edit_post_comment_path(comment.post, comment),
              class: "text-blue-600 text-sm ml-auto",
              data: { turbo_frame: dom_id(comment, :edit) } %>
        <% end %>

        <% if policy(comment).destroy? %>
          <%= button_to "Delete",
              post_comment_path(comment.post, comment),
              method: :delete,
              class: "text-red-600 text-sm",
              data: { turbo_confirm: "Delete this comment?" } %>
        <% end %>
      </div>

      <!-- Comment Body -->
      <div class="prose prose-sm max-w-none mb-3">
        <%= simple_format comment.body %>
      </div>

      <!-- Reactions -->
      <div id="<%= dom_id(comment, :reactions) %>" class="mb-2">
        <%= render "comments/reactions", comment: comment %>
      </div>

      <!-- Reply Button -->
      <% unless comment.max_depth_reached? %>
        <button data-action="click->comment#toggleReply"
                class="text-blue-600 text-sm font-medium">
          Reply
        </button>
      <% end %>

      <!-- Reply Form (hidden by default) -->
      <div id="<%= dom_id(comment, :reply_form) %>"
           class="hidden mt-4"
           data-comment-target="replyForm">
        <%= render "comments/form",
            post: comment.post,
            comment: Comment.new,
            parent: comment %>
      </div>
    </div>

    <!-- Edit Form Slot -->
    <%= turbo_frame_tag dom_id(comment, :edit) %>

    <!-- Nested Replies -->
    <% if comment.children.any? %>
      <div class="replies mt-4">
        <%= render comment.children.includes(:user, :reactions).recent %>
      </div>
    <% end %>
  </div>
<% end %>
```

## Comment Form

```erb
<!-- app/views/comments/_form.html.erb -->
<%= turbo_frame_tag (parent ? dom_id(parent, :reply_form) : "comment_form") do %>
  <%= form_with model: [post, comment],
                url: post_comments_path(post, parent_id: parent&.id),
                data: { controller: "mentions",
                       action: "turbo:submit-end->mentions#reset" } do |f| %>

    <%= render "shared/form_errors", model: comment %>

    <div class="mb-3">
      <%= f.text_area :body,
          rows: 3,
          placeholder: parent ? "Write a reply..." : "Add a comment...",
          class: "w-full border rounded-lg p-3",
          data: { mentions_target: "input" } %>
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

## Reactions Partial

```erb
<!-- app/views/comments/_reactions.html.erb -->
<div class="flex gap-2 items-center">
  <% Comment::EMOJIS.each do |emoji| %>
    <% count = comment.send("#{emoji_column_name(emoji)}_count") %>
    <% user_reacted = comment.reactions.exists?(user: current_user, emoji: emoji) %>

    <%= button_to comment_reactions_path(comment, emoji: emoji),
        method: :post,
        class: "px-2 py-1 rounded #{user_reacted ? 'bg-blue-100' : 'bg-gray-100'} hover:bg-blue-50 text-sm" do %>
      <%= emoji %>
      <% if count > 0 %>
        <span class="ml-1"><%= count %></span>
      <% end %>
    <% end %>
  <% end %>

  <button class="text-gray-400 hover:text-gray-600 text-sm"
          data-action="click->comment#showEmojiPicker">
    Add reaction
  </button>
</div>
```

## Helper Methods

```ruby
# app/helpers/comments_helper.rb
module CommentsHelper
  def emoji_column_name(emoji)
    case emoji
    when "👍" then "thumbs_up"
    when "❤️" then "heart"
    when "😂" then "laugh"
    when "🎉" then "celebration"
    when "😕" then "confused"
    when "🚀" then "rocket"
    end
  end
end

# app/models/comment.rb
class Comment < ApplicationRecord
  EMOJIS = %w[👍 ❤️ 😂 🎉 😕 🚀]
  # ...
end
```

## Key Features

### Threaded Display

- Depth-based indentation: `margin-left: <%= comment.depth * 3 %>rem`
- Visual nesting with left border
- Recursive rendering via `render comment.children`

### Turbo Frames

Each comment wrapped in a `turbo_frame_tag`:
- Enables targeted updates
- Edit form opens inline
- Delete removes frame smoothly

### Progressive Enhancement

- Works without JavaScript (form submits normally)
- Reply button toggles form via Stimulus
- Reactions use `button_to` for POST requests

### Conditional Rendering

- Edit/Delete buttons only for authorized users
- Reply button hidden at max depth
- Reaction counts hidden when zero

### Form Context

Form adapts based on context:
- Top-level: targets `#comment_form`
- Reply: targets `#reply_form_{parent_id}`
- Placeholder text changes
- Cancel button only for replies

## Related

- [Back to Index](SKILL.md)
- [Previous: Controllers](controller.md)
- [Next: Real-time](realtime.md)
