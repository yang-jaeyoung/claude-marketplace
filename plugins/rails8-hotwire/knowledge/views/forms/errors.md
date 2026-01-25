---
name: rails8-views-form-errors
description: Error display patterns including inline errors, error summaries, and Turbo integration
---

# Form Errors

## Overview

Displaying validation errors effectively is crucial for user experience. Rails provides model errors through `ActiveModel::Errors`, and with Turbo, errors update without full page reload.

## When to Use

- When displaying validation errors on forms
- When showing inline field errors
- When implementing error summaries
- When handling Turbo error responses

## Quick Start

```erb
<%# Error summary at top %>
<%= render "shared/form_errors", model: @post %>

<%# Form with inline errors %>
<%= form_with model: @post do |f| %>
  <div>
    <%= f.label :title %>
    <%= f.text_field :title %>
    <% if @post.errors[:title].any? %>
      <p class="text-red-600 text-sm"><%= @post.errors[:title].first %></p>
    <% end %>
  </div>
  <%= f.submit %>
<% end %>
```

## Main Patterns

### Pattern 1: Error Summary Partial

```erb
<%# app/views/shared/_form_errors.html.erb %>
<%# locals: (model:) %>
<% if model.errors.any? %>
  <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
    <div class="flex">
      <div class="flex-shrink-0">
        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"/>
        </svg>
      </div>
      <div class="ml-3">
        <h3 class="text-sm font-medium text-red-800">
          <%= pluralize(model.errors.count, "error") %> prohibited this from being saved:
        </h3>
        <ul class="mt-2 text-sm text-red-700 list-disc list-inside">
          <% model.errors.full_messages.each do |message| %>
            <li><%= message %></li>
          <% end %>
        </ul>
      </div>
    </div>
  </div>
<% end %>
```

### Pattern 2: Inline Field Errors

```erb
<%# Inline error after field %>
<div class="mb-4">
  <%= f.label :email, class: "block text-sm font-medium text-gray-700" %>
  <%= f.email_field :email,
      class: "mt-1 block w-full rounded-md border-gray-300 shadow-sm
             #{'border-red-500 focus:border-red-500 focus:ring-red-500' if @user.errors[:email].any?}" %>
  <% if @user.errors[:email].any? %>
    <p class="mt-1 text-sm text-red-600"><%= @user.errors[:email].first %></p>
  <% end %>
</div>

<%# Helper method for cleaner views %>
<%# app/helpers/form_helper.rb %>
module FormHelper
  def field_error(model, field)
    return unless model.errors[field].any?
    content_tag(:p, model.errors[field].first, class: "mt-1 text-sm text-red-600")
  end

  def field_error_class(model, field)
    model.errors[field].any? ? "border-red-500" : "border-gray-300"
  end
end

<%# Usage %>
<div class="mb-4">
  <%= f.label :email %>
  <%= f.email_field :email, class: "input #{field_error_class(@user, :email)}" %>
  <%= field_error(@user, :email) %>
</div>
```

### Pattern 3: Field Wrapper with Error Support

```erb
<%# app/views/shared/_form_field.html.erb %>
<%# locals: (form:, field:, type: :text_field, label: nil, hint: nil, **options) %>
<%
  model = form.object
  has_error = model.errors[field].any?
  label_text = label || field.to_s.humanize
%>

<div class="mb-4">
  <%= form.label field, label_text,
      class: "block text-sm font-medium #{has_error ? 'text-red-700' : 'text-gray-700'}" %>

  <%= form.send(type, field,
      class: "mt-1 block w-full rounded-md shadow-sm
             #{has_error ? 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500' : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'}",
      **options) %>

  <% if hint && !has_error %>
    <p class="mt-1 text-sm text-gray-500"><%= hint %></p>
  <% end %>

  <% if has_error %>
    <p class="mt-1 text-sm text-red-600"><%= model.errors[field].first %></p>
  <% end %>
</div>

<%# Usage %>
<%= render "shared/form_field", form: f, field: :title, hint: "A catchy title" %>
<%= render "shared/form_field", form: f, field: :email, type: :email_field %>
<%= render "shared/form_field", form: f, field: :bio, type: :text_area %>
```

### Pattern 4: Controller Error Handling with Turbo

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  def create
    @post = current_user.posts.build(post_params)

    if @post.save
      respond_to do |format|
        format.turbo_stream { render turbo_stream: turbo_stream.prepend("posts", @post) }
        format.html { redirect_to @post, notice: "Post created!" }
      end
    else
      # CRITICAL: Use 422 status for Turbo to replace form
      render :new, status: :unprocessable_entity
    end
  end

  def update
    @post = Post.find(params[:id])

    if @post.update(post_params)
      redirect_to @post, status: :see_other, notice: "Updated!"
    else
      render :edit, status: :unprocessable_entity
    end
  end
end
```

### Pattern 5: Turbo Stream Error Update

```erb
<%# app/views/posts/create.turbo_stream.erb %>
<%# Only rendered on error (success redirects) %>
<%= turbo_stream.replace "post_form" do %>
  <%= render "form", post: @post %>
<% end %>

<%# With flash message %>
<%= turbo_stream.update "flash" do %>
  <%= render "shared/flash", flash: { alert: "Please fix the errors below." } %>
