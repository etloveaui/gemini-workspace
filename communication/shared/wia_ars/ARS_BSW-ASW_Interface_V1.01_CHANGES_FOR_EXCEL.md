# ARS_BSW-ASW_Interface V1.01 변경점 — 엑셀 작성 친화 가이드(코드 기반)

작성일: 2025-08-20
근거: 실제 코드 비교(v1.00=`01_compare_old`, v1.01=`00_compare_current`)

## 요약
- 총 API: 42 → 51 (+9). 삭제 0, 수정 3.
- 변경 핵심: ADC RAW 채널/5V0 전환, CAN RX 인덱스 전면 교체(MVPC/ROUTING), TX MEAS 라인업 추가, 듀얼 CAN(CH1), SENT SlowChannel, 시스템(TargetAxle/Shutdown/CpuLoad/Init3).
- 본 문서는 엑셀 시트에 바로 입력하기 쉬운 형식(필드 블록)으로 정리되었습니다.

---

## 00_문서정보 시트 업데이트
- 문서명(A2): ARS_BSW-ASW_Interface_V1.01
- 버전(B2): V1.01
- 작성일(C2): 2025-08-19
- 변경 이력(마지막 행 추가):
  - “V1.00 → V1.01: API 9개 추가, 3개 수정, 듀얼 CAN, SENT SlowChannel, CPU Load 반영”

---

## 01_IF_BSW→ASW 시트

### A. 수정 항목(3)
1) ShrHWIA_BswAdc_GetPhyValue
- 변경: ADC 채널 매크로 RAW 접미사 도입, VUC 3V3→5V0
- 엑셀 반영 지침:
  - 채널 정의 셀 교체 예시:
    - BSWADC_CH_SENS_CURR_U_RAW(0), _W_RAW(1), _DC_RAW(2), SENS_HV(3)
    - VUC_5V0(8), VCOM_5V0(9), VT1_5V0(10), VT2_5V0(11), VREF_5V0(12)
  - 설명/비고: “v1.01: RAW 채널로 표준화, VUC=5V0” 추가

2) ShrHWIA_BswCan_GetMsg
- 변경: RX 인덱스 전면 교체
  - v1.00: VPC_ARS_01_10ms(0), SEA_ARS_01_1ms(1), SEA_ARS_02_1ms(2)
  - v1.01: MVPC_ARS_01_1ms(0), ROUTING_01_10ms(1), ROUTING_01_20ms(2), ROUTING_01_200ms(3)
- 엑셀 반영 지침:
  - 1st Parameter 셀에 v1.01 인덱스와 주기/ID 주석 병기: “0x20/0x27/0x26/0x25”
  - 비고: “v1.00의 VPC/SEA 계열→v1.01 MVPC/ROUTING 계열로 치환”

3) ShrHWIA_BswCan_GetState_Busoff
- 변경: 듀얼 CAN 채널 지원
  - v1.01: BSWCAN_CAN_CH0(0), BSWCAN_CAN_CH1(1)
- 엑셀 반영 지침:
  - 1st Parameter 열에 CH0/CH1 모두 명시, 비고에 “듀얼 채널” 추가

### B. 신규 추가(5)
아래 블록을 행 단위로 추가하세요(필드명 그대로 사용 권장).

1) ShrHWIA_BswAdc_GetCurrentCalibStatus
- Ver: V1.01
- NO.: (연속 번호)
- Component: BSW → ASW
- Return Type: uint8
- Element Name: ShrHWIA_BswAdc_GetCurrentCalibStatus()
- Return / Range: 0: 진행중, 1: 성공, 2: 실패
- Description: 전류 캘리브레이션 상태
- Result: NEW

2) ShrHWIA_BswAdc_GetMotorTempErrStatus
- Ver: V1.01
- NO.: (연속 번호)
- Component: BSW → ASW
- Return Type: uint8
- Element Name: ShrHWIA_BswAdc_GetMotorTempErrStatus()
- Return / Range: 0: 정상(VALID), 1: 에러(INVALID)
- Description: 모터 온도 센서 에러 상태
- Result: NEW

3) ShrHWIA_BswSent_GetSlowChannel
- Ver: V1.01
- NO.: (연속 번호)
- Component: BSW → ASW
- Return Type: Std_ReturnType
- Element Name: ShrHWIA_BswSent_GetSlowChannel(uint8 msgId, uint16* data, uint32* timestamp)
- 1st Parameter: msgId (22개 ID 지원)
- 2nd Parameter: data (출력)
- 3rd Parameter: timestamp (출력)
- Description: SENT Slow Channel 데이터 읽기
- Note: ID 목록/단위는 하위 설계서에 추후 명시
- Result: NEW

4) ShrHWIA_BswSys_GetCpuLoad
- Ver: V1.01
- NO.: (연속 번호)
- Component: BSW → ASW
- Return Type: float32
- Element Name: ShrHWIA_BswSys_GetCpuLoad()
- Unit / Range: % / 0.0~100.0
- Update: 100ms
- Description: 시스템 CPU 사용률
- Result: NEW

