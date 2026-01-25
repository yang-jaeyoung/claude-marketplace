# Devise Views Customization

## Overview

Guide to customizing Devise views with Tailwind CSS styling, ERB best practices, and modern UI patterns for Rails 8 applications.

## When to Use

- When customizing login/registration forms
- When matching authentication UI to your app design
- When adding custom fields to registration
- When implementing branded authentication pages

## Quick Start

```bash
# Generate all Devise views
rails generate devise:views

# Generate views for specific model
rails generate devise:views users

# Generate specific views only
rails generate devise:views -v registrations confirmations
```

## Main Patterns

### Pattern 1: Tailwind Styled Login Form

```erb
<%# app/views/devise/sessions/new.html.erb %>
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Sign in to your account
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Or
        <%= link_to "create a new account", new_registration_path(resource_name),
            class: "font-medium text-indigo-600 hover:text-indigo-500" %>
      </p>
    </div>

    <%= form_for(resource, as: resource_name, url: session_path(resource_name),
        html: { class: "mt-8 space-y-6" }) do |f| %>

      <div class="rounded-md shadow-sm -space-y-px">
        <div>
          <%= f.label :email, class: "sr-only" %>
          <%= f.email_field :email,
              autofocus: true,
              autocomplete: "email",
              placeholder: "Email address",
              class: "appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" %>
        </div>
        <div>
          <%= f.label :password, class: "sr-only" %>
          <%= f.password_field :password,
              autocomplete: "current-password",
              placeholder: "Password",
              class: "appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" %>
        </div>
      </div>

      <div class="flex items-center justify-between">
        <% if devise_mapping.rememberable? %>
          <div class="flex items-center">
            <%= f.check_box :remember_me, class: "h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded" %>
            <%= f.label :remember_me, class: "ml-2 block text-sm text-gray-900" %>
          </div>
        <% end %>

        <div class="text-sm">
          <%= link_to "Forgot your password?", new_password_path(resource_name),
              class: "font-medium text-indigo-600 hover:text-indigo-500" %>
        </div>
      </div>

      <div>
        <%= f.submit "Sign in",
            class: "group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" %>
      </div>
    <% end %>
  </div>
</div>
```

### Pattern 2: Registration Form with Custom Fields

```erb
<%# app/views/devise/registrations/new.html.erb %>
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Create your account
      </h2>
    </div>

    <%= form_for(resource, as: resource_name, url: registration_path(resource_name),
        html: { class: "mt-8 space-y-6" }) do |f| %>

      <%= render "devise/shared/error_messages", resource: resource %>

      <div class="space-y-4">
        <%# Custom name field %>
        <div>
          <%= f.label :name, class: "block text-sm font-medium text-gray-700" %>
          <%= f.text_field :name,
              autofocus: true,
              autocomplete: "name",
              class: "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" %>
        </div>

        <div>
          <%= f.label :email, class: "block text-sm font-medium text-gray-700" %>
          <%= f.email_field :email,
              autocomplete: "email",
              class: "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" %>
        </div>

        <div>
          <%= f.label :password, class: "block text-sm font-medium text-gray-700" %>
          <%= f.password_field :password,
              autocomplete: "new-password",
              class: "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" %>
          <p class="mt-1 text-xs text-gray-500">
            <%= @minimum_password_length %> characters minimum
          </p>
        </div>

        <div>
          <%= f.label :password_confirmation, class: "block text-sm font-medium text-gray-700" %>
          <%= f.password_field :password_confirmation,
              autocomplete: "new-password",
              class: "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" %>
        </div>
      </div>

      <div>
        <%= f.submit "Create account",
            class: "w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" %>
      </div>

      <p class="text-center text-sm text-gray-600">
        Already have an account?
        <%= link_to "Sign in", new_session_path(resource_name),
            class: "font-medium text-indigo-600 hover:text-indigo-500" %>
      </p>
    <% end %>
  </div>
</div>
```

### Pattern 3: Error Messages Partial

```erb
<%# app/views/devise/shared/_error_messages.html.erb %>
<% if resource.errors.any? %>
  <div class="rounded-md bg-red-50 p-4 mb-4">
    <div class="flex">
      <div class="flex-shrink-0">
        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
      </div>
      <div class="ml-3">
        <h3 class="text-sm font-medium text-red-800">
          <%= pluralize(resource.errors.count, "error") %> prohibited this action:
        </h3>
        <div class="mt-2 text-sm text-red-700">
          <ul class="list-disc pl-5 space-y-1">
            <% resource.errors.full_messages.each do |message| %>
              <li><%= message %></li>
            <% end %>
          </ul>
        </div>
      </div>
    </div>
  </div>
<% end %>
```

### Pattern 4: Password Reset Form

```erb
<%# app/views/devise/passwords/new.html.erb %>
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Reset your password
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Enter your email address and we'll send you a link to reset your password.
      </p>
    </div>

    <%= form_for(resource, as: resource_name, url: password_path(resource_name),
        html: { method: :post, class: "mt-8 space-y-6" }) do |f| %>

      <%= render "devise/shared/error_messages", resource: resource %>

      <div>
        <%= f.label :email, class: "block text-sm font-medium text-gray-700" %>
        <%= f.email_field :email,
            autofocus: true,
            autocomplete: "email",
            class: "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" %>
      </div>

      <div>
        <%= f.submit "Send reset instructions",
            class: "w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" %>
      </div>

      <div class="text-center">
        <%= link_to "Back to sign in", new_session_path(resource_name),
            class: "font-medium text-indigo-600 hover:text-indigo-500" %>
      </div>
    <% end %>
  </div>
</div>
```

