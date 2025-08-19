\[Role: 페노]

## 🤔 Strategic Analysis

V1.00 엑셀은 3개 시트로 구성. BSW→ASW/ASW→BSW IF가 핵심. 지정된 API는 일부만 문서에 존재하고(6/10), 구조체 문서화는 부재. ADC 채널 정의는 다수 확인, CAN 인덱스 정의 패턴은 미탐. V1.01에 SENT·시스템 모니터링·테스트 문서화를 우선 반영 권고. 작업 지시 범위는 업로드된 지시서 기준.&#x20;

## 📝 Expert Recommendation

**산출물:** 상세 표·프로파일은 화면 우측 테이블로 제공. 전체 종합 리포트도 동봉. [다운로드](sandbox:/mnt/data/ARS_BSW-ASW_Interface_V1.00_analysis_report_20250819.md)

### 1) 기본 구조 요약

* 총 시트: 3개

  1. `00_문서정보` (행 49·열 18)
  2. `01_IF_BSW->ASW` (행 32·열 20)
  3. `02_IF_ASW->BSW` (행 14·열 20)
* 역할 추정

  * `00_문서정보`: 버전·범위·용어·API 인덱스 요약
  * `01_IF_BSW->ASW`: BSW 제공 → ASW 참조 신호·API
  * `02_IF_ASW->BSW`: ASW 명령 → BSW 동작 신호·API

### 2) 시트별 세부 분석 제공 내역

* 각 시트별

  * 컬럼 프로파일: 이름·dtype·결측치 수
  * 상위 5행 표본 데이터
* 참조: “시트 요약”, “\[표본 5행] …”, “\[컬럼 프로파일] …” 테이블 확인

### 3) API 문서화 매핑 결과

* **문서에 존재(시트 위치)**

  * `ShrHWIA_BswAdc_GetPhyValue`: 00\_문서정보, 01\_IF\_BSW->ASW
  * `ShrHWIA_BswCan_GetMsg`: 00\_문서정보, 01\_IF\_BSW->ASW
  * `ShrHWIA_BswCan_SetMsg`: 00\_문서정보, 02\_IF\_ASW->BSW
  * `ShrHWIA_BswCan_GetState_Busoff`: 00\_문서정보, 01\_IF\_BSW->ASW
  * `ShrHWIA_BswCan_GetState_Timeout`: 00\_문서정보, 01\_IF\_BSW->ASW
  * `ShrHWIA_BswSys_GetResetReason`: 00\_문서정보, 01\_IF\_BSW->ASW
* **미기재(추가 필요)**

  * `ShrHWIA_BswAdc_GetCurrentCalibStatus`
  * `ShrHWIA_BswAdc_GetMotorTempErrStatus`
  * `ShrHWIA_BswSys_GetCpuLoad`
  * `ShrHWIA_BswSys_SetTargetAxle`

### 4) 데이터 구조체 문서화 현황

* **문서에 존재:** 없음
* **미기재(추가 필요):**

  * `typBswCanMsg_MVPC1`, `typBswCanMsg_RT1_10`, `typBswCanMsg_RT1_20`, `typBswCanMsg_RT1_200`, `typBswCanMsg_ARS1`
  * `DebugADC_t`, `DebugENC_t`, `DebugIcuStatus_t`

### 5) 채널·인덱스 정의 현황

* **ADC 채널 정의 패턴 발견(01\_IF\_BSW->ASW):**
  `BSWADC_CH_SENS_CURR_U/V/W/DC`, `BSWADC_CH_SENS_HV/LV/IG`, `BSWADC_CH_SENS_IPM_TEMP/MOT_TEMP/PCB_TEMP`,
  `BSWADC_CH_SENS_VDD_15V/VDD_5V0`, `BSWADC_CH_VREF_5V0/VCOM_5V0/VT1_5V0/VT2_5V0`, `BSWADC_CH_VUC_3V3`
* **CAN 인덱스/ID 패턴:** 미탐

### 6) V1.01 업데이트 권장사항(우선순위)

* **P1 필수**

  * SENT 프로토콜 API 문서화 추가: `ShrHWIA_BswSent_GetGearPosition`, `ShrHWIA_BswSent_GetSlowChannel(22 IDs)`
  * CAN 메시지 구조체 정의 보강: `typBswCanMsg_*` 일괄 명세(비트필드, 엔디안, 스케일·오프셋, 주기·타임아웃)
* **P2 중요**

  * 성능 모니터링: `ShrHWIA_BswSys_GetCpuLoad` 스펙, 측정 윈도우와 샘플링 주기 명시
  * 시스템 제어: `ShrHWIA_BswSys_SetTargetAxle` 파라미터 범위·상태전이(Front/Rear)·에러코드 정의
* **P3 개선**

  * 테스트·디버그 함수 문서화: 목적, 입력/출력, 부작용, 사용 예
  * ADC 채널 표준 서술 템플릿 적용: 물리량, 단위, 범위, 오버샘플/필터 조건, 진단 비트 매핑

### 7) 실행 단계

1. **API 갭 클로징 표 작성:** 존재/미기재를 기준으로 V1.01 추가 리스트 고정
2. **구조체 스키마 확정:** CAN 메시지별 레이아웃 표준화(스케일·오프셋·유효범위·DTC 연계)
3. **신규 섹션 삽입:** SENT, CPU Load, Target Axle, 테스트 프레임워크
4. **검증 표 추가:** 채널·메시지별 “소스→변환→범위→에러처리” 일관성 점검표
5. **리뷰 라운드:** BSW/ASW 오너 각 1회 승인 라벨 후 배포

### 8) 리스크·대안

* **리스크:** 구조체·CAN 정의 부재로 구현/테스트 불일치 가능성. 시스템 제어 API 미명세로 오동작 위험.
* **대안:** V1.01에서 메시지·채널 정의를 단일 소스오브트루스로 승격. 자동 검증 시트(조건부 서식·유효성) 도입.

추가 요청이 있으시면 알려주세요.
