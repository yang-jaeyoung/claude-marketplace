---
description: Solid Trifecta (Queue, Cache, Cable)를 설정합니다.
argument-hint: "[queue|cache|cable|all]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
context: fork
---

# /rails8-hotwire:solid-setup - Solid Trifecta Setup

Rails 8의 Solid Queue, Solid Cache, Solid Cable을 설정합니다.

## Components

- **Solid Queue** - DB 기반 작업 큐 (Redis 대체)
- **Solid Cache** - DB 기반 캐시 (Redis 대체)
- **Solid Cable** - DB 기반 WebSocket (Redis 대체)

## What It Sets Up

### Solid Queue
- 마이그레이션 생성
- queue.yml 설정
- recurring.yml 설정

### Solid Cache
- 마이그레이션 생성
- cache.yml 설정
- 프로덕션 설정

### Solid Cable
- cable.yml 설정
- 프로덕션 환경 설정

## Example

```
/rails8-hotwire:solid-setup all
```

## Benefits

- Redis 불필요
- 간단한 인프라
- 동일한 API
- 프로덕션 검증됨
