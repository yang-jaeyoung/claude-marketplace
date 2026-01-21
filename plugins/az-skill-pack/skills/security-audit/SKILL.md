---
name: security-audit
description: Run a comprehensive security audit on the codebase, detecting project type and applying appropriate checks
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

## Phase 1: Project Detection

프로젝트 타입 자동 감지:

| 파일 | 언어/프레임워크 |
|------|--------------------|
| `package.json` | Node.js/JS/TS |
| `*.csproj` | .NET/C# |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `requirements.txt` | Python |
| `pom.xml` | Java/Kotlin |

## Phase 2: Security Checklist

**상세 체크리스트**: [references/checklists.md](references/checklists.md)

### 카테고리 요약

| # | Category | 항목수 | 핵심 점검 |
|---|----------|--------|----------|
| 1 | ERROR_HANDLING | 4 | 전역 예외, 스택트레이스 숨김 |
| 2 | AUTHENTICATION | 5 | 토큰 저장, 비밀번호 해싱, JWT |
| 3 | AUTHORIZATION | 4 | 엔드포인트 보호, RBAC |
| 4 | INPUT_VALIDATION | 5 | SQL Injection, XSS, Path Traversal |
| 5 | API_SECURITY | 5 | HTTPS, CORS, Rate Limiting |
| 6 | DATA_PROTECTION | 4 | 암호화, Secret 관리 |
| 7 | SESSION_COOKIE | 4 | HttpOnly, Secure, SameSite |
| 8 | SECURITY_HEADERS | 5 | CSP, HSTS, X-Frame-Options |
| 9 | DEPENDENCY_SECURITY | 3 | 취약점 스캔, Lock 파일 |
| 10 | DATABASE_SECURITY | 4 | 연결문자열, RLS |
| 11 | AUDIT_LOGGING | 3 | 인증 이벤트, 변경 기록 |

## Phase 3: Output

### 상태 아이콘

`✅` 구현됨 | `⚠️` 부분구현 | `❌` 미구현 | `🔍` 수동확인 | `➖` N/A

### 심각도

| 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low |
|-------------|---------|-----------|--------|
| 24시간 내 | 1주 내 | 1개월 내 | 분기 내 |

### 결과 템플릿

```
## Summary
| Category | ✅ | ⚠️ | ❌ | Score |

## Priority Actions
### 🔴 Critical
| ID | 항목 | 위치 | 조치 |
```

## Examples

| 명령 | 설명 |
|------|------|
| `/security-audit` | 전체 점검 |
| `/security-audit auth` | 인증만 |
| `/security-audit --severity=critical` | Critical만 |
| `/security-audit --fix` | 수정 예시 포함 |

## CI/CD Integration

```yaml
- name: Security Audit
  run: |
    [ -f package.json ] && npm audit --audit-level=high
    [ -f *.csproj ] && dotnet list package --vulnerable
    [ -f requirements.txt ] && pip-audit
    [ -f go.mod ] && govulncheck ./...
```
