# frozen_string_literal: true

# Custom Devise failure app for Rails 8 + Turbo compatibility
# Handles authentication failures properly with Turbo Drive
#
# Installation:
# 1. Create this file at app/lib/turbo_failure_app.rb
# 2. Add to config/initializers/devise.rb:
#
#    Devise.setup do |config|
#      config.warden do |manager|
#        manager.failure_app = TurboFailureApp
#      end
#    end
#
# Why this is needed:
# - Turbo expects specific HTTP status codes for redirects (303) and errors (422)
# - Default Devise failure app returns 302 which Turbo may not follow correctly
# - This ensures flash messages appear and redirects work with Turbo Drive
#
class TurboFailureApp < Devise::FailureApp
  # Handle Turbo Stream requests
  # Turbo sends Accept: text/vnd.turbo-stream.html for form submissions
  def respond
    if request_format == :turbo_stream
      redirect
    else
      super
    end
  end

  # Return 303 See Other for redirects (Turbo requirement)
  # Standard 302 Found may cause issues with Turbo Drive
  def redirect
    store_location!
    if flash[:timedout] && flash[:alert]
      flash.keep(:timedout)
      flash.keep(:alert)
    else
      flash[:alert] = i18n_message
    end

    redirect_to redirect_url, allow_other_host: false, status: :see_other
  end

  # Skip format check for Turbo requests
  # Allows html, turbo_stream, and wildcard formats
  def skip_format?
    %w[html turbo_stream */*].include?(request_format.to_s)
  end

  private

  # Determine request format
  def request_format
    @request_format ||= begin
      format = request.format.to_sym
      format = :turbo_stream if turbo_stream_request?
      format
    end
  end

  # Check if this is a Turbo Stream request
  def turbo_stream_request?
    request.accepts.any? { |type| type.to_s.include?("turbo-stream") }
  end
end

# Alternative: Simpler version if you don't need custom flash handling
#
# class TurboFailureApp < Devise::FailureApp
#   def respond
#     if request_format == :turbo_stream
#       redirect
#     else
#       super
#     end
#   end
#
#   def skip_format?
#     %w[html turbo_stream */*].include?(request_format.to_s)
#   end
# end
