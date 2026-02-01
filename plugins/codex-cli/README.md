# Codex CLI Plugin for Claude Code

Codex CLI를 Claude Code에서 직접 사용할 수 있는 플러그인입니다.

## Features

- **모델 분리**: 용도에 따라 최적화된 모델 사용
  - 일반 질의: `gpt-5.2`
  - 코드 관련: `gpt-5.2-codex`
- **Reasoning Effort**: 작업 복잡도에 따른 추론 수준 조절
  - `low`: 빠른 실험, 간단한 수정
  - `medium`: 일반 코드 생성 (기본값)
  - `high`: 복잡한 아키텍처, 코드 리뷰
- **안전한 실행**: 기본적으로 `read-only` 샌드박스 모드 사용
- **세션 관리**: 이전 세션 이어가기 지원
- **클라우드 통합**: Codex Cloud 태스크 지원
- **MCP 통합**: MCP 서버 관리 및 MCP Server 모드 지원

## Commands

### Core Commands

| Command | Description | Model | Reasoning |
|---------|-------------|-------|-----------|
| `/codex:ask` | 일반 질의 실행 | gpt-5.2 | medium |
| `/codex:code` | 코드 관련 질의 | gpt-5.2-codex | medium |
| `/codex:review` | 코드 리뷰 실행 | gpt-5.2-codex | high |
| `/codex:exec` | 고급 옵션 실행 | 선택 가능 | 선택 가능 |

### Session & Automation

| Command | Description | Model | Reasoning |
|---------|-------------|-------|-----------|
| `/codex:resume` | 이전 세션 이어가기 | - | - |
| `/codex:auto` | Full-auto 모드 실행 | gpt-5.2-codex | medium |
| `/codex:vision` | 이미지 컨텍스트 질의 | gpt-5.2 | - |
| `/codex:search` | 웹 검색 포함 질의 | gpt-5.2 | - |

### Cloud Integration

| Command | Description |
|---------|-------------|
| `/codex:cloud` | Cloud 태스크 생성 (--env 필요) |
| `/codex:apply` | Cloud 태스크 결과 로컬 적용 |

### MCP Integration

| Command | Description |
|---------|-------------|
| `/codex:mcp-server` | Codex를 MCP 서버로 시작 |
| `/codex:mcp-list` | 설정된 MCP 서버 목록 |
| `/codex:mcp-add` | MCP 서버 추가 |

### Utility

| Command | Description |
|---------|-------------|
| `/codex:status` | 인증 상태 확인 |

## Usage

### 기본 사용법

```bash
# 일반 질의
/codex:ask What is quantum computing?

# 코드 관련 질의
/codex:code How to implement quicksort in Python?

# 코드 리뷰
/codex:review
/codex:review src/main.py
```

### 세션 관리

```bash
# 마지막 세션 이어가기
/codex:resume --last

# 특정 세션 이어가기
/codex:resume session_abc123

# 세션 목록 확인
/codex:resume
```

### Full-Auto 모드

```bash
# 자동 실행 모드 (주의: 무인 실행)
/codex:auto Fix all linting errors in src/
/codex:auto Add type annotations to utils.py
```

### 이미지 분석

```bash
# 이미지와 함께 질의
/codex:vision ./screenshot.png What does this UI show?
/codex:vision ./error.png Explain this error message
```

### 웹 검색

```bash
# 실시간 정보가 필요한 질의
/codex:search Latest React 19 features
/codex:search Current Python 3.12 release notes
```

### Cloud 기능 (실험적)

```bash
# Cloud 태스크 생성
/codex:cloud --env env123 Review this PR

# 결과 적용
/codex:apply task_abc123
```

### MCP 서버 관리 (실험적)

```bash
# Codex를 MCP 서버로 실행
/codex:mcp-server

# MCP Inspector와 함께 실행
/codex:mcp-server --inspector

# 서버 목록
/codex:mcp-list

# 서버 추가
/codex:mcp-add myserver --url https://mcp.example.com
```

### 고급 실행 옵션

```bash
# 높은 추론 수준으로 아키텍처 분석
/codex:exec -r high "Review the architecture of this project"

# 자동 승인 + 작업 공간 쓰기 권한
/codex:exec -p never -s workspace-write "Refactor the utils module"

# 커스텀 작업 디렉토리
/codex:exec --cwd ./backend "List all API endpoints"
```

## Prerequisites

- Codex CLI가 설치되어 있어야 합니다
- PATH에 `codex` 명령어가 등록되어 있어야 합니다

## Installation

### From Marketplace

```bash
claude plugins add github:jyyang/claude-marketplace
claude plugins install codex-cli
```

### Manual Installation

이 플러그인 폴더를 다음 위치에 복사합니다:
```
~/.claude/plugins/codex-cli/
```

Claude Code 재시작 후 자동으로 로드됩니다.

## Notes

- `--full-auto` 모드는 로컬 환경에서만 사용 권장
- Cloud 기능은 환경 ID가 필요하며 실험적 기능임
- MCP 기능도 실험적 상태임
- 모든 커맨드는 `read-only` 샌드박스 기본값 유지 (안전성)
