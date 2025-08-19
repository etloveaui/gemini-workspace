#include "EhalSys.h"
#include "IfxScu_reg.h"
#include "Os.h"
#include "stdlib.h"
#include "IfxStm_reg.h"
#include "Ifx_Ssw_Infra.h"
#include "TLF35584.h"
//#include "IfxDmu_reg.h"

#define BSWSYS_WDT_RESET_MAX	(9U)

Mcu_ResetType vBswSys_ResetReason = 0;
uint8 vBswSys_ResetReason2 = 0;
uint32 vBswSys_RsetStatus;
uint8 vBswSys_TargetAxle = 0; //0: Undefined 1:Front, 2:Rear

volatile uint8 vBswSys_ResetReasonFirst;
uint8 vBswSys_ReproStatus;

//float64 vBswSys_ISR_ElapsedTime;

volatile uint64  vBswSys_Cat1ElapsedTick = 0ULL;
volatile uint64 vBswSys_Cat1BaseTick = 0ULL;
volatile uint64 vBswSys_IdleBaseTick = 0ULL;

static uint32    vBswSys_IsrNestCnt      = 0U;
static uint32    vBswSys_IsrEntryTick    = 0U;
static uint32    vBswSys_WindowTick      = 0U;
float64 vBswSys_LoadPercent = 0;
uint8 vBswSys_GenLoad_Percent = 0;
uint8 vBswSys_GenMaxLoad_Percent = 0;

//#pragma section farbss="StandByRam"
//#pragma align 4
#pragma noclear
volatile uint32 vBswSys_WdtResetCount __at(0x90000000);
volatile uint32 vBswSys_ReproStatusStdbyRam __at(0x90000004); // 2025.06.06 G.W.Ham. If a software reset is triggered by reprogramming, the flag will be set.
#pragma clear
//#pragma section farbss restore

void BswSys_Init(void)
{
//	vBswSys_ReproStatus = vBswSys_ReproStatusStdbyRam;
	vBswSys_ReproStatus = (uint8)(vBswSys_ReproStatusStdbyRam & 0xFFu);
	BswSys_WdtResetControl();
}

void BswSys_SetTaregetAxle(uint8 axle)
{
	vBswSys_TargetAxle = axle;
}

uint8 BswSys_GetResetReason(void)
{
	vBswSys_RsetStatus = SCU_RSTSTAT.U;

	vBswSys_ResetReason = Mcu_GetResetReason();
	Mcu_ClearColdResetStatus(); // Clear reset reason

	return vBswSys_ResetReason;
}

void BswSys_WdtResetControl(void)
{
	  unsigned short safetyPassword;

	  vBswSys_ResetReasonFirst = BswSys_GetResetReason();

	  if(vBswSys_ResetReasonFirst == MCU_SMU_RESET){
		  if(vBswSys_WdtResetCount<BSWSYS_WDT_RESET_MAX){
			  safetyPassword = Ifx_Ssw_getSafetyWatchdogPassword();
			  Ifx_Ssw_clearSafetyEndinit(safetyPassword);
			  SCU_WDTS_CON1.B.CLRIRF = 1U;
			  Ifx_Ssw_setSafetyEndinit(safetyPassword);
			  vBswSys_WdtResetCount++;
		  }
		  else{
			  //do nothing : Go to MCU down
		  }
	  }
	  else{
		  //do nothing
	  }
}

void BswSys_SetReproStatusFlag(uint8 flag)
{
	vBswSys_ReproStatusStdbyRam = flag;
}

uint8 BswSys_GetReproStatusFlag(void)
{
	return vBswSys_ReproStatus;
}

void BswSys_GenCpuLoad_10ms(uint8 load_percent, uint8 max_load_percent)
{
    volatile uint32 dummy = 0U;
    uint32 loadTicks = 0U;
    uint32 startTime = 0U;
    uint8 actual_max_load = 0U;

    // Use default max if not set
    if (max_load_percent == 0U) {
        actual_max_load = BSWSYS_ARTIFICIAL_LOAD_MAX_DEFAULT;
    }
    else {
        actual_max_load = max_load_percent;
    }

    // Limit to max
    if (load_percent > actual_max_load) {
        load_percent = actual_max_load;
    }
    else {
        /* no action */
    }

    // Skip if 0%
    if (load_percent == 0U) {
        return;
    }

    // Calculate load ticks (1% = 10,000 ticks at 100MHz)
    loadTicks = (uint32)load_percent * 10000U;

    // Run dummy load loop
    startTime = STM0_TIM0.U;
    while ((STM0_TIM0.U - startTime) < loadTicks) {
        dummy += (dummy * 7U) + 13U;
        dummy = dummy % 65537U;
    }
}

