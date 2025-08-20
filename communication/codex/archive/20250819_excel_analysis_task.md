---
agent: codex
priority: P1
status: pending
created: 2025-08-19 15:00
task_type: excel_analysis
---

# Excel 분석 작업 지시서 (ARS Interface V1.01 문서화)

## 🎯 작업 목표
`ARS_BSW-ASW_Interface_V1.00.xlsx` 파일을 분석하여 V1.01 문서 작성을 위한 기반 정보를 추출하고, Claude가 분석한 코드 구조와 매핑하여 업데이트 방향성을 수립한다.

## 📂 파일 정보
- **대상 파일**: `C:\Users\eunta\multi-agent-workspace\communication\shared\wia_ars\ARS_BSW-ASW_Interface_V1.00.xlsx`
- **파일 성격**: BSW-ASW 인터페이스 문서 (Version 1.00)
- **고객**: WIA (ARS 시스템용)

## 🔍 분석 요청 사항

### 1. 기본 구조 분석
- **모든 시트 목록** 추출 및 용도 파악
- **각 시트별 컬럼 구조** 분석 (컬럼명, 데이터 타입, 결측치)
- **표본 데이터** (각 시트별 상위 5행) 추출

### 2. API 문서화 현황 파악
다음 API 함수들이 V1.00에 문서화되어 있는지 확인:

#### ADC 관련 API
- `ShrHWIA_BswAdc_GetPhyValue()`
- `ShrHWIA_BswAdc_GetCurrentCalibStatus()`
- `ShrHWIA_BswAdc_GetMotorTempErrStatus()`

#### CAN 관련 API
- `ShrHWIA_BswCan_GetMsg()`
- `ShrHWIA_BswCan_SetMsg()`
- `ShrHWIA_BswCan_GetState_Busoff()`
- `ShrHWIA_BswCan_GetState_Timeout()`

#### 시스템 관리 API
- `ShrHWIA_BswSys_GetCpuLoad()`
- `ShrHWIA_BswSys_SetTargetAxle()`
- `ShrHWIA_BswSys_GetResetReason()`

### 3. 데이터 구조체 문서화 현황
다음 구조체들의 문서화 여부 확인:
- `typBswCanMsg_MVPC1`
- `typBswCanMsg_RT1_10/20/200`
- `typBswCanMsg_ARS1`
- `DebugADC_t`, `DebugENC_t`, `DebugIcuStatus_t`

### 4. 채널 및 인덱스 정의 현황
- **ADC 채널 정의** (16개 채널: BSWADC_CH_*)
- **CAN 메시지 인덱스** (RX/TX 인덱스들)
- **DIO 핀 정의** (TP158, TP29 등 테스트 포인트들)

## 🚀 Claude 코드 분석 결과 요약

### 발견된 새로운 기능들 (V1.01 추가 예상)
1. **SENT 프로토콜 지원**
   - `ShrHWIA_BswSent_GetGearPosition()`
   - `ShrHWIA_BswSent_GetSlowChannel()` (22개 ID 지원)

2. **성능 모니터링**
   - `BswTest_StopWatch_Start/Stop()` (실행 시간 측정)
   - CPU 로드 모니터링

3. **향상된 시스템 제어**
   - 타겟 액슬 설정 (Front/Rear)
   - 개선된 셧다운 제어

4. **확장된 테스트 기능**
   - 927줄의 포괄적 테스트 코드 (`BswTest.c`)
   - 다양한 하드웨어 모듈 테스트

## 📊 요청하는 분석 결과 포맷

### 1. 기본 정보 요약
```
- 총 시트 개수: N개
- 주요 시트별 역할:
  * 시트1: 용도 설명
  * 시트2: 용도 설명
  ...
```

### 2. 각 시트별 상세 분석
```
## 시트명: [시트 이름]
- 총 행/열 개수: 
- 주요 컬럼:
  * 컬럼1: 데이터타입, 설명
  * 컬럼2: 데이터타입, 설명
- 표본 데이터 (5행):
  [표 형태로 제시]
```

### 3. API 매핑 결과
```
## 기존 문서화된 API (V1.00)
- [함수명]: 시트명, 위치
...

## 문서화 누락 API (V1.01 추가 필요)
- [함수명]: 추가 이유
...
```

### 4. V1.01 업데이트 권장사항
```
## 우선순위별 업데이트 항목
### P1 (필수)
- SENT 프로토콜 API 문서화
- 새로운 CAN 메시지 구조체 추가

### P2 (중요)  
- 성능 모니터링 API 추가
- 시스템 제어 API 확장

### P3 (개선)
- 테스트 함수 문서화
- 디버그 구조체 정의
```

## ⚠️ 주의사항
1. **기존 V1.00 내용을 완전히 파악**한 후 추가/수정 항목만 식별
2. **API 함수명 매칭 시 정확한 철자** 확인 필요
3. **데이터 구조체의 멤버 변수 변경사항** 주의 깊게 분석
4. **채널 번호나 인덱스 변경사항** 확인

## 🎯 최종 기대 결과
V1.00 기준 대비 V1.01에서 **정확히 무엇을 추가/수정해야 하는지** 명확한 업데이트 리스트를 Claude와 공유하여 효율적인 문서 작성 진행

---
**작업 완료 후**: 결과를 `communication/shared/` 폴더에 저장하고 Claude에게 공유하여 V1.01 문서 작성 작업 시작