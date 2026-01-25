# Supabase Integration

## Overview

Supabase provides managed PostgreSQL with built-in auth, storage, and realtime features. The database is standard PostgreSQL, fully compatible with Rails.

## When to Use

- When you need managed PostgreSQL with extras
- When building apps that need realtime database subscriptions
- When Supabase Auth/Storage integration is valuable
- When connection pooling is required

## Quick Start

### Connection Configuration

```yaml
# config/database.yml
production:
  adapter: postgresql
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  prepared_statements: false  # Required for Supabase pooler
```

### Connection Types

| Type | Use Case | URL Format |
|------|----------|------------|
| Direct | Migrations, admin | `postgres://postgres:[password]@db.[ref].supabase.co:5432/postgres` |
| Pooler (Transaction) | Web requests | `postgres://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.co:6543/postgres` |
| Pooler (Session) | Long connections | Same as transaction, with `?pgbouncer=true` |

### Environment Setup

```bash
# Direct connection (for migrations)
DATABASE_URL=postgres://postgres:your-password@db.abcdefghij.supabase.co:5432/postgres

# Pooler connection (for app)
DATABASE_URL=postgres://postgres.abcdefghij:your-password@aws-0-us-east-1.pooler.supabase.co:6543/postgres?sslmode=require

# Separate URLs for different purposes
DATABASE_URL=...pooler...       # App runtime
DIRECT_DATABASE_URL=...direct... # Migrations
```

## Connection Pooling

### Transaction Mode (Recommended)

```yaml
# config/database.yml
production:
  adapter: postgresql
  url: <%= ENV["DATABASE_URL"] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  prepared_statements: false  # Required
  advisory_locks: false       # Required for transaction mode
```

### Session Mode

```yaml
# config/database.yml
production:
  adapter: postgresql
  url: <%= ENV["DATABASE_URL"] %>?pgbouncer=true
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  prepared_statements: false
```

## Migrations with Direct Connection

### Kamal Configuration

```yaml
# config/deploy.yml
env:
  secret:
    - DATABASE_URL           # Pooler URL for runtime
    - DIRECT_DATABASE_URL    # Direct URL for migrations
```

```ruby
# config/database.yml
production:
  primary:
    url: <%= ENV["DATABASE_URL"] %>
    pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
    prepared_statements: false
    advisory_locks: false
```

```bash
# Run migrations with direct connection
DATABASE_URL=$DIRECT_DATABASE_URL kamal app exec "bin/rails db:migrate"
```

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
- name: Run migrations
  env:
    DATABASE_URL: ${{ secrets.DIRECT_DATABASE_URL }}
  run: bin/rails db:migrate

- name: Deploy
  env:
    DATABASE_URL: ${{ secrets.POOLER_DATABASE_URL }}
  run: kamal deploy
```

## SSL Configuration

### Force SSL (Recommended)

```yaml
# config/database.yml
production:
  url: <%= ENV["DATABASE_URL"] %>?sslmode=require
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
```

### With Root Certificate

```yaml
production:
  url: <%= ENV["DATABASE_URL"] %>
  sslmode: verify-full
  sslrootcert: config/certs/supabase-root.crt
```

## Supabase Features with Rails

### Row Level Security (RLS)

```sql
-- Enable RLS on table
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Policy for authenticated users
CREATE POLICY "Users can view own posts"
ON posts FOR SELECT
USING (user_id = current_setting('app.current_user_id')::uuid);
```

```ruby
# Set current user in Rails
ActiveRecord::Base.connection.execute(
  "SET app.current_user_id = '#{current_user.id}'"
)
```

### Realtime Subscriptions (Optional)

```javascript
// If using Supabase client for realtime
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

const channel = supabase
  .channel('posts')
  .on('postgres_changes',
    { event: '*', schema: 'public', table: 'posts' },
    (payload) => console.log(payload)
  )
  .subscribe()