5) ShrHWIA_IswHandler_Init3
- Ver: V1.01
- NO.: (연속 번호)
- Component: BSW → ASW
- Return Type: void
- Element Name: ShrHWIA_IswHandler_Init3()
- Task: Init
- Description: 3차 초기화(고급 기능 활성화)
- Result: NEW

---

## 02_IF_ASW→BSW 시트

### A. 수정 항목(1)
1) ShrHWIA_BswCan_SetMsg
- 변경: TX 인덱스 라인업 개편(“MEAS” 계열 추가)
  - v1.01 TX 인덱스:
    - MEAS_01_1ms(0) / 5ms(1) / 10ms(3)
    - MEAS_02_5ms(2) / 10ms(4)
    - ARS_dev_01_1ms(5)
- DLC 기준(코드 주석):
  - BSWCAN_MSG_DLC_MEAS = 32, BSWCAN_MSG_DLC_ARS_dev_01_1ms = 16
- 엑셀 반영 지침:
  - 1st Parameter 셀에 위 인덱스/주기, 비고에 DLC(32/16) 병기
  - v1.00 TX 인덱스(ARS_dev_0x514~0x517)는 주석으로 “구성 변경됨” 명시

### B. 신규 추가(4)

1) ShrHWIA_BswSys_SetTargetAxle
- Ver: V1.01
- NO.: (연속 번호)
- Task: Init
- Return Type: void
- Element Name: ShrHWIA_BswSys_SetTargetAxle(uint8 axle)
- 1st Parameter: 0: UNDEFINED, 1: FRONT, 2: REAR
- Description: 타겟 액슬 설정
- Result: NEW

2) ShrHWIA_BswSys_ShutdownRequest
- Ver: V1.01
- NO.: (연속 번호)
- Return Type: void
- Element Name: ShrHWIA_BswSys_ShutdownRequest(void)
- Safety Note: IG ON 시 무동작(안전 고려)
- Description: 안전한 시스템 종료 요청
- Result: NEW

3) ShrHWIA_BswCan_SetTimeoutMax
- Ver: V1.01
- NO.: (연속 번호)
- Return Type: void
- Element Name: ShrHWIA_BswCan_SetTimeoutMax(uint8 msg_index, uint32 timeout_max)
- Unit: ms
- Description: CAN 메시지별 타임아웃 최대값 설정(동적)
- Result: NEW

4) ShrHWIA_BswCan_SetCh0CanDisable
- Ver: V1.01
- NO.: (연속 번호)
- Return Type: void
- Element Name: ShrHWIA_BswCan_SetCh0CanDisable(uint8 disable)
- 1st Parameter: 0: 활성화, 1: 비활성화
- Description: CAN CH0 송신 제어
- Result: NEW

---

## 구조체/신호 명세(부록 시트 권장)
- 목적: 코드에 정의된 CAN 메시지 레이아웃을 명세로 고정(비트폭/엔디안/스케일/오프셋/주기/타임아웃).
- 우선 대상(v1.01):
  - typBswCanMsg_MVPC1, typBswCanMsg_RT1_10, typBswCanMsg_RT1_20, typBswCanMsg_RT1_200
  - typBswCanMsg_MEAS, typBswCanMsg_ARS1
- 서술 예시 블록(각 항목 반복):
  - 메시지명: typBswCanMsg_MVPC1
  - 크기: 16 bytes, DLC=16
  - 필드(비트/단위/스케일): MVPC_ArsFrntOpMdCmd(8b), MVPC_ArsReOpMdCmd(8b), …
  - 주기/ID: 1ms / 0x20
  - 타임아웃: N ms (SetTimeoutMax로 변경 가능)

---

## 작성 팁(엑셀 작업 속도 향상)
- 시트 복제 후 V1.01 탭 생성 → 기존 행 유지, 수정/추가만 반영
- “NO.”는 기존 연속성 유지, 신규는 뒤에 이어붙이기
- “Result” 컬럼으로 NEW/CHG 표시 → 필터로 검토/QA 용이
- 주기/ID/DLC를 1st Parameter 또는 비고에 함께 기입(현장 가독성↑)
- 변경 셀은 노란색 강조 → 리뷰/승인 속도 단축

---

## 교차 검증 체크리스트(최종 저장 전)
- ADC 채널 RAW/5V0 반영 여부
- CAN RX 인덱스가 MVPC/ROUTING으로 교체되었는지
- TX MEAS 라인업(5종)과 DLC 값(32/16) 반영 여부
- 듀얼 CAN(CH1) 표기 여부
- SENT SlowChannel/시그니처 변경 반영 여부
- System(TargetAxle/Shutdown/CpuLoad/Init3) 추가 여부
- 구조체 부록 시트에 주요 메시지 6종 레이아웃 기록 여부

---

참고 파일(코드):
- ADC: Ifc_ASW/inc/BswAdc.h, Ifc_BSW/BswAdc.c
- CAN: Ifc_ASW/inc/BswCan.h, Ifc_BSW/BswCan.c
- SENT: Ifc_ASW/inc/BswSent.h, Ifc_BSW/BswSent.c
- SYS: Ifc_ASW/inc/BswSys.h, Ifc_BSW/BswSys.c

위 지침대로 입력하면 V1.01 엑셀 문서를 빠르고 정확하게 완성할 수 있습니다.

