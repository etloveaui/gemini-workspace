# URGENT: 시스템 인코딩/스크립트 정리 작업 로그 (for Codex)

- 일시: 2025-08-18
- 요청 문서: `docs/tasks/URGENT_system_encoding_cleanup_for_codex.md`
- 수행 에이전트: codex

## 수행 목표
- cp949 인코딩 문제로 인한 `invoke review` 및 Git 워크플로 장애 해소
- 불필요/중복/실험적 스크립트 격리(아카이브)로 충돌 최소화
- 안전한 커밋/푸시 가능 상태 확보

## 적용 변경

1) 에이전트/설정
- `.agents/config.json`: `{"active": "codex"}`로 고정
- Git 로컬 인코딩 설정 적용(레포 스코프)
  - `git config i18n.filesEncoding utf-8`
  - `git config i18n.commitEncoding utf-8`
  - `git config core.quotepath false`
  - `git config core.autocrlf false`

2) 인코딩 크래시 방지
- `tasks.py`: Rich 출력이 cp949에서 실패할 때를 대비한 안전 출력 레이어(`_safe_console_print`) 추가하여 `invoke review` 경로 보호

3) 스크립트 정리(아카이브 이동)
- `scripts/_archive/`로 이동:
  - `scripts/encoding_check.py`
  - `scripts/error_prevention_system.py`
  - `scripts/git_push_optimizer.py`
  - `scripts/token_monitor.py`
  - `scripts/auto_update/` 전체 (scanner/proposer 포함)

4) 기타 정리/보관
- `config.json` → `scratchpad/_archive/config.json` 로 이동(미사용 설정 보관)

5) 스캐너 노이즈 축소
- (선행 작업) `scripts/auto_update/scanner.py`에 스캔 제외 디렉터리 추가(`venv`, `.git`, `.github`, `__pycache__`) — 이후 전체 auto_update는 아카이브됨

## 현재 상태 검증
- `invoke review`: cp949 환경에서도 크래시 없이 출력(안전 치환 폴백)
- `git status/diff`: 정상 출력(파일명/한글 표시 개선)
- 변경사항은 커밋 준비 완료(아래 커밋 메시지 참조)

## 커밋 메시지 제안
```
chore(utf8): set agent=codex, archive unstable scripts, add safe console printing, set repo UTF-8 git config

- Fix cp949 crash path in invoke review via safe print fallback
- Set active agent to codex in .agents/config.json
- Apply repo-local git UTF-8 settings (files/commit encoding, quotepath off)
- Archive experimental or duplicate scripts into scripts/_archive/
- Move unused root config.json to scratchpad/_archive/
```

## 추후 권장 작업(승인 필요)
- 시스템 전역 환경변수 설정: `setx PYTHONIOENCODING utf-8`, `setx PYTHONLEGACYWINDOWSFSENCODING utf-8`, 필요 시 `chcp 65001`
- 한글 깨진 문서 재작성/정정: `GEMINI.md`, `docs/HUB.md` 등 대상 확정 후 일괄 복구
- 필요 시 `invoke`의 다른 출력 경로에도 안전 출력 레이어 확대 적용

