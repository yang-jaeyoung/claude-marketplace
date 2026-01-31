# ZJIT: Next-Generation JIT Compiler

> ZJIT is a new experimental JIT compiler for Ruby 4.0, developed by Shopify's YJIT team.
> ZJIT는 Shopify의 YJIT 팀이 개발한 Ruby 4.0의 새로운 실험적 JIT 컴파일러입니다.

## Overview / 개요

ZJIT (Zero-overhead JIT) is a next-generation just-in-time compiler for Ruby that aims to provide better performance through advanced compilation techniques.

### Key Characteristics / 주요 특징

| Feature | Description |
|---------|-------------|
| SSA IR | Static Single Assignment Intermediate Representation |
| Larger Units | Compiles larger code units than YJIT |
| Rust-based | Requires Rust 1.85.0+ for building |
| Experimental | Not recommended for production use |

### Current Status / 현재 상태

```
Performance:     Faster than interpreter
                 Currently slower than YJIT
                 Expected to surpass YJIT in future versions

Stability:       Experimental
                 Active development
                 APIs may change

Recommendation:  Development and testing only
                 Not for production deployment
```

## Quick Start / 빠른 시작

### Enable ZJIT at Runtime

```ruby
# In your application code
RubyVM::ZJIT.enable

# Check status
RubyVM::ZJIT.enabled?  #=> true
```

### Enable via Command Line

```bash
ruby --zjit your_app.rb
```

### Enable via Environment Variable

```bash
RUBY_ZJIT_ENABLE=1 ruby your_app.rb
```

## In This Section / 이 섹션의 내용

| Document | Description |
|----------|-------------|
| [Setup](setup.md) | Detailed activation methods and configuration |
| [Performance](performance.md) | Benchmarks and optimization tips |
| [Rails Integration](rails-integration.md) | Using ZJIT with Rails 8 |

## ZJIT vs YJIT / ZJIT와 YJIT 비교

| Aspect | YJIT | ZJIT |
|--------|------|------|
| Status | Production-ready | Experimental |
| IR Type | Linear | SSA (Static Single Assignment) |
| Compilation Unit | Method-level | Larger units |
| Memory Usage | Lower | Higher |
| Current Speed | Faster | Slower (but improving) |
| Future Potential | Mature | Higher ceiling |

## When to Consider ZJIT / ZJIT 사용 시점

### Good Use Cases ✅

- Performance testing and benchmarking
- Experimentation in development
- Contributing to Ruby development
- Research and learning

### Not Recommended ❌

- Production deployments
- Mission-critical applications
- Applications requiring stability
- When YJIT is sufficient

## Requirements / 요구사항

### Build Requirements

| Requirement | Version |
|-------------|---------|
| Rust | 1.85.0 or later |
| Ruby | 4.0.0 or later |

### Installing Rust

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Update to latest version
rustup update

# Verify version
rustc --version
```

## See Also / 참고

- [Setup Guide](setup.md) - Detailed configuration
- [Performance Benchmarks](performance.md) - Speed comparisons
- [Rails Integration](rails-integration.md) - Rails-specific setup
- [What's New in Ruby 4.0](../overview/whats-new.md) - Full feature list
