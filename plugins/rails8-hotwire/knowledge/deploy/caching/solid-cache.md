# Solid Cache Configuration

## Overview

Solid Cache is Rails 8's default database-backed cache store. It eliminates the need for Redis for caching, using your existing PostgreSQL or MySQL database.

## When to Use

- When deploying Rails 8 applications
- When avoiding Redis infrastructure
- When simplifying deployment architecture
- When consistent durability is important

## Quick Start

### Installation

```bash
# Add to Gemfile (included in Rails 8 by default)
gem "solid_cache"

# Install
bundle install

# Generate migration
bin/rails solid_cache:install:migrations
bin/rails db:migrate
```

### Basic Configuration

```ruby
# config/environments/production.rb
config.cache_store = :solid_cache_store
```

```yaml
# config/solid_cache.yml
default: &default
  database: cache
  store_options:
    max_age: <%= 1.week.to_i %>
    max_size: <%= 256.megabytes %>
    namespace: <%= Rails.env %>

production:
  <<: *default

development:
  <<: *default
  store_options:
    max_age: <%= 1.day.to_i %>
    max_size: <%= 50.megabytes %>
```

## Database Configuration

### Dedicated Cache Database

```yaml
# config/database.yml
production:
  primary:
    <<: *default
    url: <%= ENV["DATABASE_URL"] %>
  cache:
    <<: *default
    url: <%= ENV["CACHE_DATABASE_URL"] %>
    migrations_paths: db/cache_migrate
```

### Same Database

```yaml
# config/database.yml
production:
  primary:
    <<: *default
    url: <%= ENV["DATABASE_URL"] %>
  cache:
    <<: *default
    url: <%= ENV["DATABASE_URL"] %>
    migrations_paths: db/cache_migrate
```

### Connection Pool Sizing

```yaml
# config/database.yml
production:
  cache:
    url: <%= ENV["CACHE_DATABASE_URL"] %>
    pool: <%= ENV.fetch("CACHE_DB_POOL") { 5 } %>
    migrations_paths: db/cache_migrate
```

## Store Options

### Full Configuration

```yaml
# config/solid_cache.yml
production:
  database: cache
  store_options:
    # Maximum age of cached entries
    max_age: <%= 1.week.to_i %>

    # Maximum total cache size (triggers eviction)
    max_size: <%= 256.megabytes %>

    # Maximum number of entries
    max_entries: 100_000

    # Namespace for keys (useful for cache invalidation)
    namespace: myapp_v1

    # Batch size for cleanup operations
    cluster_batch_size: 1000

    # How often to run cleanup (in seconds)
    expiry_batch_size: 100
```

### Environment-Specific

```yaml
# config/solid_cache.yml
default: &default
  database: cache

development:
  <<: *default
  store_options:
    max_age: <%= 1.hour.to_i %>
    max_size: <%= 10.megabytes %>
    namespace: dev

test:
  <<: *default
  store_options:
    max_age: <%= 1.minute.to_i %>
    max_size: <%= 1.megabyte %>
    namespace: test

production:
  <<: *default
  store_options:
    max_age: <%= 1.week.to_i %>
    max_size: <%= 512.megabytes %>
    namespace: <%= ENV.fetch("CACHE_NAMESPACE", "prod") %>
```

## Cache Operations

### Basic Usage

```ruby
# Write
Rails.cache.write("key", "value")
Rails.cache.write("key", "value", expires_in: 1.hour)

# Read
value = Rails.cache.read("key")

# Fetch (read or write)
value = Rails.cache.fetch("key", expires_in: 1.hour) do
  expensive_operation
end

# Delete
Rails.cache.delete("key")

# Check existence
Rails.cache.exist?("key")
```

### Fragment Caching

```erb
<!-- app/views/posts/show.html.erb -->
<% cache @post do %>
  <article>
    <h1><%= @post.title %></h1>
    <p><%= @post.body %></p>
  </article>
<% end %>
```

### Russian Doll Caching

```erb
<% cache @post do %>
  <article>
    <h1><%= @post.title %></h1>

    <% cache [@post, "comments"] do %>
      <%= render @post.comments %>
    <% end %>
  </article>
<% end %>
```

### Low-Level Caching

```ruby
class Post < ApplicationRecord
  def cached_comment_count
    Rails.cache.fetch([self, "comment_count"], expires_in: 1.hour) do
      comments.count
    end
  end
end
```

## Cache Cleanup

### Automatic Cleanup

Solid Cache automatically handles cleanup based on `max_size`, `max_age`, and `max_entries`.

### Manual Cleanup

```ruby
# Clear all cache
Rails.cache.clear

# Clear by pattern (namespace)
SolidCache.clear_namespace("myapp_v1")

# Cleanup expired entries (runs automatically, but can be triggered)
SolidCache::Entry.cleanup
```

### Scheduled Cleanup Job

