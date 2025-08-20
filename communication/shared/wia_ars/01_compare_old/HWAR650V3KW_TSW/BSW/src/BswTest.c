/*
 * BswTest.c
 *
 *  Created on: 2024. 12. 19.
 *      Author: jaegalrang
 */
#include "BswSent.h"
#include "BswTest.h"
#include "BswAdc.h"
#include "BswDac.h"
#include "BswGpt.h"
#include "BswPwm.h"
#include "BswIcu.h"
#include "BswCan.h"

#include "BswSys.h"
#include "BswDio.h"
#include "BswXcp.h"
#include "BswNvm.h"
#include "IswHandler.h"

#include "BswAdc_Cbk.h"

uint16 vBswTest_Pwm_DutyCycle_U = 3125;
uint16 vBswTest_Pwm_DutyCycle_V = 3125;
uint16 vBswTest_Pwm_DutyCycle_W = 3125;

uint8 vBswTest_Pwm_Enable_F = FALSE;
uint8 vBswTest_Pwm_Module_Ch_F = 0;
uint8 vBswTest_Pwm_Module_Ch = 0;
uint8 vBswTest_Pwm_Module_Ch_State = 0;
uint16 vBswTest_Pwm_Module_Ch_Value = 3125;
uint32 vBswTest_Pwm_Period_SetValue = 6250;	//PeriodVal: Period value in ticks (1 tick = 0.01us)
uint16 vBswTest_Pwm_Deadtime_SetValue = 200;	//DeadTimeVal: Dead time value in ticks (1 tick = 0.01us)
volatile uint32 vBswTest_WdtCount;
uint8 vBswTest_Wdt_Testcase;

//Debug
DebugADC_t vBswTest_AdcValue;
DebugENC_t vBswTest_EncValue;

#define SRVVER_BOOT_VER_ADDR	(0x8003FFE0u)
#define SRVVER_BSW_VER_ADDR		(0x8013FFE0u)
#define SRVVER_ISW_VER_ADDR		(0x801BFFD0u)
#define SRVVER_ASW_VER_ADDR		(0x801BFFE0u)

volatile const char vSrvVer_AswVersion[16] __at(SRVVER_ASW_VER_ADDR) = "ARS_ASW_123";
volatile const char vSrvVer_IswVersion[16] __at(SRVVER_ISW_VER_ADDR) = "ARS_ISW_456";

void BswTest_Pwm_Idle_Task(void)
{
	ShrHWIA_BswPwm_Enable(vBswTest_Pwm_Enable_F);							// Test_PWM_Module_ON_Example

	if(vBswTest_Pwm_Enable_F == FALSE)
	{
		ShrHWIA_BswPwm_SetPeriod(vBswTest_Pwm_Period_SetValue);		// Test_PWM_Frequency_SET_Example
		ShrHWIA_BswPwm_SetDeadTime(vBswTest_Pwm_Deadtime_SetValue);		// Test_PWM_DeadTime_SET_Example

		if(vBswTest_Pwm_Module_Ch_F == TRUE)		ShrHWIA_BswPwm_ChOutEnable(vBswTest_Pwm_Module_Ch,vBswTest_Pwm_Module_Ch_State,vBswTest_Pwm_Module_Ch_Value);
		else										ShrHWIA_BswPwm_Output_Disable();
	}
	else{}
}


void BswTest_PWM_ISR(void)
{	//2024.12.26 G.W.Ham Comment out for build
	ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_HS_U, vBswTest_Pwm_DutyCycle_U);
	ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_LS_U, vBswTest_Pwm_DutyCycle_U);
	ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_HS_V, vBswTest_Pwm_DutyCycle_V);
	ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_LS_V, vBswTest_Pwm_DutyCycle_V);
	ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_HS_W, vBswTest_Pwm_DutyCycle_W);
	ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_LS_W, vBswTest_Pwm_DutyCycle_W);
}

void BswTest_Adc_10ms_Task(void)
{
	vBswTest_AdcValue.VDD15V	= ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_VDD_15V);
	vBswTest_AdcValue.VDD5V = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_VDD_5V0);
	vBswTest_AdcValue.LVDC = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_LV);
	vBswTest_AdcValue.IG = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_IG);
	vBswTest_AdcValue.Vmcu = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_VUC_3V3);
	vBswTest_AdcValue.Vcom = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_VCOM_5V0);
	vBswTest_AdcValue.Vtr1 = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_VT1_5V0);
	vBswTest_AdcValue.Vtr2 = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_VT2_5V0);
	vBswTest_AdcValue.Vref = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_VREF_5V0);
	vBswTest_AdcValue.Tpcb = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_PCB_TEMP);
	vBswTest_AdcValue.Tigbt = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_IPM_TEMP);
	vBswTest_AdcValue.Tmot = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_MOT_TEMP);
}

