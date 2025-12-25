# Codex CLI Plugin for Claude Code

Codex CLI를 Claude Code에서 직접 사용할 수 있는 플러그인입니다.

## Features

- **모델 분리**: 용도에 따라 최적화된 모델 사용
  - 일반 질의: `gpt-5.2`
  - 코드 관련: `gpt-5.2-codex`
- **안전한 실행**: 기본적으로 `read-only` 샌드박스 모드 사용

## Commands

| Command | Description | Model |
|---------|-------------|-------|
| `/codex:ask` | 일반 질의 실행 | gpt-5.2 |
| `/codex:code` | 코드 관련 질의 | gpt-5.2-codex |
| `/codex:review` | 코드 리뷰 실행 | gpt-5.2-codex |

## Usage

```bash
# 일반 질의
/codex:ask What is quantum computing?

# 코드 관련 질의
/codex:code How to implement quicksort in Python?

# 코드 리뷰
/codex:review
/codex:review src/main.py
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
