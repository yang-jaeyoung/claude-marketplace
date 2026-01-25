# Kamal Secrets Management

## Overview

Kamal manages secrets through environment variables stored in `.kamal/secrets` locally and pushed securely to servers. Secrets are never stored in `config/deploy.yml`.

## When to Use

- When managing production credentials
- When rotating secrets
- When deploying to multiple environments
- When setting up CI/CD pipelines

## Quick Start

### Create Secrets File

```bash
# .kamal/secrets (local file, gitignored)
KAMAL_REGISTRY_PASSWORD=ghp_xxxxxxxxxxxxxxxxxxxx
RAILS_MASTER_KEY=abcdef1234567890abcdef1234567890
DATABASE_URL=postgres://user:pass@db.example.com:5432/myapp_production
REDIS_URL=redis://:password@redis.example.com:6379/0
```

### Reference in deploy.yml

```yaml
# config/deploy.yml
registry:
  password:
    - KAMAL_REGISTRY_PASSWORD

env:
  secret:
    - RAILS_MASTER_KEY
    - DATABASE_URL
    - REDIS_URL
```

### Push to Servers

```bash
# Push secrets to all servers
kamal env push

# Verify secrets are set
kamal env
```

## Secrets File Patterns

### Basic Format

```bash
# .kamal/secrets
# Format: KEY=value (no spaces around =)

# Registry
KAMAL_REGISTRY_PASSWORD=ghp_xxxxxxxxxxxxxxxxxxxx

# Rails
RAILS_MASTER_KEY=abcdef1234567890abcdef1234567890
SECRET_KEY_BASE=very_long_secret_key_here

# Database
DATABASE_URL=postgres://user:pass@host:5432/db
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_URL=redis://:password@host:6379/0
REDIS_PASSWORD=secure_password

# AWS
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Third-party
SENTRY_DSN=https://key@sentry.io/project
STRIPE_SECRET_KEY=sk_live_xxxxxxxx
```

### Multi-line Values

```bash
# Use quotes for multi-line values
PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEA...
-----END RSA PRIVATE KEY-----"
```

### Environment-specific Secrets

```bash
# .kamal/secrets.staging
RAILS_MASTER_KEY=staging_key_here
DATABASE_URL=postgres://user:pass@staging-db:5432/myapp_staging

# .kamal/secrets.production
RAILS_MASTER_KEY=production_key_here
DATABASE_URL=postgres://user:pass@prod-db:5432/myapp_production
```

```bash
# Push staging secrets
KAMAL_SECRETS_FILE=.kamal/secrets.staging kamal env push -d staging

# Push production secrets
KAMAL_SECRETS_FILE=.kamal/secrets.production kamal env push
```

## Git Security

### .gitignore Setup

```gitignore
# .gitignore
.kamal/secrets
.kamal/secrets.*
.env
.env.*
!.env.example
config/credentials/*.key
config/master.key
```

### Secrets Template

```bash
# .kamal/secrets.example (committed to git)
# Copy to .kamal/secrets and fill in values

# Registry (GitHub Container Registry token)
KAMAL_REGISTRY_PASSWORD=

# Rails master key (from config/master.key)
RAILS_MASTER_KEY=

# Database URL
DATABASE_URL=postgres://user:password@host:5432/database

# Redis URL (if using Redis)
REDIS_URL=redis://:password@host:6379/0
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: webfactory/ssh-agent@v0.8.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - uses: ruby/setup-ruby@v1
        with:
          bundler-cache: true

      - name: Create secrets file
        run: |
          mkdir -p .kamal
          cat << EOF > .kamal/secrets
          KAMAL_REGISTRY_PASSWORD=${{ secrets.GITHUB_TOKEN }}
          RAILS_MASTER_KEY=${{ secrets.RAILS_MASTER_KEY }}
          DATABASE_URL=${{ secrets.DATABASE_URL }}
          REDIS_URL=${{ secrets.REDIS_URL }}
          EOF

      - name: Deploy with Kamal
        run: kamal deploy
```

### GitLab CI

```yaml
# .gitlab-ci.yml
deploy:
  stage: deploy
  script:
    - mkdir -p .kamal
    - |
      cat << EOF > .kamal/secrets
      KAMAL_REGISTRY_PASSWORD=$CI_REGISTRY_PASSWORD
      RAILS_MASTER_KEY=$RAILS_MASTER_KEY
      DATABASE_URL=$DATABASE_URL
      EOF
    - kamal deploy
  only:
    - main
```

## Secret Rotation

### Rotate Rails Master Key

```bash
# 1. Generate new credentials with new key
EDITOR="code --wait" rails credentials:edit

# 2. Update .kamal/secrets with new RAILS_MASTER_KEY

# 3. Push new secrets
kamal env push

# 4. Deploy (restarts containers with new key)
kamal deploy
```

### Rotate Database Password

```bash
# 1. Update password in database

# 2. Update DATABASE_URL in .kamal/secrets
DATABASE_URL=postgres://user:NEW_PASSWORD@host:5432/db

# 3. Push and restart
kamal env push
kamal app restart
```

### Rotate Registry Token

```bash
# 1. Generate new token in GitHub/Docker Hub

# 2. Update KAMAL_REGISTRY_PASSWORD in .kamal/secrets

# 3. Push secrets
kamal env push

# Next deploy will use new token
```

## Accessing Secrets on Server

```bash
# View current secrets
kamal env

# Access container environment
kamal app exec "printenv"

# Rails console with environment
kamal console
# > ENV['DATABASE_URL']
```

## Secure Practices

### 1Password/Vault Integration

```bash
# Using 1Password CLI
KAMAL_REGISTRY_PASSWORD=$(op read "op://Vault/Kamal/token")
RAILS_MASTER_KEY=$(op read "op://Vault/Rails/master_key")

# Export for kamal
export KAMAL_REGISTRY_PASSWORD RAILS_MASTER_KEY
kamal deploy
```

### HashiCorp Vault

```bash
# Fetch secrets from Vault
export RAILS_MASTER_KEY=$(vault kv get -field=master_key secret/myapp)
export DATABASE_URL=$(vault kv get -field=url secret/myapp/database)

# Write to secrets file
cat << EOF > .kamal/secrets
KAMAL_REGISTRY_PASSWORD=${KAMAL_REGISTRY_PASSWORD}
RAILS_MASTER_KEY=${RAILS_MASTER_KEY}
DATABASE_URL=${DATABASE_URL}
EOF

kamal deploy
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Secrets in git | Exposed credentials | Use .gitignore |
| Secrets in clear env | Visible in deploy.yml | Use secret: list |
| Shared master key | Compromise spreads | Unique keys per env |
| No rotation policy | Stale credentials | Rotate quarterly |
| Logging secrets | Exposed in logs | Filter in production |

## Related Files

- [setup.md](./setup.md): Initial Kamal setup
- [configuration.md](./configuration.md): Full config options
- [../../core/SKILL.md](../../core/SKILL.md): Rails credentials

## References

- [Kamal Secrets](https://kamal-deploy.org/docs/configuration/environment-variables/)
- [Rails Credentials](https://guides.rubyonrails.org/security.html#custom-credentials)
