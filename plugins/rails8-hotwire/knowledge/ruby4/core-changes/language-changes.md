# Ruby 4.0 Language Changes / 언어 변경사항

> Syntax and language behavior changes in Ruby 4.0.
> Ruby 4.0의 문법 및 언어 동작 변경사항.

## 1. Splat on nil / nil Splat 연산

### Change Description

In Ruby 4.0, `*nil` no longer calls `nil.to_a`.

### Before (Ruby 3.x)

```ruby
# Ruby 3.x behavior
*nil                    #=> calls nil.to_a, returns []

def method(*args)
  args
end

method(*nil)            #=> []
[1, *nil, 2]            #=> [1, 2]
```

### After (Ruby 4.0)

```ruby
# Ruby 4.0 behavior
*nil                    #=> NoMethodError: undefined method 'to_a' for nil:NilClass

def method(*args)
  args
end

method(*nil)            #=> NoMethodError
[1, *nil, 2]            #=> NoMethodError
```

### Migration

```ruby
# ❌ Code that breaks in Ruby 4.0
def combine(base, *extras)
  [*base, *extras]
end

combine([1, 2], nil)  # Error in Ruby 4.0!

# ✅ Fixed code
def combine(base, *extras)
  [*base, *extras.compact]
end

# Or explicit handling
def combine(base, extras)
  result = base.dup
  result.concat(extras) if extras
  result
end
```

## 2. Line Continuation with Logical Operators / 논리 연산자 줄 계속

### Change Description

Logical operators (`||`, `&&`, `and`, `or`) at the start of a line now continue the previous line.

### Ruby 4.0 Behavior

```ruby
# Ruby 4.0 - This works!
result = condition1
  || condition2
  && condition3

# Equivalent to:
result = condition1 || condition2 && condition3
```

### Practical Usage

```ruby
# Complex conditions are more readable
valid = user.present?
  && user.active?
  && user.verified?
  || user.admin?

# Method chaining alternative
User.where(active: true)
  .or(User.where(admin: true))
  .order(:name)
```

### Before (Ruby 3.x)

```ruby
# In Ruby 3.x, this was a syntax error or unexpected behavior
result = condition1
  || condition2   # Syntax error or new statement

# You had to use backslash or keep on same line
result = condition1 \
  || condition2

result = condition1 || condition2
```

## 3. Kernel#open Pipe Removal / Kernel#open 파이프 제거

### Change Description

`Kernel#open` no longer executes shell commands when the argument starts with `|`.

### Before (Ruby 3.x)

```ruby
# Ruby 3.x - DANGEROUS!
open("| ls -la")              # Executed as shell command!
open("| rm -rf /")            # Could delete files!

# Reading command output
output = open("| date").read  # Got current date
```

### After (Ruby 4.0)

```ruby
# Ruby 4.0 - Safe
open("| ls -la")              # Opens file literally named "| ls -la"
                               # Or raises error if no such file
```

### Migration

```ruby
# ❌ Old way (no longer works)
output = open("| ls -la").read

# ✅ New way - Use IO.popen
output = IO.popen("ls -la") { |io| io.read }

# Or
IO.popen("ls", "-la") do |io|
  puts io.read
end

# For writing
IO.popen("mail user@example.com", "w") do |io|
  io.puts "Hello!"
end

# Capture output and error
require 'open3'
stdout, stderr, status = Open3.capture3("ls", "-la")
```

### Security Note

This change improves security by preventing accidental command injection:

```ruby
# ❌ Previously dangerous
filename = params[:file]          # User input: "| rm -rf /"
content = open(filename).read     # Would execute command!

# ✅ Now safe
filename = params[:file]
content = File.read(filename)     # Just reads file
```

## 4. Unicode 17.0.0 Support / 유니코드 17.0.0 지원

Ruby 4.0 supports Unicode 17.0.0, which includes:
- New emoji characters
- Additional scripts
- Updated character properties

