# Turbo Drive

## Overview

Turbo Drive accelerates page navigation by intercepting link clicks and form submissions, fetching pages via AJAX, and swapping the `<body>` content. No JavaScript changes required - it works automatically.

## How It Works

1. User clicks a link
2. Turbo intercepts the click
3. Fetches the page via fetch API
4. Replaces `<body>` and merges `<head>`
5. Updates browser history

## Basic Usage

Turbo Drive is enabled by default in Rails 8. No configuration needed.

```erb
<!-- Links work automatically -->
<%= link_to "Posts", posts_path %>

<!-- Forms work automatically -->
<%= form_with model: @post do |f| %>
  <%= f.text_field :title %>
  <%= f.submit %>
<% end %>
```

## Progress Bar

```css
/* Customize the progress bar */
.turbo-progress-bar {
  height: 3px;
  background-color: #0d6efd;
}
```

```javascript
// Configure progress bar delay (default: 500ms)
Turbo.setProgressBarDelay(200)
```

## Disabling Turbo Drive

```erb
<!-- Disable for specific link -->
<%= link_to "External", "https://example.com", data: { turbo: false } %>

<!-- Disable for entire section -->
<div data-turbo="false">
  <%= link_to "Regular link", some_path %>
</div>

<!-- Disable for form -->
<%= form_with model: @post, data: { turbo: false } do |f| %>
```

## Page Caching

```erb
<!-- Preview cached version while fetching -->
<meta name="turbo-cache-control" content="no-preview">

<!-- Disable caching for this page -->
<meta name="turbo-cache-control" content="no-cache">
```

## Visit Options

```erb
<!-- Replace instead of push to history -->
<%= link_to "Back", root_path, data: { turbo_action: "replace" } %>

<!-- Advance (default behavior) -->
<%= link_to "Next", next_path, data: { turbo_action: "advance" } %>
```

## JavaScript Events

```javascript
// Page load events
document.addEventListener("turbo:load", () => {
  console.log("Page loaded (initial or Turbo)")
})

document.addEventListener("turbo:visit", () => {
  console.log("Starting visit")
})

document.addEventListener("turbo:before-cache", () => {
  // Clean up before caching (remove tooltips, modals, etc.)
})

document.addEventListener("turbo:render", () => {
  console.log("Page rendered")
})
```

## Prefetching

```erb
<!-- Prefetch on hover (default in Rails 8) -->
<%= link_to "Posts", posts_path %>

<!-- Disable prefetch -->
<%= link_to "Posts", posts_path, data: { turbo_prefetch: false } %>
```

## Redirect After Form Submit

```ruby
# Controller
def create
  @post = Post.create(post_params)

  if @post.persisted?
    redirect_to @post, status: :see_other  # 303 for GET after POST
  else
    render :new, status: :unprocessable_entity  # 422 for validation errors
  end
end
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Form doesn't update | Missing status code | Add `status: :unprocessable_entity` |
| JavaScript not running | Using DOMContentLoaded | Use `turbo:load` event |
| Cached page shows stale data | Page is cached | Add `no-cache` meta tag |
| External links broken | Turbo intercepting | Add `data-turbo="false"` |

## Related

- [frames.md](./frames.md): Partial page updates
- [streams.md](./streams.md): Multiple element updates
- [morphing.md](./morphing.md): DOM morphing (Rails 8)
