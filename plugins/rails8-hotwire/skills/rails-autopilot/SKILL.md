# rails-autopilot

완전 자동 Rails 앱 생성

## Invocation
`/rails8:autopilot`

## Description
고수준 요구사항에서 완전한 Rails 8 애플리케이션을 자동으로 생성합니다.

## Workflow
1. 요구사항 분석 (rails-architect)
2. 스키마/API 설계 (rails-architect)
3. 모델 생성 (rails-executor)
4. 컨트롤러/뷰 생성 (rails-executor)
5. Hotwire 통합 (hotwire-specialist)
6. 테스트 작성 (rspec-tester)
7. 검증 (rails-reviewer)

## Input
사용자가 원하는 애플리케이션 설명

## Output
- 완전한 Rails 8 애플리케이션
- Hotwire 통합
- RSpec 테스트
- README 문서

## Example
```
/rails8:autopilot 태스크 관리 앱을 만들어주세요.
사용자가 프로젝트를 만들고, 각 프로젝트에 태스크를 추가할 수 있어야 합니다.
실시간으로 태스크 상태가 업데이트되어야 합니다.
```
