/*
 * BswPwm_Cbk.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */
#include "Platform_Types.h"

uint16 vBswPwm_CbkIsrCount;

void ShrHWIA_BswPwm_Cbk_ISR(void)
{
	vBswPwm_CbkIsrCount++;
}

