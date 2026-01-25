# Redis Caching Setup

## Overview

Redis provides in-memory caching with sub-millisecond latency. While Rails 8 defaults to Solid Cache, Redis remains valuable for high-performance caching, sessions, and Action Cable.

## When to Use

- When sub-millisecond cache latency is required
- When shared cache across multiple servers is needed
- When using Action Cable with WebSockets
- When high cache throughput is critical

## Quick Start

### Gemfile

```ruby
# Gemfile
gem "redis"
```

### Basic Configuration

```ruby
# config/environments/production.rb
config.cache_store = :redis_cache_store, {
  url: ENV.fetch("REDIS_URL"),
  connect_timeout: 2,
  read_timeout: 1,
  write_timeout: 1,
  reconnect_attempts: 1
}
```

### Redis URL Format

```bash
# Standard format
REDIS_URL=redis://localhost:6379/0

# With password
REDIS_URL=redis://:password@localhost:6379/0

# With user and password
REDIS_URL=redis://user:password@localhost:6379/0

# SSL/TLS
REDIS_URL=rediss://user:password@redis.example.com:6379/0
```

## Cache Store Options

### Full Configuration

```ruby
# config/environments/production.rb
config.cache_store = :redis_cache_store, {
  url: ENV.fetch("REDIS_URL"),

  # Connection options
  connect_timeout: 2,      # seconds
  read_timeout: 1,         # seconds
  write_timeout: 1,        # seconds
  reconnect_attempts: 3,
  reconnect_delay: 0.5,
  reconnect_delay_max: 1,

  # Cache options
  namespace: "myapp:cache",
  expires_in: 1.day,
  race_condition_ttl: 10.seconds,

  # Error handling
  error_handler: ->(method:, returning:, exception:) {
    Sentry.capture_exception(exception)
    Rails.logger.warn("Redis error: #{exception.message}")
  }
}
```

### Connection Pooling

```ruby
# config/environments/production.rb
config.cache_store = :redis_cache_store, {
  url: ENV.fetch("REDIS_URL"),
  pool_size: ENV.fetch("RAILS_MAX_THREADS") { 5 }.to_i,
  pool_timeout: 5
}
```

## Multiple Redis Instances

### Separate Caches

```ruby
# config/initializers/redis.rb
REDIS_CACHE = Redis.new(url: ENV["REDIS_CACHE_URL"])
REDIS_SESSION = Redis.new(url: ENV["REDIS_SESSION_URL"])
REDIS_SIDEKIQ = Redis.new(url: ENV["REDIS_SIDEKIQ_URL"])
```

### Rails Caching with Multiple

```ruby
# config/environments/production.rb
config.cache_store = :redis_cache_store, {
  url: ENV["REDIS_CACHE_URL"],
  namespace: "cache"
}

config.session_store :redis_store, {
  servers: [ENV["REDIS_SESSION_URL"]],
  expire_after: 1.day,
  key: "_myapp_session"
}
```

## Action Cable with Redis

### Cable Configuration

```yaml
# config/cable.yml
development:
  adapter: async

test:
  adapter: test

production:
  adapter: redis
  url: <%= ENV.fetch("REDIS_URL") %>
  channel_prefix: myapp_production
```

### Separate Redis for Cable

```yaml
# config/cable.yml
production:
  adapter: redis
  url: <%= ENV.fetch("REDIS_CABLE_URL") { ENV.fetch("REDIS_URL") } %>
  channel_prefix: myapp_cable
```

## Session Storage

### Redis Session Store

```ruby
# Gemfile
gem "redis-session-store"
```

```ruby
# config/initializers/session_store.rb
Rails.application.config.session_store :redis_store,
  servers: [ENV.fetch("REDIS_SESSION_URL")],
  expire_after: 1.day,
  key: "_myapp_session",
  threadsafe: true,
  signed: true
```

## Cache Operations

### Basic Usage

```ruby
# Write with TTL
Rails.cache.write("key", value, expires_in: 1.hour)

# Read
value = Rails.cache.read("key")

# Fetch (read or compute)
value = Rails.cache.fetch("key", expires_in: 1.hour) do
  expensive_computation
end

# Delete
Rails.cache.delete("key")
Rails.cache.delete_matched("pattern:*")  # Pattern matching

# Increment/Decrement
Rails.cache.increment("counter")
Rails.cache.decrement("counter")

# Multiple keys
Rails.cache.read_multi("key1", "key2", "key3")
Rails.cache.write_multi(key1: value1, key2: value2)
```

### Race Condition Prevention

```ruby
# Prevents thundering herd
value = Rails.cache.fetch("key", expires_in: 1.hour, race_condition_ttl: 10.seconds) do
  expensive_computation
end
```

