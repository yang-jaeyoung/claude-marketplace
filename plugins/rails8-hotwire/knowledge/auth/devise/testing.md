# Devise Testing Patterns

## Overview

Comprehensive guide to testing Devise authentication in Rails 8 applications using RSpec and Minitest. Covers controller specs, request specs, feature specs, and test helpers.

## When to Use

- When writing authentication tests
- When testing protected resources
- When verifying sign in/sign out flows
- When testing custom Devise controllers

## Quick Start

### RSpec Setup

```ruby
# spec/rails_helper.rb
RSpec.configure do |config|
  config.include Devise::Test::ControllerHelpers, type: :controller
  config.include Devise::Test::IntegrationHelpers, type: :request
  config.include Devise::Test::IntegrationHelpers, type: :feature
  config.include Warden::Test::Helpers
end
```

### Minitest Setup

```ruby
# test/test_helper.rb
class ActionDispatch::IntegrationTest
  include Devise::Test::IntegrationHelpers
end
```

## Main Patterns

### Pattern 1: Request Specs with Authentication

```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  let(:user) { create(:user) }
  let(:post_record) { create(:post, user: user) }

  describe "GET /posts" do
    context "when not authenticated" do
      it "redirects to login" do
        get posts_path
        expect(response).to redirect_to(new_user_session_path)
      end
    end

    context "when authenticated" do
      before { sign_in user }

      it "returns success" do
        get posts_path
        expect(response).to have_http_status(:ok)
      end
    end
  end

  describe "POST /posts" do
    before { sign_in user }

    it "creates a new post" do
      expect {
        post posts_path, params: { post: { title: "Test", body: "Content" } }
      }.to change(Post, :count).by(1)

      expect(response).to redirect_to(post_path(Post.last))
    end
  end

  describe "DELETE /posts/:id" do
    before { sign_in user }

    it "deletes the post" do
      post_to_delete = create(:post, user: user)

      expect {
        delete post_path(post_to_delete)
      }.to change(Post, :count).by(-1)
    end
  end
end
```

### Pattern 2: Controller Specs (Legacy)

```ruby
# spec/controllers/posts_controller_spec.rb
require 'rails_helper'

RSpec.describe PostsController, type: :controller do
  let(:user) { create(:user) }

  describe "GET #index" do
    context "when not signed in" do
      it "redirects to sign in" do
        get :index
        expect(response).to redirect_to(new_user_session_path)
      end
    end

    context "when signed in" do
      before { sign_in user }

      it "returns success" do
        get :index
        expect(response).to have_http_status(:success)
      end
    end
  end
end
```

### Pattern 3: Feature/System Specs

```ruby
# spec/features/authentication_spec.rb
require 'rails_helper'

RSpec.feature "Authentication", type: :feature do
  let(:user) { create(:user, email: "test@example.com", password: "password123") }

  scenario "User signs in successfully" do
    visit new_user_session_path

    fill_in "Email", with: user.email
    fill_in "Password", with: "password123"
    click_button "Sign in"

    expect(page).to have_content("Signed in successfully")
    expect(page).to have_current_path(root_path)
  end

  scenario "User fails to sign in with wrong password" do
    visit new_user_session_path

    fill_in "Email", with: user.email
    fill_in "Password", with: "wrongpassword"
    click_button "Sign in"

    expect(page).to have_content("Invalid Email or password")
    expect(page).to have_current_path(new_user_session_path)
  end

  scenario "User signs out" do
    sign_in user
    visit root_path

    click_button "Sign out"

    expect(page).to have_content("Signed out successfully")
    expect(page).to have_current_path(new_user_session_path)
  end

  scenario "User registers" do
    visit new_user_registration_path

    fill_in "Name", with: "John Doe"
    fill_in "Email", with: "newuser@example.com"
    fill_in "Password", with: "password123"
    fill_in "Password confirmation", with: "password123"
    click_button "Sign up"

    expect(page).to have_content("Welcome! You have signed up successfully")
    expect(User.last.email).to eq("newuser@example.com")
  end

  scenario "User resets password" do
    visit new_user_password_path

    fill_in "Email", with: user.email
    click_button "Send reset instructions"

    expect(page).to have_content("You will receive an email")

    # Check email was sent
    expect(ActionMailer::Base.deliveries.last.to).to include(user.email)
  end
end
```

