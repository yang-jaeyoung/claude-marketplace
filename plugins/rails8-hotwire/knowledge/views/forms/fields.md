---
name: rails8-views-form-fields
description: Field types, custom inputs, date/time fields, and field options
---

# Form Fields

## Overview

Rails provides a comprehensive set of form field helpers. Each maps to HTML input types with Rails-specific enhancements for model binding, error handling, and Stimulus integration.

## When to Use

- When building any form input
- When implementing date/time pickers
- When creating select dropdowns
- When adding custom field attributes

## Quick Start

```erb
<%= form_with model: @user do |f| %>
  <%= f.text_field :name %>
  <%= f.email_field :email %>
  <%= f.password_field :password %>
  <%= f.select :role, User::ROLES %>
  <%= f.submit %>
<% end %>
```

## Main Patterns

### Pattern 1: Text Input Fields

```erb
<%# Basic text field %>
<%= f.text_field :name %>

<%# With all common options %>
<%= f.text_field :name,
    class: "input",
    placeholder: "Enter your name",
    required: true,
    autofocus: true,
    autocomplete: "name",
    minlength: 2,
    maxlength: 100,
    pattern: "[A-Za-z ]+",
    disabled: @user.locked?,
    readonly: !current_user.admin?,
    data: { controller: "input" } %>

<%# Text area %>
<%= f.text_area :bio, rows: 5, cols: 40 %>
<%= f.text_area :description,
    class: "input",
    placeholder: "Write something...",
    maxlength: 1000,
    data: { controller: "character-count", character_count_max_value: 1000 } %>

<%# Rich text (Action Text) %>
<%= f.rich_text_area :content %>
```

### Pattern 2: Specialized Text Fields

```erb
<%# Email %>
<%= f.email_field :email, autocomplete: "email" %>

<%# Password %>
<%= f.password_field :password, autocomplete: "new-password" %>
<%= f.password_field :password_confirmation %>

<%# Phone %>
<%= f.phone_field :phone, autocomplete: "tel" %>
<%= f.telephone_field :mobile %>  <%# Alias %>

<%# URL %>
<%= f.url_field :website, placeholder: "https://example.com" %>

<%# Search %>
<%= f.search_field :q, placeholder: "Search...",
    data: { action: "input->search#perform" } %>

<%# Number %>
<%= f.number_field :quantity, min: 1, max: 100, step: 1 %>
<%= f.number_field :price, min: 0, step: 0.01 %>

<%# Range (slider) %>
<%= f.range_field :rating, min: 1, max: 5, step: 1 %>

<%# Color picker %>
<%= f.color_field :theme_color %>
```

### Pattern 3: Date and Time Fields

```erb
<%# Date field (native browser picker) %>
<%= f.date_field :birth_date %>
<%= f.date_field :start_date, min: Date.current, max: 1.year.from_now %>

<%# Time field %>
<%= f.time_field :start_time %>
<%= f.time_field :opens_at, step: 900 %>  <%# 15-minute intervals %>

<%# Datetime (local, no timezone) %>
<%= f.datetime_local_field :event_at %>
<%= f.datetime_field :scheduled_for %>  <%# Alias %>

<%# Week picker %>
<%= f.week_field :target_week %>

<%# Month picker %>
<%= f.month_field :billing_month %>

<%# Legacy select-based (3 dropdowns) %>
<%= f.date_select :published_on,
    order: [:year, :month, :day],
    start_year: 2020,
    end_year: Date.current.year + 5,
    include_blank: true %>

<%= f.time_select :alarm_time,
    minute_step: 15,
    include_blank: true %>

<%= f.datetime_select :meeting_at %>
```

### Pattern 4: Select Fields

