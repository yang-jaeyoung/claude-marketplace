# 04. Plan Mode Integration Specification

Claude Code의 기존 Plan Mode 출력을 워크플로우 플러그인에 통합하는 기능 명세.

## 1. Overview

### 1.1 목적
- Claude Code Plan Mode에서 생성된 계획을 Discovery 단계의 입력으로 활용
- 기존 도구와의 seamless 통합으로 사용자 경험 일관성 유지
- 중복 계획 수립 방지 및 워크플로우 진입 장벽 최소화

### 1.2 동작 방식
**하이브리드 접근법**: 자동 감지 + 사용자 확인
- SessionStart 시 기존 Plan Mode 계획 자동 감지
- 사용자에게 import 여부 확인 (Human-in-the-Loop)
- 승인 시 `task_plan.md` 형식으로 변환

## 2. Detection Logic

### 2.1 감지 조건
| 조건 | 설명 | 우선순위 |
|------|------|----------|
| 파일 존재 | `.claude/plan.md` 존재 여부 | 필수 |
| 최신성 | 최근 24시간 이내 수정 | 권장 |
| 브랜치 연관 | 현재 Git 브랜치와 연관된 계획 | 선택 |
| 완료 상태 | 체크박스 완료율 < 100% | 권장 |

### 2.2 감지 스크립트
```python
# skills/plan-importer/scripts/detect_plan.py

import os
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_PLAN_PATHS = [
    ".claude/plan.md",
    ".claude/plans/current.md",
    "docs/plan.md"
]

def detect_existing_plan():
    """
    Plan Mode에서 생성된 계획 파일을 감지

    Returns:
        dict: {
            "found": bool,
            "path": str,
            "modified": datetime,
            "summary": str,
            "completion_rate": float
        }
    """
    for plan_path in DEFAULT_PLAN_PATHS:
        if os.path.exists(plan_path):
            stat = os.stat(plan_path)
            modified = datetime.fromtimestamp(stat.st_mtime)

            # 24시간 이내 수정된 파일만
            if datetime.now() - modified > timedelta(hours=24):
                continue

            content = Path(plan_path).read_text()
            summary = extract_summary(content)
            completion = calculate_completion(content)

            return {
                "found": True,
                "path": plan_path,
                "modified": modified,
                "summary": summary,
                "completion_rate": completion
            }

    return {"found": False}

def extract_summary(content: str) -> str:
    """첫 번째 헤더 또는 첫 줄에서 요약 추출"""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
        if line.startswith('## '):
            return line[3:].strip()
    return lines[0][:50] if lines else "Unknown Plan"

def calculate_completion(content: str) -> float:
    """체크박스 완료율 계산"""
    total = content.count('- [ ]') + content.count('- [x]') + content.count('- [X]')
    if total == 0:
        return 0.0
    completed = content.count('- [x]') + content.count('- [X]')
    return completed / total
```

## 3. User Interaction Flow

### 3.1 프롬프트 UI
```
┌─────────────────────────────────────────────────────────┐
│  📋 기존 Plan Mode 계획이 감지되었습니다.                  │
│                                                         │
│  파일: .claude/plan.md                                  │
│  수정: 2시간 전                                          │
│  진행: ████████░░ 80% (4/5 완료)                        │
│  요약: "인증 시스템 리팩토링 - JWT → Session 전환"         │
│                                                         │
│  ────────────────────────────────────────────────────   │
│                                                         │
│  [1] 이 계획으로 워크플로우 시작                          │
│  [2] 계획 미리보기                                       │
│  [3] 새로운 작업 시작 (계획 무시)                         │
│  [4] 나중에 결정 (다음 세션까지 숨김)                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 선택지 동작
| 선택 | 동작 | 후속 단계 |
|------|------|----------|
| **[1] 계획으로 시작** | `convert_plan.py` 실행 → `task_plan.md` 생성 | Review Phase 진입 |
| **[2] 미리보기** | 계획 내용 표시 + 다시 선택 요청 | 프롬프트 재표시 |
| **[3] 새로운 작업** | 계획 무시, 일반 Discovery 시작 | Planner Agent 호출 |
| **[4] 나중에** | `.claude/plan_import_dismissed` 생성 | 일반 세션 진행 |

## 4. Plan Conversion

### 4.1 입력 형식 (Plan Mode 출력)
```markdown
## Implementation Plan

