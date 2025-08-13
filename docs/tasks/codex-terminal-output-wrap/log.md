# [Codex] Terminal Output Width & Scrollback Wrap Fix — 작업 로그

## 배경
- 증상: Codex 응답이 터미널 가로폭의 일부만 사용되는 것처럼 보이고, PowerShell 스크롤백에서 재표시 시 줄바꿈/인코딩이 깨져 보임.
- 맥락: Codex CLI 렌더러의 래핑 + VS Code 터미널/PowerShell 출력 버퍼 및 인코딩 설정 상호작용으로 추정.

## 범위/목표
- VS Code 터미널/PowerShell 7 환경에서 Codex 출력의 가독성을 개선(불필요한 강제 줄바꿈 최소화, 스크롤 재표시시 깨짐 방지).

## 계획(초안)
1) 환경 점검 가이드 문서화: VS Code Terminal Scrollback/Word Wrap, 폰트/렌더러 옵션, PowerShell `$PSStyle.OutputRendering` 확인.
2) 출력 형식 최적화: Codex 응답에서 불필요한 빈 줄/과도한 마크업 축소, 가로폭 활용도 증대(긴 문단 우선, 리스트 최소화).
3) PowerShell 출력 버퍼/인코딩 권장 설정 정리: `$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new(false)` 권장 메모(사용자 선택 적용).
4) 회귀 검증 체크리스트: 긴 단락/리스트/코드블록 혼합 메시지 재표시 시 깨짐 없는지 육안 확인.

## Definition of Done (DoD)
- HUB에 본 태스크가 Planned로 등록됨.
- 운영 문서(AGENTS.md)에서 출력 가이드가 반영됨(있음).
- 샘플 긴 응답 표시/스크롤 재표시 테스트에서 줄깨짐/깨짐 현상 재현율 감소 보고.

## Notes
- 코어 렌더러 변경 없이 문서/응답 스타일/환경 권장 설정으로 1차 완화.
- 렌더러 수준 수정이 필요할 경우 별도 이슈로 분리 예정.

---
## Action Taken / Verification (2025-08-12)
- VS Code 스크롤백 설정 커밋: `.vscode/settings.json`에 `terminal.integrated.scrollback=50000` 추가.
- PS7 UTF-8/렌더링: 세션용(`scripts/ps7_utf8_profile_sample.ps1`), 영구 설치(`scripts/ps7_utf8_install.ps1`) 추가 및 적용.
- 사용자 확인: "스크롤 시 안 끊김" 개선 확인됨. 추가 출력 왜곡 없음.

## Status
- Completed (MVP). 추가 이슈 발생 시 재개.
