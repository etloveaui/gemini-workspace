## **범용 AI 프롬프트 생성 지시서 (v2.0)**

### 1. 기본 원칙 (Core Principles)

1.  **'지시'가 아닌 '요청':** 우리는 AI에게 '명령'하는 것이 아니다. 우리는 AI가 가진 방대한 정보와 분석 능력을 바탕으로 '훌륭한 리포트 작성을 요청'하는 것이다. 모든 프롬프트는 이 원칙을 기반으로 작성된다.
2.  **구체성이 성공을 결정한다:** AI는 추상적인 개념(예: '기술주')보다 구체적인 실체(예: 'AAPL, MSFT, NVDA...')에 훨씬 더 정확하게 반응한다. 요청의 구체성을 최대화하는 것이 가장 중요하다.
3.  **'골든 포뮬러' 준수:** 아래에 설명될 프롬프트 '골든 포뮬러'는 예외 없이 모든 요청에 일관되게 적용되어야 한다.

---

### 2. 프롬프트 생성 3단계 프로세스 (3-Step Generation Process)

프롬프트 생성은 반드시 아래 3단계 프로세스를 순서대로 거쳐야 한다.

#### **STEP 1: 목표 섹션 요구사항 분석**

프롬프트를 작성하기 전, `HTML 템플릿`과 `MD 지침서` 파일에서 생성하려는 목표 섹션(예: `7.1`, `8.1`)의 요구사항을 정확히 분석하고 아래 항목들을 명확히 식별한다.

* **① 분석 대상 (Primary Entities):**
    * 리포트의 핵심이 되는 구체적인 대상 목록.
    * *예시 (7.1):* 11개 GICS 섹터 **ETF**
    * *예시 (8.1):* 12개 주요 기술주 **티커** (AAPL, MSFT, ...)
* **② 필수 데이터 (Required Data Points):**
    * 테이블의 컬럼 헤더나 리포트에 반드시 포함되어야 할 데이터 항목.
    * *예시 (7.1):* `Day %`, `YTD %`, `Valuation Metric`, `Comment`
    * *예시 (8.1):* `Day %`, `YTD %`
* **③ 필요한 서술 구조 (Required Narrative Structure):**
    * 데이터 외에 필요한 서술형 분석의 구조.
    * *예시 (7.1):* 여러 섹터 로테이션 테마를 통합한 **통합 분석**
    * *예시 (8.1):* 12개 기업 각각에 대한 **개별 분석 단락**
* **④ 특별 규칙 (Special Rules):**
    * 데이터 처리와 관련된 모든 특수 조건 (예: Valuation 대체 순서, 뉴스 품질 조건).

#### **STEP 2: '골든 포뮬러' 적용 및 조합**

**STEP 1**에서 분석한 내용을 바탕으로 '골든 포뮬러'의 각 구성요소를 채우고 조합하여 프롬프트 초안을 만든다.

> **골든 포뮬러:**
> **`[A: 분석 대상 및 시점]` `&` `[B: 데이터 요소]` `&` `[C: 서술/분석 요소]`**

#### **STEP 3: 최종 검토 체크리스트**

작성된 프롬프트가 아래 핵심 성공 요건을 모두 충족하는지 최종 확인한다.

1.  [ ] **주제 서술형인가?** (명령형 "Populate..." 대신 주제 제시형 "Today's..."로 시작하는가?)
2.  [ ] **대상이 구체적인가?** (추상적인 '섹터' 대신 `(ETFs)`를 명시했는가? 모든 티커를 나열했는가?)
3.  [ ] **'&' 기호를 사용했는가?** (모든 구성요소가 쉼표가 아닌 `&`로 연결되었는가?)
4.  [ ] **유연한 가이드라인을 제시했는가?** (규칙이 유동적인 항목에 `(e.g., ...)`를 사용했는가?)
5.  [ ] **서술 구조를 명확히 지시했는가?** (**STEP 1-③**에서 정의한 '통합 분석' 또는 '개별 분석' 구조를 명확히 지시하는 키워드를 사용했는가?)

---

### 3. '골든 포뮬러' 구성요소별 상세 작성 규칙

#### **[A] 분석 대상 및 시점 작성법**

