# System Tests

## Overview
System tests (E2E tests) verify full user workflows with real browser interactions using Capybara and Cuprite (Chrome driver).

## When to Use
- Testing complete user journeys
- Testing JavaScript interactions (Turbo, Stimulus)
- Testing real-time updates (Turbo Streams, ActionCable)
- Smoke tests for critical flows

## Quick Start
```ruby
# spec/system/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :system do
  before { driven_by(:cuprite) }

  it "creates a post" do
    user = create(:user)
    sign_in user

    visit new_post_path
    fill_in "Title", with: "My Post"
    click_button "Create Post"

    expect(page).to have_content("My Post")
  end
end
```

## Main Patterns

### Pattern 1: Cuprite (Fast Chrome Driver) Setup
```ruby
# spec/support/capybara.rb
require 'capybara/cuprite'

Capybara.register_driver :cuprite do |app|
  Capybara::Cuprite::Driver.new(app, {
    window_size: [1400, 1400],
    browser_options: { 'no-sandbox' => nil },
    process_timeout: 10,
    timeout: 5,
    js_errors: true,
    headless: !ENV['HEADLESS'].in?(['n', 'no', '0', 'false'])
  })
end

Capybara.default_driver = :cuprite
Capybara.javascript_driver = :cuprite
Capybara.default_max_wait_time = 5

# spec/system/posts_spec.rb
RSpec.describe "Posts", type: :system do
  before { driven_by(:cuprite) }
end
```

### Pattern 2: Basic User Interactions
```ruby
# spec/system/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :system do
  let(:user) { create(:user) }

  before do
    driven_by(:cuprite)
    sign_in user
  end

  describe "creating a post" do
    it "creates a new post successfully" do
      visit new_post_path

      fill_in "Title", with: "My New Post"
      fill_in "Body", with: "This is the content"
      check "Published"

      click_button "Create Post"

      expect(page).to have_content("My New Post")
      expect(page).to have_content("Post was successfully created")
      expect(page).to have_current_path(post_path(Post.last))
    end

    it "shows validation errors" do
      visit new_post_path

      click_button "Create Post"

      expect(page).to have_content("Title can't be blank")
      expect(page).to have_current_path(posts_path)
    end
  end

  describe "editing a post" do
    let!(:post_record) { create(:post, user: user, title: "Original Title") }

    it "updates the post" do
      visit edit_post_path(post_record)

      fill_in "Title", with: "Updated Title"
      click_button "Update Post"

      expect(page).to have_content("Updated Title")
      expect(page).to have_content("Post was successfully updated")
    end
  end

  describe "deleting a post" do
    let!(:post_record) { create(:post, user: user) }

    it "deletes the post" do
      visit post_path(post_record)

      accept_confirm do
        click_button "Delete"
      end

      expect(page).to have_content("Post was successfully deleted")
      expect(page).to have_current_path(posts_path)
    end
  end
end
```

### Pattern 3: Testing Turbo Frame Navigation
```ruby
# spec/system/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :system do
  let(:user) { create(:user) }
  let!(:post_record) { create(:post, user: user) }

  before do
    driven_by(:cuprite)
    sign_in user
  end

  describe "inline editing with Turbo Frame" do
    it "edits post without full page reload" do
      visit post_path(post_record)

      within("##{dom_id(post_record)}") do
        click_link "Edit"
      end

      # Form loads within Turbo Frame
      expect(page).to have_field("Title", with: post_record.title)
      expect(page).to have_current_path(post_path(post_record))  # URL unchanged

      fill_in "Title", with: "Updated Title"
      click_button "Update"

      # Updates without page refresh
      within("##{dom_id(post_record)}") do
        expect(page).to have_content("Updated Title")
        expect(page).not_to have_field("Title")  # Form replaced with content
      end
    end

    it "breaks out of frame on cancel" do
      visit post_path(post_record)

      within("##{dom_id(post_record)}") do
        click_link "Edit"
      end

      click_link "Cancel"  # data-turbo-frame="_top"

      expect(page).to have_current_path(post_path(post_record))
      expect(page).not_to have_field("Title")
    end
  end

  describe "modal with Turbo Frame" do
    it "opens edit form in modal" do
      visit posts_path

      click_link "Edit", match: :first

      # Modal frame loaded
      expect(page).to have_css("#modal")
      expect(page).to have_field("Title")
    end
  end
end
```

### Pattern 4: Testing Turbo Streams (Real-time Updates)
```ruby
# spec/system/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :system do
  let(:user) { create(:user) }

  before do
    driven_by(:cuprite)
    sign_in user
  end

  describe "creating a post with Turbo Stream", :js do
    it "appends post to list without page reload" do
      visit posts_path

      click_link "New Post"

      fill_in "Title", with: "Streaming Post"
      fill_in "Body", with: "Content"
      click_button "Create Post"

      # Post appears in list via Turbo Stream
      within("#posts") do
        expect(page).to have_content("Streaming Post")
      end

      # Form is reset or hidden
      expect(page).not_to have_field("Title")
    end
  end

  describe "deleting a post with Turbo Stream", :js do
    let!(:post_record) { create(:post, user: user) }

    it "removes post from list without page reload" do
      visit posts_path

      within("##{dom_id(post_record)}") do
        accept_confirm do
          click_button "Delete"
        end
      end

      # Post removed from DOM via Turbo Stream
      expect(page).not_to have_css("##{dom_id(post_record)}")
      expect(page).to have_content("Post was successfully deleted")
    end
  end
end
```

