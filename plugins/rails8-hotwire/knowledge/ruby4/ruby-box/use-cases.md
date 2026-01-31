# Ruby::Box Use Cases / 활용 사례

> Practical applications of Ruby::Box for Rails and Ruby development.
> Rails 및 Ruby 개발을 위한 Ruby::Box의 실용적인 활용 사례.

## 1. Test Isolation / 테스트 격리

### Problem

Tests can leak state through class variables, monkey patches, or global state:

```ruby
# Test A modifies String
class String
  def test_helper
    "modified"
  end
end

# Test B unexpectedly sees modified String
"hello".test_helper #=> "modified" (unexpected!)
```

### Solution with Ruby::Box

```ruby
# spec/support/isolated_test.rb
module IsolatedTest
  def with_isolation(&block)
    box = Ruby::Box.new
    box.instance_eval(&block)
  end
end

# spec/models/user_spec.rb
RSpec.describe User do
  include IsolatedTest

  it "tests in isolation" do
    with_isolation do
      # Modifications here don't affect other tests
      class String
        def test_helper
          "only for this test"
        end
      end

      expect("hello".test_helper).to eq("only for this test")
    end
  end

  it "doesn't see previous test's modifications" do
    expect("hello").not_to respond_to(:test_helper)
  end
end
```

## 2. Plugin System / 플러그인 시스템

### Problem

Loading third-party plugins can pollute namespaces:

```ruby
# Plugin A
module MyApp
  class Helper
    # Plugin A's implementation
  end
end

# Plugin B (conflicts!)
module MyApp
  class Helper
    # Overwrites Plugin A!
  end
end
```

### Solution with Ruby::Box

```ruby
class PluginManager
  def initialize
    @plugins = {}
  end

  def load_plugin(name, path)
    box = Ruby::Box.new
    box.require(path)
    @plugins[name] = box
  end

  def run_plugin(name, method, *args)
    @plugins[name].instance_eval do
      send(method, *args)
    end
  end

  def list_plugins
    @plugins.keys
  end
end

# Usage
pm = PluginManager.new
pm.load_plugin(:analytics, "./plugins/analytics")
pm.load_plugin(:auth, "./plugins/auth")

# Each plugin has isolated namespace
pm.run_plugin(:analytics, :track, "page_view")
pm.run_plugin(:auth, :authenticate, user)
```

### Rails Plugin Example

```ruby
# lib/plugin_system.rb
class RailsPluginSystem
  class << self
    def plugins
      @plugins ||= {}
    end

    def register(name, &config)
      box = Ruby::Box.new
      box.instance_eval(&config)
      plugins[name] = box
    end

    def invoke(plugin_name, action, **params)
      plugins[plugin_name].instance_eval do
        send(action, **params)
      end
    end
  end
end

# config/initializers/plugins.rb
RailsPluginSystem.register(:payment) do
  def process(amount:, currency:)
    # Payment processing logic
    { success: true, transaction_id: SecureRandom.uuid }
  end
end

# In controller
class PaymentsController < ApplicationController
  def create
    result = RailsPluginSystem.invoke(:payment, :process,
      amount: params[:amount],
      currency: params[:currency]
    )
    render json: result
  end
end
```

## 3. Multi-Version Library Support / 다중 버전 라이브러리 지원

### Problem

Some applications need multiple versions of the same gem:

```ruby
# Legacy code needs old API
OldLibrary.old_method  # v1.x API

# New code needs new API
NewLibrary.new_method  # v2.x API

# Can't load both in same namespace!
```

### Solution with Ruby::Box

```ruby
class MultiVersionLoader
  def initialize
    @versions = {}
  end

  def load_version(name, version, gem_path)
    box = Ruby::Box.new
    box.instance_eval do
      $LOAD_PATH.unshift(gem_path)
      require name
    end
    @versions["#{name}-#{version}"] = box
  end

  def use_version(name, version, &block)
    key = "#{name}-#{version}"
    @versions[key].instance_eval(&block)
  end
end

# Usage
loader = MultiVersionLoader.new
loader.load_version("api_client", "1.0", "/gems/api_client-1.0/lib")
loader.load_version("api_client", "2.0", "/gems/api_client-2.0/lib")

# Use old version
loader.use_version("api_client", "1.0") do
  ApiClient.old_format_request(data)
end

# Use new version
loader.use_version("api_client", "2.0") do
  ApiClient.new_format_request(data)
end
```

## 4. Code Evaluation Sandbox / 코드 평가 샌드박스

### Problem

Evaluating user-provided code is dangerous:

```ruby
# DANGEROUS!
eval(user_code)  # Can do anything
```

### Solution with Ruby::Box (Note: Not a security boundary!)

