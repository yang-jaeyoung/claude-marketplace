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
│   └── verify-skill.md
├── schemas/
│   ├── react-project-analyzer.schema.json
│   ├── vue-project-analyzer.schema.json
│   ├── dotnet-project-analyzer.schema.json
│   ├── intent-skill-creator.schema.json
│   └── feedback-loop-event.schema.json
├── checklists/
│   ├── react-project-analyzer.yaml
│   ├── vue-project-analyzer.yaml
│   ├── dotnet-project-analyzer.yaml
│   ├── intent-skill-creator.yaml
│   └── feedback-loop.yaml
├── hooks/
│   └── hooks.json            # Stop 이벤트 훅
└── lib/
    ├── feedback_collector.py # 이벤트 수집 CLI
    └── feedback_analyzer.py  # 패턴 분석기
```

## 요구사항

- Python 3.8+ (feedback 명령어 사용 시)
- PyYAML (선택, 분석기 기능 확장)

## 라이선스

MIT
