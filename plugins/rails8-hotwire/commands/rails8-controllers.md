---
description: RESTful 컨트롤러 패턴, Turbo 응답, 서비스 객체 가이드.
argument-hint: "[controller_name]"
allowed-tools: ["Read", "Glob", "Grep"]
---

# /rails8-hotwire:rails8-controllers - Controller Patterns

RESTful 컨트롤러 패턴과 Turbo 통합을 안내합니다.

## Topics

1. **RESTful 액션** - CRUD 패턴
2. **Turbo 응답** - turbo_stream 형식
3. **서비스 객체** - 비즈니스 로직 분리
4. **에러 처리** - 상태 코드

## Knowledge Loading

- `knowledge/controllers/INDEX.md` - 컨트롤러 전체 가이드

## Key Patterns

### RESTful with Turbo

```ruby
class PostsController < ApplicationController
  def create
    @post = Post.new(post_params)

    if @post.save
      respond_to do |format|
        format.turbo_stream
        format.html { redirect_to @post, status: :see_other }
      end
    else
      render :new, status: :unprocessable_entity
    end
  end
end
```

### Service Object Pattern

```ruby
# app/services/posts/create_service.rb
module Posts
  class CreateService
    def initialize(user:, params:)
      @user = user
      @params = params
    end

    def call
      post = @user.posts.build(@params)
      post.save ? Result.success(post) : Result.failure(post.errors)
    end
  end
end
```

## Related

- `/rails8-hotwire:rails8-views` - 뷰 패턴
- `/rails8-hotwire:rails8-turbo` - Turbo 패턴
