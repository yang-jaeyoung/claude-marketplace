# Cloudflare R2 Setup

## Overview

Cloudflare R2 is S3-compatible object storage with zero egress fees. Excellent for high-traffic applications where bandwidth costs are a concern.

## When to Use

- When S3 egress costs are significant
- When global edge caching is valuable
- When using Cloudflare CDN
- When S3 compatibility is required

## Quick Start

### Create R2 Bucket

1. Go to Cloudflare Dashboard > R2
2. Create bucket (e.g., `myapp-production`)
3. Note the Account ID from the dashboard URL

### Generate API Tokens

1. R2 > Manage R2 API Tokens
2. Create token with Object Read & Write permissions
3. Save Access Key ID and Secret Access Key

### Rails Configuration

```yaml
# config/storage.yml
cloudflare:
  service: S3
  endpoint: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
  access_key_id: <%= Rails.application.credentials.dig(:cloudflare, :access_key_id) %>
  secret_access_key: <%= Rails.application.credentials.dig(:cloudflare, :secret_access_key) %>
  bucket: myapp-production
  region: auto
```

```ruby
# config/environments/production.rb
config.active_storage.service = :cloudflare
```

### Credentials Setup

```bash
# Edit credentials
EDITOR="code --wait" bin/rails credentials:edit
```

```yaml
# config/credentials.yml.enc
cloudflare:
  access_key_id: your_access_key_id
  secret_access_key: your_secret_access_key
  account_id: your_account_id
```

## CORS Configuration

### Cloudflare Dashboard

1. R2 > Your Bucket > Settings > CORS
2. Add rule:

```json
[
  {
    "AllowedOrigins": ["https://myapp.com", "https://www.myapp.com"],
    "AllowedMethods": ["GET", "PUT", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag", "Content-Type", "Content-Length"],
    "MaxAgeSeconds": 3600
  }
]
```

### For Development

```json
[
  {
    "AllowedOrigins": ["http://localhost:3000"],
    "AllowedMethods": ["GET", "PUT", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

## Public Bucket Access

### Enable Public Access

1. R2 > Your Bucket > Settings
2. Enable "Public Access"
3. Note the public URL: `https://pub-<hash>.r2.dev/<bucket>`

### Custom Domain (Recommended)

1. R2 > Your Bucket > Settings > Custom Domains
2. Add domain: `cdn.myapp.com`
3. Cloudflare automatically provisions SSL

```ruby
# config/environments/production.rb
config.active_storage.service = :cloudflare

# Use custom domain for public URLs
Rails.application.routes.default_url_options[:host] = "myapp.com"

# Or configure CDN host
config.action_controller.asset_host = "https://cdn.myapp.com"
```

## Direct Uploads

### Configuration

```yaml
# config/storage.yml
cloudflare:
  service: S3
  endpoint: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
  access_key_id: <%= Rails.application.credentials.dig(:cloudflare, :access_key_id) %>
  secret_access_key: <%= Rails.application.credentials.dig(:cloudflare, :secret_access_key) %>
  bucket: myapp-production
  region: auto
  public: true  # For direct public URLs
```

### View Setup

```erb
<%= form_with model: @post do |f| %>
  <%= f.file_field :image, direct_upload: true %>
<% end %>
```

## Cache Configuration

### Browser Caching

```ruby
# config/environments/production.rb
config.public_file_server.headers = {
  'Cache-Control' => "public, max-age=#{1.year.to_i}"
}
```

### R2 Cache Rules

Configure in Cloudflare Dashboard:

1. Rules > Page Rules or Cache Rules
2. Add rule for `cdn.myapp.com/*`
3. Set Cache Level: Cache Everything
4. Edge Cache TTL: 1 month

## Multiple Buckets

```yaml
# config/storage.yml
cloudflare_uploads:
  service: S3
  endpoint: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
  access_key_id: <%= Rails.application.credentials.dig(:cloudflare, :access_key_id) %>
  secret_access_key: <%= Rails.application.credentials.dig(:cloudflare, :secret_access_key) %>
  bucket: myapp-uploads
  region: auto

cloudflare_assets:
  service: S3
  endpoint: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
  access_key_id: <%= Rails.application.credentials.dig(:cloudflare, :access_key_id) %>
  secret_access_key: <%= Rails.application.credentials.dig(:cloudflare, :secret_access_key) %>
  bucket: myapp-assets
  region: auto
  public: true
```

