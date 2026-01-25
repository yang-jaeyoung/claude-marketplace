# Search Feature

## Overview

Implement search from simple filtering (Ransack) to full-text PostgreSQL (pg_search) to advanced external search (Meilisearch).

## Prerequisites

- [models/queries](../../models/queries.md): ActiveRecord queries
- [hotwire/turbo-frames](../../hotwire/turbo-frames.md): Live search

## Quick Start

```ruby
# Gemfile - Choose your level
gem "ransack"           # Simple attribute search
gem "pg_search"         # PostgreSQL full-text search
gem "meilisearch-rails" # Advanced external search
```

## Implementation

### Level 1: Simple Search with Ransack

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  def index
    @q = Post.ransack(params[:q])
    @posts = @q.result.page(params[:page])
  end
end
```

```erb
<%= search_form_for @q do |f| %>
  <%= f.search_field :title_or_body_cont, placeholder: "Search..." %>
  <%= f.submit "Search" %>
<% end %>
```

### Level 2: Full-Text Search with pg_search

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  include PgSearch::Model

  pg_search_scope :search_full_text,
    against: { title: 'A', body: 'B' },
    using: { tsearch: { prefix: true } }
end

# Migration
execute <<-SQL
  CREATE INDEX posts_search_idx ON posts
  USING gin(to_tsvector('english', title || ' ' || body))
SQL
```

### Level 3: Meilisearch

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  include MeiliSearch::Rails

  meilisearch do
    attribute :title, :body
    searchable_attributes [:title, :body]
    filterable_attributes [:published]
  end
end
```

### Instant Search UI

```javascript
// app/javascript/controllers/search_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  search() {
    clearTimeout(this.timeout)
    this.timeout = setTimeout(() => {
      this.performSearch()
    }, 300)
  }

  async performSearch() {
    const query = this.inputTarget.value
    const response = await fetch(`/search?q=${query}`)
    // Update results
  }
}
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| LIKE queries | Slow, no ranking | Use full-text search |
| No debouncing | Too many requests | 300ms timeout |
| Missing indexes | Slow searches | Add GIN index |

## Related Skills

- [models/queries](../../models/queries.md)
- [hotwire/turbo-frames](../../hotwire/turbo-frames.md)

## References

- [pg_search](https://github.com/Casecommons/pg_search)
- [Meilisearch](https://www.meilisearch.com/)
- [Ransack](https://github.com/activerecord-hackery/ransack)
