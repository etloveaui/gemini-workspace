/*
 * BswSys.h
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#ifndef BSWSYS_H_
#define BSWSYS_H_

#include "Platform_Types.h"

typedef enum
{
  BSWSYS_MCU_ESR0_RESET        = 0x00U,      /* ESR0 reset     */
  BSWSYS_MCU_ESR1_RESET        = 0x01U,      /* ESR1 reset     */
  BSWSYS_MCU_SMU_RESET         = 0x02U,      /* SMU reset      */
  BSWSYS_MCU_SW_RESET          = 0x03U,      /* Software reset */
  BSWSYS_MCU_STM0_RESET        = 0x04U,      /* STM0 reset     */
  BSWSYS_MCU_STM1_RESET        = 0x05U,      /* STM1 reset     */
  BSWSYS_MCU_STM2_RESET        = 0x06U,      /* STM2 reset     */
  BSWSYS_MCU_STM3_RESET        = 0x07U,      /* STM3 reset     */
  BSWSYS_MCU_STM4_RESET        = 0x08U,      /* STM4 reset     */
  BSWSYS_MCU_STM5_RESET        = 0x09U,      /* STM5 reset     */
  BSWSYS_MCU_POWER_ON_RESET    = 0x0AU,      /* Power On reset */
  BSWSYS_MCU_CB0_RESET         = 0x0BU,      /* CB0 reset      */
  BSWSYS_MCU_CB1_RESET         = 0x0CU,      /* CB1 reset      */
  BSWSYS_MCU_CB3_RESET         = 0x0DU,      /* CB3 reset      */
  BSWSYS_MCU_EVRC_RESET        = 0x0EU,      /* EVRC Regulator Watchdog reset    */
  BSWSYS_MCU_EVR33_RESET       = 0x0FU,      /* EVR33 Regulator Watchdog reset   */
  BSWSYS_MCU_SUPPLY_WDOG_RESET = 0x10U,      /* Supply Watchdog reset            */
  BSWSYS_MCU_STBYR_RESET       = 0x11U,      /* Standby Regulator Watchdog reset */
  BSWSYS_MCU_LBIST_RESET       = 0x12U,      /* Reset from LBIST completion      */
  BSWSYS_MCU_RESET_MULTIPLE    = 0xFEU,      /* Multiple Reset Reasons found     */
  BSWSYS_MCU_RESET_UNDEFINED   = 0xFFU       /* Reset is undefined               */
} typBswSys_Mcu_Reset;

#define BSWSYS_TARGET_AXLE_UNDEFINED		(0U)
#define BSWSYS_TARGET_AXLE_FRONT			(1U)
#define BSWSYS_TARGET_AXLE_REAR				(2U)

extern void ShrHWIA_BswSys_SetTargetAxle(uint8 axle);
extern uint8 ShrHWIA_BswSys_GetReproStatusFlag(void);
extern typBswSys_Mcu_Reset ShrHWIA_BswSys_GetResetReason(void);
extern uint32 ShrHWIA_BswSys_GetResetStatus(void);
extern uint32 ShrHWIA_BswSys_GetSysTime(void);
extern void ShrHWIA_BswSys_McuReset(void);
extern void ShrHWIA_BswSys_ShutdownRequest(void);
extern float32 ShrHWIA_BswSys_GetCpuLoad(void);


#endif /* BSWSYS_H_ */
