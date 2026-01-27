# Clarification Question Templates

This document contains categorized question patterns for the intent-analyzer agent.
Questions are derived from best practices documented in tip1-3 files.

## Question Categories

### 1. Purpose / Goal (목적)

The most critical clarification - understanding "why" unlocks better solutions.

| Korean | English |
|--------|---------|
| 이 작업의 최종 목표는 무엇인가요? | What is the ultimate goal of this task? |
| 왜 이 변경이 필요한가요? | Why is this change needed? |
| 이 결과물을 누가 사용하나요? | Who will use this output? |
| 어떤 문제를 해결하려고 하나요? | What problem are you trying to solve? |

**Options (when applicable):**
- 버그 수정 / Bug fix
- 기능 추가 / New feature
- 리팩토링 / Refactoring
- 성능 개선 / Performance improvement
- 보안 강화 / Security enhancement
- 문서화 / Documentation

---

### 2. Target / Scope (대상/범위)

Identifying what specifically needs to be changed.

| Korean | English |
|--------|---------|
| 어떤 파일/모듈에 적용할까요? | Which file/module should this apply to? |
| 특정 함수나 클래스가 있나요? | Is there a specific function or class? |
| 전체 프로젝트인가요, 특정 부분인가요? | The entire project or a specific part? |
| 영향 범위를 알려주시겠어요? | What's the scope of impact? |

**Options (when applicable):**
- 특정 파일 / Specific file
- 특정 모듈 / Specific module
- 전체 프로젝트 / Entire project
- 이 디렉토리 내 / Within this directory

---

### 3. Criteria / Priority (기준/우선순위)

Understanding how to make trade-off decisions.

| Korean | English |
|--------|---------|
| 성능, 가독성, 보안 중 무엇이 더 중요한가요? | What matters more: performance, readability, or security? |
| 판단 기준이 있나요? | Are there specific criteria for decisions? |
| 완벽함보다 빠른 결과가 필요한가요? | Do you need quick results over perfection? |
| 장기 유지보수를 고려해야 하나요? | Should long-term maintainability be considered? |

**Options (when applicable):**
- 성능 우선 / Performance first
- 가독성 우선 / Readability first
- 보안 우선 / Security first
- 유지보수성 우선 / Maintainability first
- 빠른 구현 / Quick implementation

---

### 4. Constraints (제약 조건)

Understanding what must be included or excluded.

| Korean | English |
|--------|---------|
| 반드시 포함해야 할 것이 있나요? | Is there anything that must be included? |
| 절대 해서는 안 되는 것이 있나요? | Is there anything that must NOT be done? |
| 기술적 제약이 있나요? | Are there technical constraints? |
| 호환성 요구사항이 있나요? | Are there compatibility requirements? |

**Options (when applicable):**
- 외부 라이브러리 사용 금지 / No external libraries
- 기존 API 유지 / Keep existing API
- 특정 버전 호환 / Compatible with specific version
- 최소 변경 원칙 / Minimal changes only

---

### 5. Format / Output (형식/출력)

Understanding the desired deliverable format.

| Korean | English |
|--------|---------|
| 어떤 형식으로 결과를 원하시나요? | What format do you want for the output? |
| 코드만 필요한가요, 설명도 필요한가요? | Do you need just code, or explanation too? |
| 상세 구현인가요, 개요만 필요한가요? | Full implementation or just an overview? |
| 예시 코드가 필요한가요? | Do you need example code? |

**Options (when applicable):**
- 코드만 / Code only
- 코드 + 설명 / Code with explanation
- 개요/설계 / Overview/design
- 단계별 가이드 / Step-by-step guide

---

### 6. Context / Background (맥락/배경)

Understanding the situation around the request.

| Korean | English |
|--------|---------|
| 현재 어떤 상황인가요? | What's the current situation? |
| 이전에 시도한 방법이 있나요? | Have you tried any approaches before? |
| 관련 에러 메시지가 있나요? | Is there a related error message? |
| 기존 코드가 있나요, 새로 작성인가요? | Is there existing code, or starting fresh? |

**Options (when applicable):**
- 신규 개발 / New development
- 기존 코드 수정 / Modifying existing code
- 버그 조사 중 / Investigating a bug
- 기능 확장 / Extending functionality

---

## Usage Guidelines

### When to Ask Each Category

| Situation | Primary Categories |
|-----------|-------------------|
| "버그 수정해줘" | Context, Target, Purpose |
| "코드 개선해줘" | Purpose, Criteria, Target |
| "기능 추가해줘" | Purpose, Target, Constraints |
| "리팩토링해줘" | Criteria, Target, Constraints |
| "설명해줘" | Format, Target, Context |

### Question Limits

- **Maximum 3 questions** per interaction
- **Skip if obvious** from context
- **Combine related questions** when possible

### Prioritization

1. **Purpose** - Always ask if unclear
2. **Target** - Ask if no file/function specified
3. **Criteria** - Ask for vague verbs like "improve", "fix", "better"
4. **Others** - Ask only if critical to proceed

---

## Integration Notes

The intent-analyzer agent should:

1. Map ambiguity detector's `suggestions` array to these categories
2. Select appropriate questions from this template
3. Use AskUserQuestion tool with predefined options
4. Synthesize responses into a refined intent statement
