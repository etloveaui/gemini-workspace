# 2025-08-22 Codex 킥오프 노트 (세션 01)

- 목적: 멀티 에이전트 협업 세션 가동 및 초기 정렬
- 네이밍 규칙: yyyymmdd_01_xxx 적용 (본 파일 포함)
- 언어: 한국어 고정

## 체크리스트 상태
- [ ] docs/CODEX_CHECKLIST.md 확인
- [ ] docs/HUB.md 확인 및 오늘의 우선순위 동기화
- [ ] docs/AGENT_COMMUNICATION_SYSTEM.md 확인
- [ ] communication/shared/COMMUNICATION_GUIDE.md 확인
- [ ] scripts/watch_file.py 워처 설정 검토

(참고: 현재 자동 쉘 열람 제약으로 문서 확인은 보류됨. 파일 경로 확인 또는 접근 권한 제공 시 즉시 갱신 예정)

## 커뮤니케이션 채널(파일 기반)
- 발신/응답: `communication/codex/` 폴더 하위 yyyymmdd_XX_*.md
- 공용 가이드: `communication/shared/COMMUNICATION_GUIDE.md`
- 워처: `scripts/watch_file.py` (실시간 파일 변경 감지)

## 오늘의 실행 계획(초안)
1) 체크리스트/HUB 내용으로 작업 큐 정렬(P1/P2)  
2) 필요한 스크립트/도구 점검 및 venv 경로 확정  
3) 우선 과제 구현/테스트 → 결과 보고  
4) 문서 업데이트 및 다음 액션 큐 등록

## 환경 메모(Windows + Python)
- 기본 파이썬: `python` 또는 `py -3`
- 가상환경 생성: `python -m venv venv`
- 파이썬 경로: `venv\\Scripts\\python.exe`
- pip 업그레이드: `venv\\Scripts\\python.exe -m pip install -U pip`

## 협업 규칙 반영
- 프로젝트 독립성: `projects/` 하위는 독립 Git, 루트 Git에서 제외
- 보안: 비밀정보 하드코딩 금지, 입력 검증 필수
- 품질: 정확성 → 성능 → 가독성 → 유지보수성 → 테스트 가능성

## 요청 사항
- [ ] 워크스페이스 파일 구조 확인 권한(또는 경로 안내)
- [ ] 오늘 우선 과제 지정(없으면 HUB 우선순위 기준 진행)
- [ ] 타 에이전트(Claude/Gemini) 할당 필요 시 지시

— Codex 드림
