# 100xFenok 자동화 프로젝트 - 세부 계획서
## 날짜: 2025-08-19
## 작성자: 사용자 + Claude 분석

---

## 🎯 **프로젝트 개요**

### 핵심 목표
매일 6-8시간 소요되는 100xFenok Daily Wrap 생성 과정을 **90% 이상 자동화**하여 **30-60분**으로 단축

### 최종 산출물
- **입력**: TerminalX 데이터
- **출력**: `C:\Users\eunta\multi-agent-workspace\projects\100xFenok\100x\daily-wrap\YYYY-MM-DD_100x-daily-wrap.html`

---

## 📋 **34단계 자동화 프로세스 (프롬프트 1 기준)**

### **Phase 1: TerminalX 리포트 생성 (1-15단계)**

#### **메인 리포트 생성 (1-12단계)**
1. **사이트 접속**: `https://theterminalx.com/agent/enterprise`
2. **로그인**: 기존 계정 정보 사용
3. **URL 이동**: `https://theterminalx.com/agent/enterprise/report/form/10`
4. **6개 탭 생성**: 같은 URL을 6개 탭으로 열기

#### **리포트 설정 (5-11단계)**
5. **제목 입력**:
   - 3개 탭: `"YYYYMMDD 100x Daily Wrap Part1"`
   - 3개 탭: `"YYYYMMDD 100x Daily Wrap Part2"`

6. **날짜 설정** (Report Reference Date):
   - **화요일**: -2일
   - **수~토요일**: -1일

7. **프롬프트 업로드**:
   - Part1: `21_100x_Daily_Wrap_Prompt_1_20250723.md`
   - Part2: `21_100x_Daily_Wrap_Prompt_2_20250708.md`

8. **Sample Report 업로드**:
   - Part1: `10_100x_Daily_Wrap_My_Sources_1_20250723.pdf`
   - Part2: `10_100x_Daily_Wrap_My_Sources_2_20250709.pdf`

9. **Additional Sources 업로드** (각 탭당 2개 파일):
   - Part1: `10_100x_Daily_Wrap_My_Sources_1_20250723.pdf` + `21_100x_Daily_Wrap_Prompt_1_20250723.pdf`
   - Part2: `10_100x_Daily_Wrap_My_Sources_2_20250709.pdf` + `21_100x_Daily_Wrap_Prompt_2_20250708.pdf`

10. **리포트 생성 실행**: 6개 리포트 동시 생성
11. **대기**: 생성 완료까지 기다림
12. **품질 보장**: 3개씩 생성하여 최고 품질 선택

#### **부차 데이터 생성 (13-15단계)**
13. **Enterprise 메인**: `https://theterminalx.com/agent/enterprise`
14. **6개 탭 추가 생성**: 메인 페이지로
15. **설정 변경**: 기간을 "Past Day"로 설정

### **Phase 2: 데이터 추출 및 변환 (16-25단계)**

#### **HTML 추출 (16-20단계)**
16. **메인 리포트 HTML 추출**:
   - 검색어: `.text-\[\#121212\]`
   - 저장 위치: `communication/shared/100xfenok/002_terminalx/`
   - 파일명: `part1_01.html`, `part1_02.html`, `part1_03.html`, `part2_01.html`, `part2_02.html`, `part2_03.html`

17. **부차 데이터 HTML 추출**:
   - 검색어: `[&_sup]:text-[9px]`
   - 저장 위치: `communication/shared/100xfenok/003_terminalx/`

18. **부차 데이터 프롬프트** (`communication/shared/100xfenok/001_terminalx/`):
   - `3.1 3.2 Gain Lose.md`
   - `3.3 Fixed Income.md`
   - `5.1 Major IB Updates.md`
   - `6.3 Dark Pool & Political Donation Flows.md`
   - `7.1 11 GICS Sector Table.md`
   - `8.1 12 Key Tickers Table.md`

19. **HTML → JSON 변환** (도구: `Python_Lexi_Convert`):
   - 입력: `002_terminalx/*.html`
   - 출력: `004_Lexi_Convert/*.json`

20. **부차 데이터 저장**:
   - `003_terminalx/3.1 3.2 Top3.html`
   - `003_terminalx/3.3 Fixed Income.html`
   - `003_terminalx/5.1 Major IB Updates.html`
   - `003_terminalx/6.3 Dark Pool & Political Donation Flows.html`
   - `003_terminalx/7.1 11 GICS Sector Table.html`
   - `003_terminalx/8.1 12 Key Tickers Table.html`