### Pattern 4: Testing Custom Controllers

```ruby
# spec/requests/users/registrations_spec.rb
require 'rails_helper'

RSpec.describe "Users::Registrations", type: :request do
  describe "POST /users" do
    let(:valid_params) do
      {
        user: {
          name: "John Doe",
          email: "john@example.com",
          password: "password123",
          password_confirmation: "password123"
        }
      }
    end

    it "creates user with custom fields" do
      expect {
        post user_registration_path, params: valid_params
      }.to change(User, :count).by(1)

      expect(User.last.name).to eq("John Doe")
    end

    it "redirects to onboarding" do
      post user_registration_path, params: valid_params
      expect(response).to redirect_to(onboarding_path)
    end
  end
end

# spec/requests/users/sessions_spec.rb
RSpec.describe "Users::Sessions", type: :request do
  let(:user) { create(:user) }

  describe "POST /users/sign_in" do
    it "tracks login" do
      expect {
        post user_session_path, params: {
          user: { email: user.email, password: user.password }
        }
      }.to change { user.reload.login_count }.by(1)
    end
  end
end
```

### Pattern 5: Testing with FactoryBot

```ruby
# spec/factories/users.rb
FactoryBot.define do
  factory :user do
    name { Faker::Name.name }
    email { Faker::Internet.unique.email }
    password { "password123" }
    password_confirmation { "password123" }

    trait :confirmed do
      confirmed_at { Time.current }
    end

    trait :unconfirmed do
      confirmed_at { nil }
    end

    trait :admin do
      role { :admin }
    end

    trait :locked do
      locked_at { Time.current }
      failed_attempts { 5 }
    end

    trait :with_avatar do
      avatar { Rack::Test::UploadedFile.new("spec/fixtures/avatar.png", "image/png") }
    end
  end
end
```

### Pattern 6: Testing Devise Modules

```ruby
# spec/models/user_spec.rb
require 'rails_helper'

RSpec.describe User, type: :model do
  describe "Devise modules" do
    it { is_expected.to validate_presence_of(:email) }
    it { is_expected.to validate_uniqueness_of(:email).case_insensitive }

    describe "password validation" do
      it "requires minimum length" do
        user = build(:user, password: "short", password_confirmation: "short")
        expect(user).not_to be_valid
        expect(user.errors[:password]).to include("is too short (minimum is 8 characters)")
      end
    end
  end

  describe "confirmable" do
    let(:user) { create(:user, :unconfirmed) }

    it "is not confirmed by default" do
      expect(user).not_to be_confirmed
    end

    it "can be confirmed" do
      user.confirm
      expect(user).to be_confirmed
    end
  end

  describe "lockable" do
    let(:user) { create(:user) }

    it "locks after max attempts" do
      5.times { user.increment_failed_attempts }
      user.lock_access!

      expect(user).to be_access_locked
    end
  end

  describe "trackable" do
    let(:user) { create(:user) }

    it "tracks sign in" do
      user.update(
        sign_in_count: 1,
        current_sign_in_at: Time.current,
        current_sign_in_ip: "127.0.0.1"
      )

      expect(user.sign_in_count).to eq(1)
    end
  end
end
```

### Pattern 7: Testing OmniAuth

