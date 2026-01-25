---
description: 인증 시스템을 자동으로 설정합니다.
argument-hint: "[devise|builtin] [--oauth google,github]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
context: fork
---

# /rails8-hotwire:auth-setup - Authentication Setup Wizard

인증 시스템을 자동으로 설정합니다.

## Options

- **builtin** - Rails 8 기본 인증 (기본값)
- **devise** - Devise 완전 설정
- **--oauth** - OAuth 프로바이더 추가

## What It Sets Up

### Rails 8 Built-in
- User model with has_secure_password
- Sessions controller
- Authentication concern

### Devise
- User model with Devise modules
- Devise views (Tailwind 스타일)
- Turbo 호환 설정

### OAuth (optional)
- OmniAuth 설정
- 프로바이더별 콜백

## Example

```
/rails8-hotwire:auth-setup devise --oauth google,github
```

## Output

- User 모델 및 마이그레이션
- 인증 컨트롤러
- 로그인/회원가입 뷰
- Pundit 정책 (선택시)
