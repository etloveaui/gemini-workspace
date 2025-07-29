# ARS 제어기 CAN1 버스 오프 복구 문제 심층 분석 및 해결 방안 로그

## 1. 문제 정의 및 초기 현상

**작업 ID:** `ars-can-busoff-recovery-fix`
**ARS 정의:** Anti-Rolling Stabilizer

ARS 제어기의 CAN1 채널에서 Bus-Off 이벤트 발생 시, 정상적인 통신 상태로 복구되지 않는 문제가 발생했습니다.

**상세 현상:**
- Bus-Off 복구 로직이 실행된 후, 송신(TX)은 재개되는 것처럼 보였으나 **수신(RX) 관련 기능이 완전히 멈췄습니다.**
- 이로 인해 CAN RX 타임아웃 감지를 포함한 모든 수신 기반 로직이 동작하지 않았습니다.

**초기 복구 시도 및 사용자 테스트 결과 (핵심 정정):**
- **1차 시도:** `MODULE_CAN1.N[0].CCCR.B.INIT = 0;` (하드웨어 레지스터 직접 제어)만으로 복구를 시도했으나, RX 기능이 살아나지 않는 등 불완전한 복구 현상이 발생했습니다.
- **2차 시도 (사용자 테스트 성공):** `Can_17_McmCan_SetControllerMode(CAN_1, CAN_T_START);` API만을 호출했을 때, Bus-Off 복구가 정상적으로 이루어지고 RX 기능도 회복됨을 사용자께서 직접 테스트하여 확인하셨습니다.
- **초기 분석 방향:** 이 현상을 바탕으로, 문제의 원인이 단순한 하드웨어 상태 복구가 아닌, MCAL 드라이버의 내부 상태(특히 인터럽트)와 관련된 것일 수 있다는 가설을 세우고 심층 분석을 시작했습니다.

## 2. 심층 분석: MCAL API의 역할과 내부 동작

문제의 근본 원인을 파악하고 최적의 해결 방안을 도출하기 위해 하드웨어 매뉴얼, MCAL 문서, 관련 소스 코드를 종합적으로 분석했습니다.

### 2.1. 하드웨어 동작 분석 (MCU User Manual 기반)

- **근거 자료:** `projects/hwar650v3kw_2nd_sw_branch3/DOC/[EN]CAN_AURIX_TC3xx_Part2-1946-2124.pdf.json` (TC364DP User Manual)
- **Bus-Off 시 하드웨어 동작:** 컨트롤러가 Bus-Off 상태에 진입하면, 하드웨어는 자동으로 `CCCR` (CC Control Register) 레지스터의 `INIT` 비트를 '1'로 설정하여 CAN 버스와의 통신을 중단시킵니다.
  > **참조 (pg23_1):** "Software initialization is started by setting bit CCCRi.INIT, either by software or by a hardware reset, or by going Bus_Off."
- **하드웨어 레벨 복구:** `INIT` 비트를 다시 '0'으로 클리어하면, 하드웨어는 버스 유휴 상태를 감지한 후 통신에 다시 참여할 준비를 합니다.
  > **참조 (pg23_1):** "Resetting CCCRi.INIT finishes the software initialization. Afterwards the Bit Stream Processor BSP synchronizes itself to the data transfer on the CAN bus..."
- **분석:** 하드웨어 관점에서는 `INIT` 비트 제어만으로 복구가 시작되는 것처럼 보이지만, 이는 MCAL 소프트웨어 계층의 상태를 고려하지 않은 것입니다.

### 2.2. MCAL API 동작 분석 (`Can_17_McmCan.c` 소스 및 MCAL User Manual 기반)

- **핵심 API:** `Can_17_McmCan_SetControllerMode(Controller, CAN_T_START)`
- **근거 자료:**
    - `projects/hwar650v3kw_2nd_sw_branch3/HWAR650V3KW_BSW/Sourcecode/mcal/MCAL_Modules/Can_17_McmCan/ssc/src/Can_17_McmCan.c`
    - `projects/hwar650v3kw_2nd_sw_branch3/DOC/[MCAL]_UM_Can_17_McmCan_[EN].json`