### Pattern 5: Social Login Buttons

```erb
<%# app/views/devise/shared/_social_login.html.erb %>
<div class="mt-6">
  <div class="relative">
    <div class="absolute inset-0 flex items-center">
      <div class="w-full border-t border-gray-300"></div>
    </div>
    <div class="relative flex justify-center text-sm">
      <span class="px-2 bg-white text-gray-500">Or continue with</span>
    </div>
  </div>

  <div class="mt-6 grid grid-cols-2 gap-3">
    <%= button_to omniauth_authorize_path(resource_name, :google_oauth2),
        method: :post,
        data: { turbo: false },
        class: "w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50" do %>
      <svg class="w-5 h-5" viewBox="0 0 24 24">
        <path fill="currentColor" d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
      </svg>
      <span class="ml-2">Google</span>
    <% end %>

    <%= button_to omniauth_authorize_path(resource_name, :github),
        method: :post,
        data: { turbo: false },
        class: "w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50" do %>
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clip-rule="evenodd" />
      </svg>
      <span class="ml-2">GitHub</span>
    <% end %>
  </div>
</div>
```

### Pattern 6: Edit Profile Form

```erb
<%# app/views/devise/registrations/edit.html.erb %>
<div class="max-w-2xl mx-auto py-10 px-4">
  <h2 class="text-2xl font-bold mb-8">Account Settings</h2>

  <%= form_for(resource, as: resource_name, url: registration_path(resource_name),
      html: { method: :put, class: "space-y-8" }) do |f| %>

    <%= render "devise/shared/error_messages", resource: resource %>

    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium mb-4">Profile Information</h3>

      <div class="space-y-4">
        <div>
          <%= f.label :name, class: "block text-sm font-medium text-gray-700" %>
          <%= f.text_field :name, class: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" %>
        </div>

        <div>
          <%= f.label :email, class: "block text-sm font-medium text-gray-700" %>
          <%= f.email_field :email, class: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" %>
          <% if devise_mapping.confirmable? && resource.pending_reconfirmation? %>
            <p class="mt-1 text-sm text-yellow-600">
              Currently waiting confirmation for: <%= resource.unconfirmed_email %>
            </p>
          <% end %>
        </div>
      </div>
    </div>

    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium mb-4">Change Password</h3>
      <p class="text-sm text-gray-500 mb-4">Leave blank if you don't want to change it</p>

      <div class="space-y-4">
        <div>
          <%= f.label :password, "New password", class: "block text-sm font-medium text-gray-700" %>
          <%= f.password_field :password, autocomplete: "new-password",
              class: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" %>
        </div>

        <div>
          <%= f.label :password_confirmation, class: "block text-sm font-medium text-gray-700" %>
          <%= f.password_field :password_confirmation, autocomplete: "new-password",
              class: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" %>
        </div>
      </div>
    </div>

    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium mb-4">Confirm Changes</h3>

      <div>
        <%= f.label :current_password, class: "block text-sm font-medium text-gray-700" %>
        <%= f.password_field :current_password, autocomplete: "current-password",
            class: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" %>
        <p class="mt-1 text-sm text-gray-500">We need your current password to confirm your changes</p>
      </div>
    </div>

    <div class="flex justify-between">
      <%= f.submit "Update",
          class: "py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" %>

      <%= button_to "Delete my account", registration_path(resource_name),
          method: :delete,
          data: { turbo_confirm: "Are you sure? This cannot be undone." },
          class: "py-2 px-4 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500" %>
    </div>
  <% end %>
</div>
```

## Generated Views Structure

```
app/views/devise/
├── confirmations/
│   └── new.html.erb
├── mailer/
│   ├── confirmation_instructions.html.erb
│   ├── email_changed.html.erb
│   ├── password_change.html.erb
│   ├── reset_password_instructions.html.erb
│   └── unlock_instructions.html.erb
├── passwords/
│   ├── edit.html.erb
│   └── new.html.erb
├── registrations/
│   ├── edit.html.erb
│   └── new.html.erb
├── sessions/
│   └── new.html.erb
├── shared/
│   ├── _error_messages.html.erb
│   └── _links.html.erb
└── unlocks/
    └── new.html.erb
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Inline styles | Maintenance nightmare | Use Tailwind classes |
| No error handling | Poor UX on validation | Use error_messages partial |
| Missing accessibility | Fails WCAG compliance | Add labels, ARIA attributes |
| Hardcoded strings | Can't internationalize | Use I18n |

## Related Skills

- [setup.md](./setup.md): Devise installation
- [controllers.md](./controllers.md): Controller customization
- [../../views/SKILL.md](../../views/SKILL.md): View helpers and partials

## References

- [Devise Views](https://github.com/heartcombo/devise#configuring-views)
- [Tailwind Forms Plugin](https://github.com/tailwindlabs/tailwindcss-forms)
