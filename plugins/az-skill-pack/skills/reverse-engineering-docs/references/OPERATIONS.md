# 운영/유지보수 산출물 역설계 가이드

## 목적

코드베이스에서 배포, 모니터링, 문제해결 관련 설정과 스크립트를 분석하여 운영 문서를 작성합니다.

## 분석 영역

```
┌─────────────────────────────────────────────────────────────────┐
│                    운영/유지보수 산출물 영역                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   배포      │  │  모니터링   │  │  문제해결   │             │
│  │             │  │             │  │             │             │
│  │ Dockerfile  │  │ 로깅 설정   │  │ 에러 처리   │             │
│  │ CI/CD      │  │ 메트릭      │  │ 헬스체크    │             │
│  │ K8s 매니페스트│  │ 알림 설정   │  │ 재시도 정책 │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   보안      │  │   백업      │  │   확장성    │             │
│  │             │  │             │  │             │             │
│  │ 인증/인가   │  │ DB 백업     │  │ 스케일링   │             │
│  │ 암호화      │  │ 복구 절차   │  │ 캐싱       │             │
│  │ 감사 로그   │  │ 재해복구    │  │ 로드밸런싱 │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 분석 대상 파일

### 1. 배포 관련

```bash
# Docker 파일
find . -name "Dockerfile*" -o -name "docker-compose*.yml"

# Kubernetes 매니페스트
find . -name "*.yaml" -path "*k8s*" -o -name "*.yaml" -path "*kubernetes*"

# CI/CD 파이프라인
find . -name "*.yml" -path "*.github/workflows*" \
    -o -name "azure-pipelines.yml" \
    -o -name "Jenkinsfile" \
    -o -name ".gitlab-ci.yml"

# Helm Charts
find . -name "Chart.yaml" -o -name "values.yaml"
```

### 2. 모니터링 관련

```bash
# 로깅 설정
grep -rn "Serilog\|NLog\|log4net\|ILogger" --include="*.cs" --include="*.json" | head -20

# 메트릭 설정
grep -rn "prometheus\|metrics\|Meter\|Counter" --include="*.cs" --include="*.json"

# 헬스체크 설정
grep -rn "HealthCheck\|AddHealthChecks\|MapHealthChecks" --include="*.cs"

# 분산 추적
grep -rn "OpenTelemetry\|Jaeger\|Zipkin\|ActivitySource" --include="*.cs"
```

### 3. 환경 설정 관련

```bash
# 환경별 설정 파일
find . -name "appsettings*.json" -o -name ".env*" -o -name "config*.json"

# 시크릿 관리
grep -rn "SecretManager\|KeyVault\|SecretsManager" --include="*.cs" --include="*.json"
```

## 문서 템플릿

```markdown
# 운영/유지보수 가이드

## 1. 문서 정보
| 항목 | 내용 |
|-----|------|
| 프로젝트명 | [프로젝트명] |
| 버전 | [버전] |
| 작성일 | [날짜] |
| 운영 환경 | [Production 환경] |

## 2. 시스템 개요

### 2.1 운영 환경 구성
```
┌─────────────────────────────────────────────────────────────────┐
│                      Production 환경                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │
│  │    CDN      │      │    Load     │      │   API       │    │
│  │  (CloudFront)│  →   │  Balancer   │  →   │  Servers    │    │
│  └─────────────┘      └─────────────┘      └──────┬──────┘    │
│                                                   │            │
│                            ┌──────────────────────┼────────┐   │
│                            │                      │        │   │
│                            ▼                      ▼        ▼   │
│                       ┌─────────┐          ┌─────────┐ ┌─────┐│
│                       │   DB    │          │  Redis  │ │ MQ  ││
│                       │ Primary │          │ Cluster │ │     ││
│                       └────┬────┘          └─────────┘ └─────┘│
│                            │                                   │
│                       ┌────┴────┐                              │
│                       │   DB    │                              │
│                       │ Replica │                              │
│                       └─────────┘                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 인프라 스펙
| 구성요소 | 스펙 | 수량 | 비고 |
|---------|-----|------|------|
| API Server | 4 vCPU, 8GB RAM | 3 | Auto Scaling |
| Database | 8 vCPU, 32GB RAM | 2 | Primary + Replica |
| Redis | 4 vCPU, 16GB RAM | 3 | Cluster 모드 |
| Message Queue | 2 vCPU, 4GB RAM | 2 | HA 구성 |

## 3. 배포 가이드

### 3.1 배포 파이프라인
```
┌────────────────────────────────────────────────────────────────┐
│                      CI/CD 파이프라인                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐  │
│  │ Git │ → │Build│ → │Test │ → │Scan │ → │Push │ → │Deploy│  │
│  │Push │   │     │   │     │   │     │   │Image│   │      │  │
│  └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘  │
│                                                                │
│  Trigger:  dotnet   Unit+     Security  Docker    K8s         │
│  main      build    Integ     Scan      Registry  Rolling     │
│  branch    restore  Test                          Update      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 3.2 배포 절차
| 단계 | 명령어/작업 | 예상 시간 | 롤백 방법 |
|-----|-----------|----------|----------|
| 1. 빌드 | `dotnet build` | 2분 | - |
| 2. 테스트 | `dotnet test` | 5분 | - |
| 3. 이미지 빌드 | `docker build` | 3분 | - |
| 4. 이미지 푸시 | `docker push` | 2분 | - |
| 5. 배포 | `kubectl apply` | 5분 | `kubectl rollout undo` |
| 6. 검증 | 헬스체크 확인 | 2분 | - |

