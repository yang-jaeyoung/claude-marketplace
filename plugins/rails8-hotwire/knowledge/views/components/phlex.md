---
name: rails8-views-phlex
description: Phlex - Ruby-based view components as an alternative to ERB
---

# Phlex Components

## Overview

Phlex is a framework for building fast, reusable, testable views in pure Ruby. Instead of ERB templates, you write Ruby methods that generate HTML. It offers excellent performance and a clean, object-oriented approach.

## When to Use

- When you prefer Ruby over ERB
- When you want maximum view performance
- When building component libraries
- When you need type-safe view interfaces
- When you want to avoid template syntax

## Quick Start

```bash
# Add to Gemfile
bundle add phlex-rails
bin/rails generate phlex:install
```

```ruby
# app/views/components/card.rb
class Components::Card < Phlex::HTML
  def initialize(title:)
    @title = title
  end

  def view_template
    div(class: "card") do
      h3 { @title }
      yield if block_given?
    end
  end
end
```

```erb
<%# Usage in ERB %>
<%= render Components::Card.new(title: "Hello") do %>
  <p>Card content</p>
<% end %>
```

## Main Patterns

### Pattern 1: Basic Component

```ruby
# app/views/components/alert.rb
class Components::Alert < Phlex::HTML
  VARIANTS = {
    info: "bg-blue-50 text-blue-800 border-blue-200",
    success: "bg-green-50 text-green-800 border-green-200",
    warning: "bg-yellow-50 text-yellow-800 border-yellow-200",
    error: "bg-red-50 text-red-800 border-red-200"
  }.freeze

  def initialize(variant: :info, dismissible: false)
    @variant = variant
    @dismissible = dismissible
  end

  def view_template
    div(
      class: "rounded-md border p-4 #{VARIANTS[@variant]}",
      role: "alert",
      data: dismissible_data
    ) do
      div(class: "flex") do
        div(class: "flex-1") { yield }
        dismiss_button if @dismissible
      end
    end
  end

  private

  def dismissible_data
    { controller: "dismissible" } if @dismissible
  end

  def dismiss_button
    button(
      type: "button",
      data: { action: "dismissible#dismiss" },
      class: "ml-4"
    ) do
      svg(class: "h-5 w-5", viewBox: "0 0 20 20", fill: "currentColor") do |s|
        s.path(
          fill_rule: "evenodd",
          d: "M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1..."
        )
      end
    end
  end
end

# Usage
render Components::Alert.new(variant: :success, dismissible: true) do
  "Your changes have been saved!"
end
```

### Pattern 2: Component with Slots

```ruby
# app/views/components/card.rb
class Components::Card < Phlex::HTML
  def initialize(padded: true)
    @padded = padded
  end

  def view_template(&)
    div(class: "bg-white rounded-lg shadow", &)
  end

  def header(&)
    div(class: "px-6 py-4 border-b", &)
  end

  def body(&)
    div(class: @padded ? "p-6" : "", &)
  end

  def footer(&)
    div(class: "px-6 py-4 border-t text-sm text-gray-500", &)
  end

  def actions(&)
    div(class: "px-6 py-4 bg-gray-50 flex gap-2 rounded-b-lg", &)
  end
end

# Usage
render Components::Card.new do |card|
  card.header do
    h3(class: "text-lg font-semibold") { "Card Title" }
  end

  card.body do
    p { "Card content goes here." }
  end

  card.actions do
    a(href: edit_path, class: "btn btn-secondary") { "Edit" }
    a(href: delete_path, class: "btn btn-danger") { "Delete" }
  end

  card.footer do
    "Last updated: 2 hours ago"
  end
end
```

### Pattern 3: Page Layout

```ruby
# app/views/layouts/application_layout.rb
class Layouts::ApplicationLayout < Phlex::HTML
  include Phlex::Rails::Helpers::CSRFMetaTags
  include Phlex::Rails::Helpers::CSPMetaTag
  include Phlex::Rails::Helpers::StylesheetLinkTag
  include Phlex::Rails::Helpers::JavascriptImportmapTags

  def initialize(title: "My App")
    @title = title
  end

  def view_template(&)
    doctype

    html(lang: "en") do
      head do
        meta(charset: "UTF-8")
        meta(name: "viewport", content: "width=device-width, initial-scale=1.0")
        meta(name: "turbo-refresh-method", content: "morph")
        meta(name: "turbo-refresh-scroll", content: "preserve")

        csrf_meta_tags
        csp_meta_tag

        title { @title }

        stylesheet_link_tag "application", data: { turbo_track: "reload" }
        javascript_importmap_tags
      end

      body(class: "min-h-screen bg-gray-50") do
        render Components::Navbar.new

        div(id: "flash") do
          # Flash messages rendered here
        end

        main(class: "container mx-auto px-4 py-8", &)

        render Components::Footer.new
      end
    end
  end
end

# app/views/posts/index_view.rb
class Posts::IndexView < Phlex::HTML
  def initialize(posts:)
    @posts = posts
  end

  def view_template
    h1(class: "text-2xl font-bold mb-6") { "Posts" }

    div(class: "space-y-4") do
      @posts.each do |post|
        render Components::PostCard.new(post: post)
      end
    end
  end
end
```

