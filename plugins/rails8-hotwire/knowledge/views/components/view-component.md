---
name: rails8-views-view-component
description: ViewComponent gem setup, slots, testing, and best practices
---

# ViewComponent

## Overview

ViewComponent is a framework for building reusable, testable, and encapsulated view components in Rails. Components are Ruby objects that render templates, providing a clear interface and better testability than partials.

## When to Use

- When you need testable view logic
- When building reusable UI components
- When components have complex logic
- When you want typed interfaces for views
- When partials become hard to maintain

## Quick Start

```bash
# Add to Gemfile
bundle add view_component

# Generate a component
bin/rails generate component Card title
```

```ruby
# app/components/card_component.rb
class CardComponent < ViewComponent::Base
  def initialize(title:)
    @title = title
  end
end
```

```erb
<%# app/components/card_component.html.erb %>
<div class="card">
  <h3><%= @title %></h3>
  <%= content %>
</div>
```

```erb
<%# Usage %>
<%= render CardComponent.new(title: "Hello") do %>
  <p>Card content here</p>
<% end %>
```

## Main Patterns

### Pattern 1: Basic Component

```ruby
# app/components/alert_component.rb
class AlertComponent < ViewComponent::Base
  VARIANTS = %w[info success warning error].freeze

  def initialize(variant: "info", dismissible: false)
    @variant = variant.to_s
    @dismissible = dismissible

    raise ArgumentError, "Invalid variant: #{@variant}" unless VARIANTS.include?(@variant)
  end

  def variant_classes
    case @variant
    when "info" then "bg-blue-50 text-blue-800 border-blue-200"
    when "success" then "bg-green-50 text-green-800 border-green-200"
    when "warning" then "bg-yellow-50 text-yellow-800 border-yellow-200"
    when "error" then "bg-red-50 text-red-800 border-red-200"
    end
  end

  def dismissible?
    @dismissible
  end
end
```

```erb
<%# app/components/alert_component.html.erb %>
<div class="rounded-md border p-4 <%= variant_classes %>" role="alert"
     data-controller="<%= 'dismissible' if dismissible? %>">
  <div class="flex">
    <div class="flex-1">
      <%= content %>
    </div>
    <% if dismissible? %>
      <button type="button" data-action="dismissible#dismiss" class="ml-4">
        <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"/>
        </svg>
      </button>
    <% end %>
  </div>
</div>

<%# Usage %>
<%= render AlertComponent.new(variant: "success", dismissible: true) do %>
  Your changes have been saved!
<% end %>
```

### Pattern 2: Slots

```ruby
# app/components/card_component.rb
class CardComponent < ViewComponent::Base
  renders_one :header
  renders_one :footer
  renders_many :actions

  def initialize(padded: true)
    @padded = padded
  end

  def padded?
    @padded
  end
end
```

```erb
<%# app/components/card_component.html.erb %>
<div class="bg-white rounded-lg shadow">
  <% if header? %>
    <div class="px-6 py-4 border-b">
      <%= header %>
    </div>
  <% end %>

  <div class="<%= 'p-6' if padded? %>">
    <%= content %>
  </div>

  <% if actions? %>
    <div class="px-6 py-4 bg-gray-50 flex gap-2 rounded-b-lg">
      <% actions.each do |action| %>
        <%= action %>
      <% end %>
    </div>
  <% end %>

  <% if footer? %>
    <div class="px-6 py-4 border-t text-sm text-gray-500">
      <%= footer %>
    </div>
  <% end %>
</div>

<%# Usage %>
<%= render CardComponent.new do |card| %>
  <% card.with_header do %>
    <h3 class="text-lg font-semibold">Card Title</h3>
  <% end %>

  <p>Card content goes here.</p>

  <% card.with_action do %>
    <%= link_to "Edit", edit_path, class: "btn btn-secondary" %>
  <% end %>
  <% card.with_action do %>
    <%= link_to "Delete", delete_path, class: "btn btn-danger" %>
  <% end %>

  <% card.with_footer do %>
    Last updated: <%= time_ago_in_words(@updated_at) %> ago
  <% end %>
<% end %>
```

### Pattern 3: Polymorphic Slots

```ruby
# app/components/nav_component.rb
class NavComponent < ViewComponent::Base
  renders_many :items, types: {
    link: LinkItem,
    button: ButtonItem,
    divider: DividerItem
  }

  class LinkItem < ViewComponent::Base
    def initialize(href:, active: false)
      @href = href
      @active = active
    end

    def call
      link_to @href, class: "nav-link #{'active' if @active}" do
        content
      end
    end
  end

  class ButtonItem < ViewComponent::Base
    def initialize(action:)
      @action = action
    end

    def call
      button_tag class: "nav-button", data: { action: @action } do
        content
      end
    end
  end

  class DividerItem < ViewComponent::Base
    def call
      tag.hr class: "nav-divider"
    end
  end
end
```

