# ARS 제어기 CAN1 버스 오프 복구 문제 심층 분석 및 최종 해결 방안 보고서

- **작성일:** 2025년 7월 29일
- **관련 작업 ID:** `ars-can-busoff-recovery-fix`
- **문서 목적:** CAN1 채널의 Bus-Off 복구 실패 원인을 명확히 규명하고, 프로젝트의 특수한 MCAL 제약사항을 고려한 최종 해결 방안을 기술적 근거와 함께 상세히 기록하여 내부 보고 및 기술 자산으로 활용.

---

## 1. 문제 정의

ARS(Active Roll Stabilization) 제어기의 CAN1 채널에서 Bus-Off 이벤트 발생 시, 정상적인 통신 상태로 복구되지 않는 문제가 발생함.

#### 1.1. 상세 현상

- Bus-Off 복구 로직이 실행된 후, 송신(TX)은 재개되는 것처럼 보이나 **수신(RX) 관련 기능이 완전히 멈춤.**
- 이로 인해 CAN RX 타임아웃 감지를 포함한 모든 수신 기반 로직이 동작하지 않음.

#### 1.2. 초기 분석 및 진행 과정

- **1차 시도:** 하드웨어 레지스터(`MODULE_CAN1.N[0].CCCR.B.INIT = 0;`)를 직접 제어하는 방식으로 복구를 시도했으나, RX 기능이 살아나지 않는 등 불완전한 복구 현상 확인.
- **2차 시도:** 1차 시도에 MCAL API인 `Can_17_McmCan_SetControllerMode()`와 `Can_17_McmCan_EnableControllerInterrupts()`를 추가했을 때 비로소 정상 동작함을 확인함.
- **분석 방향 설정:** 이 현상을 바탕으로, 문제의 원인이 단순한 하드웨어 상태 복구가 아닌, **MCAL 드라이버의 내부 상태(특히 인터럽트)와 관련된 것**이라는 가설을 세우고 심층 분석을 시작함.

---

## 2. 심층 분석 과정 및 기술적 근거

문제의 근본 원인을 파악하기 위해 하드웨어 매뉴얼, MCAL 문서, 관련 소스 코드를 종합적으로 분석함.

### 2.1. 하드웨어 동작 분석 (MCU User Manual 기반)

- **근거 자료:** `[EN]CAN_AURIX_TC3xx_Part2-1946-2124.pdf.json` (TC364DP User Manual)
- **Bus-Off 시 하드웨어 동작:** 컨트롤러가 Bus-Off 상태에 진입하면, 하드웨어는 자동으로 `CCCR` (CC Control Register) 레지스터의 `INIT` 비트를 '1'로 설정하여 CAN 버스와의 통신을 중단시킨다.
  > **참조 (pg23_1):** "Software initialization is started by setting bit CCCRi.INIT, either by software or by a hardware reset, or by going Bus_Off."
- **하드웨어 레벨 복구:** `INIT` 비트를 다시 '0'으로 클리어하면, 하드웨어는 버스 유휴 상태를 감지한 후 통신에 다시 참여할 준비를 한다.
  > **참조 (pg23_1):** "Resetting CCCRi.INIT finishes the software initialization. Afterwards the Bit Stream Processor BSP synchronizes itself to the data transfer on the CAN bus..."
- **분석:** 하드웨어 관점에서는 `INIT` 비트 제어만으로 복구가 시작되는 것처럼 보이지만, 이는 MCAL 소프트웨어 계층의 상태를 고려하지 않은 것이다.

### 2.2. MCAL API 동작 분석 (`Can_17_McmCan.c` 소스 기반)

