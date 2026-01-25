# app/policies/application_policy.rb
# Pundit 정책 기본 클래스
#
# 사용법:
#   class PostPolicy < ApplicationPolicy
#     def update?
#       owner_or_admin?
#     end
#   end
#
#   # 컨트롤러에서
#   authorize @post

class ApplicationPolicy
  attr_reader :user, :record

  def initialize(user, record)
    @user = user
    @record = record
  end

  # 기본 CRUD 정책
  def index?
    true
  end

  def show?
    true
  end

  def create?
    user.present?
  end

  def new?
    create?
  end

  def update?
    owner_or_admin?
  end

  def edit?
    update?
  end

  def destroy?
    owner_or_admin?
  end

  # === Scope 클래스 ===
  class Scope
    attr_reader :user, :scope

    def initialize(user, scope)
      @user = user
      @scope = scope
    end

    def resolve
      if user&.admin?
        scope.all
      else
        scope.where(user: user)
      end
    end
  end

  private

  # === 공통 헬퍼 메서드 ===
  def owner?
    record.respond_to?(:user_id) && record.user_id == user&.id
  end

  def admin?
    user&.admin?
  end

  def owner_or_admin?
    owner? || admin?
  end

  def same_account?
    record.respond_to?(:account_id) && record.account_id == user&.account_id
  end
end
