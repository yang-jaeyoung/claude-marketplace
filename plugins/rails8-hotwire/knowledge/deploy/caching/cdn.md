# CDN Configuration

## Overview

Content Delivery Networks (CDN) cache static assets and responses at edge locations worldwide, reducing latency and server load. This guide covers Cloudflare, CloudFront, and general CDN integration with Rails.

## When to Use

- When serving global users
- When offloading static asset delivery
- When caching full page responses
- When DDoS protection is needed

## Quick Start

### Asset Host Configuration

```ruby
# config/environments/production.rb
config.action_controller.asset_host = "https://cdn.myapp.com"
```

### Cloudflare Setup

1. Add domain to Cloudflare
2. Update DNS to Cloudflare nameservers
3. Configure caching rules

## Cloudflare Configuration

### Page Rules

```
URL: cdn.myapp.com/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 1 year
```

### Cache Rules (Recommended)

```
# Rule 1: Static Assets
When: URI Path matches *.js, *.css, *.png, *.jpg, *.webp, *.woff2
Then:
  - Cache: Eligible for cache
  - Edge TTL: 1 month
  - Browser TTL: 1 year

# Rule 2: API Endpoints (No Cache)
When: URI Path starts with /api/
Then:
  - Cache: Bypass cache

# Rule 3: HTML Pages (Conditional)
When: URI Path does not match above
Then:
  - Cache: Bypass cache (or configure stale-while-revalidate)
```

### Transform Rules (Headers)

```
# Add cache headers for static assets
When: URI Path matches *.js or *.css
Then:
  Set header: Cache-Control = public, max-age=31536000, immutable
```

### Rails Configuration for Cloudflare

```ruby
# config/environments/production.rb

# Trust Cloudflare IPs
config.action_dispatch.trusted_proxies = ActionDispatch::RemoteIp::TRUSTED_PROXIES + [
  IPAddr.new("103.21.244.0/22"),
  IPAddr.new("103.22.200.0/22"),
  IPAddr.new("103.31.4.0/22"),
  IPAddr.new("104.16.0.0/13"),
  IPAddr.new("104.24.0.0/14"),
  IPAddr.new("108.162.192.0/18"),
  IPAddr.new("131.0.72.0/22"),
  IPAddr.new("141.101.64.0/18"),
  IPAddr.new("162.158.0.0/15"),
  IPAddr.new("172.64.0.0/13"),
  IPAddr.new("173.245.48.0/20"),
  IPAddr.new("188.114.96.0/20"),
  IPAddr.new("190.93.240.0/20"),
  IPAddr.new("197.234.240.0/22"),
  IPAddr.new("198.41.128.0/17")
]

# Use CF-Connecting-IP header
config.action_dispatch.ip_spoofing_check = false
```

```ruby
# config/initializers/cloudflare.rb
module CloudflareRemoteIp
  def remote_ip
    request.headers["CF-Connecting-IP"] || super
  end
end

ActionDispatch::Request.prepend(CloudflareRemoteIp)
```

## AWS CloudFront

### Distribution Configuration

```yaml
# CloudFront distribution settings
Origins:
  - DomainName: myapp.com
    OriginPath: ""
    S3OriginConfig: null  # Not S3
    CustomOriginConfig:
      HTTPPort: 80
      HTTPSPort: 443
      OriginProtocolPolicy: https-only

DefaultCacheBehavior:
  ViewerProtocolPolicy: redirect-to-https
  CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6  # CachingOptimized
  OriginRequestPolicyId: 88a5eaf4-2fd4-4709-b370-b4c650ea3fcf  # CORS-S3Origin
  Compress: true

CacheBehaviors:
  # Static assets
  - PathPattern: /assets/*
    ViewerProtocolPolicy: redirect-to-https
    CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6
    TTL:
      DefaultTTL: 86400
      MaxTTL: 31536000
```

### Origin Shield

```yaml
OriginShield:
  Enabled: true
  OriginShieldRegion: us-east-1
```

### Rails Configuration for CloudFront

```ruby
# config/environments/production.rb
config.action_controller.asset_host = "https://d1234567890.cloudfront.net"

# For assets in S3
config.public_file_server.headers = {
  "Cache-Control" => "public, max-age=31536000, immutable"
}
```

## Cache Headers

### Static Assets

```ruby
# config/environments/production.rb
config.public_file_server.enabled = true
config.public_file_server.headers = {
  "Cache-Control" => "public, max-age=31536000, immutable",
  "X-Content-Type-Options" => "nosniff"
}
```

### Controller-Level Caching

```ruby
class PostsController < ApplicationController
  def show
    @post = Post.find(params[:id])

    if stale?(
      last_modified: @post.updated_at,
      etag: @post.cache_key_with_version,
      public: true
    )
      expires_in 1.hour, public: true
    end
  end
end
```

### Fragment Caching Headers

