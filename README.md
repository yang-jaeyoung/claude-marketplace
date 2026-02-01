# Claude Marketplace

Claude Code 플러그인 마켓플레이스입니다. AI 기반 개발 워크플로우를 확장하고 자동화하는 플러그인들을 제공합니다.

## Highlights

- **워크플로우 자동화** - 태스크 계획부터 리뷰까지 구조화된 개발 프로세스
- **AI 도구 통합** - Gemini, Codex 등 다양한 AI CLI 도구와의 seamless 연동
- **생산성 향상** - 반복 작업 자동화 및 품질 게이트 적용

## Available Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [cw](./plugins/context-aware-workflow) | 2.0.0 | Context-aware workflow orchestration - Plan Mode 통합, 자동 태스크 계획, QA 루프, Ralph Loop 개선 사이클, 모델 라우팅 |
| [codex-cli](./plugins/codex-cli) | 1.0.0 | Codex CLI 통합 - 코드 리뷰, 자동 실행, 세션 관리, 클라우드 태스크 |
| [gemini-cli](./plugins/gemini-cli) | 1.0.0 | Gemini CLI 통합 - 코드 리뷰, 커밋 메시지 생성, 문서화, 릴리스 노트 |

## Quick Start

```bash
# 마켓플레이스 추가
claude plugins add github:jyyang/claude-marketplace

# 플러그인 설치
claude plugins install cw
claude plugins install codex-cli
claude plugins install gemini-cli
```

## Plugin Highlights

### Context-Aware Workflow (cw)

구조화된 개발 워크플로우 오케스트레이션:

```bash
/cw:start "JWT 인증 구현"      # 태스크 계획 생성
/cw:loop "버그 수정"           # 완료될 때까지 자동 반복
/cw:auto "로그아웃 버튼 추가"   # 전체 워크플로우 자동 실행
```

### Codex CLI

OpenAI Codex CLI 통합:

```bash
/codex:code How to implement quicksort?
/codex:review src/main.py
/codex:auto Fix all linting errors
```

### Gemini CLI

Google Gemini CLI 통합:

```bash
/gemini:review              # 스테이지된 변경 리뷰
/gemini:commit              # 커밋 메시지 생성
/gemini:docs src/utils.py   # 문서 생성
```

## Manual Installation

```bash
git clone https://github.com/jyyang/claude-marketplace.git
cp -r claude-marketplace/plugins/<plugin-name> ~/.claude/plugins/
```

## Contributing

1. `plugins/` 아래에 새 폴더 생성
2. `.claude-plugin/plugin.json` 메타데이터 추가
3. commands, skills, agents, hooks 구성
4. `marketplace.json` 업데이트
5. Pull request 제출

## License

MIT License
