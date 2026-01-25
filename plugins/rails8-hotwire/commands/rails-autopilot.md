---
description: 고수준 요구사항에서 완전한 Rails 8 앱을 자동 생성합니다.
argument-hint: "<app_description>"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
context: fork
---

# /rails8-hotwire:rails-autopilot - Auto App Generator

사용자의 요구사항을 분석하여 완전한 Rails 8 애플리케이션을 자동으로 생성합니다.

## Workflow

1. **요구사항 분석** - rails-architect 에이전트
2. **스키마/API 설계** - rails-architect 에이전트
3. **모델 생성** - rails-executor 에이전트
4. **컨트롤러/뷰 생성** - rails-executor 에이전트
5. **Hotwire 통합** - hotwire-specialist 에이전트
6. **테스트 작성** - rspec-tester 에이전트
7. **검증** - rails-reviewer 에이전트

## Output

- 완전한 Rails 8 애플리케이션
- Hotwire 통합 (Turbo + Stimulus)
- RSpec 테스트
- README 문서

## Example

```
/rails8-hotwire:rails-autopilot 태스크 관리 앱을 만들어주세요.
사용자가 프로젝트를 만들고, 각 프로젝트에 태스크를 추가할 수 있어야 합니다.
실시간으로 태스크 상태가 업데이트되어야 합니다.
```
