/*
 * EhalSys.h
 *
 *  Created on: 2025. 2. 14.
 *      Author: dell
 */

#ifndef EHALSYS_H_
#define EHALSYS_H_

#include "Platform_Types.h"
#include "Mcu.h"
#include "EhalAdc.h"

#define BSWSYS_TARGET_AXLE_UNDEFINED		(0U)
#define BSWSYS_TARGET_AXLE_FRONT			(1U)
#define BSWSYS_TARGET_AXLE_REAR				(2U)

#define BSWSYS_ARTIFICIAL_LOAD_MAX_DEFAULT (20U)  // Default max artificial load (20%)
#define BSWSYS_TICKSPERSECOND 	 (100000000U)
#define BSWSYS_CORECYC_PER_SEC   (300000000UL)

extern Mcu_ResetType vBswSys_ResetReason;
extern uint32 vBswSys_RsetStatus;
extern uint8 vBswSys_TargetAxle;

extern float64 vBswSys_LoadPercent;
extern uint8 vBswSys_GenLoad_Percent;
extern uint8 vBswSys_GenMaxLoad_Percent;

//extern float64 vBswSys_ISR_ElapsedTime;			 // Obsolete remove


extern void BswSys_SetTaregetAxle(uint8 axle);
extern void BswSys_WdtResetControl(void);
extern uint8 BswSys_GetResetReason(void);
extern void BswSys_SetReproStatusFlag(uint8 flag);
extern uint8 BswSys_GetReproStatusFlag(void);
extern void BswSys_Init(void);

// CPU performance functions
extern void BswSys_ShutdownRequest(void);

// CPU Load HAL Start
extern void BswSys_GenCpuLoad_10ms(uint8 load_percent, uint8 max_load_percent);
//extern float64 BswSys_MeasureCpuLoad_100ms(uint8 *measure_count);
extern float64 BswSys_MeasCpuLoad_1000ms(void);
//extern uint32 BswSys_GetSysTime(void);
extern void   BswSys_CpuLoadWindowBegin(uint32 periodTick);
extern float64 BswSys_CpuLoadWindowEnd(void);
extern void   BswSys_IsrEntry(void);
extern void   BswSys_IsrExit(void);

//extern uint64  vBswCpu_Cat1BaseTick;
//extern uint64  vBswCpu_IdleBaseTick;
//extern volatile uint64 vIdleTicksGPIO;

#define BSWSYS_ISR_ENTRY()  BswSys_IsrEntry()
#define BSWSYS_ISR_EXIT()   BswSys_IsrExit()

#define BSWSYS_PROFILING_ENABLE   1U

#if (BSWSYS_PROFILING_ENABLE == 0U)
  #undef  BSWSYS_ISR_ENTRY
  #undef  BSWSYS_ISR_EXIT
  #define BSWSYS_ISR_ENTRY()   ((void)0)
  #define BSWSYS_ISR_EXIT()    ((void)0)
#endif


#endif /* EHAL_EHALSYS_EHALSYS_H_ */