### 3.3 배포 스크립트
```bash
#!/bin/bash
# deploy.sh

VERSION=$1
ENVIRONMENT=$2

# 빌드
dotnet publish -c Release -o ./publish

# Docker 이미지 빌드 및 푸시
docker build -t myapp:$VERSION .
docker push registry.example.com/myapp:$VERSION

# Kubernetes 배포
kubectl set image deployment/myapp \
  myapp=registry.example.com/myapp:$VERSION \
  -n $ENVIRONMENT

# 배포 상태 확인
kubectl rollout status deployment/myapp -n $ENVIRONMENT
```

### 3.4 롤백 절차
| 상황 | 조치 | 명령어 |
|-----|------|-------|
| 배포 실패 | 이전 버전 롤백 | `kubectl rollout undo deployment/myapp` |
| DB 마이그레이션 실패 | 마이그레이션 롤백 | `dotnet ef database update [이전버전]` |
| 설정 오류 | ConfigMap 복원 | `kubectl apply -f configmap-backup.yaml` |

## 4. 모니터링

### 4.1 모니터링 구성
```
┌─────────────────────────────────────────────────────────────────┐
│                      모니터링 스택                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     Grafana Dashboard                     │  │
│  └───────────────────────────┬──────────────────────────────┘  │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐            │
│         │                    │                    │            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│  │ Prometheus  │     │    Loki     │     │   Jaeger    │      │
│  │  (Metrics)  │     │   (Logs)    │     │  (Traces)   │      │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘      │
│         │                   │                   │              │
│         └───────────────────┼───────────────────┘              │
│                             │                                  │
│                    ┌────────┴────────┐                        │
│                    │   Application   │                        │
│                    │   (Serilog +    │                        │
│                    │  OpenTelemetry) │                        │
│                    └─────────────────┘                        │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 핵심 메트릭
| 메트릭 | 설명 | 임계값 | 알림 조건 |
|-------|------|-------|----------|
| CPU 사용률 | 컨테이너 CPU | 80% | > 80% (5분) |
| 메모리 사용률 | 컨테이너 Memory | 85% | > 85% (5분) |
| 응답 시간 | p95 latency | 500ms | > 500ms (1분) |
| 에러율 | 5xx 응답 비율 | 1% | > 1% (1분) |
| 요청 수 | RPS | - | 급격한 변화 |
| DB 연결 | Active connections | 80% | > 80% pool |

### 4.3 대시보드 구성
| 대시보드 | 목적 | 주요 패널 |
|---------|-----|----------|
| Overview | 전체 시스템 상태 | 가용성, 에러율, 응답시간 |
| API Performance | API 성능 분석 | 엔드포인트별 지연시간, 처리량 |
| Infrastructure | 인프라 모니터링 | CPU, Memory, Disk, Network |
| Database | DB 모니터링 | 쿼리 성능, 연결 풀, 복제 지연 |
| Business | 비즈니스 메트릭 | 주문 수, 사용자 수, 매출 |

### 4.4 로깅 설정
```json
// appsettings.json - Serilog 설정 예시
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "System": "Warning"
      }
    },
    "WriteTo": [
      { "Name": "Console" },
      {
        "Name": "Seq",
        "Args": { "serverUrl": "http://seq:5341" }
      }
    ],
    "Enrich": ["FromLogContext", "WithMachineName", "WithThreadId"]
  }
}
```

### 4.5 로그 레벨 가이드
| 레벨 | 용도 | 예시 |
|-----|------|------|
| Debug | 개발 디버깅 | 변수 값, 상세 흐름 |
| Information | 정상 동작 기록 | 요청 시작/완료, 비즈니스 이벤트 |
| Warning | 잠재적 문제 | 재시도, 대체 로직 실행 |
| Error | 오류 발생 | 예외, 처리 실패 |
| Fatal | 치명적 오류 | 시스템 중단 |

## 5. 알림 설정

### 5.1 알림 채널
| 채널 | 용도 | 대상 |
|-----|------|------|
| Slack #alerts-critical | Critical 알림 | 전체 개발팀 |
| Slack #alerts-warning | Warning 알림 | 당번 |
| PagerDuty | On-call 호출 | 당번 |
| Email | 일간 리포트 | 관리자 |

### 5.2 알림 규칙
| 알림명 | 조건 | 심각도 | 알림 채널 |
|-------|------|-------|----------|
| HighErrorRate | Error rate > 5% | Critical | PagerDuty, Slack |
| HighLatency | p95 > 1s | Warning | Slack |
| PodCrashLooping | Restart > 3 | Critical | PagerDuty |
| DBConnectionExhausted | Conn > 90% | Critical | PagerDuty |
| DiskSpaceLow | Disk > 85% | Warning | Slack |

## 6. 헬스체크

### 6.1 헬스체크 엔드포인트
| 엔드포인트 | 용도 | 체크 항목 |
|-----------|------|----------|
| `/health` | 전체 상태 | 모든 의존성 |
| `/health/live` | Liveness | 앱 실행 여부 |
| `/health/ready` | Readiness | 요청 처리 가능 여부 |
| `/health/startup` | Startup | 초기화 완료 여부 |

### 6.2 의존성 체크
| 의존성 | 체크 방법 | 타임아웃 |
|-------|----------|---------|
| Database | 연결 테스트 쿼리 | 5초 |
| Redis | PING 명령 | 2초 |
| Message Queue | 연결 상태 확인 | 3초 |
| External API | 헬스 엔드포인트 호출 | 5초 |

## 7. 장애 대응

### 7.1 장애 등급
| 등급 | 정의 | 대응 시간 | 예시 |
|-----|------|----------|------|
| P1 (Critical) | 서비스 전면 중단 | 15분 | 전체 시스템 다운 |
| P2 (High) | 주요 기능 장애 | 30분 | 결제 불가 |
| P3 (Medium) | 일부 기능 장애 | 2시간 | 알림 발송 실패 |
| P4 (Low) | 경미한 이슈 | 24시간 | UI 깨짐 |

### 7.2 장애 대응 체크리스트
```
┌─────────────────────────────────────────────────────────────────┐
│                      장애 대응 프로세스                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 장애 감지 및 확인                                            │
│     □ 알림 확인 및 장애 범위 파악                                 │
│     □ 영향받는 서비스/사용자 확인                                 │
│     □ 장애 등급 결정                                             │
│                                                                 │
│  2. 초기 대응                                                    │
│     □ 담당자 소집 (P1/P2: 즉시)                                  │
│     □ 상태 페이지 업데이트                                       │
│     □ 고객 커뮤니케이션 (필요시)                                  │
│                                                                 │
│  3. 원인 분석                                                    │
│     □ 로그 분석                                                  │
│     □ 메트릭 확인                                                │
│     □ 최근 변경사항 확인                                         │
│                                                                 │
│  4. 복구 작업                                                    │
│     □ 긴급 조치 (롤백, 재시작 등)                                │
│     □ 근본 원인 해결                                             │
│     □ 정상화 확인                                                │
│                                                                 │
│  5. 사후 처리                                                    │
│     □ 포스트모템 작성                                            │
│     □ 재발 방지 대책 수립                                        │
│     □ 문서 업데이트                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 일반적인 문제 및 해결책
| 증상 | 원인 | 해결책 |
|-----|------|-------|
| 504 Gateway Timeout | 백엔드 응답 지연 | 스케일 아웃, 쿼리 최적화 |
| 503 Service Unavailable | 인스턴스 부족 | Pod 증설, HPA 조정 |
| OOM (메모리 부족) | 메모리 누수 | 재시작, 메모리 프로파일링 |
| DB 연결 부족 | 커넥션 풀 소진 | 풀 크기 조정, 쿼리 최적화 |
| 높은 CPU | 비효율적 로직 | 프로파일링, 캐싱 |