## Docker Compose

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass "${REDIS_PASSWORD}"
    volumes:
      - redis:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis:
```

## Kamal Configuration

### Redis Accessory

```yaml
# config/deploy.yml
accessories:
  redis:
    image: redis:7-alpine
    host: 192.168.1.1
    port: 6379
    cmd: "redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}"
    directories:
      - redis-data:/data
    env:
      secret:
        - REDIS_PASSWORD
```

### Environment Variables

```bash
# .kamal/secrets
REDIS_URL=redis://:password@192.168.1.1:6379/0
REDIS_PASSWORD=secure_password
```

## Managed Redis Services

### AWS ElastiCache

```ruby
# config/environments/production.rb
config.cache_store = :redis_cache_store, {
  url: ENV["ELASTICACHE_URL"],
  ssl_params: { verify_mode: OpenSSL::SSL::VERIFY_NONE }
}
```

### Upstash (Serverless)

```ruby
# config/environments/production.rb
config.cache_store = :redis_cache_store, {
  url: ENV["UPSTASH_REDIS_URL"],
  ssl_params: { verify_mode: OpenSSL::SSL::VERIFY_PEER }
}
```

### Redis Cloud

```ruby
config.cache_store = :redis_cache_store, {
  url: "redis://#{ENV['REDIS_USER']}:#{ENV['REDIS_PASSWORD']}@#{ENV['REDIS_HOST']}:#{ENV['REDIS_PORT']}"
}
```

## Sentinel Configuration

### High Availability Setup

```ruby
# config/environments/production.rb
config.cache_store = :redis_cache_store, {
  url: "redis://mymaster",
  sentinels: [
    { host: "sentinel1.example.com", port: 26379 },
    { host: "sentinel2.example.com", port: 26379 },
    { host: "sentinel3.example.com", port: 26379 }
  ],
  role: :master
}
```

## Cluster Configuration

### Redis Cluster

```ruby
# config/environments/production.rb
config.cache_store = :redis_cache_store, {
  cluster: [
    "redis://node1.example.com:6379",
    "redis://node2.example.com:6379",
    "redis://node3.example.com:6379"
  ],
  replica: true
}
```

## Monitoring

### Health Check

```ruby
# app/controllers/health_controller.rb
def redis
  redis = Redis.new(url: ENV["REDIS_URL"])
  pong = redis.ping

  if pong == "PONG"
    render json: { status: "ok", redis: "connected" }
  else
    render json: { status: "error" }, status: 503
  end
rescue => e
  render json: { status: "error", message: e.message }, status: 503
end
```

### Memory Usage

```ruby
# Check Redis memory
redis = Redis.new(url: ENV["REDIS_URL"])
info = redis.info("memory")
# => {"used_memory"=>"1234567", "used_memory_human"=>"1.18M", ...}
```

### Key Statistics

```ruby
# Count keys by pattern
redis = Redis.new(url: ENV["REDIS_URL"])
cache_keys = redis.keys("cache:*").count
session_keys = redis.keys("session:*").count
```

## Memory Management

### Maxmemory Policy

```conf
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Docker Command

```yaml
# docker-compose.yml
services:
  redis:
    command: >
      redis-server
      --appendonly yes
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
```

## Security

### Password Authentication

```conf
# redis.conf
requirepass your_secure_password
```

### TLS/SSL

```ruby
config.cache_store = :redis_cache_store, {
  url: "rediss://redis.example.com:6379",
  ssl_params: {
    verify_mode: OpenSSL::SSL::VERIFY_PEER,
    ca_file: "/path/to/ca.crt"
  }
}
```

### ACL (Redis 6+)

```conf
# redis.conf
user rails on >password ~cache:* +@read +@write
user readonly on >password ~* +@read -@write
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No connection pooling | Connection exhaustion | Use pool_size option |
| No error handling | Silent failures | Configure error_handler |
| Unbounded cache | Memory exhaustion | Set maxmemory policy |
| No TTL on keys | Memory bloat | Always set expires_in |
| Single Redis for all | Contention | Separate by purpose |

## Related Files

- [solid-cache.md](./solid-cache.md): Solid Cache (Rails 8 default)
- [cdn.md](./cdn.md): CDN caching
- [../../realtime/SKILL.md](../../realtime/SKILL.md): Action Cable

## References

- [Redis Documentation](https://redis.io/documentation)
- [Rails Redis Cache Store](https://guides.rubyonrails.org/caching_with_rails.html#activesupport-cache-rediscachestore)
- [Redis Ruby Gem](https://github.com/redis/redis-rb)
