
# 제미나이 CLI 환경 이전 및 자동화 프로젝트 실행 계획

이 문서는 제미나이 CLI의 작업 환경을 새로운 구조로 안전하게 이전하고, 후속 자동화 프로젝트를 진행하기 위한 공식 계획서입니다.

## 1단계: 제미나이 CLI 환경 이전 (가장 중요)

**목표:** 여러 PC에서 제미나이의 대화/메모리(.gemini)를 Git으로 동기화하고, 프로젝트와 임시 작업을 분리하여 관리할 수 있는 영구적인 작업 환경을 구축합니다.

**절차:**

1.  **현재 제미나이 CLI 종료:** 이 파일이 생성된 것을 확인한 후, 현재 실행 중인 터미널(CLI) 창을 완전히 닫습니다.
2.  **폴더 구조 생성 및 파일 이동:**
    *   `C:\Users\eunta\` 경로에 `gemini-workspace` 라는 새 폴더를 만듭니다.
    *   그 안에 `projects` 와 `scratchpad` 라는 두 개의 폴더를 추가로 만듭니다.
    *   **`.gemini` 폴더 이동:** `C:\Users\eunta\.gemini` 폴더를 `C:\Users\eunta\gemini-workspace\` 안으로 **잘라내기 -> 붙여넣기** 합니다. (기존 대화 기록 보존)
    *   **`100xFenok` 프로젝트 이동:** `C:\Users\eunta\gemcli\repo\100xFenok` 폴더를 `C:\Users\eunta\gemini-workspace\projects\` 안으로 **잘라내기 -> 붙여넣기** 합니다.
3.  **Git 저장소 설정:**
    *   `C:\Users\eunta\gemini-workspace` 폴더에서 터미널을 열고 `git init`을 실행합니다.
    *   GitHub에 만들어 둔 `gemini-workspace` 원격 저장소를 `git remote add origin <주소>` 명령으로 연결합니다.
    *   `.gitignore` 파일을 생성하고 아래 내용을 추가합니다. `projects`와 `scratchpad` 폴더를 동기화에서 제외하기 위함입니다.
        ```gitignore
        # 정식 프로젝트 폴더들은 각자의 Git 저장소를 가질 수 있으므로 동기화 안 함
        /projects/

        # 임시 작업 폴더는 로컬에서만 사용하므로 동기화 안 함
        /scratchpad/
        ```
    *   `git add .`, `git commit -m "Initial setup of gemini-workspace"`, `git push` 명령으로 첫 동기화를 완료합니다.
4.  **새로운 환경에서 CLI 시작:**
    *   **앞으로는 항상 `C:\Users\eunta\gemini-workspace` 폴더에서 제미나이 CLI를 실행합니다.**
    *   CLI를 실행한 후, "이전 대화 기억나?" 또는 "마이그레이션 계획 파일 읽어줘" 라고 말하여 모든 내용이 복구되었는지 확인합니다.

## 2단계: 자동화 프로젝트 (`100xFenok-generator`) 계획

**목표:** The TerminalX 로그인 -> 데이터 추출 -> 가공 -> `데일리랩.html` 파일 생성을 완전 자동화합니다.

**위치:** `C:\Users\eunta\gemini-workspace\projects\` 안에 `100xFenok-generator` 라는 새 폴더를 만들고, 그 안에서 모든 자동화 스크립트를 개발합니다.

**개발 순서:**

1.  **로그인 및 데이터 추출:** `Selenium`을 사용하여 The TerminalX에 로그인하고, 10개의 산출물 HTML을 변수로 가져오는 스크립트 작성.
2.  **데이터 가공 및 통합:** `BeautifulSoup`을 사용하여 HTML에서 데이터를 추출/가공하고, 2개의 핵심 JSON 객체로 통합하는 스크립트 작성.
3.  **최종 HTML 빌드:** `Jinja2` 템플릿 엔진을 사용하여, 가공된 데이터를 `100x-daily-wrap-template.html`에 삽입하여 최종 결과물을 `../100xFenok/100x/daily-wrap/` 폴더에 저장하는 스크립트 작성.

---
**이 파일의 지시대로 진행하면 모든 작업 내용을 보존한 채 안전하게 이사할 수 있습니다.**