void BswTest_ICU_SENS2(void)
{
	vBswTest_EncValue.EncA_Frequency = ShrHWIA_BswIcu_GetFrequency(BSWICU_CH_SENS1_PWM);
	vBswTest_EncValue.EncA_Duty = ShrHWIA_BswIcu_GetDuty(BSWICU_CH_SENS1_PWM);
}

void BswTest_Adc_ISR(void)
{
	vBswTest_AdcValue.PhaseU = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_CURR_U);
	vBswTest_AdcValue.PhaseV = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_CURR_V);
	vBswTest_AdcValue.PhaseW = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_CURR_W);
	vBswTest_AdcValue.HVDC = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_HV);
}

void BswTest_ENC_A_ISR(void)
{
	vBswTest_EncValue.EncA_Pulse	= ShrHWIA_BswGpt_GetEncPulseCnt(BSWGPT_ENC_CH_SENS1);
	vBswTest_EncValue.EncA_Dir	= ShrHWIA_BswGpt_GetEncDirection(BSWGPT_ENC_CH_SENS1);
}

void BswTest_ICU_ENC_ISR(void)
{
	vBswTest_EncValue.EncA_Frequency = ShrHWIA_BswIcu_GetFrequency(BSWICU_CH_SENS1_PWM);
	vBswTest_EncValue.EncA_Duty = ShrHWIA_BswIcu_GetDuty(BSWICU_CH_SENS1_PWM);
}

void BswTest_ENC_B_ISR(void) // [TBD] Sent?
{
	;
}
uint8 vBswDac_Ch = 0;
uint8 vBswDac_Usage_Channnel_Qty = 4;
void BswTest_DAC_Idle_Task(void)
{
	vBswDac_Ch ++;

	if(vBswDac_Ch == vBswDac_Usage_Channnel_Qty){
		vBswDac_Ch = 0;
	}
	else{
		//no action
	}

	if(vBswDac_Ch == 0){
		ShrHWIA_BswDac_SetValue(0, vBswAdc_gDACTest, vBswAdc_DAC_TEST_MAX, -vBswAdc_DAC_TEST_MAX);
	}
	else if(vBswDac_Ch == 1){
		ShrHWIA_BswDac_SetValue(1, vBswAdc_gDACTest, vBswAdc_DAC_TEST_MAX, -vBswAdc_DAC_TEST_MAX);
	}
	else if(vBswDac_Ch == 2){
		ShrHWIA_BswDac_SetValue(2, vBswAdc_gDACTest, vBswAdc_DAC_TEST_MAX, -vBswAdc_DAC_TEST_MAX);
	}
	else if(vBswDac_Ch == 3){
		ShrHWIA_BswDac_SetValue(3, vBswAdc_gDACTest, vBswAdc_DAC_TEST_MAX, -vBswAdc_DAC_TEST_MAX);
	}
	else{
		//no action
	}
}

typedef struct structRTS_RUNTIME{
    uint32 execution_time_us;
    uint32 period_us;
    uint32 execution_time;
    uint32 period;
    uint32 start_time;
}typBswTest_TaskRuntime;
#define BSWTEST_STOPWATCH_NUM_MAX           (5U)
typBswTest_TaskRuntime vBswTest_TaskRuntime[BSWTEST_STOPWATCH_NUM_MAX];


void BswTest_StopWatch_Start(uint8 Task_Id)
{
    uint32 current_time = ShrHWIA_BswSys_GetSysTime();

    vBswTest_TaskRuntime[Task_Id].period = current_time - vBswTest_TaskRuntime[Task_Id].start_time;
    vBswTest_TaskRuntime[Task_Id].period_us = (uint32)vBswTest_TaskRuntime[Task_Id].period /100; // TC364 0.01us/tick
    vBswTest_TaskRuntime[Task_Id].start_time = current_time;
}