<% end %>

<%# The form partial needs an ID %>
<%# app/views/posts/_form.html.erb %>
<%= form_with model: post, id: "post_form" do |f| %>
  <%= render "shared/form_errors", model: post %>
  ...
<% end %>
```

### Pattern 6: JavaScript Error Highlighting

```javascript
// app/javascript/controllers/form_validation_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["field", "error"]

  connect() {
    this.element.addEventListener("turbo:submit-end", this.handleSubmitEnd.bind(this))
  }

  handleSubmitEnd(event) {
    if (!event.detail.success) {
      // Scroll to first error
      const firstError = this.element.querySelector(".text-red-600")
      if (firstError) {
        firstError.scrollIntoView({ behavior: "smooth", block: "center" })
      }
    }
  }

  validate(event) {
    const field = event.target
    const errorElement = this.element.querySelector(`[data-error-for="${field.name}"]`)

    if (field.validity.valid) {
      field.classList.remove("border-red-500")
      if (errorElement) errorElement.textContent = ""
    } else {
      field.classList.add("border-red-500")
      if (errorElement) errorElement.textContent = field.validationMessage
    }
  }
}
```

```erb
<%= form_with model: @post, data: { controller: "form-validation" } do |f| %>
  <div>
    <%= f.label :title %>
    <%= f.text_field :title, required: true, data: { action: "blur->form-validation#validate" } %>
    <p data-error-for="post[title]" class="text-sm text-red-600"></p>
  </div>
  <%= f.submit %>
<% end %>
```

### Pattern 7: Error Messages with Icons

```erb
<%# app/views/shared/_field_error.html.erb %>
<%# locals: (messages:) %>
<% if messages.any? %>
  <div class="flex items-start gap-1 mt-1">
    <svg class="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"/>
    </svg>
    <p class="text-sm text-red-600"><%= messages.first %></p>
  </div>
<% end %>

<%# Usage %>
<%= render "shared/field_error", messages: @post.errors[:title] %>
```

### Pattern 8: Base Errors (Model-Level)

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  validate :validate_publication_date

  private

  def validate_publication_date
    if published_at && published_at < created_at
      errors.add(:base, "Publication date cannot be before creation date")
    end
  end
end
```

```erb
<%# Display base errors separately %>
<% if @post.errors[:base].any? %>
  <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
    <ul class="text-sm text-yellow-800">
      <% @post.errors[:base].each do |error| %>
        <li><%= error %></li>
      <% end %>
    </ul>
  </div>
<% end %>
```

### Pattern 9: API-Style Error Response

```ruby
# For JSON/API responses
class Api::PostsController < ApplicationController
  def create
    @post = Post.new(post_params)

    if @post.save
      render json: @post, status: :created
    else
      render json: {
        errors: @post.errors.full_messages,
        details: @post.errors.details
      }, status: :unprocessable_entity
    end
  end
end
```

### Pattern 10: Custom Error Display with ViewComponent

```ruby
# app/components/form_error_component.rb
class FormErrorComponent < ViewComponent::Base
  def initialize(model:, attribute: nil)
    @model = model
    @attribute = attribute
  end

  def errors
    if @attribute
      @model.errors[@attribute]
    else
      @model.errors.full_messages
    end
  end

  def render?
    errors.any?
  end
end
```

```erb
<%# app/components/form_error_component.html.erb %>
<div class="bg-red-50 border-l-4 border-red-500 p-4 my-4">
  <div class="flex">
    <div class="flex-shrink-0">
      <svg class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"/>
      </svg>
    </div>
    <div class="ml-3">
      <% if @attribute %>
        <p class="text-sm text-red-700"><%= errors.first %></p>
      <% else %>
        <ul class="text-sm text-red-700 list-disc list-inside">
          <% errors.each do |error| %>
            <li><%= error %></li>
          <% end %>
        </ul>
      <% end %>
    </div>
  </div>
</div>

<%# Usage %>
<%= render FormErrorComponent.new(model: @post) %>
<%= render FormErrorComponent.new(model: @post, attribute: :title) %>
```

## Error Response Checklist

- [ ] Controller returns `status: :unprocessable_entity` (422) on validation failure
- [ ] Form has an ID for Turbo Stream replacement
- [ ] Error summary shown at top of form
- [ ] Inline errors shown under fields
- [ ] Error fields have visual distinction (red border)
- [ ] Form scrolls to first error on submit

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Missing 422 status | Turbo doesn't update form | Always return `:unprocessable_entity` |
| Only summary, no inline | User hunts for errors | Show errors at field level |
| No visual field indication | Errors hard to spot | Add red border/background |
| Showing all errors | Overwhelming | Show first error per field |
| Not scrolling to errors | Errors not visible | Scroll to first error |

## Related Skills

- [form-builder.md](./form-builder.md): Form setup
- [fields.md](./fields.md): Field types
- [../templates/_form_errors.html.erb](../templates/_form_errors.html.erb): Error template

## References

- [ActiveModel Errors](https://api.rubyonrails.org/classes/ActiveModel/Errors.html)
- [Turbo Drive Forms](https://turbo.hotwired.dev/handbook/drive#form-submissions)
