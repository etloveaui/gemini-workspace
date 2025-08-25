# 20250825 토큰 사용량 요약 보고서

- 날짜: 2025-08-25
- 에이전트: Codex
- 목적: usage ∪ usage_log 일일 집계 및 건강도 점검 요약

## 요약
- 전체 이벤트: 12
- 추정 토큰 합계: 134
- 전체 상태: ok (warn>=200,000, critical>=300,000)
- 에이전트별:
  - claude: events=2, est_tokens=46, status=ok
  - codex: events=0, est_tokens=0, status=ok
  - gemini: events=0, est_tokens=0, status=ok
  - unknown: events=10, est_tokens=88, status=ok

## 유의사항
- 토큰은 문자열 길이 기반 추정치이며, 절대값은 부정확할 수 있습니다.
- 테이블이 하나라도 비어도 집계는 진행됩니다.