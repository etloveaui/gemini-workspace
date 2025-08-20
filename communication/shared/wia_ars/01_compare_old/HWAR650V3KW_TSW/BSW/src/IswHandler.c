/*
 * BswTask.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */


#include "Platform_Types.h"
#include "BswAdc.h"
#include "BswDac.h"
#include "BswTest.h"
#include "BswPwm.h"
#include "BswXcp.h"
#include "IswHandler.h"
#include "BuildTime.h"
#include "BswAdc_Cbk.h"


typedef struct{
	uint32 count_Init;
	uint32 count_Init2;
	uint32 count_Idle;
	uint32 count_1ms;
	uint32 count_2ms;
	uint32 count_5ms;
	uint32 count_10ms;
	uint32 count_20ms;
	uint32 count_50ms;
	uint32 count_100ms;
}typOsTask_Count;

typOsTask_Count vBswTask_Count;



void ShrHWIA_IswHandler_Init(void)
{
	vBswTask_Count.count_Init++;
}

void ShrHWIA_IswHandler_Init2(void)
{
	vBswTask_Count.count_Init2++;
}


uint16 vIswHandler_CbkIsrCount;

void ShrHWIA_IswHandler_Idle(void)
{
	vBswTask_Count.count_Idle++;
	if(vIswHandler_CbkIsrCount != vBswAdc_CbkIsrCount)
	{
		vIswHandler_CbkIsrCount = vBswAdc_CbkIsrCount;
		BswTest_DAC_Idle_Task();	// Test_DAC_Example
	}
	else{

	}
	BswTest_Pwm_Idle_Task();									// Test_PWM_Module_ON_Example
}

void ShrHWIA_IswHandler_1ms(void)
{
	vBswTask_Count.count_1ms++;
	BswTest_CanRx_1ms_Task();
	BswTest_CanTx_1ms_Task();
	BswTest_Sent_1ms_Task();
	BswTest_GetSysTime();
}

void ShrHWIA_IswHandler_10ms(void)
{
	vBswTask_Count.count_10ms++;
	BswTest_CanRx_10ms_Task();  // Test Example
	BswTest_Adc_10ms_Task();	// Test Example
#ifdef TEST_CAN_ON
	VectorTest_Task_10ms();		// Remove_after_a_test.
#endif
	BswTest_CanTx_10ms_Task();  // Test Example
}

void ShrHWIA_IswHandler_100ms(void)
{
	vBswTask_Count.count_100ms++;
	BswTest_McuReset();
	BswTest_Dio_100ms_Task();
	BswTest_Nvm_100ms_Task();
	BswTest_Wdt_100ms_Task();
	BswTest_Sys_100ms_Task();
}

void ShrHWIA_IswHandler_2ms(void)
{
	vBswTask_Count.count_2ms++;
}

void ShrHWIA_IswHandler_5ms(void)
{
	vBswTask_Count.count_5ms++;
	BswXcp_Task_5ms();
}

void ShrHWIA_IswHandler_20ms(void)
{
	vBswTask_Count.count_20ms++;
}

void ShrHWIA_IswHandler_50ms(void)
{
	vBswTask_Count.count_50ms++;
}
