---
name: deploy-kamal
description: Kamal 2를 사용한 배포 자동화 설정
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
---

# Deploy Kamal - Kamal 배포 자동화

## Workflow

1. `config/deploy.yml` 생성
2. Dockerfile 최적화
3. 환경 변수 설정
4. SSL 설정
5. GitHub Actions 설정

## Generated Files

- `config/deploy.yml` - Kamal 설정
- `Dockerfile` - 멀티스테이지 빌드 최적화
- `.github/workflows/deploy.yml` - CI/CD 파이프라인

## Instructions

kamal-deployer 에이전트를 사용하여 배포 환경을 구성합니다.

## Example

```
/rails8-hotwire:deploy-kamal AWS EC2에 배포하고 싶습니다
/rails8-hotwire:deploy-kamal Hetzner 서버에 배포 설정해주세요
```

## Quick Setup

```bash
# Kamal 설치
gem install kamal

# 설정 초기화
kamal init

# 배포
kamal deploy
```
