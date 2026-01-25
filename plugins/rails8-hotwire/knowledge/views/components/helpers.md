---
name: rails8-views-helpers
description: Helper methods, presenter pattern, and decorator pattern for views
---

# View Helpers & Presenters

## Overview

View helpers, presenters, and decorators extract logic from views into testable Ruby classes. Helpers provide utility methods, presenters wrap models with view logic, and decorators add display methods while maintaining the original interface.

## When to Use

- **Helpers**: Utility methods used across views (formatting, UI generation)
- **Presenters**: When a view needs complex logic for a single model
- **Decorators**: When you want to add methods to a model for display purposes

## Quick Start

```ruby
# Helper (utility methods)
module DateHelper
  def format_date(date)
    date&.strftime("%B %d, %Y")
  end
end

# Presenter (view-specific logic)
class PostPresenter
  def initialize(post, view_context)
    @post = post
    @h = view_context
  end

  def published_badge
    @h.content_tag(:span, "Published", class: "badge badge-green") if @post.published?
  end
end

# Decorator (model extension)
class PostDecorator < SimpleDelegator
  def formatted_date
    created_at.strftime("%B %d, %Y")
  end
end
```

## Main Patterns

### Pattern 1: Application Helper

```ruby
# app/helpers/application_helper.rb
module ApplicationHelper
  # Format currency
  def format_currency(amount, currency: "USD")
    number_to_currency(amount, unit: currency_symbol(currency))
  end

  # Safe truncate with HTML
  def smart_truncate(text, length: 100)
    return "" if text.blank?
    truncate(strip_tags(text), length: length, omission: "...")
  end

  # Time ago with tooltip
  def time_ago_with_tooltip(time)
    return "Never" if time.blank?

    content_tag(:time,
      time_ago_in_words(time) + " ago",
      datetime: time.iso8601,
      title: time.to_fs(:long),
      data: { controller: "tooltip" }
    )
  end

  # Conditional wrapper
  def wrap_if(condition, tag, options = {}, &block)
    if condition
      content_tag(tag, options, &block)
    else
      capture(&block)
    end
  end

  private

  def currency_symbol(currency)
    { "USD" => "$", "EUR" => "€", "GBP" => "£" }[currency] || currency
  end
end
```

### Pattern 2: Button Helper

```ruby
# app/helpers/button_helper.rb
module ButtonHelper
  def btn(text = nil, path = nil, variant: :primary, size: :md, icon: nil, **options, &block)
    classes = btn_classes(variant, size)
    options[:class] = [classes, options[:class]].compact.join(" ")

    content = if block
      capture(&block)
    elsif icon
      safe_join([render_icon(icon), text], " ")
    else
      text
    end

    if path
      link_to content, path, **options
    else
      content_tag :button, content, type: "button", **options
    end
  end

  def btn_primary(text, path = nil, **options, &block)
    btn(text, path, variant: :primary, **options, &block)
  end

  def btn_secondary(text, path = nil, **options, &block)
    btn(text, path, variant: :secondary, **options, &block)
  end

  def btn_danger(text, path = nil, **options, &block)
    btn(text, path, variant: :danger, **options, &block)
  end

  private

  def btn_classes(variant, size)
    base = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"

    variants = {
      primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
      secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500",
      danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
      ghost: "text-gray-700 hover:bg-gray-100 focus:ring-gray-500",
      link: "text-blue-600 hover:text-blue-800 hover:underline"
    }

    sizes = {
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-sm",
      lg: "px-6 py-3 text-base"
    }

    [base, variants[variant], sizes[size]].join(" ")
  end

  def render_icon(name)
    render "shared/icons/#{name}"
  end
end
```

### Pattern 3: Presenter Class

```ruby
# app/presenters/base_presenter.rb
class BasePresenter
  include ActionView::Helpers::TagHelper
  include ActionView::Helpers::UrlHelper
  include ActionView::Context

  def initialize(object, view_context)
    @object = object
    @h = view_context
  end

  def method_missing(method, *args, &block)
    if @object.respond_to?(method)
      @object.public_send(method, *args, &block)
    else
      super
    end
  end

  def respond_to_missing?(method, include_private = false)
    @object.respond_to?(method, include_private) || super
  end

  private

  def h
    @h
  end
end

# app/presenters/post_presenter.rb
class PostPresenter < BasePresenter
  def title_with_status
    content_tag(:span) do
      safe_join([
        @object.title,
        status_badge
      ].compact, " ")
    end
  end

  def status_badge
    if @object.published?
      content_tag(:span, "Published", class: "badge badge-green")
    elsif @object.draft?
      content_tag(:span, "Draft", class: "badge badge-gray")
    else
      content_tag(:span, "Archived", class: "badge badge-yellow")
    end
  end

  def author_link
    h.link_to @object.author.name, h.user_path(@object.author), class: "text-blue-600 hover:underline"
  end

  def published_date
    return "Not published" unless @object.published_at

    h.time_tag(@object.published_at, @object.published_at.to_fs(:long))
  end

  def excerpt(length: 200)
    h.truncate(h.strip_tags(@object.body), length: length)
  end

  def reading_time
    words = @object.body.split.size
    minutes = (words / 200.0).ceil
    "#{minutes} min read"
  end

  def edit_link
    return unless h.policy(@object).edit?

    h.link_to "Edit", h.edit_post_path(@object), class: "text-gray-600 hover:text-gray-900"
  end

  def delete_button
    return unless h.policy(@object).destroy?

    h.button_to "Delete", h.post_path(@object),
      method: :delete,
      class: "text-red-600 hover:text-red-800",
      data: { turbo_confirm: "Are you sure?" }
  end
end
```

