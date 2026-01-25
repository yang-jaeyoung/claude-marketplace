# Turbo Testing Patterns

## Overview
Testing Turbo Drive, Turbo Frames, Turbo Streams, and Stimulus controllers in Rails 8 applications.

## When to Use
- Testing Turbo Stream broadcasts and responses
- Verifying Turbo Frame navigation and lazy loading
- Testing Stimulus controller interactions
- Ensuring progressive enhancement works correctly

## Quick Start
```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  let(:user) { create(:user) }
  let(:headers) { { "Accept" => "text/vnd.turbo-stream.html" } }

  before { sign_in user }

  it "responds with turbo stream on create" do
    post posts_path,
         params: { post: attributes_for(:post) },
         headers: headers

    expect(response.media_type).to eq("text/vnd.turbo-stream.html")
    expect(response.body).to include('<turbo-stream')
  end
end
```

## Main Patterns

### Pattern 1: Testing Turbo Stream Responses
```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  let(:user) { create(:user) }
  let(:turbo_headers) { { "Accept" => "text/vnd.turbo-stream.html" } }

  before { sign_in user }

  describe "POST /posts" do
    context "with turbo stream format" do
      it "appends post to list" do
        post posts_path,
             params: { post: attributes_for(:post, title: "New Post") },
             headers: turbo_headers

        expect(response.media_type).to eq("text/vnd.turbo-stream.html")
        expect(response.body).to include('action="append"')
        expect(response.body).to include('target="posts"')
        expect(response.body).to include("New Post")
      end

      it "renders validation errors in modal" do
        post posts_path,
             params: { post: { title: "" } },
             headers: turbo_headers

        expect(response.media_type).to eq("text/vnd.turbo-stream.html")
        expect(response.body).to include('action="update"')
        expect(response.body).to include('target="modal"')
        expect(response.body).to include("can't be blank")
      end
    end
  end

  describe "PATCH /posts/:id" do
    let(:post_record) { create(:post, user: user) }

    it "updates post inline with replace action" do
      patch post_path(post_record),
            params: { post: { title: "Updated" } },
            headers: turbo_headers

      expect(response.body).to include('action="replace"')
      expect(response.body).to include("target=\"#{dom_id(post_record)}\"")
      expect(response.body).to include("Updated")
    end
  end

  describe "DELETE /posts/:id" do
    let!(:post_record) { create(:post, user: user) }

    it "removes post from DOM" do
      delete post_path(post_record), headers: turbo_headers

      expect(response.body).to include('action="remove"')
      expect(response.body).to include("target=\"#{dom_id(post_record)}\"")
    end
  end
end
```

### Pattern 2: Testing Turbo Frame Navigation
```ruby
# spec/system/turbo_frames_spec.rb
require 'rails_helper'

RSpec.describe "Turbo Frames", type: :system do
  let(:user) { create(:user) }
  let!(:post_record) { create(:post, user: user) }

  before do
    driven_by(:cuprite)
    sign_in user
  end

  describe "inline editing" do
    it "loads edit form in frame without navigation" do
      visit post_path(post_record)

      original_url = current_url

      within("##{dom_id(post_record)}") do
        click_link "Edit"
      end

      # URL doesn't change (frame navigation)
      expect(current_url).to eq(original_url)

      # Form appears within frame
      within("##{dom_id(post_record)}") do
        expect(page).to have_field("Title", with: post_record.title)
      end
    end

    it "updates post and replaces frame content" do
      visit post_path(post_record)

      within("##{dom_id(post_record)}") do
        click_link "Edit"
        fill_in "Title", with: "Updated Title"
        click_button "Update"
      end

      # Frame content replaced with updated post
      within("##{dom_id(post_record)}") do
        expect(page).to have_content("Updated Title")
        expect(page).not_to have_field("Title")  # Form is gone
      end
    end
  end

  describe "lazy loading" do
    it "loads frame content on scroll" do
      visit posts_path

      # Frame not loaded initially
      expect(page).not_to have_css("#comments_frame[complete]")

      # Scroll to trigger lazy load
      execute_script("document.querySelector('#comments_frame').scrollIntoView()")

      # Frame loads content
      expect(page).to have_css("#comments_frame[complete]", wait: 5)
      expect(page).to have_content("Comments")
    end
  end

  describe "breaking out of frames" do
    it "navigates full page when data-turbo-frame='_top'" do
      visit posts_path

      # Click link that breaks out of frame
      click_link "View All Posts"  # data-turbo-frame="_top"

      expect(page).to have_current_path(posts_path)
    end
  end
end
```

