# Kamal Configuration

## Overview

Comprehensive guide to `config/deploy.yml` options. Kamal 2 configuration covers servers, registries, accessories, and Traefik.

## When to Use

- When customizing deployment topology
- When adding database/Redis containers
- When configuring SSL/TLS
- When setting up multi-server deployments

## Quick Start

```yaml
# config/deploy.yml - Complete example
service: myapp

image: ghcr.io/myuser/myapp

servers:
  web:
    hosts:
      - 192.168.1.1
      - 192.168.1.2
    labels:
      traefik.http.routers.myapp.rule: Host(`myapp.com`)
      traefik.http.routers.myapp.tls: true
      traefik.http.routers.myapp.tls.certresolver: letsencrypt
    options:
      memory: 1g
      cpus: 2

registry:
  server: ghcr.io
  username: myuser
  password:
    - KAMAL_REGISTRY_PASSWORD

env:
  clear:
    RAILS_ENV: production
    RAILS_LOG_TO_STDOUT: true
    RAILS_SERVE_STATIC_FILES: true
  secret:
    - RAILS_MASTER_KEY
    - DATABASE_URL

builder:
  multiarch: false
  cache:
    type: gha

healthcheck:
  path: /up
  port: 3000
  interval: 10s
  max_attempts: 10

traefik:
  options:
    publish:
      - "443:443"
    volume:
      - "/letsencrypt:/letsencrypt"
  args:
    entryPoints.websecure.address: ":443"
    certificatesResolvers.letsencrypt.acme.email: "admin@myapp.com"
    certificatesResolvers.letsencrypt.acme.storage: "/letsencrypt/acme.json"
    certificatesResolvers.letsencrypt.acme.httpchallenge.entrypoint: "web"

accessories:
  db:
    image: postgres:16
    host: 192.168.1.1
    port: 5432
    env:
      secret:
        - POSTGRES_PASSWORD
    directories:
      - data:/var/lib/postgresql/data
    options:
      memory: 2g

  redis:
    image: redis:7-alpine
    host: 192.168.1.1
    port: 6379
    directories:
      - data:/data
    cmd: "redis-server --appendonly yes"
```

## Servers Configuration

### Basic Setup

```yaml
servers:
  web:
    hosts:
      - 192.168.1.1
      - 192.168.1.2
```

### With Labels and Options

```yaml
servers:
  web:
    hosts:
      - 192.168.1.1
    labels:
      traefik.http.routers.myapp.rule: Host(`myapp.com`)
      traefik.http.routers.myapp.tls: true
      traefik.http.routers.myapp.tls.certresolver: letsencrypt
    options:
      memory: 1g        # Memory limit
      cpus: 2           # CPU limit
      add-host: host.docker.internal:host-gateway
    cmd: "./bin/thrust ./bin/rails server"
```

### Multiple Roles

```yaml
servers:
  web:
    hosts:
      - 192.168.1.1
    labels:
      traefik.http.routers.myapp.rule: Host(`myapp.com`)

  job:
    hosts:
      - 192.168.1.2
    cmd: "bundle exec solid_queue:start"
    labels: {}  # No Traefik routing

  cron:
    hosts:
      - 192.168.1.2
    cmd: "bundle exec whenever"
    labels: {}
```

## Registry Configuration

### GitHub Container Registry

```yaml
registry:
  server: ghcr.io
  username: myuser
  password:
    - KAMAL_REGISTRY_PASSWORD
```

### Docker Hub

```yaml
registry:
  username: myuser
  password:
    - KAMAL_REGISTRY_PASSWORD
# server omitted = Docker Hub
```

### AWS ECR

```yaml
registry:
  server: 123456789.dkr.ecr.us-east-1.amazonaws.com
  username: AWS
  password:
    - KAMAL_REGISTRY_PASSWORD
# Password = $(aws ecr get-login-password)
```

### Self-hosted Registry

```yaml
registry:
  server: registry.myapp.com:5000
  username: admin
  password:
    - KAMAL_REGISTRY_PASSWORD
```

## Environment Variables

```yaml
env:
  # Plain text (visible in config)
  clear:
    RAILS_ENV: production
    RAILS_LOG_TO_STDOUT: true
    RAILS_SERVE_STATIC_FILES: true
    WEB_CONCURRENCY: 2
    RAILS_MAX_THREADS: 5

  # From secrets file (encrypted)
  secret:
    - RAILS_MASTER_KEY
    - DATABASE_URL
    - REDIS_URL
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
```

