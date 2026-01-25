# Rails 8 + Hotwire Plugin for Claude Code

🚂 Rails 8 + Hotwire 풀스택 웹 개발을 위한 Claude Code 플러그인

## Features

### 16 Specialized Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `rails8:rails-architect` | Opus | 아키텍처 설계, 복잡한 디버깅 |
| `rails8:rails-architect-low` | Haiku | 빠른 Rails 질문 답변 |
| `rails8:rails-executor` | Sonnet | 기능 구현 |
| `rails8:rails-executor-high` | Opus | 복잡한 마이그레이션, 리팩토링 |
| `rails8:hotwire-specialist` | Sonnet | Turbo/Stimulus 패턴 |
| `rails8:hotwire-specialist-high` | Opus | 복잡한 실시간 시스템 |
| `rails8:rspec-tester` | Sonnet | RSpec 테스트 작성 |
| `rails8:rspec-tester-low` | Haiku | 간단한 테스트 생성 |
| `rails8:kamal-deployer` | Sonnet | Kamal/Docker 배포 |
| `rails8:devise-specialist` | Sonnet | 인증 패턴 |
| `rails8:activerecord-optimizer` | Sonnet | 쿼리 최적화, N+1 수정 |
| `rails8:stimulus-designer` | Sonnet | Stimulus 컨트롤러 설계 |
| `rails8:turbo-debugger` | Opus | Turbo 응답 디버깅 |
| `rails8:rails-migrator` | Sonnet | 데이터베이스 마이그레이션 |
| `rails8:rails-reviewer` | Opus | 심층 코드 리뷰 |
| `rails8:rails-reviewer-low` | Haiku | 빠른 컨벤션 체크 |

### 6 Automated Hooks

| Hook | Trigger | Function |
|------|---------|----------|
| rails-detector | SessionStart | Rails 프로젝트 감지, 컨텍스트 주입 |
| convention-validator | UserPromptSubmit | Rails 안티패턴 감지 |
| migration-guard | PreToolUse | 위험한 마이그레이션 차단 |
| test-enforcer | PreToolUse | 테스트 작성 강제 |
| turbo-response-check | PostToolUse | Turbo 응답 검증 |
| deploy-safety | PreToolUse | 배포 명령 안전성 검사 |

### 20 Skills

**Core Skills (10)**
- `/rails8:core` - 프로젝트 설정
- `/rails8:turbo` - Turbo/Stimulus
- `/rails8:models` - ActiveRecord
- `/rails8:controllers` - 컨트롤러 패턴
- `/rails8:views` - 뷰 레이어
- `/rails8:auth` - 인증/인가
- `/rails8:realtime` - 실시간 기능
- `/rails8:background` - 백그라운드 작업
- `/rails8:testing` - 테스트
- `/rails8:deploy` - 배포

**Automation Skills (10)**
- `/rails8:autopilot` - 완전 자동 Rails 앱 생성
- `/rails8:scaffold-plus` - 향상된 스캐폴딩
- `/rails8:turbo-wizard` - Turbo 설정 마법사
- `/rails8:stimulus-gen` - Stimulus 컨트롤러 생성
- `/rails8:auth-setup` - 인증 설정 마법사
- `/rails8:deploy-kamal` - Kamal 배포 자동화
- `/rails8:test-gen` - 테스트 생성
- `/rails8:n1-hunter` - N+1 쿼리 수정
- `/rails8:solid-setup` - Solid Trifecta 설정
- `/rails8:hotwire-debug` - Hotwire 디버깅

### 6 Pipelines

| Pipeline | Stages | Purpose |
|----------|--------|---------|
| feature | analyze → test → implement → hotwire → review | TDD 기능 구현 |
| crud | model → scaffold → turbo → specs | CRUD 리소스 생성 |
| auth | devise → views → policies → specs | 인증 설정 |
| deploy | docker → kamal → ci → deploy | 배포 워크플로우 |
| test | analyze → specs → fix → verify | TDD 워크플로우 |
| refactor | analyze → specs → refactor → verify | 안전한 리팩토링 |

## Installation

플러그인은 이미 `~/.claude/plugins/rails8-hotwire/`에 설치되어 있습니다.

## Quick Start

```bash
# Rails 프로젝트에서 Claude Code 실행
claude

# 자동 감지: Rails 8 프로젝트가 감지되면 컨텍스트가 자동으로 주입됩니다

# 주요 명령어
/rails8:autopilot 태스크 관리 앱 만들어줘
/rails8:scaffold-plus Post title:string body:text
/rails8:turbo-wizard
```

## Core Philosophy

| Principle | Description |
|-----------|-------------|
| **Convention over Configuration** | Rails 컨벤션 준수 |
| **HTML over the Wire** | JSON API 대신 서버 렌더링 HTML |
| **Server-side First** | Progressive Enhancement |
| **No PaaS Required** | Solid Trifecta + Kamal 자체 배포 |

## Rails 8 Key Stack

- **Solid Queue**: Redis-free DB 기반 작업 큐
- **Solid Cache**: DB 기반 캐시
- **Solid Cable**: Redis-free WebSocket
- **Kamal 2**: Docker 기반 제로 다운타임 배포
- **Propshaft + Import Maps**: 번들러 없는 프론트엔드

## License

MIT
