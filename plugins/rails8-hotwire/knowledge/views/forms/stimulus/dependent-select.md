---
name: rails8-stimulus-dependent-select
description: Dynamic dropdown population based on parent selection
---

# Dependent Select

## Overview

Dynamically populates a child select dropdown based on the value selected in a parent dropdown. Common for country/city, category/subcategory relationships.

## Controller Code

```javascript
// app/javascript/controllers/dependent_select_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["parent", "child"]
  static values = { url: String }

  async update() {
    const parentValue = this.parentTarget.value

    if (!parentValue) {
      this.clearChildOptions()
      this.childTarget.disabled = true
      return
    }

    this.childTarget.disabled = true
    this.setChildLoading()

    try {
      const url = `${this.urlValue}?parent_id=${parentValue}`
      const response = await fetch(url, {
        headers: { "Accept": "application/json" }
      })
      const data = await response.json()

      this.populateChildOptions(data)
      this.childTarget.disabled = false
    } catch (error) {
      console.error("Failed to load options:", error)
      this.setChildError()
    }
  }

  clearChildOptions() {
    // Clear all options and add default
    while (this.childTarget.options.length > 0) {
      this.childTarget.remove(0)
    }
    this.childTarget.add(new Option("Select...", ""))
  }

  setChildLoading() {
    this.clearChildOptions()
    this.childTarget.options[0].text = "Loading..."
  }

  setChildError() {
    this.clearChildOptions()
    this.childTarget.options[0].text = "Error loading"
  }

  populateChildOptions(data) {
    this.clearChildOptions()
    data.forEach(item => {
      this.childTarget.add(new Option(item.name, item.id))
    })
  }
}
```

## ERB Usage

```erb
<div data-controller="dependent-select"
     data-dependent-select-url-value="<%= cities_path %>">
  <div class="mb-4">
    <%= f.label :country_id %>
    <%= f.collection_select :country_id, Country.all, :id, :name,
        { prompt: "Select country" },
        { data: {
            dependent_select_target: "parent",
            action: "change->dependent-select#update"
          } } %>
  </div>

  <div class="mb-4">
    <%= f.label :city_id %>
    <%= f.select :city_id,
        options_for_select(@cities&.map { |c| [c.name, c.id] }, @user.city_id),
        { prompt: "Select city" },
        { data: { dependent_select_target: "child" }, disabled: @user.country_id.blank? } %>
  </div>
</div>
```

## Controller Setup

```ruby
# app/controllers/cities_controller.rb
class CitiesController < ApplicationController
  def index
    @cities = City.where(country_id: params[:parent_id])
    render json: @cities.select(:id, :name)
  end
end
```

## Routes

```ruby
# config/routes.rb
resources :cities, only: [:index]
```

## Features

- **Async loading**: Fetches options via AJAX
- **Loading states**: Shows "Loading..." while fetching
- **Error handling**: Displays error message on failure
- **Progressive enhancement**: Disables child until parent selected
- **Clean state management**: Properly clears and repopulates options

## Multi-Level Example

```erb
<!-- Country > State > City -->
<div data-controller="dependent-select"
     data-dependent-select-url-value="<%= states_path %>">
  <%= f.collection_select :country_id, Country.all, :id, :name,
      { prompt: "Select country" },
      { data: { dependent_select_target: "parent", action: "change->dependent-select#update" } } %>

  <%= f.select :state_id, [],
      { prompt: "Select state" },
      { data: { dependent_select_target: "child" }, disabled: true } %>
</div>

<div data-controller="dependent-select"
     data-dependent-select-url-value="<%= cities_path %>">
  <%= f.select :state_id, [],
      { prompt: "Select state" },
      { data: { dependent_select_target: "parent", action: "change->dependent-select#update" } } %>

  <%= f.select :city_id, [],
      { prompt: "Select city" },
      { data: { dependent_select_target: "child" }, disabled: true } %>
</div>
```

## JSON Response Format

```ruby
# Expected JSON format
[
  { "id": 1, "name": "New York" },
  { "id": 2, "name": "Los Angeles" },
  { "id": 3, "name": "Chicago" }
]
```

## Related Skills

- [SKILL.md](./SKILL.md): All form Stimulus patterns
- [../form-builder.md](../form-builder.md): Form basics
- [../../controllers/SKILL.md](../../controllers/SKILL.md): Controller patterns
