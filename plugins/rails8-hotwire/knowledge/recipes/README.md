# Rails 8 + Hotwire Recipes

Production-ready combination recipes for Rails 8 applications. Each recipe combines multiple skills into complete, tested features.

## Recipe Categories

### SaaS (3 recipes)

| Recipe | Description | Key Technologies |
|--------|-------------|------------------|
| [Multi-Tenant](saas/multi-tenant.md) | Complete multi-tenant architecture with subdomain routing and data isolation | acts_as_tenant, subdomain routing, row-level security |
| [Subscription](saas/subscription.md) | Stripe/Lemon Squeezy subscription billing with webhooks and customer portal | Stripe, stripe_event, webhooks, billing portal |
| [Onboarding](saas/onboarding.md) | Multi-step onboarding wizard with progress tracking and email sequences | Turbo Frames, JSONB data, Solid Queue |

### Features (6 recipes)

| Recipe | Description | Key Technologies |
|--------|-------------|------------------|
| [Comments](features/comments.md) | Threaded comment system with reactions and @mentions | ancestry gem, Turbo Streams, real-time updates |
| [Notifications](features/notifications.md) | In-app notifications with email digests and preferences | noticed gem, Turbo Streams, background jobs |
| [Search](features/search.md) | Progressive search from Ransack to Meilisearch | Ransack, pg_search, Meilisearch, instant search |
| [File Upload](features/file-upload.md) | Direct uploads with image processing and cloud storage | ActiveStorage, image_processing, AWS S3 |
| [Export/Import](features/export-import.md) | Async CSV/Excel export and batch import | CSV, background jobs, validation |
| [Dashboard](features/dashboard.md) | Real-time dashboard with charts and caching | Chartkick, groupdate, Russian doll caching |

### Integrations (4 recipes)

| Recipe | Description | Key Technologies |
|--------|-------------|------------------|
| [Lemon Squeezy](integrations/lemon-squeezy.md) | Payment processing integration | Lemon Squeezy API, webhooks |
| [Resend](integrations/resend.md) | Transactional email service | Resend API, email templates |
| [Cloudflare](integrations/cloudflare.md) | R2 storage and CDN integration | Cloudflare R2, CDN, caching |
| [Supabase](integrations/supabase.md) | Database and authentication | Supabase Auth, PostgreSQL |

### Full-Stack Apps (3 recipes)

| Recipe | Description | Key Technologies |
|--------|-------------|------------------|
| [Blog](full-stack/blog.md) | Complete blogging platform with comments, tags, and RSS | Posts, comments, tagging, RSS feed |
| [Todo](full-stack/todo.md) | Todo app with drag-drop and real-time updates | acts_as_list, SortableJS, Turbo Streams |
| [CRM](full-stack/crm.md) | Customer relationship management with pipeline | Contacts, deals, activities, kanban view |

## Usage Patterns

### Combine Recipes for Complete Applications

**SaaS MVP**
```
multi-tenant + subscription + onboarding + dashboard
```

**Community Platform**
```
comments + notifications + search + file-upload
```

**Content Management**
```
blog + comments + search + file-upload
```

**Business Application**
```
crm + notifications + export-import + dashboard
```

## Quick Start Guide

1. **Choose your recipes** based on features needed
2. **Install dependencies** from each recipe's Quick Start section
3. **Follow implementation steps** in order (models → controllers → views)
4. **Run tests** to verify integration
5. **Customize** for your specific needs

## Common Patterns

### Authentication Required
Most recipes assume authentication is set up. Use:
- Built-in Rails authentication (`bin/rails generate authentication`)
- Devise gem
- Custom authentication

### Real-time Updates
Recipes using Turbo Streams require:
- Action Cable configured
- `turbo_stream_from` in views
- `broadcasts_to` in models

### Background Jobs
Recipes with async processing require:
- Solid Queue (Rails 8 default)
- Or alternative: Sidekiq, Delayed Job

### Cloud Storage
File upload recipes work with:
- AWS S3
- Google Cloud Storage
- Cloudflare R2
- Local storage (development)

## Anti-Pattern Reference

Common mistakes across all recipes:

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No error handling | Silent failures | Rescue errors, log, notify |
| Missing indexes | Slow queries | Index foreign keys, frequently queried columns |
| N+1 queries | Poor performance | Use `includes`, `eager_load`, or `preload` |
| No caching | Slow page loads | Fragment caching, Russian doll caching |
| Synchronous operations | Slow requests | Use background jobs for heavy work |
| No pagination | Memory issues | Kaminari, pagy, or Rails built-in |
| Hardcoded config | Not portable | Use Rails credentials or ENV vars |

## Testing Strategy

Each recipe includes:
- **Model specs**: Business logic validation
- **Request specs**: Integration testing
- **System specs**: End-to-end user flows

Use RSpec or Minitest based on preference.

## Production Checklist

Before deploying recipes to production:

- [ ] Run full test suite
- [ ] Configure production credentials
- [ ] Set up error monitoring (Sentry, Honeybadger)
- [ ] Enable caching in production
- [ ] Configure CDN for assets
- [ ] Set up database backups
- [ ] Configure logging (Lograge)
- [ ] Set up performance monitoring (Skylight, Scout)
- [ ] Review security (Brakeman scan)
- [ ] Load test critical paths

## Contributing

These recipes are living documentation. Improvements welcome:

1. Add new recipes for common patterns
2. Update recipes with Rails 8 best practices
3. Add more comprehensive test examples
4. Expand anti-pattern sections

## Further Reading

- [Rails Guides](https://guides.rubyonrails.org/)
- [Hotwire Handbook](https://turbo.hotwired.dev/handbook/introduction)
- [Rails 8 Release Notes](https://edgeguides.rubyonrails.org/8_0_release_notes.html)
- [Solid Queue Guide](https://github.com/rails/solid_queue)
