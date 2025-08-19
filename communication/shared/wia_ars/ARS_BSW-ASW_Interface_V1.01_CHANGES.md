# ARS_BSW-ASW_Interface V1.01 변경점 요약

## 📋 문서 개요
- **문서명**: ARS_BSW-ASW_Interface_V1.01.xlsx
- **이전 버전**: V1.00
- **작성일**: 2025-08-19
- **변경 사유**: 코드 구현과 문서 동기화, 신규 기능 추가

## 🔄 전체 변경 요약
- **총 API 개수**: 42개 → 51개 (9개 추가)
- **삭제된 API**: 없음
- **수정된 API**: 3개 (정의 변경)
- **추가된 API**: 9개 (신규 기능)

---

## 📊 시트별 변경사항

### 01_IF_BSW->ASW 시트 (BSW → ASW 인터페이스)
**기존**: 30개 API → **신규**: 35개 API

#### 🔧 수정된 API (3개)

##### 1. ShrHWIA_BswAdc_GetPhyValue - 채널 정의 변경
**변경 이유**: 코드 구현과 문서 불일치 해결
```diff
- #define BSWADC_CH_SENS_CURR_U       (0U)
- #define BSWADC_CH_SENS_CURR_W      (1U)  
- #define BSWADC_CH_SENS_HV             (2U)
- #define BSWADC_CH_SENS_CURR_DC    (3U)
- #define BSWADC_CH_VUC_3V3              (8U)

+ #define BSWADC_CH_SENS_CURR_U_RAW	(0U)
+ #define BSWADC_CH_SENS_CURR_W_RAW	(1U)
+ #define BSWADC_CH_SENS_CURR_DC_RAW	(2U)
+ #define BSWADC_CH_SENS_HV			(3U)
+ #define BSWADC_CH_VUC_5V0			(8U)
```

##### 2. ShrHWIA_BswCan_GetMsg - RX 인덱스 변경
**변경 이유**: CAN 메시지 구조 재설계
```diff
- #define BSWCAN_MSG_RX_INDEX_VPC_ARS_01_10ms		(0U) //Rx // 0x51C
- #define BSWCAN_MSG_RX_INDEX_SEA_ARS_01_1ms		(1U) //Rx // 0x51A
- #define BSWCAN_MSG_RX_INDEX_SEA_ARS_02_1ms		(2U) //Rx // 0x51B

+ #define BSWCAN_MSG_RX_INDEX_MVPC_ARS_01_1ms		(0U) //Rx // 0x20
+ #define BSWCAN_MSG_RX_INDEX_ROUTING_01_10ms		(1U) //Rx // 0x27
+ #define BSWCAN_MSG_RX_INDEX_ROUTING_01_20ms		(2U) //Rx // 0x26
+ #define BSWCAN_MSG_RX_INDEX_ROUTING_01_200ms	(3U) //Rx // 0x25
```

##### 3. ShrHWIA_BswCan_GetState_Busoff - 채널 확장
**변경 이유**: 듀얼 CAN 채널 지원
```diff
- #define BSWCAN_CAN_CH0			(0U)

+ #define BSWCAN_CAN_CH0			(0U)
+ #define BSWCAN_CAN_CH1			(1U)
```

#### ➕ 신규 추가 API (5개)

##### 4. ShrHWIA_BswAdc_GetCurrentCalibStatus (신규)
- **기능**: 전류 캘리브레이션 상태 반환
- **반환값**: 0(진행중), 1(성공), 2(실패)
- **추가 이유**: 전류 센서 진단 기능 강화

##### 5. ShrHWIA_BswAdc_GetMotorTempErrStatus (신규)
- **기능**: 모터 온도 센서 에러 상태 반환
- **반환값**: 0(정상), 1(에러)
- **추가 이유**: 온도 센서 진단 기능 강화

##### 6. ShrHWIA_BswSent_GetSlowChannel (신규)
- **기능**: SENT Slow Channel 데이터 읽기 (22개 ID 지원)
- **파라미터**: msgId, data*, timestamp*
- **추가 이유**: SENT 프로토콜 고급 기능 지원

##### 7. ShrHWIA_BswSys_GetCpuLoad (신규)
- **기능**: CPU 사용률 반환 (0.0~100.0%)
- **업데이트 주기**: 100ms
- **추가 이유**: 시스템 성능 모니터링

