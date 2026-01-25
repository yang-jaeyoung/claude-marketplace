# File Upload System

## Overview

Production-ready file upload with ActiveStorage, direct uploads to cloud storage, image processing with variants, and progress tracking.

## Prerequisites

- [core/gems](../../core/gems.md): ActiveStorage, image_processing
- [deploy/docker](../../deploy/docker.md): Image processing dependencies
- [hotwire/stimulus](../../hotwire/stimulus.md): Upload UI

## Quick Start

```bash
rails active_storage:install
rails db:migrate

# Gemfile
gem "image_processing"
gem "aws-sdk-s3"
```

## Implementation

### ActiveStorage Configuration

```ruby
# config/storage.yml
amazon:
  service: S3
  access_key_id: <%= Rails.application.credentials.dig(:aws, :access_key_id) %>
  secret_access_key: <%= Rails.application.credentials.dig(:aws, :secret_access_key) %>
  region: us-east-1
  bucket: your-bucket

# app/models/user.rb
class User < ApplicationRecord
  has_one_attached :avatar do |attachable|
    attachable.variant :thumb, resize_to_limit: [100, 100]
    attachable.variant :medium, resize_to_limit: [300, 300]
  end

  validates :avatar, content_type: ['image/png', 'image/jpg'],
                     size: { less_than: 5.megabytes }
end
```

### Direct Upload

```erb
<%= form_with model: @user do |f| %>
  <%= f.file_field :avatar, direct_upload: true, accept: "image/*" %>
  <%= f.submit %>
<% end %>
```

### Image Variants

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  has_one_attached :cover_image do |attachable|
    attachable.variant :hero, resize_to_limit: [1200, 600]
  end
end

# View
<%= image_tag @post.cover_image.variant(:hero) %>
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Storing files in DB | Database bloat | Use cloud storage |
| No file type validation | Security risk | Validate content_type |
| Synchronous processing | Slow uploads | Use direct upload |

## Related Skills

- [hotwire/stimulus](../../hotwire/stimulus.md)
- [background/solid-queue](../../background/solid-queue.md)

## References

- [ActiveStorage Guide](https://guides.rubyonrails.org/active_storage_overview.html)