```ruby
# spec/rails_helper.rb
OmniAuth.config.test_mode = true

# spec/features/omniauth_spec.rb
RSpec.feature "OAuth Authentication", type: :feature do
  before do
    OmniAuth.config.mock_auth[:google_oauth2] = OmniAuth::AuthHash.new(
      provider: "google_oauth2",
      uid: "123456",
      info: {
        email: "test@gmail.com",
        name: "Test User"
      }
    )
  end

  after do
    OmniAuth.config.mock_auth[:google_oauth2] = nil
  end

  scenario "User signs in with Google" do
    visit new_user_session_path
    click_button "Sign in with Google"

    expect(page).to have_content("Successfully authenticated from Google")
    expect(User.last.email).to eq("test@gmail.com")
  end

  scenario "OAuth failure" do
    OmniAuth.config.mock_auth[:google_oauth2] = :invalid_credentials

    visit new_user_session_path
    click_button "Sign in with Google"

    expect(page).to have_content("Authentication failed")
  end
end

# spec/requests/omniauth_callbacks_spec.rb
RSpec.describe "OmniAuth Callbacks", type: :request do
  before do
    OmniAuth.config.test_mode = true
    OmniAuth.config.mock_auth[:google_oauth2] = OmniAuth::AuthHash.new(
      provider: "google_oauth2",
      uid: "123456",
      info: { email: "test@gmail.com", name: "Test User" }
    )
  end

  describe "POST /users/auth/google_oauth2/callback" do
    it "creates user from oauth" do
      expect {
        post user_google_oauth2_omniauth_callback_path
      }.to change(User, :count).by(1)
    end

    it "links to existing user" do
      user = create(:user, email: "test@gmail.com")

      expect {
        post user_google_oauth2_omniauth_callback_path
      }.not_to change(User, :count)

      expect(controller.current_user).to eq(user)
    end
  end
end
```

### Pattern 8: Testing Mailers

```ruby
# spec/mailers/devise_mailer_spec.rb
require 'rails_helper'

RSpec.describe Devise::Mailer, type: :mailer do
  describe "reset_password_instructions" do
    let(:user) { create(:user) }
    let(:token) { user.send_reset_password_instructions }
    let(:mail) { Devise::Mailer.reset_password_instructions(user, token) }

    it "renders the headers" do
      expect(mail.subject).to eq("Reset password instructions")
      expect(mail.to).to eq([user.email])
    end

    it "includes reset link" do
      expect(mail.body.encoded).to include(edit_user_password_url(reset_password_token: token))
    end
  end

  describe "confirmation_instructions" do
    let(:user) { create(:user, :unconfirmed) }
    let(:mail) { Devise::Mailer.confirmation_instructions(user, user.confirmation_token) }

    it "renders confirmation link" do
      expect(mail.body.encoded).to include(user_confirmation_url(confirmation_token: user.confirmation_token))
    end
  end
end
```

## Test Helpers Reference

```ruby
# Integration/Request helpers
sign_in(user)                    # Sign in user
sign_out(user)                   # Sign out user

# Controller helpers
sign_in(user)                    # Sign in user
sign_out(user)                   # Sign out user
controller.current_user          # Access current user

# Warden helpers (for feature specs)
login_as(user, scope: :user)     # Sign in without going through form
logout(:user)                    # Sign out
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Testing Devise internals | Unnecessary, already tested | Test your customizations only |
| Using controller specs | Deprecated pattern | Use request specs |
| Not clearing OmniAuth mocks | Tests bleed into each other | Clear in `after` block |
| Hardcoded passwords | Tests fail on policy change | Use factory defaults |

## Related Skills

- [setup.md](./setup.md): Devise installation
- [controllers.md](./controllers.md): Controller customization
- [../../testing/SKILL.md](../../testing/SKILL.md): General testing patterns

## References

- [Devise Test Helpers](https://github.com/heartcombo/devise#test-helpers)
- [RSpec Rails](https://github.com/rspec/rspec-rails)
- [OmniAuth Testing](https://github.com/omniauth/omniauth/wiki/Integration-Testing)
