# app/queries/application_query.rb
# 쿼리 객체 기본 클래스
#
# 사용법:
#   posts = PostsQuery.new.call(status: "published", author_id: 1)
#   posts = PostsQuery.new(Post.featured).call(q: "ruby")

class ApplicationQuery
  def initialize(scope = default_scope)
    @scope = scope
  end

  def call(filters = {})
    raise NotImplementedError, "Subclass must implement #call"
  end

  private

  def default_scope
    raise NotImplementedError, "Subclass must implement #default_scope"
  end

  # 필터 헬퍼
  def filter_by(scope, column, value)
    value.present? ? scope.where(column => value) : scope
  end

  def search_by(scope, columns, query)
    return scope if query.blank?

    conditions = columns.map { |col| "#{col} ILIKE :q" }.join(" OR ")
    scope.where(conditions, q: "%#{query}%")
  end

  def order_by(scope, column, direction = :desc)
    scope.order(column => direction)
  end
end
