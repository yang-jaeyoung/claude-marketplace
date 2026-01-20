---
description: "스킬 피드백을 분석하여 패턴을 감지하고 개선 제안을 생성"
argument-hint: "<skill> [--period=7]"
allowed-tools: ["Bash"]
---
# /feedback-analyze

수집된 피드백을 분석하여 반복 패턴을 감지하고 개선 제안을 생성합니다.

## 사용법

```
/feedback-analyze <skill> [--period=7]
```

## 파라미터

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| skill | O | 분석할 스킬 이름 |
| --period | X | 분석 기간 (일, 기본: 7) |

## 예시

```
/feedback-analyze vue-project-analyzer
/feedback-analyze dotnet-project-analyzer --period=14
```

## 분석 패턴

| 패턴 | 트리거 조건 | 우선순위 | 제안 조치 |
|------|------------|----------|----------|
| 반복 실패 | 동일 check_id 3회+ 실패 | HIGH | 검증 로직/가이드 수정 |
| 반복 수정 | 동일 섹션 3회+ 수정 | MEDIUM | 생성 가이드 개선 |
| 성능 이상 | 실행 시간 > 평균 + 2σ | LOW | 최적화 가이드 추가 |

## 실행 지시

다음 bash 명령을 실행하세요:

```bash
python ${CLAUDE_PLUGIN_ROOT}/lib/feedback_analyzer.py analyze "$skill" --period="${period:-7}"
```

## 출력

분석 결과를 Markdown 형식으로 출력하며 다음 내용을 포함합니다:
- 분석 기간 및 총 실행 횟수
- 반복 실패 패턴
- 반복 수정 패턴
- 성능 분석
- 개선 제안
