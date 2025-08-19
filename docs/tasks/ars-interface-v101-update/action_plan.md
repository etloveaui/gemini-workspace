---
task: ARS_BSW-ASW_Interface_V1.01_Update
priority: P1
status: active
created: 2025-08-19 15:10
assigned: claude
---

# ARS Interface V1.01 업데이트 작업 계획

## 📊 현황 분석 결과

### V1.00 기존 문서 구조 (GPT 분석 + CSV 확인)
- **3개 시트 구성**:
  - `00_문서정보`: 49행×18열 (버전 이력, API 인덱스)
  - `01_IF_BSW->ASW`: 32행×20열 (BSW→ASW 인터페이스)
  - `02_IF_ASW->BSW`: 14행×20열 (ASW→BSW 인터페이스)

### 기존 문서화된 API (6개)
- `ShrHWIA_BswAdc_GetPhyValue`
- `ShrHWIA_BswCan_GetMsg`
- `ShrHWIA_BswCan_SetMsg` 
- `ShrHWIA_BswCan_GetState_Busoff`
- `ShrHWIA_BswCan_GetState_Timeout`
- `ShrHWIA_BswSys_GetResetReason`

### 코드 분석에서 발견된 신규 API (미문서화)
- `ShrHWIA_BswAdc_GetCurrentCalibStatus`
- `ShrHWIA_BswAdc_GetMotorTempErrStatus`
- `ShrHWIA_BswSys_GetCpuLoad`
- `ShrHWIA_BswSys_SetTargetAxle`
- `ShrHWIA_BswSent_GetGearPosition`
- `ShrHWIA_BswSent_GetSlowChannel`

## 🎯 V1.01 업데이트 작업 계획

### Phase 1: 필수 API 문서화 (P1)
1. **SENT 프로토콜 API 추가**
   - `ShrHWIA_BswSent_GetGearPosition()` 
   - `ShrHWIA_BswSent_GetSlowChannel()` (22개 ID 지원)
   - 파라미터, 반환값, 사용법 상세 기술

2. **ADC 확장 API 추가**
   - `ShrHWIA_BswAdc_GetCurrentCalibStatus()`
   - `ShrHWIA_BswAdc_GetMotorTempErrStatus()`

3. **시스템 관리 API 추가**  
   - `ShrHWIA_BswSys_GetCpuLoad()`
   - `ShrHWIA_BswSys_SetTargetAxle()`

### Phase 2: 데이터 구조체 정의 (P2)
1. **CAN 메시지 구조체 문서화**
   - `typBswCanMsg_MVPC1`
   - `typBswCanMsg_RT1_10/20/200`  
   - `typBswCanMsg_ARS1`
   - 비트필드, 스케일링, 주기 정보 포함

2. **디버그 구조체 추가**
   - `DebugADC_t`, `DebugENC_t`, `DebugIcuStatus_t`

### Phase 3: 테스트 및 고급 기능 (P3)
1. **성능 모니터링 함수군**
   - `BswTest_StopWatch_Start/Stop()`
   - 실행 시간 측정 방법론

2. **확장된 채널 정의**
   - 22개 SENT Slow Channel ID 매핑
   - 새로운 ADC 채널 정의

## 📝 작업 실행 단계

### Step 1: V1.00 원본 CSV 정확한 분석
- [x] 3개 시트별 구조 파악
- [x] 기존 API 매핑 완료
- [x] 누락된 API 식별

### Step 2: V1.01 추가 내용 정의
- [ ] **01_IF_BSW->ASW 시트 업데이트**
  - SENT API 2개 추가
  - ADC 확장 API 2개 추가  
  - 시스템 관리 API 2개 추가

- [ ] **02_IF_ASW->BSW 시트 업데이트**  
  - 타겟 액슬 설정 API 추가
  - 테스트 제어 API 추가

- [ ] **00_문서정보 시트 업데이트**
  - V1.01 버전 이력 추가
  - 변경된 API 목록 업데이트

### Step 3: 새로운 CSV 파일 생성
- [ ] 기존 CSV 기반으로 V1.01 버전 생성
- [ ] 각 시트별 구조 유지하면서 내용 추가
- [ ] API 파라미터, 반환값, 설명 정확히 기입

### Step 4: Excel 파일 재구성
- [ ] 3개 CSV를 Excel 시트로 통합
- [ ] 원본 포맷팅 및 레이아웃 유지
- [ ] V1.01로 버전 업데이트

## 📋 품질 체크리스트
- [ ] 모든 신규 API가 적절한 시트에 배치됨
- [ ] 파라미터 타입과 범위가 코드와 일치함
- [ ] 구조체 정의가 실제 구현과 매핑됨
- [ ] 채널 번호와 상수가 정확함
- [ ] 문서 버전 이력이 업데이트됨

## 🚀 즉시 시작 가능한 상태
모든 분석이 완료되어 즉시 V1.01 문서 작성을 시작할 수 있습니다.
토큰 효율성을 위해 단계별로 진행하며, 각 단계 완료 시 백업을 수행합니다.

**예상 작업 시간**: 2-3시간 (단계별 검토 포함)
**최종 산출물**: `ARS_BSW-ASW_Interface_V1.01.xlsx`