### Pattern 3: Testing Turbo Stream Broadcasts
```ruby
# spec/models/post_spec.rb
require 'rails_helper'

RSpec.describe Post, type: :model do
  describe 'broadcasts' do
    it 'broadcasts append on create' do
      user = create(:user)

      expect {
        create(:post, user: user)
      }.to have_broadcasted_to("posts")
        .from_channel(Turbo::StreamsChannel)
    end

    it 'broadcasts update on save' do
      post = create(:post)

      expect {
        post.update(title: "Updated")
      }.to have_broadcasted_to(post)
        .from_channel(Turbo::StreamsChannel)
    end

    it 'broadcasts remove on destroy' do
      post = create(:post)

      expect {
        post.destroy
      }.to have_broadcasted_to("posts")
        .from_channel(Turbo::StreamsChannel)
    end
  end
end

# spec/system/real_time_updates_spec.rb
require 'rails_helper'

RSpec.describe "Real-time updates", type: :system do
  let(:user) { create(:user) }
  let!(:post_record) { create(:post, user: user) }

  before do
    driven_by(:cuprite)
    sign_in user
  end

  it "receives new comments via broadcast", :js do
    visit post_path(post_record)

    # Simulate another user adding a comment
    using_session(:other_user) do
      other_user = create(:user)
      sign_in other_user
      visit post_path(post_record)

      fill_in "Comment", with: "Real-time comment!"
      click_button "Add Comment"
    end

    # Original session receives broadcast
    using_session(:default) do
      expect(page).to have_content("Real-time comment!", wait: 5)
    end
  end
end
```

### Pattern 4: Testing Custom Turbo Stream Actions
```ruby
# app/javascript/controllers/turbo_streams_controller.js
import { StreamActions } from "@hotwired/turbo"

StreamActions.toast = function() {
  const message = this.getAttribute("message")
  // Show toast notification
}

# spec/requests/notifications_spec.rb
require 'rails_helper'

RSpec.describe "Notifications", type: :request do
  let(:user) { create(:user) }
  let(:headers) { { "Accept" => "text/vnd.turbo-stream.html" } }

  before { sign_in user }

  it "sends custom toast action" do
    post notifications_path,
         params: { message: "Hello!" },
         headers: headers

    expect(response.body).to include('action="toast"')
    expect(response.body).to include('message="Hello!"')
  end
end

# spec/system/toast_notifications_spec.rb
require 'rails_helper'

RSpec.describe "Toast notifications", type: :system do
  before do
    driven_by(:cuprite)
    sign_in create(:user)
  end

  it "shows toast on success", :js do
    visit new_post_path

    fill_in "Title", with: "Test Post"
    click_button "Create"

    expect(page).to have_css(".toast", text: "Post created successfully", wait: 3)
  end
end
```

### Pattern 5: Testing Stimulus Controllers
```ruby
# app/javascript/controllers/clipboard_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["source"]

  copy(event) {
    event.preventDefault()
    const text = this.sourceTarget.textContent
    navigator.clipboard.writeText(text)
  }
}

# spec/system/clipboard_spec.rb
require 'rails_helper'

RSpec.describe "Clipboard", type: :system do
  before { driven_by(:cuprite) }

  it "copies text to clipboard on click", :js do
    visit root_path

    # Find element with Stimulus controller
    find("[data-controller='clipboard']").find("[data-action='clipboard#copy']").click

    # Verify clipboard content (browser-dependent)
    clipboard_text = page.evaluate_script('navigator.clipboard.readText()')
    expect(clipboard_text).to eq("Expected text")
  end
end

# Alternative: Test via DOM changes instead of clipboard
# spec/system/dropdown_spec.rb
require 'rails_helper'

RSpec.describe "Dropdown", type: :system do
  before { driven_by(:cuprite) }

  it "toggles dropdown visibility", :js do
    visit root_path

    # Initially hidden
    expect(page).not_to have_css("[data-dropdown-target='menu']", visible: :visible)

    # Click to open
    find("[data-action='dropdown#toggle']").click
    expect(page).to have_css("[data-dropdown-target='menu']", visible: :visible)

    # Click to close
    find("[data-action='dropdown#toggle']").click
    expect(page).not_to have_css("[data-dropdown-target='menu']", visible: :visible)
  end

  it "closes on outside click", :js do
    visit root_path

    find("[data-action='dropdown#toggle']").click
    expect(page).to have_css("[data-dropdown-target='menu']", visible: :visible)

    # Click outside
    find("body").click
    expect(page).not_to have_css("[data-dropdown-target='menu']", visible: :visible)
  end
end
```