void BswTest_StopWatch_Stop(uint8 Task_Id)
{
    vBswTest_TaskRuntime[Task_Id].execution_time = ShrHWIA_BswSys_GetSysTime() - vBswTest_TaskRuntime[Task_Id].start_time;
    vBswTest_TaskRuntime[Task_Id].execution_time_us = (uint32)vBswTest_TaskRuntime[Task_Id].execution_time /100; // TC364 0.01us/tick
}

uint32 vBswTest_GetSysTimeTick; // 0.01us/tick
void BswTest_GetSysTime(void)
{
	BswTest_StopWatch_Start(0);
	vBswTest_GetSysTimeTick = ShrHWIA_BswSys_GetSysTime();

	BswTest_StopWatch_Stop(0);
}

uint8 vBswTest_McuReset = 0;
void BswTest_McuReset(void)
{
	if(vBswTest_McuReset == 1){
		ShrHWIA_BswSys_McuReset();
	}
}

//Rx Msg
typBswCanMsg_VPC1 vBswTest_CanMsg_VPC_ARS_01_10ms;
uint8 vBswTest_CanMsg_VPC_ARS_01_10ms_RxNew;
uint8 vBswTest_CanMsg_VPC_ARS_01_10ms_Dlc;

typBswCanMsg_SEA1 vBswTest_CanMsg_SEA_ARS_01_1ms;
uint8 vBswTest_CanMsg_SEA_ARS_01_1ms_RxNew;
uint8 vBswTest_CanMsg_SEA_ARS_01_1ms_Dlc;

typBswCanMsg_SEA2 vBswTest_CanMsg_SEA_ARS_02_1ms;
uint8 vBswTest_CanMsg_SEA_ARS_02_1ms_RxNew;
uint8 vBswTest_CanMsg_SEA_ARS_02_1ms_Dlc;

//Tx Msg
typBswCanMsg_ARS1 vBswTest_CanMsg_ARS_dev_01_10ms;
typBswCanMsg_ARS2 vBswTest_CanMsg_ARS_dev_02_1ms;
typBswCanMsg_ARS3 vBswTest_CanMsg_ARS_dev_03_10ms;
typBswCanMsg_ARS4 vBswTest_CanMsg_ARS_dev_04_10ms;

uint8 vBswTest_BusOffState; // 1 : Bus_off, 0 : not in Bus_off

void BswTest_CanRx_1ms_Task(void)
{
	vBswTest_CanMsg_SEA_ARS_01_1ms_RxNew = ShrHWIA_BswCan_GetMsg(BSWCAN_MSG_RX_INDEX_SEA_ARS_01_1ms, &vBswTest_CanMsg_SEA_ARS_01_1ms_Dlc, &vBswTest_CanMsg_SEA_ARS_01_1ms.byte[0]);
	vBswTest_CanMsg_SEA_ARS_02_1ms_RxNew = ShrHWIA_BswCan_GetMsg(BSWCAN_MSG_RX_INDEX_SEA_ARS_02_1ms, &vBswTest_CanMsg_SEA_ARS_02_1ms_Dlc, &vBswTest_CanMsg_SEA_ARS_02_1ms.byte[0]);
}

void BswTest_CanTx_1ms_Task(void)
{
	vBswTest_BusOffState = ShrHWIA_BswCan_GetState_Busoff(BSWCAN_CAN_CH0);

	if(vBswTest_BusOffState == FALSE){
		ShrHWIA_BswCan_SetMsg(BSWCAN_MSG_TX_INDEX_ARS_dev_02_1ms, BSWCAN_MSG_DLC_ARS_dev_02_1ms, &vBswTest_CanMsg_ARS_dev_02_1ms.byte[0]);
	}
}

void BswTest_CanRx_10ms_Task(void)
{
	vBswTest_CanMsg_VPC_ARS_01_10ms_RxNew = ShrHWIA_BswCan_GetMsg(BSWCAN_MSG_RX_INDEX_VPC_ARS_01_10ms, &vBswTest_CanMsg_VPC_ARS_01_10ms_Dlc, &vBswTest_CanMsg_VPC_ARS_01_10ms.byte[0]);
}

