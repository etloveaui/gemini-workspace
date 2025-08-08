# [GEMINI.cli A2] Environment Doctor & Tests
WORKDIR: C:\Users\eunta\gemini-workspace

STEPS:
1) py --version || python --version
2) pip install -r requirements.txt
3) invoke doctor
4) invoke test -q
5) invoke search -q "hello"  # 현재는 더미 Provider 적용 전이면 실패/빈출력 가능

STOP & REPORT:
- doctor 요약 (문제 항목만)
- pytest 통과/실패 요약(총/통과/실패/스킵)
- search 실행 로그(표준출력)
