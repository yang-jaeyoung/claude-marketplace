# app/jobs/application_job.rb
# ActiveJob (Solid Queue) 기본 클래스
#
# 사용법:
#   class MyJob < ApplicationJob
#     queue_as :default
#
#     def perform(record_id)
#       record = Record.find(record_id)
#       # 작업 로직
#     end
#   end
#
#   # 큐에 추가
#   MyJob.perform_later(record.id)

class ApplicationJob < ActiveJob::Base
  # 재시도 설정 (Solid Queue)
  retry_on ActiveRecord::Deadlocked, wait: 5.seconds, attempts: 3
  retry_on Net::OpenTimeout, wait: :polynomially_longer, attempts: 10

  # 삭제할 예외
  discard_on ActiveJob::DeserializationError

  # === 공통 콜백 ===
  before_perform :log_job_start
  after_perform :log_job_complete
  around_perform :track_execution_time

  private

  def log_job_start
    Rails.logger.info "[JOB] Starting #{self.class.name} with args: #{arguments.inspect}"
  end

  def log_job_complete
    Rails.logger.info "[JOB] Completed #{self.class.name}"
  end

  def track_execution_time
    start_time = Time.current
    yield
    duration = Time.current - start_time
    Rails.logger.info "[JOB] #{self.class.name} took #{duration.round(2)}s"
  end
end

# === 예시: 이메일 전송 Job ===
# class SendNotificationJob < ApplicationJob
#   queue_as :default
#
#   def perform(user_id, notification_type)
#     user = User.find(user_id)
#     NotificationMailer.send(notification_type, user).deliver_now
#   end
# end

# === 예시: 예약 실행 Job ===
# class DailyReportJob < ApplicationJob
#   queue_as :scheduled
#
#   def perform
#     Report.generate_daily
#
#     # 다음 실행 예약
#     self.class.set(wait_until: Date.tomorrow.noon).perform_later
#   end
# end

# === 예시: 배치 처리 Job ===
# class BatchProcessJob < ApplicationJob
#   queue_as :default
#
#   def perform(batch_ids)
#     batch_ids.each do |id|
#       ProcessRecordJob.perform_later(id)
#     end
#   end
# end
