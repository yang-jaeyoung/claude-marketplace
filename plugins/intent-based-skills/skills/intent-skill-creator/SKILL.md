---
name: intent-skill-creator
description: "This skill should be used when the user wants to create a new intent-based skill, scaffold an intent-based skill structure, or generate skill templates. Creates intent.yaml, SKILL.md, schema/, and verification/ following the intent-based skill framework. Triggers: '새 스킬 만들어줘', 'create new skill', 'scaffold skill', '분석 스킬 생성', 'generate skill template', '의도 기반 스킬 생성'."
---

# Intent Skill Creator - 의도 기반 스킬 생성기

새로운 의도 기반 스킬의 전체 구조를 자동으로 생성합니다.

## 실행 프로세스 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                    SKILL CREATION PROCESS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. INPUT COLLECTION                                            │
│     └─ 스킬 이름, 도메인, 유형 수집                              │
│     └─ 출력 형식 결정                                           │
│                                                                 │
│  2. TEMPLATE SELECTION                                          │
│     └─ 스킬 유형에 맞는 템플릿 선택                              │
│     └─ analyzer / generator / documenter / etc.                 │
│                                                                 │
│  3. FILE GENERATION                                             │
│     └─ intent.yaml 생성                                         │
│     └─ SKILL.md 생성                                            │
│     └─ schema/output.schema.json 생성                           │
│     └─ verification/ 파일들 생성                                │
│                                                                 │
│  4. VALIDATION & GUIDANCE                                       │
│     └─ 생성된 파일 검증                                         │
│     └─ 커스터마이즈 가이드 제공                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: 의도 명확화 (선택적)

사용자 입력이 모호할 때 추가 질문을 통해 의도를 명확히 합니다.

### 전략별 동작

| 전략 | 동작 |
|------|------|
| `always` | 모든 required 질문 순차 진행 |
| `adaptive` | 모호성 감지 시에만 질문 (기본값) |
| `minimal` | 필수 정보 누락 시에만 질문 |
| `skip` | 질문 없이 기본값 사용 |

### 모호성 판단 기준

| 상황 | 판단 | 행동 |
|------|------|------|
| skill_name만 있음 | 모호 | skill_domain 질문 |
| "분석 스킬" 요청 | 부분 명확 | 대상(TARGET) 질문 |
| 전체 정보 있음 | 명확 | Phase 1로 진행 |

### 질문 실행 흐름

```
1. skip_conditions 확인
   └─ 모두 만족 → Phase 1로 진행

2. required 질문 처리 (strategy=always 또는 값 누락 시)
   └─ 응답을 input에 매핑 (maps_to)

3. disambiguation 처리 (trigger_pattern 매칭 시)
   └─ 추가 정보 수집

4. conditional 질문 처리 (조건 만족 시)
   └─ 선택적 정보 수집

5. limits 확인 (max_questions, max_rounds 초과 시 중단)
```

---

## Phase 1: 입력 수집 (1분)

### 필수 정보 확인

사용자에게 다음 정보를 확인하거나 요청에서 추출:

| 항목 | 필수 | 예시 |
|------|------|------|
| **skill_name** | ✅ | `react-project-analyzer` |
| **skill_domain** | ✅ | `React 프로젝트 구조 분석 및 문서화` |
| skill_type | 선택 | `analyzer` / `generator` / `documenter` |
| input_type | 선택 | `directory` / `file` / `data` |
| output_formats | 선택 | `["markdown", "json", "mermaid"]` |

### 스킬 유형 자동 판별

요청에서 키워드로 유형 추론:

| 키워드 | 스킬 유형 |
|--------|----------|
| 분석, analyze, 파악, 구조 | `analyzer` |
| 생성, generate, 만들기, create | `generator` |
| 문서화, document, 정리 | `documenter` |
| 변환, convert, transform, 마이그레이션 | `transformer` |
| 검증, validate, 체크, lint | `validator` |

### 입력 검증

```bash
# 스킬 이름 형식 검증 (kebab-case)
echo "$SKILL_NAME" | grep -qE "^[a-z][a-z0-9-]*$" || echo "ERROR: Invalid skill name"

# 출력 디렉토리 확인
mkdir -p "$OUTPUT_DIR"
```