void BswTest_CanTx_10ms_Task(void)
{
	vBswTest_BusOffState = ShrHWIA_BswCan_GetState_Busoff(BSWCAN_CAN_CH0);

	if(vBswTest_BusOffState == FALSE){
		ShrHWIA_BswCan_SetMsg(BSWCAN_MSG_TX_INDEX_ARS_dev_01_10ms, BSWCAN_MSG_DLC_ARS_dev_01_10ms, &vBswTest_CanMsg_ARS_dev_01_10ms.byte[0]);
		ShrHWIA_BswCan_SetMsg(BSWCAN_MSG_TX_INDEX_ARS_dev_03_10ms, BSWCAN_MSG_DLC_ARS_dev_03_10ms, &vBswTest_CanMsg_ARS_dev_03_10ms.byte[0]);
		ShrHWIA_BswCan_SetMsg(BSWCAN_MSG_TX_INDEX_ARS_dev_04_10ms, BSWCAN_MSG_DLC_ARS_dev_04_10ms, &vBswTest_CanMsg_ARS_dev_04_10ms.byte[0]);
	}
}

uint8 vBswTest_Dio_Testcase=0xFF;

uint16 vBswTest_Dio_LedOnTimeMs = 1000; // 1sec on
uint16 vBswTest_Dio_LedOffTimeMs = 2000; // 2sec off

void BswTest_Dio_100ms_Task(void)
{
	ShrHWIA_BswDio_Set_LED_Indicate(vBswTest_Dio_LedOnTimeMs, vBswTest_Dio_LedOffTimeMs);

	switch(vBswTest_Dio_Testcase){
	case 0: // OFF
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP158, BSWDIO_FLAG_OFF);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP29, BSWDIO_FLAG_OFF);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP31, BSWDIO_FLAG_OFF);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP48, BSWDIO_FLAG_OFF);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP50, BSWDIO_FLAG_OFF);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP51, BSWDIO_FLAG_OFF);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP52, BSWDIO_FLAG_OFF);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP53, BSWDIO_FLAG_OFF);
		vBswTest_Dio_Testcase = 0xFF;
		break;
	case 1: // ON
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP158, BSWDIO_FLAG_ON);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP29, BSWDIO_FLAG_ON);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP31, BSWDIO_FLAG_ON);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP48, BSWDIO_FLAG_ON);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP50, BSWDIO_FLAG_ON);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP51, BSWDIO_FLAG_ON);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP52, BSWDIO_FLAG_ON);
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP53, BSWDIO_FLAG_ON);
		vBswTest_Dio_Testcase = 0xFF;
		break;
	case 2: // Toggle
		if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP158) == BSWDIO_FLAG_ON){
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP158, BSWDIO_FLAG_OFF);
		}
		else{
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP158, BSWDIO_FLAG_ON);
		}

		if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP29) == BSWDIO_FLAG_ON){
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP29, BSWDIO_FLAG_OFF);
		}
		else{
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP29, BSWDIO_FLAG_ON);
		}

		if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP31) == BSWDIO_FLAG_ON){
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP31, BSWDIO_FLAG_OFF);
		}
		else{
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP31, BSWDIO_FLAG_ON);
		}

		if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP48) == BSWDIO_FLAG_ON){
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP48, BSWDIO_FLAG_OFF);
		}
		else{
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP48, BSWDIO_FLAG_ON);
		}

		if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP50) == BSWDIO_FLAG_ON){
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP50, BSWDIO_FLAG_OFF);
		}
		else{
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP50, BSWDIO_FLAG_ON);
		}

		if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP51) == BSWDIO_FLAG_ON){
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP51, BSWDIO_FLAG_OFF);
		}
		else{
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP51, BSWDIO_FLAG_ON);
		}

		if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP52) == BSWDIO_FLAG_ON){
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP52, BSWDIO_FLAG_OFF);
		}
		else{
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP52, BSWDIO_FLAG_ON);
		}

		if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP53) == BSWDIO_FLAG_ON){
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP53, BSWDIO_FLAG_OFF);
		}
		else{
			ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP53, BSWDIO_FLAG_ON);
		}
		vBswTest_Dio_Testcase = 0xFF;
		break;
	default:
		break;
	}
}

uint8 vBswTest_NvM_ReadData_0[64];
uint8 vBswTest_NvM_WriteData_0[64];
uint8 vBswTest_NvM_ReadData_1[64];
uint8 vBswTest_NvM_WriteData_1[64];
uint8 vBswTest_NvM_ReadData_2[64];
uint8 vBswTest_NvM_WriteData_2[64];
uint8 vBswTest_NvM_ReadData_3[64];
uint8 vBswTest_NvM_WriteData_3[64];

uint8 vBswTest_NvM_Testcase = 0xFF;


