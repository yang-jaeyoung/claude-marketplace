# Multi-Stage Docker Builds

## Overview

Multi-stage builds create smaller, more secure production images by separating build-time dependencies from runtime dependencies.

## When to Use

- When optimizing Docker image size
- When separating build and runtime environments
- When compiling assets that need Node.js
- When including native gem extensions

## Quick Start

### Basic Multi-Stage Pattern

```dockerfile
# Stage 1: Build
FROM ruby:3.3.0-slim AS build
# Install build dependencies, gems, compile assets

# Stage 2: Runtime
FROM ruby:3.3.0-slim AS runtime
# Copy only what's needed from build stage
COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /rails /rails
```

## Complete Examples

### Rails with Import Maps (No Node.js)

```dockerfile
ARG RUBY_VERSION=3.3.0

# Base stage
FROM ruby:$RUBY_VERSION-slim AS base
WORKDIR /rails
ENV RAILS_ENV="production" \
    BUNDLE_DEPLOYMENT="1" \
    BUNDLE_PATH="/usr/local/bundle" \
    BUNDLE_WITHOUT="development:test"

# Build stage
FROM base AS build

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential \
    git \
    libpq-dev \
    pkg-config

COPY Gemfile Gemfile.lock ./
RUN bundle install && \
    rm -rf ~/.bundle/ "${BUNDLE_PATH}"/ruby/*/cache

COPY . .

RUN bundle exec bootsnap precompile app/ lib/
RUN SECRET_KEY_BASE_DUMMY=1 ./bin/rails assets:precompile

# Runtime stage
FROM base

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    curl \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /rails /rails

RUN useradd rails --create-home --shell /bin/bash && \
    chown -R rails:rails db log storage tmp
USER rails:rails

EXPOSE 3000
CMD ["./bin/thrust", "./bin/rails", "server"]
```

### Rails with Node.js Assets

```dockerfile
ARG RUBY_VERSION=3.3.0
ARG NODE_VERSION=20

# Base stage
FROM ruby:$RUBY_VERSION-slim AS base
WORKDIR /rails
ENV RAILS_ENV="production" \
    BUNDLE_DEPLOYMENT="1" \
    BUNDLE_PATH="/usr/local/bundle" \
    BUNDLE_WITHOUT="development:test"

# Node stage (for asset compilation)
FROM node:$NODE_VERSION-slim AS node

# Build stage
FROM base AS build

# Copy Node.js from node stage
COPY --from=node /usr/local/bin/node /usr/local/bin/
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
    npm install -g yarn

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential \
    git \
    libpq-dev \
    pkg-config

# Install Ruby gems
COPY Gemfile Gemfile.lock ./
RUN bundle install && \
    rm -rf ~/.bundle/ "${BUNDLE_PATH}"/ruby/*/cache

# Install Node packages
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile --production=false

COPY . .

RUN bundle exec bootsnap precompile app/ lib/
RUN SECRET_KEY_BASE_DUMMY=1 ./bin/rails assets:precompile

# Clean up node_modules (not needed at runtime)
RUN rm -rf node_modules

# Runtime stage
FROM base

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    curl \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /rails /rails

RUN useradd rails --create-home --shell /bin/bash && \
    chown -R rails:rails db log storage tmp
USER rails:rails

EXPOSE 3000
CMD ["./bin/thrust", "./bin/rails", "server"]
```

### With Multiple Database Support

```dockerfile
ARG RUBY_VERSION=3.3.0

FROM ruby:$RUBY_VERSION-slim AS base
WORKDIR /rails
ENV RAILS_ENV="production" \
    BUNDLE_DEPLOYMENT="1" \
    BUNDLE_PATH="/usr/local/bundle" \
    BUNDLE_WITHOUT="development:test"

FROM base AS build

# Install ALL database client libraries for building gems
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential \
    git \
    libpq-dev \
    libmysqlclient-dev \
    libsqlite3-dev \
    pkg-config

COPY Gemfile Gemfile.lock ./
RUN bundle install && \
    rm -rf ~/.bundle/ "${BUNDLE_PATH}"/ruby/*/cache

COPY . .
RUN bundle exec bootsnap precompile app/ lib/
RUN SECRET_KEY_BASE_DUMMY=1 ./bin/rails assets:precompile

# PostgreSQL runtime
FROM base AS production-pg

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y curl libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /rails /rails

RUN useradd rails --create-home --shell /bin/bash && \
    chown -R rails:rails db log storage tmp
USER rails:rails

EXPOSE 3000
CMD ["./bin/thrust", "./bin/rails", "server"]

# MySQL runtime
FROM base AS production-mysql

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y curl libmysqlclient21 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /rails /rails

RUN useradd rails --create-home --shell /bin/bash && \
    chown -R rails:rails db log storage tmp
USER rails:rails

EXPOSE 3000
CMD ["./bin/thrust", "./bin/rails", "server"]
```