- **핵심 API:** `Can_17_McmCan_SetControllerMode(Controller, CAN_T_START)`
- **근거 자료:** `mcal/MCAL_Modules/Can_17_McmCan/ssc/src/Can_17_McmCan.c`
- **분석:** 이 함수는 단순한 레지스터 조작 래퍼(Wrapper)가 아니다. 컨트롤러를 `STOPPED`에서 `STARTED` 상태로 전환하는 공식적인 상태 머신 전환 절차이며, 내부적으로 `Can_17_McmCan_lSetModeStart` 함수를 호출하여 다음과 같은 복합적인 작업을 수행한다.
    1.  **하드웨어 통신 재개:** `NodeRegAddressPtr->CCCR.B.INIT = CAN_17_MCMCAN_BIT_RESET_VAL;` 코드를 통해 `INIT` 비트를 '0'으로 클리어한다.
    2.  **인터럽트 재활성화:** `NodeRegAddressPtr->IE.U |= CoreConfigPtr->...CanEnableInterruptMask;` 코드를 통해 **Bus-Off 발생 시 비활성화되었을 수 있는 모든 관련 인터럽트를 `IE` (Interrupt Enable) 레지스터에 다시 설정**한다. **이것이 RX 기능 복구의 핵심이다.**
    3.  **내부 상태 동기화:** MCAL 드라이버가 관리하는 컨트롤러 상태 변수를 `STARTED`로 갱신한다.
- **결론:** `SetControllerMode` API는 하드웨어와 소프트웨어(MCAL)의 상태를 모두 동기화하고, 완전한 복구에 필요한 모든 절차를 포함하고 있음을 확인함.

- **추가 API:** `Can_17_McmCan_EnableControllerInterrupts(Controller)`
- **분석:** 이 함수는 명시적으로 컨트롤러의 인터럽트를 활성화한다. `SetControllerMode` 내부에서 인터럽트가 활성화될 것으로 예상되지만, 사용자님의 특정 MCAL 빌드에서 완벽한 복구를 보장하기 위한 **안전장치** 역할을 하며, 실제 테스트에서 RX 복구에 기여했음이 확인됨.

### 2.3. 프로젝트 특수성: CAN1 채널의 MCAL 제약사항

- **제약사항:** CAN0 채널은 완전한 AUTOSAR 스택(CanSM 포함)의 관리를 받지만, **CAN1 채널은 `CanSM`의 관리 없이 MCAL 드라이버 레벨에서 직접 제어**해야 한다.
- **분석:** 이로 인해 AUTOSAR의 표준 Bus-Off 복구 체계(`CanDrv` -> `CanIf` -> `CanSM` -> `CanIf` -> `CanDrv`)가 CAN1에는 적용될 수 없다. `Can_17_McmCan_IsrBusOffHandler`나 `Can_17_McmCan_MainFunction_BusOff`와 같은 MCAL의 표준 보고 함수들은 최종적으로 `CanSM`에 보고하도록 설계되어 있으므로, `CanSM`이 없는 CAN1 환경에서는 보고 체계가 끊어져 복구 명령이 내려올 수 없다.
- **결론:** CAN1을 위해서는 EHAL과 같은 상위 어플리케이션 레이어에서 Bus-Off 감지와 복구 로직을 모두 책임져야만 한다.

---

## 3. 주요 Q&A 및 대안 검토

| 검토 항목 | 상세 내용 및 결론 |
| :--- | :--- |
| **`SetControllerMode` API의 부하 문제** | **결론: 문제 없음.** 이 API는 상태 머신을 전환하는 상대적으로 무거운 작업이지만, Bus-Off라는 예외 상황에서만 단발적으로 호출되므로 시스템에 부하를 주지 않는다. 주기적으로 상태를 확인하는 것은 매우 가벼운 작업이다. |
| **레지스터 직접 제어 방식 (MCAL 미사용)** | **결론: 절대 불가.** `CCCR.INIT` 비트 외에 `IE` (Interrupt Enable) 레지스터 등 MCAL이 관리하는 다른 레지스터들의 상태를 알 수 없다. 이를 직접 제어하는 것은 MCAL의 추상화 계층을 파괴하고, 드라이버와 하드웨어의 상태 불일치를 유발하여 예측 불가능한 심각한 오류를 초래할 수 있다. |
| **`Can_17_McmCan_IsrBusOffHandler` 또는 `Can_17_McmCan_MainFunction_BusOff` 사용** | **결론: 부적합.** 이 함수들은 복구 함수가 아니라, Bus-Off 발생을 감지하고 상위 레이어(`CanIf`->`CanSM`)에 **보고**하는 함수이다. `CanSM`이 없는 CAN1 환경에서는 보고를 받은 후 복구를 명령할 주체가 없어 컨트롤러가 영원히 `STOPPED` 상태에 머무르게 된다. |
| **`Can_17_McmCan_GetControllerErrorState` 사용** | **결론: 현재 프로젝트에서는 사용 불가.** 이 함수는 MCAL이 제공하는 표준 API이지만, 현재 프로젝트의 MCAL 빌드 설정에서 CAN1 채널에 대해 해당 함수가 생성되지 않았음이 확인됨. 따라서 Bus-Off 상태 감지를 위해 `MODULE_CAN1.N[0].PSR.B.BO` 레지스터를 직접 읽는 것이 유일한 방법임. |

