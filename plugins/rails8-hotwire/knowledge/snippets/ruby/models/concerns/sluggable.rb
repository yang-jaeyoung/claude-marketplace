# app/models/concerns/sluggable.rb
# URL 친화적 슬러그 생성 Concern
#
# 사용법:
#   class Post < ApplicationRecord
#     include Sluggable
#     sluggable_column :title  # 슬러그 생성 소스 컬럼
#   end
#
#   @post.to_param  # "123-my-post-title" 반환
#
# 마이그레이션:
#   add_column :posts, :slug, :string
#   add_index :posts, :slug, unique: true

module Sluggable
  extend ActiveSupport::Concern

  included do
    before_validation :generate_slug, if: :should_generate_slug?
    validates :slug, uniqueness: true, allow_nil: true
  end

  class_methods do
    def sluggable_column(column = :title)
      @sluggable_column = column
    end

    def get_sluggable_column
      @sluggable_column || :title
    end
  end

  def to_param
    slug.present? ? "#{id}-#{slug}" : id.to_s
  end

  private

  def generate_slug
    source = send(self.class.get_sluggable_column)
    return if source.blank?

    base_slug = source.parameterize
    self.slug = ensure_unique_slug(base_slug)
  end

  def should_generate_slug?
    slug.blank? && send(self.class.get_sluggable_column).present?
  end

  def ensure_unique_slug(base_slug)
    slug = base_slug
    counter = 1

    while self.class.unscoped.where(slug: slug).where.not(id: id).exists?
      slug = "#{base_slug}-#{counter}"
      counter += 1
    end

    slug
  end
end
