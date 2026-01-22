# Intent-Based Skills Plugin

의도 기반 스킬 프레임워크 플러그인 - 복잡한 작업을 일관되고 검증 가능한 방식으로 수행합니다.

## 설치

```bash
claude plugins add github:jyyang/claude-marketplace --plugin intent-based-skills
```

## 스킬 (Skills)

### intent-skill-creator

새로운 의도 기반 스킬의 전체 구조를 자동으로 생성합니다.

**트리거**: `새 스킬 만들어줘`, `create new skill`, `scaffold skill`

**생성물**:
- `intent.yaml` - 의도 명세
- `SKILL.md` - 실행 가이드
- `schema/output.schema.json` - 출력 스키마
- `verification/` - 검증 스크립트

### feedback-loop

스킬 실행 결과를 체계적으로 수집하고 분석하여 자동으로 개선 제안을 생성합니다.

**트리거**: `feedback start`, `feedback analyze`, `스킬 피드백 분석`

**기능**:
- 실행 이벤트 수집 (start/complete/failure/correction)
- 반복 실패/수정 패턴 감지
- 개선 제안 리포트 생성

### react-project-analyzer

React 프로젝트의 구조, 컴포넌트 의존성, 상태관리, 라우팅을 분석하여 종합 문서를 생성합니다.

**트리거**: `React 프로젝트 분석`, `React 아키텍처 분석`

**분석 항목**:
- React 버전 (17.x/18.x/19.x)
- 빌드 도구 (Vite/CRA/Next.js/Remix)
- 상태관리 (Redux Toolkit/Zustand/Context API)
- 컴포넌트 분류 및 의존성 그래프
- 라우팅 구조 (React Router v7)

### vue-project-analyzer

Vue 프로젝트 구조 분석 및 문서화를 수행합니다.

**트리거**: `Vue 프로젝트 분석`, `Vue 아키텍처 분석`

### dotnet-project-analyzer

.NET 프로젝트 구조 분석 및 문서화를 수행합니다.

**트리거**: `.NET 프로젝트 분석`, `C# 아키텍처 분석`

### research-orchestrator

멀티 에이전트 기반 자동화된 연구 시스템입니다. 4단계 워크플로우를 통해 복잡한 연구 주제를 체계적으로 분석합니다.

**트리거**: `/research`, `연구 수행`, `research on`

**워크플로우**:
1. **Decomposition**: 연구 목표를 독립적인 Stage로 분해
2. **Execution**: 각 Stage를 병렬로 실행하여 Findings 수집
3. **Verification**: 모든 결과를 교차 검증하여 일관성 평가
4. **Synthesis**: 최종 연구 리포트 생성

**연구 깊이**:
- `quick`: 2-3 stages (빠른 개요)
- `standard`: 4-6 stages (기본 분석)
- `deep`: 7-10 stages (심층 연구)

**연구 유형**:
- `technical`: 기술 연구 (아키텍처, 구현, 성능)
- `academic`: 학술 연구 (이론, 방법론, 선행연구)
- `market`: 시장 조사 (경쟁사, 트렌드)
- `comparative`: 비교 분석

**출력물**:
- `RESEARCH-REPORT.md` - 최종 연구 리포트
- `research-data.json` - 구조화된 연구 데이터
- `stages/` - 각 Stage별 결과
- `validation/` - 교차 검증 결과
- `diagrams/` - Mermaid 다이어그램

## 명령어 (Commands)

### Feedback 명령어

| 명령어 | 설명 |
|--------|------|
| `/feedback-start <skill>` | 스킬 실행 피드백 수집 시작, session_id 반환 |
| `/feedback-complete <skill> <session> ...` | 실행 완료 기록 |
| `/feedback-failure <skill> <session> ...` | 검증 실패 기록 |
| `/feedback-correction <skill> <session> ...` | 사용자 수정 기록 |
| `/feedback-analyze <skill>` | 패턴 분석 |
| `/feedback-report <skill>` | 리포트 생성 |
| `/feedback-apply <skill>` | 적용 가이드 생성 |

### 검증 명령어

| 명령어 | 설명 |
|--------|------|
| `/verify-skill <skill>` | 스킬 출력물 검증 |

### Research 명령어

| 명령어 | 설명 |
|--------|------|
| `/research --goal <goal>` | 연구 수행 (기본 standard 깊이) |
| `/research --goal <goal> --depth quick` | 빠른 연구 (2-3 stages) |
| `/research --goal <goal> --depth deep` | 심층 연구 (7-10 stages) |
| `/research --goal <goal> --type market` | 시장 조사 유형 |
| `/research --goal <goal> --auto` | 자동 실행 모드 |
| `/research --resume` | 이전 연구 재개 |

## 사용 예시

### 1. 새 스킬 생성

```
새로운 analyzer 스킬을 만들어줘. 이름은 nextjs-project-analyzer로 하고, Next.js 프로젝트를 분석하는 스킬이야.
```

### 2. React 프로젝트 분석

```
이 React 프로젝트를 분석해줘
```

