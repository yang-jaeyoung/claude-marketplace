---
description: Solid Queue, Sidekiq 백그라운드 작업 가이드.
argument-hint: "[job_type]"
allowed-tools: ["Read", "Glob", "Grep"]
---

# /rails8-hotwire:rails8-background - Background Jobs

백그라운드 작업 처리를 안내합니다.

## Topics

1. **Solid Queue** - Rails 8 기본 (Redis 불필요)
2. **Sidekiq** - Redis 기반 고성능
3. **작업 스케줄링** - 반복 작업
4. **에러 처리** - 재시도 전략

## Knowledge Loading

- `knowledge/background/INDEX.md` - 백그라운드 전체 가이드

## Key Patterns

### Solid Queue Job

```ruby
class SendEmailJob < ApplicationJob
  queue_as :default

  def perform(user_id)
    user = User.find(user_id)
    UserMailer.welcome(user).deliver_now
  end
end

# Usage
SendEmailJob.perform_later(user.id)
```

### Scheduled Jobs

```ruby
# config/recurring.yml
production:
  daily_cleanup:
    class: CleanupJob
    schedule: every day at 3am
```

## Related

- `/rails8-hotwire:solid-setup` - Solid Trifecta 설정
- `/rails8-hotwire:rails8-deploy` - 배포 가이드