---

## Phase 2: 템플릿 선택 (1분)

### 스킬 유형별 구조

#### Analyzer 유형
```
분석 대상 → 구조 파악 → 상세 분석 → 문서/리포트 생성
```
- 출력: ARCHITECTURE.md, analysis-data.json, diagrams/

#### Generator 유형
```
입력/설정 → 템플릿 선택 → 코드/문서 생성 → 검증
```
- 출력: 생성된 파일들, generation-report.json

#### Documenter 유형
```
소스 수집 → 정보 추출 → 구조화 → 포맷팅
```
- 출력: README.md, API-DOCS.md, *.html

#### Transformer 유형
```
입력 파싱 → 변환 규칙 적용 → 출력 생성 → 검증
```
- 출력: 변환된 파일들, transformation-log.json

#### Validator 유형
```
대상 로드 → 규칙 적용 → 결과 집계 → 리포트
```
- 출력: validation-report.md, validation-results.json

---

## Phase 3: 파일 생성 (2분)

### 생성할 디렉토리 구조

```
{skill_name}/
├── intent.yaml              # 의도 명세
├── SKILL.md                 # 실행 가이드
├── schema/
│   └── output.schema.json   # 출력 스키마
├── verification/
│   ├── checklist.yaml       # 검증 체크리스트
│   └── run-verification.sh  # 자동 검증 스크립트
├── scripts/                 # (선택) 헬퍼 스크립트
├── templates/               # (선택) 템플릿 파일
└── references/              # (선택) 참고 자료
```

### 파일 생성 알고리즘

```
1. 디렉토리 구조 생성
   mkdir -p {skill_name}/{schema,verification}

2. 템플릿 선택 (skill_type 기반)
   ├─ analyzer  → templates/types/analyzer.intent.yaml.template
   ├─ generator → templates/types/generator.intent.yaml.template
   ├─ documenter→ templates/types/documenter.intent.yaml.template
   ├─ transformer→templates/types/transformer.intent.yaml.template
   ├─ validator → templates/types/validator.intent.yaml.template
   └─ custom    → templates/intent.yaml.template

3. 플레이스홀더 치환 순서
   a. 공통: {{SKILL_NAME}}, {{SKILL_TYPE}}, {{DATE}}, {{AUTHOR}}
   b. 유형별: {{TARGET}}, {{SOURCE_TYPE}}, {{OUTPUT_TYPE}}
   c. Phase별: {{PHASE_N_NAME}}, {{PHASE_N_DURATION}}
   d. Clarification: {{CLARIFICATION_STRATEGY}}

4. 파일 생성 순서 (의존성 기반)
   [1] intent.yaml       (다른 파일의 기준)
   [2] output.schema.json (intent.yaml 참조)
   [3] SKILL.md          (execution_hints 참조)
   [4] checklist.yaml    (intent.yaml 참조)
   [5] run-verification.sh (checklist.yaml 참조)

5. 권한 설정
   chmod +x verification/run-verification.sh
```

### 3.1 intent.yaml 생성

**반드시 포함할 섹션:**

```yaml
meta:
  name: {skill_name}
  version: "1.0.0"
  description: "{skill_domain}"
  tags: [...]

intent:
  goal: |
    # TODO: 이 스킬의 최종 목표를 명확히 기술
  triggers:
    - # TODO: 이 스킬을 트리거하는 요청 패턴
  non_goals:
    - # TODO: 이 스킬이 하지 않는 것
  success_criteria:
    - # TODO: 성공 기준

input:
  required:
    - name: # TODO
      type: # TODO
      description: # TODO
      constraints: []
  optional: []

output:
  artifacts:
    - name: # TODO
      type: file
      format: # TODO
      path: # TODO
      required_sections: []

constraints:
  quality: []
  performance:
    max_execution_time: # TODO

verification:
  pre_conditions: []
  post_conditions: []
  checklist: []

execution_hints:
  phase_order: []
  best_practices: []
```

### 3.2 SKILL.md 생성

**YAML Frontmatter (Claude Code 스킬 형식):**

```yaml
---
name: {skill_name}
description: "This skill should be used when the user wants to {use_case}. {skill_domain} Triggers: '{trigger1}', '{trigger2}'."
---
```