```erb
<%# Usage %>
<%= render NavComponent.new do |nav| %>
  <% nav.with_link(href: root_path, active: true) { "Home" } %>
  <% nav.with_link(href: about_path) { "About" } %>
  <% nav.with_divider %>
  <% nav.with_button(action: "modal#open") { "Contact" } %>
<% end %>
```

### Pattern 4: Conditional Rendering

```ruby
# app/components/avatar_component.rb
class AvatarComponent < ViewComponent::Base
  def initialize(user:, size: :md)
    @user = user
    @size = size
  end

  # Don't render if no user
  def render?
    @user.present?
  end

  def size_classes
    case @size
    when :sm then "w-8 h-8 text-sm"
    when :md then "w-10 h-10 text-base"
    when :lg then "w-16 h-16 text-xl"
    end
  end

  def initials
    @user.name.split.map(&:first).join.upcase[0..1]
  end

  def has_avatar?
    @user.avatar.attached?
  end
end
```

```erb
<%# app/components/avatar_component.html.erb %>
<% if has_avatar? %>
  <%= image_tag @user.avatar, class: "rounded-full #{size_classes}", alt: @user.name %>
<% else %>
  <div class="rounded-full bg-gray-200 flex items-center justify-center font-medium text-gray-600 <%= size_classes %>">
    <%= initials %>
  </div>
<% end %>
```

### Pattern 5: Component with Stimulus

```ruby
# app/components/dropdown_component.rb
class DropdownComponent < ViewComponent::Base
  renders_one :trigger
  renders_one :menu

  def initialize(align: :left)
    @align = align
  end

  def alignment_classes
    case @align
    when :left then "left-0"
    when :right then "right-0"
    end
  end
end
```

```erb
<%# app/components/dropdown_component.html.erb %>
<div class="relative" data-controller="dropdown">
  <div data-action="click->dropdown#toggle">
    <%= trigger %>
  </div>

  <div data-dropdown-target="menu"
       class="hidden absolute mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50 <%= alignment_classes %>">
    <%= menu %>
  </div>
</div>
```

```erb
<%# Usage %>
<%= render DropdownComponent.new(align: :right) do |dropdown| %>
  <% dropdown.with_trigger do %>
    <button class="btn btn-secondary">Options</button>
  <% end %>

  <% dropdown.with_menu do %>
    <div class="py-1">
      <%= link_to "Edit", edit_path, class: "block px-4 py-2 hover:bg-gray-100" %>
      <%= link_to "Delete", delete_path, class: "block px-4 py-2 hover:bg-gray-100 text-red-600" %>
    </div>
  <% end %>
<% end %>
```

### Pattern 6: Collection Components

```ruby
# app/components/table_component.rb
class TableComponent < ViewComponent::Base
  renders_many :columns, ColumnComponent

  def initialize(collection:)
    @collection = collection
  end

  class ColumnComponent < ViewComponent::Base
    attr_reader :header

    def initialize(header:, accessor: nil, &block)
      @header = header
      @accessor = accessor
      @block = block
    end

    def value_for(item)
      if @block
        view_context.capture { @block.call(item) }
      elsif @accessor
        item.public_send(@accessor)
      end
    end
  end
end
```

```erb
<%# app/components/table_component.html.erb %>
<table class="min-w-full divide-y divide-gray-200">
  <thead class="bg-gray-50">
    <tr>
      <% columns.each do |column| %>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
          <%= column.header %>
        </th>
      <% end %>
    </tr>
  </thead>
  <tbody class="bg-white divide-y divide-gray-200">
    <% @collection.each do |item| %>
      <tr>
        <% columns.each do |column| %>
          <td class="px-6 py-4 whitespace-nowrap">
            <%= column.value_for(item) %>
          </td>
        <% end %>
      </tr>
    <% end %>
  </tbody>
</table>

<%# Usage %>
<%= render TableComponent.new(collection: @users) do |table| %>
  <% table.with_column(header: "Name", accessor: :name) %>
  <% table.with_column(header: "Email", accessor: :email) %>
  <% table.with_column(header: "Status") do |user| %>
    <span class="badge badge-<%= user.active? ? 'green' : 'gray' %>">
      <%= user.active? ? 'Active' : 'Inactive' %>
    </span>
  <% end %>
  <% table.with_column(header: "Actions") do |user| %>
    <%= link_to "Edit", edit_user_path(user), class: "text-blue-600" %>
  <% end %>
<% end %>
```

