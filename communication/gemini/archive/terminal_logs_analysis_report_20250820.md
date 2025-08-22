# terminal_logs 분석 보고서 (2025-08-20)

## 요약
- 총 파일: 17개, 총 용량: 약 39.4 KB (40,307 bytes)
- 기간/폴더별 분포: 2025-08-13(3개/3.9 KB), 2025-08-15(11개/30.7 KB), 2025-08-17(2개/4.3 KB), 루트 단일(1개/1.3 KB)
- 유형: PowerShell Transcript(.txt), 세션 메타(JSON), 작업 요약(MD)
- 생성 패턴: VS Code/PowerShell transcript 기반(예: “PowerShell transcript start”, Host Application=VS Code PowerShell), 수동/세션 단위 저장

## 현황 분석
- 파일 수/용량
  - 2025-08-13: 3개 / 3,956 bytes
  - 2025-08-15: 11개 / 30,720 bytes
  - 2025-08-17: 2개 / 4,265 bytes
  - root: 1개 / 1,366 bytes
- 샘플 확인 결과
  - PowerShell transcript 헤더 포함, PID/PSVersion/Host Application 기록
  - 2025-08-17에는 `claude_session_*.json`(세션 메타), `claude_work_summary.md`(요약) 포함
- 생성 소스 추정
  - scripts/session_logger.py는 docs/sessions/*.md에 TL;DR 기록(terminal_logs 직접 생성 아님)
  - terminal_logs는 PowerShell transcript(또는 VS Code 통합)로 별도 수집된 로그로 보임

## 문제점
- 표준화 부재: 파일명/형식이 섞여 있음(txt/json/md).
- 로테이션 정책 부재: 보관 기간/압축 기준 미정.
- 접근성 혼선: 세션 요약은 docs/sessions, 원시 로그는 terminal_logs로 이원화.

## 정리 전략(제안)
- 보관 기준
  - 최신 14일: 원본 유지
  - 15~60일: 일자 폴더 단위 ZIP 압축 보관
  - 60일 초과: ZIP 보관 또는 삭제(보안·감사 요건에 따름)
- 파일 표준화
  - 파일명 패턴 통일: `session_YYYYMMDD_HHMMSS__agent-<name>__pid-<id>.txt`
  - 메타(JSON)와 요약(MD)은 동일 타임스탬프 접두로 매칭 가능하도록
- 저장소 슬림화
  - 대용량/장기 로그는 `archive/terminal_logs/YYYY-MM/`에 ZIP으로 이동 후 Git에는 메타만 커밋

## 자동화 권고
- 주간 로테이션(일요일 새벽)
  - 최근 14일 제외 폴더 ZIP 압축 → `archive/terminal_logs/<YYYY-MM>.zip`
  - 압축 후 원본 삭제(예외: 보관 예외 목록)
- 최소 스크립트 설계
  - PowerShell: `Compress-Archive -Path terminal_logs\2025-08-* -DestinationPath archive\terminal_logs\2025-08.zip`
  - Python(선호): 날짜 계산+압축+무결성 검사+로그 기록

## 개선안
- 로테이션 정책 문서화: `docs/setup/log_rotation.md`
- 실행 래퍼: `scripts/run_log_rotation.ps1`(권한·경로 인용 엄격)
- 접근성 통합: docs/sessions에는 요약만, terminal_logs에는 원본만, 보고서는 communication 하위 유지

## 기대 효과
- 디스크 사용량 관리 용이, 리포 비대화 완화
- 로그 접근성/가치 향상(요약/원본 역할 분리)
- 운영 자동화로 수작업 감소, 오류율 저감

## 부록: 데이터 스냅샷(2025-08-20 기준)
- 총합: 17개 / 40,307 bytes
- 분포(개수)
  - terminal_logs: 1
  - 2025-08-13: 3
  - 2025-08-15: 11
  - 2025-08-17: 2
- 분포(용량)
  - terminal_logs: 1,366 B
  - 2025-08-13: 3,956 B
  - 2025-08-15: 30,720 B
  - 2025-08-17: 4,265 B

