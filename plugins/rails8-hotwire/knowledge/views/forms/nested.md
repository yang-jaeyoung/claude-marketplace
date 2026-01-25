---
name: rails8-views-form-nested
description: accepts_nested_attributes_for, fields_for, and dynamic nested forms with Stimulus
---

# Nested Forms

## Overview

Nested forms allow creating/editing associated records within a single form. Rails uses `accepts_nested_attributes_for` in models and `fields_for` in views. Combined with Stimulus, you can dynamically add/remove nested items.

## When to Use

- When creating parent and children together (Order + LineItems)
- When editing has_many associations inline
- When building multi-step forms with related data
- When implementing dynamic form sections

## Quick Start

```ruby
# Model
class Post < ApplicationRecord
  has_many :images, dependent: :destroy
  accepts_nested_attributes_for :images, allow_destroy: true, reject_if: :all_blank
end
```

```erb
<%# View %>
<%= form_with model: @post do |f| %>
  <%= f.text_field :title %>

  <%= f.fields_for :images do |image_form| %>
    <%= render "image_fields", f: image_form %>
  <% end %>

  <%= f.submit %>
<% end %>
```

## Main Patterns

### Pattern 1: Model Setup

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  has_many :comments, dependent: :destroy
  has_many :images, dependent: :destroy
  has_one :metadata, dependent: :destroy

  # Basic nested attributes
  accepts_nested_attributes_for :comments

  # With destroy capability
  accepts_nested_attributes_for :images, allow_destroy: true

  # Reject blank entries
  accepts_nested_attributes_for :metadata,
    reject_if: :all_blank

  # Custom rejection
  accepts_nested_attributes_for :comments,
    allow_destroy: true,
    reject_if: proc { |attrs| attrs['body'].blank? }

  # Limit number of nested records
  accepts_nested_attributes_for :images,
    allow_destroy: true,
    limit: 10
end

# Controller - permit nested params
def post_params
  params.require(:post).permit(
    :title,
    :body,
    images_attributes: [:id, :file, :caption, :_destroy],
    comments_attributes: [:id, :body, :_destroy],
    metadata_attributes: [:id, :keywords, :description]
  )
end
```

### Pattern 2: Basic fields_for

```erb
<%# For has_one %>
<%= form_with model: @post do |f| %>
  <%= f.text_field :title %>

  <%= f.fields_for :metadata do |metadata_form| %>
    <%= metadata_form.text_field :keywords %>
    <%= metadata_form.text_area :description %>
  <% end %>

  <%= f.submit %>
<% end %>

<%# For has_many (iterates automatically) %>
<%= form_with model: @post do |f| %>
  <%= f.text_field :title %>

  <%= f.fields_for :images do |image_form| %>
    <div class="nested-fields">
      <%= image_form.file_field :file %>
      <%= image_form.text_field :caption %>
    </div>
  <% end %>

  <%= f.submit %>
<% end %>
```

### Pattern 3: Dynamic Add/Remove with Stimulus

```erb
<%# app/views/posts/_form.html.erb %>
<%= form_with model: @post, data: { controller: "nested-form" } do |f| %>
  <%= f.text_field :title %>

  <div data-nested-form-target="container">
    <%= f.fields_for :images do |image_form| %>
      <%= render "image_fields", f: image_form %>
    <% end %>
  </div>

  <%# Template for new items %>
  <template data-nested-form-target="template">
    <%= f.fields_for :images, Image.new, child_index: "NEW_RECORD" do |image_form| %>
      <%= render "image_fields", f: image_form %>
    <% end %>
  </template>

  <button type="button" data-action="nested-form#add" class="btn btn-secondary">
    Add Image
  </button>

  <%= f.submit %>
<% end %>

<%# app/views/posts/_image_fields.html.erb %>
<div class="nested-fields flex items-center gap-4 p-4 border rounded mb-2"
     data-nested-form-target="fields">
  <%= f.file_field :file, class: "flex-1" %>
  <%= f.text_field :caption, placeholder: "Caption", class: "flex-1" %>

  <%# Destroy checkbox (hidden, toggled by remove button) %>
  <%= f.hidden_field :_destroy, data: { nested_form_target: "destroy" } %>

  <button type="button"
          data-action="nested-form#remove"
          class="text-red-600 hover:text-red-800">
    Remove
  </button>
