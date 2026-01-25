# app/services/result.rb
# 서비스 객체 결과를 캡슐화하는 Value Object
#
# 사용법:
#   Result.success(post)      # 성공
#   Result.failure(errors)    # 실패
#
#   result.success?  # true/false
#   result.failure?  # true/false
#   result.value     # 성공 시 반환값
#   result.errors    # 실패 시 에러

class Result
  attr_reader :value, :errors

  def initialize(success:, value: nil, errors: nil)
    @success = success
    @value = value
    @errors = errors
  end

  def success? = @success
  def failure? = !@success

  def self.success(value)
    new(success: true, value: value)
  end

  def self.failure(errors)
    new(success: false, errors: errors)
  end

  # 체이닝 지원
  def and_then
    return self if failure?
    yield(value)
  end

  def or_else
    return self if success?
    yield(errors)
  end
end
