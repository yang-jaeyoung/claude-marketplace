---
description: Devise, Pundit, OAuth 인증/인가 가이드.
argument-hint: "[auth_type]"
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
---

# /rails8-hotwire:rails8-auth - Authentication & Authorization

인증과 인가 패턴을 안내합니다.

## Topics

1. **Rails 8 기본 인증** - bin/rails generate authentication
2. **Devise** - 완전한 인증 솔루션
3. **Pundit** - 정책 기반 인가
4. **OAuth** - Google, GitHub 소셜 로그인

## Knowledge Loading

- `knowledge/auth/devise/setup.md` - Devise 설정
- `knowledge/auth/authorization/pundit.md` - Pundit 설정

## Quick Setup

### Rails 8 Built-in Auth

```bash
bin/rails generate authentication
bin/rails db:migrate
```

### Devise Setup

```bash
bundle add devise
rails generate devise:install
rails generate devise User
rails db:migrate
```

### Pundit Policy

```ruby
class PostPolicy < ApplicationPolicy
  def update?
    user == record.user
  end

  def destroy?
    user == record.user || user.admin?
  end
end
```

## Related

- `/rails8-hotwire:auth-setup` - 인증 설정 마법사
- `/rails8-hotwire:rails8-controllers` - 컨트롤러 패턴
