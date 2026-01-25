# app/jobs/application_job.rb
# 모든 Job의 기본 클래스

class ApplicationJob < ActiveJob::Base
  # 재시도 전략 기본값
  retry_on StandardError, wait: :polynomially_longer, attempts: 5

  # 직렬화 실패 시 폐기
  discard_on ActiveJob::DeserializationError

  # 에러 로깅
  rescue_from StandardError do |exception|
    Rails.logger.error "[#{self.class.name}] #{exception.message}"
    Rails.logger.error exception.backtrace.first(10).join("\n")

    # Sentry 등 에러 모니터링 연동
    # Sentry.capture_exception(exception)

    raise # 재시도를 위해 다시 발생
  end

  # 큐 우선순위 기본값
  queue_as :default

  private

  # 작업 진행 로깅 헬퍼
  def log_start
    Rails.logger.info "[#{self.class.name}] Started"
  end

  def log_complete
    Rails.logger.info "[#{self.class.name}] Completed"
  end
end
