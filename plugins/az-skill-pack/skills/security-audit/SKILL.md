---
name: security-audit
description: 프레임워크/언어에 관계없이 대상 프로젝트를 자동 분석하여 적합한 보안 점검을 수행하는 범용 스킬입니다.
---

# Universal Security Audit

## Usage
```
/security-audit [scope] [options]
```

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `scope` | `full`\|`error`\|`auth`\|`data`\|`api`\|`deps`\|`config` | `full` |
| `--severity` | `critical`\|`high`\|`medium`\|`low` | `medium` |
| `--format` | `table`\|`report`\|`checklist` | `table` |
| `--fix` | 수정 코드 예시 포함 | `false` |
| `--path` | 점검 대상 경로 | `.` |

---

## Phase 1: Project Detection

### 감지 파일
| 파일 | 언어/프레임워크 |
|------|-----------------|
| `package.json` | Node.js/JS/TS |
| `*.csproj` | .NET/C# |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `requirements.txt`, `pyproject.toml` | Python |
| `pom.xml`, `build.gradle` | Java/Kotlin |
| `Gemfile` | Ruby |
| `composer.json` | PHP |

### 프레임워크 감지
| 패턴 | 프레임워크 | 타입 |
|------|-----------|------|
| `next.config`, `app/` | Next.js | frontend |
| `remix.config` | Remix | frontend |
| `vite.config` | React/Vite | frontend |
| `angular.json` | Angular | frontend |
| `nuxt.config` | Nuxt.js | frontend |
| `svelte.config` | SvelteKit | frontend |
| `Program.cs`, `*.csproj` | ASP.NET Core | backend |
| `main.go`, `go.mod` | Go | backend |
| `Cargo.toml`, `main.rs` | Rust | backend |
| `manage.py`, `settings.py` | Django | backend |
| `app.py` | Flask | backend |
| `fastapi` | FastAPI | backend |
| `pom.xml`, `Application.java` | Spring Boot | backend |
| `express`, `app.js` | Express.js | backend |
| `nestjs`, `app.module.ts` | NestJS | backend |

---

## Phase 2: Security Checklist

### 1. ERROR_HANDLING
| ID | 항목 | 심각도 | 패턴 |
|----|------|--------|------|
| ERR-001 | 전역 예외 처리 | 🟠 | `UseExceptionHandler`, `ErrorBoundary`, `recover()`, `@ExceptionHandler` |
| ERR-002 | 스택트레이스 숨김 | 🔴 | `NODE_ENV`, `ASPNETCORE_ENVIRONMENT`, `DEBUG=False` |
| ERR-003 | 구조화 로깅 | 🟡 | `winston`, `Serilog`, `loguru`, `zap`, `tracing` |
| ERR-004 | 요청 추적 ID | 🟡 | `correlation-id`, `trace-id`, `x-request-id` |

### 2. AUTHENTICATION
| ID | 항목 | 심각도 | 패턴 |
|----|------|--------|------|
| AUTH-001 | 안전한 토큰 저장 | 🔴 | ❌ `localStorage` → ✅ `httpOnly`, `secure`, `sameSite` |
| AUTH-002 | 비밀번호 해싱 | 🔴 | ✅ `BCrypt`, `Argon2`, `PBKDF2` / ❌ `MD5`, `SHA1` |
| AUTH-003 | JWT 검증 | 🔴 | `TokenValidationParameters`, `jwt.verify`, `ValidateIssuer` |
| AUTH-004 | 세션 관리 | 🟠 | `session timeout`, `regenerate` |
| AUTH-005 | MFA/2FA | 🟡 | `totp`, `2fa`, `authenticator` |

### 3. AUTHORIZATION
| ID | 항목 | 심각도 | 패턴 |
|----|------|--------|------|
| AUTHZ-001 | 엔드포인트 보호 | 🔴 | `[Authorize]`, `@login_required`, `@PreAuthorize`, `authMiddleware` |
| AUTHZ-002 | RBAC | 🟠 | `RequireRole`, `hasRole`, `has_permission` |
| AUTHZ-003 | 리소스 소유권 | 🔴 | `userId`, `ownerId`, `belongsTo` (🔍수동확인) |
| AUTHZ-004 | 최소 권한 | 🟠 | `FallbackPolicy Deny`, `defaultDeny` |

### 4. INPUT_VALIDATION
| ID | 항목 | 심각도 | 패턴 |
|----|------|--------|------|
| VAL-001 | 입력 검증 | 🔴 | `FluentValidation`, `zod`, `pydantic`, `@Valid` |
| VAL-002 | SQL Injection | 🔴 | ✅ `parameterized`, `PreparedStatement` / ❌ string concat |
| VAL-003 | XSS | 🔴 | ✅ `DOMPurify`, `HtmlEncode` / ❌ unsafe innerHTML |
| VAL-004 | Path Traversal | 🔴 | ✅ `Path.Combine`, `path.join` / ❌ `../` |
| VAL-005 | Command Injection | 🔴 | ❌ unsanitized shell execution |

