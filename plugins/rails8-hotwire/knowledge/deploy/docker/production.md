# Production Docker Optimizations

## Overview

Production Docker images require security hardening, size optimization, and performance tuning beyond development configurations.

## When to Use

- When deploying to production
- When optimizing image size
- When hardening container security
- When improving build/deploy speed

## Quick Start

### Optimized Production Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.4
ARG RUBY_VERSION=3.3.0
FROM ruby:$RUBY_VERSION-slim AS base

WORKDIR /rails

ENV RAILS_ENV="production" \
    BUNDLE_DEPLOYMENT="1" \
    BUNDLE_PATH="/usr/local/bundle" \
    BUNDLE_WITHOUT="development:test" \
    BUNDLE_JOBS=4 \
    BUNDLE_RETRY=3

# Build stage
FROM base AS build

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential \
    git \
    libjemalloc-dev \
    libpq-dev \
    pkg-config

# Install gems with caching
COPY Gemfile Gemfile.lock ./
RUN --mount=type=cache,target=/root/.bundle/cache \
    bundle install && \
    rm -rf ~/.bundle/ "${BUNDLE_PATH}"/ruby/*/cache

COPY . .

RUN bundle exec bootsnap precompile app/ lib/
RUN SECRET_KEY_BASE_DUMMY=1 ./bin/rails assets:precompile

# Clean up unnecessary files
RUN rm -rf node_modules tmp/cache vendor/bundle test spec .git

# Final stage
FROM base

# Install minimal runtime dependencies
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    curl \
    libjemalloc2 \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy built artifacts
COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /rails /rails

# Security: non-root user
RUN useradd rails --create-home --shell /bin/bash && \
    chown -R rails:rails db log storage tmp
USER rails:rails

# Performance: jemalloc
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2
ENV MALLOC_CONF=dirty_decay_ms:1000,narenas:2,background_thread:true

ENTRYPOINT ["/rails/bin/docker-entrypoint"]
EXPOSE 3000
CMD ["./bin/thrust", "./bin/rails", "server"]
```

## Size Optimization

### Layer Ordering (Cache Efficiency)

```dockerfile
# Bad: Changes to any file invalidate gem cache
COPY . .
RUN bundle install

# Good: Gems cached until Gemfile changes
COPY Gemfile Gemfile.lock ./
RUN bundle install
COPY . .
```

### Slim Base Images

| Image | Size | Use Case |
|-------|------|----------|
| `ruby:3.3.0` | ~900MB | Development |
| `ruby:3.3.0-slim` | ~180MB | Production |
| `ruby:3.3.0-alpine` | ~80MB | Minimal (compatibility issues) |

### Remove Build Artifacts

```dockerfile
FROM build AS cleanup

# Remove development/test gems
RUN bundle config set --local without 'development test' && \
    bundle clean --force

# Remove gem cache
RUN rm -rf "${BUNDLE_PATH}"/ruby/*/cache

# Remove unnecessary files
RUN rm -rf \
    .git \
    .github \
    .gitignore \
    node_modules \
    test \
    spec \
    coverage \
    tmp/cache \
    vendor/bundle \
    log/*.log \
    *.md \
    Makefile \
    Rakefile
```

### .dockerignore Optimization

```dockerignore
# .dockerignore
.git
.github
.gitignore
.dockerignore
Dockerfile*
docker-compose*

# Development files
.env*
.kamal/secrets*
.rspec
.rubocop*
Guardfile

# Test/coverage
test/
spec/
coverage/
tmp/

# Documentation
*.md
docs/
CHANGELOG
LICENSE

# Dependencies (reinstalled in container)
vendor/bundle
node_modules

# Generated files
log/*.log
public/assets
public/packs
storage/

# OS/Editor
.DS_Store
.idea/
.vscode/
*.swp
```

## Security Hardening

### Non-root User

```dockerfile
# Create user and group
RUN groupadd --gid 1000 rails && \
    useradd --uid 1000 --gid rails --shell /bin/bash --create-home rails

# Set ownership
RUN chown -R rails:rails /rails

# Switch to non-root
USER rails:rails
```

### Read-only Filesystem

```yaml
# config/deploy.yml (Kamal)
servers:
  web:
    hosts:
      - 192.168.1.1
    options:
      read-only: true
      tmpfs:
        - /rails/tmp
        - /rails/log
```

### Security Scanning

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push]

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          format: table
          exit-code: 1
          severity: CRITICAL,HIGH
```

### Minimal Capabilities

```yaml
# config/deploy.yml (Kamal)
servers:
  web:
    options:
      cap-drop: ALL
      cap-add:
        - NET_BIND_SERVICE
      security-opt:
        - no-new-privileges:true
```

## Memory Optimization

### jemalloc Configuration

```dockerfile
# Install jemalloc
RUN apt-get install -y libjemalloc2

# Enable jemalloc
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2
ENV MALLOC_CONF=dirty_decay_ms:1000,narenas:2,background_thread:true
```

### YJIT (Ruby 3.2+)

```dockerfile
ENV RUBY_YJIT_ENABLE=1
```

### Memory Limits

```yaml
# config/deploy.yml
servers:
  web:
    options:
      memory: 1g
      memory-swap: 1g  # Disable swap
```

## Build Speed Optimization

### BuildKit Cache Mounts

```dockerfile
# syntax=docker/dockerfile:1.4

# Cache apt packages
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y ...

# Cache bundler
RUN --mount=type=cache,target=/root/.bundle/cache \
    bundle install

# Cache node modules
RUN --mount=type=cache,target=/rails/node_modules \
    yarn install
```

### GitHub Actions Cache

```yaml
# .github/workflows/build.yml
jobs:
  build:
    steps:
      - uses: docker/setup-buildx-action@v3

      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: myapp:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Parallel Builds

```dockerfile
# Parallel gem installation
ENV BUNDLE_JOBS=4
ENV BUNDLE_RETRY=3

# Parallel asset compilation
ENV RAILS_ASSETS_PRECOMPILE_PARALLEL=true
```

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/up || exit 1
```

## Multi-Platform Builds

```bash
# Build for multiple architectures
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  -t myapp:latest .
```

```yaml
# config/deploy.yml (Kamal)
builder:
  multiarch: true
  # Or specify platforms
  platforms:
    - linux/amd64
    - linux/arm64
```

## Image Size Comparison

| Optimization | Size | Savings |
|--------------|------|---------|
| Default (ruby:3.3.0) | ~1.2GB | Baseline |
| Slim base | ~400MB | -66% |
| Multi-stage | ~300MB | -75% |
| + Cleanup | ~250MB | -79% |
| Alpine base | ~150MB | -87% |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Running as root | Security risk | Use non-root user |
| Single stage | Large images | Multi-stage builds |
| No .dockerignore | Slow builds | Add comprehensive ignore |
| Dev deps in prod | Bloated image | BUNDLE_WITHOUT |
| No health check | Silent failures | Add HEALTHCHECK |

## Related Files

- [Dockerfile](./Dockerfile): Base Dockerfile
- [multi-stage.md](./multi-stage.md): Multi-stage patterns
- [../kamal/configuration.md](../kamal/configuration.md): Kamal deployment

## References

- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [BuildKit](https://docs.docker.com/build/buildkit/)
- [Container Security](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
