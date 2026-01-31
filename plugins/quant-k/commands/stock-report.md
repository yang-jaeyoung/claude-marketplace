---
description: 주식 종합분석 리포트 생성. 종목명 또는 종목코드로 분석 요청.
argument-hint: <종목명|종목코드> [저장경로]
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
---

# 주식 종합분석 리포트

종목의 종합분석 리포트를 생성합니다.

## 분석 순서

1. **종목 확인**: 종목명/코드 검색
2. **데이터 수집**: OHLCV, 펀더멘털, 시총
3. **팩터 분석**: PER, PBR, 모멘텀, ROE
4. **유사 종목**: 시총/PER 유사 10개
5. **리포트 생성**: Markdown 형식

## 필수 명령어

```bash
# 종목 검색
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" search "종목명"

# 데이터 수집 (병렬)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all "종목코드" --days 365
```

⚠️ **절대 경로 필수!** 상대 경로(`scripts/...`) 사용 금지

## 사용 예시

```bash
/stock-report 동운아나텍
/stock-report 094170 report/
```

## 리포트 구조

```markdown
# {종목명} ({종목코드}) 종합분석

## 요약
- 현재가, 시총, PER/PBR, 투자의견

## 1. 기본 정보
## 2. 가격 동향
## 3. 밸류에이션 분석
## 4. 팩터 분석
## 5. 유사 종목 비교
## 6. 매수 타이밍 분석
## 7. 투자 의견 요약
```
