# Removed Features in Ruby 4.0 / 제거된 기능

> Features that have been removed in Ruby 4.0 and their replacements.
> Ruby 4.0에서 제거된 기능과 대체 방안.

## Ractor API Removals / Ractor API 제거

### Ractor.yield

**Status:** Removed

**Before (Ruby 3.x):**
```ruby
r = Ractor.new do
  Ractor.yield 42
end
value = r.take
```

**After (Ruby 4.0):**
```ruby
port = Ractor::Port.new
r = Ractor.new(port) do |p|
  p << 42
end
value = port.receive
```

### Ractor#take

**Status:** Removed

**Before (Ruby 3.x):**
```ruby
r = Ractor.new { "result" }
value = r.take
```

**After (Ruby 4.0):**
```ruby
port = Ractor::Port.new
r = Ractor.new(port) do |p|
  p << "result"
end
value = port.receive
```

### Ractor#close_incoming

**Status:** Removed

**Before (Ruby 3.x):**
```ruby
r = Ractor.new do
  while msg = Ractor.receive
    process(msg)
  end
end
r.close_incoming  # Signal no more input
```

**After (Ruby 4.0):**
```ruby
port = Ractor::Port.new
r = Ractor.new(port) do |p|
  loop do
    msg = Ractor.receive
    break if msg == :done  # Use sentinel value
    p << process(msg)
  end
end
r.send(:done)  # Send sentinel to signal completion
```

### Ractor#close_outgoing

**Status:** Removed

**Before (Ruby 3.x):**
```ruby
r = Ractor.new do
  Ractor.yield 1
  Ractor.yield 2
  # Outgoing automatically closed when Ractor ends
end
r.close_outgoing  # Manually close
```

**After (Ruby 4.0):**
Use Ractor::Port for all communication. Ports don't need explicit closing.

## Process::Status Method Removals / Process::Status 메서드 제거

### Process::Status#& (Bitwise AND)

**Status:** Removed (deprecated since Ruby 3.3)

**Before (Ruby 3.x):**
```ruby
status = $?
low_bits = status & 0xFF
```

**After (Ruby 4.0):**
```ruby
status = $?
# Use specific methods instead
status.exitstatus   # Get exit status
status.termsig      # Get termination signal
status.stopsig      # Get stop signal
```

### Process::Status#>> (Bitwise Right Shift)

**Status:** Removed (deprecated since Ruby 3.3)

**Before (Ruby 3.x):**
```ruby
status = $?
exit_code = status >> 8
```

**After (Ruby 4.0):**
```ruby
status = $?
exit_code = status.exitstatus
```

## Kernel#open Pipe Behavior / Kernel#open 파이프 동작

### Pipe Command Execution

**Status:** Removed

**Before (Ruby 3.x):**
```ruby
# Executed shell command
output = open("| ls -la").read
data = open("| cat file.txt").read
```

**After (Ruby 4.0):**
```ruby
# Use IO.popen
output = IO.popen("ls -la") { |io| io.read }
output = IO.popen(["ls", "-la"]) { |io| io.read }

# Or use backticks/system
output = `ls -la`

# For more control
require 'open3'
stdout, stderr, status = Open3.capture3("ls", "-la")
```

## Migration Script / 마이그레이션 스크립트

Use this script to find deprecated patterns in your codebase:

```ruby
#!/usr/bin/env ruby
# find_deprecated_ruby4.rb

require 'find'

PATTERNS = {
  'Ractor.yield' => 'Use Ractor::Port instead',
  '.take' => 'Use Ractor::Port#receive instead (if Ractor context)',
  'close_incoming' => 'Use sentinel values instead',
  'close_outgoing' => 'Use Ractor::Port instead',
  'open("|' => 'Use IO.popen instead',
  "open('|" => 'Use IO.popen instead',
  '>> 8' => 'Use Process::Status#exitstatus if for process status',
  '& 0x' => 'Check if used with Process::Status'
}

def scan_file(file)
  content = File.read(file)
  issues = []

  PATTERNS.each do |pattern, message|
    if content.include?(pattern)
      # Find line numbers
      content.each_line.with_index(1) do |line, num|
        if line.include?(pattern)
          issues << { line: num, pattern: pattern, message: message }
        end
      end
    end
  end

  issues
end

def scan_directory(dir)
  Find.find(dir) do |path|
    next unless path.end_with?('.rb')
    next if path.include?('vendor')
    next if path.include?('node_modules')

    issues = scan_file(path)
    if issues.any?
      puts "\n#{path}:"
      issues.each do |issue|
        puts "  Line #{issue[:line]}: '#{issue[:pattern]}' - #{issue[:message]}"
      end
    end
  end
end

if ARGV.empty?
  puts "Usage: ruby find_deprecated_ruby4.rb <directory>"
  exit 1
end

scan_directory(ARGV[0])
```

## Quick Reference Table / 빠른 참조 표

| Removed | Replacement | Ruby Version Deprecated |
|---------|-------------|------------------------|
| `Ractor.yield` | `Ractor::Port#<<` | 4.0 |
| `Ractor#take` | `Ractor::Port#receive` | 4.0 |
| `Ractor#close_incoming` | Sentinel values | 4.0 |
| `Ractor#close_outgoing` | N/A (use Port) | 4.0 |
| `Process::Status#&` | `#exitstatus/#termsig` | 3.3 |
| `Process::Status#>>` | `#exitstatus` | 3.3 |
| `Kernel#open("\|")` | `IO.popen` | 4.0 |

## Testing After Migration / 마이그레이션 후 테스트

```ruby
# spec/ruby4_compatibility_spec.rb

RSpec.describe "Ruby 4.0 Compatibility" do
  describe "Ractor" do
    it "uses Ractor::Port for communication" do
      port = Ractor::Port.new
      r = Ractor.new(port) { |p| p << 42 }
      expect(port.receive).to eq(42)
    end
  end

  describe "Process status" do
    it "uses exitstatus method" do
      system("true")
      expect($?.exitstatus).to eq(0)

      system("false")
      expect($?.exitstatus).to eq(1)
    end
  end

  describe "IO.popen" do
    it "executes commands safely" do
      output = IO.popen(["echo", "hello"]) { |io| io.read.strip }
      expect(output).to eq("hello")
    end
  end
end
```

## See Also / 참고

- [Deprecations](deprecations.md) - Deprecated but not yet removed
- [Ractor Migration](../ractor/migration.md) - Complete Ractor migration guide
- [Upgrade Guide](../overview/upgrade-guide.md) - Full upgrade process