```ruby
# New emoji in Unicode 17.0.0
"🫩".length  #=> 1
"🫩".bytes   #=> [240, 159, 171, 169]

# Character properties
"a".match?(/\p{Latin}/)       #=> true
"あ".match?(/\p{Hiragana}/)   #=> true
```

## 5. Math Module Additions / Math 모듈 추가

### Math.log1p

Computes `log(1 + x)` with better precision for small x:

```ruby
# For very small x, log1p is more accurate
x = 0.0000001

Math.log(1 + x)    #=> 9.999999505838704e-08 (less accurate)
Math.log1p(x)      #=> 9.9999995e-08 (more accurate)
```

### Math.expm1

Computes `exp(x) - 1` with better precision for small x:

```ruby
x = 0.0000001

Math.exp(x) - 1    #=> 1.0000000116860974e-07 (less accurate)
Math.expm1(x)      #=> 1.0000000050000001e-07 (more accurate)
```

## 6. Array#rfind / Array#rfind 추가

Find element from the right (reverse):

```ruby
arr = [1, 2, 3, 2, 1]

arr.find { |x| x == 2 }   #=> 2 (found at index 1)
arr.rfind { |x| x == 2 }  #=> 2 (found at index 3)

# Practical usage
log_entries = ["INFO: start", "ERROR: fail", "INFO: retry", "ERROR: timeout"]

# Find last error
log_entries.rfind { |e| e.start_with?("ERROR") }
#=> "ERROR: timeout"
```

## 7. String Strip Methods Enhancement / String Strip 메서드 개선

New `selectors` argument for strip methods:

```ruby
str = "  hello world  "

# Traditional
str.strip   #=> "hello world"
str.lstrip  #=> "hello world  "
str.rstrip  #=> "  hello world"

# Ruby 4.0 - with selectors
str.strip(selectors: [:left])   #=> "hello world  "  (same as lstrip)
str.strip(selectors: [:right])  #=> "  hello world"  (same as rstrip)
str.strip(selectors: :both)     #=> "hello world"    (default)

# Custom characters (existing feature, enhanced)
"###hello###".strip(selectors: :both, chars: "#")  #=> "hello"
```

## 8. ArgumentError Improvements / ArgumentError 개선

Error messages now include the class/module name:

### Before (Ruby 3.x)

```ruby
def greet(name:)
  puts "Hello, #{name}"
end

greet()
# ArgumentError: missing keyword: name
```

### After (Ruby 4.0)

```ruby
def greet(name:)
  puts "Hello, #{name}"
end

greet()
# ArgumentError: missing keyword: name (Object#greet)
#                                        ^^^^^^^^^^^^
```

This makes debugging easier by showing where the method is defined.

## 9. Object#inspect Customization / Object#inspect 커스터마이징

Enhanced control over inspect output:

```ruby
class User
  attr_accessor :id, :name, :password

  def inspect
    "#<User id=#{id} name=#{name.inspect}>"
    # Note: password is intentionally excluded
  end
end

user = User.new
user.id = 1
user.name = "Alice"
user.password = "secret"

puts user.inspect
#=> #<User id=1 name="Alice">
```

## Migration Checklist / 마이그레이션 체크리스트

| Change | Action Required |
|--------|-----------------|
| `*nil` | Check for nil splats, add explicit handling |
| Line continuation | No action (new feature) |
| `Kernel#open(\|)` | Replace with `IO.popen` |
| Unicode 17.0.0 | No action (enhancement) |
| Math.log1p/expm1 | No action (new methods) |
| Array#rfind | No action (new method) |
| String strip | No action (enhancement) |
| ArgumentError | No action (improvement) |

## See Also / 참고

- [Set and Pathname](set-pathname.md)
- [Ruby Module](ruby-module.md)
- [Removed Features](../breaking-changes/removed-features.md)
- [What's New in Ruby 4.0](../overview/whats-new.md)