## 8. 백업 및 복구

### 8.1 백업 정책
| 대상 | 주기 | 보존 기간 | 방식 |
|-----|------|----------|------|
| Database | 일 1회 (전체) | 30일 | pg_dump |
| Database | 5분 (WAL) | 7일 | WAL 아카이브 |
| Redis | 일 1회 | 7일 | RDB 스냅샷 |
| 설정 파일 | Git 커밋 시 | 영구 | Git |

### 8.2 복구 절차
| 시나리오 | RTO | RPO | 절차 |
|---------|-----|-----|------|
| 데이터 손실 | 1시간 | 5분 | WAL 복구 |
| DB 서버 장애 | 15분 | 0 | Replica 승격 |
| 전체 리전 장애 | 4시간 | 1시간 | DR 사이트 전환 |

## 9. 보안 운영

### 9.1 접근 통제
| 역할 | 접근 범위 | 인증 방식 |
|-----|----------|----------|
| 개발자 | Dev/Staging | SSO + MFA |
| 운영자 | All | SSO + MFA + VPN |
| 외부 | 없음 | - |

### 9.2 보안 체크리스트
| 항목 | 주기 | 담당 |
|-----|------|------|
| 의존성 취약점 스캔 | 일간 | CI/CD 자동 |
| 컨테이너 이미지 스캔 | 배포 시 | CI/CD 자동 |
| 침투 테스트 | 분기 | 보안팀 |
| 접근 권한 검토 | 월간 | 운영팀 |
| 인증서 만료 확인 | 주간 | 모니터링 자동 |

