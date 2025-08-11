# [P-AGENT] Fix Agent Watch ACK Loop - 작업 로그

## 1. 목표
- `invoke agent.watch --ack` 명령어 사용 시, `context/messages.jsonl` 파일에 중복된 ACK 메시지가 반복적으로 기록되는 버그를 해결한다.

## 2. 문제 현상
- Codex가 `agent.watch --ack`를 실행했을 때, `context/messages.jsonl`에 동일한 ACK 메시지가 수십, 수백 번 반복적으로 기록되는 현상이 발생했다.
- 이는 `agent.watch` 스크립트가 메시지를 '읽음'으로 제대로 처리하지 못하고, 동일 메시지를 계속해서 새로운 메시지로 인식하여 ACK 응답을 반복적으로 보낸 것으로 추정된다.

## 3. 원인 분석 (가설)
- `agent.watch` 내부의 메시지 처리 로직 또는 '읽음' 상태 관리 메커니즘에 결함이 있을 수 있다.
- 특히, `messages.jsonl` 파일의 `read_at` 타임스탬프 업데이트가 제대로 이루어지지 않거나, 경쟁 상태(race condition)로 인해 메시지 중복 처리가 발생할 가능성이 있다.

## 4. 해결 계획
1.  **코드 분석:** `scripts/agents/messages.py` 및 `tasks.py` 내의 `agent_watch` 관련 코드를 상세히 분석하여 버그의 정확한 원인을 파악한다.
2.  **재현 테스트:** 버그를 재현할 수 있는 최소한의 테스트 케이스를 작성한다.
3.  **수정 및 검증:** '읽음' 상태 관리 로직을 개선하고, 중복 ACK 메시지 생성을 방지하는 코드를 적용한 후, 재현 테스트를 통해 수정 사항을 검증한다.

## 5. 영향
- 이 버그는 `context/messages.jsonl` 파일의 크기를 불필요하게 증가시키고, 에이전트 간의 통신 기록을 오염시켜 디버깅 및 분석을 어렵게 만든다.