### 3. 피드백 수집 및 분석

```bash
# 1. 실행 시작
/feedback-start react-project-analyzer

# 2. (스킬 실행 후) 분석
/feedback-analyze react-project-analyzer

# 3. 리포트 생성
/feedback-report react-project-analyzer
```

### 4. 연구 수행

```bash
# 기술 비교 연구
/research --goal "React Server Components vs Next.js App Router 비교 분석" --type comparative --depth standard

# 시장 조사
/research --goal "2024 AI 코딩 어시스턴트 시장 분석" --type market --depth deep

# 학술 연구
/research --goal "LLM의 Reasoning 능력 평가 방법론" --type academic
```

## 디렉토리 구조

```
intent-based-skills/
├── .claude-plugin/
│   └── plugin.json          # 플러그인 메타데이터
├── skills/
│   ├── intent-skill-creator.md
│   ├── feedback-loop.md
│   ├── react-project-analyzer.md
│   ├── vue-project-analyzer.md
│   └── dotnet-project-analyzer.md
├── commands/
│   ├── feedback-start.md
│   ├── feedback-complete.md
│   ├── feedback-failure.md
│   ├── feedback-correction.md
│   ├── feedback-analyze.md
│   ├── feedback-report.md
│   ├── feedback-apply.md
│   ├── verify-skill.md
│   └── research.md              # Research Orchestrator CLI
├── schemas/
│   ├── react-project-analyzer.schema.json
│   ├── vue-project-analyzer.schema.json
│   ├── dotnet-project-analyzer.schema.json
│   ├── intent-skill-creator.schema.json
│   ├── feedback-loop-event.schema.json
│   └── research-orchestrator.schema.json  # 연구 결과 스키마
├── checklists/
│   ├── react-project-analyzer.yaml
│   ├── vue-project-analyzer.yaml
│   ├── dotnet-project-analyzer.yaml
│   ├── intent-skill-creator.yaml
│   ├── feedback-loop.yaml
│   └── research-orchestrator.yaml  # 연구 결과 검증
├── hooks/
│   └── hooks.json            # Stop 이벤트 훅
├── lib/
│   ├── feedback_collector.py # 이벤트 수집 CLI
│   ├── feedback_analyzer.py  # 패턴 분석기
│   ├── colors.py             # 크로스 플랫폼 색상 출력
│   ├── verifier_base.py      # 검증 스크립트 기본 클래스
│   └── research_orchestrator/  # 연구 오케스트레이터 라이브러리
│       ├── __init__.py
│       ├── orchestrator.py   # 메인 오케스트레이터
│       ├── models.py         # 데이터 모델
│       ├── config.py         # 설정 관리
│       ├── errors.py         # 예외 클래스
│       ├── guardrails.py     # AUTO 모드 안전장치
│       ├── verifier.py       # 결과 검증기
│       ├── agents/           # 에이전트 구현
│       ├── utils/            # 유틸리티
│       └── prompts/          # 프롬프트 템플릿
└── skills/
    └── research-orchestrator/
        └── SKILL.md          # 연구 오케스트레이터 스킬
```

## 요구사항

- Python 3.8+ (feedback 명령어 사용 시)
- PyYAML (선택, 분석기 기능 확장)

## OMC (oh-my-claudecode) 연동

intent-based-skills와 oh-my-claudecode(OMC)는 상호 보완적인 관계입니다.

### 연구 기능 비교

| 기능 | intent-based-skills `/research` | OMC `/omc:research` | CAW `/cw:research` |
|------|--------------------------------|--------------------|--------------------|
| **목적** | 범용 주제 연구 | 코드베이스 + 외부 연구 | 프로젝트 컨텍스트 기반 연구 |
| **워크플로우** | 4단계 (분해→실행→검증→합성) | Scientist 에이전트 기반 | Internal + External 연구 |
| **깊이 옵션** | quick/standard/deep | AUTO 모드 | 고정 워크플로우 |
| **출력물** | RESEARCH-REPORT.md + JSON | 자연어 응답 | .caw/ 연구 파일 |
| **검증** | 교차 검증 내장 | 선택적 | 선택적 |

### 사용 가이드

**독립 사용**: intent-based-skills의 연구 기능은 OMC 없이도 완전히 동작합니다.

**함께 사용 시**:
- **기술 비교/학술 연구**: `/research` (intent-based-skills) - 구조화된 리포트 생성
- **코드베이스 탐색 연구**: `/omc:research` - 빠른 코드 분석
- **프로젝트 문서화**: `/cw:research` - CAW 워크플로우 연계

### 에이전트 연동

OMC가 설치된 환경에서 intent-based-skills의 research-orchestrator는 OMC 에이전트를 활용할 수 있습니다:

```
[OMC 에이전트 사용 가능 시]
  Stage 실행 → omc:scientist (심층 분석)
  교차 검증 → omc:critic (비판적 검토)

[OMC 없을 시]
  기본 에이전트로 모든 기능 수행
```

## 라이선스

MIT
