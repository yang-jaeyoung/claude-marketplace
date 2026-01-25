# spec/support/turbo.rb
# Turbo Stream 테스트 헬퍼

module TurboTestHelpers
  # Turbo Stream 요청 헬퍼
  def turbo_stream_headers
    { "Accept" => "text/vnd.turbo-stream.html" }
  end

  # Turbo Stream 응답 확인
  def expect_turbo_stream
    expect(response.media_type).to eq("text/vnd.turbo-stream.html")
  end

  # 특정 액션 포함 확인
  def expect_turbo_stream_action(action, target: nil)
    expect(response.body).to include("turbo-stream")
    expect(response.body).to include("action=\"#{action}\"")
    expect(response.body).to include("target=\"#{target}\"") if target
  end
end

RSpec.configure do |config|
  config.include TurboTestHelpers, type: :request
  config.include TurboTestHelpers, type: :system
end
