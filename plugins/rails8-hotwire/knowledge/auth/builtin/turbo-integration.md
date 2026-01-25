# Rails 8 Built-in Auth + Turbo Integration

The built-in authentication generator is designed to work with Turbo, but there are important patterns to follow for seamless integration.

## Status Codes (Critical)

Turbo requires specific HTTP status codes to function correctly:

| Scenario | Status Code | Why |
|----------|-------------|-----|
| Successful redirect | `303 See Other` | Forces GET request after POST/DELETE |
| Validation errors | `422 Unprocessable Entity` | Triggers Turbo to replace form |
| Unauthorized | `401 Unauthorized` | For API responses |

### Correct Implementation

```ruby
# app/controllers/sessions_controller.rb
class SessionsController < ApplicationController
  allow_unauthenticated_access only: [:new, :create]

  def create
    if user = User.authenticate_by(email_address: params[:email_address], password: params[:password])
      start_new_session_for(user)
      redirect_to root_path, notice: "Signed in successfully", status: :see_other  # 303
    else
      flash.now[:alert] = "Invalid email or password"
      render :new, status: :unprocessable_entity  # 422
    end
  end

  def destroy
    terminate_session
    redirect_to root_path, notice: "Signed out", status: :see_other  # 303
  end
end
```

### Common Mistake: Missing Status Codes

```ruby
# BAD: Missing status codes
def create
  if user = User.authenticate_by(...)
    start_new_session_for(user)
    redirect_to root_path  # Turbo may not follow correctly
  else
    render :new  # Turbo won't replace the form
  end
end

# GOOD: Explicit status codes
def create
  if user = User.authenticate_by(...)
    start_new_session_for(user)
    redirect_to root_path, status: :see_other
  else
    render :new, status: :unprocessable_entity
  end
end
```

## Form Configuration

### Standard Turbo Form

```erb
<!-- app/views/sessions/new.html.erb -->
<%= form_with url: session_path, class: "space-y-4" do |f| %>
  <!-- Turbo enabled by default in Rails 7+ -->

  <div>
    <%= f.label :email_address %>
    <%= f.email_field :email_address,
        required: true,
        autofocus: true,
        autocomplete: "email" %>
  </div>

  <div>
    <%= f.label :password %>
    <%= f.password_field :password,
        required: true,
        autocomplete: "current-password" %>
  </div>

  <%= f.submit "Sign in",
      class: "btn-primary",
      data: { turbo_submits_with: "Signing in..." } %>
<% end %>
```

### Disabling Turbo (If Needed)

```erb
<!-- For specific forms that need full page reload -->
<%= form_with url: session_path, data: { turbo: false } do |f| %>
  <!-- ... -->
<% end %>
```

## Flash Messages with Turbo

### Partial for Flash Messages

```erb
<!-- app/views/shared/_flash.html.erb -->
<div id="flash" class="fixed top-4 right-4 z-50">
  <% flash.each do |type, message| %>
    <div class="flash-<%= type %> p-4 rounded shadow-lg mb-2"
         data-controller="flash"
         data-flash-remove-after-value="5000">
      <%= message %>
      <button data-action="flash#dismiss" class="ml-2">&times;</button>
    </div>
  <% end %>
</div>
```

### Flash Stimulus Controller

```javascript
// app/javascript/controllers/flash_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { removeAfter: Number }

  connect() {
    if (this.removeAfterValue) {
      setTimeout(() => this.dismiss(), this.removeAfterValue)
    }
  }

  dismiss() {
    this.element.remove()
  }
}
```

### Layout Integration

```erb
<!-- app/views/layouts/application.html.erb -->
<!DOCTYPE html>
<html>
<head>
  <%= csrf_meta_tags %>
  <%= csp_meta_tag %>
  <!-- ... -->
</head>
<body>
  <%= render "shared/flash" %>

  <%= yield %>
</body>
</html>
```

## Turbo Stream Authentication Responses

### Login Success with Turbo Stream

```ruby
# app/controllers/sessions_controller.rb
def create
  if user = User.authenticate_by(email_address: params[:email_address], password: params[:password])
    start_new_session_for(user)

    respond_to do |format|
      format.html { redirect_to root_path, notice: "Signed in", status: :see_other }
      format.turbo_stream do
        render turbo_stream: [
          turbo_stream.update("user_menu", partial: "shared/user_menu"),
          turbo_stream.update("flash", partial: "shared/flash")
        ]
      end
    end
  else
    flash.now[:alert] = "Invalid credentials"
    render :new, status: :unprocessable_entity
  end
end
```

### Logout with Turbo Stream

