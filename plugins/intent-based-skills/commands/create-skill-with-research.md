---
description: "Research-driven skill creation. Conducts domain research before generating skill with enriched context"
argument-hint: "<skill_name> --domain <domain> [--depth quick|standard] [--auto] [--reuse-research]"
allowed-tools: ["Bash", "Read", "Write", "Glob", "Grep", "Task", "WebSearch", "WebFetch", "Edit"]
---

# Create Skill with Research - 리서치 기반 스킬 생성

도메인 리서치를 수행한 후 그 결과를 바탕으로 완성도 높은 스킬을 생성합니다.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              CREATE-SKILL-WITH-RESEARCH PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [INPUT] skill_name + domain                                                │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────────┐                                                    │
│  │ STAGE 1: RESEARCH   │  research-orchestrator (quick depth)              │
│  │ - 도메인 best practices                                                  │
│  │ - 기술 제약사항                                                          │
│  │ - 검증 항목 수집                                                         │
│  └──────────┬──────────┘                                                    │
│             │                                                               │
│             ▼                                                               │
│  ┌─────────────────────┐                                                    │
│  │ CHECKPOINT          │  "리서치 결과를 검토하시겠습니까? [Y/n]"          │
│  └──────────┬──────────┘                                                    │
│             │                                                               │
│             ▼                                                               │
│  ┌─────────────────────┐                                                    │
│  │ STAGE 2: EXTRACT    │  key-insights.json 생성                           │
│  │ - triggers 추출                                                          │
│  │ - constraints 추출                                                       │
│  │ - verification 항목                                                      │
│  └──────────┬──────────┘                                                    │
│             │                                                               │
│             ▼                                                               │
│  ┌─────────────────────┐                                                    │
│  │ STAGE 3: GENERATE   │  intent-skill-creator (context 주입)              │
│  │ - intent.yaml                                                            │
│  │ - SKILL.md                                                               │
│  │ - schema/                                                                │
│  │ - verification/                                                          │
│  │ - references/ (리서치 결과)                                              │
│  └──────────┬──────────┘                                                    │
│             │                                                               │
│             ▼                                                               │
│  [OUTPUT] 완성도 높은 스킬 구조                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Usage

```bash
# 기본 사용법
/create-skill-with-research <skill_name> --domain "<domain_description>"

# 전체 옵션
/create-skill-with-research <skill_name> \
  --domain "<domain_description>" \
  --type <analyzer|generator|documenter|transformer|validator> \
  --depth <quick|standard> \
  --output <output_dir> \
  --auto \
  --reuse-research \
  --skip-research
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<skill_name>` | Yes | - | 생성할 스킬 이름 (kebab-case) |
| `--domain` | Yes | - | 스킬 도메인 설명 |
| `--type` | No | analyzer | 스킬 유형 |
| `--depth` | No | quick | 리서치 깊이 (quick: 2-3 stages, standard: 4-6 stages) |
| `--output` | No | ./skills | 출력 디렉토리 |
| `--auto` | No | false | 전체 자동 실행 (체크포인트 스킵) |
| `--reuse-research` | No | false | 기존 리서치 결과 재사용 |
| `--skip-research` | No | false | 리서치 스킵 (기본 intent-skill-creator 동작) |

## Examples

```bash
# Kubernetes 분석 스킬
/create-skill-with-research kubernetes-analyzer \
  --domain "Kubernetes 클러스터 구성 분석 및 보안 검토"

# Terraform 마이그레이션 스킬 (standard depth)
/create-skill-with-research terraform-migrator \
  --domain "Terraform v0.x에서 v1.x로 마이그레이션" \
  --type transformer \
  --depth standard

# 기존 리서치 재사용
/create-skill-with-research kubernetes-security-checker \
  --domain "Kubernetes 보안 점검" \
  --reuse-research

# 리서치 없이 빠른 생성
/create-skill-with-research json-formatter \
  --domain "JSON 파일 포맷팅" \
  --type transformer \
  --skip-research
```

---

## Execution Instructions

### Stage 1: Domain Research

#### 1.1 리서치 캐시 확인 (--reuse-research 또는 기본)

```bash
# 기존 리서치 결과 확인
CACHE_DIR=".research-cache/${SKILL_DOMAIN_HASH}"
if [ -d "$CACHE_DIR" ] && [ -f "$CACHE_DIR/research-data.json" ]; then
    echo "기존 리서치 결과 발견: $CACHE_DIR"
    # 캐시 유효성 검증 (7일 이내)
fi
```

