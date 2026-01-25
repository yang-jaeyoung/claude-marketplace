# Turbo Native

## Overview

Turbo Native enables building hybrid mobile applications that wrap your Rails web app in a native shell. The web content renders in a native WebView with seamless navigation between web and native screens.

## Platforms

- **Turbo iOS**: Swift framework for iOS/iPadOS
- **Turbo Android**: Kotlin library for Android

## Basic Concept

```
┌─────────────────────────────────┐
│         Native Shell            │
│  ┌───────────────────────────┐  │
│  │       Native Header       │  │
│  ├───────────────────────────┤  │
│  │                           │  │
│  │      Web View             │  │
│  │      (Your Rails App)     │  │
│  │                           │  │
│  ├───────────────────────────┤  │
│  │       Native Tab Bar      │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

## Rails Configuration

### Path Configuration

```ruby
# config/initializers/turbo_native.rb
class TurboNativePathConfiguration
  def self.rules
    [
      # Native modal for new/edit forms
      { patterns: ["/new$", "/edit$"], properties: { presentation: "modal" } },

      # Native navigation for specific paths
      { patterns: ["/settings"], properties: { presentation: "push" } },

      # Replace current screen
      { patterns: ["/sessions/new"], properties: { presentation: "replace" } }
    ]
  end
end
```

### Detecting Native Requests

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  helper_method :turbo_native_app?

  private

  def turbo_native_app?
    request.user_agent.to_s.include?("Turbo Native")
  end
end
```

### Native-Specific Views

```erb
<!-- app/views/layouts/application.html.erb -->
<% unless turbo_native_app? %>
  <nav class="web-navigation">
    <%= render "shared/header" %>
  </nav>
<% end %>

<main>
  <%= yield %>
</main>

<% unless turbo_native_app? %>
  <%= render "shared/footer" %>
<% end %>
```

## Bridge Components

### JavaScript Bridge

```javascript
// app/javascript/controllers/bridge_controller.js
import { Controller } from "@hotwired/stimulus"
import { BridgeComponent } from "@hotwired/turbo-native-bridge"

export default class extends Controller {
  static component = "menu"

  connect() {
    this.bridge = new BridgeComponent(this.element, this.constructor.component)
  }

  showMenu() {
    this.bridge.send("showMenu", {
      title: "Options",
      items: ["Edit", "Delete", "Share"]
    }, (result) => {
      this.handleMenuSelection(result.selectedIndex)
    })
  }

  handleMenuSelection(index) {
    switch(index) {
      case 0: this.edit(); break
      case 1: this.delete(); break
      case 2: this.share(); break
    }
  }
}
```

### Native Button

```erb
<button data-controller="bridge"
        data-action="bridge#showMenu"
        data-bridge-component="menu">
  Options
</button>
```

## Path Properties

| Property | Values | Description |
|----------|--------|-------------|
| `presentation` | push, modal, replace, pop, refresh, clearAll, none | Navigation style |
| `context` | default, modal | Presentation context |
| `pull_to_refresh_enabled` | true, false | Enable pull to refresh |

## Native Form Handling

```erb
<!-- Use native-style submit button -->
<%= form_with model: @post, data: { controller: "native-form" } do |f| %>
  <%= f.text_field :title %>
  <%= f.submit "Save", data: { bridge_title: "Save Post" } %>
<% end %>
```

```javascript
// native_form_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  connect() {
    if (this.#isTurboNative) {
      this.#setupNativeForm()
    }
  }

  #setupNativeForm() {
    // Tell native app about form
    window.webkit?.messageHandlers?.form?.postMessage({
      submitTitle: this.element.querySelector("[data-bridge-title]")?.dataset.bridgeTitle
    })
  }

  get #isTurboNative() {
    return navigator.userAgent.includes("Turbo Native")
  }
}
```

## Authentication Flow

```ruby
# app/controllers/sessions_controller.rb
class SessionsController < ApplicationController
  def create
    if user = User.authenticate(params[:email], params[:password])
      sign_in(user)

      if turbo_native_app?
        # Signal native app about successful auth
        render json: { token: user.auth_token }, status: :ok
      else
        redirect_to root_path
      end
    else
      render :new, status: :unprocessable_entity
    end
  end
end
```

## Deep Linking

```ruby
# config/routes.rb
Rails.application.routes.draw do
  # Universal links / App links
  get "/.well-known/apple-app-site-association", to: "deep_links#apple"
  get "/.well-known/assetlinks.json", to: "deep_links#android"
end
```

```ruby
# app/controllers/deep_links_controller.rb
class DeepLinksController < ApplicationController
  def apple
    render json: {
      applinks: {
        apps: [],
        details: [{
          appID: "TEAM_ID.com.example.app",
          paths: ["/posts/*", "/users/*"]
        }]
      }
    }
  end
end
```

## Push Notifications

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_many :push_tokens, dependent: :destroy

  def send_push_notification(title:, body:, data: {})
    push_tokens.each do |token|
      PushNotificationJob.perform_later(token, title, body, data)
    end
  end
end
```

## Strada Integration

Strada provides additional bridge components for richer native interactions:

```javascript
// app/javascript/controllers/strada/form_controller.js
import { BridgeComponent, BridgeElement } from "@hotwired/strada"

export default class extends BridgeComponent {
  static component = "form"
  static targets = ["submit"]

  submitTargetConnected(target) {
    const title = target.textContent
    this.send("connect", { title }, () => {
      target.click()
    })
  }
}
```

## Common Patterns

### Native-Only Navigation

```erb
<% if turbo_native_app? %>
  <!-- Native back button handled by shell -->
<% else %>
  <%= link_to "Back", :back, class: "back-button" %>
<% end %>
```

### Platform Detection

```ruby
def ios_app?
  turbo_native_app? && request.user_agent.include?("iOS")
end

def android_app?
  turbo_native_app? && request.user_agent.include?("Android")
end
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Navigation not working | Path config mismatch | Check path patterns |
| Bridge events not firing | Component not registered | Verify Strada setup |
| Auth loop | Token not persisted | Store auth token in native |
| Slow WebView | Not caching | Enable URL caching |

## Related

- [drive.md](./drive.md): Web navigation
- [frames.md](./frames.md): Partial updates
- [Turbo iOS](https://github.com/hotwired/turbo-ios)
- [Turbo Android](https://github.com/hotwired/turbo-android)
- [Strada](https://strada.hotwired.dev/)