### **Phase 3: JSON 통합 (26-28단계)**

#### **Gemini 2.5 Pro Canvas 활용**
21. **Part1 JSON 통합**:
   - 프롬프트: `005_Json/Instruction_Json_20250726.md`
   - 입력 파일 (7개):
     - `004_Lexi_Convert/part1_01.json`
     - `004_Lexi_Convert/part1_02.json`
     - `004_Lexi_Convert/part1_03.json`
     - `003_terminalx/3.1 3.2 Top3.html`
     - `003_terminalx/3.3 Fixed Income.html`
     - `003_terminalx/5.1 Major IB Updates.html`
     - `003_terminalx/6.3 Dark Pool & Political Donation Flows.html`
   - 출력: `005_Json/YYYYMMDD 100x Daily Wrap Part1.json`

22. **Part2 JSON 통합**:
   - 프롬프트: `005_Json/Instruction_Json_20250726.md`
   - 입력 파일 (5개):
     - `004_Lexi_Convert/part2_01.json`
     - `004_Lexi_Convert/part2_02.json`
     - `004_Lexi_Convert/part2_03.json`
     - `003_terminalx/7.1 11 GICS Sector Table.html`
     - `003_terminalx/8.1 12 Key Tickers Table.html`
   - 출력: `005_Json/YYYYMMDD 100x Daily Wrap Part2.json`

### **Phase 4: 최종 HTML 생성 (29-34단계)**

#### **Gemini 2.5 Pro Canvas 최종 단계**
23. **최종 HTML 생성**:
   - 프롬프트: `006_HTML/wrap-generate-prompt.txt`
   - 입력 파일 (4개):
     - `005_Json/YYYYMMDD 100x Daily Wrap Part1.json`
     - `005_Json/YYYYMMDD 100x Daily Wrap Part2.json`
     - `006_HTML/100x-wrap-agent.md`
     - `006_HTML/100x-daily-wrap-template.html`
   - 출력: `006_HTML/YYYY-MM-DD_100x-daily-wrap.html`

24. **품질 검증 및 수정**: 필요시 수동 보정
25. **최종 산출물 이동**: `projects/100xFenok/100x/daily-wrap/`로 이동

---

## 🚀 **자동화 구현 전략**

### **기술 스택**
- **웹 자동화**: Selenium WebDriver
- **데이터 변환**: Python + BeautifulSoup
- **JSON 통합**: Local LLM (Ollama) 또는 Claude API
- **HTML 생성**: 템플릿 시스템 + LLM
- **스케줄링**: Windows Task Scheduler

### **품질 보장 시스템**
1. **3중 생성**: 같은 리포트를 3개씩 생성하여 최고 품질 선택
2. **데이터 검증**: 금융 데이터 논리성 자동 검증
3. **구조 검증**: HTML/JSON 구조 유효성 검사
4. **백업 시스템**: 각 단계별 결과 자동 백업

### **예상 성과**
- **시간 단축**: 6-8시간 → 30-60분 (90% 단축)
- **품질 향상**: 일관된 품질의 리포트 생성
- **오류 감소**: 수동 작업 오류 최소화
- **확장성**: 다른 리포트 형식으로 확장 가능

---

## ⚠️ **중요 고려사항**

### **데이터 정확성**
- 금융 데이터의 높은 정확성 요구
- 실시간 검증 시스템 필요
- 이상 데이터 자동 감지 및 알림

### **시스템 안정성**
- TerminalX 사이트 변경에 대한 대응
- 네트워크 장애 시 복구 방안
- 생성 실패 시 대체 방안

### **사용자 개입 최소화**
- 90% 자동화, 10% 검증
- 품질 임계값 미달 시만 수동 개입
- 완전 무인 실행 시스템 구축

---

## 📈 **향후 확장 계획**

### **Phase 2 개선사항**
- 웹 UI 관리 대시보드
- 모바일 알림 시스템
- 다중 리포트 형식 지원

### **Phase 3 확장**
- 실시간 데이터 연동
- AI 분석 기능 추가
- 자동 인사이트 생성

---

**🎯 결론: 현재 기술로 95% 자동화 가능, 품질과 안정성 확보를 통한 완전 자동화 시스템 구축 목표**