# Kamal 2 Setup

## Overview

Kamal 2 is Rails 8's default deployment tool. It deploys containerized applications to any server via Docker and SSH, with zero-downtime deployments using Traefik.

## When to Use

- When deploying Rails 8 applications to VPS/bare metal
- When you need full control over infrastructure
- When avoiding PaaS costs
- When deploying to multiple servers

## Quick Start

### Installation

```bash
# Add to Gemfile
gem "kamal", "~> 2.0"

# Or install globally
gem install kamal

# Verify installation
kamal version
```

### Initialize Project

```bash
# Generate Kamal configuration files
kamal init

# Files created:
# - config/deploy.yml    (main configuration)
# - .kamal/secrets       (secrets template)
# - Dockerfile           (if not exists)
```

### Minimal Configuration

```yaml
# config/deploy.yml
service: myapp

image: ghcr.io/myuser/myapp

servers:
  web:
    hosts:
      - 192.168.1.1
    labels:
      traefik.http.routers.myapp.rule: Host(`myapp.com`)

registry:
  server: ghcr.io
  username: myuser
  password:
    - KAMAL_REGISTRY_PASSWORD

env:
  clear:
    RAILS_ENV: production
    RAILS_LOG_TO_STDOUT: true
  secret:
    - RAILS_MASTER_KEY
```

## Server Preparation

### Requirements

- SSH access with key-based authentication
- Docker installed (or let Kamal install it)

### First-Time Setup

```bash
# Install Docker on remote servers (optional, Kamal can do this)
kamal server bootstrap

# Push secrets to servers
kamal env push

# Deploy for the first time
kamal setup

# This runs:
# - Docker installation (if needed)
# - Traefik setup
# - Network creation
# - First deployment
```

## Project Structure

```
myapp/
├── config/
│   ├── deploy.yml          # Main Kamal config
│   └── deploy.production.yml  # Environment overrides (optional)
├── .kamal/
│   ├── secrets              # Local secrets file
│   └── hooks/               # Deployment hooks
│       ├── pre-build
│       ├── post-deploy
│       └── pre-connect
├── Dockerfile               # Container build
└── .dockerignore            # Files to exclude
```

## Common Commands

```bash
# Full deployment
kamal deploy

# Deploy without running migrations
kamal deploy --skip-migrations

# Rollback to previous version
kamal rollback

# View application logs
kamal logs

# Open Rails console
kamal console

# Run arbitrary command
kamal app exec "bin/rails db:seed"

# Check deployment status
kamal details

# Restart application
kamal app restart

# Remove application completely
kamal remove
```

## Multiple Environments

```yaml
# config/deploy.yml (base)
service: myapp
image: ghcr.io/myuser/myapp

# Common configuration...
```

```yaml
# config/deploy.staging.yml
servers:
  web:
    hosts:
      - staging.myapp.com

env:
  clear:
    RAILS_ENV: staging
```

```bash
# Deploy to staging
kamal deploy -d staging
```

## SSH Configuration

```yaml
# config/deploy.yml
ssh:
  user: deploy                    # SSH username
  port: 22                        # SSH port (optional)
  keys:
    - ~/.ssh/deploy_key           # SSH key path
  keys_only: true                 # Disable password auth
  proxy: jump.myapp.com           # Jump host (optional)
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Root SSH user | Security risk | Create deploy user |
| Password auth | Security risk | Use SSH keys |
| Secrets in repo | Exposed credentials | Use `.kamal/secrets` |
| Skipping setup | Missing infrastructure | Run `kamal setup` first |

## Related Files

- [configuration.md](./configuration.md): Detailed config options
- [secrets.md](./secrets.md): Secret management
- [zero-downtime.md](./zero-downtime.md): Rolling deployments

## References

- [Kamal Documentation](https://kamal-deploy.org/)
- [Kamal GitHub](https://github.com/basecamp/kamal)