### Pattern 4: Form Components

```ruby
# app/views/components/form_field.rb
class Components::FormField < Phlex::HTML
  include Phlex::Rails::Helpers::FormWith

  def initialize(form:, field:, type: :text_field, label: nil, hint: nil, **options)
    @form = form
    @field = field
    @type = type
    @label = label || field.to_s.humanize
    @hint = hint
    @options = options
  end

  def view_template
    div(class: "mb-4") do
      label_element
      input_element
      hint_element if @hint
      error_element
    end
  end

  private

  def label_element
    label(for: field_id, class: label_classes) { @label }
  end

  def input_element
    case @type
    when :text_field
      input(type: "text", name: field_name, id: field_id, class: input_classes, **@options)
    when :text_area
      textarea(name: field_name, id: field_id, class: input_classes, **@options)
    when :email_field
      input(type: "email", name: field_name, id: field_id, class: input_classes, **@options)
    when :password_field
      input(type: "password", name: field_name, id: field_id, class: input_classes, **@options)
    end
  end

  def hint_element
    p(class: "mt-1 text-sm text-gray-500") { @hint }
  end

  def error_element
    return unless has_errors?

    p(class: "mt-1 text-sm text-red-600") { errors.first }
  end

  def field_id
    "#{model_name}_#{@field}"
  end

  def field_name
    "#{model_name}[#{@field}]"
  end

  def model_name
    @form.object.class.model_name.param_key
  end

  def has_errors?
    @form.object.errors[@field].any?
  end

  def errors
    @form.object.errors[@field]
  end

  def label_classes
    base = "block text-sm font-medium"
    has_errors? ? "#{base} text-red-700" : "#{base} text-gray-700"
  end

  def input_classes
    base = "mt-1 block w-full rounded-md shadow-sm"
    if has_errors?
      "#{base} border-red-300 focus:border-red-500 focus:ring-red-500"
    else
      "#{base} border-gray-300 focus:border-blue-500 focus:ring-blue-500"
    end
  end
end
```

### Pattern 5: Table Component

```ruby
# app/views/components/data_table.rb
class Components::DataTable < Phlex::HTML
  def initialize(collection:)
    @collection = collection
    @columns = []
  end

  def view_template(&block)
    configure_columns(&block) if block

    table(class: "min-w-full divide-y divide-gray-200") do
      render_header
      render_body
    end
  end

  def column(header:, accessor: nil, &block)
    @columns << { header: header, accessor: accessor, block: block }
  end

  private

  def configure_columns(&block)
    block.call(self)
  end

  def render_header
    thead(class: "bg-gray-50") do
      tr do
        @columns.each do |col|
          th(class: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase") do
            col[:header]
          end
        end
      end
    end
  end

  def render_body
    tbody(class: "bg-white divide-y divide-gray-200") do
      @collection.each do |item|
        tr do
          @columns.each do |col|
            td(class: "px-6 py-4 whitespace-nowrap") do
              value = col[:block] ? col[:block].call(item) : item.public_send(col[:accessor])
              if value.is_a?(Phlex::HTML)
                render value
              else
                text value.to_s
              end
            end
          end
        end
      end
    end
  end
end

# Usage
render Components::DataTable.new(collection: @users) do |table|
  table.column(header: "Name", accessor: :name)
  table.column(header: "Email", accessor: :email)
  table.column(header: "Status") do |user|
    Components::Badge.new(
      text: user.active? ? "Active" : "Inactive",
      variant: user.active? ? :green : :gray
    )
  end
end
```

### Pattern 6: Button Component

