# Devise + Turbo Compatibility

## Overview

Rails 8 uses Turbo by default for form submissions and navigation. Devise requires specific configuration to work correctly with Turbo's expectations for HTTP status codes and response handling.

## When to Use

- When setting up Devise in a Rails 8 application
- When authentication forms show full-page reloads on errors
- When flash messages don't appear after authentication
- When redirect loops occur after sign in/out

## Quick Start

```ruby
# config/initializers/devise.rb
Devise.setup do |config|
  # Required for Rails 8 + Turbo
  config.responder.error_status = :unprocessable_entity  # 422
  config.responder.redirect_status = :see_other          # 303

  # ... other config
end
```

## The Problem

Turbo expects specific HTTP status codes:

| Scenario | Expected Status | Default Devise | Result |
|----------|-----------------|----------------|--------|
| Form error | 422 (Unprocessable Entity) | 200 (OK) | Full page reload |
| Successful redirect | 303 (See Other) | 302 (Found) | Turbo may not follow |

## Main Patterns

### Pattern 1: Basic Configuration (Recommended)

```ruby
# config/initializers/devise.rb
Devise.setup do |config|
  # These two lines fix 99% of Turbo issues
  config.responder.error_status = :unprocessable_entity
  config.responder.redirect_status = :see_other
end
```

### Pattern 2: Custom Failure App for Turbo

For advanced control over authentication failures:

```ruby
# config/initializers/devise.rb
Devise.setup do |config|
  config.warden do |manager|
    manager.failure_app = TurboFailureApp
  end
end
```

```ruby
# app/lib/turbo_failure_app.rb
class TurboFailureApp < Devise::FailureApp
  def respond
    if request_format == :turbo_stream
      redirect
    else
      super
    end
  end

  def skip_format?
    %w[html turbo_stream */*].include?(request_format.to_s)
  end
end
```

See [snippets/devise/turbo_failure_app.rb](../snippets/devise/turbo_failure_app.rb) for full implementation.

### Pattern 3: Custom Devise Controller for Turbo

```ruby
# app/controllers/turbo_devise_controller.rb
class TurboDeviseController < ApplicationController
  class Responder < ActionController::Responder
    def to_turbo_stream
      if has_errors? && default_action
        render rendering_options.merge(formats: :html, status: :unprocessable_entity)
      else
        controller.render(options.merge(formats: :html))
      rescue ActionView::MissingTemplate
        redirect_to navigation_location, status: :see_other
      end
    end
  end

  self.responder = Responder
  respond_to :html, :turbo_stream
end

# config/initializers/devise.rb
Devise.setup do |config|
  config.parent_controller = 'TurboDeviseController'
end
```

### Pattern 4: Sign Out Button

The sign out action must use DELETE method with Turbo:

```erb
<%# Correct: button_to for DELETE %>
<%= button_to "Sign out", destroy_user_session_path,
    method: :delete,
    class: "btn btn-outline" %>

<%# Alternative: link with turbo method %>
<%= link_to "Sign out", destroy_user_session_path,
    data: { turbo_method: :delete },
    class: "btn btn-outline" %>

<%# If using GET for sign out (less secure) %>
<%# config.sign_out_via = :get in devise.rb %>
<%= link_to "Sign out", destroy_user_session_path %>
```

### Pattern 5: Form Error Handling

```erb
<%# app/views/devise/sessions/new.html.erb %>
<%= form_for(resource, as: resource_name, url: session_path(resource_name),
    data: { turbo_frame: "_top" }) do |f| %>

  <%# Errors will render in-place with 422 status %>
  <%= render "devise/shared/error_messages", resource: resource %>

  <%= f.email_field :email, autofocus: true %>
  <%= f.password_field :password %>
  <%= f.submit "Sign in" %>
<% end %>
```

### Pattern 6: Flash Messages with Turbo Streams

