## TerminalX 자동화 스크립트: 종합 개선 지침

제시하신 실행 계획과 여러 LLM의 분석을 종합하여, 현재 마주한 문제들을 해결하고 스크립트의 안정성과 효율성을 극대화할 수 있는 최종 지침을 마련했습니다. 아래 계획을 순서대로 적용하면, 신뢰도 높은 자동화 시스템을 완성할 수 있을 것입니다.

-----

### 1\. 즉각적인 버그 수정 (가장 시급)

스크립트 실행을 막는 치명적인 버그부터 해결해야 합니다.

#### 1-1. `print` 구문 오류

  - **문제점**: `main_generator.py` 파일의 마지막 `print`문에 개행이 포함되어 있어 `SyntaxError`를 유발합니다.

  - **조치**: 문자열 내에 `\n` (개행 문자)을 사용하여 한 줄로 수정합니다.

    ```python
    # 수정 전
    print("
    --- 자동화 완료 ---")

    # 수정 후
    print("\n--- 자동화 완료 ---")
    ```

#### 1-2. 파일 경로 설정 오류

  - **문제점**: 스크립트 내 경로 계산 로직(`os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))`)이 `folder-structure.txt` 에 명시된 실제 구조와 달라 `FileNotFoundError`를 일으킬 가능성이 높습니다.

  - **조치**: 스크립트 파일의 위치를 기준으로 경로를 명확하고 단순하게 재설정합니다.

    ```python
    # __init__ 메소드 상단 수정 제안
    def __init__(self):
        # 스크립트가 위치한 디렉토리를 프로젝트의 루트 디렉토리로 정의합니다.
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 상위 디렉토리 구조가 복잡하므로, 필요한 외부 경로는 명시적으로 관리하는 것이 좋습니다.
        # 예: self.base_dir = os.path.abspath(os.path.join(self.project_dir, "..", ".."))
        # 여기서는 project_dir를 중심으로 경로를 재설정합니다.
        self.secrets_file = os.path.join(self.project_dir, '..', '..', 'secrets', 'my_sensitive_data.md') # 예시 구조
        self.generated_html_dir = os.path.join(self.project_dir, 'generated_html')
        self.generated_json_dir = os.path.join(self.project_dir, 'generated_json')
        self.input_data_dir = os.path.join(self.project_dir, 'input_data')
        
        # [cite_start]chromedriver.exe가 프로젝트 루트에 있다고 가정합니다[cite: 7].
        self.chromedriver_path = os.path.join(self.project_dir, 'chromedriver.exe')

    # _setup_webdriver 메소드 수정 제안
    def _setup_webdriver(self):
        # ...
        # Service 객체 생성 시, 새로 정의한 경로를 사용합니다.
        service = Service(executable_path=self.chromedriver_path)
        # ...
    ```

-----

### 2\. 아키텍처 개선: `ReportBatch` 클래스 도입

두 개 이상의 리포트를 체계적으로 관리하고 상태를 추적하기 위해, `ReportBatch` 클래스를 도입하는 것을 강력히 추천합니다. 이는 코드의 가독성과 확장성을 크게 향상시킵니다.

**`ReportBatch` 클래스 정의 예시:**

```python
class ReportBatch:
    def __init__(self):
        self.reports = []

    def add_report(self, url, title, part_type):
        """새 리포트 정보를 배치에 추가합니다."""
        self.reports.append({
            'url': url,
            'title': title,
            'part_type': part_type,
            'status': 'Generating', # 초기 상태
            'retry_count': 0
        })

    def get_pending_reports(self):
        """아직 'Generated' 상태가 아닌 리포트들을 반환합니다."""
        return [r for r in self.reports if r['status'] != 'Generated']

    def all_completed(self):
        """모든 리포트가 성공적으로 생성되었는지 확인합니다."""
        return all(r['status'] == 'Generated' for r in self.reports)

    def handle_failure(self, report_title):
        """특정 리포트가 실패했음을 기록하고, 재시도 횟수를 늘립니다."""
        for report in self.reports:
            if report['title'] == report_title:
                report['status'] = 'Failed'
                report['retry_count'] += 1
                return report
        return None
```

-----

### 3\. 핵심 로직 재설계

`ReportBatch` 클래스를 중심으로 `run_full_automation` 워크플로우를 재구성하여 안정성과 효율을 높입니다.

#### 3-1. `run_full_automation` 워크플로우 재설계

생성(Fire-and-Forget), 모니터링, 후속 처리 단계를 명확히 분리합니다.

