# n1-hunter

N+1 쿼리 감지 및 수정

## Invocation
`/rails8:n1-hunter`

## Description
N+1 쿼리를 찾아 수정합니다.

## Workflow
1. Bullet gem 로그 분석
2. 컨트롤러/뷰 분석
3. includes/preload 추가
4. 수정 사항 적용

## Output
- 발견된 N+1 목록
- 수정된 코드
- 성능 개선 리포트
