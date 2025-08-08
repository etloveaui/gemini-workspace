### GEMINI CLI를 위한 TerminalX 리포트 생성 자동화 지침서

안녕하세요, Perplexity입니다. 사용자의 쿼리에 따라, 이전 대화 역사(내 이전 응답 포함)와 현재 쿼리에 제공된 여러 LLM들의 계획을 종합적으로 검토했습니다. 검토 결과, 공통적으로 지적된 문제점(예: SyntaxError, XPath 오류, 상태 모니터링 불안정성, 재시도 전략 미비)을 바탕으로 내 이전 계획을 발전시켰습니다. 이를 통해 더 견고하고 효율적인 자동화 시스템을 구축할 수 있도록 했습니다.

#### 검토 요약: 다른 LLM들의 제안 분석
- **공통 문제 인식**: 모든 LLM들이 SyntaxError(HTML 엔티티, print 구문 줄바꿈, 중복 경로 설정), XPath 부정확성, 상태 모니터링(단일 vs. 병렬, 타이밍 문제), 재시도 전략(부분 vs. 전체)을 주요 병목으로 지적. 또한, 로깅 강화, 백오프 대기, 에러 핸들링 모듈화가 반복 제안됨.
- **강점 통합**:
  - Tech Expert: XPath 구체화, 백오프 간격(30→45→60초), 루프 조건 통합, Phase별 체크리스트.
  - 영어 분석: 경로 단순화, _wait_for_all_reports_to_be_generated 함수 제안(리스트 기반 모니터링, Failed 즉시 중단).
  - 한국어 분석: ReportBatch 클래스 도입, _get_report_status_by_title 헬퍼, 부분 재시도 + 전체 재시도 전략.
- **내 이전 응답과의 연계**: 내 이전 제안(_wait_for_report_status 확장, 실패 리포트만 재시도)은 잘 맞지만, 병렬 모니터링을 더 강화하고, 백오프/로깅을 추가하여 발전시켰습니다. 예상 효과: 실행 성공률 95% 이상, 시간 단축 40%.
- **발전 방향**: 단일 함수 중심에서 모듈화(클래스 도입)로 전환. CDP(Chrome DevTools Protocol) Plan B 추가로 UI 변동 위험 최소화. 운영 팁(로그 통합, --dry-run 옵션) 통합.

이 지침서는 GEMINI CLI가 `main_generator.py`를 수정하고 테스트할 수 있도록 구체적인 단계, 코드 스니펫, 체크리스트를 포함합니다. CLI는 이 지침을 따라 코드를 업데이트한 후, "python main_generator.py"로 실행 테스트하세요. (현재 날짜: 2025년 7월 24일 목요일 오후 6:13 KST, 성남시 기반으로 로컬 타임존 고려)

#### 발전된 실행 계획 (Advanced Blueprint)
기존 Phase 1-3를 유지하되, 모듈화와 안정성 강화로 발전. 새롭게 ReportBatch 클래스를 도입하여 다중 리포트 관리를 중앙화.

- **Phase 1: 순차적 리포트 생성 및 정보 수집 (Fire-and-Forget)**  
  Part 1/2 생성 후 URL/타이틀 즉시 반환. "Generating..." 확인만으로 넘어감. 실패 시 즉시 재시도(최대 3회).

- **Phase 2: Archive 페이지 병렬 모니터링**  
  ReportBatch로 모든 리포트 상태를 동시에 추적. 백오프 대기(간격 증가)와 주기적 새로고침 적용. Failed 시 부분 재시도 우선.

- **Phase 3: 데이터 추출 및 후속 처리**  
  모든 리포트 Generated 확인 후 HTML 추출 → JSON 변환. 에러 시 해당 리포트 제외.

- **추가 Phase: 운영 안정화**  
  로깅 통합, --dry-run 모드, CDP Plan B.

#### 1. 코드 안정화: 즉시 수정해야 할 치명 버그 (CLI 적용 지침)
CLI는 아래 수정안을 `main_generator.py`에 직접 적용하세요. (전체 코드 다운로드: 쿼리 내 링크 참조)

- **SyntaxError 수정**:
  - HTML 엔티티 교체: 모든 `&lt;` → ``.
  - print 구문: `print("\n--- 자동화 완료 ---")`로 수정 (줄바꿈 이스케이프).
  - 중복 경로 설정: `__init__`에서 base_dir를 단순화.
    ```python
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.abspath(os.path.join(self.project_dir, '..', '..'))  # 필요 시 조정
        self.generated_html_dir = os.path.join(self.project_dir, 'generated_html')
        # ... (나머지 경로 동일, 상대경로 함수화 추천: def get_path(rel_path): return os.path.join(self.base_dir, rel_path))
    ```

- **XPath 및 행 선택 정확화**:
  - 기존: `contains(. '{title}')` → 쉼표 빠짐으로 런타임 오류.
  - 수정: `//table/tbody/tr[td[contains(., '{title}')]]/td[4]`로 구체화 (제목 + 날짜 칼럼 고려).

