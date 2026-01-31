---
description: KRX-Quant Ultra 분석 모드. 모든 기능을 최대 역량으로 활용한 심층 분석.
argument-hint: <종목명|종목코드> [저장경로]
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - Task
  - WebFetch
---

# KRX-Quant Ultra 분석 모드

**상세 실행 지침:** `skills/ultra-analyze/SKILL.md` 참조

## 자동 활성화 키워드

`울트라`, `ultra`, `딥 분석`, `전체 분석`, `심층 분석`

## 실행 요약

| Phase | 작업 | 도구 |
|-------|------|------|
| 1 | KRX 데이터 수집 | Bash (collect_all) |
| 2-4 | 에이전트 병렬 실행 | **Task (필수)** |
| 5 | 기술분석 | 직접 |
| 6 | 리포트 생성 | Write |

## 사용 예시

```bash
/ultra-analyze 동운아나텍
/ultra-analyze 094170 report/
```

## vs 일반 분석

| 항목 | stock-report | ultra-analyze |
|------|--------------|---------------|
| 가격 데이터 | 1년 | 1년 |
| 팩터 | 6개 | 15개 |
| 유사 종목 | 10개 | 20개+ |
| 웹 스크래핑 | 없음 | 포함 |
| 리포트 | 단일 파일 | 디렉토리 구조 |
