# 100x Alpha Scout 게시 구조 분석 (Codex)

## 개요
- 범위: `projects/100xFenok/alpha-scout` 전반 구조 및 게시(포스팅) 흐름 파악
- 목적: RAW 데이터 → 템플릿 → 리포트 HTML → 메인(목록) 노출까지의 파이프라인 정리

## 디렉터리 구조 요약
- `alpha-scout/`
  - `alpha-scout-main.html`: 메인(목록) 페이지. fetch로 인덱스/메타데이터 로드 후 동적 렌더링
  - `alpha-scout-main_template.html`: 메인 템플릿(설계 철학/가이드 포함, placeholder 구조)
  - `data/`
    - `reports-index.json`: 최신순 리포트 목록(파일명 배열). 예: `["2025-08-24_data.json", ...]`
    - `metadata/*.json`: 메인에 노출할 요약 메타(최신 1건 featured, 나머지는 archive 카드). 필드 예: `displayDate`, `filePath`, `featuredPicks`, `archivePicks` 등
  - `reports/`
    - `YYYY-MM-DD_100x-alpha-scout.html`: 개별 리포트 결과물 HTML (정적 산출물)
    - `alpha-scout-template.html`: 개별 리포트 템플릿 (토큰 치환 방식 `@@...@@`)
    - `data/*.json`: 템플릿 치환용 데이터(시장요약, 섹터, 종목별 카드 등)
  - `_agent-prompts/`: 빌드/업데이트 절차 관련 프롬프트 문서

## 게시 파이프라인 (현재 동작 설계)
1) 데이터 준비: `reports/data/YYYY-MM-DD_data.json`에 구조화 데이터 작성
2) 리포트 생성: `alpha-scout-template.html`의 토큰(`@@FIELD@@`)을 위 JSON 값으로 치환하여 `reports/YYYY-MM-DD_100x-alpha-scout.html` 생성
3) 메타 작성: `data/metadata/YYYY-MM-DD_data.json`에 메인 노출용 요약(JSON) 작성
   - `displayDate`: "2025-08-24" 형태 표시용
   - `filePath`: `alpha-scout/reports/YYYY-MM-DD_100x-alpha-scout.html`
   - `featuredPicks`: { value|momentum|institution } 각 카드용 상세
   - `archivePicks`: { value, momentum, institution } 티커 요약
4) 인덱스 갱신: `data/reports-index.json`의 배열 맨 앞에 최신 파일명을 추가(최신 → 과거 순)
5) 메인 렌더: `alpha-scout-main.html`이
   - 인덱스 로드 → 첫 항목을 featured, 나머지를 archive로 분리
   - 각 항목에 대해 `data/metadata/*.json`을 fetch하여 카드 구성
   - 카드의 링크는 `index.html?path=alpha-scout/reports/....html` 형태로 SPA 연동

## 확인 사항 및 관찰 포인트
- `data/metadata/*.json`이 현재 저장소 상태에선 내용이 비어 있음(빈 파일). 메인에서 JSON 파싱 실패 가능성 → 운영본/로컬 빌더의 누락 또는 아직 미작성 상태로 추정
- `reports/data/*.json`은 실제 값 포함(예: 2025-08-24_data.json), 개별 리포트 HTML 생성에 충분
- 메인 템플릿/실제 메인 분리: 설계 가이드는 `*_template.html`, 실제 동작은 `alpha-scout-main.html`에서 fetch 기반 동적 렌더링

## 새 리포트 발행 체크리스트
- [ ] `reports/data/YYYY-MM-DD_data.json` 작성(데이터 일관성 확인)
- [ ] 템플릿 치환으로 `reports/YYYY-MM-DD_100x-alpha-scout.html` 생성
- [ ] `data/metadata/YYYY-MM-DD_data.json` 작성(`displayDate`, `filePath`, `featuredPicks`, `archivePicks` 등)
- [ ] `data/reports-index.json` 맨 앞에 `YYYY-MM-DD_data.json` 추가(최신 우선)
- [ ] 메인(`alpha-scout-main.html`)에서 최신 카드/아카이브 카드와 링크 확인

## 리뉴얼 논의용 제안(가이드)
- 단일 소스 빌드: RAW → 스키마 검증 → (1) 개별 리포트 HTML, (2) 메타데이터, (3) 인덱스 갱신까지 자동화하는 단일 스크립트
- 스키마 정의: `reports/data/*`와 `data/metadata/*`에 대한 JSON 스키마 명시 및 검증 추가
- 안전장치: 인덱스와 메타의 참조 경로(`filePath`) 자동 체크 및 dead link 검사
- JS 메인 보완: 메타 로드 실패 시 graceful fallback 메시지 및 로깅 강화

## 다음 단계 제안
1) 사용자가 원하는 리뉴얼 방향 상세 수령(요구 항목/디자인/데이터 확장)
2) 스키마 초안 및 빌드 스크립트 설계안 제시
3) PoC: 과거 1건 데이터를 대상으로 end-to-end 자동 생성 테스트

— Codex (2025-08-26)

