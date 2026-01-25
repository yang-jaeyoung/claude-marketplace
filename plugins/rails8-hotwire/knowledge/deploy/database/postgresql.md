# PostgreSQL Configuration

## Overview

PostgreSQL is the recommended database for Rails 8 production deployments. This guide covers configuration, connection pooling, and optimization.

## When to Use

- When deploying Rails applications to production
- When configuring connection pooling
- When optimizing database performance
- When setting up multiple databases

## Quick Start

### Basic Configuration

```yaml
# config/database.yml
default: &default
  adapter: postgresql
  encoding: unicode
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  timeout: 5000

development:
  <<: *default
  database: myapp_development

test:
  <<: *default
  database: myapp_test

production:
  <<: *default
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
```

## Connection Pooling

### Pool Size Calculation

```
Pool Size = (Web Concurrency * Threads) + Background Workers + 1
Example: (2 * 5) + 3 + 1 = 14
```

### Configuration

```yaml
# config/database.yml
production:
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("DB_POOL") { ENV.fetch("RAILS_MAX_THREADS") { 5 } } %>
  checkout_timeout: 5
  reaping_frequency: 10
  idle_timeout: 300
```

### PgBouncer Setup

```bash
# Install PgBouncer
apt-get install pgbouncer

# /etc/pgbouncer/pgbouncer.ini
[databases]
myapp = host=localhost dbname=myapp_production

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 5
```

### PgBouncer with Rails

```yaml
# config/database.yml
production:
  adapter: postgresql
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  prepared_statements: false  # Required for PgBouncer
  advisory_locks: false       # Required for transaction mode
```

## Multiple Databases

### Rails 8 Multi-DB

```yaml
# config/database.yml
production:
  primary:
    url: <%= ENV["DATABASE_URL"] %>
    pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  primary_replica:
    url: <%= ENV["DATABASE_REPLICA_URL"] %>
    pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
    replica: true
  cache:
    url: <%= ENV["CACHE_DATABASE_URL"] %>
    pool: 5
    migrations_paths: db/cache_migrate
  queue:
    url: <%= ENV["QUEUE_DATABASE_URL"] %>
    pool: 5
    migrations_paths: db/queue_migrate
```

### Automatic Role Switching

```ruby
# config/environments/production.rb
config.active_record.database_selector = { delay: 2.seconds }
config.active_record.database_resolver = ActiveRecord::Middleware::DatabaseSelector::Resolver
config.active_record.database_resolver_context = ActiveRecord::Middleware::DatabaseSelector::Resolver::Session
```

### Manual Database Switching

```ruby
# Read from replica
ActiveRecord::Base.connected_to(role: :reading) do
  User.all
end

# Write to primary
ActiveRecord::Base.connected_to(role: :writing) do
  User.create!(name: "John")
end

# Connect to specific database
ActiveRecord::Base.connected_to(database: :cache) do
  SolidCache::Entry.all
end
```

## Performance Optimization

### Connection Settings

```yaml
# config/database.yml
production:
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>

  # Connection optimization
  connect_timeout: 5
  checkout_timeout: 5

  # Statement caching
  prepared_statements: true
  statement_limit: 200

  # Lock optimization
  advisory_locks: true
  lock_timeout: 5000
```

### Query Optimization

```ruby
# config/initializers/postgresql.rb
ActiveSupport.on_load(:active_record) do
  # Enable query analysis
  if Rails.env.production?
    ActiveRecord::Base.connection.execute("SET statement_timeout = '30s'")
  end
end
```

### Index Recommendations

```ruby
# Gemfile
gem "pg_query"        # Query parsing
gem "pghero"          # Query analysis dashboard
```

```ruby
# config/routes.rb
authenticate :user, ->(u) { u.admin? } do
  mount PgHero::Engine, at: "pghero"
end
```

## SSL Configuration

### Force SSL Connection

```yaml
# config/database.yml
production:
  url: <%= ENV["DATABASE_URL"] %>
  sslmode: require
  sslrootcert: config/certs/ca-certificate.crt
```

### With Client Certificate

```yaml
production:
  url: <%= ENV["DATABASE_URL"] %>
  sslmode: verify-full
  sslrootcert: config/certs/ca-certificate.crt
  sslcert: config/certs/client-cert.pem
  sslkey: config/certs/client-key.pem
```