```erb
<%# Usage in views %>
<% presenter = PostPresenter.new(@post, self) %>
<h1><%= presenter.title_with_status %></h1>
<p>By <%= presenter.author_link %> | <%= presenter.published_date %></p>
<p><%= presenter.reading_time %></p>
```

### Pattern 4: Presenter Helper

```ruby
# app/helpers/presenter_helper.rb
module PresenterHelper
  def present(object, presenter_class = nil)
    presenter_class ||= "#{object.class}Presenter".constantize
    presenter = presenter_class.new(object, self)

    if block_given?
      yield presenter
    else
      presenter
    end
  end
end

# Usage
<%= present(@post) do |p| %>
  <h1><%= p.title_with_status %></h1>
<% end %>

# Or
<% post = present(@post) %>
<%= post.author_link %>
```

### Pattern 5: Decorator with SimpleDelegator

```ruby
# app/decorators/base_decorator.rb
class BaseDecorator < SimpleDelegator
  def self.decorate_collection(collection)
    collection.map { |item| new(item) }
  end

  def class
    __getobj__.class
  end

  def to_model
    __getobj__
  end
end

# app/decorators/user_decorator.rb
class UserDecorator < BaseDecorator
  def full_name
    [first_name, last_name].compact.join(" ")
  end

  def display_name
    full_name.presence || email.split("@").first
  end

  def avatar_url(size: 40)
    if avatar.attached?
      Rails.application.routes.url_helpers.url_for(avatar.variant(resize_to_fill: [size, size]))
    else
      gravatar_url(size)
    end
  end

  def role_badge
    case role
    when "admin" then "badge-red"
    when "moderator" then "badge-yellow"
    else "badge-gray"
    end
  end

  def member_since
    created_at.strftime("%B %Y")
  end

  def last_active
    return "Never" unless last_sign_in_at
    "#{ActionController::Base.helpers.time_ago_in_words(last_sign_in_at)} ago"
  end

  private

  def gravatar_url(size)
    hash = Digest::MD5.hexdigest(email.downcase)
    "https://www.gravatar.com/avatar/#{hash}?s=#{size}&d=mp"
  end
end

# Usage in controller
@user = UserDecorator.new(User.find(params[:id]))
@users = UserDecorator.decorate_collection(User.all)
```

### Pattern 6: Form Helper

```ruby
# app/helpers/form_helper.rb
module FormHelper
  def form_field(form, field, type: :text_field, label: nil, hint: nil, **options)
    model = form.object
    has_error = model.errors[field].any?

    content_tag(:div, class: "mb-4") do
      safe_join([
        form.label(field, label, class: label_classes(has_error)),
        form.send(type, field, class: input_classes(has_error), **options),
        hint_tag(hint, has_error),
        error_tag(model, field)
      ].compact)
    end
  end

  def form_select(form, field, choices, label: nil, hint: nil, **options)
    model = form.object
    has_error = model.errors[field].any?

    content_tag(:div, class: "mb-4") do
      safe_join([
        form.label(field, label, class: label_classes(has_error)),
        form.select(field, choices, {}, class: input_classes(has_error), **options),
        hint_tag(hint, has_error),
        error_tag(model, field)
      ].compact)
    end
  end

  private

  def label_classes(has_error)
    base = "block text-sm font-medium mb-1"
    has_error ? "#{base} text-red-700" : "#{base} text-gray-700"
  end

  def input_classes(has_error)
    base = "block w-full rounded-md shadow-sm"
    if has_error
      "#{base} border-red-300 focus:border-red-500 focus:ring-red-500"
    else
      "#{base} border-gray-300 focus:border-blue-500 focus:ring-blue-500"
    end
  end

  def hint_tag(hint, has_error)
    return if hint.blank? || has_error
    content_tag(:p, hint, class: "mt-1 text-sm text-gray-500")
  end

  def error_tag(model, field)
    return unless model.errors[field].any?
    content_tag(:p, model.errors[field].first, class: "mt-1 text-sm text-red-600")
  end
end
```

