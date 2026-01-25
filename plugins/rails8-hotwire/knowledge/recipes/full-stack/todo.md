# Todo Application

## Overview

Todo app with lists, items, drag-drop reordering (Stimulus Sortable), sharing, and real-time updates.

## Prerequisites

- [hotwire/turbo-frames](../../hotwire/turbo-frames.md)
- [hotwire/stimulus](../../hotwire/stimulus.md)

## Quick Start

```bash
rails generate model TodoList name:string user:references
rails generate model TodoItem title:string completed:boolean position:integer list:references
rails db:migrate
```

## Implementation

### Models with Acts As List

```ruby
# Gemfile
gem "acts_as_list"

# app/models/todo_list.rb
class TodoList < ApplicationRecord
  belongs_to :user
  has_many :items, -> { order(position: :asc) }, class_name: "TodoItem", dependent: :destroy

  validates :name, presence: true
end

# app/models/todo_item.rb
class TodoItem < ApplicationRecord
  belongs_to :list, class_name: "TodoList"

  acts_as_list scope: :list

  validates :title, presence: true

  broadcasts_to :list
end
```

### Drag and Drop with Stimulus

```javascript
// app/javascript/controllers/sortable_controller.js
import { Controller } from "@hotwired/stimulus"
import Sortable from "sortablejs"

export default class extends Controller {
  connect() {
    this.sortable = Sortable.create(this.element, {
      animation: 150,
      onEnd: this.end.bind(this)
    })
  }

  end(event) {
    const id = event.item.dataset.id
    const position = event.newIndex + 1

    fetch(`/todo_items/${id}/move`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": document.querySelector("[name='csrf-token']").content
      },
      body: JSON.stringify({ position })
    })
  }
}
```

```erb
<!-- app/views/todo_lists/show.html.erb -->
<ul data-controller="sortable">
  <% @list.items.each do |item| %>
    <li data-id="<%= item.id %>">
      <%= item.title %>
    </li>
  <% end %>
</ul>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No position tracking | Random order | Use acts_as_list |
| Client-side only state | Lost on refresh | Save to database |
| No optimistic updates | Feels slow | Update UI immediately |

## Related Skills

- [hotwire/turbo-frames](../../hotwire/turbo-frames.md)
- [hotwire/stimulus](../../hotwire/stimulus.md)

## References

- [SortableJS](https://sortablejs.github.io/Sortable/)
- [acts_as_list](https://github.com/brendon/acts_as_list)
