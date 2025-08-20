/*
 * BswSys.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#include "IfxStm_reg.h"
#include "Mcu.h"
#include "BswSys.h"
#include "Gpt.h"
#include "IfxGtm_reg.h"

#include "IfxScu_reg.h"
#include "EhalSys.h"

typBswSys_Mcu_Reset ShrHWIA_BswSys_GetResetReason(void)
{
	return vBswSys_ResetReason;
}

uint32 ShrHWIA_BswSys_GetResetStatus(void)
{
	return vBswSys_RsetStatus;
}

uint32 ShrHWIA_BswSys_GetSysTime(void)
{
	uint32 value;
	//return Gpt_GetTimeElapsed(GptConf_GptChannelConfiguration_GptChannelConfiguration_0);
	//return (uint16)GTM_TOM0_CH0_CN0;
	//value = (uint16)MODULE_GTM.TOM[0].CH1.CN0.U;
	value = STM0_TIM0.U;
	return value;
}

void ShrHWIA_BswSys_McuReset(void)
{
    Mcu_PerformReset(); // 2024.11.18 G.W.Ham
}
