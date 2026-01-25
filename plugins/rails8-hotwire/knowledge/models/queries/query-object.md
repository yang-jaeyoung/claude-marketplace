# Query Objects

## Overview

Query objects encapsulate complex database queries into dedicated classes, keeping models slim and queries reusable and testable.

## Basic Query Object

```ruby
# app/queries/posts_query.rb
class PostsQuery
  def initialize(relation = Post.all)
    @relation = relation
  end

  def call(params = {})
    @relation
      .then { |r| filter_by_status(r, params[:status]) }
      .then { |r| filter_by_author(r, params[:author_id]) }
      .then { |r| filter_by_date(r, params[:from], params[:to]) }
      .then { |r| search(r, params[:q]) }
      .then { |r| with_includes(r) }
      .then { |r| sort(r, params[:sort]) }
  end

  private

  def filter_by_status(relation, status)
    return relation if status.blank?
    relation.where(status: status)
  end

  def filter_by_author(relation, author_id)
    return relation if author_id.blank?
    relation.where(user_id: author_id)
  end

  def filter_by_date(relation, from, to)
    relation = relation.where("created_at >= ?", from) if from.present?
    relation = relation.where("created_at <= ?", to) if to.present?
    relation
  end

  def search(relation, query)
    return relation if query.blank?
    relation.where("title ILIKE :q OR body ILIKE :q", q: "%#{query}%")
  end

  def with_includes(relation)
    relation.includes(:user, :tags)
  end

  def sort(relation, sort_param)
    case sort_param
    when "oldest" then relation.order(created_at: :asc)
    when "popular" then relation.order(views_count: :desc)
    else relation.order(created_at: :desc)
    end
  end
end

# Usage in controller
class PostsController < ApplicationController
  def index
    @posts = PostsQuery.new.call(filter_params).page(params[:page])
  end

  private

  def filter_params
    params.permit(:status, :author_id, :from, :to, :q, :sort)
  end
end
```

## Callable Query Object

```ruby
# app/queries/application_query.rb
class ApplicationQuery
  def self.call(...)
    new(...).call
  end
end

# app/queries/published_posts_query.rb
class PublishedPostsQuery < ApplicationQuery
  def initialize(user: nil)
    @user = user
  end

  def call
    scope = Post.published.includes(:user, :tags)
    scope = scope.where(user: @user) if @user
    scope.order(published_at: :desc)
  end
end

# Usage
PublishedPostsQuery.call
PublishedPostsQuery.call(user: current_user)
```

## Composable Query Objects

```ruby
# app/queries/concerns/searchable.rb
module Searchable
  def search(relation, query, columns:)
    return relation if query.blank?

    conditions = columns.map { |col| "#{col} ILIKE :q" }.join(" OR ")
    relation.where(conditions, q: "%#{query}%")
  end
end

# app/queries/concerns/sortable.rb
module Sortable
  def sort(relation, sort_param, allowed:, default:)
    column, direction = parse_sort(sort_param, allowed, default)
    relation.order(column => direction)
  end

  private

  def parse_sort(param, allowed, default)
    return default if param.blank?

    column, direction = param.to_s.split("_")
    direction = %w[asc desc].include?(direction) ? direction.to_sym : :asc

    if allowed.include?(column.to_sym)
      [column.to_sym, direction]
    else
      default
    end
  end
end

# app/queries/products_query.rb
class ProductsQuery
  include Searchable
  include Sortable

  def initialize(relation = Product.all)
    @relation = relation
  end

  def call(params = {})
    @relation
      .then { |r| filter_by_category(r, params[:category_id]) }
      .then { |r| filter_by_price(r, params[:min_price], params[:max_price]) }
      .then { |r| search(r, params[:q], columns: [:name, :description]) }
      .then { |r| sort(r, params[:sort], allowed: [:name, :price, :created_at], default: [:created_at, :desc]) }
  end

  private

  def filter_by_category(relation, category_id)
    return relation if category_id.blank?
    relation.where(category_id: category_id)
  end

  def filter_by_price(relation, min, max)
    relation = relation.where("price >= ?", min) if min.present?
    relation = relation.where("price <= ?", max) if max.present?
    relation
  end
end
```

## Query Object with Result Object

