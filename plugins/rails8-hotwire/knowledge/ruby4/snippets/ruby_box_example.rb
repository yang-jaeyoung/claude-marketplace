# Ruby 4.0 Ruby::Box Examples
# 루비 4.0 Ruby::Box 예제
#
# IMPORTANT: Ruby::Box is experimental and requires RUBY_BOX=1 environment variable
# 중요: Ruby::Box는 실험적이며 RUBY_BOX=1 환경 변수가 필요합니다

# =============================================================================
# BASIC USAGE
# 기본 사용법
# =============================================================================

# Check if Ruby::Box is available
unless defined?(Ruby::Box)
  puts "Ruby::Box not available. Run with RUBY_BOX=1 environment variable."
  puts "Example: RUBY_BOX=1 ruby #{__FILE__}"
  exit 1
end

# Create a basic box
box = Ruby::Box.new

# Define classes in the box
box.instance_eval do
  class Greeting
    def self.hello(name)
      "Hello, #{name}!"
    end
  end
end

# Use from within box
result = box.instance_eval { Greeting.hello("World") }
puts result  #=> "Hello, World!"

# Verify isolation - Greeting is not in global namespace
puts defined?(Greeting)  #=> nil

# =============================================================================
# ISOLATION DEMONSTRATION
# 격리 시연
# =============================================================================

class IsolationDemo
  def self.run
    # Global String is unmodified
    puts "Global String methods: #{String.instance_methods.grep(/box_/).count}"

    # Create box with monkey patch
    box = Ruby::Box.new
    box.instance_eval do
      class String
        def box_special
          "Special: #{self}"
        end
      end
    end

    # Inside box - method exists
    box_result = box.instance_eval { "test".box_special }
    puts "Inside box: #{box_result}"  #=> "Special: test"

    # Outside box - method doesn't exist
    puts "Outside box responds to box_special?: #{"test".respond_to?(:box_special)}"
    #=> false
  end
end

# =============================================================================
# PLUGIN SYSTEM EXAMPLE
# 플러그인 시스템 예제
# =============================================================================

class PluginManager
  def initialize
    @plugins = {}
  end

  def register(name, &definition)
    box = Ruby::Box.new
    box.instance_eval(&definition)
    @plugins[name] = {
      box: box,
      registered_at: Time.now
    }
  end

  def run(plugin_name, method_name, *args)
    plugin = @plugins[plugin_name]
    raise "Plugin not found: #{plugin_name}" unless plugin

    plugin[:box].instance_eval do
      send(method_name, *args)
    end
  end

  def list_plugins
    @plugins.keys
  end
end

# Usage:
# manager = PluginManager.new
#
# manager.register(:calculator) do
#   def add(a, b)
#     a + b
#   end
#
#   def multiply(a, b)
#     a * b
#   end
# end
#
# manager.register(:formatter) do
#   def format_currency(amount)
#     "$#{sprintf('%.2f', amount)}"
#   end
# end
#
# manager.run(:calculator, :add, 1, 2)       #=> 3
# manager.run(:formatter, :format_currency, 42.5)  #=> "$42.50"

# =============================================================================
# TEST ISOLATION HELPER
# 테스트 격리 헬퍼
# =============================================================================

class TestIsolator
  def self.run_isolated(&block)
    box = Ruby::Box.new
    box.instance_eval(&block)
  end

  def self.with_isolated_constants(&block)
    box = Ruby::Box.new
    result = box.instance_eval(&block)

    # Return deep copy to avoid leaking box references
    Marshal.load(Marshal.dump(result))
  rescue TypeError
    # If result can't be marshaled, return as-is
    result
  end
end

# Usage:
# result = TestIsolator.run_isolated do
#   CONST = "isolated"
#   class Temp
#     def value
#       CONST
#     end
#   end
#   Temp.new.value
# end
#
# puts result  #=> "isolated"
# puts defined?(CONST)  #=> nil
# puts defined?(Temp)   #=> nil

# =============================================================================
# SANDBOXED CODE RUNNER
# 샌드박스 코드 실행기
# =============================================================================