Files to modify:
- `auth/jwt.ts`
- `auth/middleware.ts`
- `lib/session.ts`

Steps:
- [ ] 1. Review current JWT implementation in `auth/jwt.ts`
- [ ] 2. Create session store interface
- [x] 3. Implement Redis session adapter
- [ ] 4. Update middleware to use sessions
- [ ] 5. Add migration script for existing tokens

Considerations:
- Backward compatibility with existing tokens
- Session expiry handling
```

### 4.2 출력 형식 (task_plan.md)
```markdown
# Task Plan: Implementation Plan

## Metadata
| Field | Value |
|-------|-------|
| **Source** | Claude Code Plan Mode |
| **Original File** | `.claude/plan.md` |
| **Imported** | 2024-01-15 14:30:00 |
| **Completion** | 20% (1/5) |

## Context Files

### Active Context
| File | Reason | Status |
|------|--------|--------|
| `auth/jwt.ts` | 명시적 언급 | 📖 Read |
| `auth/middleware.ts` | 명시적 언급 | 📖 Read |
| `lib/session.ts` | 명시적 언급 | 📝 Edit |

### Project Context (Read-Only)
- `GUIDELINES.md`
- `ARCHITECTURE.md`

## Execution Phases

### Phase 1: Analysis
| # | Step | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 1.1 | Review current JWT implementation | ⏳ Pending | Planner | `auth/jwt.ts` 분석 |

### Phase 2: Implementation
| # | Step | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 2.1 | Create session store interface | ⏳ Pending | Builder | |
| 2.2 | Implement Redis session adapter | ✅ Done | Builder | (imported as completed) |
| 2.3 | Update middleware to use sessions | ⏳ Pending | Builder | |

### Phase 3: Migration
| # | Step | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 3.1 | Add migration script | ⏳ Pending | Builder | |

## Considerations (from original plan)
- Backward compatibility with existing tokens
- Session expiry handling

## Validation Checklist
- [ ] 기존 테스트 통과
- [ ] 새 세션 관련 테스트 추가
- [ ] GUIDELINES.md 준수 확인
- [ ] Reviewer Agent 검증 완료
```

### 4.3 변환 스크립트
```python
# skills/plan-importer/scripts/convert_plan.py

import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict

def convert_plan_to_task(plan_path: str) -> str:
    """
    Plan Mode 출력을 task_plan.md 형식으로 변환
    """
    content = Path(plan_path).read_text()

    # 파싱
    title = extract_title(content)
    files = extract_files(content)
    steps = extract_steps(content)
    considerations = extract_considerations(content)

    # 단계를 Phase로 그룹화
    phases = group_steps_into_phases(steps)

    # task_plan.md 생성
    return generate_task_plan(
        title=title,
        source_path=plan_path,
        files=files,
        phases=phases,
        considerations=considerations
    )

def extract_files(content: str) -> List[str]:
    """파일 경로 추출 (백틱 내 또는 Files to modify 섹션)"""
    files = set()

    # 백틱 내 파일 경로
    backtick_pattern = r'`([^`]+\.[a-z]+)`'
    files.update(re.findall(backtick_pattern, content))

    # Files to modify 섹션
    files_section = re.search(r'Files to modify:\n((?:- .+\n)+)', content)
    if files_section:
        for line in files_section.group(1).split('\n'):
            match = re.search(r'`([^`]+)`', line)
            if match:
                files.add(match.group(1))

    return list(files)

def extract_steps(content: str) -> List[Dict]:
    """체크박스 항목 추출"""
    steps = []
    pattern = r'- \[([ xX])\] (?:\d+\. )?(.+)'

    for match in re.finditer(pattern, content):
        completed = match.group(1).lower() == 'x'
        description = match.group(2).strip()
        steps.append({
            "description": description,
            "completed": completed,
            "files": extract_files(description)
        })

    return steps

