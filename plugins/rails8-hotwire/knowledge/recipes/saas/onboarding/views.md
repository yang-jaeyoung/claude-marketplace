# Onboarding Views

## Layout with Progress Bar

```erb
<!-- app/views/layouts/onboarding.html.erb -->
<!DOCTYPE html>
<html>
  <head>
    <title>Setup - <%= current_account.name %></title>
    <%= csrf_meta_tags %>
    <%= csp_meta_tag %>
    <%= stylesheet_link_tag "application", "data-turbo-track": "reload" %>
    <%= javascript_importmap_tags %>
  </head>

  <body class="bg-gray-50" data-controller="onboarding-progress">
    <div class="min-h-screen flex flex-col">
      <!-- Header -->
      <header class="bg-white shadow-sm">
        <div class="max-w-4xl mx-auto px-6 py-4">
          <h1 class="text-lg font-semibold"><%= current_account.name %></h1>
        </div>
      </header>

      <!-- Progress Bar -->
      <div class="bg-white border-b">
        <div class="max-w-4xl mx-auto px-6 py-6">
          <div class="flex justify-between items-center mb-4">
            <% Onboarding::STEPS.each_with_index do |step_name, index| %>
              <% active = @onboarding.current_step_index >= index %>
              <div class="flex items-center">
                <div class="flex items-center <%= 'text-blue-600' if active %>">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center <%= active ? 'bg-blue-600 text-white' : 'bg-gray-200' %>">
                    <% if @onboarding.current_step_index > index %>
                      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                      </svg>
                    <% else %>
                      <%= index + 1 %>
                    <% end %>
                  </div>
                  <span class="ml-2 text-sm font-medium"><%= step_name.titleize %></span>
                </div>

                <% unless index == Onboarding::STEPS.length - 1 %>
                  <div class="w-16 h-0.5 mx-4 <%= active ? 'bg-blue-600' : 'bg-gray-200' %>"></div>
                <% end %>
              </div>
            <% end %>
          </div>

          <!-- Progress percentage -->
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                 style="width: <%= @onboarding.progress_percentage %>%"></div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <main class="flex-grow">
        <div class="max-w-2xl mx-auto px-6 py-12">
          <%= yield %>
        </div>
      </main>
    </div>
  </body>
</html>
```

## Step 1: Profile

```erb
<!-- app/views/onboarding/profile.html.erb -->
<div class="bg-white rounded-lg shadow-sm p-8">
  <h2 class="text-2xl font-bold mb-2">Tell us about yourself</h2>
  <p class="text-gray-600 mb-6">This helps your team recognize you</p>

  <%= form_with model: current_user, url: onboarding_path(step: "profile"), method: :patch do |f| %>
    <div class="mb-6">
      <%= f.label :name, "Full Name", class: "block text-sm font-medium mb-2" %>
      <%= f.text_field :name, class: "w-full border rounded-lg p-3", autofocus: true %>
      <%= render "shared/field_error", model: current_user, field: :name %>
    </div>

    <div class="mb-6">
      <%= f.label :title, "Job Title", class: "block text-sm font-medium mb-2" %>
      <%= f.text_field :title, class: "w-full border rounded-lg p-3", placeholder: "e.g., Product Manager" %>
    </div>

    <div class="mb-6">
      <%= f.label :avatar, "Profile Picture", class: "block text-sm font-medium mb-2" %>
      <%= f.file_field :avatar, accept: "image/*", class: "w-full" %>
    </div>

    <div class="flex justify-between items-center">
      <%= link_to "Skip", skip_onboarding_path, method: :post, class: "text-gray-600 hover:text-gray-900" %>
      <%= f.submit "Continue", class: "btn btn-primary" %>
    </div>
  <% end %>
</div>
```

## Step 2: Team

```erb
<!-- app/views/onboarding/team.html.erb -->
<div class="bg-white rounded-lg shadow-sm p-8">
  <h2 class="text-2xl font-bold mb-2">Invite your team</h2>
  <p class="text-gray-600 mb-6">Collaboration is better together</p>

  <%= form_with url: onboarding_path(step: "team"), method: :patch do |f| %>
    <div class="mb-6">
      <%= label_tag :emails, "Email addresses (comma-separated)", class: "block text-sm font-medium mb-2" %>
      <%= text_area_tag :emails, nil,
          class: "w-full border rounded-lg p-3",
          rows: 4,
          placeholder: "colleague@example.com, teammate@example.com" %>
      <p class="text-sm text-gray-500 mt-1">We'll send them an invitation to join your workspace</p>
    </div>

    <div class="flex justify-between items-center">
      <%= link_to "Skip", skip_onboarding_path, method: :post, class: "text-gray-600 hover:text-gray-900" %>
      <%= f.submit "Send Invitations", class: "btn btn-primary" %>
    </div>
  <% end %>
</div>
```