* **규칙 3-A-1:** `Today's` 또는 날짜 `(MM/DD)`로 시작한다.
* **규칙 3-A-2 (가장 중요):** **STEP 1**에서 식별한 '① 분석 대상'을 명시한다.
    * 대상이 특정 그룹일 경우, `(ETFs)`와 같이 타입을 명시하여 구체화한다.
    * **대상이 고정된 목록(Enumerated List)일 경우, 반드시 모든 항목을 프롬프트에 직접 나열해야 한다.** (예: 8.1 섹션의 12개 티커)

#### **[B] 데이터 요소 작성법 (주로 표 생성을 위해)**

* **규칙 3-B-1:** **STEP 1**에서 식별한 '② 필수 데이터'와 '④ 특별 규칙'을 키워드로 변환한다.
* **규칙 3-B-2:** 각 키워드는 `&`로 연결한다.
* **규칙 3-B-3:** '④ 특별 규칙' 중 대체 순서(Fallback) 같은 조건은 반드시 `(e.g., ...)` 구문을 사용해 유연하게 표현한다. (예: `& Valuation (e.g., Fwd P/E or P/E TTM)`)

#### **[C] 서술/분석 요소 작성법 (서술 구조 통제를 위해)**

* **규칙 3-C-1 (가장 중요):** **STEP 1-③**에서 정의한 '필요한 서술 구조'를 AI가 오해 없이 따르도록 명시적으로 지시하는 키워드를 사용한다.
    * **통합 분석**이 필요할 경우: `& Key ... Themes` 와 같이 포괄적인 키워드를 사용한다.
    * **개별 분석**이 필요할 경우: `for each ...` 와 같이 범위를 명확히 한정하는 키워드를 사용한다.
    * **Bad 👎 (테마별 그룹핑 유발):** `& a specific, catalyst-driven News Summary`
    * **Good 👍 (개별 단락 생성 유도):** `& 1-paragraph summary for each ticker citing its key driver`

---

### 4. 섹션별 적용 예시

#### **예시 1: `7.1 11 GICS Sector Table` 프롬프트 생성**

1.  **STEP 1 (분석):**
    * ① 분석 대상: 11개 GICS 섹터 **ETFs**
    * ② 필수 데이터: Day %, YTD %, Valuation, Comment
    * ③ 서술 구조: 여러 테마를 다루는 **통합 분석** (Sector Rotation Views)
    * ④ 특별 규칙: Valuation Fallback Order
2.  **STEP 2 (조합):**
    * [A]: `Today's 11 GICS sector (ETFs) performance`
    * [B]: `& Day % & YTD % & 1-line driver comment & Valuation (e.g., P/E TTM)`
    * [C]: `& Key Sector Rotation Themes` (통합 분석을 위해 포괄적 키워드 사용)
3.  **최종 프롬프트:**
    > **Today's 11 GICS sector (ETFs) performance & Day % & YTD % & 1-line driver comment & Valuation (e.g., P/E TTM) & Key Sector Rotation Themes**

#### **예시 2: `8.1 12 Key Tickers Table` 프롬프트 생성 (업데이트 반영)**

1.  **STEP 1 (분석):**
    * ① 분석 대상: **AAPL, MSFT, NVDA, ... , PLTR** (12개 티커 전체)
    * ② 필수 데이터: Day %, YTD %
    * ③ 서술 구조: 12개 기업 **각각에 대한 개별 분석 단락**
    * ④ 특별 규칙: News 품질 조건
2.  **STEP 2 (조합):**
    * [A]: `Today's performance for AAPL, MSFT, NVDA, AMZN, GOOGL, META, AVGO, CRWD, NFLX, NOW, TSLA, PLTR`
    * [B]: `& Day % & YTD %`
    * [C]: `& 1-paragraph summary for each ticker citing its key driver` (**규칙 3-C-1**에 따라 '개별 분석'을 명시적으로 지시)
3.  **최종 프롬프트:**
    > **Today's performance for AAPL, MSFT, NVDA, AMZN, GOOGL, META, AVGO, CRWD, NFLX, NOW, TSLA, PLTR & Day % & YTD % & 1-paragraph summary for each ticker citing its key driver**