def group_steps_into_phases(steps: List[Dict]) -> List[Dict]:
    """
    단계를 논리적 Phase로 그룹화
    - 분석/리뷰 키워드 → Phase 1 (Analysis)
    - 구현/생성 키워드 → Phase 2 (Implementation)
    - 마이그레이션/배포 키워드 → Phase 3 (Migration/Deploy)
    """
    phases = {
        "Analysis": [],
        "Implementation": [],
        "Migration": []
    }

    analysis_keywords = ['review', 'analyze', 'check', 'investigate', 'understand']
    migration_keywords = ['migrate', 'deploy', 'script', 'migration']

    for step in steps:
        desc_lower = step["description"].lower()

        if any(kw in desc_lower for kw in analysis_keywords):
            phases["Analysis"].append(step)
        elif any(kw in desc_lower for kw in migration_keywords):
            phases["Migration"].append(step)
        else:
            phases["Implementation"].append(step)

    # 빈 Phase 제거
    return {k: v for k, v in phases.items() if v}

def generate_task_plan(title, source_path, files, phases, considerations) -> str:
    """task_plan.md 마크다운 생성"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ... 템플릿 기반 생성 로직 ...
    pass
```

## 5. Hook Configuration

### 5.1 hooks.json 업데이트
```json
{
  "hooks": [
    {
      "event": "SessionStart",
      "script": "skills/plan-importer/scripts/detect_plan.py",
      "timeout": 5000,
      "description": "Plan Mode 계획 자동 감지",
      "on_result": {
        "found": "prompt_plan_import",
        "not_found": "continue"
      }
    }
  ]
}
```

### 5.2 SessionStart Hook 통합
```
기존 SessionStart Hook:
  1. init_session.py (플러그인 버전 체크, GUIDELINES.md 로드)

추가:
  2. detect_plan.py (Plan Mode 계획 감지)
     └─ 발견 시: prompt_plan_import 트리거
     └─ 미발견: 일반 세션 진행
```

## 6. Skill Definition

### 6.1 SKILL.md
```markdown
# plan-importer

Claude Code Plan Mode에서 생성된 계획을 워크플로우 시스템으로 가져옵니다.

## Capabilities
- Plan Mode 출력 파일 자동 감지
- 계획을 task_plan.md 형식으로 변환
- 파일 참조 자동 추출 → Active Context 설정
- 완료된 단계 상태 보존

## Usage
자동으로 SessionStart 시 실행됩니다.
수동 호출: `/workflow:start --from-plan`

## Configuration
```yaml
plan_paths:
  - ".claude/plan.md"
  - ".claude/plans/current.md"
detection:
  max_age_hours: 24
  min_completion_rate: 0.0
  max_completion_rate: 1.0
```
```

## 7. Command Updates

### 7.1 /workflow:start 확장
```markdown
| Command | Arguments | Description |
|---------|-----------|-------------|
| `/workflow:start` | `[task description]` | 기본: 새 작업 시작 |
| `/workflow:start` | `--from-plan` | 감지된 Plan Mode 계획 import |
| `/workflow:start` | `--plan-file <path>` | 특정 계획 파일 지정 |
| `/workflow:start` | `--ignore-plan` | 기존 계획 무시하고 새로 시작 |
```

## 8. File Structure

```
skills/
└── plan-importer/
    ├── SKILL.md                    # Skill 정의
    ├── config.yaml                 # 설정 (경로, 감지 조건)
    └── scripts/
        ├── detect_plan.py          # 계획 파일 감지
        ├── parse_plan.py           # Plan Mode 형식 파싱
        ├── convert_plan.py         # task_plan.md 변환
        └── prompt_templates/
            └── import_prompt.md    # 사용자 프롬프트 템플릿
```

## 9. Edge Cases

| 상황 | 처리 방법 |
|------|----------|
| 여러 계획 파일 존재 | 가장 최근 수정된 파일 우선, 선택 UI 제공 |
| 계획 100% 완료 상태 | import 제안하되 "이미 완료됨" 표시 |
| 파싱 실패 | 원본 내용 그대로 표시 + 수동 편집 제안 |
| 계획 파일 삭제됨 | `.claude/plan_import_dismissed` 무시, 정상 세션 |
| Git 브랜치 전환 | 브랜치별 계획 분리 저장 고려 (향후) |

## 10. Future Enhancements

- [ ] 브랜치별 계획 자동 연결
- [ ] 여러 계획 파일 병합 기능
- [ ] Plan Mode ↔ task_plan.md 양방향 동기화
- [ ] 계획 버전 히스토리 관리
