# Ruby 4.0 ZJIT Configuration Examples
# 루비 4.0 ZJIT 설정 예제

# =============================================================================
# BASIC ZJIT ACTIVATION
# 기본 ZJIT 활성화
# =============================================================================

# Method 1: Runtime activation
RubyVM::ZJIT.enable if defined?(RubyVM::ZJIT)

# Method 2: Check and enable with logging
if defined?(RubyVM::ZJIT)
  RubyVM::ZJIT.enable
  puts "ZJIT enabled: #{RubyVM::ZJIT.enabled?}"
else
  puts "ZJIT not available in this Ruby build"
end

# =============================================================================
# RAILS INITIALIZER
# Rails 초기화 설정
# =============================================================================

# config/initializers/jit.rb
if defined?(Rails)
  Rails.application.config.after_initialize do
    # Environment-based JIT selection
    case ENV['JIT_MODE']
    when 'zjit'
      if defined?(RubyVM::ZJIT)
        RubyVM::ZJIT.enable
        Rails.logger.info "ZJIT enabled for #{Rails.env}"
      else
        Rails.logger.warn "ZJIT requested but not available"
      end
    when 'yjit'
      if defined?(RubyVM::YJIT)
        RubyVM::YJIT.enable
        Rails.logger.info "YJIT enabled for #{Rails.env}"
      end
    else
      # Default: YJIT for production, nothing for development
      if Rails.env.production? && defined?(RubyVM::YJIT)
        RubyVM::YJIT.enable
        Rails.logger.info "YJIT enabled (production default)"
      end
    end

    # Log JIT status
    Rails.logger.info "JIT Status:"
    Rails.logger.info "  YJIT: #{defined?(RubyVM::YJIT) && RubyVM::YJIT.enabled?}"
    Rails.logger.info "  ZJIT: #{defined?(RubyVM::ZJIT) && RubyVM::ZJIT.enabled?}"
  end
end

# =============================================================================
# CONDITIONAL JIT HELPER
# 조건부 JIT 헬퍼
# =============================================================================

module JITHelper
  class << self
    def enable_best_available
      if ENV['JIT_MODE'] == 'zjit' && zjit_available?
        RubyVM::ZJIT.enable
        :zjit
      elsif yjit_available?
        RubyVM::YJIT.enable
        :yjit
      else
        :none
      end
    end

    def yjit_available?
      defined?(RubyVM::YJIT) && RubyVM::YJIT.respond_to?(:enable)
    end

    def zjit_available?
      defined?(RubyVM::ZJIT) && RubyVM::ZJIT.respond_to?(:enable)
    end

    def current_jit
      if zjit_available? && RubyVM::ZJIT.enabled?
        :zjit
      elsif yjit_available? && RubyVM::YJIT.enabled?
        :yjit
      else
        :none
      end
    end

    def status
      {
        ruby_version: Ruby::VERSION,
        yjit: {
          available: yjit_available?,
          enabled: yjit_available? && RubyVM::YJIT.enabled?
        },
        zjit: {
          available: zjit_available?,
          enabled: zjit_available? && RubyVM::ZJIT.enabled?
        },
        current: current_jit
      }
    end
  end
end

# Usage:
# JITHelper.enable_best_available
# puts JITHelper.status

# =============================================================================
# PUMA CONFIGURATION WITH ZJIT
# ZJIT와 함께 Puma 설정
# =============================================================================

# config/puma.rb
=begin
on_worker_fork do
  # Enable JIT in forked workers
  case ENV['JIT_MODE']
  when 'zjit'
    RubyVM::ZJIT.enable if defined?(RubyVM::ZJIT)
  when 'yjit'
    RubyVM::YJIT.enable if defined?(RubyVM::YJIT)
  end
end

after_worker_fork do
  # Log JIT status per worker
  jit = if defined?(RubyVM::ZJIT) && RubyVM::ZJIT.enabled?
          "ZJIT"
        elsif defined?(RubyVM::YJIT) && RubyVM::YJIT.enabled?
          "YJIT"
        else
          "None"
        end

  puts "[Worker #{Process.pid}] JIT: #{jit}"
end
=end

# =============================================================================
# DOCKER CONFIGURATION
# Docker 설정
# =============================================================================

# Example Dockerfile snippet:
=begin
FROM ruby:4.0

# Set JIT mode via environment
ENV JIT_MODE=yjit

# For ZJIT experimentation:
# ENV JIT_MODE=zjit
=end

# docker-compose.yml snippet:
=begin
services:
  web:
    build: .
    environment:
      - JIT_MODE=yjit  # Production: use stable YJIT

  web-experimental:
    build: .
    environment:
      - JIT_MODE=zjit  # Testing: use experimental ZJIT
    profiles:
      - experimental
=end

# =============================================================================
# BENCHMARK WITH JIT COMPARISON
# JIT 비교 벤치마크
# =============================================================================

if __FILE__ == $0
  require 'benchmark'

  def fibonacci(n)
    return n if n <= 1
    fibonacci(n - 1) + fibonacci(n - 2)
  end

  puts "Ruby #{Ruby::VERSION}"
  puts "JIT Status: #{JITHelper.status}"
  puts

  # Warmup
  10.times { fibonacci(20) }

  # Benchmark
  Benchmark.bm(15) do |x|
    x.report("fibonacci(30):") do
      10.times { fibonacci(30) }
    end
  end
end
