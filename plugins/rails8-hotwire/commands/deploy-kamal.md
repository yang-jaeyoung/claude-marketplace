---
description: Kamal 배포를 자동으로 설정하고 실행합니다.
argument-hint: "[setup|deploy|logs]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
context: fork
---

# /rails8-hotwire:deploy-kamal - Kamal Deployment Automation

Kamal 기반 프로덕션 배포를 자동화합니다.

## Subcommands

- **setup** - Kamal 초기 설정
- **deploy** - 배포 실행
- **logs** - 로그 확인

## What It Does

### Setup
1. Kamal 설치 확인
2. deploy.yml 생성
3. Dockerfile 최적화
4. GitHub Actions 워크플로우 생성

### Deploy
1. 테스트 실행
2. Docker 이미지 빌드
3. 서버 배포
4. 헬스체크

## Example

```
/rails8-hotwire:deploy-kamal setup
```

## Configuration

```yaml
# config/deploy.yml
service: myapp
image: user/myapp

servers:
  web:
    hosts:
      - 192.168.1.100
    options:
      memory: 512m
```