class SafeRunner
  # NOTE: This is NOT a security sandbox!
  # For security, use OS-level isolation (containers, VMs)

  def initialize
    @box = Ruby::Box.new
    setup_safe_methods
  end

  def setup_safe_methods
    @box.instance_eval do
      # Define allowed operations
      module SafeMath
        def self.calculate(expr)
          # Only allow simple arithmetic
          # This is a simplified example
          eval(expr.gsub(/[^0-9+\-*\/().\s]/, ''))
        end
      end

      module SafeString
        def self.process(str)
          str.upcase.reverse
        end
      end
    end
  end

  def run_math(expression)
    @box.instance_eval { SafeMath.calculate(expression) }
  end

  def run_string(text)
    @box.instance_eval { SafeString.process(text) }
  end
end

# Usage:
# runner = SafeRunner.new
# runner.run_math("2 + 3 * 4")  #=> 14
# runner.run_string("hello")    #=> "OLLEH"

# =============================================================================
# MULTI-TENANT CONFIGURATION
# 멀티테넌트 설정
# =============================================================================

class TenantConfiguration
  def initialize
    @configs = {}
  end

  def setup_tenant(tenant_id, &config_block)
    box = Ruby::Box.new
    box.instance_eval(&config_block)
    @configs[tenant_id] = box
  end

  def get_config(tenant_id, key)
    box = @configs[tenant_id]
    return nil unless box

    box.instance_eval { CONFIG[key] rescue nil }
  end

  def run_for_tenant(tenant_id, &block)
    box = @configs[tenant_id]
    return nil unless box

    box.instance_eval(&block)
  end
end

# Usage:
# tenants = TenantConfiguration.new
#
# tenants.setup_tenant("acme") do
#   CONFIG = {
#     theme: "blue",
#     max_users: 100
#   }.freeze
# end
#
# tenants.setup_tenant("beta") do
#   CONFIG = {
#     theme: "green",
#     max_users: 50
#   }.freeze
# end
#
# tenants.get_config("acme", :theme)  #=> "blue"
# tenants.get_config("beta", :theme)  #=> "green"

# =============================================================================
# LIBRARY VERSION ISOLATION
# 라이브러리 버전 격리
# =============================================================================

class LibraryLoader
  def initialize
    @libraries = {}
  end

  def load_version(name, version, &setup)
    key = "#{name}@#{version}"
    box = Ruby::Box.new
    box.instance_eval(&setup) if block_given?
    @libraries[key] = box
    key
  end

  def call(key, method, *args)
    box = @libraries[key]
    raise "Library not loaded: #{key}" unless box

    box.instance_eval { send(method, *args) }
  end
end

# Usage:
# loader = LibraryLoader.new
#
# # Load "v1" of a library
# loader.load_version("api", "1.0") do
#   def format(data)
#     { v1: data }
#   end
# end
#
# # Load "v2" of the same library
# loader.load_version("api", "2.0") do
#   def format(data)
#     { version: 2, payload: data }
#   end
# end
#
# loader.call("api@1.0", :format, "test")  #=> {v1: "test"}
# loader.call("api@2.0", :format, "test")  #=> {version: 2, payload: "test"}

# =============================================================================
# RUN EXAMPLES
# 예제 실행
# =============================================================================

if __FILE__ == $0
  puts "=" * 60
  puts "Ruby::Box Examples"
  puts "=" * 60
  puts

  if defined?(Ruby::Box)
    puts "✓ Ruby::Box is available"
    puts

    # Run isolation demo
    puts "Isolation Demo:"
    IsolationDemo.run
    puts

    # Plugin system demo
    puts "Plugin System Demo:"
    pm = PluginManager.new
    pm.register(:greeter) do
      def greet(name)
        "Hello, #{name}!"
      end
    end
    puts pm.run(:greeter, :greet, "Ruby 4.0")
    puts
  else
    puts "✗ Ruby::Box not available"
    puts "Run with: RUBY_BOX=1 ruby #{__FILE__}"
  end
end