</div>
```

```javascript
// app/javascript/controllers/nested_form_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["container", "template", "fields", "destroy"]

  add(event) {
    event.preventDefault()

    const content = this.templateTarget.innerHTML
    const newIndex = new Date().getTime()
    const newContent = content.replace(/NEW_RECORD/g, newIndex)

    this.containerTarget.insertAdjacentHTML("beforeend", newContent)
  }

  remove(event) {
    event.preventDefault()

    const fields = event.target.closest("[data-nested-form-target='fields']")
    const destroyInput = fields.querySelector("[data-nested-form-target='destroy']")

    if (destroyInput) {
      // Mark for destruction (existing record)
      destroyInput.value = "1"
      fields.style.display = "none"
    } else {
      // Remove from DOM (new record)
      fields.remove()
    }
  }
}
```

### Pattern 4: Nested Form with Validation Errors

```erb
<%# app/views/posts/_image_fields.html.erb %>
<div class="nested-fields p-4 border rounded mb-2
            <%= 'border-red-500 bg-red-50' if f.object.errors.any? %>"
     data-nested-form-target="fields">

  <% if f.object.errors.any? %>
    <div class="text-red-600 text-sm mb-2">
      <%= f.object.errors.full_messages.to_sentence %>
    </div>
  <% end %>

  <div class="flex items-center gap-4">
    <div class="flex-1">
      <%= f.label :file %>
      <%= f.file_field :file, class: "input" %>
    </div>

    <div class="flex-1">
      <%= f.label :caption %>
      <%= f.text_field :caption, class: "input" %>
    </div>

    <%= f.hidden_field :_destroy, data: { nested_form_target: "destroy" } %>
    <button type="button" data-action="nested-form#remove" class="btn btn-danger">
      Remove
    </button>
  </div>
</div>
```

### Pattern 5: Nested Form for belongs_to

```ruby
# app/models/comment.rb
class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :author, class_name: "User", optional: true

  # Create author inline if provided
  accepts_nested_attributes_for :author, reject_if: :all_blank
end
```

```erb
<%= form_with model: [@post, @comment] do |f| %>
  <%= f.text_area :body %>

  <fieldset class="border p-4 rounded">
    <legend>Or post as guest:</legend>
    <%= f.fields_for :author, @comment.author || User.new do |author_form| %>
      <%= author_form.text_field :name, placeholder: "Name" %>
      <%= author_form.email_field :email, placeholder: "Email" %>
    <% end %>
  </fieldset>

  <%= f.submit %>
<% end %>
```

### Pattern 6: Multi-Level Nesting

```ruby
# Models
class Survey < ApplicationRecord
  has_many :questions, dependent: :destroy
  accepts_nested_attributes_for :questions, allow_destroy: true
end

class Question < ApplicationRecord
  belongs_to :survey
  has_many :options, dependent: :destroy
  accepts_nested_attributes_for :options, allow_destroy: true
end

class Option < ApplicationRecord
  belongs_to :question
end
```

```erb
<%# app/views/surveys/_form.html.erb %>
<%= form_with model: @survey, data: { controller: "nested-form" } do |f| %>
  <%= f.text_field :title %>

  <div data-nested-form-target="container" data-nested-level="questions">
    <%= f.fields_for :questions do |q_form| %>
      <%= render "question_fields", f: q_form %>
    <% end %>
  </div>

  <template data-nested-form-target="template" data-nested-level="questions">
    <%= f.fields_for :questions, Question.new, child_index: "QUESTION_INDEX" do |q_form| %>
      <%= render "question_fields", f: q_form %>
    <% end %>
  </template>

  <button type="button" data-action="nested-form#add" data-nested-level="questions">
    Add Question
  </button>

  <%= f.submit %>
<% end %>

<%# app/views/surveys/_question_fields.html.erb %>
<div class="nested-fields question-fields border p-4 rounded mb-4"
     data-nested-form-target="fields" data-controller="nested-form">
  <%= f.text_field :text, placeholder: "Question text" %>

  <div data-nested-form-target="container" data-nested-level="options">
    <%= f.fields_for :options do |o_form| %>
      <%= render "option_fields", f: o_form %>
    <% end %>
  </div>

  <template data-nested-form-target="template" data-nested-level="options">
    <%= f.fields_for :options, Option.new, child_index: "OPTION_INDEX" do |o_form| %>
      <%= render "option_fields", f: o_form %>
    <% end %>
  </template>

  <button type="button" data-action="nested-form#add" data-nested-level="options">
    Add Option
  </button>

  <%= f.hidden_field :_destroy, data: { nested_form_target: "destroy" } %>
  <button type="button" data-action="nested-form#remove">Remove Question</button>
