---
name: reverse-engineering-docs
description: Generate project documentation by analyzing the codebase (requirements, functional spec, use cases, architecture, UI, database, operations)
---

# 프로젝트 문서 역설계 Skill

코드베이스를 분석하여 프로젝트 문서를 역설계합니다.

## 문서 유형

| 문서 | 설명 | 가이드 |
|------|------|--------|
| 요구사항 명세서 | 기능적/비기능적 요구사항 | [REQUIREMENTS.md](references/REQUIREMENTS.md) |
| 기능 명세서 | 각 기능의 상세 동작 | [FUNCTIONAL.md](references/FUNCTIONAL.md) |
| 유스케이스 시나리오 | 사용자-시스템 상호작용 | [USECASE.md](references/USECASE.md) |
| 아키텍처 설계서 | 시스템 구조 및 컴포넌트 | [ARCHITECTURE.md](references/ARCHITECTURE.md) |
| UI/화면 설계서 | 인터페이스 구성 및 흐름 | [UI_DESIGN.md](references/UI_DESIGN.md) |
| 데이터베이스 설계서 | 데이터 모델 및 스키마 | [DATABASE.md](references/DATABASE.md) |
| 운영/유지보수 문서 | 배포, 모니터링, 문제해결 | [OPERATIONS.md](references/OPERATIONS.md) |

## 분석 프로세스

1. **프로젝트 구조 파악** - 디렉토리, 설정 파일, 의존성
2. **기술 스택 식별** - 언어, 프레임워크, 라이브러리
3. **아키텍처 패턴 분석** - 레이어 구조, 모듈 관계
4. **도메인 모델 추출** - 엔티티, 값 객체, 비즈니스 규칙
5. **기능 및 API 매핑** - 엔드포인트, 서비스, 유스케이스
6. **문서 생성** - 표준 템플릿 기반 문서화

## 사용 방법

```
# 전체 문서 생성
이 프로젝트의 문서를 역설계해 주세요

# 특정 문서만 생성
이 코드베이스의 아키텍처 설계서를 작성해 주세요
```

## 분석 대상 파일

| 기술 | 파일 |
|------|------|
| .NET | `*.csproj`, `appsettings.json` |
| Node.js | `package.json`, `tsconfig.json` |
| Python | `requirements.txt`, `pyproject.toml` |
| Docker | `Dockerfile`, `docker-compose.yml` |
| CI/CD | `.github/workflows/`, `azure-pipelines.yml` |

## 코드 분석 영역

| 영역 | 패턴 |
|------|------|
| 엔티티/모델 | `**/Models/**`, `**/Entities/**` |
| 서비스 | `**/Services/**`, `**/Application/**` |
| 컨트롤러 | `**/Controllers/**`, `**/Endpoints/**` |
| 데이터 접근 | `**/Repositories/**`, `**/Data/**` |

## 문서 품질 기준

| 기준 | 설명 |
|------|------|
| 완전성 | 코드에서 식별된 모든 기능 포함 |
| 정확성 | 실제 구현과 일치 |
| 일관성 | 문서 간 용어 통일 |
| 추적성 | 코드 위치 참조 포함 |

## 주의사항

1. **코드 우선**: 추측보다 실제 코드 기반 분석
2. **버전 명시**: 분석 시점의 코드 상태 기록
3. **미구현 구분**: 계획된 기능과 구현된 기능 구분
4. **민감정보 제외**: 비밀번호, API 키 등 제외
