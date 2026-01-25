# CRM Application

## Overview

Customer Relationship Management system with contacts, deals, activities, and pipeline visualization using Turbo Frames.

## Prerequisites

- [models/associations](../../models/associations.md)
- [hotwire/turbo-frames](../../hotwire/turbo-frames.md)

## Quick Start

```bash
rails generate model Contact name:string email:string company:string
rails generate model Deal contact:references title:string amount:decimal stage:string
rails generate model Activity contact:references deal:references type:string notes:text
rails db:migrate
```

## Implementation

### Models

```ruby
# app/models/contact.rb
class Contact < ApplicationRecord
  has_many :deals, dependent: :destroy
  has_many :activities, dependent: :destroy

  validates :name, presence: true
  validates :email, format: { with: URI::MailTo::EMAIL_REGEXP }

  def self.ransackable_attributes(auth_object = nil)
    ["name", "email", "company"]
  end
end

# app/models/deal.rb
class Deal < ApplicationRecord
  belongs_to :contact
  has_many :activities, dependent: :destroy

  STAGES = %w[lead qualified proposal negotiation closed_won closed_lost].freeze

  validates :title, presence: true
  validates :stage, inclusion: { in: STAGES }

  scope :active, -> { where.not(stage: ["closed_won", "closed_lost"]) }
end
```

### Pipeline View

```erb
<!-- app/views/deals/pipeline.html.erb -->
<div class="pipeline grid grid-cols-5 gap-4">
  <% Deal::STAGES.each do |stage| %>
    <div class="stage">
      <h3><%= stage.titleize %></h3>
      <div class="deals">
        <% @deals_by_stage[stage].each do |deal| %>
          <%= turbo_frame_tag dom_id(deal) do %>
            <div class="deal-card">
              <%= link_to deal.title, deal %>
              <p><%= number_to_currency(deal.amount) %></p>
            </div>
          <% end %>
        <% end %>
      </div>
    </div>
  <% end %>
</div>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No activity tracking | Lost context | Log all interactions |
| Poor search | Can't find contacts | Use Ransack or pg_search |
| No pipeline visualization | Hard to track | Use kanban-style view |

## Related Skills

- [models/associations](../../models/associations.md)
- [hotwire/turbo-frames](../../hotwire/turbo-frames.md)
- [recipes/search](../features/search.md)

## References

- [CRM Best Practices](https://www.salesforce.com/crm/)