### Pattern 6: Testing Turbo Drive Navigation
```ruby
# spec/system/turbo_drive_spec.rb
require 'rails_helper'

RSpec.describe "Turbo Drive", type: :system do
  before { driven_by(:cuprite) }

  it "navigates without full page reload", :js do
    visit root_path

    # Track page load events
    page.execute_script(<<~JS)
      window.pageLoads = 0;
      document.addEventListener('turbo:load', () => window.pageLoads++);
    JS

    click_link "Posts"

    # Turbo Drive navigation occurred
    expect(page).to have_current_path(posts_path)

    # Only one turbo:load event (no full page reload)
    page_loads = page.evaluate_script('window.pageLoads')
    expect(page_loads).to eq(1)
  end

  it "disables Turbo Drive on specific links" do
    visit root_path

    # Link with data-turbo="false" causes full reload
    click_link "External Link"  # data-turbo="false"

    # Full page reload occurred (can verify via window.performance)
  end

  it "shows progress bar during navigation", :js do
    visit root_path

    # Progress bar appears during navigation
    click_link "Slow Page"

    expect(page).to have_css(".turbo-progress-bar", wait: 1)
  end
end
```

### Pattern 7: Testing Morphing (Turbo 8+)
```ruby
# spec/system/turbo_morphing_spec.rb
require 'rails_helper'

RSpec.describe "Turbo Morphing", type: :system do
  before do
    driven_by(:cuprite)
    sign_in create(:user)
  end

  it "morphs page content without losing focus", :js do
    visit posts_path

    # Fill input field
    fill_in "Search", with: "test query"

    # Trigger page refresh with morphing
    click_button "Refresh"  # data-turbo-action="replace"

    # Input field retains value and focus after morph
    expect(find_field("Search").value).to eq("test query")
    expect(page).to have_css("input#search:focus")
  end

  it "preserves scroll position during morph", :js do
    visit long_posts_path

    # Scroll down
    page.execute_script("window.scrollTo(0, 500)")

    click_button "Refresh"

    # Scroll position maintained
    scroll_y = page.evaluate_script("window.scrollY")
    expect(scroll_y).to be_within(10).of(500)
  end
end
```

### Pattern 8: Testing Error Handling
```ruby
# spec/system/turbo_errors_spec.rb
require 'rails_helper'

RSpec.describe "Turbo error handling", type: :system do
  before do
    driven_by(:cuprite)
    sign_in create(:user)
  end

  it "handles 422 validation errors", :js do
    visit new_post_path

    click_button "Create Post"  # Empty form

    # Error messages displayed without page reload
    expect(page).to have_content("can't be blank")
    expect(page).to have_current_path(posts_path)  # POST action path
  end

  it "handles 500 server errors gracefully", :js do
    # Simulate server error
    allow_any_instance_of(PostsController).to receive(:create).and_raise(StandardError)

    visit new_post_path

    click_button "Create Post"

    # Error page rendered
    expect(page).to have_content("Something went wrong")
  end

  it "retries failed requests", :js do
    visit posts_path

    # Simulate network failure
    page.driver.browser.network_conditions = {
      offline: true,
      latency: 0,
      download_throughput: 0,
      upload_throughput: 0
    }

    click_link "New Post"

    # Turbo shows retry UI
    expect(page).to have_content("Network error")

    # Restore network
    page.driver.browser.network_conditions = { offline: false }

    click_button "Retry"

    expect(page).to have_current_path(new_post_path)
  end
end
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Not testing Turbo Stream format | Broken real-time features | Always test with `Accept: text/vnd.turbo-stream.html` |
| Testing JavaScript logic in system tests | Slow, brittle | Test Stimulus controllers via DOM interactions, not internals |
| Not using `wait` for async updates | Flaky tests | Use Capybara's auto-wait or explicit `wait:` option |
| Testing HTML structure instead of behavior | Brittle to markup changes | Test visible content and interactions |
| Not isolating Turbo tests | Hard to debug | Use separate test cases for Drive, Frames, Streams |

## Related Skills
- [System Tests](../types/system.md): E2E testing setup
- [Request Specs](../types/requests.md): Testing Turbo Stream responses
- [Turbo Frames](../../hotwire/turbo-frames.md): Turbo Frame patterns
- [Turbo Streams](../../hotwire/turbo-streams.md): Turbo Stream patterns

## References
- [Turbo Handbook - Testing](https://turbo.hotwired.dev/handbook/testing)
- [RSpec Rails System Tests](https://rspec.info/features/6-0/rspec-rails/system-specs/)
- [Capybara Matchers](https://rubydoc.info/github/teamcapybara/capybara/master/Capybara/Node/Matchers)
