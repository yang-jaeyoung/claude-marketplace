---
description: Kamal, Docker, 클라우드 배포 가이드.
argument-hint: "[platform]"
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
---

# /rails8-hotwire:rails8-deploy - Deployment

Kamal 기반 프로덕션 배포를 안내합니다.

## Topics

1. **Kamal** - Zero-downtime 배포
2. **Docker** - 컨테이너화
3. **PostgreSQL** - 프로덕션 DB
4. **SSL** - Let's Encrypt

## Knowledge Loading

- `knowledge/deploy/INDEX.md` - 배포 전체 가이드
- `knowledge/deploy/kamal/setup.md` - Kamal 설정

## Quick Setup

```bash
bundle add kamal
kamal init
```

### Kamal Configuration

```yaml
# config/deploy.yml
service: myapp
image: user/myapp

servers:
  web:
    hosts:
      - 192.168.1.100

env:
  clear:
    RAILS_ENV: production
```

### Deploy Commands

```bash
# First deploy
kamal setup

# Regular deploy
kamal deploy

# Check logs
kamal app logs
```

## Related

- `/rails8-hotwire:deploy-kamal` - Kamal 자동화
- `/rails8-hotwire:solid-setup` - Solid Trifecta 설정
