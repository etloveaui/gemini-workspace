---
agent: codex
type: requirements_summary
created: 2025-08-26
source: communication/codex/20250826_01_prompt.md
---

# 100x Alpha Scout — 사용자 요구사항 정리

## 제공 자료(단일 소스)
- RAW HTML 6개: `communication/shared/100xalpha/`
  - 01_AI_Hardware_Screening.html
  - 02_AI_Software_Screening.html
  - 03_AI_Big_Screening.html
  - 04_AI_Startup_Emerging_Screening.html
  - 05_AI_Infra_Screening.html
  - 06_Healthcare_Screening.html

## 핵심 요구
- 6개의 RAW HTML 각각을 “알파 스카우트” 리포트로 변환.
- 기존보다 “더 예쁜” 단일 공통 템플릿이 필요.
- 6개 모두를 포괄할 수 있는 JSON 산출 방식(스키마/출력 규칙)이 필요.
- 메타데이터 산출(요약·링크 등)도 새 구조에 맞게 변경.
- 메인 페이지도 새 구조에 맞춰 일부 수정 필요.
- 브리핑/계획은 쉽게 설명할 것.
- 컨텍스트(용량) 65% 이슈가 있으면 자동 압축 지원(불가 시 사용자가 처리).

## 제약/가이드
- 시스템 핵심 파일 수정 금지, `communication/`와 `projects/` 내에서만 작업.
- 프로젝트 독립성 준수(각 프로젝트는 독립 Git, 루트에 병합 금지).
- 모든 산출물·소통은 한국어.

## 산출물 기대치(요약)
- 새 템플릿(공통) 1종.
- RAW → JSON 변환 규칙 및 결과(6건).
- 수정된 메타 데이터 산출(6건).
- 메인 페이지(아카이브/피처드) 수정안.

## 상태
- 100xFenok 내 임시 V2 작업물은 사용자 지시에 따라 전량 삭제 완료.
- 다음 단계는 위 요구에 맞춘 설계/구현 재개 지시 대기.