```erb
<%# Basic select %>
<%= f.select :status, ["draft", "published", "archived"] %>

<%# With labels different from values %>
<%= f.select :status, [["Draft", "draft"], ["Published", "published"]] %>

<%# From array of objects %>
<%= f.select :category_id, Category.pluck(:name, :id) %>

<%# With options_for_select %>
<%= f.select :role, options_for_select(User::ROLES, @user.role) %>

<%# With grouped options %>
<%= f.select :country, grouped_options_for_select({
  "North America" => [["USA", "us"], ["Canada", "ca"]],
  "Europe" => [["UK", "uk"], ["Germany", "de"]]
}) %>

<%# With blank option %>
<%= f.select :category_id, Category.pluck(:name, :id),
    { include_blank: "Select a category" },
    { class: "select" } %>

<%# With prompt (only shown when no selection) %>
<%= f.select :priority, %w[low medium high],
    { prompt: "Choose priority" } %>

<%# Multiple select %>
<%= f.select :tag_ids, Tag.pluck(:name, :id),
    { include_blank: false },
    { multiple: true, size: 5, class: "select" } %>

<%# Collection select %>
<%= f.collection_select :author_id, User.all, :id, :name,
    { prompt: "Select author" },
    { class: "select" } %>
```

### Pattern 5: Checkboxes and Radio Buttons

```erb
<%# Single checkbox (boolean) %>
<%= f.check_box :published %>
<%= f.label :published, "Make this public" %>

<%# Checkbox with custom values %>
<%= f.check_box :terms, { class: "checkbox" }, "accepted", "not_accepted" %>

<%# Multiple checkboxes (has_many / array) %>
<div class="space-y-2">
  <% Tag.all.each do |tag| %>
    <label class="flex items-center gap-2">
      <%= check_box_tag "post[tag_ids][]", tag.id, @post.tag_ids.include?(tag.id) %>
      <%= tag.name %>
    </label>
  <% end %>
</div>

<%# Collection checkboxes (cleaner) %>
<%= f.collection_check_boxes :tag_ids, Tag.all, :id, :name do |b| %>
  <label class="flex items-center gap-2">
    <%= b.check_box class: "checkbox" %>
    <%= b.label class: "text-sm" %>
  </label>
<% end %>

<%# Radio buttons %>
<div class="space-y-2">
  <% %w[draft published archived].each do |status| %>
    <label class="flex items-center gap-2">
      <%= f.radio_button :status, status, class: "radio" %>
      <%= status.humanize %>
    </label>
  <% end %>
</div>

<%# Collection radio buttons %>
<%= f.collection_radio_buttons :category_id, Category.all, :id, :name do |b| %>
  <label class="flex items-center gap-2">
    <%= b.radio_button class: "radio" %>
    <%= b.label %>
  </label>
<% end %>
```

### Pattern 6: File Fields

```erb
<%# Basic file upload %>
<%= f.file_field :avatar %>

<%# With accept filter %>
<%= f.file_field :image, accept: "image/*" %>
<%= f.file_field :document, accept: ".pdf,.doc,.docx" %>

<%# Multiple files %>
<%= f.file_field :photos, multiple: true %>

<%# Active Storage direct upload %>
<%= f.file_field :cover_image, direct_upload: true %>

<%# With preview using Stimulus %>
<div data-controller="image-preview">
  <%= f.file_field :avatar,
      accept: "image/*",
      data: { action: "change->image-preview#preview",
              image_preview_target: "input" } %>
  <img data-image-preview-target="preview" class="hidden mt-2 w-32 h-32 object-cover rounded">
</div>
```

### Pattern 7: Hidden Fields

```erb
<%# Hidden field %>
<%= f.hidden_field :user_id %>
<%= f.hidden_field :token, value: @token %>

<%# Hidden field outside form builder %>
<%= hidden_field_tag :redirect_to, request.referer %>

<%# CSRF token (automatically included) %>
<%# authenticity_token is added by form_with %>
```

### Pattern 8: Label Helper

```erb
<%# Basic label %>
<%= f.label :name %>  <%# => <label for="user_name">Name</label> %>

<%# Custom text %>
<%= f.label :name, "Full Name" %>

<%# With block for complex content %>
<%= f.label :terms do %>
  I agree to the <%= link_to "Terms", terms_path %>
<% end %>

<%# With class %>
<%= f.label :name, class: "block text-sm font-medium text-gray-700" %>

<%# For specific field ID %>
<%= f.label :email, "Email Address", for: "user_email_field" %>
```