**캐시 재사용 조건:**
- `--reuse-research` 플래그 사용
- 동일 도메인 해시의 캐시 존재
- 캐시 생성 후 7일 이내

#### 1.2 리서치 실행 (캐시 없거나 --skip-research 아닌 경우)

research-orchestrator 스킬을 다음 파라미터로 호출:

```yaml
research_goal: |
  "${SKILL_NAME}" 스킬 개발을 위한 도메인 조사:

  1. 핵심 분석/처리 대상
     - ${DOMAIN}에서 다루어야 할 주요 요소
     - 일반적인 구조 및 패턴

  2. Best Practices
     - 업계 표준 및 권장 사항
     - 일반적인 체크리스트 항목

  3. 기술적 제약사항
     - 필요한 도구 및 권한
     - 호환성 고려사항

  4. 검증 기준
     - 성공적인 분석/처리의 기준
     - 품질 지표

depth: quick  # 기본값, --depth로 변경 가능
type: technical
output: .research-cache/${SKILL_DOMAIN_HASH}
```

#### 1.3 리서치 결과 저장

```
.research-cache/${SKILL_DOMAIN_HASH}/
├── RESEARCH-REPORT.md
├── research-data.json
├── stages/
│   └── ...
└── meta.json  # 캐시 메타정보 (생성일, 도메인 해시 등)
```

### Checkpoint: 리서치 결과 확인

**Interactive 모드 (기본):**

```
═══════════════════════════════════════════════════════════════════
📚 리서치 완료: ${SKILL_NAME} 도메인 조사
═══════════════════════════════════════════════════════════════════

📋 주요 발견:
  - 핵심 분석 대상: ${KEY_TARGETS}
  - 발견된 Best Practices: ${BP_COUNT}개
  - 제안된 검증 항목: ${VERIFICATION_COUNT}개

📁 리서치 결과: .research-cache/${HASH}/RESEARCH-REPORT.md

이 리서치 결과를 기반으로 스킬을 생성합니다.
리서치 결과를 검토하시겠습니까? [Y/n/수정 요청]
═══════════════════════════════════════════════════════════════════
```

**사용자 응답 처리:**
- `Y` (또는 Enter): Stage 2로 진행
- `n`: Stage 2로 바로 진행 (검토 스킵)
- `수정 요청`: 추가 조사 항목 입력받아 리서치 보강

**AUTO 모드 (--auto):**
- 체크포인트 스킵, 바로 Stage 2 진행

---

### Stage 2: Context Extraction

리서치 결과에서 스킬 생성에 필요한 정보를 추출합니다.

#### 2.1 research-data.json 분석

```python
# 추출 대상
extracted = {
    "inferred_triggers": [],      # 사용 시나리오 → intent.yaml triggers
    "technical_constraints": [],  # 기술 제약 → intent.yaml constraints
    "verification_items": [],     # 검증 항목 → verification/checklist.yaml
    "suggested_phases": [],       # 실행 단계 → SKILL.md phases
    "best_practices": [],         # BP → SKILL.md 가이드
    "reference_standards": []     # 참고 표준 → references/
}
```

#### 2.2 key-insights.json 생성

```json
{
  "meta": {
    "skill_name": "${SKILL_NAME}",
    "domain": "${DOMAIN}",
    "research_date": "2024-01-15",
    "research_hash": "${HASH}"
  },
  "skill_generation_context": {
    "inferred_triggers": [
      "example trigger 1",
      "example trigger 2"
    ],
    "technical_constraints": [
      "constraint 1",
      "constraint 2"
    ],
    "verification_items": [
      {
        "id": "VER-001",
        "name": "verification item",
        "priority": "must",
        "type": "auto"
      }
    ],
    "suggested_phases": [
      {
        "name": "Phase 1 Name",
        "objective": "objective",
        "tools": ["tool1", "tool2"],
        "outputs": ["output1"]
      }
    ],
    "best_practices": [
      "best practice 1"
    ],
    "reference_standards": [
      "standard 1"
    ]
  }
}
```

---

### Stage 3: Skill Generation

intent-skill-creator를 리서치 컨텍스트와 함께 호출합니다.

