# Ruby::Box Isolation Patterns / 격리 패턴

> Understanding how Ruby::Box isolates code and state.
> Ruby::Box가 코드와 상태를 격리하는 방법 이해하기.

## Isolation Model / 격리 모델

Ruby::Box creates isolated namespaces within a single Ruby process. Understanding what is and isn't isolated is crucial for effective use.

## What Gets Isolated / 격리되는 것

### 1. Class Definitions / 클래스 정의

```ruby
box = Ruby::Box.new

box.instance_eval do
  class IsolatedClass
    def method
      "Only exists in box"
    end
  end
end

# Inside box
box.instance_eval do
  IsolatedClass.new.method #=> "Only exists in box"
end

# Outside box
defined?(IsolatedClass) #=> nil
IsolatedClass #=> NameError
```

### 2. Module Definitions / 모듈 정의

```ruby
box = Ruby::Box.new

box.instance_eval do
  module IsolatedModule
    def self.utility
      "Box-only utility"
    end
  end
end

# Isolated
defined?(IsolatedModule) #=> nil
```

### 3. Monkey Patches / 몽키 패치

```ruby
box = Ruby::Box.new

box.instance_eval do
  class String
    def box_method
      "Extended in box: #{self}"
    end
  end
end

# Inside box - works
box.instance_eval do
  "test".box_method #=> "Extended in box: test"
end

# Outside box - unaffected
"test".box_method #=> NoMethodError
```

### 4. Constants / 상수

```ruby
box = Ruby::Box.new

box.instance_eval do
  BOX_CONSTANT = "Isolated value"
  ANOTHER = 42
end

# Isolated
defined?(BOX_CONSTANT) #=> nil
BOX_CONSTANT #=> NameError
```

### 5. Global Variables (Box-specific) / 전역 변수

```ruby
box = Ruby::Box.new

box.instance_eval do
  $box_global = "Box-specific global"
end

# Behavior depends on implementation
# Typically isolated or shadowed
$box_global #=> nil or different behavior
```

### 6. Class Variables / 클래스 변수

```ruby
box = Ruby::Box.new

box.instance_eval do
  class Config
    @@setting = "box_value"

    def self.setting
      @@setting
    end
  end
end

# Isolated within box
box.instance_eval { Config.setting } #=> "box_value"
```

## What Is NOT Isolated / 격리되지 않는 것

### 1. Objects Passed by Reference / 참조로 전달된 객체

```ruby
external_array = [1, 2, 3]

box = Ruby::Box.new

box.instance_eval do
  # If external_array is accessible, mutations affect it
  external_array << 4  # Modifies external array
end

external_array #=> [1, 2, 3, 4]
```

### 2. Core Classes (Object, Kernel, BasicObject)

```ruby
box = Ruby::Box.new

box.instance_eval do
  # These are shared, not isolated
  Object.class        #=> Class (shared)
  Kernel.methods      #=> [...] (shared)
  BasicObject.class   #=> Class (shared)
end
```

### 3. Built-in Methods

```ruby
box = Ruby::Box.new

box.instance_eval do
  # Built-in methods work
  [1, 2, 3].map { |x| x * 2 }  #=> [2, 4, 6]
  "hello".upcase               #=> "HELLO"
end
```

### 4. File System, Network, Process

```ruby
box = Ruby::Box.new

box.instance_eval do
  # I/O is not isolated
  File.read("file.txt")      # Reads real file
  Net::HTTP.get(uri)         # Makes real request
  Process.pid                # Real process ID
end
```

## Isolation Boundaries / 격리 경계

### Creating Clean Isolation

```ruby
def create_isolated_environment
  box = Ruby::Box.new

  # Set up isolated environment
  box.instance_eval do
    # Define isolated classes
    class Environment
      def initialize
        @data = {}
      end

      def set(key, value)
        @data[key] = value
      end

      def get(key)
        @data[key]
      end
    end
  end

  box
end

# Each call creates fresh isolation
env1 = create_isolated_environment
env2 = create_isolated_environment

# Completely independent
```

### Controlled Data Exchange