```bash
# Build PostgreSQL variant
docker build --target production-pg -t myapp:pg .

# Build MySQL variant
docker build --target production-mysql -t myapp:mysql .
```

### Separate Build for Testing

```dockerfile
ARG RUBY_VERSION=3.3.0

FROM ruby:$RUBY_VERSION-slim AS base
WORKDIR /rails

# Development/Test stage
FROM base AS development

ENV RAILS_ENV="development" \
    BUNDLE_PATH="/usr/local/bundle"

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential \
    git \
    libpq-dev \
    curl \
    chromium \
    chromium-driver

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

EXPOSE 3000
CMD ["bin/rails", "server", "-b", "0.0.0.0"]

# Test stage
FROM development AS test

ENV RAILS_ENV="test"

RUN bundle exec rails db:prepare
CMD ["bin/rails", "test"]

# Production build stage
FROM base AS build
# ... (production build as before)

# Production runtime stage
FROM base AS production
# ... (production runtime as before)
```

```bash
# Run tests
docker build --target test -t myapp:test .
docker run myapp:test

# Build production
docker build --target production -t myapp:prod .
```

### With Asset Precompilation Cache

```dockerfile
ARG RUBY_VERSION=3.3.0

FROM ruby:$RUBY_VERSION-slim AS base
WORKDIR /rails
ENV RAILS_ENV="production" \
    BUNDLE_PATH="/usr/local/bundle"

# Gem installation stage
FROM base AS gems

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential \
    git \
    libpq-dev

COPY Gemfile Gemfile.lock ./
RUN bundle install && \
    rm -rf ~/.bundle/ "${BUNDLE_PATH}"/ruby/*/cache

# Asset compilation stage
FROM gems AS assets

COPY . .
RUN bundle exec bootsnap precompile app/ lib/
RUN SECRET_KEY_BASE_DUMMY=1 ./bin/rails assets:precompile

# Production stage
FROM base AS production

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    curl \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy gems from gems stage
COPY --from=gems /usr/local/bundle /usr/local/bundle

# Copy app with compiled assets from assets stage
COPY --from=assets /rails /rails

RUN useradd rails --create-home --shell /bin/bash && \
    chown -R rails:rails db log storage tmp
USER rails:rails

EXPOSE 3000
CMD ["./bin/thrust", "./bin/rails", "server"]
```

## Stage Dependencies

```
┌──────────────┐
│    base      │ Common settings
└──────┬───────┘
       │
       ├──────────────────────────────────┐
       │                                  │
┌──────▼───────┐                  ┌───────▼──────┐
│    build     │ Build deps       │  development │ Dev/test
└──────┬───────┘                  └───────┬──────┘
       │                                  │
       │                          ┌───────▼──────┐
       │                          │    test      │
       │                          └──────────────┘
┌──────▼───────┐
│  production  │ Minimal runtime
└──────────────┘
```

## BuildKit Features

### Cache Mounts

```dockerfile
# syntax=docker/dockerfile:1.4

FROM ruby:3.3.0-slim AS build

# Cache apt packages
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y build-essential

# Cache bundler
RUN --mount=type=cache,target=/root/.bundle/cache \
    bundle install
```

### Secret Mounts

```dockerfile
# syntax=docker/dockerfile:1.4

FROM ruby:3.3.0-slim AS build

# Use secret during build (not persisted in image)
RUN --mount=type=secret,id=github_token \
    BUNDLE_GITHUB__COM=$(cat /run/secrets/github_token) \
    bundle install
```

```bash
docker build --secret id=github_token,src=~/.github_token .
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Single stage | Large image | Multi-stage build |
| No base stage | Repeated ENV | Extract common base |
| Build deps in runtime | Bloated image | COPY only artifacts |
| All targets identical | No flexibility | Define purpose-specific targets |

## Related Files

- [Dockerfile](./Dockerfile): Base Dockerfile
- [production.md](./production.md): Production optimizations
- [../kamal/configuration.md](../kamal/configuration.md): Deployment config

## References

- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [BuildKit](https://docs.docker.com/build/buildkit/)
- [Docker Target](https://docs.docker.com/engine/reference/commandline/build/#target)
