---
name: rails8-views-partial-conventions
description: Naming conventions, organization patterns, and best practices for Rails partials
---

# Partial Conventions

## Overview

Rails partials follow specific naming conventions and organization patterns. Understanding these conventions ensures maintainable, discoverable, and performant views.

## When to Use

- When extracting reusable view code
- When organizing view components
- When standardizing file naming
- When deciding where to place partials

## Quick Start

```erb
<%# Partial naming: always starts with underscore %>
<%# app/views/posts/_post.html.erb %>
<article id="<%= dom_id(post) %>" class="post">
  <h2><%= post.title %></h2>
  <p><%= post.body %></p>
</article>

<%# Rendering: omit underscore %>
<%= render "posts/post", post: @post %>

<%# Collection rendering: Rails infers partial name %>
<%= render @posts %>
```

## Main Patterns

### Pattern 1: Naming Rules

```erb
<%# File names always start with underscore %>
_post.html.erb           # Correct
post.html.erb            # Wrong - not a partial

<%# When rendering, omit the underscore %>
<%= render "post" %>                    # Renders _post.html.erb
<%= render "posts/post" %>              # Renders posts/_post.html.erb
<%= render "shared/navbar" %>           # Renders shared/_navbar.html.erb

<%# Collection naming: singular form %>
_post.html.erb           # For collection rendering of @posts
_comment.html.erb        # For collection rendering of @comments

<%# Action-specific partials %>
_form.html.erb           # Shared form for new/edit
_list.html.erb           # List display
_card.html.erb           # Card display variant
```

### Pattern 2: Directory Organization

```
app/views/
├── posts/
│   ├── index.html.erb
│   ├── show.html.erb
│   ├── new.html.erb
│   ├── edit.html.erb
│   ├── _post.html.erb         # Single post display
│   ├── _form.html.erb         # Shared form
│   ├── _header.html.erb       # Post header
│   └── _sidebar.html.erb      # Post-specific sidebar
│
├── comments/
│   ├── _comment.html.erb      # Single comment
│   ├── _form.html.erb         # Comment form
│   └── _list.html.erb         # Comments list wrapper
│
├── shared/                    # Cross-controller partials
│   ├── _navbar.html.erb
│   ├── _footer.html.erb
│   ├── _flash.html.erb
│   ├── _pagination.html.erb
│   ├── _search.html.erb
│   ├── _empty_state.html.erb
│   └── _form_errors.html.erb
│
├── layouts/                   # Layout files
│   └── application.html.erb
│
└── components/                # ViewComponent or UI components
    └── card/
        ├── _card.html.erb
        └── _header.html.erb
```

### Pattern 3: Partial Lookup Path

```erb
<%# Rails searches in this order: %>

<%# 1. Current controller's view directory %>
<%# In PostsController, render "form" looks for: %>
<%# app/views/posts/_form.html.erb %>

<%# 2. Explicit path %>
<%= render "comments/form" %>
<%# app/views/comments/_form.html.erb %>

<%# 3. Shared directory (explicit) %>
<%= render "shared/flash" %>
<%# app/views/shared/_flash.html.erb %>

<%# 4. Application directory (for layouts) %>
<%= render "application/navbar" %>
<%# app/views/application/_navbar.html.erb %>
```

### Pattern 4: Render Syntax Variations

```erb
<%# Basic render %>
<%= render "post" %>

<%# With explicit partial keyword %>
<%= render partial: "post" %>

<%# With local variables %>
<%= render "post", post: @post %>
<%= render partial: "post", locals: { post: @post } %>

<%# Collection rendering %>
<%= render @posts %>                                    # Auto-detects partial
<%= render partial: "post", collection: @posts %>       # Explicit
<%= render partial: "post", collection: @posts, as: :article %>  # Rename variable

<%# With layout wrapper %>
<%= render partial: "post", collection: @posts, layout: "post_wrapper" %>

<%# Render object (model) %>
<%= render @post %>                    # Renders posts/_post.html.erb
<%= render @comment %>                 # Renders comments/_comment.html.erb

<%# Render with spacer %>
<%= render partial: "post", collection: @posts, spacer_template: "post_spacer" %>
```