### Pattern 9: Field Wrapper Pattern

```erb
<%# Reusable field component %>
<%# app/views/shared/_field.html.erb %>
<%# locals: (form:, field:, label: nil, hint: nil, **options) %>
<div class="mb-4">
  <%= form.label field, label, class: "block text-sm font-medium text-gray-700 mb-1" %>

  <%= form.text_field field, class: "input #{form.object.errors[field].any? ? 'border-red-500' : ''}", **options %>

  <% if hint %>
    <p class="mt-1 text-sm text-gray-500"><%= hint %></p>
  <% end %>

  <% if form.object.errors[field].any? %>
    <p class="mt-1 text-sm text-red-600"><%= form.object.errors[field].first %></p>
  <% end %>
</div>

<%# Usage %>
<%= form_with model: @user do |f| %>
  <%= render "shared/field", form: f, field: :name, hint: "Your display name" %>
  <%= render "shared/field", form: f, field: :email, label: "Email Address" %>
  <%= f.submit %>
<% end %>
```

### Pattern 10: Stimulus-Enhanced Fields

```erb
<%# Character counter %>
<div data-controller="character-count">
  <%= f.text_area :bio,
      maxlength: 500,
      data: { character_count_target: "input", action: "input->character-count#update" } %>
  <span data-character-count-target="count">0</span>/500
</div>

<%# Auto-resize textarea %>
<%= f.text_area :content,
    data: { controller: "auto-resize", action: "input->auto-resize#resize" } %>

<%# Slug generator %>
<div data-controller="slug">
  <%= f.text_field :title, data: { action: "input->slug#generate", slug_target: "source" } %>
  <%= f.text_field :slug, data: { slug_target: "output" }, readonly: true %>
</div>

<%# Dependent select %>
<div data-controller="dependent-select">
  <%= f.select :country_id, Country.pluck(:name, :id),
      { prompt: "Select country" },
      { data: { action: "change->dependent-select#load", dependent_select_target: "source" } } %>

  <%= f.select :city_id, [],
      { prompt: "Select city" },
      { data: { dependent_select_target: "dependent", dependent_select_url_value: cities_path } } %>
</div>
```

## Field Options Summary

| Option | Purpose | Example |
|--------|---------|---------|
| `class` | CSS classes | `class: "input"` |
| `id` | Override ID | `id: "custom_id"` |
| `placeholder` | Placeholder text | `placeholder: "Enter..."` |
| `required` | HTML5 required | `required: true` |
| `disabled` | Disable field | `disabled: @locked` |
| `readonly` | Read-only field | `readonly: true` |
| `autofocus` | Focus on load | `autofocus: true` |
| `autocomplete` | Browser autocomplete | `autocomplete: "email"` |
| `data` | Data attributes | `data: { controller: "x" }` |
| `min/max` | Number/date range | `min: 0, max: 100` |
| `step` | Number increment | `step: 0.01` |
| `pattern` | Regex validation | `pattern: "[0-9]+"` |
| `minlength/maxlength` | Length limits | `maxlength: 100` |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Date selects for UX | Clunky 3-dropdown UI | Use native `date_field` |
| No autocomplete hints | Poor autofill | Add `autocomplete` attribute |
| select without prompt | Unclear default | Add `prompt:` or `include_blank:` |
| Inline validation only | Server bypassed | Always validate server-side |
| No maxlength on text | Database overflow | Match DB column limits |

## Related Skills

- [form-builder.md](./form-builder.md): Form setup
- [errors.md](./errors.md): Error display
- [stimulus.md](./stimulus.md): Enhanced fields

## References

- [Rails Form Helpers](https://guides.rubyonrails.org/form_helpers.html)
- [HTML Input Types](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input)
