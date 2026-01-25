---
description: Turbo 통합된 향상된 스캐폴딩을 생성합니다.
argument-hint: "<resource_name> [fields...]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
context: fork
---

# /rails8-hotwire:scaffold-plus - Enhanced Scaffolding

기본 Rails scaffold에 Turbo Frame/Stream, 서비스 객체, RSpec 테스트를 추가한 향상된 스캐폴딩을 생성합니다.

## Generated Files

- Model with validations
- Controller with Turbo responses
- Views with Turbo Frames
- Service objects (Create, Update, Delete)
- RSpec specs (model, request, system)
- Factory Bot factory

## Example

```
/rails8-hotwire:scaffold-plus Post title:string body:text published:boolean user:references
```

## Output Structure

```
app/models/post.rb
app/controllers/posts_controller.rb
app/views/posts/
  _form.html.erb
  _post.html.erb
  index.html.erb
  show.html.erb
  new.html.erb
  edit.html.erb
app/services/posts/
  create_service.rb
  update_service.rb
spec/models/post_spec.rb
spec/requests/posts_spec.rb
spec/system/posts_spec.rb
spec/factories/posts.rb
```
