# app/models/concerns/soft_deletable.rb
# 소프트 삭제 기능을 제공하는 Concern
#
# 사용법:
#   class Post < ApplicationRecord
#     include SoftDeletable
#   end
#
#   @post.soft_delete   # deleted_at 설정
#   @post.restore       # deleted_at 해제
#   @post.deleted?      # 삭제 여부 확인
#
#   Post.kept           # 삭제되지 않은 레코드
#   Post.deleted        # 삭제된 레코드
#   Post.unscoped       # 모든 레코드 (default_scope 무시)
#
# 마이그레이션:
#   add_column :posts, :deleted_at, :datetime
#   add_index :posts, :deleted_at

module SoftDeletable
  extend ActiveSupport::Concern

  included do
    scope :kept, -> { where(deleted_at: nil) }
    scope :deleted, -> { where.not(deleted_at: nil) }

    # 주의: default_scope 사용 시 unscoped 필요할 수 있음
    default_scope { kept }
  end

  def soft_delete
    update(deleted_at: Time.current)
  end

  def restore
    update(deleted_at: nil)
  end

  def deleted?
    deleted_at.present?
  end

  # destroy를 soft_delete로 오버라이드 (선택적)
  # def destroy
  #   soft_delete
  # end
end
