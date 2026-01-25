# Blog Application

## Overview

Complete blog with posts, comments, tags, RSS feed, and admin CRUD. Production-ready blogging platform.

## Prerequisites

- [models/associations](../../models/associations.md)
- [hotwire/turbo-frames](../../hotwire/turbo-frames.md)
- [recipes/comments](../features/comments.md)

## Quick Start

```bash
rails new blog
cd blog
rails generate scaffold Post title:string body:text published:boolean
rails generate model Tag name:string
rails generate model Tagging post:references tag:references
rails db:migrate
```

## Implementation

### Models

```ruby
# app/models/post.rb
class Post < ApplicationRecord
  belongs_to :author, class_name: "User"
  has_many :comments, dependent: :destroy
  has_many :taggings, dependent: :destroy
  has_many :tags, through: :taggings

  validates :title, presence: true
  validates :body, presence: true

  scope :published, -> { where(published: true) }
  scope :recent, -> { order(created_at: :desc) }

  def tag_list
    tags.pluck(:name).join(", ")
  end

  def tag_list=(names)
    self.tags = names.split(",").map do |name|
      Tag.find_or_create_by!(name: name.strip)
    end
  end
end

# app/models/tag.rb
class Tag < ApplicationRecord
  has_many :taggings, dependent: :destroy
  has_many :posts, through: :taggings

  validates :name, presence: true, uniqueness: true
end
```

### Controllers

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  skip_before_action :authenticate_user!, only: [:index, :show]

  def index
    @posts = Post.published.recent.page(params[:page])
  end

  def show
    @post = Post.find(params[:id])
    @comment = Comment.new
  end

  def new
    @post = current_user.posts.build
  end

  def create
    @post = current_user.posts.build(post_params)

    if @post.save
      redirect_to @post, notice: "Post created"
    else
      render :new, status: :unprocessable_entity
    end
  end

  private

  def post_params
    params.require(:post).permit(:title, :body, :published, :tag_list)
  end
end
```

### RSS Feed

```ruby
# config/routes.rb
resources :posts do
  collection do
    get :feed, defaults: { format: :rss }
  end
end

# app/views/posts/feed.rss.builder
xml.instruct! :xml, version: "1.0"
xml.rss version: "2.0" do
  xml.channel do
    xml.title "My Blog"
    xml.description "Latest posts"
    xml.link posts_url

    @posts.each do |post|
      xml.item do
        xml.title post.title
        xml.description post.body
        xml.pubDate post.created_at.to_s(:rfc822)
        xml.link post_url(post)
        xml.guid post_url(post)
      end
    end
  end
end
```

## Testing

```ruby
# spec/models/post_spec.rb
require "rails_helper"

RSpec.describe Post, type: :model do
  it "parses tag list" do
    post = create(:post)
    post.tag_list = "rails, ruby, web"

    expect(post.tags.count).to eq(3)
    expect(post.tags.pluck(:name)).to contain_exactly("rails", "ruby", "web")
  end
end
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| No pagination | Slow page loads | Use kaminari or pagy |
| Missing SEO tags | Poor discoverability | Add meta tags gem |
| No sitemap | Poor indexing | Generate sitemap.xml |

## Related Skills

- [models/associations](../../models/associations.md)
- [recipes/comments](../features/comments.md)
- [recipes/search](../features/search.md)

## References

- [Rails Blog Tutorial](https://guides.rubyonrails.org/getting_started.html)
