# spec/rails_helper.rb 추가 설정
# RSpec 테스트 기본 구조
#
# 사용법:
#   RSpec.describe User, type: :model do
#     # 테스트 작성
#   end

# === Factory Bot 설정 ===
RSpec.configure do |config|
  config.include FactoryBot::Syntax::Methods
end

# === Devise 헬퍼 ===
RSpec.configure do |config|
  config.include Devise::Test::ControllerHelpers, type: :controller
  config.include Devise::Test::IntegrationHelpers, type: :request
end

# === Request 스펙 헬퍼 ===
module RequestSpecHelpers
  def json_response
    JSON.parse(response.body)
  end

  def auth_headers(user)
    { "Authorization" => "Bearer #{user.generate_jwt}" }
  end
end

RSpec.configure do |config|
  config.include RequestSpecHelpers, type: :request
end

# === Database Cleaner (Solid Queue용) ===
RSpec.configure do |config|
  config.before(:suite) do
    DatabaseCleaner.strategy = :transaction
    DatabaseCleaner.clean_with(:truncation)
  end

  config.around(:each) do |example|
    DatabaseCleaner.cleaning do
      example.run
    end
  end
end

# === Turbo Streams 테스트 헬퍼 ===
module TurboStreamHelpers
  def assert_turbo_stream(action:, target:)
    assert_select "turbo-stream[action='#{action}'][target='#{target}']"
  end
end

RSpec.configure do |config|
  config.include TurboStreamHelpers, type: :request
end