```ruby
def destroy
  terminate_session

  respond_to do |format|
    format.html { redirect_to root_path, notice: "Signed out", status: :see_other }
    format.turbo_stream do
      render turbo_stream: [
        turbo_stream.update("user_menu", partial: "shared/guest_menu"),
        turbo_stream.update("flash", partial: "shared/flash")
      ]
    end
  end
end
```

## Modal Login Form

### Trigger Button

```erb
<%= link_to "Sign in", new_session_path,
    data: { turbo_frame: "modal" },
    class: "btn" %>

<!-- Modal container -->
<%= turbo_frame_tag "modal" %>
```

### Modal-wrapped Form

```erb
<!-- app/views/sessions/new.html.erb -->
<%= turbo_frame_tag "modal" do %>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center"
       data-controller="modal"
       data-action="keydown.esc->modal#close click->modal#closeBackground">
    <div class="bg-white rounded-lg p-6 max-w-md w-full" data-modal-target="content">
      <h2 class="text-xl font-bold mb-4">Sign In</h2>

      <%= form_with url: session_path, class: "space-y-4" do |f| %>
        <div>
          <%= f.label :email_address %>
          <%= f.email_field :email_address, required: true, autofocus: true %>
        </div>

        <div>
          <%= f.label :password %>
          <%= f.password_field :password, required: true %>
        </div>

        <div class="flex justify-between items-center">
          <%= f.submit "Sign in", class: "btn-primary" %>
          <%= link_to "Cancel", root_path, data: { turbo_frame: "_top" }, class: "text-gray-500" %>
        </div>
      <% end %>

      <p class="mt-4 text-sm text-center">
        <%= link_to "Forgot password?", new_password_path %>
      </p>
    </div>
  </div>
<% end %>
```

### Modal Controller

```javascript
// app/javascript/controllers/modal_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["content"]

  close() {
    this.element.remove()
  }

  closeBackground(event) {
    if (!this.contentTarget.contains(event.target)) {
      this.close()
    }
  }
}
```

## Handling Authentication Redirects

### Storing Return Location

```ruby
# app/controllers/concerns/authentication.rb
module Authentication
  # ... existing code ...

  private

  def request_authentication
    store_location
    redirect_to new_session_path
  end

  def store_location
    session[:return_to] = request.fullpath if request.get?
  end

  def stored_location
    session.delete(:return_to)
  end
end
```

### Redirect After Login

```ruby
# app/controllers/sessions_controller.rb
def create
  if user = User.authenticate_by(...)
    start_new_session_for(user)
    redirect_to stored_location || root_path, notice: "Signed in", status: :see_other
  end
end
```

## CSRF Token Refresh

Turbo automatically handles CSRF tokens, but ensure the meta tag is present:

```erb
<!-- app/views/layouts/application.html.erb -->
<head>
  <%= csrf_meta_tags %>
  <%= csp_meta_tag %>
</head>
```

For single-page-app style navigation, the token refreshes automatically on Turbo visits.

## Troubleshooting

### Issue: Form doesn't submit / page refreshes fully

```erb
<!-- Check that Turbo is not disabled -->
<%= form_with url: session_path do |f| %>  <!-- Good: Turbo enabled by default -->
<%= form_with url: session_path, local: true do |f| %>  <!-- Bad: disables Turbo -->
```

### Issue: Flash messages appear twice

```erb
<!-- Ensure flash partial has unique ID -->
<div id="flash">  <!-- Good: will be replaced -->
  <!-- flash messages -->
</div>
```

### Issue: Redirect not working after login

```ruby
# Ensure status: :see_other on all redirects
redirect_to root_path, status: :see_other  # Required for Turbo
```

### Issue: Form errors not showing

```ruby
# Ensure 422 status for validation failures
render :new, status: :unprocessable_entity  # Required for Turbo to swap content
```

## Best Practices Summary

| Practice | Implementation |
|----------|----------------|
| Always use status codes | `:see_other` for redirects, `:unprocessable_entity` for errors |
| Include CSRF meta tags | `<%= csrf_meta_tags %>` in layout head |
| Use flash partial with ID | `<div id="flash">` for Turbo Stream updates |
| Provide loading feedback | `data-turbo-submits-with` on submit buttons |
| Handle modal forms | Use `turbo_frame_tag` with modal container |

## Related Documentation

- [../../hotwire/turbo/frames.md](../../hotwire/turbo/frames.md): Turbo Frames deep dive
- [../../hotwire/turbo/streams.md](../../hotwire/turbo/streams.md): Turbo Streams patterns
- [../../controllers/SKILL.md](../../controllers/SKILL.md): Controller response patterns