```ruby
# app/views/components/button.rb
class Components::Button < Phlex::HTML
  VARIANTS = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300",
    danger: "bg-red-600 text-white hover:bg-red-700",
    ghost: "text-gray-700 hover:bg-gray-100"
  }.freeze

  SIZES = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base"
  }.freeze

  def initialize(href: nil, variant: :primary, size: :md, disabled: false, **options)
    @href = href
    @variant = variant
    @size = size
    @disabled = disabled
    @options = options
  end

  def view_template(&)
    if @href
      a(href: @href, class: button_classes, **@options, &)
    else
      button(type: "button", class: button_classes, disabled: @disabled, **@options, &)
    end
  end

  private

  def button_classes
    [
      "inline-flex items-center justify-center font-medium rounded-md transition-colors",
      VARIANTS[@variant],
      SIZES[@size],
      @disabled ? "opacity-50 cursor-not-allowed" : ""
    ].join(" ")
  end
end

# Usage
render Components::Button.new(variant: :primary) { "Submit" }
render Components::Button.new(href: posts_path, variant: :secondary) { "Back to Posts" }
```

### Pattern 7: Component Composition

```ruby
# app/views/components/modal.rb
class Components::Modal < Phlex::HTML
  def initialize(title: nil, size: :md)
    @title = title
    @size = size
  end

  def view_template(&)
    div(
      class: "fixed inset-0 bg-black/50 flex items-center justify-center z-50",
      data: { controller: "modal", action: "keydown.esc->modal#close click->modal#closeOnBackdrop" }
    ) do
      div(class: "bg-white rounded-lg shadow-xl #{size_classes}", data: { modal_target: "content" }) do
        render_header if @title
        div(class: "p-6", &)
      end
    end
  end

  def render_header
    div(class: "flex items-center justify-between p-4 border-b") do
      h2(class: "text-lg font-semibold") { @title }
      close_button
    end
  end

  def close_button
    button(
      type: "button",
      class: "text-gray-400 hover:text-gray-600",
      data: { action: "modal#close" }
    ) do
      svg(class: "w-6 h-6", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24") do |s|
        s.path(
          stroke_linecap: "round",
          stroke_linejoin: "round",
          stroke_width: "2",
          d: "M6 18L18 6M6 6l12 12"
        )
      end
    end
  end

  def footer(&)
    div(class: "flex justify-end gap-3 p-4 border-t bg-gray-50 rounded-b-lg", &)
  end

  private

  def size_classes
    case @size
    when :sm then "w-full max-w-sm mx-4"
    when :md then "w-full max-w-lg mx-4"
    when :lg then "w-full max-w-2xl mx-4"
    when :xl then "w-full max-w-4xl mx-4"
    end
  end
end

# Usage
render Components::Modal.new(title: "Confirm Delete", size: :sm) do |modal|
  p { "Are you sure you want to delete this item?" }

  modal.footer do
    render Components::Button.new(variant: :secondary, data: { action: "modal#close" }) { "Cancel" }
    render Components::Button.new(variant: :danger) { "Delete" }
  end
end
```

### Pattern 8: Testing Phlex Components

```ruby
# spec/views/components/alert_spec.rb
require "rails_helper"

RSpec.describe Components::Alert do
  it "renders content" do
    output = render_component do
      "Success message"
    end

    expect(output).to include("Success message")
  end

  it "applies correct variant classes" do
    output = render_component(variant: :error) do
      "Error"
    end

    expect(output).to include("bg-red-50")
  end

  it "includes dismiss button when dismissible" do
    output = render_component(dismissible: true) do
      "Alert"
    end

    expect(output).to include("dismissible#dismiss")
  end

  private

  def render_component(variant: :info, dismissible: false, &block)
    component = Components::Alert.new(variant: variant, dismissible: dismissible)
    component.call(&block)
  end
end
```

## Controller Integration

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  layout -> { Layouts::ApplicationLayout }

  def index
    @posts = Post.all
    render Posts::IndexView.new(posts: @posts)
  end

  def show
    @post = Post.find(params[:id])
    render Posts::ShowView.new(post: @post)
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Too much in one component | Hard to maintain | Split into smaller components |
| String interpolation in attrs | XSS risk | Use attribute methods |
| Direct DB access | Violates separation | Accept data as arguments |
| Mixing Phlex and ERB randomly | Inconsistent codebase | Choose one primary approach |
| No component organization | Hard to find | Use namespaced modules |

## Related Skills

- [view-component.md](./view-component.md): ViewComponent alternative
- [helpers.md](./helpers.md): Helper methods
- [../tailwind/patterns.md](../tailwind/patterns.md): Tailwind patterns

## References

- [Phlex Documentation](https://www.phlex.fun/)
- [Phlex GitHub](https://github.com/phlex-ruby/phlex)
- [Phlex Rails](https://github.com/phlex-ruby/phlex-rails)
