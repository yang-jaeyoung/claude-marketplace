# Deprecated Features in Ruby 4.0 / 사용 중단 기능

> Features deprecated in Ruby 4.0 that will be removed in future versions.
> Ruby 4.0에서 사용 중단된 기능으로, 향후 버전에서 제거될 예정입니다.

## ObjectSpace._id2ref

### Status

Deprecated in Ruby 4.0

### What It Does

Converts an object ID back to the object reference.

### Why Deprecated

- Fragile: Objects can be garbage collected
- Security: Can access objects unexpectedly
- Performance: Interferes with GC optimizations

### Current Behavior

```ruby
obj = "hello"
id = obj.object_id

# Still works but warns
ObjectSpace._id2ref(id)
# warning: ObjectSpace._id2ref is deprecated and will be removed in Ruby 5.0
```

### Alternatives

```ruby
# Use WeakRef for weak references
require 'weakref'

obj = "hello"
weak = WeakRef.new(obj)

# Later...
weak.weakref_alive?  #=> true if not GC'd
weak.__getobj__      #=> "hello" (or raises if GC'd)
```

```ruby
# Use a registry for long-lived references
class ObjectRegistry
  def initialize
    @objects = {}
    @counter = 0
  end

  def register(obj)
    id = (@counter += 1)
    @objects[id] = obj
    id
  end

  def get(id)
    @objects[id]
  end

  def unregister(id)
    @objects.delete(id)
  end
end

registry = ObjectRegistry.new
id = registry.register("hello")
registry.get(id)  #=> "hello"
```

## Set#to_set with Arguments

### Status

Deprecated in Ruby 4.0

### Current Behavior

```ruby
set = Set[1, 2, 3]

# Deprecated: passing arguments
set.to_set(SortedSet)
# warning: passing arguments to Set#to_set is deprecated

# Still works without arguments
set.to_set  #=> same set
```

### Alternatives

```ruby
# Create new set explicitly
sorted = SortedSet.new(set)

# Or use explicit conversion
other_set_type = MyCustomSet.new(set.to_a)
```

## Enumerable#to_set with Arguments

### Status

Deprecated in Ruby 4.0

### Current Behavior

```ruby
array = [1, 2, 3]

# Deprecated: passing arguments
array.to_set(SortedSet)
# warning: passing arguments to Enumerable#to_set is deprecated

# Still works without arguments
array.to_set  #=> Set[1, 2, 3]
```

### Alternatives

```ruby
# Use explicit constructor
sorted = SortedSet.new(array)

# Or chain methods
custom_set = array.to_set.tap { |s| s.transform_to(OtherSetType) }
```

## Deprecation Timeline / 사용 중단 일정

| Feature | Deprecated | Expected Removal |
|---------|------------|------------------|
| `ObjectSpace._id2ref` | Ruby 4.0 | Ruby 5.0 |
| `Set#to_set(klass)` | Ruby 4.0 | Ruby 5.0 |
| `Enumerable#to_set(klass)` | Ruby 4.0 | Ruby 5.0 |

## Handling Deprecation Warnings / 사용 중단 경고 처리

### Show All Warnings

```bash
# Run Ruby with verbose warnings
ruby -W:deprecated script.rb

# In Rails
RUBYOPT="-W:deprecated" bin/rails server
```

### Suppress Warnings (Not Recommended)

```ruby
# Temporarily suppress
Warning.ignore(/deprecated/)

# Or for specific code
$VERBOSE = nil
# deprecated code
$VERBOSE = true
```

### Track Deprecations in Tests

```ruby
# spec/spec_helper.rb
RSpec.configure do |config|
  config.before(:suite) do
    @deprecation_warnings = []
    Warning.extend(Module.new {
      def warn(msg)
        if msg.include?('deprecated')
          @deprecation_warnings << msg
        end
        super
      end
    })
  end

  config.after(:suite) do
    if @deprecation_warnings.any?
      puts "\n\nDeprecation Warnings:"
      @deprecation_warnings.uniq.each { |w| puts "  - #{w}" }
    end
  end
end
```

## Migration Strategy / 마이그레이션 전략

### 1. Enable Deprecation Warnings

```bash
# Development
export RUBYOPT="-W:deprecated"

# CI/CD
# Add to your test command
bundle exec rspec -W:deprecated
```

### 2. Find Deprecated Usage

```bash
# Search for known deprecated patterns
grep -r "_id2ref" --include="*.rb" .
grep -r "to_set(" --include="*.rb" .
```

### 3. Update Code

```ruby
# Before
ObjectSpace._id2ref(id)

# After
# Use WeakRef or custom registry
```

### 4. Test Thoroughly

```ruby
# Ensure no deprecation warnings in test output
RSpec.configure do |config|
  config.around(:each) do |example|
    warnings = []
    Warning.instance_variable_set(:@deprecation_warnings, warnings)
    example.run
    expect(warnings).to be_empty, "Deprecation warnings: #{warnings.join(', ')}"
  end
end
```

## Rails-Specific Deprecations / Rails 관련 사용 중단

When upgrading Rails 8 apps to Ruby 4.0, also check:

### ActiveSupport Deprecations

```ruby
# These may trigger Ruby 4.0 deprecations
ActiveSupport::Deprecation.warn(...)  # Check if using deprecated Ruby features
```

### Gem Deprecations

Some gems may use deprecated Ruby features:

```bash
# Check gem source for deprecated patterns
bundle exec gem unpack some_gem
grep -r "_id2ref\|to_set(" some_gem/
```

## See Also / 참고

- [Removed Features](removed-features.md) - Already removed
- [Upgrade Guide](../overview/upgrade-guide.md) - Full upgrade process
- [What's New](../overview/whats-new.md) - New features
