---
name: stock-report
description: 주식 종합분석 리포트 생성. "삼성전자 분석해줘", "005930 종합분석" 등 자동 활성화.
argument-hint: <종목명|종목코드> [저장경로]
---

# 주식 종합분석 리포트

## 데이터 수집

```bash
# 권장: 병렬 수집 (ohlcv + fundamental + market_cap)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all "종목코드" --days 365

# 종목 검색
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" search "종목명"
```

## 워크플로우

1. **종목 식별**: search 또는 ticker_info로 코드 확인
2. **데이터 수집**: `collect_all` 실행
3. **분석**: 52주 고저가, 이동평균, 밸류에이션
4. **리포트**: Markdown 출력/저장

## ⚠️ 출력 경로 규칙

- 저장경로 지정 시 → 해당 경로에만 파일 생성
- 저장경로 미지정 → 콘솔 출력만
- **프로젝트 루트에 data/, scripts/ 등 생성 금지**

## 리포트 구조

```markdown
# {종목명} ({코드}) 종합분석

## 요약
| 현재가 | 시총 | PER | PBR | DIV |

## 1. 가격 동향
- 52주 고저가, 이동평균(20/60/120일)

## 2. 밸류에이션
- PER, PBR, EPS, BPS 분석

## 3. 투자 판단
- 기술적 분석, 매수 타이밍
```

## 에러 처리

| 상황 | 처리 |
|------|------|
| 종목 미발견 | 유사 종목 제안 |
| pykrx 미설치 | `/quant-k:setup` 안내 |