```ruby
# app/queries/dashboard_stats_query.rb
class DashboardStatsQuery
  def initialize(user)
    @user = user
  end

  def call
    Result.new(
      total_posts: total_posts,
      published_posts: published_posts,
      total_views: total_views,
      top_posts: top_posts,
      recent_comments: recent_comments
    )
  end

  private

  Result = Struct.new(:total_posts, :published_posts, :total_views, :top_posts, :recent_comments, keyword_init: true)

  def total_posts
    @user.posts.count
  end

  def published_posts
    @user.posts.published.count
  end

  def total_views
    @user.posts.sum(:views_count)
  end

  def top_posts
    @user.posts.published.order(views_count: :desc).limit(5)
  end

  def recent_comments
    Comment.joins(:post).where(posts: { user_id: @user.id }).recent.limit(10)
  end
end

# Usage
stats = DashboardStatsQuery.new(current_user).call
stats.total_posts
stats.top_posts
```

## Query Object with SQL

```ruby
# app/queries/user_activity_query.rb
class UserActivityQuery
  def initialize(user)
    @user = user
  end

  def call
    ActiveRecord::Base.connection.execute(sql).to_a
  end

  private

  def sql
    <<~SQL
      SELECT
        DATE(created_at) as date,
        COUNT(*) as posts_count,
        SUM(views_count) as total_views
      FROM posts
      WHERE user_id = #{@user.id}
        AND created_at >= '#{30.days.ago.to_date}'
      GROUP BY DATE(created_at)
      ORDER BY date DESC
    SQL
  end
end

# Safer version with sanitization
class UserActivityQuery
  def call
    Post.connection.select_all(
      Post.sanitize_sql([sql, user_id: @user.id, since: 30.days.ago])
    ).to_a
  end

  private

  def sql
    <<~SQL
      SELECT
        DATE(created_at) as date,
        COUNT(*) as posts_count,
        SUM(views_count) as total_views
      FROM posts
      WHERE user_id = :user_id
        AND created_at >= :since
      GROUP BY DATE(created_at)
      ORDER BY date DESC
    SQL
  end
end
```

## Filtering Pattern

```ruby
# app/queries/filterable.rb
class Filterable
  def initialize(relation)
    @relation = relation
    @filters = []
  end

  def filter(name, value, &block)
    @filters << [name, value, block]
    self
  end

  def apply
    @filters.reduce(@relation) do |relation, (name, value, block)|
      if value.present?
        block.call(relation, value)
      else
        relation
      end
    end
  end
end

# Usage
class OrdersQuery
  def call(params)
    Filterable.new(Order.all)
      .filter(:status, params[:status]) { |r, v| r.where(status: v) }
      .filter(:customer_id, params[:customer_id]) { |r, v| r.where(customer_id: v) }
      .filter(:date_from, params[:from]) { |r, v| r.where("created_at >= ?", v) }
      .filter(:date_to, params[:to]) { |r, v| r.where("created_at <= ?", v) }
      .apply
      .includes(:customer, :line_items)
      .order(created_at: :desc)
  end
end
```

## Testing Query Objects

```ruby
# spec/queries/posts_query_spec.rb
RSpec.describe PostsQuery do
  describe "#call" do
    let!(:published_post) { create(:post, status: :published) }
    let!(:draft_post) { create(:post, status: :draft) }
    let!(:old_post) { create(:post, created_at: 2.months.ago) }

    it "returns all posts by default" do
      result = described_class.new.call

      expect(result).to include(published_post, draft_post, old_post)
    end

    it "filters by status" do
      result = described_class.new.call(status: :published)

      expect(result).to include(published_post)
      expect(result).not_to include(draft_post)
    end

    it "filters by date range" do
      result = described_class.new.call(from: 1.month.ago, to: Time.current)

      expect(result).to include(published_post)
      expect(result).not_to include(old_post)
    end

    it "searches by title" do
      searchable = create(:post, title: "Ruby on Rails Guide")

      result = described_class.new.call(q: "rails")

      expect(result).to include(searchable)
      expect(result).not_to include(published_post)
    end
  end
end
```

## File Organization

```
app/
├── queries/
│   ├── application_query.rb
│   ├── concerns/
│   │   ├── searchable.rb
│   │   └── sortable.rb
│   ├── posts_query.rb
│   ├── products_query.rb
│   └── users/
│       ├── active_users_query.rb
│       └── inactive_users_query.rb
```

## When to Use Query Objects

| Scenario | Use Query Object? |
|----------|-------------------|
| Simple `where` clause | No, use scope |
| 3+ filter conditions | Yes |
| Reused across controllers | Yes |
| Complex joins/aggregations | Yes |
| Needs testing in isolation | Yes |
| One-off query | No, inline is fine |

## Related

- [basics.md](./basics.md): Query fundamentals
- [n-plus-one.md](./n-plus-one.md): Eager loading
- [../activerecord/scopes.md](../activerecord/scopes.md): Model scopes
