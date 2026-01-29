---
description: KRX 주식 데이터 수집 커맨드
---

# /krx-collect

KRX(한국거래소) 주식 데이터를 수집합니다.

## 사용법

```
/krx-collect <시장|종목코드> [시작일] [종료일] [옵션]
```

## 예시

```bash
# KOSPI 전 종목 목록
/krx-collect KOSPI

# KOSDAQ 전 종목 목록
/krx-collect KOSDAQ

# 삼성전자 1년치 가격 데이터
/krx-collect 005930 20240101 20241231

# 삼성전자 재무 지표
/krx-collect 005930 --detail

# 캐시 무시하고 새로 수집
/krx-collect KOSPI --refresh

# 시가총액 조회
/krx-collect KOSPI --marketcap
```

## 옵션

| 옵션 | 설명 |
|------|------|
| --detail | 재무 지표 포함 상세 조회 |
| --refresh | 캐시 무시 |
| --marketcap | 시가총액 조회 |

## 출력

수집된 데이터는 `.omc/quant-k/data/` 디렉토리에 Parquet 형식으로 캐시됩니다.