//static float64 BswSys_ClampCpuLoad(float64 load)
//{
//    if (load < 0.0f) {
//        return 0.0f;
//    }
//    else if (load > 100.0f) {
//        return 100.0f;
//    }
//    else {
//        return load;
//    }
//}

//float64 BswSys_MeasureCpuLoad_100ms(uint8 *measure_count)
//{
//    float64 TicksPerPeriod = 0.0f;
//    Os_StopwatchTickType TimeInIdle = 0;
//    float64 PercentInIdle = 0.0f;
//    float64 Load = 0.0f;
//
//    if (*measure_count == 0) {
//        return 0.0f;
//    }
//
//    TicksPerPeriod = 0.1f * BSWSYS_TICKSPERSECOND;   /* 100ms @ 100MHz */
//    TimeInIdle = Os_GetIdleElapsedTime(OS_CORE_CURRENT);
//
//    PercentInIdle = 100.0f * ((float64)TimeInIdle / TicksPerPeriod);
//    Load = 100.0f - PercentInIdle;
//
//    Os_ResetIdleElapsedTime(OS_CORE_CURRENT);
//    (*measure_count)--;
//
//    return BswSys_ClampCpuLoad(Load);
//}

//float64 vBswSys_CpuLoad_1000ms = 0.0f;
//float64 TicksPerPeriod = 0.0f;
//Os_StopwatchTickType TimeInIdle = 0;
//float64 PercentInIdle = 0.0f;

//float64 BswSys_MeasureCpuLoad_1000ms(void)
//{
//
////    float64 Load = 0.0f;
//
////    if (*measure_count == 0) {
////        return 0.0f;
////    }
//
//    TicksPerPeriod = 1.0f * BSWSYS_TICKSPERSECOND;   /* 1000ms @ 100MHz */
//    TimeInIdle = Os_GetIdleElapsedTime(OS_CORE_CURRENT);
//
//    PercentInIdle = 100.0f * (((float64)TimeInIdle - (float64)vBswSys_ISR_ElapsedTime) / TicksPerPeriod);
//    vBswSys_ISR_ElapsedTime = 0;
//    vBswSys_CpuLoad_1000ms = 100.0f - PercentInIdle;
//
//    Os_ResetIdleElapsedTime(OS_CORE_CURRENT);
//
//    return BswSys_ClampCpuLoad(vBswSys_CpuLoad_1000ms);
//}

float64 BswSys_MeasCpuLoad_1000ms(void)
{

	/* 1 s  = 100 000 000 tick @100 MHz */

    return BswSys_CpuLoadWindowEnd();	/* Cat-1 + Cat-2 + Task */
}

//uint32 BswSys_GetSysTime(void)
//{
//	uint32 value;
//
//	value = STM0_TIM0.U;
//	return value;
//}

// CPU-Load  HAL
void BswSys_CpuLoadWindowBegin(uint32 periodTick)
{
	vBswSys_WindowTick = periodTick;

    vBswSys_Cat1BaseTick = vBswSys_Cat1ElapsedTick;                   /* Cat-1 */
    vBswSys_IdleBaseTick = Os_GetIdleElapsedTime(OS_CORE_CURRENT);    /* Idle */
}

float64 BswSys_CpuLoadWindowEnd(void)
{
    uint64 idleNow = Os_GetIdleElapsedTime(OS_CORE_CURRENT);
    uint64 cat1Now = vBswSys_Cat1ElapsedTick;

    uint64 idleDelta = idleNow - vBswSys_IdleBaseTick;
    uint64 cat1Delta = cat1Now - vBswSys_Cat1BaseTick;

    uint64 realIdle = (idleDelta > cat1Delta) ? (idleDelta - cat1Delta) : 0ULL;

    float64 pctIdle = 100.0 * ((float64)realIdle / (float64)vBswSys_WindowTick);
    float64 pctLoad = 100.0 - pctIdle;
    if (pctLoad < 0.0)   pctLoad = 0.0;
    if (pctLoad > 100.0) pctLoad = 100.0;

    return pctLoad;
}

void BswSys_IsrEntry(void)
{
    if (vBswSys_IsrNestCnt++ == 0U)
        vBswSys_IsrEntryTick = STM0_TIM0.U;
}

void BswSys_IsrExit(void)
{
    if (--vBswSys_IsrNestCnt == 0U)
        vBswSys_Cat1ElapsedTick += (uint64)(STM0_TIM0.U - vBswSys_IsrEntryTick);
}

void BswSys_ShutdownRequest(void)
{
    vTLF35584_Panels.force_shutdown_request = TRUE;
}