> **중요**: `description`은 반드시 "This skill should be used when..."으로 시작하고, 마지막에 `Triggers:`로 트리거 키워드를 포함해야 합니다.

**필수 구조:**

```markdown
---
name: {skill_name}
description: "This skill should be used when the user wants to {use_case}. {description} Triggers: '{triggers}'."
---

# {Skill Title}

{한 줄 설명}

## 실행 프로세스

[프로세스 다이어그램]

## Phase 1: {첫 번째 단계}
### 목적
### 실행 명령어
### 수집/확인 항목

## Phase 2: {두 번째 단계}
...

## Phase N: 검증

### 자동 검증
```bash
bash verification/run-verification.sh <args>
```

### 체크리스트
- [ ] MUST 항목들
- [ ] SHOULD 항목들

## 오류 복구

| 상황 | 조치 |
|------|------|
```

### 3.3 schema/output.schema.json 생성

**기본 구조:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "{skill_name}/output",
  "title": "{Skill Output Schema}",
  "type": "object",
  "required": ["meta"],
  "properties": {
    "meta": {
      "type": "object",
      "required": ["generated_at", "skill_version"],
      "properties": {
        "generated_at": { "type": "string", "format": "date-time" },
        "skill_version": { "type": "string" }
      }
    }
    // TODO: 도메인 특화 속성 추가
  }
}
```

### 3.4 verification/checklist.yaml 생성

**기본 구조:**

```yaml
version: "1.0"

pre_execution:
  - id: PRE-001
    name: # TODO
    validation: auto
    script: |
      # TODO
    priority: must

post_execution:
  files:
    - id: FILE-001
      name: # TODO
      validation: auto
      script: |
        # TODO
      priority: must
  
  content:
    - id: CONTENT-001
      name: # TODO
      validation: auto
      script: |
        # TODO
      priority: should
  
  accuracy:
    - id: ACCURACY-001
      name: # TODO
      validation: manual
      guidance: |
        # TODO
      priority: should
```

### 3.5 verification/run-verification.sh 생성

**기본 구조:**

```bash
#!/bin/bash
# {skill_name} - Verification Runner

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 인자 파싱
# TODO: 스킬에 맞는 인자 정의

# 검증 함수
run_check() {
    local id="$1"
    local name="$2"
    local priority="$3"
    local script="$4"
    # ... 검증 로직
}

# 사전 조건 검증
echo "=== 사전 조건 검증 ==="
# TODO: 사전 조건 체크

# 출력 검증
echo "=== 출력 검증 ==="
# TODO: 출력 파일 체크

# 결과 요약
echo "=== 검증 결과 ==="
# TODO: 요약 출력
```

---

## Phase 4: 검증 및 가이드 (1분)

### 생성 파일 검증

```bash
# 모든 필수 파일 존재 확인
test -f "$OUTPUT_DIR/intent.yaml"
test -f "$OUTPUT_DIR/SKILL.md"
test -f "$OUTPUT_DIR/schema/output.schema.json"
test -f "$OUTPUT_DIR/verification/checklist.yaml"
test -f "$OUTPUT_DIR/verification/run-verification.sh"

# YAML/JSON 유효성 검증
python3 -c "import yaml; yaml.safe_load(open('$OUTPUT_DIR/intent.yaml'))"
python3 -c "import json; json.load(open('$OUTPUT_DIR/schema/output.schema.json'))"

# 실행 권한 부여
chmod +x "$OUTPUT_DIR/verification/run-verification.sh"
```

### 커스터마이즈 가이드 제공

생성 완료 후 사용자에게 안내:

```
✅ 스킬 생성 완료: {skill_name}

📁 생성된 파일:
   {output_dir}/
   ├── intent.yaml
   ├── SKILL.md
   ├── schema/output.schema.json
   └── verification/

🔧 다음 단계 (커스터마이즈 필요):

1. intent.yaml 수정
   - TODO 마커 검색하여 도메인 특화 내용 추가
   - triggers, constraints, verification 항목 구체화

2. SKILL.md 수정
   - Phase별 구체적인 실행 명령어 추가
   - 도메인 특화 가이드 작성

