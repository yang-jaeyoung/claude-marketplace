---
name: solid-setup
description: Solid Queue, Cache, Cable을 설정합니다 (Rails 8 기본)
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
---

# Solid Setup - Solid Trifecta 설정

Rails 8의 "No PaaS Required" 철학을 구현하는 Solid Trifecta를 설정합니다.

## Components

1. **Solid Queue** - DB 기반 백그라운드 작업 (Redis 불필요)
2. **Solid Cache** - DB 기반 캐싱 (Redis 불필요)
3. **Solid Cable** - DB 기반 WebSocket Pub/Sub (Redis 불필요)

## Workflow

1. Gem 설치
2. 마이그레이션 실행
3. 설정 파일 생성
4. 환경별 설정

## Instructions

rails-executor 에이전트를 사용하여 Solid Trifecta를 설정합니다.

## Example

```
/rails8-hotwire:solid-setup 전체 Solid Trifecta를 설정해주세요
/rails8-hotwire:solid-setup Solid Queue만 설정해주세요
```