```ruby
class User < ApplicationRecord
  has_one_attached :avatar, service: :cloudflare_uploads
end

class Asset < ApplicationRecord
  has_one_attached :file, service: :cloudflare_assets
end
```

## Presigned URLs

### Generate Presigned URL

```ruby
# For private access
blob = user.avatar.blob
url = blob.url(expires_in: 1.hour)
```

### Public URLs

```ruby
# With public bucket
class User < ApplicationRecord
  has_one_attached :avatar

  def avatar_url
    if avatar.attached?
      "https://cdn.myapp.com/#{avatar.key}"
    end
  end
end
```

## Migration from S3

### Copy Data

```bash
# Using rclone
rclone copy s3:old-bucket r2:new-bucket --progress

# Or AWS CLI with R2 endpoint
aws s3 sync s3://old-bucket s3://new-bucket \
  --endpoint-url https://<ACCOUNT_ID>.r2.cloudflarestorage.com
```

### Update Rails Config

```yaml
# config/storage.yml
# Change from:
amazon:
  service: S3
  access_key_id: <%= Rails.application.credentials.dig(:aws, :access_key_id) %>
  # ...

# To:
cloudflare:
  service: S3
  endpoint: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
  # ...
```

## Kamal Secrets

```bash
# .kamal/secrets
CLOUDFLARE_ACCESS_KEY_ID=your_access_key
CLOUDFLARE_SECRET_ACCESS_KEY=your_secret_key
CLOUDFLARE_ACCOUNT_ID=your_account_id
```

```yaml
# config/deploy.yml
env:
  secret:
    - CLOUDFLARE_ACCESS_KEY_ID
    - CLOUDFLARE_SECRET_ACCESS_KEY
    - CLOUDFLARE_ACCOUNT_ID
```

```yaml
# config/storage.yml
cloudflare:
  service: S3
  endpoint: https://<%= ENV["CLOUDFLARE_ACCOUNT_ID"] %>.r2.cloudflarestorage.com
  access_key_id: <%= ENV["CLOUDFLARE_ACCESS_KEY_ID"] %>
  secret_access_key: <%= ENV["CLOUDFLARE_SECRET_ACCESS_KEY"] %>
  bucket: myapp-production
  region: auto
```

## Lifecycle Rules

### Auto-delete Old Files

Configure in R2 dashboard or via API:

```bash
# Example: Delete files older than 90 days
curl -X PUT "https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/r2/buckets/<BUCKET>/lifecycle" \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": [{
      "id": "delete-old-files",
      "enabled": true,
      "conditions": {
        "age": 90
      },
      "actions": {
        "type": "DeleteObject"
      }
    }]
  }'
```

## Cost Comparison

| Provider | Storage | Egress | Class A Ops | Class B Ops |
|----------|---------|--------|-------------|-------------|
| R2 | $0.015/GB | $0 | $4.50/M | $0.36/M |
| S3 | $0.023/GB | $0.09/GB | $5.00/M | $0.40/M |
| GCS | $0.020/GB | $0.12/GB | $5.00/M | $0.40/M |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Missing CORS | Direct uploads fail | Configure CORS |
| No custom domain | Slow global access | Use custom domain with Cloudflare CDN |
| Public bucket for private files | Security risk | Use presigned URLs |
| No lifecycle rules | Storage bloat | Set deletion policies |

## Related Files

- [active-storage.md](./active-storage.md): Active Storage config
- [s3.md](./s3.md): AWS S3 configuration
- [../caching/cdn.md](../caching/cdn.md): CDN integration

## References

- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
- [R2 S3 Compatibility](https://developers.cloudflare.com/r2/api/s3/)
- [Rails Active Storage S3](https://guides.rubyonrails.org/active_storage_overview.html#amazon-s3-service)
