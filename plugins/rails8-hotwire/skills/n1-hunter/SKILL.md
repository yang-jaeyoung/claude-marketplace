---
name: n1-hunter
description: N+1 쿼리를 찾아 수정합니다
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
---

# N+1 Hunter - N+1 쿼리 감지 및 수정

## Workflow

1. Bullet gem 로그 분석
2. 컨트롤러/뷰 분석
3. includes/preload 추가
4. 수정 사항 적용

## Output

- 발견된 N+1 목록
- 수정된 코드
- 성능 개선 리포트

## Instructions

activerecord-optimizer 에이전트를 사용하여 N+1 문제를 찾고 해결합니다.

## Example

```
/rails8-hotwire:n1-hunter PostsController#index에서 N+1이 발생합니다
```

## Common Fixes

```ruby
# Before (N+1)
Post.all.each { |p| p.author.name }

# After (Fixed)
Post.includes(:author).each { |p| p.author.name }
```
