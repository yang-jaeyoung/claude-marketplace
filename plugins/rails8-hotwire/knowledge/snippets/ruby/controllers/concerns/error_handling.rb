# app/controllers/concerns/error_handling.rb
# 컨트롤러 에러 처리 Concern
#
# 사용법:
#   class ApplicationController < ActionController::Base
#     include ErrorHandling
#   end

module ErrorHandling
  extend ActiveSupport::Concern

  included do
    rescue_from ActiveRecord::RecordNotFound, with: :not_found
    rescue_from Pundit::NotAuthorizedError, with: :forbidden
    rescue_from ActionController::ParameterMissing, with: :bad_request
  end

  private

  def not_found
    respond_to do |format|
      format.html do
        render "errors/not_found", status: :not_found, layout: "application"
      end
      format.json do
        render json: { error: "Not found" }, status: :not_found
      end
      format.turbo_stream do
        flash.now[:alert] = "찾을 수 없습니다"
        render turbo_stream: turbo_stream.update("flash", partial: "shared/flash")
      end
    end
  end

  def forbidden
    respond_to do |format|
      format.html do
        redirect_to root_path, alert: "권한이 없습니다"
      end
      format.json do
        render json: { error: "Forbidden" }, status: :forbidden
      end
      format.turbo_stream do
        flash.now[:alert] = "권한이 없습니다"
        render turbo_stream: turbo_stream.update("flash", partial: "shared/flash")
      end
    end
  end

  def bad_request(exception)
    respond_to do |format|
      format.html do
        redirect_back fallback_location: root_path, alert: exception.message
      end
      format.json do
        render json: { error: exception.message }, status: :bad_request
      end
    end
  end

  def internal_error(exception)
    Rails.logger.error(exception.message)
    Rails.logger.error(exception.backtrace.join("\n"))

    respond_to do |format|
      format.html do
        render "errors/internal_error", status: :internal_server_error
      end
      format.json do
        render json: { error: "Internal server error" }, status: :internal_server_error
      end
    end
  end
end