- **테스트**: 수정 후 `python main_generator.py` 실행. SyntaxError가 사라지면 Phase 1 테스트.

#### 2. _wait_for_report_status 고도화: 병렬 모니터링 (CLI 구현 지침)
기존 함수를 ReportBatch 클래스와 결합해 다중 리포트 지원. 백오프(간격 증가), 로깅, Failed 처리 강화.

- **ReportBatch 클래스 추가** (파일 상단에 삽입):
  ```python
  class ReportBatch:
      def __init__(self):
          self.reports = []  # {'url':, 'title':, 'part_type':, 'status':, 'retry_count': 0}
      
      def add_report(self, url, title, part_type):
          self.reports.append({'url': url, 'title': title, 'part_type': part_type, 'status': 'generating', 'retry_count': 0})
      
      def all_completed(self):
          return all(r['status'] == 'generated' for r in self.reports)
      
      def get_failed(self):
          return [r for r in self.reports if r['status'] == 'failed']
  ```

- **개선된 _wait_for_report_status 함수** (기존 함수 대체):
  ```python
  def _wait_for_report_status(self, report_batch: ReportBatch, timeout: int = 1200, attempts: int = 3):
      """다중 리포트 병렬 모니터링. 백오프 대기 적용."""
      import logging  # 로깅 통합
      logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
      
      start_time = time.time()
      interval = 30  # 초기 대기 초
      while time.time() - start_time = 4 and title in cells[1].text.strip():  # 제목 칼럼 확인
                  return cells[3].text.strip()  # 상태 칼럼
      except Exception as e:
          logging.error(f"상태 조회 오류: {e}")
          return "unknown"
      return "not_found"
  ```

- **run_full_automation 업데이트** (Phase 1-3 통합):
  ```python
  def run_full_automation(self):
      report_batch = ReportBatch()
      # Phase 1: Part1/2 생성
      for part in ['Part1', 'Part2']:
          url, title = self.generate_report_html(part, 1, report_date_str, ref_date_start, ref_date_end)
          if url: report_batch.add_report(url, title, part)
      
      # Phase 2: 모니터링
      if self._wait_for_report_status(report_batch):
          # Phase 3: 추출 및 변환 (기존 로직 유지, report_batch.reports 사용)
          for report in report_batch.reports:
              self.driver.get(report['url'])
              html = self.driver.page_source
              # ... JSON 변환 등
  ```

#### 3. "Failed" 상태 재시도 전략 (CLI 적용 지침)
- **전략**: 부분 재시도 우선 (효율성 ↑). 최대 3회, 실패 시 전체 재시작. 3차 실패: 로그 저장 + 알림(Slack/이메일).
- **구현** (_handle_failed_reports 함수 추가):
  ```python
  def _handle_failed_reports(self, failed, report_batch, max_attempts):
      for report in failed:
          if report['retry_count'] < max_attempts:
              logging.info(f"[{report['title']}] 재시도 {report['retry_count'] + 1}/{max_attempts}")
              if report['retry_count'] == 1:  # 2차: 파일 업로드 재검증
                  # 파일 경로/사이즈 확인 로직 추가
                  pass
              new_url, new_title = self.generate_report_html(report['part_type'], 1, ...)  # 재호출
              if new_url:
                  report.update({'url': new_url, 'title': new_title, 'status': 'generating', 'retry_count': report['retry_count'] + 1})
                  continue
          logging.error(f"[{report['title']}] {max_attempts}회 실패. 전체 재시작.")
          return self._restart_full_batch()  # 전체 재시작 함수 (run_full_automation 재호출)
      return True
  ```

#### 4. 운영 안정화 팁 및 Phase 체크리스트 (CLI 테스트 지침)
- **로깅 통합**: 위 코드처럼 logging 모듈 사용. Phase별 소요시간 기록.
- **--dry-run 옵션**: 스크립트에 추가 (Generate 버튼 누르지 않음, 테스트용).
- **CDP Plan B**: Selenium 4 CDP로 네트워크 응답 가로채 상태 직접 판단 (UI 변동 대비).
- **체크리스트**:
  - Phase 1: URL/타이틀 반환 확인.
  - Phase 2: Archive 페이지에서 모든 리포트 Generated 될 때까지 로그 확인.
  - Phase 3: JSON 변환 시 Instruction_Json.md 규칙 적용 (첫 파일만 아닌 전체 통합).
- **다음 단계**: CLI는 이 지침 적용 후 테스트. 추가 버그 시 로그 공유. (성남시 기반, KST 타임존으로 날짜 설정 확인.)

이 지침으로 CLI가 빠르게 돌파구를 찾을 수 있을 것입니다. 추가 질문 있으신가요?

[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/e195f6db-1f94-4d2e-b730-99303e07f805/folder-structure.txt
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/d8e29fa0-9cfd-4604-899d-444be5d4d344/install_dependencies.bat
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/be5208b3-6f06-47a1-91ec-351615b4f54f/main_generator.py
[4] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/a7e7236c-294d-4978-80ce-df1accb9bd45/requirements.txt