- **분석:** 이 함수는 단순한 레지스터 조작 래퍼(Wrapper)가 아닙니다. 컨트롤러를 `STOPPED`에서 `STARTED` 상태로 전환하는 공식적인 상태 머신 전환 절차이며, 내부적으로 `Can_17_McmCan_lSetModeStart` 함수를 호출하여 다음과 같은 복합적인 작업을 수행합니다.
    1.  **하드웨어 통신 재개:** `NodeRegAddressPtr->CCCR.B.INIT = CAN_17_MCMCAN_BIT_RESET_VAL;` 코드를 통해 `INIT` 비트를 '0'으로 클리어합니다.
    2.  **인터럽트 재활성화:** `NodeRegAddressPtr->IE.U |= CoreConfigPtr->...CanEnableInterruptMask;` 코드를 통해 **Bus-Off 발생 시 비활성화되었을 수 있는 모든 관련 인터럽트를 `IE` (Interrupt Enable) 레지스터에 다시 설정**합니다.
        > **참조 (MCAL UM pg121_2):** `Can_17_McmCan_SetControllerMode`의 "SFR accessed" 목록에 `CAN_N_IE(w)`가 명시되어 있습니다. 이는 이 함수가 `IE` 레지스터를 조작하여 인터럽트를 활성화함을 의미합니다.
    3.  **내부 상태 동기화:** MCAL 드라이버가 관리하는 컨트롤러 상태 변수를 `STARTED`로 갱신합니다.
- **결론:** `SetControllerMode` API는 하드웨어와 소프트웨어(MCAL)의 상태를 모두 동기화하고, 완전한 복구에 필요한 모든 절차를 포함하고 있습니다. 사용자님의 테스트에서 이 API만으로 복구가 성공한 것은 이 함수가 내부적으로 필요한 모든 복구 작업을 수행하기 때문입니다.

### 2.3. `Can_17_McmCan_EnableControllerInterrupts`의 역할 및 최종 불필요성

- **근거 자료:** `projects/hwar650v3kw_2nd_sw_branch3/DOC/[MCAL]_UM_Can_17_McmCan_[EN].json` (pg124_2)
- **분석:** 이 함수는 "주어진 CAN 컨트롤러의 허용된 인터럽트를 다시 활성화한다"고 명시되어 있습니다. 내부적으로 `CanDisableIntrpCountPtr`라는 카운터를 관리하며, 이 카운터가 0이 될 때만 실제로 `IE` 레지스터를 조작하여 인터럽트를 활성화합니다.
- **최종 불필요성:** `Can_17_McmCan_SetControllerMode(CAN_1, CAN_T_START)`가 이미 내부적으로 인터럽트를 활성화하는 로직을 포함하고 있으므로, `Can_17_McmCan_EnableControllerInterrupts`의 추가 호출은 **중복**입니다. 사용자님의 최신 테스트 결과(`SetControllerMode`만으로 성공)는 이 중복 호출이 실제로는 필요 없음을 명확히 보여줍니다. 다만, 이 중복 호출이 `CanDisableIntrpCountPtr`와 같은 내부 카운터의 상태에 따라 방어적인 역할을 할 수는 있지만, 필수적인 것은 아닙니다.

### 2.4. `MODULE_CAN1.N[0].CCCR.B.INIT = 0;`의 역할 및 최종 불필요성

- **분석:** 이 코드는 하드웨어 레지스터를 직접 조작하여 `INIT` 비트를 클리어하는 것입니다.
- **최종 불필요성:** `Can_17_McmCan_SetControllerMode(CAN_1, CAN_T_START)` 함수가 내부적으로 `CCCR.B.INIT` 비트를 '0'으로 설정하는 로직을 포함하고 있으므로, 이 직접 레지스터 조작은 **중복**입니다. 또한, 이 직접 조작만으로는 MCAL 드라이버의 내부 상태(특히 인터럽트 활성화)를 동기화하지 못하므로, 단독으로는 불완전한 복구를 초래합니다.

