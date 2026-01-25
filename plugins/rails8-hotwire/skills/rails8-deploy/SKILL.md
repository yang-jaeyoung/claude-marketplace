---
name: rails8-deploy
description: Kamal 2, Docker, CI/CD 배포 가이드
allowed-tools: Read, Glob, Grep
---

# Rails 8 Deploy - Deployment Skill

## Topics

- Kamal 2 configuration
- Docker image optimization
- Zero-downtime deployment
- SSL/TLS setup
- CI/CD (GitHub Actions)
- Cloud platforms (Render, Railway, Fly.io)
- Database configuration
- Monitoring and logging

## Quick Start

```bash
# Install Kamal
gem install kamal

# Initialize in project
kamal init

# Deploy
kamal deploy
```

## Knowledge Reference

For comprehensive documentation, see:
- **[knowledge/deploy/SKILL.md](../../knowledge/deploy/SKILL.md)**: Full deployment guide
- **[knowledge/deploy/kamal/](../../knowledge/deploy/kamal/)**: Kamal configuration
- **[knowledge/deploy/docker/](../../knowledge/deploy/docker/)**: Dockerfile optimization
- **[knowledge/deploy/platforms/](../../knowledge/deploy/platforms/)**: Platform-specific guides

## Related Agents

- `kamal-deployer`: Deployment specialist
- `rails-architect`: Infrastructure architecture

## Related Skills

- [rails8-background](../rails8-background/SKILL.md): Job queue deployment
- [rails8-realtime](../rails8-realtime/SKILL.md): WebSocket deployment
