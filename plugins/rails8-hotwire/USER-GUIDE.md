# Rails 8 + Hotwire 플러그인 사용 가이드

한국 개발자를 위한 완벽한 사용 설명서입니다.

---

## 목차

1. [소개](#소개)
2. [빠른 시작](#빠른-시작)
3. [스킬 사용법](#스킬-사용법)
4. [에이전트 사용법](#에이전트-사용법)
5. [파이프라인 사용법](#파이프라인-사용법)
6. [훅 동작 설명](#훅-동작-설명)
7. [실전 시나리오](#실전-시나리오)
8. [팁 & 트릭](#팁--트릭)
9. [문제 해결](#문제-해결)

---

## 소개

### 플러그인이 무엇인가?

Rails 8과 Hotwire를 사용한 **풀스택 웹 개발 완벽 가이드**입니다.

- 프로젝트 생성부터 배포까지 전체 라이프사이클 지원
- 20개의 전문 스킬로 구성
- 16개의 전문 에이전트와 6개의 자동 파이프라인 포함
- 실시간 기능(ActionCable), 인증(Devise), 배포(Kamal) 등 포함

### 누구를 위한 것인가?

- Rails 8을 배우려는 한국 개발자
- Hotwire로 현대적인 UX를 구현하려는 팀
- 기존 Rails 프로젝트에 Hotwire를 추가하려는 개발자
- 풀스택 웹 애플리케이션을 빠르게 구축하려는 스타트업

### 주요 기능 요약

| 기능 | 설명 |
|------|------|
| 프로젝트 설정 | Rails 8 프로젝트 생성 및 초기 구조 설정 |
| Hotwire | Turbo Drive/Frame/Stream, Stimulus 구현 |
| 데이터 모델 | ActiveRecord 패턴 및 쿼리 최적화 |
| 컨트롤러 | RESTful 패턴 및 서비스 객체 |
| 뷰 템플릿 | 부분 렌더링, 컴포넌트, 폼 처리 |
| 인증/인가 | Devise, Pundit, OAuth 통합 |
| 실시간 기능 | ActionCable, Turbo Streams 실시간 업데이트 |
| 백그라운드 작업 | Solid Queue, Sidekiq 배경 작업 처리 |
| 테스트 | RSpec, Factory Bot 테스트 작성 |
| 배포 | Kamal, Docker, 클라우드 배포 |
| 자동화 스킬 | 스캐폴드, 인증 설정, N+1 탐지 등 |

---

## 빠른 시작

### 1. 플러그인 설치 확인

플러그인이 올바르게 설치되었는지 확인합니다.

```bash
# Claude Code에서 스킬 목록 확인
# /rails8-hotwire:rails8-core 등의 형식으로 호출
```

플러그인이 로드되면 다음과 같은 메시지가 나타납니다:

```
Rails 8 + Hotwire 플러그인이 활성화되었습니다.
20개의 스킬과 16개의 전문 에이전트를 사용할 수 있습니다.
```

### 2. 첫 번째 사용 예제

**새 Rails 8 프로젝트 생성하기:**

```bash
# Claude Code에서 요청
새 Rails 8 프로젝트를 생성해주세요.
PostgreSQL, Tailwind CSS를 포함하고 싶어요.
```

또는 직접 스킬 호출:

```bash
/rails8-hotwire:rails8-core

# 또는
/rails8-hotwire:rails8-core
```

프로젝트가 생성되고 초기 구조가 자동으로 설정됩니다.

### 3. 기본 명령어

모든 스킬은 슬래시(`/`) 다음에 스킬 이름으로 호출됩니다.

```bash
# 메인 스킬
/rails8-hotwire                         # 메인 가이드

# 지식 기반 스킬 (10개)
/rails8-hotwire:rails8-core             # 프로젝트 설정
/rails8-hotwire:rails8-turbo            # Turbo + Stimulus
/rails8-hotwire:rails8-models           # 모델 & 쿼리
/rails8-hotwire:rails8-controllers      # 컨트롤러
/rails8-hotwire:rails8-views            # 뷰 & 컴포넌트
/rails8-hotwire:rails8-auth             # 인증 & 인가
/rails8-hotwire:rails8-realtime         # 실시간 기능
/rails8-hotwire:rails8-background       # 배경 작업
/rails8-hotwire:rails8-testing          # 테스트
/rails8-hotwire:rails8-deploy           # 배포

# 자동화 스킬 (10개)
/rails8-hotwire:rails-autopilot         # Rails 앱 자동 생성
/rails8-hotwire:scaffold-plus           # 향상된 스캐폴딩
/rails8-hotwire:turbo-wizard            # Turbo 설정 마법사
/rails8-hotwire:stimulus-gen            # Stimulus 컨트롤러 생성
/rails8-hotwire:auth-setup              # 인증 설정 마법사
/rails8-hotwire:deploy-kamal            # Kamal 배포 자동화
/rails8-hotwire:test-gen                # 테스트 생성기
/rails8-hotwire:n1-hunter               # N+1 쿼리 탐지
/rails8-hotwire:solid-setup             # Solid Trifecta 설정
/rails8-hotwire:hotwire-debug           # Hotwire 디버깅
```

---

## 스킬 사용법

### 스킬 분류

플러그인의 20개 스킬은 2가지 카테고리로 나뉩니다:

#### 1. 지식 기반 스킬 (10개)

Rails 8 개발의 핵심 개념과 패턴을 다룹니다:
- `rails8-core`, `rails8-turbo`, `rails8-models`, `rails8-controllers`, `rails8-views`
- `rails8-auth`, `rails8-realtime`, `rails8-background`, `rails8-testing`, `rails8-deploy`

#### 2. 자동화 스킬 (10개)

특정 작업을 자동화하는 도구 스킬입니다:
- `rails-autopilot`, `scaffold-plus`, `turbo-wizard`, `stimulus-gen`, `auth-setup`
- `deploy-kamal`, `test-gen`, `n1-hunter`, `solid-setup`, `hotwire-debug`

---

### 스킬 1: Rails 8 코어 설정 (`rails8-core`)

#### 호출 방법

```bash
/rails8-hotwire:rails8-core
```

#### 사용 시나리오

- 새 Rails 8 프로젝트를 시작할 때
- 프로젝트 폴더 구조를 설계할 때
- Gemfile에 필수 젬을 추가할 때
- 서비스 객체, 폼 객체, 쿼리 객체 패턴을 배울 때

#### 포함 내용

| 항목 | 설명 |
|------|------|
| 프로젝트 생성 | Rails 8 프로젝트 생성 명령어 및 권장 옵션 |
| 폴더 구조 | `app/services`, `app/queries`, `app/forms` 등 표준 구조 |
| Gemfile 구성 | 필수 및 권장 젬 목록 |
| 데이터베이스 | PostgreSQL 설정 및 마이그레이션 |
| 환경 변수 | Credentials 및 ENV 관리 |
| 서비스 객체 | 비즈니스 로직 분리 패턴 |
| 폼 객체 | 복잡한 폼 처리 패턴 |
| 쿼리 객체 | 재사용 가능한 쿼리 패턴 |

#### 예제

**새 프로젝트 생성:**

```bash
rails new myapp \
  --database=postgresql \
  --css=tailwind \
  --skip-jbuilder \
  --skip-action-mailbox

cd myapp
```

**서비스 객체 예제:**

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

# 사용법
result = Posts::CreateService.new(user: current_user, params: post_params).call

if result.success?
  redirect_to result.value
else
  render :new, status: :unprocessable_entity
end
```

---

### 스킬 2: Hotwire 기초 (`rails8-turbo`)

#### 호출 방법

```bash
/rails8-hotwire:rails8-turbo
```

#### 사용 시나리오

- 페이지 전환을 빠르게 만들고 싶을 때 (Turbo Drive)
- 페이지 일부만 업데이트하고 싶을 때 (Turbo Frame)
- 실시간으로 UI를 갱신하고 싶을 때 (Turbo Stream)
- 클라이언트 인터랙션을 추가하고 싶을 때 (Stimulus)

#### 포함 내용

| 항목 | 설명 |
|------|------|
| Turbo Drive | SPA 스타일의 빠른 페이지 전환 |
| Turbo Frame | 페이지 일부 영역만 교체 |
| Turbo Stream | 실시간 다중 요소 업데이트 |
| Turbo Morphing | DOM 스마트 업데이트 (Rails 8) |
| Stimulus 기초 | 클라이언트 인터랙션 컨트롤러 |
| 패턴들 | 인라인 편집, 라이브 검색, 모달 등 |

#### 예제

**Turbo Frame 인라인 편집:**

```erb
<!-- app/views/articles/show.html.erb -->
<%= turbo_frame_tag dom_id(@article) do %>
  <h1><%= @article.title %></h1>
  <p><%= @article.body %></p>
  <%= link_to "수정", edit_article_path(@article) %>
<% end %>

<!-- app/views/articles/edit.html.erb -->
<%= turbo_frame_tag dom_id(@article) do %>
  <%= form_with model: @article do |f| %>
    <%= f.text_field :title %>
    <%= f.text_area :body %>
    <%= f.submit "저장" %>
    <%= link_to "취소", @article %>
  <% end %>
<% end %>
```

**Stimulus 토글 컨트롤러:**

```javascript
// app/javascript/controllers/toggle_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["content"]
  static values = { open: { type: Boolean, default: false } }

  toggle() {
    this.openValue = !this.openValue
  }

  openValueChanged(isOpen) {
    this.contentTarget.classList.toggle("hidden", !isOpen)
  }
}
```

---

### 스킬 3: 데이터 모델 (`rails8-models`)

#### 호출 방법

```bash
/rails8-hotwire:rails8-models
```

#### 사용 시나리오

- 데이터베이스 테이블을 설계할 때
- ActiveRecord 모델을 만들 때
- 복잡한 쿼리를 최적화할 때
- 모델 검증과 콜백을 설정할 때
- N+1 문제를 해결할 때

#### 포함 내용

| 항목 | 설명 |
|------|------|
| 마이그레이션 | 테이블 생성 및 구조 변경 |
| 연관 관계 | has_many, belongs_to, has_and_belongs_to_many |
| 검증 | validates 규칙 및 커스텀 검증 |
| 콜백 | before_save, after_create 등 |
| 스코프 | 재사용 가능한 쿼리 정의 |
| 쿼리 최적화 | includes, eager_load, N+1 방지 |
| 트랜잭션 | 데이터 일관성 보장 |

#### 예제

**모델 정의:**

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  belongs_to :user
  has_many :comments, dependent: :destroy
  has_many :tags, through: :taggings

  validates :title, presence: true, length: { minimum: 5 }
  validates :body, presence: true

  scope :published, -> { where(published: true) }
  scope :recent, -> { order(created_at: :desc) }

  before_save :generate_slug

  private

  def generate_slug
    self.slug = title.parameterize
  end
end
```

**쿼리 최적화:**

```ruby
# 나쁜 예: N+1 문제
posts = Post.all
posts.each do |post|
  puts post.user.name  # 매번 데이터베이스 쿼리
end

# 좋은 예: 한 번에 로드
posts = Post.includes(:user)
posts.each do |post|
  puts post.user.name  # 이미 로드됨
end
```

---

### 스킬 4: 컨트롤러 (`rails8-controllers`)

#### 호출 방법

```bash
/rails8-hotwire:rails8-controllers
```

#### 사용 시나리오

- RESTful 액션을 구현할 때
- 요청을 처리하고 응답을 반환할 때
- Turbo 스트림 응답을 만들 때
- 폼 제출을 처리할 때
- 에러를 처리할 때

#### 포함 내용

| 항목 | 설명 |
|------|------|
| RESTful 액션 | index, show, new, create, edit, update, destroy |
| 응답 형식 | HTML, JSON, Turbo Stream 처리 |
| Turbo 통합 | turbo_stream 응답 |
| 에러 처리 | status codes, rescue 블록 |
| 필터 | before_action, authorize 등 |
| 강한 매개변수 | require, permit 보안 |

#### 예제

**RESTful 컨트롤러:**

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  before_action :set_post, only: [:show, :edit, :update, :destroy]

  def index
    @posts = PostsQuery.new.call(filter_params)
  end

  def create
    @post = Post.new(post_params)

    if @post.save
      redirect_to @post, notice: "생성되었습니다"
    else
      render :new, status: :unprocessable_entity
    end
  end

  def update
    if @post.update(post_params)
      respond_to do |format|
        format.html { redirect_to @post }
        format.turbo_stream do
          render turbo_stream: turbo_stream.replace(@post, @post)
        end
      end
    else
      render :edit, status: :unprocessable_entity
    end
  end

  private

  def set_post
    @post = Post.find(params[:id])
  end

  def post_params
    params.require(:post).permit(:title, :body, :published)
  end
end
```

---

### 스킬 5: 뷰 & 컴포넌트 (`rails8-views`)

#### 호출 방법

```bash
/rails8-hotwire:rails8-views
```

#### 사용 시나리오

- HTML 레이아웃을 설계할 때
- 부분 템플릿(Partial)을 만들 때
- ViewComponent로 재사용 가능한 컴포넌트를 만들 때
- 폼을 구현할 때
- Tailwind CSS로 스타일링할 때

#### 포함 내용

| 항목 | 설명 |
|------|------|
| 레이아웃 | application.html.erb, 다중 레이아웃 |
| 부분 템플릿 | 재사용 가능한 뷰 조각 |
| ViewComponent | 객체지향 컴포넌트 |
| 폼 헬퍼 | form_with, 커스텀 폼 빌더 |
| Tailwind CSS | 스타일링 및 다크모드 |
| 에러 표시 | 폼 검증 에러 표시 |

#### 예제

**ViewComponent 정의:**

```ruby
# app/components/button_component.rb
class ButtonComponent < ViewComponent::Base
  def initialize(label:, variant: "primary", size: "md", **html_attributes)
    @label = label
    @variant = variant
    @size = size
    @html_attributes = html_attributes
  end

  def css_classes
    "btn btn-#{@variant} btn-#{@size}"
  end
end
```

```erb
<!-- app/components/button_component.html.erb -->
<button class="<%= css_classes %>" <%= html_attributes %>>
  <%= @label %>
</button>

<!-- 사용법 -->
<%= render ButtonComponent.new(label: "저장", variant: "success") %>
```

**복잡한 폼:**

```erb
<!-- app/views/posts/_form.html.erb -->
<%= form_with model: @post, local: true do |f| %>
  <% if @post.errors.any? %>
    <div class="alert alert-danger">
      <%= @post.errors.full_messages.join(", ") %>
    </div>
  <% end %>

  <div class="mb-4">
    <%= f.label :title %>
    <%= f.text_field :title, class: "form-input" %>
  </div>

  <div class="mb-4">
    <%= f.label :body %>
    <%= f.text_area :body, rows: 10, class: "form-input" %>
  </div>

  <%= f.submit "저장", class: "btn btn-primary" %>
<% end %>
```

---

### 스킬 6: 인증 & 인가 (`rails8-auth`)

#### 호출 방법

```bash
/rails8-hotwire:rails8-auth
```

#### 사용 시나리오

- 사용자 로그인/로그아웃을 구현할 때
- 역할 기반 접근 제어(RBAC)를 설정할 때
- OAuth (Google, GitHub)로 소셜 로그인을 추가할 때
- 2단계 인증(2FA)을 구현할 때
- API 토큰 인증을 추가할 때

#### 포함 내용

| 항목 | 설명 |
|------|------|
| Devise | 사용자 인증 및 세션 관리 |
| Pundit | 정책 기반 인가 |
| OAuth | Google, GitHub, Apple 소셜 로그인 |
| 2FA | 이중 인증 구현 |
| 매직 링크 | 이메일 링크로 로그인 |
| 초대 | 사용자 초대 메커니즘 |
| API 토큰 | 토큰 기반 인증 |

#### 예제

**Devise 설정:**

```bash
bundle add devise
rails generate devise:install
rails generate devise User
rails db:migrate
```

**Pundit 정책:**

```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  def show?
    true  # 모든 사용자가 볼 수 있음
  end

  def create?
    user.present?  # 로그인한 사용자만 생성
  end

  def update?
    user == record.user  # 작성자만 수정
  end

  def destroy?
    user == record.user || user.admin?  # 작성자 또는 관리자만 삭제
  end
end
```

**컨트롤러에서 사용:**

```ruby
class PostsController < ApplicationController
  def show
    @post = Post.find(params[:id])
    authorize @post
  end

  def update
    @post = Post.find(params[:id])
    authorize @post

    if @post.update(post_params)
      redirect_to @post
    else
      render :edit, status: :unprocessable_entity
    end
  end
end
```

---

### 스킬 7: 실시간 기능 (`rails8-realtime`)

#### 호출 방법

```bash
/rails8-hotwire:rails8-realtime
```

#### 사용 시나리오

- WebSocket으로 실시간 알림을 보낼 때
- 여러 사용자가 동시에 같은 페이지를 볼 때 갱신할 때
- 채팅 또는 협업 기능을 만들 때
- 라이브 업데이트를 보여줄 때

#### 포함 내용

| 항목 | 설명 |
|------|------|
| ActionCable 기초 | WebSocket 채널 설정 |
| Turbo Broadcasts | 모델 변경을 자동 브로드캐스트 |
| 커스텀 Streams | 특정 이벤트 브로드캐스팅 |
| 알림 | 사용자별 실시간 알림 |
| 협업 | 여러 사용자의 동시 편집 |
| 배포 | Kamal에서 WebSocket 설정 |

#### 예제

**Turbo Broadcasts:**

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  broadcasts_to ->(post) { :posts }, inserts_by: :prepend
end

# 저장하면 자동으로 모든 구독자에게 전송됨
post = Post.create(title: "새 글", body: "내용")
```

**커스텀 채널:**

```ruby
# app/channels/chat_channel.rb
class ChatChannel < ApplicationCable::Channel
  def subscribed
    stream_for @room
  end

  def send_message(data)
    message = Message.create(content: data["content"], room: @room)
    ChatChannel.broadcast_to(@room, { message: message })
  end
end
```

---

### 스킬 8: 백그라운드 작업 (`rails8-background`)

#### 호출 방법

```bash
/rails8-hotwire:rails8-background
```

#### 사용 시나리오

- 이메일을 비동기로 보낼 때
- 이미지를 처리할 때
- 정기적인 작업을 실행할 때 (크론 작업)
- 무거운 데이터 처리를 뒤로 미룰 때

#### 포함 내용

| 항목 | 설명 |
|------|------|
| Solid Queue | Redis 없이 DB 기반 작업 큐 (Rails 8 기본) |
| Sidekiq | Redis 기반 강력한 작업 처리 |
| 메일러 | 비동기 이메일 전송 |
| 작업 스케줄링 | Cron 작업 정의 |
| 에러 처리 | 실패한 작업 재시도 |
| 모니터링 | 작업 상태 확인 |

#### 예제

**Solid Queue 작업:**

```ruby
# app/jobs/send_email_job.rb
class SendEmailJob < ApplicationJob
  queue_as :default

  def perform(user_id)
    user = User.find(user_id)
    UserMailer.welcome(user).deliver_now
  end
end

# 호출
SendEmailJob.perform_later(current_user.id)
```

**스케줄링:**

```ruby
# config/initializers/solid_queue.rb
Solid::Queue.configure do |config|
  config.recurring_tasks = [
    { key: "daily_summary", schedule: "0 9 * * *", command: -> { DailySummaryJob.perform_later } }
  ]
end
```

---

### 스킬 9: 테스트 (`rails8-testing`)

#### 호출 방법

```bash
/rails8-hotwire:rails8-testing
```

#### 사용 시나리오

- 모델 테스트를 작성할 때
- 컨트롤러 테스트를 작성할 때
- 통합 테스트(시스템 테스트)를 작성할 때
- Turbo 상호작용을 테스트할 때

#### 포함 내용

| 항목 | 설명 |
|------|------|
| RSpec 기초 | 테스트 프레임워크 |
| 모델 스펙 | 모델 검증 및 메서드 테스트 |
| 요청 스펙 | HTTP 요청 테스트 |
| 시스템 스펙 | 브라우저 자동화 테스트 |
| Factory Bot | 테스트 데이터 생성 |
| Faker | 무작위 테스트 데이터 |

#### 예제

**RSpec 테스트:**

```ruby
# spec/models/post_spec.rb
RSpec.describe Post, type: :model do
  describe "검증" do
    it { is_expected.to validate_presence_of(:title) }
    it { is_expected.to validate_presence_of(:body) }
  end

  describe "연관 관계" do
    it { is_expected.to belong_to(:user) }
    it { is_expected.to have_many(:comments) }
  end
end
```

**시스템 테스트:**

```ruby
# spec/system/posts_spec.rb
RSpec.describe "Posts", type: :system do
  let(:user) { create(:user) }

  it "새 글을 작성할 수 있다" do
    login_as user
    visit posts_path
    click_link "새 글 작성"

    fill_in "제목", with: "테스트 글"
    fill_in "내용", with: "테스트 내용"
    click_button "저장"

    expect(page).to have_text("생성되었습니다")
  end
end
```

---

### 스킬 10: 배포 (`rails8-deploy`)

#### 호출 방법

```bash
/rails8-hotwire:rails8-deploy
```

#### 사용 시나리오

- Kamal로 서버에 배포할 때
- Docker 이미지를 만들 때
- 데이터베이스를 설정할 때
- 파일 저장소(S3, Cloudflare R2)를 연결할 때
- 프로덕션 모니터링을 설정할 때

#### 포함 내용

| 항목 | 설명 |
|------|------|
| Kamal | Zero-downtime 배포 |
| Docker | 컨테이너화 |
| PostgreSQL | 데이터베이스 설정 |
| S3 / Cloudflare R2 | 파일 저장소 |
| Render, Railway, Fly.io | PaaS 배포 |
| 모니터링 | Sentry, 로깅 |
| SSL 인증서 | Let's Encrypt |

#### 예제

**Kamal 배포:**

```bash
bundle add kamal
kamal init
# config/deploy.yml 수정
kamal deploy
```

**Docker Dockerfile:**

```dockerfile
FROM ruby:3.3-slim

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential postgresql-client
COPY Gemfile Gemfile.lock ./
RUN bundle install --without development test
COPY . .

RUN bundle exec rake assets:precompile

EXPOSE 3000
CMD ["bundle", "exec", "rails", "s", "-b", "0.0.0.0"]
```

---

## 에이전트 사용법

### 16개 에이전트 목록

플러그인에는 16개의 전문 에이전트가 포함되어 있습니다. 각 에이전트는 특정 작업에 최적화되어 있습니다.

#### 에이전트 분류

| 역할 | 에이전트 | 모델 | 최적 사용 |
|------|---------|------|---------|
| 아키텍처 | rails-architect | Opus | Rails 아키텍처 설계 및 분석 |
| | rails-architect-low | Haiku | 빠른 구조 확인 |
| 구현 | rails-executor | Sonnet | Rails 코드 구현 |
| | rails-executor-high | Opus | 복잡한 리팩토링 |
| Hotwire | hotwire-specialist | Sonnet | Turbo/Stimulus 패턴 |
| | hotwire-specialist-high | Opus | 복잡한 Hotwire 아키텍처 |
| 테스트 | rspec-tester | Sonnet | RSpec 테스트 작성 |
| | rspec-tester-low | Haiku | 빠른 테스트 검증 |
| 코드 리뷰 | rails-reviewer | Opus | 심층 코드 리뷰 |
| | rails-reviewer-low | Haiku | 빠른 코드 체크 |
| 디버깅 | turbo-debugger | Opus | Turbo/Stimulus 디버깅 |
| 배포 | kamal-deployer | Sonnet | Kamal 배포 자동화 |
| 인증 | devise-specialist | Sonnet | Devise 설정 및 OAuth |
| DB 최적화 | activerecord-optimizer | Sonnet | 쿼리 최적화, N+1 탐지 |
| 프론트엔드 | stimulus-designer | Sonnet | Stimulus 컨트롤러 설계 |
| 마이그레이션 | rails-migrator | Sonnet | DB 마이그레이션 관리 |

### 에이전트 자동 호출

에이전트는 상황에 따라 자동으로 호출됩니다.

| 상황 | 자동 호출 에이전트 |
|------|-----------------|
| "Rails 8 프로젝트를 만들어줘" | rails-architect → rails-executor |
| "이 코드를 분석해줘" | rails-architect |
| "Turbo 패턴을 찾아줘" | hotwire-specialist |
| "Stimulus 컴포넌트를 만들어줘" | stimulus-designer |
| "테스트를 작성해줘" | rspec-tester |
| "배포를 도와줘" | kamal-deployer |
| "Devise를 설정해줘" | devise-specialist |
| "N+1 쿼리를 찾아줘" | activerecord-optimizer |

### 에이전트 직접 호출

에이전트는 Task 도구를 통해 자동으로 선택됩니다. 직접 지정이 필요한 경우:

```bash
# 빠른 분석 (Haiku)
"rails-architect-low로 이 코드의 구조를 확인해줘"

# 일반 구현 (Sonnet)
"rails-executor로 Devise를 프로젝트에 통합해줘"

# 복잡한 분석 (Opus)
"rails-architect로 이 애플리케이션의 확장 가능한 구조를 설계해줘"

# Hotwire 전문
"hotwire-specialist로 Turbo Stream 패턴을 적용해줘"

# 테스트 작성
"rspec-tester로 모델 테스트를 작성해줘"
```

---

## 파이프라인 사용법

### 6개 내장 파이프라인

파이프라인은 여러 에이전트를 자동으로 연결하여 복잡한 작업을 처리합니다.

**호출 방법:** `/rails8:pipeline <name>` 또는 자연어로 요청

#### 파이프라인 1: 인증 (auth)

**구성:** devise-specialist → rails-executor → devise-specialist → rspec-tester

**사용:** 인증 시스템을 처음부터 구축할 때

```bash
/rails8:pipeline auth
"이메일/패스워드와 Google OAuth로 인증을 설정해주세요"
```

**과정:**
1. devise-specialist가 Devise 또는 Rails 8 기본 인증 설정
2. rails-executor가 인증 뷰 생성
3. devise-specialist가 Pundit 정책 설정
4. rspec-tester가 인증 테스트 작성

#### 파이프라인 2: CRUD (crud)

**구성:** rails-executor → rails-executor → hotwire-specialist → rspec-tester

**사용:** Turbo 통합된 CRUD 리소스를 생성할 때

```bash
/rails8:pipeline crud
"Post 리소스를 title, body, published 필드로 생성해주세요"
```

**과정:**
1. rails-executor가 모델과 마이그레이션 생성
2. rails-executor가 컨트롤러와 뷰 생성
3. hotwire-specialist가 Turbo Frame/Stream 통합
4. rspec-tester가 요청/시스템 스펙 작성

#### 파이프라인 3: 배포 (deploy)

**구성:** kamal-deployer → kamal-deployer → kamal-deployer → kamal-deployer

**사용:** 프로덕션 배포 인프라를 설정할 때

```bash
/rails8:pipeline deploy
"Hetzner VPS에 SSL과 함께 배포해주세요"
```

**과정:**
1. kamal-deployer가 Dockerfile 최적화
2. kamal-deployer가 Kamal 설정 생성
3. kamal-deployer가 GitHub Actions 워크플로우 생성
4. kamal-deployer가 배포 실행

#### 파이프라인 4: 기능 구현 (feature)

**구성:** rails-architect → rspec-tester → rails-executor → hotwire-specialist → rails-reviewer

**사용:** TDD 방식으로 새 기능을 구현할 때

```bash
/rails8:pipeline feature
"실시간 업데이트가 있는 알림 시스템을 구현해주세요"
```

**과정:**
1. rails-architect가 요구사항 분석 및 구현 계획 수립
2. rspec-tester가 테스트 먼저 작성
3. rails-executor가 테스트 통과하도록 구현
4. hotwire-specialist가 Turbo/Stimulus 통합
5. rails-reviewer가 코드 품질, 보안, 성능 검토

#### 파이프라인 5: 리팩토링 (refactor)

**구성:** rails-architect → rspec-tester → rails-executor-high → rspec-tester

**사용:** 기존 코드를 안전하게 리팩토링할 때

```bash
/rails8:pipeline refactor
"PostsController에서 서비스 객체를 추출해주세요"
```

**과정:**
1. rails-architect가 리팩토링 대상 분석 및 계획 수립
2. rspec-tester가 기준 테스트 커버리지 확보
3. rails-executor-high가 리팩토링 실행
4. rspec-tester가 모든 테스트 통과 확인

#### 파이프라인 6: 테스트 (test)

**구성:** rails-architect-low → rspec-tester → rails-executor → rspec-tester-low

**사용:** 기존 코드에 TDD 워크플로우를 적용할 때

```bash
/rails8:pipeline test
"User 모델에 테스트를 추가해주세요"
```

**과정:**
1. rails-architect-low가 테스트 대상 빠르게 분석
2. rspec-tester가 RSpec 테스트 작성
3. rails-executor가 실패하는 테스트 수정 (조건부)
4. rspec-tester-low가 최종 검증

---

## 훅 동작 설명

### 6개 자동 훅

훅은 특정 이벤트에서 자동으로 실행되는 검사입니다. 4개의 이벤트에서 6개의 스크립트가 동작합니다.

#### 훅 1: Rails 프로젝트 감지 (rails-detector)

**이벤트:** `SessionStart`

**동작:** 세션 시작 시 Rails 프로젝트 여부를 감지합니다.

**체크하는 내용:**
- Gemfile에 `rails` 젬이 있는가?
- Rails 8 프로젝트인가?
- Hotwire 관련 젬이 설치되어 있는가?

**결과:**
- Rails 프로젝트 감지 시 플러그인 기능 활성화
- 비Rails 프로젝트에서는 자동으로 비활성화

#### 훅 2: 컨벤션 검증 (convention-validator)

**이벤트:** `UserPromptSubmit`

**동작:** 사용자 요청이 Rails 컨벤션을 따르는지 검증합니다.

**체크하는 내용:**
- 모델명이 단수형인가?
- 컨트롤러명이 복수형인가?
- RESTful 라우트 패턴을 따르는가?

**결과:**
- 컨벤션 위반 시 올바른 패턴 제안
- Rails 베스트 프랙티스 가이드

#### 훅 3: 마이그레이션 보호 (migration-guard)

**이벤트:** `PreToolUse` (Edit/Write 도구 사용 시)

**동작:** 마이그레이션 파일 수정을 감지하고 검증합니다.

**체크하는 내용:**
- 외래키에 인덱스가 있는가?
- NOT NULL 제약이 적절한가?
- 되돌릴 수 없는 마이그레이션인가?

**경고 메시지:**
```
주의: 외래키에 인덱스가 없습니다.
마이그레이션에 다음을 추가하세요:
  add_index :posts, :user_id
```

#### 훅 4: 테스트 강제 (test-enforcer)

**이벤트:** `PreToolUse` (Edit/Write 도구 사용 시)

**동작:** 새 모델/컨트롤러 생성 시 테스트 파일 존재 여부를 확인합니다.

**체크하는 내용:**
- 모델에 해당하는 스펙 파일이 있는가?
- 컨트롤러에 해당하는 요청 스펙이 있는가?

**경고 메시지:**
```
주의: Post 모델에 테스트가 없습니다.
테스트 파일을 생성하세요:
  spec/models/post_spec.rb
```

#### 훅 5: 배포 안전 (deploy-safety)

**이벤트:** `PreToolUse` (Bash 도구 사용 시)

**동작:** 배포 관련 명령어 실행 전 안전 검사를 수행합니다.

**체크하는 내용:**
- kamal deploy 실행 전 테스트 통과 여부
- 환경 변수 설정 여부
- 위험한 명령어 감지 (force push, db:drop 등)

**경고 메시지:**
```
주의: 배포 전 체크리스트:
  [ ] bundle exec rspec (모든 테스트 통과)
  [ ] 환경 변수 설정 확인
  [ ] 위험 명령어 경고
```

#### 훅 6: Turbo 응답 확인 (turbo-response-check)

**이벤트:** `PostToolUse` (Edit/Write 도구 사용 후)

**동작:** 컨트롤러 수정 후 Turbo 호환성을 확인합니다.

**체크하는 내용:**
- 폼 에러 시 422 상태 코드 사용 여부
- 리다이렉트 시 303 상태 코드 사용 여부
- Turbo Stream 응답 형식

**경고 메시지:**
```
주의: 폼 에러 시 상태 코드가 없습니다.
수정:
  render :edit, status: :unprocessable_entity
```

---

## 실전 시나리오

### 시나리오 1: 새 Rails 8 프로젝트 시작하기

**목표:** 완전히 새로운 Rails 8 + Hotwire 프로젝트를 만들기

#### 단계 1: 프로젝트 생성

```bash
# Claude Code에서
새 Rails 8 프로젝트를 생성해주세요.
이름: myblog
데이터베이스: PostgreSQL
CSS: Tailwind
```

또는 수동으로:

```bash
rails new myblog --database=postgresql --css=tailwind --skip-jbuilder

cd myblog
```

#### 단계 2: 필수 젬 추가

```bash
bundle add pagy pundit faraday

# 개발 환경
bundle add --group development rspec-rails factory_bot_rails faker
bundle add --group development annotate bullet rubocop-rails-omakase
```

#### 단계 3: 폴더 구조 설정

```bash
mkdir -p app/services
mkdir -p app/queries
mkdir -p app/forms
mkdir -p app/policies
mkdir -p app/presenters
```

#### 단계 4: RSpec 설정

```bash
rails generate rspec:install
```

#### 단계 5: 인증 설정

```bash
# Rails 8 기본 인증
bin/rails generate authentication

# 또는 Devise 사용
bundle add devise
rails generate devise:install
rails generate devise User
```

#### 단계 6: 첫 모델 생성

```bash
# 블로그 글 모델
rails generate model Post user:references title:string body:text published:boolean slug:string --index

# 댓글 모델
rails generate model Comment user:references post:references body:text --index

rails db:migrate
```

#### 단계 7: 첫 컨트롤러 생성

```bash
rails generate controller Posts index show new create edit update destroy
```

#### 단계 8: Hotwire 설정

Gemfile에 다음이 이미 포함되어 있는지 확인:

```ruby
gem "turbo-rails"
gem "stimulus-rails"
```

### 시나리오 2: 기존 프로젝트에 Hotwire 추가하기

**목표:** Rails 6/7 프로젝트를 Hotwire로 업그레이드

#### 단계 1: Hotwire 젬 추가

```bash
bundle add turbo-rails stimulus-rails
bundle install
```

#### 단계 2: JavaScript 통합

```bash
rails javascript:install:esbuild
```

#### 단계 3: Turbo 드라이브 활성화

```erb
<!-- app/views/layouts/application.html.erb -->
<%= turbo_include_tags %>
```

#### 단계 4: 첫 Turbo Frame 추가

```erb
<!-- app/views/posts/index.html.erb -->
<%= turbo_frame_tag "posts" do %>
  <% @posts.each do |post| %>
    <%= render post %>
  <% end %>
<% end %>
```

#### 단계 5: 컨트롤러 수정

```ruby
def create
  @post = Post.new(post_params)

  if @post.save
    redirect_to @post, status: :see_other
  else
    render :new, status: :unprocessable_entity
  end
end
```

### 시나리오 3: 인증 시스템 구축하기

**목표:** Devise와 Pundit으로 완전한 사용자 관리 시스템 만들기

#### 단계 1: Devise 설정

```bash
bundle add devise
rails generate devise:install
rails generate devise User
rails db:migrate
```

#### 단계 2: Devise 뷰 커스터마이징

```bash
rails generate devise:views
# app/views/devise 디렉토리 생성
```

#### 단계 3: Pundit 정책 생성

```bash
# 정책 기본 클래스
rails generate pundit:install
```

```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  def index?
    true
  end

  def show?
    true
  end

  def create?
    user.present?
  end

  def update?
    user == record.user
  end

  def destroy?
    user == record.user || user.admin?
  end
end
```

#### 단계 4: 컨트롤러 보호

```ruby
class PostsController < ApplicationController
  before_action :authenticate_user!, except: [:index, :show]

  def create
    authorize Post
    @post = current_user.posts.build(post_params)
    # ...
  end
end
```

#### 단계 5: Turbo와 Devise 통합

```ruby
# app/javascript/controllers/authentication_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  logout() {
    fetch("/users/sign_out", {
      method: "DELETE",
      headers: {
        "X-CSRF-Token": document.querySelector("[name='csrf-token']").content
      }
    }).then(() => {
      window.location.href = "/"
    })
  }
}
```

### 시나리오 4: 실시간 기능 구현하기

**목표:** 채팅 애플리케이션에 실시간 메시지 업데이트 추가

#### 단계 1: 메시지 모델 생성

```bash
rails generate model Message user:references conversation:references body:text
rails db:migrate
```

#### 단계 2: 모델에 broadcast 추가

```ruby
# app/models/message.rb
class Message < ApplicationRecord
  belongs_to :user
  belongs_to :conversation

  # 메시지가 생성되면 모든 구독자에게 전송
  broadcasts_to ->(message) { message.conversation }
end
```

#### 단계 3: 채널 구독

```erb
<!-- app/views/conversations/show.html.erb -->
<%= turbo_stream_from @conversation %>

<div id="messages">
  <%= render @conversation.messages %>
</div>

<%= form_with model: [@conversation, Message.new], local: true do |f| %>
  <%= f.text_area :body %>
  <%= f.submit "전송" %>
<% end %>
```

#### 단계 4: 메시지 부분 템플릿

```erb
<!-- app/views/messages/_message.html.erb -->
<div id="<%= dom_id(message) %>" class="message">
  <strong><%= message.user.name %></strong>
  <p><%= message.body %></p>
  <small><%= time_ago_in_words(message.created_at) %> 전</small>
</div>
```

#### 단계 5: 컨트롤러 액션

```ruby
# app/controllers/messages_controller.rb
class MessagesController < ApplicationController
  def create
    @conversation = Conversation.find(params[:conversation_id])
    @message = @conversation.messages.build(message_params)
    @message.user = current_user

    if @message.save
      # 자동으로 broadcasts_to가 전송
      redirect_to @conversation
    else
      render :new, status: :unprocessable_entity
    end
  end
end
```

### 시나리오 5: Kamal로 배포하기

**목표:** 프로덕션 서버에 애플리케이션 배포

#### 단계 1: Kamal 설치

```bash
bundle add kamal
kamal init
```

#### 단계 2: 배포 설정

```yaml
# config/deploy.yml
service: myblog
image: user/myblog

servers:
  web:
    hosts:
      - 192.168.1.100

  db:
    hosts:
      - 192.168.1.100
    options:
      volumes:
        - /var/lib/postgresql/data

env:
  clear:
    RAILS_ENV: production
    DATABASE_URL: postgres://user:password@db/myblog

registry:
  username: user
  password:
    - KAMAL_REGISTRY_PASSWORD
```

#### 단계 3: 시크릿 설정

```bash
# 데이터베이스 암호
kamal env push DATABASE_PASSWORD

# Rails 암호화 키
kamal env push RAILS_MASTER_KEY
```

#### 단계 4: 첫 배포

```bash
# 서버 준비
kamal server bootstrap

# 배포
kamal deploy

# 데이터베이스 마이그레이션
kamal app exec "bin/rails db:migrate"
```

#### 단계 5: 무중단 배포

```bash
# 새 버전 배포 (무중단)
kamal deploy

# 로그 확인
kamal app logs

# 상태 확인
kamal app status
```

---

## 팁 & 트릭

### 팁 1: 빠른 프로젝트 생성

**문제:** 프로젝트 생성이 너무 오래 걸린다.

**해결:**

```bash
# 최소 옵션으로 빠르게 생성
rails new myapp \
  --minimal \
  --skip-bundle \
  --database=postgresql

cd myapp
# 필요한 것만 Gemfile에 추가
bundle install
```

### 팁 2: N+1 쿼리 자동 감지

**문제:** 성능이 느리고 데이터베이스 쿼리가 너무 많다.

**해결:**

```ruby
# Gemfile에 추가
gem 'bullet', groups: [:development, :test]

# config/environments/development.rb
config.after_initialize do
  Bullet.enable = true
  Bullet.alert = true
  Bullet.bullet_logger = true
end

# 개발 중에 경고가 표시됨
```

### 팁 3: Turbo Frame 디버깅

**문제:** Turbo Frame이 작동하지 않는다.

**확인 사항:**

```erb
<!-- 1. Frame ID가 있는가? -->
<%= turbo_frame_tag "posts" do %>
  <!-- 2. 폼 응답의 Frame ID가 일치하는가? -->
  <form action="/posts" method="post">
    <!-- 3. 상태 코드가 올바른가? (422 또는 303) -->
  </form>
<% end %>
```

**디버깅 방법:**

```javascript
// 브라우저 콘솔
document.addEventListener("turbo:before-frame-render", (event) => {
  console.log("Frame render:", event.detail);
})

document.addEventListener("turbo:frame-missing", (event) => {
  console.log("Frame not found:", event.detail);
})
```

### 팁 4: Stimulus 값 추적

**문제:** 상태 변경을 추적하기 어렵다.

**해결:**

```javascript
// Controller에서
openValueChanged(isOpen) {
  console.log("Open changed to:", isOpen);
  // 상태 변경 시 실행
}
```

### 팁 5: 개발 서버 성능

**문제:** 개발 중 서버가 너무 느리다.

**해결:**

```bash
# CSS와 JS 컴파일러 병렬 실행
./bin/dev

# 또는 분리해서 실행
./bin/rails server
./bin/js --watch
```

### 팁 6: 테스트 속도 향상

**문제:** 테스트가 너무 오래 걸린다.

**해결:**

```ruby
# spec/spec_helper.rb
RSpec.configure do |config|
  # 병렬 테스트 실행
  config.profile_examples = 10
end

# 실행
bundle exec rspec --parallel
```

### 팁 7: 효율적인 폼 검증

**문제:** 폼 검증 메시지가 명확하지 않다.

**해결:**

```ruby
# app/models/post.rb
validates :title, presence: { message: "제목을 입력하세요" }
validates :body, length: { minimum: 10, message: "최소 10자 이상입니다" }
```

### 팁 8: 재사용 가능한 부분 템플릿

**문제:** 같은 코드가 여러 곳에서 반복된다.

**해결:**

```erb
<!-- app/views/shared/_flash.html.erb -->
<% if notice %>
  <div class="alert alert-success"><%= notice %></div>
<% end %>
<% if alert %>
  <div class="alert alert-danger"><%= alert %></div>
<% end %>

<!-- 어디서든 사용 -->
<%= render "shared/flash" %>
```

### 팁 9: 효율적인 쿼리 작성

**문제:** 쿼리가 복잡하고 반복된다.

**해결:**

```ruby
# app/queries/published_posts_query.rb
class PublishedPostsQuery
  def initialize(scope = Post.all)
    @scope = scope
  end

  def call(filters = {})
    @scope
      .where(published: true)
      .then { |s| by_author(s, filters[:author_id]) }
      .then { |s| by_tag(s, filters[:tag]) }
      .includes(:user, :tags)
      .order(created_at: :desc)
  end

  private

  def by_author(scope, author_id)
    author_id.present? ? scope.where(user_id: author_id) : scope
  end

  def by_tag(scope, tag)
    tag.present? ? scope.joins(:tags).where(tags: { name: tag }) : scope
  end
end

# 사용
posts = PublishedPostsQuery.new.call(author_id: 1, tag: "rails")
```

### 자주 묻는 질문 (FAQ)

**Q: Turbo vs. Stimulus는 언제 사용하나?**

A:
- Turbo (80%): 페이지 전환, 부분 업데이트 자동 처리
- Stimulus (20%): 버튼 클릭, 드래그 등 DOM 이벤트 처리

**Q: Redis 없이 실시간 기능을 사용할 수 있나?**

A: 네! Rails 8의 Solid Cable을 사용하면 Redis 없이 WebSocket을 처리할 수 있습니다.

**Q: Devise를 사용해야 하나?**

A: Rails 8은 기본 인증을 제공하지만, Devise는 더 많은 기능(2FA, OAuth)을 제공합니다. 필요에 따라 선택하세요.

**Q: 테스트 커버리지는 어느 정도가 좋은가?**

A: 최소 70% 이상. 비즈니스 로직은 85%+ 권장.

**Q: 배포할 때 무엇을 확인해야 하나?**

A:
- 모든 테스트 통과 (`rspec`)
- 코드 스타일 검사 (`rubocop`)
- 데이터베이스 마이그레이션 준비
- 환경 변수 설정
- 로그 및 모니터링 설정

---

## 문제 해결

### 문제 1: Turbo Frame이 작동하지 않음

**증상:** 링크를 클릭해도 페이지가 새로고침되고 Frame이 업데이트되지 않음

**원인:**
1. Frame ID가 일치하지 않음
2. 상태 코드가 잘못됨
3. Turbo 라이브러리가 로드되지 않음

**해결:**

```ruby
# 1. 상태 코드 확인
def create
  @post = Post.new(post_params)
  if @post.save
    redirect_to @post, status: :see_other  # 303
  else
    render :new, status: :unprocessable_entity  # 422
  end
end

# 2. Frame ID 확인
<%= turbo_frame_tag "posts" do %>
  <!-- 응답도 같은 frame ID를 사용해야 함 -->
  <%= turbo_frame_tag "posts" do %>
    <!-- 콘텐츠 -->
  <% end %>
<% end %>
```

### 문제 2: 캐싱으로 인한 이전 버전 사용

**증상:** 코드를 변경했는데 변화가 보이지 않음

**원인:** 브라우저 캐시 또는 Rails 캐시

**해결:**

```bash
# 개발 서버 재시작
# Ctrl+C 후 다시 실행
./bin/rails server

# 또는 캐시 삭제
rails cache:clear

# 또는 브라우저 캐시 삭제
# Chrome: Ctrl+Shift+Delete
# Safari: Develop > Empty Web Storage
```

### 문제 3: 데이터베이스 마이그레이션 오류

**증상:** `rails db:migrate` 실행 시 에러

**원인:** 마이그레이션 문법 오류 또는 충돌

**해결:**

```bash
# 마이그레이션 상태 확인
rails db:migrate:status

# 마지막 마이그레이션 롤백
rails db:rollback

# 모든 마이그레이션 재실행
rails db:migrate:reset

# 특정 마이그레이션만 실행
rails db:migrate:up VERSION=20240101120000
```

### 문제 4: Devise 로그인 문제

**증상:** 로그인 폼을 작성했는데 작동하지 않음

**원인:** 라우트 설정 누락 또는 컨트롤러 필터 누락

**해결:**

```ruby
# config/routes.rb
devise_for :users

# app/controllers/posts_controller.rb
before_action :authenticate_user!

# 또는 특정 액션만
before_action :authenticate_user!, except: [:index, :show]
```

### 문제 5: Stimulus 컨트롤러가 로드되지 않음

**증상:** Stimulus 컨트롤러가 작동하지 않음

**원인:** 파일명 규칙 미준수 또는 자동 로드 설정 오류

**해결:**

```javascript
// 파일명: app/javascript/controllers/dropdown_controller.js
// (snake_case 필수)

// HTML에서:
// <div data-controller="dropdown">
// (컨트롤러 이름을 kebab-case로 사용)

// Stimulus 자동 로드 확인:
// app/javascript/application.js에서:
import { application } from "./application"
import * as Stimulus from "@hotwired/stimulus"

window.Stimulus = Stimulus
application.load(definitionsFromContext(
  require.context("./controllers", true, /.*_controller\.js$/)
))
```

### 문제 6: ActionCable (WebSocket) 연결 문제

**증상:** 실시간 업데이트가 작동하지 않음

**원인:** 개발 환경에서 WebSocket 미지원 또는 설정 오류

**해결:**

```ruby
# config/cable.yml
development:
  adapter: local

production:
  adapter: redis
  url: <%= ENV.fetch("REDIS_URL") { "redis://localhost:6379" } %>
  channel_prefix: myapp_production_

# config/environments/development.rb
config.action_cable.allowed_request_origins = [
  /http:\/\/localhost/,
  /http:\/\/127.0.0.1/
]
```

### 문제 7: 성능 문제

**증상:** 페이지 로드가 느림

**원인:** N+1 쿼리, 무거운 비즈니스 로직, 느린 외부 API

**해결:**

```ruby
# 1. N+1 감지
# Bullet gem 추가

# 2. 쿼리 최적화
Post.includes(:user, :comments).all  # GOOD
Post.all.each { |p| p.user }         # BAD: N+1

# 3. 캐싱 추가
Rails.cache.fetch("posts:all", expires_in: 1.hour) do
  Post.published.all
end

# 4. 백그라운드 작업으로 이동
Post::ProcessJob.perform_later(post_id)
```

### 문제 8: 배포 후 정적 자산이 로드되지 않음

**증상:** CSS/JS가 로드되지 않음

**원인:** Assets precompile 누락

**해결:**

```bash
# Kamal 배포 전에 실행
bundle exec rails assets:precompile

# 또는 Kamal이 자동으로 처리하도록 설정
# config/deploy.yml에서 build 설정 확인
```

### 문제 9: 프로덕션에서만 발생하는 버그

**증상:** 개발 환경에서는 잘 작동하는데 프로덕션에서 오류

**원인:** 환경 변수 누락, 권한 문제, 캐싱 문제

**해결:**

```bash
# 프로덕션 환경에서 로그 확인
kamal app logs

# 환경 변수 확인
kamal env status

# 데이터베이스 상태 확인
kamal app exec "bin/rails db:migrate:status"

# 캐시 삭제
kamal app exec "bin/rails cache:clear"
```

### 문제 10: 메모리 누수

**증상:** 시간이 지날수록 메모리 사용량 증가

**원인:** 캐시에 저장된 데이터, 이벤트 리스너 해제 안 됨

**해결:**

```ruby
# Solid Cache 메모리 한계 설정
Rails.application.config.solid_cache.store_options = {
  max_size: 100.megabytes
}

# Stimulus 컨트롤러에서 정리
disconnect() {
  // 이벤트 리스너 제거
  this.element.removeEventListener("click", this.handler)
}
```

---

## 결론

이 가이드는 Rails 8과 Hotwire로 현대적인 웹 애플리케이션을 만드는 데 필요한 모든 정보를 제공합니다.

**다음 단계:**

1. 빠른 시작 섹션을 따라 첫 프로젝트를 생성하세요
2. 실전 시나리오를 선택해 구현해보세요
3. 문제가 발생하면 문제 해결 섹션을 참조하세요
4. 팁 & 트릭으로 개발 효율성을 높이세요

**추가 리소스:**

- [Ruby on Rails 공식 문서](https://guides.rubyonrails.org/)
- [Hotwire 공식 문서](https://hotwired.dev/)
- [Turbo Handbook](https://turbo.hotwired.dev/)
- [Stimulus Handbook](https://stimulus.hotwired.dev/)

행운을 빕니다!
