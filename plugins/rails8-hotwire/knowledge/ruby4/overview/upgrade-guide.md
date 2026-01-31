# Ruby 3.x to 4.0 Upgrade Guide / 업그레이드 가이드

> This guide covers the migration process from Ruby 3.x to Ruby 4.0 for Rails 8 applications.
> 이 가이드는 Rails 8 애플리케이션을 위한 Ruby 3.x에서 4.0으로의 마이그레이션을 다룹니다.

## Prerequisites / 사전 요구사항

| Component | Minimum Version |
|-----------|-----------------|
| Ruby | 3.2.0 (for upgrade) |
| Rails | 8.0.0 or later |
| Bundler | 4.0.0 (included with Ruby 4.0) |
| RubyGems | 4.0.0 (included with Ruby 4.0) |

## Step-by-Step Upgrade / 단계별 업그레이드

### Step 1: Check Current Ruby Version / 현재 Ruby 버전 확인

```bash
ruby -v
# ruby 3.3.0 (2023-12-25 revision 5124f9ac75) [x86_64-darwin24]
```

### Step 2: Update Ruby Version Manager / Ruby 버전 관리자 업데이트

**rbenv:**
```bash
brew upgrade rbenv ruby-build
# or
git -C ~/.rbenv/plugins/ruby-build pull
```

**rvm:**
```bash
rvm get stable
```

**asdf:**
```bash
asdf plugin update ruby
```

### Step 3: Install Ruby 4.0 / Ruby 4.0 설치

**rbenv:**
```bash
rbenv install 4.0.1
rbenv local 4.0.1
```

**rvm:**
```bash
rvm install 4.0.1
rvm use 4.0.1
```

**asdf:**
```bash
asdf install ruby 4.0.1
asdf local ruby 4.0.1
```

### Step 4: Update Gemfile / Gemfile 업데이트

```ruby
# Gemfile
ruby "4.0.1"

# or with version constraint
ruby ">= 4.0.0"
```

### Step 5: Run Bundle Install / Bundle Install 실행

```bash
bundle install

# If issues occur, try:
bundle update --bundler
bundle install
```

### Step 6: Run Tests / 테스트 실행

```bash
bundle exec rspec
# or
bundle exec rails test
```

## Breaking Changes Checklist / 주요 변경사항 체크리스트

### 1. Ractor API Changes / Ractor API 변경

**Before (Ruby 3.x):**
```ruby
r = Ractor.new do
  Ractor.yield 42
end
value = r.take
```

**After (Ruby 4.0):**
```ruby
port = Ractor::Port.new
r = Ractor.new(port) do |p|
  p << 42
end
value = port.receive
```

### 2. Splat on nil / nil Splat 연산

**Before (Ruby 3.x):**
```ruby
def method(*args)
  args
end
method(*nil)  #=> [] (called nil.to_a)
```

**After (Ruby 4.0):**
```ruby
method(*nil)  #=> NoMethodError
# Fix: Use explicit empty array
method(*nil.to_a)  # or method()
```

### 3. Kernel#open with Pipe / Kernel#open 파이프

**Before (Ruby 3.x):**
```ruby
output = open("| ls -la").read
```

**After (Ruby 4.0):**
```ruby
output = IO.popen("ls -la") { |io| io.read }
```

### 4. Set and Pathname requires / Set, Pathname require

**Before (Ruby 3.x):**
```ruby
require 'set'
require 'pathname'

set = Set.new([1, 2, 3])
path = Pathname.new("/home")
```

**After (Ruby 4.0):**
```ruby
# No require needed (but still works for backward compatibility)
set = Set[1, 2, 3]
path = Pathname("/home")
```

### 5. Process::Status Methods / Process::Status 메서드

**Removed Methods:**
```ruby
# These no longer work
status = $?
status & 0xFF     # Removed
status >> 8       # Removed

# Use instead
status.exitstatus
status.termsig
status.stopsig
```

## Common Issues and Solutions / 자주 발생하는 문제와 해결책

### Issue 1: Gem Compatibility / 젬 호환성 문제

```bash
# Error: Some gems may not support Ruby 4.0 yet
bundle install
# Bundler could not find compatible versions for gem "some-gem"
```

**Solution:**
```ruby
# Gemfile - Try the latest version
gem 'some-gem', github: 'owner/some-gem', branch: 'main'

# Or use a fork with Ruby 4.0 support
gem 'some-gem', github: 'your-fork/some-gem', branch: 'ruby-4-support'
```

### Issue 2: Native Extension Build Failures / 네이티브 확장 빌드 실패

```bash
# Error: Gem::Ext::BuildError
```

**Solution:**
```bash
# Update development dependencies
# macOS
xcode-select --install
brew install openssl readline

# Linux (Ubuntu/Debian)
sudo apt-get install build-essential libssl-dev libreadline-dev zlib1g-dev
```

### Issue 3: ZJIT Build Issues / ZJIT 빌드 문제

```bash
# Error: ZJIT requires Rust 1.85.0 or later
```

**Solution:**
```bash
# Install or update Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup update
```

### Issue 4: Deprecated Method Warnings / 사용 중단 메서드 경고

```ruby
# Warning: ObjectSpace._id2ref is deprecated
```

**Solution:**
Review and update code that uses deprecated methods:
```ruby
# Replace deprecated patterns
# Instead of ObjectSpace._id2ref(id)
# Use WeakRef or other alternatives
```

## Rails-Specific Considerations / Rails 관련 고려사항

### Active Record

No breaking changes for most applications. Test thoroughly:

```bash
bundle exec rails db:migrate
bundle exec rails db:test:prepare
bundle exec rspec spec/models
```

### Action Pack

Test controllers and request specs:

```bash
bundle exec rspec spec/controllers
bundle exec rspec spec/requests
```

### Active Job / Solid Queue

Background jobs should work without changes:

```bash
bundle exec rspec spec/jobs
```

### Hotwire / Turbo

No Ruby 4.0 specific changes. Test integration:

```bash
bundle exec rspec spec/system
```

## Rollback Plan / 롤백 계획

If issues arise, rollback to Ruby 3.x:

```bash
# rbenv
rbenv local 3.3.0

# rvm
rvm use 3.3.0

# asdf
asdf local ruby 3.3.0

# Reinstall gems
bundle install
```

## Verification Checklist / 검증 체크리스트

- [ ] All tests passing
- [ ] Application boots successfully
- [ ] Key features work in development
- [ ] Background jobs execute correctly
- [ ] Real-time features (Action Cable) work
- [ ] Third-party integrations function
- [ ] Performance is acceptable

## See Also / 참고

- [What's New in Ruby 4.0](whats-new.md)
- [Rails Compatibility](compatibility.md)
- [Removed Features](../breaking-changes/removed-features.md)
- [Deprecations](../breaking-changes/deprecations.md)