### Pattern 7: Component Testing

```ruby
# spec/components/alert_component_spec.rb
require "rails_helper"

RSpec.describe AlertComponent, type: :component do
  it "renders content" do
    render_inline(AlertComponent.new(variant: "success")) do
      "Success message"
    end

    expect(page).to have_text("Success message")
  end

  it "applies correct variant classes" do
    render_inline(AlertComponent.new(variant: "error")) { "Error" }

    expect(page).to have_css(".bg-red-50")
  end

  it "renders dismiss button when dismissible" do
    render_inline(AlertComponent.new(dismissible: true)) { "Alert" }

    expect(page).to have_button
  end

  it "does not render dismiss button by default" do
    render_inline(AlertComponent.new) { "Alert" }

    expect(page).not_to have_button
  end

  it "raises error for invalid variant" do
    expect {
      AlertComponent.new(variant: "invalid")
    }.to raise_error(ArgumentError)
  end
end
```

### Pattern 8: Previews

```ruby
# spec/components/previews/alert_component_preview.rb
class AlertComponentPreview < ViewComponent::Preview
  # @param variant select [info, success, warning, error]
  # @param dismissible toggle
  def default(variant: "info", dismissible: false)
    render AlertComponent.new(variant: variant, dismissible: dismissible) do
      "This is an alert message."
    end
  end

  def all_variants
    render_with_template
  end
end
```

```erb
<%# spec/components/previews/alert_component_preview/all_variants.html.erb %>
<div class="space-y-4">
  <% %w[info success warning error].each do |variant| %>
    <%= render AlertComponent.new(variant: variant) do %>
      This is a <%= variant %> alert.
    <% end %>
  <% end %>
</div>
```

### Pattern 9: Helpers and Translations

```ruby
# app/components/button_component.rb
class ButtonComponent < ViewComponent::Base
  include ActionView::Helpers::UrlHelper

  def initialize(href: nil, variant: :primary, size: :md, disabled: false)
    @href = href
    @variant = variant
    @size = size
    @disabled = disabled
  end

  def call
    if @href
      link_to @href, class: button_classes, disabled: @disabled do
        content
      end
    else
      content_tag :button, content, class: button_classes, disabled: @disabled
    end
  end

  private

  def button_classes
    [base_classes, variant_classes, size_classes].join(" ")
  end

  def base_classes
    "inline-flex items-center justify-center font-medium rounded-md transition-colors"
  end

  def variant_classes
    case @variant
    when :primary then "bg-blue-600 text-white hover:bg-blue-700"
    when :secondary then "bg-gray-200 text-gray-800 hover:bg-gray-300"
    when :danger then "bg-red-600 text-white hover:bg-red-700"
    end
  end

  def size_classes
    case @size
    when :sm then "px-3 py-1.5 text-sm"
    when :md then "px-4 py-2 text-sm"
    when :lg then "px-6 py-3 text-base"
    end
  end
end
```

### Pattern 10: Component Generator Template

```ruby
# lib/generators/component/component_generator.rb
class ComponentGenerator < Rails::Generators::NamedBase
  source_root File.expand_path("templates", __dir__)

  def create_component
    template "component.rb.tt", "app/components/#{file_name}_component.rb"
    template "component.html.erb.tt", "app/components/#{file_name}_component.html.erb"
    template "component_spec.rb.tt", "spec/components/#{file_name}_component_spec.rb"
    template "component_preview.rb.tt", "spec/components/previews/#{file_name}_component_preview.rb"
  end
end
```

## Configuration

```ruby
# config/application.rb
config.view_component.preview_paths << Rails.root.join("spec/components/previews")
config.view_component.show_previews = Rails.env.development?
config.view_component.default_preview_layout = "component_preview"
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Fat components | Hard to maintain | Split into smaller components |
| Logic in templates | Hard to test | Move to component class |
| Direct DB queries | Violates separation | Accept data as arguments |
| Not testing components | Bugs in UI | Write component specs |
| Overusing components | Added complexity | Use partials for simple cases |

## Related Skills

- [phlex.md](./phlex.md): Alternative component library
- [helpers.md](./helpers.md): View helpers
- [../partials/conventions.md](../partials/conventions.md): When to use partials

## References

- [ViewComponent Documentation](https://viewcomponent.org/)
- [ViewComponent GitHub](https://github.com/ViewComponent/view_component)