## Backup and Restore

### pg_dump Backup

```bash
# Backup
pg_dump -Fc -h host -U user -d myapp_production > backup.dump

# Restore
pg_restore -h host -U user -d myapp_production backup.dump

# With environment variable
pg_dump $DATABASE_URL > backup.sql
```

### Kamal Backup Script

```bash
#!/bin/bash
# .kamal/hooks/pre-deploy

# Backup before deployment
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backups/myapp_${DATE}.dump"

kamal accessory exec db "pg_dump -Fc -U postgres myapp_production" > $BACKUP_FILE
```

### Automated Backups

```ruby
# app/jobs/database_backup_job.rb
class DatabaseBackupJob < ApplicationJob
  queue_as :maintenance

  def perform
    timestamp = Time.current.strftime("%Y%m%d_%H%M%S")
    filename = "backup_#{timestamp}.dump"

    # Dump to temp file
    system("pg_dump -Fc #{ENV['DATABASE_URL']} > /tmp/#{filename}")

    # Upload to S3
    File.open("/tmp/#{filename}") do |file|
      bucket.object("backups/#{filename}").upload_file(file)
    end

    # Cleanup
    File.delete("/tmp/#{filename}")
  end

  private

  def bucket
    Aws::S3::Resource.new.bucket(ENV["BACKUP_BUCKET"])
  end
end
```

## Monitoring

### Connection Monitoring

```ruby
# app/controllers/health_controller.rb
def show
  checks = {
    database: database_check,
    pool: pool_check
  }

  render json: checks
end

private

def database_check
  ActiveRecord::Base.connection.execute("SELECT 1")
  { status: "ok" }
rescue => e
  { status: "error", message: e.message }
end

def pool_check
  pool = ActiveRecord::Base.connection_pool
  {
    status: "ok",
    size: pool.size,
    connections: pool.connections.size,
    waiting: pool.num_waiting_in_queue
  }
end
```

### Slow Query Logging

```ruby
# config/environments/production.rb
config.active_record.verbose_query_logs = false

# Log slow queries
ActiveSupport::Notifications.subscribe("sql.active_record") do |*args|
  event = ActiveSupport::Notifications::Event.new(*args)
  if event.duration > 1000  # 1 second
    Rails.logger.warn("SLOW QUERY (#{event.duration.round}ms): #{event.payload[:sql]}")
  end
end
```

## Docker PostgreSQL

### docker-compose.yml

```yaml
services:
  db:
    image: postgres:16
    volumes:
      - postgres:/var/lib/postgresql/data
      - ./tmp/db-init:/docker-entrypoint-initdb.d
    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp_production
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myapp"]
      interval: 10s
      timeout: 5s
      retries: 5
    command:
      - "postgres"
      - "-c"
      - "max_connections=200"
      - "-c"
      - "shared_buffers=256MB"
      - "-c"
      - "work_mem=16MB"
      - "-c"
      - "maintenance_work_mem=128MB"
      - "-c"
      - "effective_cache_size=768MB"

volumes:
  postgres:
```

### Kamal Accessory

```yaml
# config/deploy.yml
accessories:
  db:
    image: postgres:16
    host: 192.168.1.1
    port: 5432
    env:
      clear:
        POSTGRES_USER: myapp
        POSTGRES_DB: myapp_production
      secret:
        - POSTGRES_PASSWORD
    directories:
      - data:/var/lib/postgresql/data
    options:
      memory: 2g
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Pool too small | Connection timeouts | Calculate based on workers |
| No statement timeout | Runaway queries | Set statement_timeout |
| Missing indexes | Slow queries | Use EXPLAIN ANALYZE |
| No backups | Data loss risk | Automated backup jobs |
| Pooler without config | Connection issues | Disable prepared_statements |

## Related Files

- [supabase.md](./supabase.md): Supabase PostgreSQL
- [neon.md](./neon.md): Neon serverless
- [migrations.md](./migrations.md): Migration patterns

## References

- [Rails Database Configuration](https://guides.rubyonrails.org/configuring.html#database-configuration)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PgHero](https://github.com/ankane/pghero)