## Step 3: Workspace

```erb
<!-- app/views/onboarding/workspace.html.erb -->
<div class="bg-white rounded-lg shadow-sm p-8">
  <h2 class="text-2xl font-bold mb-2">Configure your workspace</h2>
  <p class="text-gray-600 mb-6">Customize how you work</p>

  <%= form_with url: onboarding_path(step: "workspace"), method: :patch do |f| %>
    <div class="mb-6">
      <%= label_tag :timezone, "Timezone", class: "block text-sm font-medium mb-2" %>
      <%= select_tag :timezone,
          options_for_select(ActiveSupport::TimeZone.all.map { |tz| [tz.to_s, tz.name] }, Time.zone.name),
          class: "w-full border rounded-lg p-3" %>
    </div>

    <div class="mb-6">
      <%= label_tag :default_view, "Default View", class: "block text-sm font-medium mb-2" %>
      <%= select_tag :default_view,
          options_for_select([["List View", "list"], ["Board View", "board"], ["Calendar View", "calendar"]], "list"),
          class: "w-full border rounded-lg p-3" %>
    </div>

    <div class="mb-6">
      <label class="flex items-center">
        <%= check_box_tag :notifications_enabled, "1", true, class: "mr-2" %>
        <span class="text-sm">Enable desktop notifications</span>
      </label>
    </div>

    <div class="flex justify-between items-center">
      <%= link_to "Back", onboarding_path(step: "team"), class: "text-gray-600 hover:text-gray-900" %>
      <%= f.submit "Continue", class: "btn btn-primary" %>
    </div>
  <% end %>
</div>
```

## Step 4: Preferences

```erb
<!-- app/views/onboarding/preferences.html.erb -->
<div class="bg-white rounded-lg shadow-sm p-8">
  <h2 class="text-2xl font-bold mb-2">Email preferences</h2>
  <p class="text-gray-600 mb-6">Choose what you want to hear about</p>

  <%= form_with url: onboarding_path(step: "preferences"), method: :patch do |f| %>
    <div class="space-y-4 mb-6">
      <label class="flex items-start">
        <%= check_box_tag :email_digest, "1", true, class: "mt-1 mr-3" %>
        <div>
          <div class="font-medium">Daily digest</div>
          <div class="text-sm text-gray-600">Summary of your team's activity</div>
        </div>
      </label>

      <label class="flex items-start">
        <%= check_box_tag :weekly_summary, "1", true, class: "mt-1 mr-3" %>
        <div>
          <div class="font-medium">Weekly summary</div>
          <div class="text-sm text-gray-600">Weekly highlights and metrics</div>
        </div>
      </label>

      <label class="flex items-start">
        <%= check_box_tag :product_updates, "1", true, class: "mt-1 mr-3" %>
        <div>
          <div class="font-medium">Product updates</div>
          <div class="text-sm text-gray-600">New features and improvements</div>
        </div>
      </label>
    </div>

    <div class="flex justify-between items-center">
      <%= link_to "Back", onboarding_path(step: "workspace"), class: "text-gray-600 hover:text-gray-900" %>
      <%= f.submit "Complete Setup", class: "btn btn-primary" %>
    </div>
  <% end %>
</div>
```

## Layout Features

| Feature | Implementation |
|---------|----------------|
| **Progress Indicator** | Step circles with checkmarks for completed steps |
| **Progress Bar** | Percentage-based visual progress |
| **Step Highlighting** | Blue color for active/completed steps |
| **Responsive** | Tailwind CSS for mobile-friendly layout |
| **Skip Navigation** | Skip links on each step |
| **Back Navigation** | Back links on workspace/preferences |

## Related Files

- [controller.md](./controller.md): Controller rendering these views
- [model.md](./model.md): Model providing progress data
- [jobs.md](./jobs.md): Stimulus controller for progress tracking