3. schema/output.schema.json 수정
   - 출력 데이터 구조 정의
   - 필수 필드 및 타입 명시

4. verification/ 수정
   - 도메인 특화 검증 항목 추가
   - 자동 검증 스크립트 완성

5. 테스트
   - 실제 입력으로 스킬 실행
   - 검증 스크립트 실행
```

---

## 스킬 유형별 템플릿 예시

### Analyzer 템플릿 (intent.yaml 핵심 부분)

```yaml
intent:
  goal: "{대상}의 전체 구조를 파악하고 문서화한다"
  triggers:
    - "{대상} 분석"
    - "{대상} 구조 파악"
    - "{대상} 아키텍처 문서화"

input:
  required:
    - name: project_path
      type: directory
      description: "분석할 {대상} 경로"

output:
  artifacts:
    - name: architecture_document
      format: markdown
      path: "{output_dir}/ARCHITECTURE.md"
    - name: analysis_data
      format: json
      path: "{output_dir}/analysis-data.json"
    - name: diagrams
      format: mermaid
      path: "{output_dir}/diagrams/"

execution_hints:
  phase_order:
    - name: "진입점 파악"
    - name: "구조 분류"
    - name: "상세 분석"
    - name: "문서 생성"
```

### Generator 템플릿 (intent.yaml 핵심 부분)

```yaml
intent:
  goal: "{입력}을 기반으로 {출력}을 자동 생성한다"
  triggers:
    - "{출력} 생성"
    - "{출력} 만들어줘"

input:
  required:
    - name: source
      type: file
      description: "생성 소스"
    - name: template
      type: enum
      values: [...]
      description: "사용할 템플릿"

output:
  artifacts:
    - name: generated_files
      type: directory
      path: "{output_dir}/generated/"
    - name: generation_report
      format: json
      path: "{output_dir}/generation-report.json"

execution_hints:
  phase_order:
    - name: "입력 파싱"
    - name: "템플릿 적용"
    - name: "파일 생성"
    - name: "검증"
```

---

## 오류 복구

### Phase별 오류 및 복구

| Phase | 오류 | 원인 | 조치 | 롤백 |
|-------|------|------|------|------|
| 0 | 질문 응답 없음 | 사용자 무응답 | 기본값 사용 | 불필요 |
| 1 | 스킬 이름 형식 오류 | 공백/특수문자 | kebab-case 변환 제안 | 불필요 |
| 1 | 동일 이름 스킬 존재 | 중복 | 덮어쓰기 확인 또는 버전 suffix | 불필요 |
| 2 | 템플릿 파일 없음 | 경로 오류 | 기본 템플릿 사용 | 불필요 |
| 3 | YAML 구문 오류 | 템플릿 문제 | 구문 수정 후 재생성 | 파일 삭제 |
| 3 | JSON 구문 오류 | 템플릿 문제 | 구문 수정 후 재생성 | 파일 삭제 |
| 3 | 디스크 공간 부족 | 시스템 | 공간 확보 후 재실행 | 디렉토리 삭제 |
| 4 | 검증 실패 | 구조 불완전 | 수동 수정 가이드 | 불필요 |

### 롤백 명령어

```bash
# 전체 롤백
rm -rf "$SKILL_DIR"

# 특정 파일 재생성
rm "$SKILL_DIR/intent.yaml" && # Phase 3.1 재실행
```

### 일반 오류 조치

| 상황 | 조치 |
|------|------|
| 스킬 이름 형식 오류 | kebab-case로 변환 제안 |
| 동일 이름 스킬 존재 | 덮어쓰기 확인 또는 새 이름 제안 |
| 출력 디렉토리 권한 없음 | 다른 경로 제안 또는 권한 안내 |
| 참조 스킬 없음 | 기본 템플릿 사용 |

---

## Quick Reference

| 명령 | 용도 |
|------|------|
| `grep -r "TODO" {skill_dir}` | 커스터마이즈 포인트 찾기 |
| `python3 -c "import yaml; ..."` | YAML 검증 |
| `python3 -c "import json; ..."` | JSON 검증 |
| `chmod +x *.sh` | 스크립트 실행 권한 |
