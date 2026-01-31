# Ruby::Box Basics / 기본 사용법

> Getting started with Ruby::Box for namespace isolation.
> 네임스페이스 격리를 위한 Ruby::Box 시작하기.

## Enabling Ruby::Box / Ruby::Box 활성화

Ruby::Box is disabled by default and must be enabled via environment variable:

```bash
# Enable Ruby::Box
export RUBY_BOX=1

# Or for a single command
RUBY_BOX=1 ruby your_script.rb
```

### Checking Availability

```ruby
# Check if Ruby::Box is enabled
if defined?(Ruby::Box)
  puts "Ruby::Box is available"
else
  puts "Ruby::Box is not enabled (set RUBY_BOX=1)"
end
```

## Creating a Box / Box 생성

### Basic Creation

```ruby
# Create a new isolated box
box = Ruby::Box.new

# Box is empty - no code loaded yet
```

### Loading Code into a Box

```ruby
box = Ruby::Box.new

# Load a file
box.require("./my_library")

# Load a gem (if isolated gems are supported)
box.require("some_gem")
```

## Executing Code in a Box / Box 내에서 코드 실행

### Using instance_eval

```ruby
box = Ruby::Box.new

# Define code in the box
box.instance_eval do
  class MyClass
    def greet
      "Hello from box!"
    end
  end

  MY_CONSTANT = "isolated value"
end

# Access from box
box.instance_eval do
  MyClass.new.greet  #=> "Hello from box!"
  MY_CONSTANT        #=> "isolated value"
end

# Global namespace is unaffected
defined?(MyClass)     #=> nil
defined?(MY_CONSTANT) #=> nil
```

### Using Blocks

```ruby
box = Ruby::Box.new

result = box.instance_eval do
  x = 10
  y = 20
  x + y
end

puts result #=> 30
```

## Data Exchange Between Box and Outside / Box와 외부 간 데이터 교환

### Passing Data In

```ruby
box = Ruby::Box.new
external_data = [1, 2, 3]

box.instance_eval do
  # Access external variables via binding
  # Note: Exact API may vary - this is conceptual
end

# Alternative: Use method parameters
box.define_method(:process) do |data|
  data.map { |x| x * 2 }
end

box.process(external_data) #=> [2, 4, 6]
```

### Getting Data Out

```ruby
box = Ruby::Box.new

# Execute and get return value
result = box.instance_eval do
  calculation = (1..10).sum
  calculation
end

puts result #=> 55
```

## Working with Classes / 클래스 작업

### Defining Classes in a Box

```ruby
box = Ruby::Box.new

box.instance_eval do
  class User
    attr_accessor :name

    def initialize(name)
      @name = name
    end

    def greet
      "Hello, #{@name}!"
    end
  end
end

# Create instance within box
user = box.instance_eval do
  User.new("Alice")
end

# Use the instance
puts user.greet #=> "Hello, Alice!"
```

### Extending Core Classes (Isolated)

```ruby
box = Ruby::Box.new

box.instance_eval do
  # This String extension only exists in the box
  class String
    def excited
      "#{self}!"
    end
  end
end

# Inside box
box.instance_eval do
  "Hello".excited #=> "Hello!"
end

# Outside box - not affected
"Hello".excited #=> NoMethodError
```

## Working with Modules / 모듈 작업

```ruby
box = Ruby::Box.new

box.instance_eval do
  module Helpers
    def self.format_name(first, last)
      "#{last}, #{first}"
    end
  end
end

# Use from box
result = box.instance_eval do
  Helpers.format_name("John", "Doe")
end

puts result #=> "Doe, John"
```

## Global Variables / 전역 변수

```ruby
# Set global variable outside box
$outside_var = "external"

box = Ruby::Box.new

box.instance_eval do
  # Create global variable in box
  $box_var = "internal"

  # Access external global (behavior may vary)
  puts $outside_var  # Depends on isolation level
end

# Box's global variable is isolated
defined?($box_var)  #=> nil (in global namespace)
```

## Constants / 상수

```ruby
# External constant
EXTERNAL_CONST = "outside"

box = Ruby::Box.new

box.instance_eval do
  BOX_CONST = "inside"

  # External constants may or may not be visible
  # depending on isolation implementation
end

# Box constant is isolated
defined?(BOX_CONST)  #=> nil (in global namespace)
EXTERNAL_CONST       #=> "outside" (unaffected)
```

## Error Handling / 오류 처리

```ruby
box = Ruby::Box.new

begin
  box.instance_eval do
    raise "Error inside box"
  end
rescue => e
  puts "Caught: #{e.message}"
  # Errors propagate out of the box
end
```

## Multiple Boxes / 여러 Box 사용

```ruby
box1 = Ruby::Box.new
box2 = Ruby::Box.new

# Each box is independent
box1.instance_eval do
  VALUE = 1
end

box2.instance_eval do
  VALUE = 2
end

box1.instance_eval { VALUE } #=> 1
box2.instance_eval { VALUE } #=> 2

# No global pollution
defined?(VALUE) #=> nil
```

## Debugging Tips / 디버깅 팁

### Inspecting Box Contents

```ruby
box = Ruby::Box.new

box.instance_eval do
  class TestClass; end
  TEST_VAR = 123
end

# Check what's defined (conceptual API)
box.constants rescue nil
box.methods rescue nil
```

### Logging Box Activity

```ruby
class DebugBox
  def initialize
    @box = Ruby::Box.new
    @log = []
  end

  def execute(&block)
    @log << "Executing at #{Time.now}"
    @box.instance_eval(&block)
  end

  def log
    @log
  end
end

db = DebugBox.new
db.execute { 1 + 1 }
puts db.log
```

## Common Pitfalls / 자주 하는 실수

### 1. Forgetting to Enable Ruby::Box

```ruby
# ❌ Ruby::Box not enabled
box = Ruby::Box.new #=> NameError: uninitialized constant Ruby::Box

# ✅ Enable first
# RUBY_BOX=1 ruby script.rb
```

### 2. Expecting Full Isolation

```ruby
# ⚠️ Some things may still leak through
# depending on implementation details
box = Ruby::Box.new
box.instance_eval do
  # Object, Kernel, BasicObject are likely shared
  Object.class #=> Class
end
```

### 3. Performance Overhead

```ruby
# ⚠️ Creating many boxes has overhead
1000.times do
  box = Ruby::Box.new  # Not efficient
  box.instance_eval { 1 + 1 }
end

# ✅ Reuse boxes when possible
box = Ruby::Box.new
1000.times do
  box.instance_eval { 1 + 1 }  # Better
end
```

## See Also / 참고

- [Ruby::Box Overview](INDEX.md)
- [Isolation Patterns](isolation.md)
- [Use Cases](use-cases.md)
