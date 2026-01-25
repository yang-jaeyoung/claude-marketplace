# app/services/application_service.rb
# Rails 8 서비스 객체 기본 클래스
#
# 사용법:
#   result = Posts::CreateService.call(user: current_user, params: post_params)
#   if result.success?
#     redirect_to result.value
#   else
#     render :new, status: :unprocessable_entity
#   end

class ApplicationService
  def self.call(...)
    new(...).call
  end

  private

  # 서브클래스에서 사용할 헬퍼 메서드

  def success(value)
    Result.success(value)
  end

  def failure(errors)
    Result.failure(errors)
  end
end