```erb
<%# app/views/layouts/application.html.erb %>
<div id="flash">
  <%= render "shared/flash" %>
</div>

<%# app/views/shared/_flash.html.erb %>
<% flash.each do |type, message| %>
  <div class="flash flash-<%= type %>"
       data-controller="flash"
       data-flash-remove-delay-value="3000">
    <%= message %>
    <button data-action="flash#dismiss">&times;</button>
  </div>
<% end %>
```

```javascript
// app/javascript/controllers/flash_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { removeDelay: { type: Number, default: 5000 } }

  connect() {
    setTimeout(() => this.dismiss(), this.removeDelayValue)
  }

  dismiss() {
    this.element.remove()
  }
}
```

### Pattern 7: Handling OAuth with Turbo

OAuth callbacks need special handling:

```erb
<%# OAuth buttons must disable Turbo %>
<%= button_to omniauth_authorize_path(resource_name, :google_oauth2),
    method: :post,
    data: { turbo: false },
    class: "btn btn-google" do %>
  Sign in with Google
<% end %>
```

```ruby
# app/controllers/users/omniauth_callbacks_controller.rb
class Users::OmniauthCallbacksController < Devise::OmniauthCallbacksController
  skip_before_action :verify_authenticity_token, only: [:google_oauth2, :github]

  def google_oauth2
    @user = User.from_omniauth(request.env["omniauth.auth"])

    if @user.persisted?
      sign_in_and_redirect @user, event: :authentication
    else
      # Handle Turbo redirect
      redirect_to new_user_registration_path, status: :see_other,
                  alert: "Could not authenticate"
    end
  end
end
```

### Pattern 8: Modal Authentication

```erb
<%# Login form in a modal %>
<%= turbo_frame_tag "auth_modal" do %>
  <div data-controller="modal">
    <%= form_for(resource, as: resource_name, url: session_path(resource_name),
        data: { turbo_frame: "auth_modal" }) do |f| %>

      <%= render "devise/shared/error_messages", resource: resource %>

      <div class="field">
        <%= f.email_field :email, placeholder: "Email" %>
      </div>

      <div class="field">
        <%= f.password_field :password, placeholder: "Password" %>
      </div>

      <%= f.submit "Sign in" %>
    <% end %>
  </div>
<% end %>
```

```ruby
# Controller must render frame on success
class Users::SessionsController < Devise::SessionsController
  def create
    super do |resource|
      if request.headers["Turbo-Frame"]
        render turbo_stream: turbo_stream.action(:redirect, after_sign_in_path_for(resource))
        return
      end
    end
  end
end
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Form shows full page on error | Missing 422 status | Add `config.responder.error_status = :unprocessable_entity` |
| Redirect doesn't work | Wrong status code | Add `config.responder.redirect_status = :see_other` |
| Sign out not working | Using GET method | Use `button_to` with `method: :delete` |
| Flash not showing | Not using Turbo Streams | Ensure flash partial in layout |
| OAuth broken | Turbo intercepting | Add `data: { turbo: false }` |
| Modal not closing | Wrong frame target | Use `turbo_frame: "_top"` for redirect |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| `link_to` for sign out | DELETE not sent | Use `button_to` or `data-turbo-method` |
| Missing status config | Turbo ignores responses | Configure responder in devise.rb |
| Turbo on OAuth buttons | OAuth flow breaks | Add `data: { turbo: false }` |
| No error frame | Errors replace page | Scope form to turbo_frame |

## Related Skills

- [setup.md](./setup.md): Initial Devise setup
- [controllers.md](./controllers.md): Controller customization
- [../../hotwire/SKILL.md](../../hotwire/SKILL.md): Turbo fundamentals

## References

- [Devise + Turbo Guide](https://github.com/heartcombo/devise#hotwireturbo)
- [Turbo Handbook - Forms](https://turbo.hotwired.dev/handbook/drive#form-submissions)
- [GoRails: Devise with Hotwire](https://gorails.com/episodes/devise-hotwire-turbo)
