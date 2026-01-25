# Active Storage Configuration

## Overview

Active Storage handles file uploads in Rails, supporting local disk, cloud storage (S3, GCS, Azure), and direct uploads. Rails 8 includes improved direct upload handling and variant processing.

## When to Use

- When handling file uploads
- When storing user-generated content
- When processing images/documents
- When configuring cloud storage

## Quick Start

### Installation

```bash
# Already included in Rails 8, but to set up:
bin/rails active_storage:install
bin/rails db:migrate
```

### Basic Configuration

```yaml
# config/storage.yml
local:
  service: Disk
  root: <%= Rails.root.join("storage") %>

production:
  service: S3
  access_key_id: <%= Rails.application.credentials.dig(:aws, :access_key_id) %>
  secret_access_key: <%= Rails.application.credentials.dig(:aws, :secret_access_key) %>
  region: us-east-1
  bucket: myapp-production
```

```ruby
# config/environments/production.rb
config.active_storage.service = :production
```

## Model Attachments

### Single Attachment

```ruby
class User < ApplicationRecord
  has_one_attached :avatar

  # With specific service
  has_one_attached :avatar, service: :cloudflare
end
```

### Multiple Attachments

```ruby
class Post < ApplicationRecord
  has_many_attached :images
end
```

### Attachment Validation

```ruby
class User < ApplicationRecord
  has_one_attached :avatar

  validates :avatar, content_type: [:png, :jpg, :jpeg, :webp],
                     size: { less_than: 5.megabytes }
end

# Using activestorage-validator gem
class Document < ApplicationRecord
  has_one_attached :file

  validates :file, attached: true,
                   content_type: ['application/pdf'],
                   size: { less_than: 10.megabytes }
end
```

## Direct Uploads

### JavaScript Setup

```erb
<!-- app/views/posts/_form.html.erb -->
<%= form_with model: @post do |f| %>
  <%= f.file_field :images, multiple: true, direct_upload: true %>
<% end %>
```

### Stimulus Controller

```javascript
// app/javascript/controllers/upload_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "progress"]

  connect() {
    this.inputTarget.addEventListener("direct-upload:start", (event) => {
      this.progressTarget.hidden = false
    })

    this.inputTarget.addEventListener("direct-upload:progress", (event) => {
      const { progress } = event.detail
      this.progressTarget.value = progress
    })

    this.inputTarget.addEventListener("direct-upload:end", (event) => {
      this.progressTarget.hidden = true
    })
  }
}
```

```erb
<div data-controller="upload">
  <%= f.file_field :images, multiple: true, direct_upload: true,
      data: { upload_target: "input" } %>
  <progress data-upload-target="progress" max="100" hidden></progress>
</div>
```

### CORS Configuration (S3)

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://myapp.com"],
      "AllowedMethods": ["PUT"],
      "AllowedHeaders": ["Origin", "Content-Type", "Content-MD5", "Content-Disposition"],
      "MaxAgeSeconds": 3600,
      "ExposeHeaders": ["Origin", "Content-Type", "Content-MD5", "Content-Disposition"]
    }
  ]
}
```

## Image Variants

### Basic Variants

```erb
<%= image_tag user.avatar.variant(resize_to_limit: [100, 100]) %>
<%= image_tag user.avatar.variant(resize_to_fill: [200, 200]) %>
<%= image_tag user.avatar.variant(resize_to_fit: [300, 300]) %>
```

### Named Variants

```ruby
class User < ApplicationRecord
  has_one_attached :avatar do |attachable|
    attachable.variant :thumb, resize_to_limit: [100, 100]
    attachable.variant :medium, resize_to_limit: [300, 300]
    attachable.variant :large, resize_to_limit: [800, 800]
  end
end
```

```erb
<%= image_tag user.avatar.variant(:thumb) %>
<%= image_tag user.avatar.variant(:medium) %>
```

### Preprocessed Variants

```ruby
class User < ApplicationRecord
  has_one_attached :avatar do |attachable|
    attachable.variant :thumb, resize_to_limit: [100, 100], preprocessed: true
  end

  after_commit :process_avatar, on: [:create, :update]

  private

  def process_avatar
    avatar.variant(:thumb).processed if avatar.attached?
  end
end
```

## Proxy Mode

### Enable Proxy

```ruby
# config/environments/production.rb
config.active_storage.resolve_model_to_route = :rails_storage_proxy
```

### CDN with Proxy

```ruby
# config/environments/production.rb
config.active_storage.resolve_model_to_route = :rails_storage_proxy

