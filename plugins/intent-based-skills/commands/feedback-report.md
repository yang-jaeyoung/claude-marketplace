---
description: "스킬 피드백 분석 리포트를 생성"
argument-hint: "<skill> [--format=md|json]"
allowed-tools: ["Bash"]
---
# /feedback-report

스킬 피드백 분석 리포트를 생성합니다.

## 사용법

```
/feedback-report <skill> [--format=md|json]
```

## 파라미터

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| skill | O | 리포트 대상 스킬 이름 |
| --format | X | 출력 형식 (md 또는 json, 기본: md) |

## 예시

```
/feedback-report vue-project-analyzer
/feedback-report dotnet-project-analyzer --format=json
```

## 리포트 내용

### Markdown 형식 (기본)

```markdown
# {skill_name} 피드백 분석 리포트

**분석 기간**: YYYY-MM-DD ~ YYYY-MM-DD
**총 실행**: N회

## 반복 실패 패턴
| Check ID | 이름 | 실패 횟수 | 우선순위 |
|----------|------|----------|----------|
| ... | ... | ... | ... |

## 반복 수정 패턴
| 파일 | 섹션 | 수정 횟수 |
|------|------|----------|
| ... | ... | ... |

## 성능 분석
- 평균 실행 시간: X.Xs
- 표준 편차: X.Xs
- 이상 감지: N건

## 개선 제안
1. [HIGH] ...
2. [MEDIUM] ...
```

## 실행 지시

다음 bash 명령을 실행하세요:

```bash
python ${CLAUDE_PLUGIN_ROOT}/lib/feedback_analyzer.py report "$skill" --format="${format:-md}"
```

## 저장 위치

리포트는 `~/.claude/feedback/reports/{skill}/report-{date}.md`에 저장됩니다.
