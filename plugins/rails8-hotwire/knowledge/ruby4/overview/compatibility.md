# Ruby 4.0 and Rails Compatibility / 호환성 정보

> Compatibility information for Ruby 4.0 with Rails and popular gems.
> Ruby 4.0과 Rails 및 주요 젬들의 호환성 정보입니다.

## Rails Version Compatibility / Rails 버전 호환성

| Rails Version | Minimum Ruby | Maximum Ruby | Ruby 4.0 Status |
|---------------|--------------|--------------|-----------------|
| 8.1.x | 3.2.0 | - | ✅ Recommended |
| 8.0.x | 3.2.0 | - | ✅ Compatible |
| 7.2.x | 3.2.0 | - | ⚠️ Test First |
| 7.1.x | 3.1.0 | - | ⚠️ Test First |
| 7.0.x | 3.0.0 | - | ❌ Not Recommended |
| 6.1.x | 2.5.0 | 3.2.x | ❌ Not Supported |

## Ruby Version Support Matrix / Ruby 버전 지원 매트릭스

| Ruby Version | Status | End of Life |
|--------------|--------|-------------|
| 4.0.x | Current | - |
| 3.4.x | Maintained | TBD |
| 3.3.x | Maintained | TBD |
| 3.2.x | Security | 2026-03-31 |
| 3.1.x | EOL | 2025-03-31 |
| 3.0.x | EOL | 2024-03-31 |

## Popular Gems Compatibility / 주요 젬 호환성

### Authentication / 인증

| Gem | Version | Ruby 4.0 | Notes |
|-----|---------|----------|-------|
| devise | 4.10+ | ✅ | Full support |
| omniauth | 2.2+ | ✅ | Full support |
| rodauth | 2.35+ | ✅ | Full support |
| sorcery | 0.18+ | ⚠️ | Check latest |

### Background Jobs / 백그라운드 작업

| Gem | Version | Ruby 4.0 | Notes |
|-----|---------|----------|-------|
| solid_queue | 1.2+ | ✅ | Rails 8 default |
| sidekiq | 7.3+ | ✅ | Full support |
| good_job | 4.2+ | ✅ | Full support |
| delayed_job | 4.1+ | ⚠️ | Test first |

### Testing / 테스트

| Gem | Version | Ruby 4.0 | Notes |
|-----|---------|----------|-------|
| rspec | 3.14+ | ✅ | Full support |
| rspec-rails | 7.0+ | ✅ | Full support |
| factory_bot | 6.5+ | ✅ | Full support |
| capybara | 3.40+ | ✅ | Full support |
| selenium-webdriver | 4.25+ | ✅ | Full support |

### Database / 데이터베이스

| Gem | Version | Ruby 4.0 | Notes |
|-----|---------|----------|-------|
| pg | 1.6+ | ✅ | Full support |
| mysql2 | 0.5.6+ | ✅ | Full support |
| sqlite3 | 2.4+ | ✅ | Full support |
| redis | 5.3+ | ✅ | Full support |

### Deployment / 배포

| Gem | Version | Ruby 4.0 | Notes |
|-----|---------|----------|-------|
| kamal | 2.4+ | ✅ | Rails 8 default |
| capistrano | 3.19+ | ✅ | Full support |
| puma | 6.5+ | ✅ | Full support |

### Asset Pipeline / 에셋 파이프라인

| Gem | Version | Ruby 4.0 | Notes |
|-----|---------|----------|-------|
| propshaft | 1.1+ | ✅ | Rails 8 default |
| cssbundling-rails | 1.4+ | ✅ | Full support |
| jsbundling-rails | 1.3+ | ✅ | Full support |
| importmap-rails | 2.1+ | ✅ | Full support |

### Hotwire / 핫와이어

| Gem | Version | Ruby 4.0 | Notes |
|-----|---------|----------|-------|
| turbo-rails | 2.0+ | ✅ | Full support |
| stimulus-rails | 1.3+ | ✅ | Full support |

## RubyGems & Bundler 4.0 / RubyGems & Bundler 4.0

Ruby 4.0 includes updated versions of RubyGems and Bundler.

### RubyGems 4.0 Changes

```bash
# Removed command (use alternatives)
gem query        # ❌ Removed
gem search       # ✅ Use instead
gem list         # ✅ Use instead
```

### Bundler 4.0 Changes

```bash
# Not recommended (ambiguous)
bundle           # ⚠️ Deprecated standalone use

# Use explicit commands
bundle install   # ✅ Recommended
bundle update    # ✅ Recommended
bundle exec      # ✅ Recommended
```

## Platform Support / 플랫폼 지원

### Fully Supported Platforms / 완전 지원 플랫폼

| Platform | Architecture | ZJIT Support |
|----------|--------------|--------------|
| macOS | ARM64 (Apple Silicon) | ✅ |
| macOS | x86_64 (Intel) | ✅ |
| Linux | x86_64 | ✅ |
| Linux | ARM64 | ✅ |

### Limited Support / 제한적 지원

| Platform | Architecture | ZJIT Support | Notes |
|----------|--------------|--------------|-------|
| Windows | x86_64 | ⚠️ | Experimental |
| FreeBSD | x86_64 | ⚠️ | Community support |

## Docker Images / 도커 이미지

### Official Ruby 4.0 Images

```dockerfile
# Alpine (smallest)
FROM ruby:4.0-alpine

# Debian (most compatible)
FROM ruby:4.0

# Slim Debian (balanced)
FROM ruby:4.0-slim
```

### Rails 8 with Ruby 4.0

```dockerfile
# Dockerfile
FROM ruby:4.0-slim

# Install dependencies
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential git libpq-dev

# Set working directory
WORKDIR /app

# Install gems
COPY Gemfile Gemfile.lock ./
RUN bundle install

# Copy application
COPY . .

# Precompile assets
RUN ./bin/rails assets:precompile

# Start server
CMD ["./bin/rails", "server", "-b", "0.0.0.0"]
```

## CI/CD Configuration / CI/CD 설정

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Ruby 4.0
      uses: ruby/setup-ruby@v1
      with:
        ruby-version: '4.0'
        bundler-cache: true

    - name: Run tests
      run: bundle exec rspec
```

### GitLab CI

```yaml
# .gitlab-ci.yml
image: ruby:4.0

stages:
  - test

test:
  stage: test
  script:
    - bundle install
    - bundle exec rspec
  cache:
    paths:
      - vendor/bundle
```

## Checking Compatibility / 호환성 확인

### Before Upgrading

```bash
# Check gem compatibility
bundle outdated

# Check for deprecated APIs
bundle exec ruby-deprecation-toolkit

# Run full test suite
bundle exec rspec
```

### After Upgrading

```bash
# Verify Ruby version
ruby -v

# Check for warnings
RUBYOPT=-W:all bundle exec rails server

# Run tests with verbose warnings
bundle exec rspec --warnings
```

## See Also / 참고

- [Upgrade Guide](upgrade-guide.md)
- [What's New in Ruby 4.0](whats-new.md)
- [Breaking Changes](../breaking-changes/removed-features.md)
