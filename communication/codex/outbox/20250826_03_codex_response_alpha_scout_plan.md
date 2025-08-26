---
agent: codex
priority: P1
status: proposed
created: 2025-08-26 13:10
---

# Codex 응답 — Alpha Scout 구조 분석 및 실행 계획

## 1) 요청 1·2 처리 결과 요약
- `projects/100xFenok` 및 `alpha-scout` 전반 구조 파악 완료.
- 게시 파이프라인 확인: `reports/data/*.json` → 템플릿 치환(개별 리포트 HTML) → `data/metadata/*.json`(메인 요약) → `data/reports-index.json`(최신순) → `alpha-scout-main.html`가 fetch로 렌더.
- 현 상태: `reports/data/*`는 채워져 있음(예: 2025-08-24), 반면 `data/metadata/*.json`은 비어 있어 메인 목록 렌더 시 실패 가능.

## 2) 메타데이터 스키마(메인에서 요구)
- `displayDate`: `YYYY-MM-DD` 표기
- `filePath`: `alpha-scout/reports/YYYY-MM-DD_100x-alpha-scout.html`
- `featuredPicks`: { value|momentum|institution → { ticker, name, description, metric:{label,value} } }
- `archiveTitle`: 아카이브 카드 제목(권장: 해당 주 헤드라인 요약)
- `archivePicks`: { value, momentum, institution } // 티커 요약

## 3) 실행 옵션 제안
1. 샘플 생성(권장): 최신 `2025-08-24` 기준으로 `data/metadata/2025-08-24_data.json` 자동 생성 → 메인 노출 검증 후 나머지 일괄 생성
2. 일괄 생성: 인덱스의 모든 항목에 대해 메타 자동 생성(규칙: value는 `valuePicks[0]`, momentum은 `momentumPicks[0]` 있으면 사용, institution은 `consensus`에서 `상향|신규` 우선 티커 선택)
3. 리뉴얼 사양 반영 후 생성: 리뉴얼 필드·카드 구성이 확정되면 그 스키마로 메타/메인 JS를 함께 조정

## 4) 샘플 메타 초안(2025-08-24)
```json
{
  "displayDate": "2025-08-24",
  "filePath": "alpha-scout/reports/2025-08-24_100x-alpha-scout.html",
  "featuredPicks": {
    "value": {
      "ticker": "NVDA",
      "name": "엔비디아",
      "description": "AI 데이터센터 GPU 선도주자",
      "metric": { "label": "Forward P/E", "value": "45.2배" }
    }
    /* momentum, institution은 원하시면 규칙에 맞춰 채웁니다 */
  },
  "archiveTitle": "파월 의장 9월 금리인하 시사, 시장 강세 마감",
  "archivePicks": { "value": "NVDA", "momentum": "", "institution": "" }
}
```

## 5) 다음 단계(선택 필요)
- [ ] 옵션 1로 진행(샘플 1건 생성 후 검증)
- [ ] 옵션 2로 진행(인덱스 전건 자동 생성)
- [ ] 옵션 3로 진행(리뉴얼 스펙 수령 후 동시 반영)

리뉴얼 구체 사양(카드 구성, 필드 확장, 페이징/정렬 규칙 등) 주시면 그 기준으로 스키마·빌더 스크립트까지 설계·구현하겠습니다.

— Codex (2025-08-26)