## 3. 부트 SW (CAN0)와 메인 어플리케이션 (CAN1)의 Bus-Off 복구 방식 차이점 분석

`TC364_GINT_BOOT2` 부트 SW의 CAN0 채널이 `MODULE_CAN0.N[0].PSR.B.BO` 읽기와 `INIT` 비트 설정만으로 Bus-Off 복구가 잘 되는 반면, 메인 어플리케이션의 CAN1은 `SetControllerMode`가 필수적이었던 이유를 심층 분석했습니다.

- **근거 자료:**
    - `projects/hwar650v3kw_2nd_sw_branch3/TC364_GINT_BOOT2/0_Src/AppSw/FBL/FblMgr.c`
    - `projects/hwar650v3kw_2nd_sw_branch3/TC364_GINT_BOOT2/0_Src/AppSw/Tricore/DemoMcal/Demo_Can_17_McmCan/Can_17_McmCan_Demo.c`

### 3.1. 부트 SW (`TC364_GINT_BOOT2`)의 CAN 동작 방식

- **`FblMgr.c`의 `FblMgr_CanBusOffRecovery`:**
    ```c
    void FblMgr_CanBusOffRecovery(void)
    {
    	uint8 bus_off_flag;
    	bus_off_flag = MODULE_CAN0.N[0].PSR.B.BO; // CAN0의 Bus-Off 상태를 하드웨어 레지스터로 직접 확인
    	if(bus_off_flag == 1){
    		MODULE_CAN0.N[0].CCCR.B.INIT = 0; // INIT 비트 클리어
    	}
    }
    ```
    이 함수는 MCAL API를 사용하지 않고 하드웨어 레지스터를 직접 조작합니다.
- **`Can_17_McmCan_Demo.c`의 역할:** 이 파일은 부트 SW 환경에서 MCAL CAN 드라이버를 초기화하는 데 사용됩니다. `Can_17_McmCan_Init` 및 `Can_17_McmCan_SetControllerMode`와 같은 MCAL API를 호출합니다.
- **`FblMgr.c`와 `Can_17_McmCan_Demo.c`의 관계:** `FblMgr.c`는 `Can_17_McmCan_Write`와 같은 MCAL API를 사용하여 CAN 메시지를 송신하지만, CAN 드라이버의 초기화 및 상태 전환(`Init`, `SetControllerMode`)은 직접 수행하지 않는 것으로 보입니다. 이는 `Can_17_McmCan_Demo.c` 또는 다른 초기화 루틴이 MCAL 드라이버를 초기화하고 `CAN_T_START` 상태로 전환한 후, `FblMgr.c`는 이미 초기화된 MCAL 드라이버의 기능을 활용하는 구조임을 시사합니다.

### 3.2. 차이점의 근본 원인: MCAL 드라이버의 "설정(Configuration)" 차이

두 환경의 Bus-Off 복구 동작 차이는 **MCAL 드라이버의 "활성 관리" 수준 또는 "설정(Configuration)" 차이**에 있습니다.

-   **메인 어플리케이션 (CAN1):**
    -   메인 어플리케이션의 MCAL은 `Can_17_McmCan_SetControllerMode`와 같은 API를 통해 CAN 컨트롤러의 상태를 **적극적으로 관리**하도록 설정되어 있습니다.
    -   Bus-Off 발생 시, 이 MCAL 설정은 내부적으로 컨트롤러의 상태를 `STOPPED`로 변경하고, **안전을 위해 관련 인터럽트들을 비활성화**합니다.
    -   따라서, `MODULE_CAN1.N[0].CCCR.B.INIT = 0;`만으로는 하드웨어의 `INIT` 비트만 클리어될 뿐, MCAL 드라이버가 비활성화한 인터럽트들은 여전히 비활성화된 상태로 남아있게 되어 RX 기능이 복구되지 않았습니다.
    -   `Can_17_McmCan_SetControllerMode(CAN_1, CAN_T_START)`는 MCAL 드라이버의 내부 상태 머신을 `STARTED`로 전환하면서, **비활성화된 인터럽트들을 다시 활성화하는 역할**을 수행하므로 메인 어플리케이션에서 필수적입니다.

