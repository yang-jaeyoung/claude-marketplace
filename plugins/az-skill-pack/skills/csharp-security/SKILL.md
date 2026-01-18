---
name: csharp-security
description: C# 보안 코딩 가이드라인을 적용합니다. NIST SP 800-63B 비밀번호 정책, 보안 헤더, 암호화 구현 시 자동으로 활성화됩니다. 인증, 비밀번호, 해싱, XSS, CSRF 관련 코드 작업 시 사용합니다.
---

# C# Secure Coding Guidelines

NIST SP 800-63B-4 및 OWASP Top 10 2025 준수 보안 가이드입니다.

## 핵심 보안 원칙

1. **Defense in Depth**: 다층 방어
2. **Zero Trust**: 모든 요청 검증
3. **Least Privilege**: 최소 권한
4. **Secure by Default**: 기본 보안 설정

## NIST 비밀번호 정책

| 항목 | 규칙 |
|------|------|
| 최소 길이 | 8자 필수, **15자 권장** |
| 최대 길이 | 128자 |
| 복잡성 규칙 | **사용 금지** (대소문자/숫자/특수문자 강제 X) |
| 유출 체크 | **필수** (Have I Been Pwned API) |
| 주기적 변경 | **금지** (유출 시에만 변경) |
| 붙여넣기 | **허용 필수** |
| 비밀번호 힌트 | **금지** |
| 보안 질문 | **금지** (MFA로 대체) |

### 비밀번호 검증 순서

1. 길이 체크 (8~128자)
2. 유출 여부 체크 (HIBP API k-Anonymity)
3. 일반적 비밀번호 블랙리스트 체크
4. 사용자명 포함 여부 체크
5. 반복/연속 패턴 경고

## 비밀번호 해싱

### 권장 알고리즘: Argon2id

```
파라미터:
- Salt: 16 bytes
- Hash: 32 bytes
- Iterations: 4
- Memory: 64 MB (65536 KB)
- Parallelism: 2
```

### 대안: PBKDF2

- 최소 600,000 iterations
- SHA-256 또는 SHA-512

**주의**: 타이밍 공격 방지를 위해 `CryptographicOperations.FixedTimeEquals()` 사용

## 필수 보안 헤더

| 헤더 | 값 |
|------|-----|
| X-Content-Type-Options | `nosniff` |
| X-Frame-Options | `DENY` |
| Referrer-Policy | `strict-origin-when-cross-origin` |
| Content-Security-Policy | `default-src 'self'; frame-ancestors 'none';` |
| Strict-Transport-Security | `max-age=63072000; includeSubDomains; preload` |
| Permissions-Policy | `camera=(), microphone=(), geolocation=()` |

**주의**: `X-XSS-Protection`은 deprecated, CSP로 대체됨

## 입력 검증

```csharp
// DTO 검증 예시
[Required]
[StringLength(50, MinimumLength = 3)]
[RegularExpression(@"^[a-zA-Z0-9_-]+$")]
public string Username { get; set; }

[Required]
[EmailAddress]
[MaxLength(255)]
public string Email { get; set; }

[Required]
[MinLength(15)]
[MaxLength(128)]
public string Password { get; set; }
```

## 보안 체크리스트

### 개발 단계
- [ ] 비밀번호 최소 15자 권장, 복잡성 규칙 제거
- [ ] 유출 비밀번호 체크 (HIBP API)
- [ ] Argon2id 또는 PBKDF2(600K+) 해싱
- [ ] 모든 보안 헤더 설정
- [ ] CSP 구현

### 배포 전
- [ ] 취약한 종속성 검사
- [ ] 비밀정보 스캔 (secrets scanning)
- [ ] TLS 1.2/1.3 강제

## 참고

- 상세 구현: `csharp_secure_coding_guide_v3.1.md` 참조
- NIST SP 800-63B: https://pages.nist.gov/800-63-4/
- OWASP Cheat Sheet: https://cheatsheetseries.owasp.org/