### Pattern 5: Testing Stimulus Controllers
```ruby
# spec/system/dropdown_spec.rb
require 'rails_helper'

RSpec.describe "Dropdown", type: :system do
  before { driven_by(:cuprite) }

  it "toggles dropdown on click" do
    visit root_path

    # Dropdown is initially hidden
    expect(page).not_to have_css("[data-dropdown-target='menu']", visible: :visible)

    # Click to open
    find("[data-action='click->dropdown#toggle']").click

    expect(page).to have_css("[data-dropdown-target='menu']", visible: :visible)

    # Click again to close
    find("[data-action='click->dropdown#toggle']").click

    expect(page).not_to have_css("[data-dropdown-target='menu']", visible: :visible)
  end

  it "closes dropdown when clicking outside" do
    visit root_path

    find("[data-action='click->dropdown#toggle']").click
    expect(page).to have_css("[data-dropdown-target='menu']", visible: :visible)

    # Click outside
    find("body").click

    expect(page).not_to have_css("[data-dropdown-target='menu']", visible: :visible)
  end
end
```

### Pattern 6: Page Objects Pattern
```ruby
# spec/support/page_objects/post_page.rb
class PostPage
  include Capybara::DSL

  def visit_new
    visit new_post_path
  end

  def fill_form(title:, body:, published: false)
    fill_in "Title", with: title
    fill_in "Body", with: body
    check "Published" if published
  end

  def submit
    click_button "Create Post"
  end

  def expect_created(title)
    expect(page).to have_content(title)
    expect(page).to have_content("Post was successfully created")
  end
end

# spec/system/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :system do
  let(:user) { create(:user) }
  let(:post_page) { PostPage.new }

  before do
    driven_by(:cuprite)
    sign_in user
  end

  it "creates a post" do
    post_page.visit_new
    post_page.fill_form(title: "My Post", body: "Content", published: true)
    post_page.submit
    post_page.expect_created("My Post")
  end
end
```

### Pattern 7: Testing Asynchronous Behavior
```ruby
# spec/system/notifications_spec.rb
require 'rails_helper'

RSpec.describe "Notifications", type: :system do
  let(:user) { create(:user) }

  before do
    driven_by(:cuprite)
    sign_in user
  end

  it "shows flash message that auto-dismisses", :js do
    visit posts_path

    # Flash appears
    expect(page).to have_css(".flash-notice", text: "Welcome!")

    # Flash disappears after delay
    expect(page).not_to have_css(".flash-notice", wait: 6)
  end

  it "updates live counter via Turbo Stream", :js do
    visit dashboard_path

    # Initial count
    expect(page).to have_content("Posts: 0")

    # Another user creates a post (simulated)
    create(:post, user: user)

    # Counter updates in real-time
    expect(page).to have_content("Posts: 1", wait: 5)
  end
end
```

### Pattern 8: Testing Accessibility
```ruby
# spec/system/accessibility_spec.rb
require 'rails_helper'

RSpec.describe "Accessibility", type: :system do
  before { driven_by(:cuprite) }

  it "navigates form with keyboard" do
    visit new_post_path

    # Tab through form
    page.driver.browser.keyboard.type(:tab)
    expect(page).to have_css("input#post_title:focus")

    page.driver.browser.keyboard.type(:tab)
    expect(page).to have_css("textarea#post_body:focus")
  end

  it "uses proper ARIA labels" do
    visit posts_path

    expect(page).to have_css("[aria-label='Create new post']")
    expect(page).to have_css("[role='navigation']")
  end
end
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Overusing system tests | Slow test suite | Use request specs for most cases, system tests for critical flows only |
| Not using `within` scopes | Fragile selectors | Use `within` to scope interactions |
| Using `sleep` for waits | Flaky tests | Use Capybara's auto-wait or explicit `wait` |
| Testing API logic in system tests | Wrong tool | Use request specs for API testing |
| Not using page objects | Duplicated code | Extract page objects for complex workflows |

## Related Skills
- [Request Specs](./requests.md): Testing HTTP endpoints
- [Turbo Testing](../patterns/turbo.md): Turbo-specific patterns
- [Capybara Setup](../setup/rspec.md): Capybara configuration

## References
- [Capybara Documentation](https://github.com/teamcapybara/capybara)
- [Cuprite](https://github.com/rubycdp/cuprite)
- [Rails System Testing Guide](https://guides.rubyonrails.org/testing.html#system-testing)