-   **부트 SW (CAN0):**
    -   부트 SW의 MCAL은 메인 어플리케이션의 MCAL과 달리, Bus-Off 발생 시 인터럽트를 비활성화하는 등의 "적극적인 상태 관리"를 수행하지 않도록 **"수동적"이거나 "경량화"된 방식으로 설정**되어 있을 가능성이 높습니다.
    -   이러한 환경에서는 Bus-Off 발생 시 MCAL 드라이버가 인터럽트를 비활성화하지 않으므로, `MODULE_CAN0.N[0].CCCR.B.INIT = 0;`만으로도 하드웨어 레벨에서 통신이 재개되고 인터럽트도 활성 상태를 유지하여 정상적으로 복구가 되는 것입니다.
    -   즉, 부트 SW의 MCAL은 Bus-Off 발생 시 MCAL 드라이버의 내부 상태가 크게 변경되지 않으므로, 하드웨어 레지스터 조작만으로도 충분히 복구가 가능합니다.

**결론:** 두 환경의 차이는 MCAL 드라이버의 **"설정(Configuration)" 차이**이며, 이 설정이 Bus-Off 발생 시 MCAL이 CAN 컨트롤러의 상태와 인터럽트를 어떻게 관리하는지에 영향을 미칩니다.

## 4. 검토된 다른 대안들 및 기각 사유

문제 해결 과정에서 다양한 대안들이 검토되었으나, 현재 프로젝트의 특수한 환경과 MCAL 제약사항으로 인해 다음과 같은 이유로 기각되었습니다.

-   **`Can_17_McmCan_MainFunction_BusOff`:**
    -   **역할:** 이 함수는 Bus-Off 상태를 감지하고 상위 레이어(CanIf -> CanSM)에 **보고**하는 역할만 할 뿐, 직접적인 복구(Controller 재시작)를 수행하지 않습니다.
    -   **기각 사유:** CAN1 채널은 `CanSM`의 관리를 받지 않으므로, 이 함수를 사용하더라도 복구를 명령할 주체가 없어 컨트롤러가 영원히 `STOPPED` 상태에 머무르게 됩니다.

-   **`Can_17_McmCan_IsrBusOffHandler`:**
    -   **역할:** Bus-Off 인터럽트 발생 시 호출되는 ISR 핸들러입니다. 이 함수는 Bus-Off 상황을 정리하고 컨트롤러의 상태를 `STOPPED`로 변경한 뒤, 상위 레이어(`CanIf`)에 "Bus-Off가 발생했다"고 보고하는 역할만 합니다. 스스로 컨트롤러를 재시작하지 않습니다.
    -   **기각 사유:** `MainFunction_BusOff`와 동일하게 `CanSM` 부재로 인해 복구 명령이 내려오지 않아 컨트롤러가 `STOPPED` 상태에 머무르게 됩니다.

-   **`Can_17_McmCan_GetControllerErrorState` 및 `Can_17_McmCan_GetControllerMode`:**
    -   **역할:** 이 함수들은 MCAL 드라이버가 컨트롤러의 에러 상태(`CAN_ERRORSTATE_BUSOFF`)나 현재 모드(`CAN_CS_STOPPED`)를 추상화된 방식으로 제공하는 이상적인 API입니다.
    -   **기각 사유:** 현재 프로젝트의 MCAL 빌드 설정에서 CAN1 채널에 대해 해당 함수들이 **생성되지 않았음이 확인**되었습니다. 따라서 이 API들을 사용할 수 없습니다. Bus-Off 상태 감지를 위해 `MODULE_CAN1.N[0].PSR.B.BO` 레지스터를 직접 읽는 것이 유일한 방법입니다.

