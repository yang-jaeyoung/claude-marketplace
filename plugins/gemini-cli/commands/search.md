---
description: Google Search Grounding을 사용한 웹 검색
argument-hint: "<query>"
allowed-tools: ["Bash"]
---

# Gemini Search

Google Search Grounding을 사용하여 웹 검색을 수행합니다.

## Instructions

1. 사용자 쿼리를 arguments에서 가져옵니다
2. Gemini CLI에 웹 검색 프롬프트를 전달합니다:

```bash
gemini -p "다음 질문에 대해 웹 검색을 수행하고, 검색 결과를 기반으로 답변해주세요.
출처 URL을 반드시 포함하세요.

질문: <user_query>"
```

3. 검색 결과를 사용자에게 표시합니다

## 출력 형식

- 검색 결과 요약
- 핵심 정보
- 출처 URL 목록

## Usage Examples

```
/gemini:search jQuery 4 release date 2026
/gemini:search latest React 19 features
/gemini:search Claude Code plugins documentation
```

## Notes

- Gemini는 프롬프트에 웹 검색 요청 시 자동으로 Search Grounding 실행
- 무료 티어 1,500 쿼리/일 한도
- 실시간 정보 + LLM 분석이 동시에 필요한 경우 적합
- 복잡한 연구는 `/research` 명령과 함께 사용 권장