## 10. 연락처

### 10.1 담당자
| 역할 | 담당자 | 연락처 |
|-----|-------|-------|
| 기술 리드 | [이름] | [이메일/전화] |
| DevOps | [이름] | [이메일/전화] |
| DBA | [이름] | [이메일/전화] |
| 보안 담당 | [이름] | [이메일/전화] |

### 10.2 외부 지원
| 서비스 | 공급업체 | 지원 채널 |
|-------|---------|----------|
| Cloud | AWS | 지원 티켓 |
| Database | - | 커뮤니티 |
| 모니터링 | Datadog | 지원 채널 |
```

## 분석 명령어 모음

```bash
# Docker 설정 분석
cat Dockerfile
cat docker-compose.yml

# Kubernetes 설정 분석
find . -name "*.yaml" -path "*k8s*" -exec cat {} \;

# CI/CD 파이프라인 분석
cat .github/workflows/*.yml 2>/dev/null
cat azure-pipelines.yml 2>/dev/null
cat .gitlab-ci.yml 2>/dev/null

# 환경 변수 분석
grep -rn "Environment\|env:" --include="*.yaml" --include="*.yml"

# 헬스체크 설정 분석
grep -rn "healthcheck\|livenessProbe\|readinessProbe" --include="*.yaml" --include="*.cs"

# 리소스 제한 분석
grep -rn "resources:\|limits:\|requests:" --include="*.yaml"
```
# 로깅 설정
grep -rn "Serilog\|NLog\|log4net\|ILogger" --include="*.cs" | head -20
cat appsettings*.json 2>/dev/null | grep -A 10 "Logging\|Serilog"

# 헬스체크
grep -rn "AddHealthChecks\|MapHealthChecks\|IHealthCheck" --include="*.cs"

# 메트릭 (Prometheus, OpenTelemetry)
grep -rn "Metrics\|Counter\|Histogram\|OpenTelemetry" --include="*.cs"
```

### 3. 보안 관련

```bash
# 인증/인가 설정
grep -rn "AddAuthentication\|AddAuthorization\|JwtBearer" --include="*.cs"

# CORS 설정
grep -rn "AddCors\|UseCors\|WithOrigins" --include="*.cs"

# 암호화 설정
grep -rn "DataProtection\|Encrypt\|Decrypt" --include="*.cs"
```

## 문서 템플릿

```markdown
# 운영/유지보수 가이드

## 1. 문서 정보
| 항목 | 내용 |
|-----|------|
| 프로젝트명 | [프로젝트명] |
| 버전 | [버전] |
| 작성일 | [날짜] |
| 환경 | Development / Staging / Production |

## 2. 시스템 환경

### 2.1 환경 구성
| 환경 | 용도 | 인프라 | URL |
|-----|------|-------|-----|
| Development | 개발 | Docker Local | http://localhost:5000 |
| Staging | 테스트 | AWS ECS | https://staging.example.com |
| Production | 운영 | AWS EKS | https://api.example.com |

### 2.2 서버 구성
```
Production Environment
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                         │
│                    (AWS ALB / Nginx)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │  App 1  │     │  App 2  │     │  App 3  │
    │ (Pod)   │     │ (Pod)   │     │ (Pod)   │
    └────┬────┘     └────┬────┘     └────┬────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
              ┌─────────────────────┐
              │   Database (RDS)    │
              │   Cache (Redis)     │
              │   Queue (SQS)       │
              └─────────────────────┘
```

### 2.3 필수 환경 변수
| 변수명 | 설명 | 예시 | 필수 |
|-------|------|------|-----|
| ASPNETCORE_ENVIRONMENT | 환경 구분 | Production | Y |
| ConnectionStrings__DefaultConnection | DB 연결 | Host=...;Database=... | Y |
| Jwt__Secret | JWT 시크릿 | *** | Y |
| Redis__Configuration | Redis 연결 | localhost:6379 | N |

## 3. 배포 절차

### 3.1 배포 파이프라인
```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Commit  │ →  │  Build   │ →  │   Test   │ →  │  Deploy  │
│  (Git)   │    │  (CI)    │    │  (Auto)  │    │  (CD)    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │              │               │               │
     │              ▼               ▼               ▼
     │         컴파일/빌드      단위테스트        스테이징
     │         Docker 이미지   통합테스트         프로덕션
     └──────────────────────────────────────────────┘
```

### 3.2 배포 명령어

#### Docker 배포
```bash
# 이미지 빌드
docker build -t myapp:latest .

# 이미지 푸시
docker push myregistry.azurecr.io/myapp:latest

# 컨테이너 실행
docker-compose -f docker-compose.prod.yml up -d
```

#### Kubernetes 배포
```bash
# 매니페스트 적용
kubectl apply -f k8s/deployment.yaml

# 롤아웃 상태 확인
kubectl rollout status deployment/myapp

# 롤백
kubectl rollout undo deployment/myapp
```

### 3.3 배포 체크리스트
| 단계 | 항목 | 확인 |
|-----|------|-----|
| 사전 | DB 마이그레이션 필요 여부 | □ |
| 사전 | 환경 변수 변경 여부 | □ |
| 사전 | 의존 서비스 상태 확인 | □ |
| 배포 | 이미지 빌드 성공 | □ |
| 배포 | 테스트 통과 | □ |
| 사후 | 헬스체크 통과 | □ |
| 사후 | 로그 정상 확인 | □ |
| 사후 | 주요 기능 테스트 | □ |

## 4. 모니터링

### 4.1 헬스체크 엔드포인트
| 엔드포인트 | 용도 | 정상 응답 |
|-----------|------|----------|
| /health | 기본 헬스체크 | 200 OK |
| /health/ready | 준비 상태 | 200 OK |
| /health/live | 생존 상태 | 200 OK |
| /health/db | DB 연결 상태 | 200 OK |

### 4.2 로깅 구성
| 로그 레벨 | 환경 | 용도 |
|----------|-----|------|
| Debug | Development | 상세 디버깅 |
| Information | Staging | 일반 정보 |
| Warning | Production | 경고 이상 |
| Error | All | 오류 추적 |

### 4.3 로그 위치
| 환경 | 저장소 | 보관 기간 |
|-----|-------|----------|
| Development | Console / 파일 | 1일 |
| Staging | CloudWatch | 7일 |
| Production | CloudWatch + S3 | 90일 |

### 4.4 모니터링 대시보드
| 메트릭 | 임계값 | 알림 채널 |
|-------|-------|----------|
| CPU 사용률 | > 80% | Slack |
| 메모리 사용률 | > 85% | Slack |
| 응답 시간 | > 500ms | Slack, PagerDuty |
| 에러율 | > 1% | Slack, PagerDuty |
| 5xx 에러 | > 10/min | PagerDuty |

## 5. 문제해결 가이드

### 5.1 일반적인 문제

#### 애플리케이션 시작 실패
| 증상 | 원인 | 해결 방법 |
|-----|------|----------|
| 시작 즉시 종료 | 환경 변수 누락 | 필수 환경 변수 확인 |
| DB 연결 실패 | 연결 문자열 오류 | 연결 문자열 및 네트워크 확인 |
| 포트 충돌 | 포트 이미 사용 중 | 다른 포트 사용 또는 기존 프로세스 종료 |

#### 성능 저하
| 증상 | 원인 | 해결 방법 |
|-----|------|----------|
| 느린 응답 | DB 쿼리 지연 | 쿼리 최적화, 인덱스 추가 |
| 메모리 증가 | 메모리 누수 | 프로파일링, 캐시 정리 |
| CPU 높음 | 과도한 요청 | 스케일 아웃, 캐싱 |

### 5.2 진단 명령어

```bash
# 로그 확인
kubectl logs -f deployment/myapp --tail=100

# 리소스 사용량
kubectl top pods

# 이벤트 확인
kubectl get events --sort-by='.lastTimestamp'

# DB 연결 테스트
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1"

# Redis 연결 테스트
redis-cli -h $REDIS_HOST ping
```

### 5.3 롤백 절차

```bash
# 1. 현재 상태 확인
kubectl rollout history deployment/myapp

# 2. 이전 버전으로 롤백
kubectl rollout undo deployment/myapp

# 3. 특정 버전으로 롤백
kubectl rollout undo deployment/myapp --to-revision=3

# 4. 롤백 확인
kubectl rollout status deployment/myapp
```

## 6. 백업 및 복구

### 6.1 백업 정책
| 대상 | 주기 | 보관 기간 | 방법 |
|-----|------|----------|------|
| 데이터베이스 | 매일 | 30일 | AWS RDS 자동 백업 |
| 파일 스토리지 | 매일 | 90일 | S3 버전관리 |
| 설정 파일 | 변경 시 | 무기한 | Git 버전관리 |

### 6.2 복구 절차

#### 데이터베이스 복구
```bash
# 1. 복구 시점 확인
aws rds describe-db-cluster-snapshots --db-cluster-identifier mydb

# 2. 스냅샷에서 복구
aws rds restore-db-cluster-from-snapshot \
  --db-cluster-identifier mydb-restored \
  --snapshot-identifier mydb-snapshot-20240115

# 3. 연결 문자열 업데이트
# 4. 애플리케이션 재시작
```

## 7. 보안 운영

### 7.1 보안 체크리스트
| 항목 | 주기 | 담당 |
|-----|------|-----|
| 인증서 갱신 | 연 1회 | DevOps |
| 시크릿 로테이션 | 분기 1회 | DevOps |
| 취약점 스캔 | 주 1회 | 보안팀 |
| 접근 권한 검토 | 월 1회 | 보안팀 |

### 7.2 시크릿 관리
| 시크릿 | 저장소 | 갱신 주기 |
|-------|-------|----------|
| DB 비밀번호 | AWS Secrets Manager | 90일 |
| JWT 시크릿 | K8s Secret | 180일 |
| API 키 | AWS Secrets Manager | 요청 시 |

## 8. 연락처

### 8.1 에스컬레이션 경로
| 레벨 | 담당 | 연락처 | 응답 시간 |
|-----|------|-------|----------|
| L1 | 운영팀 | ops@example.com | 30분 |
| L2 | 개발팀 | dev@example.com | 2시간 |
| L3 | 아키텍트 | arch@example.com | 4시간 |

### 8.2 외부 서비스 지원
| 서비스 | 제공사 | 지원 연락처 |
|-------|-------|-----------|
| AWS | Amazon | AWS Support |
| Database | AWS RDS | AWS Support |
| Monitoring | Datadog | support@datadog.com |
```

## 분석 명령어 모음

```bash
# Docker 설정 분석
cat Dockerfile | head -50
cat docker-compose*.yml

# CI/CD 파이프라인 분석
cat .github/workflows/*.yml 2>/dev/null
cat azure-pipelines.yml 2>/dev/null

# 헬스체크 구성 분석
grep -rn "HealthCheck\|MapHealth" --include="*.cs"

# 로깅 설정 분석
grep -rn "UseSerilog\|AddLogging\|ConfigureLogging" --include="*.cs"

# 환경 설정 분석
cat appsettings*.json | head -100
```
