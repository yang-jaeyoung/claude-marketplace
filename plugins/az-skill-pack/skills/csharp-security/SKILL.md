---
name: csharp-security
description: C# 보안 코딩 가이드라인을 적용합니다. NIST SP 800-63B 비밀번호 정책, 보안 헤더, 암호화 구현 시 자동으로 활성화됩니다.
---

# C# Secure Coding Guidelines

NIST SP 800-63B-4 및 OWASP Top 10 2025 준수 가이드입니다.

## 핵심 원칙

**Defense in Depth** | **Zero Trust** | **Least Privilege** | **Secure by Default**

## NIST 비밀번호 정책

| 항목 | 규칙 |
|------|------|
| 길이 | 8자 필수, **15자 권장**, 최대 128자 |
| 복잡성 규칙 | **사용 금지** |
| 유출 체크 | **필수** (HIBP API k-Anonymity) |
| 주기적 변경 | **금지** (유출 시에만) |

**검증 순서**: 길이 체크 → 유출 여부 → 블랙리스트 → 사용자명 포함 여부

## 비밀번호 해싱

| 알고리즘 | 설정 |
|----------|------|
| **Argon2id** (권장) | Salt 16B, Hash 32B, Iter 4, Mem 64MB, Para 2 |
| PBKDF2 (대안) | 최소 600,000 iterations, SHA-256/512 |

⚠️ `CryptographicOperations.FixedTimeEquals()` 사용 (타이밍 공격 방지)

## 필수 보안 헤더

| 헤더 | 값 |
|------|-----|
| X-Content-Type-Options | `nosniff` |
| X-Frame-Options | `DENY` |
| Content-Security-Policy | `default-src 'self'` |
| Strict-Transport-Security | `max-age=63072000; includeSubDomains` |
| Referrer-Policy | `strict-origin-when-cross-origin` |

## 체크리스트

**개발**: ☐ 비밀번호 15자 권장 ☐ HIBP API 연동 ☐ Argon2id/PBKDF2 해싱 ☐ 보안 헤더 설정

**배포**: ☐ 취약 종속성 검사 ☐ 비밀정보 스캔 ☐ TLS 1.2/1.3 강제

## 참고

- [NIST SP 800-63B](https://pages.nist.gov/800-63-4/)
- [OWASP Cheat Sheet](https://cheatsheetseries.owasp.org/)
