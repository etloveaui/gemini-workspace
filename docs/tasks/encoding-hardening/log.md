# Task: Workspace Encoding Hardening

## Goal
- 레포 전역에서 UTF-8(Windows CRLF)로 일관되게 작업하여 한글/주석/문자열 모지바케를 방지한다.

## Changes (2025-08-15)
- `.editorconfig`: `charset=utf-8`, `end_of_line=crlf`, `insert_final_newline=true`, 탭/트레일링 공백 정책 고정.
- `.gitattributes`: `* text=auto eol=crlf`, 웹자산(`*.html, *.css, *.js, *.md, *.json`) `working-tree-encoding=UTF-8`.
- `.vscode/settings.json`: `files.encoding=utf8`, `files.eol=CRLF`, `files.autoGuessEncoding=false`.
- `scripts/ps7_utf8_profile_sample.ps1`:
  - `[Console]::OutputEncoding/InputEncoding = UTF8`
  - `$OutputEncoding = [Text.Encoding]::UTF8`
  - `Out-File/Set-Content/Add-Content` 기본 인코딩 `utf8`
  - `chcp 65001`, `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1`

## Usage
- VS Code: 창 reload/재실행 → 워크스페이스 설정 자동 반영(열린 파일은 Reopen with Encoding: UTF-8 권장).
- PowerShell 7: 새 세션에서 `. .\scripts\ps7_utf8_profile_sample.ps1` 적용.
- Git 속성: 커밋 후 체크아웃/정규화부터 효과 안정적.

## Verification Checklist
- 콘솔: `[Console]::OutputEncoding`, `[Console]::InputEncoding`가 UTF-8 인지 확인.
- 파일 라운드트립: `한글✔`을 `Out-File -Encoding utf8`로 저장 후 재열람 시 깨짐 없음.

## Notes
- Git 미추적 경로의 직접 패치는 피하고, 오버레이(임시 CSS/JS) 또는 `edits.propose`로 제안부터 진행.
- 정규식 대체로 구조 훼손 방지(컨텍스트 패치 사용).