### Pattern 5: Convention for Model Partials

```erb
<%# When rendering a model, Rails looks for: %>
<%# app/views/{model_plural}/_{model_singular}.html.erb %>

<%= render @post %>
<%# Renders: app/views/posts/_post.html.erb %>
<%# With local: post = @post %>

<%= render @user.posts %>
<%# Renders: app/views/posts/_post.html.erb for each post %>

<%# For namespaced models %>
<%= render @admin_user %>
<%# Renders: app/views/admin/users/_user.html.erb %>

<%# Override with to_partial_path %>
class Post < ApplicationRecord
  def to_partial_path
    "posts/card"  # Renders posts/_card.html.erb
  end
end
```

### Pattern 6: Semantic Naming

```erb
<%# Name partials by their purpose, not their content %>

<%# Good: Describes what it represents %>
_post.html.erb
_comment.html.erb
_user_card.html.erb
_form.html.erb
_sidebar.html.erb
_pagination.html.erb
_empty_state.html.erb

<%# Bad: Generic or unclear %>
_partial.html.erb
_item.html.erb
_content.html.erb
_div.html.erb

<%# For variants, use descriptive suffixes %>
_post.html.erb          # Default display
_post_card.html.erb     # Card variant
_post_row.html.erb      # Table row variant
_post_compact.html.erb  # Compact variant
```

### Pattern 7: Format-Specific Partials

```erb
<%# Rails can have format-specific partials %>
_post.html.erb           # HTML format
_post.turbo_stream.erb   # Turbo Stream format
_post.json.jbuilder      # JSON format
_post.xml.builder        # XML format

<%# In controller %>
def show
  @post = Post.find(params[:id])
  respond_to do |format|
    format.html          # Renders show.html.erb
    format.turbo_stream  # Renders show.turbo_stream.erb
    format.json          # Renders show.json.jbuilder
  end
end
```

### Pattern 8: Prefixes for Special Partials

```erb
<%# Use consistent prefixes for special cases %>

<%# Form-related %>
_form.html.erb           # Main form
_form_fields.html.erb    # Just the fields (for nested forms)
_form_actions.html.erb   # Submit buttons section

<%# Variants %>
_post_card.html.erb      # Card display
_post_list.html.erb      # List item display
_post_table_row.html.erb # Table row display

<%# State-specific %>
_empty_state.html.erb    # When collection is empty
_loading_state.html.erb  # Loading indicator
_error_state.html.erb    # Error display

<%# Component parts %>
_header.html.erb         # Header section
_footer.html.erb         # Footer section
_actions.html.erb        # Action buttons
```

## Partial Checklist

Before creating a partial, verify:

- [ ] Name starts with underscore
- [ ] Name is singular for collections
- [ ] Located in appropriate directory
- [ ] Purpose is clear from name
- [ ] Not duplicating existing partial
- [ ] Local variables are documented

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Forgetting underscore | File not found as partial | Always prefix with `_` |
| Plural partial names | Confusion with collections | Use singular: `_post` not `_posts` |
| Deep nesting in shared/ | Hard to find | Keep shared/ flat, use subdirs only for related groups |
| Generic names | Unclear purpose | Use descriptive, specific names |
| Inconsistent paths | Team confusion | Document conventions in CLAUDE.md |
| Format in filename wrong | Not rendered | Use `_name.html.erb` not `_name.erb.html` |

## Related Skills

- [collections.md](./collections.md): Collection rendering patterns
- [locals.md](./locals.md): Local variable passing
- [turbo-frames.md](./turbo-frames.md): Turbo Frame partials

## References

- [Rails Layouts and Rendering](https://guides.rubyonrails.org/layouts_and_rendering.html#using-partials)
- [Partial Render API](https://api.rubyonrails.org/classes/ActionView/PartialRenderer.html)