##### 8. ShrHWIA_IswHandler_Init3 (신규)
- **기능**: 3차 초기화 함수 (고급 기능 활성화)
- **추가 이유**: 단계별 초기화 지원

### 02_IF_ASW->BSW 시트 (ASW → BSW 인터페이스)
**기존**: 12개 API → **신규**: 16개 API

#### 🔧 수정된 API (1개)

##### ShrHWIA_BswCan_SetMsg - TX 인덱스 확장
**변경 이유**: 측정 데이터 전송 채널 확장
```diff
- #define BSWCAN_MSG_TX_INDEX_ARS_dev_01_10ms		(0U) //Tx // 0x514
- #define BSWCAN_MSG_TX_INDEX_ARS_dev_02_1ms		(1U) //Tx // 0x515

+ #define BSWCAN_MSG_TX_INDEX_MEAS_01_1ms			(0U) //Tx 0x401
+ #define BSWCAN_MSG_TX_INDEX_MEAS_01_5ms			(1U) //Tx 0x402
+ #define BSWCAN_MSG_TX_INDEX_MEAS_02_5ms			(2U) //Tx 0x403
+ #define BSWCAN_MSG_TX_INDEX_MEAS_01_10ms		(3U) //Tx 0x404
+ #define BSWCAN_MSG_TX_INDEX_MEAS_02_10ms		(4U) //Tx 0x405
+ #define BSWCAN_MSG_TX_INDEX_ARS_dev_01_1ms		(5U) //Tx Front: 0x21, Rear: 0x22
```

#### ➕ 신규 추가 API (4개)

##### 1. ShrHWIA_BswSys_SetTargetAxle (신규)
- **기능**: 타겟 액슬 설정 (전륜/후륜)
- **파라미터**: 0(미정의), 1(전륜), 2(후륜)
- **추가 이유**: 시스템 구성 제어

##### 2. ShrHWIA_BswSys_ShutdownRequest (신규)  
- **기능**: 시스템 셧다운 요청
- **안전 기능**: IG ON시 무동작
- **추가 이유**: 안전한 시스템 종료

##### 3. ShrHWIA_BswCan_SetTimeoutMax (신규)
- **기능**: CAN 메시지별 타임아웃 동적 설정
- **파라미터**: msg_index, timeout_max(ms)
- **추가 이유**: CAN 통신 안정성 향상

##### 4. ShrHWIA_BswCan_SetCh0CanDisable (신규)
- **기능**: CAN CH0 송신 활성화/비활성화
- **파라미터**: 0(활성화), 1(비활성화)  
- **추가 이유**: CAN 채널별 제어

### 00_문서정보 시트
**변경사항**: V1.01 버전 이력 추가 예정

---

## 🎯 변경 효과

### 기능 향상
1. **진단 기능 강화**: ADC 캘리브레이션, 온도 센서 진단
2. **통신 안정성**: CAN 타임아웃 설정, 채널별 제어
3. **성능 모니터링**: CPU 사용률 실시간 측정
4. **시스템 제어**: 타겟 액슬 설정, 안전 셧다운

### 호환성
- **하위 호환**: 기존 API 모두 유지 (삭제 없음)
- **점진적 업그레이드**: 신규 API는 선택적 사용 가능

### 품질 향상
- **코드-문서 동기화**: 구현과 명세 일치
- **표준화**: 일관된 명명 규칙 적용

---

## ⚠️ 주의사항

### 이전 버전 사용자
1. **ADC 채널**: 기존 매크로명 변경 (CURR_U → CURR_U_RAW)
2. **CAN 인덱스**: RX/TX 인덱스 번호 변경
3. **VUC 전압**: 3V3 → 5V0 변경

### 신규 기능 사용시
1. **SENT Slow Channel**: 22개 ID 지원 확인
2. **CPU Load**: 측정 윈도우 100ms 고려
3. **Target Axle**: 시스템 초기화 시점 설정 권장

---

## 📅 릴리즈 정보
- **버전**: V1.01
- **릴리즈 날짜**: 2025-08-19
- **다음 계획**: 데이터 구조체 정의 추가 (V1.02)

---
*본 문서는 ARS_BSW-ASW_Interface_V1.01.xlsx의 모든 변경사항을 정확히 반영합니다.*