-   **레지스터 직접 제어 방식 (MCAL 미사용):**
    -   **역할:** `MODULE_CAN1.N[0].CCCR.B.INIT = 0;`와 같이 하드웨어 레지스터를 직접 조작하여 복구를 시도하는 방식입니다.
    -   **기각 사유:** 이 방식은 MCAL의 추상화 계층을 파괴하고, 드라이버와 하드웨어의 상태 불일치를 유발하여 예측 불가능한 심각한 오류를 초래할 수 있습니다. 특히 MCAL이 인터럽트를 비활성화하는 등 적극적으로 상태를 관리하는 환경에서는 불완전한 복구(RX 기능 미회복)를 야기합니다.

## 5. 최종 확정된 해결 방안 및 코드

#### 5.1. 근본 원인

**"불완전한 복구 절차로 인한 MCAL 드라이버와 하드웨어 간의 상태 불일치"**

Bus-Off 발생 시 메인 어플리케이션의 MCAL 드라이버는 안전을 위해 내부적으로 컨트롤러 상태를 `STOPPED`로 변경하고 관련 인터럽트를 비활성화합니다. `MODULE_CAN1.N[0].CCCR.B.INIT = 0;`와 같은 하드웨어 레지스터 직접 조작 방식은 이 비활성화된 인터럽트를 다시 활성화하지 못하므로, 수신(RX) 기능이 동작하지 않는 문제를 야기합니다.

CAN1 채널은 `CanSM`의 관리를 받지 않으므로, EHAL 레이어에서 Bus-Off 감지와 복구 로직을 모두 책임져야 합니다.

#### 5.2. 최종 해결 방안

프로젝트의 특수한 MCAL 제약사항(특히 `Can_17_McmCan_GetControllerErrorState`와 같은 상태 확인 API의 부재)을 고려했을 때, **사용자님께서 직접 테스트하여 작동함을 확인하신 `Can_17_McmCan_SetControllerMode(CAN_1, CAN_T_START);` API만을 사용하는 것이 현재로서는 가장 실용적이고 효과적인 최선의 방법입니다.**

이 방법은 Bus-Off 상태를 하드웨어 레지스터로 직접 감지하고, MCAL의 핵심 API를 사용하여 드라이버의 내부 상태를 동기화하며, 필요한 인터럽트 활성화를 `SetControllerMode` 내부에서 처리하여 RX 기능을 보장합니다.

**최종 수정 코드:**

```c
// EHAL/CAN_HAL/CAN_HAL.c

// Can_17_McmCan.h 헤더 파일 포함 필요
#include "Can_17_McmCan.h"

// ... (기존 코드)

void EhalCan1_BusOffRecovery_Task(void)
{
    // Bus-Off 상태를 하드웨어 레지스터로 직접 감지 (MCAL API 부재로 인한 유일한 방법)
    if (MODULE_CAN1.N[0].PSR.B.BO == 1U)
    {
        vEhalCan_Can1BusOffState = 1U;
        
        /* 
         * MCAL 드라이버 상태를 STARTED로 전환 및 복구.
         * 이 함수는 내부적으로 하드웨어 INIT 비트 클리어 및 필요한 인터럽트 활성화를 모두 처리합니다.
         * 사용자 테스트를 통해 이 API만으로 완전한 복구가 확인되었습니다.
         */
        (void)Can_17_McmCan_SetControllerMode(CAN_1, CAN_T_START);
    }
    else
    {
        vEhalCan_Can1BusOffState = 0U;
    }
}
```

## 6. 기대 효과

-   **안정성 확보:** CAN1 채널의 Bus-Off 발생 시, 실제 환경에서 검증된 방식으로 통신이 안정적으로 복구됩니다.
-   **실용성:** 프로젝트의 특수한 MCAL 제약사항을 우회하여 문제를 해결하는 현실적인 방안입니다.
-   **유지보수성:** 코드의 동작이 명확하고, 필요한 최소한의 MCAL API 호출로 복구를 수행합니다.
-   **기술적 근거 확보:** 모든 분석 과정과 결론이 상세하게 기록되어 향후 유사 문제 발생 시 참조 자료로 활용될 수 있습니다.