#### 3.1 스킬 생성 파라미터

```yaml
skill_name: ${SKILL_NAME}
skill_domain: ${DOMAIN}
skill_type: ${TYPE}
output_dir: ${OUTPUT}/${SKILL_NAME}

# 리서치 컨텍스트 주입
research_context:
  source: .research-cache/${HASH}/key-insights.json
  apply_to:
    - triggers         # intent.yaml의 triggers 섹션
    - constraints      # intent.yaml의 constraints 섹션
    - verification     # verification/checklist.yaml
    - phases           # SKILL.md의 Phase 구조
    - best_practices   # SKILL.md의 가이드라인
```

#### 3.2 컨텍스트 적용 규칙

| 리서치 항목 | 적용 대상 | 적용 방식 |
|-------------|-----------|-----------|
| `inferred_triggers` | intent.yaml → triggers | 직접 삽입 |
| `technical_constraints` | intent.yaml → constraints.technical | 직접 삽입 |
| `verification_items` | verification/checklist.yaml | MUST/SHOULD로 분류하여 삽입 |
| `suggested_phases` | SKILL.md → Phase 섹션들 | Phase 구조 생성 |
| `best_practices` | SKILL.md → 각 Phase 가이드 | 인라인 삽입 |
| `reference_standards` | references/standards.md | 참조 문서 생성 |

#### 3.3 references/ 폴더 생성

```
${SKILL_NAME}/
├── ...
└── references/
    ├── RESEARCH-REPORT.md      # 리서치 리포트 복사
    ├── research-data.json      # 리서치 데이터 복사
    └── standards.md            # 참조 표준 문서 (생성)
```

#### 3.4 TODO 마커 최소화

리서치 컨텍스트가 적용된 항목은 TODO 대신 실제 값으로 채움:

```yaml
# Before (기존 intent-skill-creator)
triggers:
  - # TODO: 이 스킬을 트리거하는 요청 패턴

# After (리서치 컨텍스트 적용)
triggers:
  - "Kubernetes 클러스터 분석"
  - "K8s 보안 검토"
  - "클러스터 구성 점검"
  # CUSTOMIZE: 추가 트리거 패턴
```

---

## Output Structure

```
${OUTPUT_DIR}/${SKILL_NAME}/
├── intent.yaml              # 리서치 기반 상세 명세
├── SKILL.md                 # 구체화된 실행 가이드
├── schema/
│   └── output.schema.json   # 출력 스키마
├── verification/
│   ├── checklist.yaml       # 도메인 특화 검증 항목
│   └── run-verification.sh
└── references/              # 리서치 결과 포함
    ├── RESEARCH-REPORT.md
    ├── research-data.json
    └── standards.md
```

---

## Error Recovery

| Stage | Error | Cause | Action | Rollback |
|-------|-------|-------|--------|----------|
| 1 | 리서치 타임아웃 | 범위 과대 | depth를 quick으로 재시도 | 불필요 |
| 1 | 캐시 손상 | 파일 문제 | 캐시 삭제 후 재실행 | 캐시 삭제 |
| 2 | 추출 실패 | JSON 파싱 오류 | 수동 추출 또는 기본값 | 불필요 |
| 3 | 스킬 생성 실패 | 디스크/권한 | 경로 확인 후 재시도 | 스킬 폴더 삭제 |

### Rollback Commands

```bash
# 캐시 삭제
rm -rf .research-cache/${SKILL_DOMAIN_HASH}

# 생성된 스킬 삭제
rm -rf ${OUTPUT_DIR}/${SKILL_NAME}

# 전체 캐시 정리 (7일 이상)
find .research-cache -type d -mtime +7 -exec rm -rf {} +
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `ls .research-cache/` | 캐시된 리서치 목록 |
| `cat .research-cache/*/meta.json` | 캐시 메타정보 확인 |
| `grep -r "CUSTOMIZE" ${SKILL_DIR}` | 커스터마이즈 포인트 찾기 |
| `grep -r "TODO" ${SKILL_DIR}` | 남은 TODO 항목 찾기 |

### 예상 소요 시간

| Mode | Research | Total |
|------|----------|-------|
| quick (기본) | 10-15분 | 15-20분 |
| standard | 20-30분 | 25-35분 |
| --skip-research | - | 5분 |
| --reuse-research | 0분 | 5분 |
