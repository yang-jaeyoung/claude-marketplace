# Set and Pathname: Core Class Promotions / 코어 클래스 승격

> In Ruby 4.0, Set and Pathname are promoted to core classes.
> Ruby 4.0에서 Set과 Pathname이 코어 클래스로 승격되었습니다.

## Overview / 개요

Previously, `Set` and `Pathname` required explicit `require` statements. In Ruby 4.0, they are available immediately without any require.

## Set / 셋

### Before Ruby 4.0

```ruby
# Required require statement
require 'set'

set = Set.new([1, 2, 3])
```

### Ruby 4.0+

```ruby
# No require needed!
set = Set[1, 2, 3]
```

### Set Usage / Set 사용법

```ruby
# Creating Sets
set1 = Set[1, 2, 3]
set2 = Set.new([4, 5, 6])
set3 = Set.new  # Empty set

# Adding elements
set1 << 4
set1.add(5)

# Removing elements
set1.delete(1)

# Set operations
set1 | set2  # Union
set1 & set2  # Intersection
set1 - set2  # Difference
set1 ^ set2  # Symmetric difference

# Checking membership
set1.include?(2)  #=> true
set1.member?(2)   #=> true

# Iteration
set1.each { |item| puts item }
set1.map { |item| item * 2 }  #=> Array

# Size
set1.size
set1.length
set1.empty?
```

### Set vs Array / Set과 Array 비교

| Operation | Array | Set | When to Use Set |
|-----------|-------|-----|-----------------|
| Add | O(1)* | O(1) | Unique elements needed |
| Include? | O(n) | O(1) | Frequent membership checks |
| Delete | O(n) | O(1) | Frequent deletions |
| Order | Preserved | Not guaranteed | Order doesn't matter |

```ruby
# Performance comparison
require 'benchmark'

arr = (1..10000).to_a
set = Set.new(arr)

Benchmark.bm do |x|
  x.report("Array include?") { 1000.times { arr.include?(5000) } }
  x.report("Set include?")   { 1000.times { set.include?(5000) } }
end
# Set is significantly faster for include? checks
```

### Rails Usage / Rails에서의 사용

```ruby
# In models
class User < ApplicationRecord
  VALID_ROLES = Set['admin', 'editor', 'viewer'].freeze

  validates :role, inclusion: { in: VALID_ROLES }
end

# In controllers
class ArticlesController < ApplicationController
  ALLOWED_PARAMS = Set[:title, :body, :published].freeze

  def article_params
    params.require(:article).permit(*ALLOWED_PARAMS)
  end
end
```

## Pathname / 패스네임

### Before Ruby 4.0

```ruby
# Required require statement
require 'pathname'

path = Pathname.new('/usr/local/bin')
```

### Ruby 4.0+

```ruby
# No require needed!
path = Pathname('/usr/local/bin')

# Or using Kernel method
path = Pathname.new('/usr/local/bin')
```

### Pathname Usage / Pathname 사용법

```ruby
# Creating Pathnames
path = Pathname('/home/user/documents')

# Path components
path.basename     #=> #<Pathname:documents>
path.dirname      #=> #<Pathname:/home/user>
path.extname      #=> "" (or ".txt" for file.txt)

# Path manipulation
path / 'file.txt'           #=> #<Pathname:/home/user/documents/file.txt>
path.join('sub', 'file.txt') #=> #<Pathname:/home/user/documents/sub/file.txt>
path.parent                  #=> #<Pathname:/home/user>

# Path queries
path.exist?       #=> true/false
path.directory?   #=> true/false
path.file?        #=> true/false
path.absolute?    #=> true/false
path.relative?    #=> true/false

# File operations
path.read          # Read file contents
path.write('data') # Write to file
path.readlines     # Read as array of lines
path.each_line { } # Iterate lines

# Directory operations
path.children      # Array of child Pathnames
path.entries       # Array including . and ..
path.glob('*.rb')  # Find matching files

# Expansion
path.expand_path   # Expand ~ and resolve .
path.realpath      # Resolve symlinks
```

### Pathname in Rails / Rails에서의 Pathname

```ruby
# Application paths
Rails.root                    #=> #<Pathname:/app>
Rails.root.join('config')     #=> #<Pathname:/app/config>

# In initializers
config_path = Rails.root / 'config' / 'settings.yml'
if config_path.exist?
  YAML.load_file(config_path)
end

# In services
class FileProcessor
  def initialize(base_path)
    @base = Pathname(base_path)
  end

  def process_all
    @base.glob('**/*.csv').each do |file|
      process_file(file)
    end
  end

  def process_file(path)
    path.each_line do |line|
      # Process line
    end
  end
end
```

### String vs Pathname / String과 Pathname 비교

```ruby
# String path manipulation (error-prone)
path = '/home/user'
full = path + '/documents/file.txt'  # Works but...
full = path + 'documents'             # Missing /!

# Pathname (safer)
path = Pathname('/home/user')
full = path / 'documents' / 'file.txt'  # Always correct
```

## Backward Compatibility / 하위 호환성

The `require` statements still work in Ruby 4.0:

```ruby
# These still work (for backward compatibility)
require 'set'       # No error, just no-op
require 'pathname'  # No error, just no-op

# Your existing code continues to work
```

## Migration Notes / 마이그레이션 노트

### Removing Unnecessary Requires

You can optionally remove `require 'set'` and `require 'pathname'` from your codebase:

```bash
# Find files with these requires
grep -r "require 'set'" .
grep -r "require 'pathname'" .
```

However, keeping them doesn't cause any issues and maintains backward compatibility with Ruby 3.x.

### Gemfile Considerations

If you have gems that depend on Set or Pathname, they will work correctly in Ruby 4.0 regardless of whether they have require statements.

## See Also / 참고

- [Ruby Module](ruby-module.md)
- [Language Changes](language-changes.md)
- [What's New in Ruby 4.0](../overview/whats-new.md)