```ruby
# ⚠️ This is namespace isolation, NOT security sandboxing
class CodeEvaluator
  ALLOWED_METHODS = %i[map select reduce sum]

  def initialize
    @box = Ruby::Box.new
    setup_safe_environment
  end

  def setup_safe_environment
    @box.instance_eval do
      # Define safe subset of operations
      module SafeArray
        def self.process(arr, &block)
          arr.map(&block)
        end
      end
    end
  end

  def evaluate(code, input_data)
    @box.instance_eval do
      # Only allow specific operations
      SafeArray.process(input_data) { |x| eval(code) }
    end
  rescue => e
    { error: e.message }
  end
end

evaluator = CodeEvaluator.new
evaluator.evaluate("x * 2", [1, 2, 3]) #=> [2, 4, 6]
```

## 5. Feature Flags with Isolated Implementations / 격리된 구현의 기능 플래그

### Implementation

```ruby
class FeatureBox
  def initialize
    @features = {}
  end

  def define_feature(name, enabled: false, &implementation)
    box = Ruby::Box.new
    box.instance_eval(&implementation)
    @features[name] = { box: box, enabled: enabled }
  end

  def enable(name)
    @features[name][:enabled] = true
  end

  def disable(name)
    @features[name][:enabled] = false
  end

  def run(name, method, *args)
    feature = @features[name]
    return nil unless feature[:enabled]

    feature[:box].instance_eval do
      send(method, *args)
    end
  end
end

# Usage
features = FeatureBox.new

features.define_feature(:new_algorithm) do
  def calculate(data)
    # New algorithm implementation
    data.sum * 1.5
  end
end

features.define_feature(:old_algorithm) do
  def calculate(data)
    # Old algorithm
    data.sum
  end
end

# Switch implementations
if user.beta_tester?
  features.enable(:new_algorithm)
  features.disable(:old_algorithm)
else
  features.enable(:old_algorithm)
end

features.run(:new_algorithm, :calculate, [1, 2, 3])
```

## 6. Library Development / 라이브러리 개발

### Testing Library in Isolation

```ruby
# Test that your library doesn't leak state
RSpec.describe "MyLibrary isolation" do
  it "doesn't pollute Object" do
    original_methods = Object.instance_methods

    box = Ruby::Box.new
    box.require("my_library")

    # Library loaded in box shouldn't affect Object
    expect(Object.instance_methods).to eq(original_methods)
  end

  it "can be loaded multiple times independently" do
    box1 = Ruby::Box.new
    box2 = Ruby::Box.new

    box1.require("my_library")
    box2.require("my_library")

    box1.instance_eval { MyLibrary.config = :a }
    box2.instance_eval { MyLibrary.config = :b }

    expect(box1.instance_eval { MyLibrary.config }).to eq(:a)
    expect(box2.instance_eval { MyLibrary.config }).to eq(:b)
  end
end
```

## 7. Rails Engine Isolation / Rails 엔진 격리

### Conceptual Example

```ruby
# More isolated Rails engines
class IsolatedEngine
  def initialize(engine_path)
    @box = Ruby::Box.new
    @box.require(engine_path)
  end

  def routes
    @box.instance_eval { Engine.routes }
  end

  def models
    @box.instance_eval { Engine.models }
  end
end

# Each engine in its own box
admin_engine = IsolatedEngine.new("admin_engine")
api_engine = IsolatedEngine.new("api_engine")

# No namespace conflicts between engines
```

## 8. REPL/Console Isolation / REPL/콘솔 격리

### Safe Console Mode

```ruby
class IsolatedConsole
  def initialize
    @box = Ruby::Box.new
    @history = []
  end

  def execute(code)
    result = @box.instance_eval(code)
    @history << { code: code, result: result }
    result
  rescue => e
    @history << { code: code, error: e.message }
    "Error: #{e.message}"
  end

  def reset
    @box = Ruby::Box.new
    @history.clear
    "Console reset"
  end
end

console = IsolatedConsole.new
console.execute("class Foo; end")
console.execute("Foo.new")
console.reset  # Fresh start
```

## Best Practices / 모범 사례

### 1. Prefer Reusing Boxes

```ruby
# ❌ Creating box for each operation
def process(data)
  box = Ruby::Box.new  # Overhead each time
  box.instance_eval { transform(data) }
end

# ✅ Reuse box
class Processor
  def initialize
    @box = Ruby::Box.new
    setup
  end

  def process(data)
    @box.instance_eval { transform(data) }
  end
end
```

### 2. Deep Copy Data Crossing Boundaries

```ruby
# ✅ Safe data transfer
def safe_transfer(data)
  Marshal.load(Marshal.dump(data))
end

result = box.instance_eval { compute }
safe_result = safe_transfer(result)
```

### 3. Document Isolation Guarantees

```ruby
# ✅ Clear documentation
class PluginRunner
  # @note Plugins run in isolated Ruby::Box
  # @note Plugins cannot access application classes
  # @note Plugins share Object/Kernel with host
  def run_plugin(name, action)
    @boxes[name].instance_eval { send(action) }
  end
end
```

## See Also / 참고

- [Ruby::Box Overview](INDEX.md)
- [Basic Usage](basics.md)
- [Isolation Patterns](isolation.md)