```ruby
# Set cache headers for cached fragments
class ApplicationController < ActionController::Base
  after_action :set_cache_headers

  private

  def set_cache_headers
    if request.get? && response.successful?
      response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=300"
    end
  end
end
```

## Stale-While-Revalidate

### Controller Configuration

```ruby
def show
  @post = Post.find(params[:id])

  expires_in 1.minute, public: true, stale_while_revalidate: 5.minutes
end
```

### CDN Configuration (Cloudflare)

```
Cache-Control: public, max-age=60, stale-while-revalidate=300
```

## Cache Invalidation

### Cloudflare API

```ruby
# lib/cloudflare_cache.rb
class CloudflareCache
  def self.purge(urls)
    conn = Faraday.new(url: "https://api.cloudflare.com")
    conn.post("/client/v4/zones/#{ENV['CLOUDFLARE_ZONE_ID']}/purge_cache") do |req|
      req.headers["Authorization"] = "Bearer #{ENV['CLOUDFLARE_API_TOKEN']}"
      req.headers["Content-Type"] = "application/json"
      req.body = { files: Array(urls) }.to_json
    end
  end

  def self.purge_all
    conn = Faraday.new(url: "https://api.cloudflare.com")
    conn.post("/client/v4/zones/#{ENV['CLOUDFLARE_ZONE_ID']}/purge_cache") do |req|
      req.headers["Authorization"] = "Bearer #{ENV['CLOUDFLARE_API_TOKEN']}"
      req.headers["Content-Type"] = "application/json"
      req.body = { purge_everything: true }.to_json
    end
  end
end
```

### CloudFront Invalidation

```ruby
# lib/cloudfront_cache.rb
class CloudfrontCache
  def self.invalidate(paths)
    client = Aws::CloudFront::Client.new
    client.create_invalidation(
      distribution_id: ENV["CLOUDFRONT_DISTRIBUTION_ID"],
      invalidation_batch: {
        paths: {
          quantity: paths.length,
          items: paths
        },
        caller_reference: "#{Time.current.to_i}-#{SecureRandom.hex(4)}"
      }
    )
  end
end
```

### After Model Update

```ruby
class Post < ApplicationRecord
  after_commit :purge_cdn_cache, on: [:update, :destroy]

  private

  def purge_cdn_cache
    CloudflareCache.purge("https://myapp.com/posts/#{id}")
  end
end
```

## Full Page Caching

### Rack::Cache

```ruby
# Gemfile
gem "rack-cache"
```

```ruby
# config/environments/production.rb
config.action_dispatch.rack_cache = true
config.cache_store = :redis_cache_store, { url: ENV["REDIS_URL"] }
```

### Page Cache Headers

```ruby
class PagesController < ApplicationController
  def home
    @posts = Post.published.limit(10)

    fresh_when(
      etag: @posts,
      last_modified: @posts.maximum(:updated_at),
      public: true
    )

    expires_in 5.minutes, public: true
  end
end
```

## Asset Fingerprinting

### Rails Defaults

```ruby
# config/environments/production.rb
config.assets.digest = true  # Default in Rails 8

# Generates: application-abc123.css
# Allows cache-forever headers
```

### CDN-Friendly Asset URLs

```erb
<!-- Uses asset_host automatically -->
<%= stylesheet_link_tag "application" %>
<!-- Output: https://cdn.myapp.com/assets/application-abc123.css -->
```

## Multi-CDN Setup

```ruby
# config/environments/production.rb

# Primary CDN
config.action_controller.asset_host = Proc.new { |source|
  if source.ends_with?(".js", ".css")
    "https://static.myapp.com"  # CloudFront for static
  else
    "https://cdn.myapp.com"     # Cloudflare for images
  end
}
```

## Monitoring

### Cache Hit Ratio

```ruby
# Track via CDN analytics or custom headers
class ApplicationController < ActionController::Base
  after_action :track_cache_status

  private

  def track_cache_status
    cache_status = request.headers["CF-Cache-Status"] || "DYNAMIC"
    Rails.logger.info("CDN Cache Status: #{cache_status}")
  end
end
```

### Cloudflare Analytics

Access via Cloudflare Dashboard > Analytics > Caching

### CloudFront Reports

Access via AWS Console > CloudFront > Reports & Analytics

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No cache headers | CDN can't cache | Set Cache-Control |
| Caching authenticated pages | Data leakage | Bypass cache for auth |
| No invalidation strategy | Stale content | Implement purge mechanism |
| Caching error pages | Persistent errors | Short TTL for errors |
| Missing Vary header | Wrong cached content | Set Vary: Accept-Encoding |

## Related Files

- [solid-cache.md](./solid-cache.md): Application caching
- [redis.md](./redis.md): Redis caching
- [../storage/cloudflare-r2.md](../storage/cloudflare-r2.md): R2 storage

## References

- [Cloudflare Caching](https://developers.cloudflare.com/cache/)
- [CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [Rails Caching Guide](https://guides.rubyonrails.org/caching_with_rails.html)
- [HTTP Caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
