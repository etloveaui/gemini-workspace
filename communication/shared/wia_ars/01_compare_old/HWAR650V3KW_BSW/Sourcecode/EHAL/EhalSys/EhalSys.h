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

extern Mcu_ResetType vBswSys_ResetReason;
extern uint32 vBswSys_RsetStatus;

extern void BswSys_WdtResetControl(void);
extern uint8 BswSys_GetResetReason(void);


#endif /* EHAL_EHALSYS_EHALSYS_H_ */
