# spec/support/cuprite.rb
# Cuprite (Chrome 드라이버) 설정 - Selenium보다 30% 빠름

require "capybara/cuprite"

Capybara.register_driver(:cuprite) do |app|
  Capybara::Cuprite::Driver.new(
    app,
    window_size: [1440, 900],
    browser_options: {
      "no-sandbox": nil,
      "disable-gpu": nil,
      "disable-dev-shm-usage": nil
    },
    process_timeout: 30,
    timeout: 30,
    inspector: ENV["INSPECTOR"].present?,
    headless: ENV["HEADLESS"] != "false"
  )
end

Capybara.default_driver = :rack_test
Capybara.javascript_driver = :cuprite

# CI 환경 설정
if ENV["CI"]
  Capybara.default_max_wait_time = 10
end