```

### Storage Integration

```ruby
# config/storage.yml
supabase:
  service: S3
  endpoint: https://[project-ref].supabase.co/storage/v1/s3
  access_key_id: <%= Rails.application.credentials.dig(:supabase, :access_key_id) %>
  secret_access_key: <%= Rails.application.credentials.dig(:supabase, :secret_access_key) %>
  bucket: uploads
  region: auto
  force_path_style: true
```

## Solid Queue with Supabase

### Configuration

```yaml
# config/database.yml
production:
  primary:
    url: <%= ENV["DATABASE_URL"] %>
    pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
    prepared_statements: false
    advisory_locks: false
  queue:
    url: <%= ENV["DATABASE_URL"] %>
    pool: 5
    prepared_statements: false
    advisory_locks: false
    migrations_paths: db/queue_migrate
```

Note: Advisory locks are disabled with Supabase pooler. Solid Queue works but uses table-based locking.

## Solid Cache with Supabase

```yaml
# config/database.yml
production:
  primary:
    url: <%= ENV["DATABASE_URL"] %>
  cache:
    url: <%= ENV["DATABASE_URL"] %>
    pool: 5
    prepared_statements: false
    migrations_paths: db/cache_migrate
```

## Backup and Restore

### Supabase Dashboard

Supabase provides automatic daily backups on paid plans.

### Manual Backup

```bash
# Using direct connection
pg_dump $DIRECT_DATABASE_URL > backup.sql

# Restore
psql $DIRECT_DATABASE_URL < backup.sql
```

### pg_dump with SSL

```bash
pg_dump "$DIRECT_DATABASE_URL?sslmode=require" > backup.sql
```

## Performance Optimization

### Connection Limits

| Plan | Direct Connections | Pooler Connections |
|------|-------------------|-------------------|
| Free | 15 | 200 |
| Pro | 60 | 1500 |
| Team | 200 | 3000 |
| Enterprise | Custom | Custom |

### Pool Sizing

```yaml
# config/database.yml
production:
  pool: <%= ENV.fetch("DB_POOL") { 10 } %>  # Keep below plan limit
```

### Query Optimization

```ruby
# config/initializers/supabase.rb
if Rails.env.production?
  # Set statement timeout
  ActiveRecord::Base.connection.execute("SET statement_timeout = '30s'")
end
```

## Monitoring

### Connection Health Check

```ruby
# app/controllers/health_controller.rb
def database
  ActiveRecord::Base.connection.execute("SELECT 1")
  render json: { status: "ok" }
rescue => e
  render json: { status: "error", message: e.message }, status: 503
end
```

### Query Performance

Use Supabase Dashboard > Database > Query Performance for slow query analysis.

## Kamal Configuration

```yaml
# config/deploy.yml
service: myapp
image: ghcr.io/myuser/myapp

env:
  clear:
    RAILS_ENV: production
    RAILS_LOG_TO_STDOUT: true
  secret:
    - RAILS_MASTER_KEY
    - DATABASE_URL         # Pooler URL
    - DIRECT_DATABASE_URL  # For migrations

# No db accessory needed - using Supabase
```

```bash
# .kamal/secrets
DATABASE_URL=postgres://postgres.xxx:password@aws-0-us-east-1.pooler.supabase.co:6543/postgres?sslmode=require
DIRECT_DATABASE_URL=postgres://postgres:password@db.xxx.supabase.co:5432/postgres?sslmode=require
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Direct URL in production | Exceeds connection limits | Use pooler URL |
| prepared_statements: true | Pooler incompatibility | Disable prepared statements |
| Large pool size | Exhausts connections | Size based on plan limits |
| Migrations via pooler | Schema changes fail | Use direct connection |

## Related Files

- [postgresql.md](./postgresql.md): PostgreSQL configuration
- [neon.md](./neon.md): Neon serverless
- [migrations.md](./migrations.md): Migration patterns

## References

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Connection Pooling](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [Supabase with Rails](https://supabase.com/docs/guides/getting-started/frameworks/rails)
