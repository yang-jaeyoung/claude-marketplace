# Comment Controllers

Controllers for managing comments and reactions with Turbo Stream responses.

## CommentsController

```ruby
# app/controllers/comments_controller.rb
class CommentsController < ApplicationController
  before_action :authenticate_user!
  before_action :set_post
  before_action :set_comment, only: [:edit, :update, :destroy]

  def create
    @comment = @post.comments.build(comment_params)
    @comment.user = current_user

    # Handle parent comment for threading
    if params[:parent_id].present?
      parent = @post.comments.find(params[:parent_id])
      @comment.parent = parent unless parent.max_depth_reached?
    end

    respond_to do |format|
      if @comment.save
        format.turbo_stream
        format.html { redirect_to @post, notice: "Comment posted" }
      else
        format.turbo_stream do
          render turbo_stream: turbo_stream.replace(
            dom_id_for_reply_form,
            partial: "comments/form",
            locals: { post: @post, comment: @comment, parent: @comment.parent }
          )
        end
        format.html { redirect_to @post, alert: "Failed to post comment" }
      end
    end
  end

  def edit
    authorize @comment
  end

  def update
    authorize @comment

    respond_to do |format|
      if @comment.update(comment_params)
        format.turbo_stream
        format.html { redirect_to @post, notice: "Comment updated" }
      else
        format.turbo_stream do
          render turbo_stream: turbo_stream.replace(
            dom_id(@comment, :edit),
            partial: "comments/edit_form",
            locals: { comment: @comment }
          )
        end
        format.html { render :edit, status: :unprocessable_entity }
      end
    end
  end

  def destroy
    authorize @comment

    @comment.destroy

    respond_to do |format|
      format.turbo_stream
      format.html { redirect_to @post, status: :see_other, notice: "Comment deleted" }
    end
  end

  private

  def set_post
    @post = Post.find(params[:post_id])
  end

  def set_comment
    @comment = @post.comments.find(params[:id])
  end

  def comment_params
    params.require(:comment).permit(:body, mentioned_user_ids: [])
  end

  def dom_id_for_reply_form
    if params[:parent_id]
      "reply_form_#{params[:parent_id]}"
    else
      "comment_form"
    end
  end
end
```

## ReactionsController

```ruby
# app/controllers/reactions_controller.rb
class ReactionsController < ApplicationController
  before_action :authenticate_user!
  before_action :set_comment

  def create
    @reaction = @comment.reactions.find_or_initialize_by(
      user: current_user,
      emoji: params[:emoji]
    )

    if @reaction.persisted?
      # Toggle off
      @reaction.destroy
      action = :removed
    else
      # Toggle on
      @reaction.save
      action = :added
    end

    respond_to do |format|
      format.turbo_stream do
        render turbo_stream: turbo_stream.replace(
          dom_id(@comment, :reactions),
          partial: "comments/reactions",
          locals: { comment: @comment.reload }
        )
      end
      format.html { redirect_to @comment.post }
    end
  end

  private

  def set_comment
    @comment = Comment.find(params[:comment_id])
  end
end
```

## Routes

```ruby
# config/routes.rb
Rails.application.routes.draw do
  resources :posts do
    resources :comments, only: [:create, :edit, :update, :destroy]
  end

  resources :comments, only: [] do
    resources :reactions, only: [:create]
  end
end
```

## Key Features

### Nested Comments

- `parent_id` parameter determines threading
- `max_depth_reached?` prevents excessive nesting
- Parent comment ID embedded in form URL

### Turbo Stream Responses

Both controllers use dual responses:
- **Success**: Turbo Stream template (real-time update)
- **Failure**: Replace form with errors inline
- **HTML fallback**: Traditional redirect for non-Turbo requests

### Reaction Toggle

ReactionsController implements toggle behavior:
1. Find or initialize reaction by user + emoji
2. If already exists → destroy (toggle off)
3. If new → save (toggle on)
4. Replace reactions partial via Turbo Stream

### Authorization

Uses Pundit (or similar) for access control:
- Only comment author can edit/delete
- `authorize @comment` checks permissions
- Customize policy in `app/policies/comment_policy.rb`

## Related

- [Back to Index](SKILL.md)
- [Previous: Models](model.md)
- [Next: Views](views.md)