```ruby
class IsolatedRunner
  def initialize
    @box = Ruby::Box.new
    @input = nil
    @output = nil
  end

  def set_input(data)
    # Deep copy to prevent reference leakage
    @input = Marshal.load(Marshal.dump(data))
  end

  def run(&block)
    @output = @box.instance_eval(&block)
    # Deep copy output
    Marshal.load(Marshal.dump(@output))
  end
end

runner = IsolatedRunner.new
runner.set_input([1, 2, 3])
result = runner.run { [4, 5, 6] }
```

## Isolation Strategies / 격리 전략

### Strategy 1: Complete Isolation

```ruby
# Maximize isolation - no external access
def fully_isolated_execution(code_string)
  box = Ruby::Box.new

  # Define allowed subset
  box.instance_eval do
    # Only allow pure computation
    # No I/O, no network, no file access
  end

  box.instance_eval(code_string)
end
```

### Strategy 2: Selective Exposure

```ruby
# Expose specific capabilities
def sandbox_with_math
  box = Ruby::Box.new

  box.instance_eval do
    # Expose Math module
    module SafeMath
      def self.sqrt(x)
        Math.sqrt(x)
      end

      def self.sin(x)
        Math.sin(x)
      end
    end
  end

  box
end

sandbox = sandbox_with_math
sandbox.instance_eval do
  SafeMath.sqrt(16) #=> 4.0
end
```

### Strategy 3: Namespace Wrapping

```ruby
# Wrap libraries in isolated namespace
def isolated_json
  box = Ruby::Box.new

  box.instance_eval do
    require 'json'

    module IsolatedJSON
      def self.parse(str)
        JSON.parse(str)
      end

      def self.generate(obj)
        JSON.generate(obj)
      end
    end
  end

  box
end
```

## Testing Isolation / 격리 테스트

### Verify Class Isolation

```ruby
def test_class_isolation
  box = Ruby::Box.new

  box.instance_eval do
    class TestClass
      VALUE = 123
    end
  end

  # Should not exist globally
  raise "Leak!" if defined?(TestClass)

  # Should exist in box
  result = box.instance_eval { TestClass::VALUE }
  raise "Not accessible in box!" unless result == 123

  puts "Class isolation: PASS"
end
```

### Verify Monkey Patch Isolation

```ruby
def test_monkey_patch_isolation
  original = "test".respond_to?(:custom_method)

  box = Ruby::Box.new
  box.instance_eval do
    class String
      def custom_method
        "modified"
      end
    end
  end

  # Global String should be unchanged
  raise "Leak!" if "test".respond_to?(:custom_method)

  # Box String should have method
  box.instance_eval do
    raise "Not working in box!" unless "test".custom_method == "modified"
  end

  puts "Monkey patch isolation: PASS"
end
```

### Verify Constant Isolation

```ruby
def test_constant_isolation
  box = Ruby::Box.new

  box.instance_eval do
    ISOLATED_CONST = "secret"
  end

  raise "Leak!" if defined?(ISOLATED_CONST)

  value = box.instance_eval { ISOLATED_CONST }
  raise "Not accessible!" unless value == "secret"

  puts "Constant isolation: PASS"
end
```

## Limitations and Caveats / 제한 사항 및 주의점

### 1. Not a Security Sandbox

```ruby
# ⚠️ Ruby::Box is NOT a security boundary
box = Ruby::Box.new

box.instance_eval do
  # These still work!
  File.delete("important.txt")     # Can delete files
  system("rm -rf /")               # Can run commands
  `curl evil.com`                  # Can make requests
end

# For security, use OS-level sandboxing
```

### 2. Memory Overhead

```ruby
# Each box has memory overhead
boxes = 100.times.map { Ruby::Box.new }
# Uses more memory than sharing namespace
```

### 3. Performance Considerations

```ruby
# Box operations have overhead
# Frequently crossing box boundaries is expensive

# ❌ Inefficient
1000.times do
  box.instance_eval { compute }
end

# ✅ Better
box.instance_eval do
  1000.times { compute }
end
```

## See Also / 참고

- [Ruby::Box Overview](INDEX.md)
- [Basic Usage](basics.md)
- [Use Cases](use-cases.md)