### 5. API_SECURITY
| ID | 항목 | 심각도 | 패턴 |
|----|------|--------|------|
| API-001 | HTTPS 강제 | 🔴 | `UseHttpsRedirection`, `ssl_certificate` |
| API-002 | CORS | 🟠 | ✅ specific origins / ❌ `AllowAnyOrigin`, `*` |
| API-003 | Rate Limiting | 🟠 | `RateLimiter`, `express-rate-limit`, `limit_req` |
| API-004 | 요청 크기 제한 | 🟡 | `MaxRequestBodySize`, `client_max_body_size` |
| API-005 | API 버전 관리 | 🟢 | `/api/v1`, `api-version` |

### 6. DATA_PROTECTION
| ID | 항목 | 심각도 | 패턴 |
|----|------|--------|------|
| DATA-001 | 민감 데이터 암호화 | 🔴 | `DataProtection`, `Fernet`, `AES`, `Cipher` |
| DATA-002 | Secret 관리 | 🔴 | ✅ `env`, `KeyVault` / ❌ hardcoded |
| DATA-003 | 로깅 민감정보 제외 | 🔴 | `mask`, `redact`, `SensitiveDataMasking` |
| DATA-004 | 데이터 마스킹 | 🟡 | `mask`, `***` |

### 7. SESSION_COOKIE
| ID | 항목 | 심각도 | 패턴 |
|----|------|--------|------|
| SESS-001 | HttpOnly | 🔴 | `HttpOnly: true` |
| SESS-002 | Secure | 🔴 | `Secure: true` |
| SESS-003 | SameSite | 🟠 | `SameSite: Strict\|Lax` |
| SESS-004 | 세션 타임아웃 | 🟡 | `expire`, `maxAge` |

### 8. SECURITY_HEADERS
| ID | 항목 | 심각도 | 패턴 |
|----|------|--------|------|
| HDR-001 | CSP | 🟠 | `Content-Security-Policy` |
| HDR-002 | X-Content-Type-Options | 🟡 | `nosniff` |
| HDR-003 | X-Frame-Options | 🟡 | `DENY`, `SAMEORIGIN` |
| HDR-004 | HSTS | 🟠 | `Strict-Transport-Security` |
| HDR-005 | Referrer-Policy | 🟢 | `Referrer-Policy` |

### 9. DEPENDENCY_SECURITY
| ID | 항목 | 심각도 | 명령 |
|----|------|--------|------|
| DEP-001 | 취약점 스캔 | 🔴 | `npm audit`, `dotnet list package --vulnerable`, `pip-audit`, `govulncheck`, `cargo audit` |
| DEP-002 | Lock 파일 | 🟡 | `package-lock.json`, `go.sum`, `Cargo.lock` |
| DEP-003 | 미사용 의존성 | 🟢 | `npx depcheck`, `pip-autoremove` |

### 10. DATABASE_SECURITY (Backend)
| ID | 항목 | 심각도 | 패턴 |
|----|------|--------|------|
| DB-001 | 연결문자열 보안 | 🔴 | ❌ hardcoded credentials |
| DB-002 | 권한 분리 | 🟠 | `ReadOnly`, `WriteConnection` |
| DB-003 | Row-Level Security | 🟠 | `HasQueryFilter`, `TenantId`, `RLS` |
| DB-004 | 연결 풀링 | 🟡 | `pooling`, `maxPoolSize` |

### 11. AUDIT_LOGGING
| ID | 항목 | 심각도 | 패턴 |
|----|------|--------|------|
| AUDIT-001 | 인증 이벤트 | 🟠 | login/logout/failure 기록 |
| AUDIT-002 | 데이터 변경 | 🟠 | `audit`, `changelog`, `history` |
| AUDIT-003 | 관리자 작업 | 🟠 | 권한/설정 변경 기록 |

---

## Phase 3: Output

### 상태 아이콘
`✅` 구현됨 | `⚠️` 부분구현 | `❌` 미구현 | `🔍` 수동확인 | `➖` N/A

### 심각도
| 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low |
|------------|---------|-----------|--------|
| 24시간 내 | 1주 내 | 1개월 내 | 분기 내 |

### 결과 템플릿
```
## Summary
| Category | ✅ | ⚠️ | ❌ | Score |
|----------|---|---|---|-------|

## [Category]
| ID | 항목 | 상태 | 심각도 | 위치 |

## Priority Actions
### 🔴 Critical
| ID | 항목 | 위치 | 조치 |
```

---

## Examples
| 명령 | 설명 |
|------|------|
| `/security-audit` | 전체 점검 |
| `/security-audit auth` | 인증만 |
| `/security-audit --severity=critical` | Critical만 |
| `/security-audit --fix` | 수정 예시 포함 |

---

## CI/CD
```yaml
- name: Security Audit
  run: |
    [ -f package.json ] && npm audit --audit-level=high
    [ -f *.csproj ] && dotnet list package --vulnerable
    [ -f requirements.txt ] && pip-audit
    [ -f go.mod ] && govulncheck ./...
    [ -f Cargo.toml ] && cargo audit
```

---

## Extension
```yaml
custom_rules:
  - id: CUSTOM-001
    name: 회사 정책
    patterns: { all: [companyPolicy] }
    severity: high

exclude_rules: [DEP-003, HDR-005]
```