void BswTest_Nvm_100ms_Task(void)
{
	uint8 i;

    switch(vBswTest_NvM_Testcase) {
        case 0:
        	ShrHWIA_BswNvm_ReadBlock(BSWNVM_BLOCK_INDEX_0, vBswTest_NvM_ReadData_0);
        	vBswTest_NvM_Testcase = 0xFF;
            break;

        case 1:
        	ShrHWIA_BswNvm_ReadBlock(BSWNVM_BLOCK_INDEX_1, vBswTest_NvM_ReadData_1);
        	vBswTest_NvM_Testcase = 0xFF;
            break;

        case 2:
        	ShrHWIA_BswNvm_ReadBlock(BSWNVM_BLOCK_INDEX_2, vBswTest_NvM_ReadData_2);
        	vBswTest_NvM_Testcase = 0xFF;
            break;

        case 3:
        	ShrHWIA_BswNvm_ReadBlock(BSWNVM_BLOCK_INDEX_3, vBswTest_NvM_ReadData_3);
        	vBswTest_NvM_Testcase = 0xFF;
            break;

        case 4:
        	BswTest_StopWatch_Start(1);
        	ShrHWIA_BswNvm_WriteBlock(BSWNVM_BLOCK_INDEX_0, vBswTest_NvM_WriteData_0);
        	BswTest_StopWatch_Stop(1);
        	vBswTest_NvM_Testcase = 0xFF;
            break;

        case 5:
        	ShrHWIA_BswNvm_WriteBlock(BSWNVM_BLOCK_INDEX_1, vBswTest_NvM_WriteData_1);
        	vBswTest_NvM_Testcase = 0xFF;
            break;

        case 6:
        	ShrHWIA_BswNvm_WriteBlock(BSWNVM_BLOCK_INDEX_2, vBswTest_NvM_WriteData_2);
        	vBswTest_NvM_Testcase = 0xFF;
            break;

        case 7:
        	ShrHWIA_BswNvm_WriteBlock(BSWNVM_BLOCK_INDEX_3, vBswTest_NvM_WriteData_3);
        	vBswTest_NvM_Testcase = 0xFF;
            break;

        case 8:
            for(i=0;i<64;i++){
            	vBswTest_NvM_WriteData_0[i]=0x0;
            }
            vBswTest_NvM_Testcase = 0xFF;
            break;
        case 9:
            for(i=0;i<64;i++){
            	vBswTest_NvM_WriteData_0[i]=0xFF;
            }
            vBswTest_NvM_Testcase = 0xFF;
            break;

        default:
            // Default case for invalid or unhandled test cases
            break;
    }
}

void BswTest_Wdt_100ms_Task(void)
{
	if(vBswTest_Wdt_Testcase == 1){
		ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP158, BSWDIO_FLAG_ON);
		while(1){
			vBswTest_WdtCount++;
		}
	}
	else{
		//do nothing
	}
}

typBswSys_Mcu_Reset vBswTest_ResetReason;
uint32 vBswTest_ResetStatus;

void BswTest_Sys_100ms_Task(void)
{
	vBswTest_ResetReason = ShrHWIA_BswSys_GetResetReason();
	vBswTest_ResetStatus = ShrHWIA_BswSys_GetResetStatus();
}

#define BSWTEST_SENT_MAX_LOG_COUNT 10

typBswSent_StateType vBswTest_SentStateArray[BSWTEST_SENT_MAX_LOG_COUNT];
uint16 vBswTest_SentDataArray[BSWTEST_SENT_MAX_LOG_COUNT];
static uint32 vBswTest_SentCounter = 0;

typBswSent_StateType vBswTest_State;
uint16 vBswTest_SentData;

void BswTest_Sent_1ms_Task(void)
{
    typBswSent_StateType tempstate;
    uint16 tempdata;

    tempstate = ShrHWIA_BswSent_GetGearPosition(&tempdata);

    if (vBswTest_SentCounter < BSWTEST_SENT_MAX_LOG_COUNT)
    {
    	vBswTest_SentStateArray[vBswTest_SentCounter] = tempstate;
        vBswTest_SentDataArray[vBswTest_SentCounter] = tempdata;
    }
    else
    {
        vBswTest_State = tempstate;
        vBswTest_SentData = tempdata;
    }

    vBswTest_SentCounter++;
//    vBswTest_State = ShrHWIA_BswSent_GetGearPosition(&vBswTest_SentData);
}
