---
name: csharp-convention
description: C# 코드 작성 시 Microsoft 공식 컨벤션을 적용합니다. C# 코드 리뷰, 새 코드 작성, 리팩토링, .cs 파일 작업 시 자동으로 활성화됩니다.
---

# C# Coding Conventions

Microsoft 공식 C# Coding Conventions 기반의 코드 스타일 가이드입니다.

## 네이밍 컨벤션

### PascalCase 사용
- 클래스, 구조체, 레코드: `CustomerOrder`, `PaymentService`
- 메서드: `GetCustomerById`, `CalculateTotal`
- 프로퍼티: `FirstName`, `IsEnabled`
- 이벤트: `OrderCompleted`, `PropertyChanged`
- 네임스페이스: `MyCompany.Product.Module`
- 열거형 및 열거형 값: `OrderStatus`, `OrderStatus.Pending`
- 상수: `MaxRetryCount`, `DefaultTimeout`

### camelCase 사용
- 지역 변수: `customerName`, `totalAmount`
- 메서드 파라미터: `orderId`, `isActive`

### _camelCase 사용 (언더스코어 접두사)
- private 필드: `_customerRepository`, `_logger`
- private static 필드: `_instance`, `_connectionString`

### 접두사/접미사 규칙
- 인터페이스: `I` 접두사 (`IRepository`, `ILogger`, `IDisposable`)
- 제네릭 타입 파라미터: `T` 접두사 (`TKey`, `TValue`, `TEntity`)
- 비동기 메서드: `Async` 접미사 (`GetDataAsync`, `SaveChangesAsync`)
- Attribute 클래스: `Attribute` 접미사 (`ValidateAttribute`)
- Exception 클래스: `Exception` 접미사 (`NotFoundException`)

### 피해야 할 패턴
- 헝가리안 표기법 사용 금지: ~~`strName`~~, ~~`intCount`~~
- 약어 사용 최소화: `GetWindow` (O), ~~`GetWin`~~ (X)
- 단일 문자 변수명 지양 (루프 인덱스 `i`, `j`, `k` 제외)

## 코드 스타일

### 들여쓰기 및 공백
- 들여쓰기: 4 스페이스 (탭 사용 금지)
- 한 줄 최대 길이: 120자 권장
- 연산자 앞뒤 공백: `x = y + z`
- 콤마 뒤 공백: `Method(a, b, c)`
- 괄호 내부 공백 없음: `Method(param)` (O), ~~`Method( param )`~~ (X)

### 중괄호 스타일 (Allman Style)
```csharp
// 올바른 예
public class CustomerService
{
    public void ProcessOrder(Order order)
    {
        if (order.IsValid)
        {
            // 처리 로직
        }
    }
}
```

### var 사용 규칙
```csharp
// 타입이 명확한 경우 var 사용
var customer = new Customer();
var orders = GetOrders();

// 타입이 명확하지 않은 경우 명시적 타입 선언
int count = GetCount();
string message = ProcessResult();
```

### using 문
```csharp
// 파일 상단에 정리, 알파벳 순
using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Extensions.Logging;

// 또는 파일 범위 네임스페이스 사용 (C# 10+)
namespace MyApp.Services;
```

### null 처리
```csharp
// null 조건 연산자 사용
var name = customer?.Name ?? "Unknown";

// null 체크 시 is null 패턴 사용
if (customer is null)
{
    throw new ArgumentNullException(nameof(customer));
}

// nullable reference types 활용 (C# 8+)
public string? GetOptionalValue() { }
```

## 아키텍처 패턴

### SOLID 원칙
1. **Single Responsibility**: 클래스는 하나의 책임만 가짐
2. **Open/Closed**: 확장에 열려있고 수정에 닫혀있음
3. **Liskov Substitution**: 하위 타입은 상위 타입을 대체 가능
4. **Interface Segregation**: 클라이언트별 인터페이스 분리
5. **Dependency Inversion**: 추상화에 의존

### 의존성 주입
```csharp
public class OrderService
{
    private readonly IOrderRepository _orderRepository;
    private readonly ILogger<OrderService> _logger;

    public OrderService(
        IOrderRepository orderRepository,
        ILogger<OrderService> logger)
    {
        _orderRepository = orderRepository;
        _logger = logger;
    }
}
```

### 인터페이스 기반 설계
```csharp
// 인터페이스 정의
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(int id);
    Task<IEnumerable<Order>> GetAllAsync();
    Task AddAsync(Order order);
}

// 구현
public class SqlOrderRepository : IOrderRepository
{
    // 구현 내용
}
```

## 파일 구조

### 클래스 멤버 순서
1. 상수 (const)
2. 정적 필드 (static fields)
3. 필드 (fields)
4. 생성자 (constructors)
5. 프로퍼티 (properties)
6. 메서드 (methods)
7. 중첩 타입 (nested types)

### 접근 제한자 순서
```csharp
public class Example
{
    // 1. public
    // 2. internal
    // 3. protected internal
    // 4. protected
    // 5. private protected
    // 6. private
}
```

## 주석 규칙

### XML 문서 주석
```csharp
/// <summary>
/// 고객 정보를 조회합니다.
/// </summary>
/// <param name="id">고객 ID</param>
/// <returns>고객 정보. 없으면 null.</returns>
/// <exception cref="ArgumentException">ID가 0 이하인 경우</exception>
public async Task<Customer?> GetCustomerAsync(int id)
{
    // 구현
}
```

### 인라인 주석
```csharp
// TODO: 캐싱 구현 필요
// HACK: 임시 해결책, 리팩토링 필요
// NOTE: 성능상의 이유로 이 방식 사용
```