### Pattern 7: Navigation Helper

```ruby
# app/helpers/navigation_helper.rb
module NavigationHelper
  def nav_link(text, path, icon: nil, badge: nil, **options)
    is_active = current_page?(path) || request.path.start_with?(path.to_s)
    classes = nav_link_classes(is_active, options.delete(:class))

    link_to path, class: classes, **options do
      safe_join([
        icon ? render("shared/icons/#{icon}", class: "w-5 h-5 mr-3") : nil,
        content_tag(:span, text),
        badge ? content_tag(:span, badge, class: "ml-auto badge badge-blue") : nil
      ].compact)
    end
  end

  def nav_section(title, &block)
    content_tag(:div, class: "mb-6") do
      safe_join([
        content_tag(:h3, title, class: "px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider"),
        content_tag(:nav, class: "mt-2 space-y-1", &block)
      ])
    end
  end

  def breadcrumb(*items)
    content_tag(:nav, aria: { label: "Breadcrumb" }) do
      content_tag(:ol, class: "flex items-center space-x-2 text-sm text-gray-500") do
        safe_join(items.map.with_index do |(name, path), index|
          is_last = index == items.length - 1
          breadcrumb_item(name, path, is_last)
        end)
      end
    end
  end

  private

  def nav_link_classes(active, custom_classes)
    base = "flex items-center px-3 py-2 text-sm rounded-md"
    state = active ? "bg-gray-100 text-gray-900 font-medium" : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
    [base, state, custom_classes].compact.join(" ")
  end

  def breadcrumb_item(name, path, is_last)
    content_tag(:li, class: "flex items-center") do
      if is_last
        content_tag(:span, name, class: "text-gray-900 font-medium")
      else
        safe_join([
          link_to(name, path, class: "hover:text-gray-700"),
          content_tag(:span, "/", class: "mx-2 text-gray-400")
        ])
      end
    end
  end
end
```

### Pattern 8: Testing Helpers

```ruby
# spec/helpers/button_helper_spec.rb
require "rails_helper"

RSpec.describe ButtonHelper, type: :helper do
  describe "#btn" do
    it "renders a button with text" do
      result = helper.btn("Click me")
      expect(result).to have_button("Click me")
    end

    it "renders a link when path provided" do
      result = helper.btn("Go", "/path")
      expect(result).to have_link("Go", href: "/path")
    end

    it "applies variant classes" do
      result = helper.btn("Save", variant: :primary)
      expect(result).to include("bg-blue-600")
    end

    it "applies size classes" do
      result = helper.btn("Save", size: :lg)
      expect(result).to include("px-6")
    end
  end
end

# spec/presenters/post_presenter_spec.rb
require "rails_helper"

RSpec.describe PostPresenter do
  let(:view_context) { ApplicationController.new.view_context }
  let(:post) { create(:post, :published) }
  let(:presenter) { described_class.new(post, view_context) }

  describe "#status_badge" do
    context "when published" do
      it "returns green badge" do
        expect(presenter.status_badge).to include("badge-green")
      end
    end

    context "when draft" do
      let(:post) { create(:post, :draft) }

      it "returns gray badge" do
        expect(presenter.status_badge).to include("badge-gray")
      end
    end
  end

  describe "#reading_time" do
    it "calculates minutes based on word count" do
      post.body = "word " * 400  # 400 words = 2 minutes
      expect(presenter.reading_time).to eq("2 min read")
    end
  end
end
```

## Helper vs Presenter vs Decorator

| Aspect | Helper | Presenter | Decorator |
|--------|--------|-----------|-----------|
| Location | `app/helpers/` | `app/presenters/` | `app/decorators/` |
| Scope | Application-wide utilities | View-specific model logic | Model enhancement |
| Access | All views automatically | Instantiate per use | Wrap model instance |
| Testing | Helper specs | Unit specs | Unit specs |
| Best for | Formatting, UI utilities | Complex view logic | Adding display methods |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Logic in views | Hard to test | Extract to presenter/helper |
| Too many helpers | Hard to find | Organize by domain |
| Helper with state | Side effects | Use presenters instead |
| Decorator DB queries | N+1 queries | Eager load in controller |
| Mixing concerns | Unclear responsibilities | Separate by purpose |

## Related Skills

- [view-component.md](./view-component.md): Component approach
- [phlex.md](./phlex.md): Ruby-based views
- [../partials/conventions.md](../partials/conventions.md): Partial patterns

## References

- [Rails Helpers](https://guides.rubyonrails.org/action_view_helpers.html)
- [Presenter Pattern](https://www.rubyguides.com/2019/08/rails-presenter-pattern/)
- [Draper Gem](https://github.com/drapergem/draper) (decorator library)