</div>
```

### Pattern 7: Cocoon Alternative (Simpler Stimulus)

```javascript
// app/javascript/controllers/fields_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = {
    wrapperSelector: { type: String, default: ".nested-fields" }
  }

  add(event) {
    const template = this.element.querySelector("template")
    const content = template.content.cloneNode(true)

    // Replace placeholder index with timestamp
    const html = content.firstElementChild.outerHTML
      .replace(/NEW_RECORD/g, new Date().getTime().toString())

    event.target.insertAdjacentHTML("beforebegin", html)
  }

  remove(event) {
    const wrapper = event.target.closest(this.wrapperSelectorValue)
    const destroy = wrapper.querySelector("input[name*='_destroy']")

    if (destroy && !wrapper.dataset.newRecord) {
      destroy.value = "1"
      wrapper.style.display = "none"
    } else {
      wrapper.remove()
    }
  }
}
```

### Pattern 8: Server-Side Add (Turbo Stream)

```ruby
# app/controllers/posts_controller.rb
def add_image
  @post = Post.find(params[:id])
  @image = @post.images.build

  respond_to do |format|
    format.turbo_stream
  end
end
```

```erb
<%# app/views/posts/add_image.turbo_stream.erb %>
<%= turbo_stream.append "images" do %>
  <%= form_with model: [@post, @image], data: { turbo_frame: "_top" } do |f| %>
    <%= render "image_fields", f: f %>
  <% end %>
<% end %>
```

### Pattern 9: Sortable Nested Items

```erb
<div data-controller="sortable nested-form"
     data-sortable-handle-value=".handle">
  <%= f.fields_for :items do |item_form| %>
    <div class="nested-fields flex items-center gap-2"
         data-nested-form-target="fields">
      <span class="handle cursor-move">&#x2630;</span>
      <%= item_form.hidden_field :position, data: { sortable_target: "position" } %>
      <%= item_form.text_field :name %>
      <%= item_form.hidden_field :_destroy, data: { nested_form_target: "destroy" } %>
      <button type="button" data-action="nested-form#remove">Remove</button>
    </div>
  <% end %>
</div>
```

### Pattern 10: Conditional Nested Forms

```erb
<%# Show nested form only when checkbox is checked %>
<div data-controller="toggle">
  <%= f.check_box :has_metadata,
      data: { action: "toggle#toggle", toggle_target: "trigger" } %>
  <%= f.label :has_metadata, "Add metadata" %>

  <div data-toggle-target="content" class="<%= 'hidden' unless f.object.has_metadata? %>">
    <%= f.fields_for :metadata do |m| %>
      <%= m.text_field :keywords %>
      <%= m.text_area :description %>
    <% end %>
  </div>
</div>
```

## Strong Parameters for Nested Attributes

```ruby
def post_params
  params.require(:post).permit(
    :title,
    :body,
    # Simple nested
    images_attributes: [:id, :file, :caption, :_destroy],

    # With specific fields
    comments_attributes: [:id, :body, :author_name, :_destroy],

    # Deeply nested
    questions_attributes: [
      :id, :text, :_destroy,
      options_attributes: [:id, :label, :value, :_destroy]
    ],

    # belongs_to nested
    author_attributes: [:id, :name, :email]
  )
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Missing `_destroy` permit | Can't remove items | Add `:_destroy` to params |
| No `allow_destroy: true` | Destroy silently fails | Add option to model |
| Fixed child_index | Duplicate IDs | Use timestamp or `NEW_RECORD` |
| No reject_if | Saves blank records | Add `reject_if: :all_blank` |
| Too many nesting levels | Complex, buggy | Maximum 2 levels recommended |

## Related Skills

- [form-builder.md](./form-builder.md): Form basics
- [stimulus.md](./stimulus.md): Dynamic behaviors
- [../../hotwire/SKILL.md](../../hotwire/SKILL.md): Turbo Streams

## References

- [Nested Attributes](https://api.rubyonrails.org/classes/ActiveRecord/NestedAttributes/ClassMethods.html)
- [fields_for](https://api.rubyonrails.org/classes/ActionView/Helpers/FormHelper.html#method-i-fields_for)
