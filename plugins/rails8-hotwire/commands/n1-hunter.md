---
description: N+1 쿼리를 탐지하고 수정 방안을 제시합니다.
argument-hint: "[path]"
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
---

# /rails8-hotwire:n1-hunter - N+1 Query Hunter

N+1 쿼리 문제를 탐지하고 수정 방안을 제시합니다.

## What It Does

1. 컨트롤러/뷰 분석
2. 잠재적 N+1 패턴 탐지
3. includes/preload 제안
4. 쿼리 객체 패턴 제안

## Detection Patterns

- 루프 내 연관 접근
- 뷰에서 연관 호출
- 중첩 연관 접근

## Example

```
/rails8-hotwire:n1-hunter app/controllers/posts_controller.rb
```

## Output

```
N+1 Query Detected:

Location: app/controllers/posts_controller.rb:15
Issue: @posts.each { |p| p.user.name }

Suggested Fix:
  - @posts = Post.all
  + @posts = Post.includes(:user).all

Additional Recommendations:
  - Add bullet gem for runtime detection
  - Create PostsQuery object for complex queries
```