```python
def run_full_automation(self):
    """개선된 전체 자동화 워크플로우"""
    # 1. 로그인
    if not self._login_terminalx():
        return

    # 날짜 설정 등 사전 준비
    # ...

    # 2. 리포트 배치 생성
    report_batch = ReportBatch()
    reports_to_create = ['Part1', 'Part2']

    # Phase 1: 모든 리포트 생성 요청 (Fire-and-Forget)
    for part in reports_to_create:
        url, title = self.generate_report_html(part, 1, ...)
        if url:
            report_batch.add_report(url, title, part)
        else:
            print(f"오류: {part} 리포트 생성 요청에 실패했습니다.")
            # 필요 시 여기서 중단 결정 가능

    # Phase 2: 통합 상태 모니터링
    if not self.monitor_and_retry_reports(report_batch):
        print("최종 오류: 일부 리포트 생성에 실패하여 자동화를 중단합니다.")
        return

    # Phase 3: 데이터 추출 및 후속 처리
    print("\n--- 모든 리포트 생성 완료. 데이터 처리를 시작합니다. ---")
    self._extract_and_process_data(report_batch)

    print("\n--- 자동화 완료 ---")
    # ... (Git 커밋/푸시 안내 메시지)
```

#### 3-2. `monitor_and_retry_reports` (상태 모니터링 및 재시도)

기존 `_wait_for_report_status` 함수를 대체하여, 모니터링과 재시도 로직을 통합 관리합니다.

```python
def monitor_and_retry_reports(self, report_batch: ReportBatch, max_retries_per_report: int = 2, timeout: int = 1800):
    """
    모든 리포트가 'Generated'가 될 때까지 모니터링하며, 'Failed' 상태 시 재시도를 관리합니다.
    """
    overall_start_time = time.time()

    while time.time() - overall_start_time < timeout:
        pending_reports = report_batch.get_pending_reports()
        if not pending_reports:
            print("모든 리포트가 성공적으로 생성되었습니다.")
            return True

        self.driver.get("https://theterminalx.com/agent/enterprise/report/archive")
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//table/tbody")))
        
        # 현재 페이지의 모든 리포트 상태를 한번에 읽어옵니다.
        rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
        status_map = {row.find_element(By.XPATH, "./td[1]").text: row.find_element(By.XPATH, "./td[4]").text for row in rows}

        for report in pending_reports:
            current_status = status_map.get(report['title'], 'Not Found')
            
            if current_status == 'Generated':
                report['status'] = 'Generated'
                print(f"  - 성공: '{report['title']}' [Generated]")
            
            elif current_status == 'Failed':
                failed_report = report_batch.handle_failure(report['title'])
                if failed_report['retry_count'] < max_retries_per_report:
                    print(f"  - 실패 감지: '{report['title']}'. 재시도를 시작합니다. (시도 {failed_report['retry_count']})")
                    new_url, new_title = self.generate_report_html(report['part_type'], 1, ...)
                    if new_url:
                        # 재시도 성공 시, 새 정보로 업데이트
                        report['url'], report['title'], report['status'] = new_url, new_title, 'Generating'
                else:
                    print(f"  - 최종 실패: '{report['title']}'가 최대 재시도 횟수를 초과했습니다.")
                    return False # 전체 프로세스 실패 처리
            else:
                 print(f"  - 대기: '{report['title']}' [{current_status}]")

        time.sleep(45) # 다음 Polling까지 45초 대기 (Exponential Backoff 적용 가능)

    print("오류: 전체 작업 시간 초과.")
    return False
```

-----

### 4\. 운영 안정성을 위한 고급 제안

  - [cite\_start]**HTML 파싱 개선**: `main.html` 업데이트 시, 불안정한 `replace()` 대신 `BeautifulSoup4` [cite: 1] 라이브러리를 사용하여 특정 `<a>` 태그의 `href` 속성을 정확히 찾아 수정하는 것이 장기적으로 안정적입니다.
  - **로깅(Logging) 도입**: `print()` 대신 Python의 `logging` 모듈을 사용하세요. `INFO`, `WARNING`, `ERROR` 레벨을 구분하여 로그를 남기면, 문제 발생 시 원인 추적이 훨씬 용이합니다.
  - **Dry-Run 모드 추가**: `--dry-run`과 같은 커맨드라인 인자를 추가하여, 실제 'Generate' 버튼을 클릭하지 않고 폼 입력까지만 테스트하는 기능을 구현하면 개발 및 디버깅 효율이 높아집니다.