## Builder Configuration

### Local Build

```yaml
builder:
  multiarch: false
  local:
    arch: amd64
```

### Remote Build

```yaml
builder:
  remote:
    arch: amd64
    host: ssh://build@build-server
```

### GitHub Actions Cache

```yaml
builder:
  cache:
    type: gha
    options: mode=max
```

### Registry Cache

```yaml
builder:
  cache:
    type: registry
    options: mode=max,image-manifest=true
```

### Build Arguments

```yaml
builder:
  args:
    RUBY_VERSION: 3.3.0
    NODE_VERSION: 20
```

## Accessories (Sidecars)

### PostgreSQL

```yaml
accessories:
  db:
    image: postgres:16
    host: 192.168.1.1
    port: 5432
    env:
      clear:
        POSTGRES_DB: myapp_production
      secret:
        - POSTGRES_PASSWORD
    directories:
      - data:/var/lib/postgresql/data
    options:
      memory: 2g
```

### Redis

```yaml
accessories:
  redis:
    image: redis:7-alpine
    host: 192.168.1.1
    port: 6379
    directories:
      - data:/data
    cmd: "redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}"
    env:
      secret:
        - REDIS_PASSWORD
```

### Multiple Accessories

```yaml
accessories:
  db:
    image: postgres:16
    host: 192.168.1.1
    # ...

  redis:
    image: redis:7-alpine
    host: 192.168.1.1
    # ...

  memcached:
    image: memcached:1.6-alpine
    host: 192.168.1.1
    port: 11211
```

## Traefik Configuration

### Basic SSL

```yaml
traefik:
  options:
    publish:
      - "443:443"
    volume:
      - "/letsencrypt:/letsencrypt"
  args:
    entryPoints.websecure.address: ":443"
    certificatesResolvers.letsencrypt.acme.email: "admin@myapp.com"
    certificatesResolvers.letsencrypt.acme.storage: "/letsencrypt/acme.json"
    certificatesResolvers.letsencrypt.acme.httpchallenge.entrypoint: "web"
```

### HTTP to HTTPS Redirect

```yaml
traefik:
  options:
    publish:
      - "80:80"
      - "443:443"
    volume:
      - "/letsencrypt:/letsencrypt"
  args:
    entryPoints.web.address: ":80"
    entryPoints.websecure.address: ":443"
    entryPoints.web.http.redirections.entryPoint.to: websecure
    entryPoints.web.http.redirections.entryPoint.scheme: https
    certificatesResolvers.letsencrypt.acme.email: "admin@myapp.com"
    certificatesResolvers.letsencrypt.acme.storage: "/letsencrypt/acme.json"
    certificatesResolvers.letsencrypt.acme.httpchallenge.entrypoint: "web"
```

### Custom Domain with Labels

```yaml
servers:
  web:
    hosts:
      - 192.168.1.1
    labels:
      traefik.http.routers.myapp.rule: Host(`myapp.com`) || Host(`www.myapp.com`)
      traefik.http.routers.myapp.tls: true
      traefik.http.routers.myapp.tls.certresolver: letsencrypt
      traefik.http.routers.myapp.entrypoints: websecure
```

## Healthcheck Configuration

```yaml
healthcheck:
  path: /up                    # Health check endpoint
  port: 3000                   # Application port
  interval: 10s                # Check interval
  max_attempts: 10             # Max retries before failing
  cmd: "curl -f http://localhost:3000/up"  # Custom command
```

## Hooks

```bash
# .kamal/hooks/pre-build
#!/bin/bash
echo "Running pre-build hook..."
bundle exec rails assets:precompile
```

```bash
# .kamal/hooks/post-deploy
#!/bin/bash
echo "Running post-deploy hook..."
curl -X POST https://api.opsgenie.com/v2/heartbeats/myapp/ping
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Secrets in clear | Exposed credentials | Use secret env |
| Missing healthcheck | Deploy failures undetected | Configure /up endpoint |
| Single server | No redundancy | Add multiple hosts |
| No memory limits | Resource exhaustion | Set options.memory |

## Related Files

- [setup.md](./setup.md): Initial setup
- [secrets.md](./secrets.md): Secret management
- [../docker/production.md](../docker/production.md): Dockerfile optimization

## References

- [Kamal Configuration](https://kamal-deploy.org/docs/configuration/)
- [Traefik Docker](https://doc.traefik.io/traefik/providers/docker/)
