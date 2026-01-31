# What's New in Ruby 4.0 / Ruby 4.0 새로운 기능

> Released: December 25, 2025 (Ruby's 30th Anniversary)
> 릴리즈: 2025년 12월 25일 (Ruby 30주년 기념)

## Major Features / 주요 기능

### 1. ZJIT (Zero-overhead JIT Compiler)

A new JIT compiler developed by Shopify's YJIT team.

**Key Characteristics:**
- SSA IR (Static Single Assignment Intermediate Representation) based
- Supports larger compilation units than YJIT
- Currently faster than interpreter, but slower than YJIT
- Experimental status - not recommended for production

```ruby
# Activate ZJIT
RubyVM::ZJIT.enable

# Check if enabled
RubyVM::ZJIT.enabled? #=> true
```

**Build Requirements:** Rust 1.85.0 or later

### 2. Ruby::Box (Namespace Isolation)

An experimental feature for isolating library code within a process.

**Activation:**
```bash
RUBY_BOX=1 ruby your_app.rb
```

**Usage:**
```ruby
box = Ruby::Box.new
box.require("some_library")
# Library's definitions are isolated within the box
```

**What Gets Isolated:**
- Monkey patches
- Global variables
- Class variables
- Module/Class definitions

### 3. Ractor::Port (Improved Concurrency)

New synchronization mechanism for Ractors.

```ruby
port1 = Ractor::Port.new
port2 = Ractor::Port.new

Ractor.new(port1, port2) do |p1, p2|
  p1 << "first message"
  p2 << "second message"
end

port1.receive #=> "first message"
port2.receive #=> "second message"
```

**Removed Methods:**
- `Ractor.yield` → Use `Ractor::Port`
- `Ractor#take` → Use `Ractor::Port#receive`
- `Ractor#close_incoming`
- `Ractor#close_outgoing`

**New Methods:**
- `Ractor.shareable_proc`
- `Ractor.shareable_lambda`

### 4. Core Class Promotions

**Set (No longer requires `require 'set'`):**
```ruby
# Before Ruby 4.0
require 'set'
set = Set.new([1, 2, 3])

# Ruby 4.0+
set = Set[1, 2, 3]
```

**Pathname (No longer requires `require 'pathname'`):**
```ruby
# Before Ruby 4.0
require 'pathname'
path = Pathname.new("/usr/local")

# Ruby 4.0+
path = Pathname("/usr/local")
```

**New Ruby Module:**
```ruby
Ruby::VERSION      #=> "4.0.0"
Ruby::RELEASE_DATE #=> "2025-12-25"
Ruby::PLATFORM     #=> "x86_64-darwin24"
```

## Language Changes / 언어 변경사항

### 1. Splat on nil

```ruby
# Before Ruby 4.0
*nil #=> calls nil.to_a, returns []

# Ruby 4.0+
*nil #=> raises NoMethodError (no longer calls to_a)
```

### 2. Line Continuation with Logical Operators

```ruby
# Ruby 4.0+ allows this
result = condition1
  || condition2
  && condition3

# Logical operators at line start continue previous line
```

### 3. Kernel#open Pipe Removal

```ruby
# Before Ruby 4.0
open("| ls -la")  # Executed as shell command

# Ruby 4.0+ - This no longer works
# Use IO.popen instead:
IO.popen("ls -la") { |io| puts io.read }
```

### 4. Unicode 17.0.0 Support

Full support for Unicode 17.0.0 standard.

## Standard Library Changes / 표준 라이브러리 변경

### Math Module Additions

```ruby
# New methods for numerical precision
Math.log1p(0.0001)  #=> More accurate than Math.log(1 + 0.0001)
Math.expm1(0.0001)  #=> More accurate than Math.exp(0.0001) - 1
```

### Array#rfind

```ruby
# Find from right (reverse find)
[1, 2, 3, 2, 1].rfind { |x| x == 2 }  #=> 2 (found at index 3)
```

### String Strip Methods

```ruby
# New selectors argument
"  hello  ".strip(selectors: [:left])   #=> "hello  "
"  hello  ".strip(selectors: [:right])  #=> "  hello"
"  hello  ".strip(selectors: :both)     #=> "hello" (default)
```

### Object#inspect Customization

```ruby
class User
  def inspect
    "#<User id=#{id} name=#{name.inspect}>"
  end
end
```

## Error Message Improvements / 오류 메시지 개선

### ArgumentError Now Includes Class/Module Name

```ruby
# Ruby 4.0+ error messages include more context
def greet(name:)
  puts "Hello, #{name}"
end

greet()
# ArgumentError: missing keyword: name (Kernel#greet)
#                                       ^^^^^^^^^^^^
```

## Summary Table / 요약 표

| Feature | Status | Category |
|---------|--------|----------|
| ZJIT | Experimental | Performance |
| Ruby::Box | Experimental | Isolation |
| Ractor::Port | Stable | Concurrency |
| Set (core) | Stable | Core Classes |
| Pathname (core) | Stable | Core Classes |
| Ruby module | Stable | Core Module |
| Math.log1p/expm1 | Stable | Math |
| Array#rfind | Stable | Arrays |
| Unicode 17.0.0 | Stable | Encoding |

## See Also / 참고

- [Upgrade Guide](upgrade-guide.md) - Migration from Ruby 3.x
- [Rails Compatibility](compatibility.md) - Rails version requirements
- [ZJIT Setup](../zjit/setup.md) - Detailed ZJIT configuration
- [Ruby::Box Basics](../ruby-box/basics.md) - Isolation patterns