# In views, still use url_for which goes through proxy
<%= image_tag user.avatar %>
```

## Multiple Storage Services

```yaml
# config/storage.yml
local:
  service: Disk
  root: <%= Rails.root.join("storage") %>

amazon:
  service: S3
  access_key_id: <%= Rails.application.credentials.dig(:aws, :access_key_id) %>
  secret_access_key: <%= Rails.application.credentials.dig(:aws, :secret_access_key) %>
  region: us-east-1
  bucket: myapp-production

cloudflare:
  service: S3
  endpoint: https://<account_id>.r2.cloudflarestorage.com
  access_key_id: <%= Rails.application.credentials.dig(:cloudflare, :access_key_id) %>
  secret_access_key: <%= Rails.application.credentials.dig(:cloudflare, :secret_access_key) %>
  bucket: myapp-uploads
  region: auto
```

```ruby
class User < ApplicationRecord
  has_one_attached :avatar, service: :cloudflare
  has_many_attached :documents, service: :amazon
end
```

## Background Processing

### Analyze Job

```ruby
# Runs automatically after attachment
# Extracts metadata (dimensions, duration, etc.)
config.active_storage.queues.analysis = :default
```

### Mirror Job

```ruby
# For mirroring to backup storage
config.active_storage.queues.mirror = :low
```

### Purge Job

```ruby
# For deleting files
config.active_storage.queues.purge = :low
```

### Custom Processing

```ruby
class ProcessImageJob < ApplicationJob
  queue_as :default

  def perform(blob)
    blob.open do |file|
      # Custom processing
      processed = ImageProcessing::Vips
        .source(file)
        .resize_to_limit(1920, 1080)
        .saver(quality: 80)
        .call

      # Replace original
      blob.upload(processed)
    end
  end
end
```

## Metadata and Analysis

### Check Metadata

```ruby
user.avatar.metadata
# => { "identified" => true, "width" => 800, "height" => 600, "analyzed" => true }

user.avatar.blob.content_type
# => "image/jpeg"

user.avatar.blob.byte_size
# => 123456
```

### Custom Analyzers

```ruby
# config/initializers/active_storage.rb
Rails.application.config.active_storage.analyzers.prepend(MyCustomAnalyzer)
```

## Storage Cleanup

### Purge Unattached Blobs

```ruby
# config/environments/production.rb
config.active_storage.service_urls_expire_in = 1.hour

# Run cleanup job
ActiveStorage::Blob.unattached.where("created_at < ?", 1.day.ago).find_each(&:purge_later)
```

### Scheduled Cleanup

```ruby
# app/jobs/cleanup_unattached_blobs_job.rb
class CleanupUnattachedBlobsJob < ApplicationJob
  queue_as :maintenance

  def perform
    ActiveStorage::Blob.unattached.where("active_storage_blobs.created_at < ?", 2.days.ago).find_each(&:purge_later)
  end
end
```

## Docker Configuration

```dockerfile
# Dockerfile
# Install image processing libraries
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    libvips42 \
    imagemagick
```

```ruby
# config/application.rb
config.active_storage.variant_processor = :vips  # or :mini_magick
```

## Testing

```ruby
# spec/models/user_spec.rb
RSpec.describe User do
  it "attaches avatar" do
    user = User.new(name: "Test")
    user.avatar.attach(
      io: File.open(Rails.root.join("spec/fixtures/avatar.jpg")),
      filename: "avatar.jpg",
      content_type: "image/jpeg"
    )

    expect(user.avatar).to be_attached
  end
end
```

```ruby
# spec/rails_helper.rb
RSpec.configure do |config|
  config.after(:each) do
    FileUtils.rm_rf(ActiveStorage::Blob.service.root)
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Sync variant processing | Slow requests | Use preprocessed: true |
| No content type validation | Security risk | Validate content types |
| Large files without direct upload | Timeout/memory | Use direct uploads |
| Unattached blob accumulation | Storage waste | Schedule cleanup jobs |

## Related Files

- [cloudflare-r2.md](./cloudflare-r2.md): Cloudflare R2 setup
- [s3.md](./s3.md): AWS S3 configuration
- [../caching/cdn.md](../caching/cdn.md): CDN integration

## References

- [Active Storage Overview](https://guides.rubyonrails.org/active_storage_overview.html)
- [Direct Uploads](https://guides.rubyonrails.org/active_storage_overview.html#direct-uploads)
- [ImageProcessing](https://github.com/janko/image_processing)
