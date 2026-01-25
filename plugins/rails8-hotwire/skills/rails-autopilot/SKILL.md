---
name: rails-autopilot
description: 고수준 요구사항에서 완전한 Rails 8 애플리케이션을 자동으로 생성합니다
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
---

# Rails Autopilot - 완전 자동 Rails 앱 생성

## Workflow

1. **요구사항 분석** - rails-architect 에이전트 사용
2. **스키마/API 설계** - rails-architect 에이전트 사용
3. **모델 생성** - rails-executor 에이전트 사용
4. **컨트롤러/뷰 생성** - rails-executor 에이전트 사용
5. **Hotwire 통합** - hotwire-specialist 에이전트 사용
6. **테스트 작성** - rspec-tester 에이전트 사용
7. **검증** - rails-reviewer 에이전트 사용

## Output

- 완전한 Rails 8 애플리케이션
- Hotwire 통합 (Turbo + Stimulus)
- RSpec 테스트
- README 문서

## Instructions

사용자의 애플리케이션 요구사항을 분석하고, 위 워크플로우에 따라 전체 앱을 생성합니다.

Rails 8 기본 원칙을 따릅니다:
- Convention over Configuration
- HTML over the Wire (Hotwire)
- No PaaS Required (Solid Trifecta)
- Server-side First

## Example Usage

```
/rails8-hotwire:rails-autopilot 태스크 관리 앱을 만들어주세요.
사용자가 프로젝트를 만들고, 각 프로젝트에 태스크를 추가할 수 있어야 합니다.
실시간으로 태스크 상태가 업데이트되어야 합니다.
```
