---
name: rails8-recipes
description: Comments, notifications, search, file upload, subscription payments, multi-tenant, and more practical combination recipes. Use when implementing complete features or integrating external services.
triggers:
  - recipe
  - example
  - full-stack
  - complete feature
  - comment system
  - search
  - file upload
  - 레시피
  - 예제
  - 풀스택
  - 완전한 기능
  - 댓글 시스템
  - 검색
  - 파일 업로드
summary: |
  개별 스킬을 조합한 실전 레시피를 다룹니다. 댓글 시스템, 알림, 검색, 파일 업로드,
  구독 결제, 멀티테넌트 등 완전한 기능 구현 패턴을 포함합니다. 실제 프로덕션
  패턴이 필요할 때 참조하세요.
token_cost: medium
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - features/*.md
  deep:
    - "**/*.md"
---

# Recipes: Practical Combination Patterns

## Overview

Practical recipes that combine individual skills to implement complete features. Includes SaaS features, general features, external service integrations, and full-stack app examples.

## When to Use

- When complete feature implementation is needed
- When combining multiple skills
- When real production patterns are needed
- When integrating external services

## File Structure

```
recipes/
├── SKILL.md
├── saas/
│   ├── multi-tenant.md       # Multi-tenant SaaS
│   ├── subscription.md       # Subscription payments
│   └── onboarding.md         # Onboarding flow
├── features/
│   ├── comments.md           # Comment system
│   ├── notifications.md      # Notification system
│   ├── search.md             # Search feature
│   ├── file-upload.md        # File upload
│   ├── export-import.md      # Export/Import
│   └── dashboard.md          # Dashboard
├── integrations/
│   ├── lemon-squeezy.md      # Payments
│   ├── resend.md             # Email
│   ├── cloudflare.md         # CDN + R2
│   └── supabase.md           # DB + Auth
└── full-stack/
    ├── blog.md               # Blog
    ├── todo.md               # Todo app
    └── crm.md                # CRM
```

## Quick Reference

| Feature | Required Skills | Recipe |
|---------|-----------------|--------|
| Comment system | hotwire, models, realtime | features/comments.md |
| Notification system | realtime, background | features/notifications.md |
| Search feature | models, hotwire | features/search.md |
| File upload | models, deploy | features/file-upload.md |
| Subscription payments | auth, external API | integrations/lemon-squeezy.md |

## Recipe Example: Real-time Comment System

### Required Skills
- hotwire (Turbo Streams)
- models (Comment model)
- realtime (broadcasting)

### 1. Model Setup

```ruby
# app/models/comment.rb
class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user

  validates :body, presence: true

  # Real-time broadcast
  broadcasts_to :post

  scope :recent, -> { order(created_at: :desc) }
end
```

### 2. Controller

```ruby
# app/controllers/comments_controller.rb
class CommentsController < ApplicationController
  before_action :authenticate_user!
  before_action :set_post

  def create
    @comment = @post.comments.build(comment_params)
    @comment.user = current_user

    respond_to do |format|
      if @comment.save
        format.turbo_stream
        format.html { redirect_to @post, status: :see_other }
      else
        format.turbo_stream do
          render turbo_stream: turbo_stream.replace(
            "comment_form",
            partial: "comments/form",
            locals: { post: @post, comment: @comment }
          )
        end
        format.html { redirect_to @post, alert: "Failed to create comment" }
      end
    end
  end

  def destroy
    @comment = @post.comments.find(params[:id])
    authorize @comment

    @comment.destroy

    respond_to do |format|
      format.turbo_stream
      format.html { redirect_to @post, status: :see_other }
    end
  end

  private

  def set_post
    @post = Post.find(params[:post_id])
  end

  def comment_params
    params.require(:comment).permit(:body)
  end
end
```

### 3. Views

```erb
<!-- app/views/posts/show.html.erb -->
<article>
  <h1><%= @post.title %></h1>
  <p><%= @post.body %></p>
</article>

<section id="comments">
  <!-- Real-time subscription -->
  <%= turbo_stream_from @post %>

  <h2>Comments (<span id="comment_count"><%= @post.comments.count %></span>)</h2>

  <div id="comments_list">
    <%= render @post.comments.recent.includes(:user) %>
  </div>

  <div id="comment_form">
    <%= render "comments/form", post: @post, comment: Comment.new %>
  </div>
</section>
```

```erb
<!-- app/views/comments/_comment.html.erb -->
<%= turbo_frame_tag dom_id(comment) do %>
  <div class="comment p-4 border-b">
    <div class="flex items-center gap-2 mb-2">
      <strong><%= comment.user.name %></strong>
      <span class="text-gray-500 text-sm">
        <%= time_ago_in_words(comment.created_at) %> ago
      </span>
    </div>
    <p><%= comment.body %></p>

    <% if policy(comment).destroy? %>
      <%= button_to "Delete",
          post_comment_path(comment.post, comment),
          method: :delete,
          class: "text-red-500 text-sm",
          data: { turbo_confirm: "Are you sure you want to delete this?" } %>
    <% end %>
  </div>
<% end %>
```

```erb
<!-- app/views/comments/_form.html.erb -->
<%= turbo_frame_tag "comment_form" do %>
  <%= form_with model: [post, comment],
                data: { controller: "reset-form",
                       action: "turbo:submit-end->reset-form#reset" } do |f| %>

    <%= render "shared/form_errors", model: comment %>

    <div class="mb-4">
      <%= f.text_area :body,
          rows: 3,
          placeholder: "Enter your comment...",
          class: "w-full border rounded p-2" %>
    </div>

    <%= f.submit "Post Comment", class: "btn btn-primary" %>
  <% end %>
<% end %>
```

### 4. Turbo Stream Templates

```erb
<!-- app/views/comments/create.turbo_stream.erb -->
<%= turbo_stream.prepend "comments_list", @comment %>
<%= turbo_stream.update "comment_count", @post.comments.count %>
<%= turbo_stream.update "comment_form" do %>
  <%= render "comments/form", post: @post, comment: Comment.new %>
<% end %>

<!-- app/views/comments/destroy.turbo_stream.erb -->
<%= turbo_stream.remove @comment %>
<%= turbo_stream.update "comment_count", @post.comments.count %>
```

### 5. Form Reset Controller

```javascript
// app/javascript/controllers/reset_form_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  reset() {
    this.element.reset()
  }
}
```

## Recipe Combination Guide

| Project Type | Recommended Recipe Combination |
|--------------|-------------------------------|
| Blog | blog + comments + search |
| SaaS MVP | multi-tenant + subscription + onboarding |
| Community | comments + notifications + file-upload |
| Dashboard | dashboard + export-import + search |
| E-commerce | lemon-squeezy + notifications + search |

## Related Skills

- [core](../core/SKILL.md): Basic patterns
- [hotwire](../hotwire/SKILL.md): Turbo/Stimulus
- [realtime](../realtime/): Real-time features (Phase 2)
- [deploy](../deploy/): Deployment (Phase 2)