---

## 4. 최종 결론 및 해결 방안

#### 4.1. 근본 원인

**"불완전한 복구 절차로 인한 MCAL 드라이버와 하드웨어 간의 상태 불일치"**

Bus-Off 발생 시 MCAL 드라이버는 안전을 위해 내부적으로 컨트롤러 상태를 `STOPPED`로 변경하고 관련 인터럽트를 비활성화한다. 레지스터(`CCCR.B.INIT = 0;`)만 직접 조작하는 방식은 이 비활성화된 인터럽트를 다시 활성화하지 못하므로, 수신(RX) 기능이 동작하지 않는 문제를 야기한다.

CAN1 채널은 `CanSM`의 관리를 받지 않으므로, EHAL 레이어에서 Bus-Off 감지와 복구 로직을 모두 책임져야 한다.

#### 4.2. 최종 해결 방안

프로젝트의 특수한 MCAL 제약사항(특히 `Can_17_McmCan_GetControllerErrorState`의 부재)을 고려했을 때, **사용자님께서 직접 테스트하여 작동함을 확인하신 초기 솔루션이 현재로서는 가장 실용적이고 효과적인 최선의 방법**이다.

이 방법은 Bus-Off 상태를 하드웨어 레지스터로 직접 감지하고, MCAL의 핵심 API를 사용하여 드라이버의 내부 상태를 동기화하며, 명시적인 인터럽트 재활성화를 통해 RX 기능을 보장한다.

**최종 수정 코드:**

```c
// EHAL/CAN_HAL/CAN_HAL.c

// Can_17_McmCan.h 헤더 파일 포함 필요
#include "Can_17_McmCan.h"

// ... (기존 코드)

void EhalCan1_BusOffRecovery_Task(void)
{
    // Bus-Off 상태를 하드웨어 레지스터로 직접 감지
    if (MODULE_CAN1.N[0].PSR.B.BO == 1U){
        vEhalCan_Can1BusOffState = 1U;
        
        // 하드웨어 INIT 비트 클리어 (SetControllerMode가 처리하지만, 안전을 위해 유지)
        MODULE_CAN1.N[0].CCCR.B.INIT = 0;
        
        // MCAL 드라이버 상태를 STARTED로 전환 및 복구
        (void)Can_17_McmCan_SetControllerMode (CAN_1, CAN_T_START);
        
        // 인터럽트 명시적 재활성화 (RX 복구에 기여)
        Can_17_McmCan_EnableControllerInterrupts(CAN_1);
    }
    else{
        vEhalCan_Can1BusOffState = 0U;
    }
}
```

---

## 5. 기대 효과

- **안정성 확보:** CAN1 채널의 Bus-Off 발생 시, 실제 환경에서 검증된 방식으로 통신이 안정적으로 복구됨.
- **실용성:** 프로젝트의 특수한 MCAL 제약사항을 우회하여 문제를 해결하는 현실적인 방안.
- **유지보수성:** 코드의 동작이 명확하고, 필요한 최소한의 조작으로 복구를 수행.
