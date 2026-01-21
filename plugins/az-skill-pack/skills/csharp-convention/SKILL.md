---
name: csharp-convention
description: C# 코드 작성 시 Microsoft 공식 컨벤션을 적용합니다. C# 코드 리뷰, 새 코드 작성, 리팩토링, .cs 파일 작업 시 자동으로 활성화됩니다.
---

# C# Coding Conventions

Microsoft 공식 C# Coding Conventions 기반 가이드입니다.

## Naming

| 대상 | 스타일 | 예시 |
|------|--------|------|
| 클래스/메서드/프로퍼티 | PascalCase | `CustomerService`, `GetById` |
| 지역변수/파라미터 | camelCase | `orderId`, `customerName` |
| private 필드 | _camelCase | `_repository`, `_logger` |
| 인터페이스 | `I` 접두사 | `IRepository` |
| 제네릭 | `T` 접두사 | `TKey`, `TValue` |
| 비동기 메서드 | `Async` 접미사 | `GetDataAsync` |

❌ 헝가리안 표기법: `strName`, `intCount`
❌ 과도한 약어: `GetWin` → ✅ `GetWindow`

## Code Style

- **들여쓰기**: 4 스페이스
- **한 줄**: 120자 권장
- **중괄호**: Allman Style (새 줄)
- **var**: 타입이 명확할 때만

```csharp
public class CustomerService
{
    private readonly IRepository _repo;

    public async Task<Customer?> GetAsync(int id)
    {
        var customer = await _repo.FindAsync(id);
        return customer;
    }
}
```

## null 처리

```csharp
var name = customer?.Name ?? "Unknown";  // null 조건 연산자
if (customer is null) throw new ArgumentNullException(nameof(customer));
```

## 파일 구조

**멤버 순서**: 상수 → 정적 필드 → 필드 → 생성자 → 프로퍼티 → 메서드 → 중첩 타입

**접근 제한자**: `public` → `internal` → `protected internal` → `protected` → `private protected` → `private`

## SOLID 원칙

| 원칙 | 핵심 |
|------|------|
| S - Single Responsibility | 하나의 책임 |
| O - Open/Closed | 확장 열림, 수정 닫힘 |
| L - Liskov Substitution | 하위 타입 대체 가능 |
| I - Interface Segregation | 클라이언트별 인터페이스 |
| D - Dependency Inversion | 추상화에 의존 |

## XML 문서 주석

```csharp
/// <summary>고객 정보 조회</summary>
/// <param name="id">고객 ID</param>
public async Task<Customer?> GetAsync(int id)
```

**참고**: [Microsoft C# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