```ruby
# app/jobs/cache_cleanup_job.rb
class CacheCleanupJob < ApplicationJob
  queue_as :maintenance

  def perform
    SolidCache::Entry.cleanup
  end
end
```

```ruby
# config/recurring.yml (Solid Queue)
cache_cleanup:
  class: CacheCleanupJob
  queue: maintenance
  schedule: every hour
```

## Multi-Database Setup

### Separate Cache Database

```yaml
# config/database.yml
production:
  primary:
    url: <%= ENV["DATABASE_URL"] %>
    pool: 10
  cache:
    url: <%= ENV["CACHE_DATABASE_URL"] %>
    pool: 5
    migrations_paths: db/cache_migrate
```

### Migrations

```bash
# Create cache database migration
bin/rails generate migration CreateSolidCacheEntries --database=cache

# Or install directly
bin/rails solid_cache:install:migrations
bin/rails db:migrate:cache
```

## Performance Optimization

### Index Configuration

```ruby
# The default migration creates optimal indexes
# Solid Cache handles this automatically
```

### Query Optimization

```yaml
# config/solid_cache.yml
production:
  store_options:
    # Larger batch sizes for better performance
    cluster_batch_size: 1000
    expiry_batch_size: 500

    # Higher limits reduce cleanup frequency
    max_entries: 500_000
```

### Connection Pool

```yaml
# config/database.yml
production:
  cache:
    url: <%= ENV["CACHE_DATABASE_URL"] %>
    pool: <%= ENV.fetch("CACHE_DB_POOL") { 10 } %>
    prepared_statements: true
```

## Cache Versioning

### Version-Based Invalidation

```ruby
# Change namespace to invalidate all cache
# config/solid_cache.yml
production:
  store_options:
    namespace: myapp_v2  # Change to invalidate
```

### Key-Based Versioning

```ruby
class Post < ApplicationRecord
  # Automatically versioned by updated_at
  def cache_key_with_version
    "#{cache_key}/#{updated_at.to_i}"
  end
end
```

## Kamal Configuration

### Deploy Configuration

```yaml
# config/deploy.yml
env:
  clear:
    RAILS_ENV: production
  secret:
    - DATABASE_URL
    - CACHE_DATABASE_URL
    - RAILS_MASTER_KEY
```

### Database Accessory

```yaml
# config/deploy.yml
accessories:
  cache-db:
    image: postgres:16
    host: 192.168.1.1
    port: 5433
    env:
      secret:
        - POSTGRES_PASSWORD
    directories:
      - cache-data:/var/lib/postgresql/data
```

## Monitoring

### Cache Statistics

```ruby
# app/controllers/admin/cache_controller.rb
class Admin::CacheController < ApplicationController
  def show
    @stats = {
      entries: SolidCache::Entry.count,
      size: SolidCache::Entry.sum("length(value)"),
      oldest: SolidCache::Entry.minimum(:created_at),
      newest: SolidCache::Entry.maximum(:created_at)
    }
  end
end
```

### Health Check

```ruby
# app/controllers/health_controller.rb
def cache
  Rails.cache.write("health_check", Time.current)
  value = Rails.cache.read("health_check")

  if value
    render json: { status: "ok", cache: "connected" }
  else
    render json: { status: "error", cache: "failed" }, status: 503
  end
end
```

## Solid Cache vs Redis

| Feature | Solid Cache | Redis |
|---------|-------------|-------|
| Persistence | Database-backed | RAM + optional RDB/AOF |
| Latency | ~1-5ms | ~0.1-1ms |
| Scalability | Vertical | Horizontal (cluster) |
| Durability | Transactional | Configurable |
| Setup | No additional service | Redis server required |
| Cost | Uses existing DB | Additional infrastructure |

## Migration from Redis

### Gradual Migration

```ruby
# config/environments/production.rb
# Step 1: Use both (Redis primary)
config.cache_store = :redis_cache_store, { url: ENV["REDIS_URL"] }

# Step 2: Switch to Solid Cache
config.cache_store = :solid_cache_store
```

### Clear Old Cache

```ruby
# Clear Redis cache before switching
Rails.cache.clear  # While still on Redis

# Switch to Solid Cache
# Update config and redeploy
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Same DB as primary | Contention | Use dedicated cache DB |
| Tiny max_size | Constant eviction | Size based on usage |
| No namespace | Version conflicts | Use namespaced keys |
| Sync cache clearing | Slow deploys | Clear in background |

## Related Files

- [redis.md](./redis.md): Redis caching
- [cdn.md](./cdn.md): CDN caching
- [../../background/SKILL.md](../../background/SKILL.md): Background jobs

## References

- [Solid Cache GitHub](https://github.com/rails/solid_cache)
- [Rails Caching Guide](https://guides.rubyonrails.org/caching_with_rails.html)
- [Rails 8 Release Notes](https://guides.rubyonrails.org/8_0_release_notes.html)
