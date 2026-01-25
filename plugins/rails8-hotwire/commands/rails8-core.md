---
description: Rails 8 프로젝트 초기 설정 가이드. 프로젝트 생성, Solid Trifecta, 디렉토리 구조 등.
argument-hint: "[project_name]"
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
---

# /rails8-hotwire:rails8-core - Rails 8 Project Setup

Rails 8 프로젝트 초기 설정을 안내합니다.

## Tasks

1. **프로젝트 생성** - rails new 명령어 및 권장 옵션
2. **Solid Trifecta 설정** - Queue, Cache, Cable
3. **디렉토리 구조** - 표준 Rails 8 구조
4. **환경 설정** - credentials, database.yml

## Knowledge Loading

관련 지식 파일을 로드합니다:
- `knowledge/core/INDEX.md` - 핵심 설정 가이드

## Quick Start

```bash
# Rails 8 프로젝트 생성
rails new myapp \
  --database=postgresql \
  --css=tailwind \
  --skip-jbuilder \
  --skip-action-mailbox

cd myapp

# 기본 인증 생성 (Rails 8)
bin/rails generate authentication
bin/rails db:migrate
```

## Related

- `/rails8-hotwire:rails8-turbo` - Hotwire 설정
- `/rails8-hotwire:rails8-models` - 모델 패턴
