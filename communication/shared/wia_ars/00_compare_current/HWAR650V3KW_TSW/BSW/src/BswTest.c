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

#include "VectorTest.h"		//TEST

extern measModule_t		meas;				// Measure Module

uint16 vBswTest_Pwm_DutyCycle_U = 3125;
uint16 vBswTest_Pwm_DutyCycle_V = 3125;
uint16 vBswTest_Pwm_DutyCycle_W = 3125;

Pwm_Enable_mode vBswTest_Pwm_Enable_Mode = PWM_3PH_DISABLE;
uint8 vBswTest_Pwm_Module_Ch 		= 0;
uint8 vBswTest_Pwm_Module_Ch_State 	= 0;
uint16 vBswTest_Pwm_Module_Ch_Value = 3125;
uint32 vBswTest_Pwm_Period_SetValue = 6250;	//PeriodVal: Period value in ticks (1 tick = 0.01us)
uint16 vBswTest_Pwm_Deadtime_SetValue = 200;	//DeadTimeVal: Dead time value in ticks (1 tick = 0.01us)
volatile uint32 vBswTest_WdtCount;
uint8 vBswTest_Wdt_Testcase;

uint8 vBswTest_CalibStatus;			//Current calibration status (0=In Progress, 1=Pass, 2=Fail)
uint8 vBswTest_MotTempErrStatus;  	// Motor Temperature Error Status: (0=Valid, 1=Invalid)

//Debug
DebugADC_t vBswTest_AdcValue;
DebugENC_t vBswTest_EncValue;
DebugIcuStatus_t vBswTest_IcuStatus;

#define SRVVER_BOOT_VER_ADDR	(0x8003FFE0u)
#define SRVVER_BSW_VER_ADDR		(0x8013FFE0u)
#define SRVVER_ROM_VER_ADDR		(0x801BFFC0u)
#define SRVVER_ISW_VER_ADDR		(0x801BFFD0u)
#define SRVVER_ASW_VER_ADDR		(0x801BFFE0u)

volatile const char vSrvVer_RomVersion[16] __at(SRVVER_ROM_VER_ADDR) = "ARS_ROM_789";
volatile const char vSrvVer_IswVersion[16] __at(SRVVER_ISW_VER_ADDR) = "ARS_ISW_456";
volatile const char vSrvVer_AswVersion[16] __at(SRVVER_ASW_VER_ADDR) = "ARS_ASW_123";

void BswTest_Pwm_Idle_Task(void)
{
	vBswTest_Pwm_Enable_Mode = ShrHWIA_BswPwm_Enable(vBswTest_Pwm_Enable_Mode);

	if(vBswTest_Pwm_Enable_Mode == PWM_3PH_DISABLE)
	{
		ShrHWIA_BswPwm_Output_Disable();

		ShrHWIA_BswPwm_SetPeriod(vBswTest_Pwm_Period_SetValue);			// Test_PWM_Frequency_SET_Example
		ShrHWIA_BswPwm_SetDeadTime(vBswTest_Pwm_Deadtime_SetValue);		// Test_PWM_DeadTime_SET_Example
	}
	else{}
}

void BswTest_PWM_ISR(void)
{
	if((vBswTest_Pwm_Enable_Mode == PWM_3PH_DISABLE) || (vBswTest_Pwm_Enable_Mode == PWM_3PH_SYNC_ENABLE))
	{
		ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_HS_U, vBswTest_Pwm_DutyCycle_U);
		ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_LS_U, vBswTest_Pwm_DutyCycle_U);
		ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_HS_V, vBswTest_Pwm_DutyCycle_V);
		ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_LS_V, vBswTest_Pwm_DutyCycle_V);
		ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_HS_W, vBswTest_Pwm_DutyCycle_W);
		ShrHWIA_BswPwm_SetDutyCycle(BSWPWM_CH_DRV_LS_W, vBswTest_Pwm_DutyCycle_W);
	}
	else if(vBswTest_Pwm_Enable_Mode == PWM_CH_ENABLE)
	{
		ShrHWIA_BswPwm_Channel_SetDutyCycle(vBswTest_Pwm_Module_Ch, vBswTest_Pwm_Module_Ch_State, vBswTest_Pwm_Module_Ch_Value);
	}
	else{}
}

void BswTest_Adc_10ms_Task(void)
{
	vBswTest_CalibStatus = ShrHWIA_BswAdc_GetCurrentCalibStatus();
	vBswTest_MotTempErrStatus = ShrHWIA_BswAdc_GetMotorTempErrStatus();

	vBswTest_AdcValue.VDD15V	= ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_VDD_15V);
	vBswTest_AdcValue.VDD5V = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_VDD_5V0);
	vBswTest_AdcValue.LVDC = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_LV);
	vBswTest_AdcValue.IG = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_IG);
	vBswTest_AdcValue.Vmcu = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_VUC_5V0);
	vBswTest_AdcValue.Vcom = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_VCOM_5V0);
	vBswTest_AdcValue.Vtr1 = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_VT1_5V0);
	vBswTest_AdcValue.Vtr2 = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_VT2_5V0);
	vBswTest_AdcValue.Vref = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_VREF_5V0);
	vBswTest_AdcValue.Tpcb = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_PCB_TEMP);
	vBswTest_AdcValue.Tigbt = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_IPM_TEMP);
	vBswTest_AdcValue.Tmot = ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_MOT_TEMP);
}

void BswTest_Adc_ISR(void)
{
	vBswTest_AdcValue.PhaseU_Raw	= ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_CURR_U_RAW);
	vBswTest_AdcValue.PhaseW_Raw	= ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_CURR_W_RAW);
	vBswTest_AdcValue.IDC_Raw		= ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_CURR_DC_RAW);
	vBswTest_AdcValue.HVDC			= ShrHWIA_BswAdc_GetPhyValue(BSWADC_CH_SENS_HV);
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

void BswTest_ICU_SENS2(void)
{
	;
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



//Rx Msg
typBswCanMsg_MVPC1 vBswTest_CanMsg_MVPC_ARS_01_1ms;
uint8 vBswTest_CanMsg_MVPC_ARS_01_1ms_RxNew;
uint8 vBswTest_CanMsg_MVPC_ARS_01_1ms_Dlc;
uint8 vBswTest_CanMsg_MVPC_ARS_01_1ms_Timeout;

typBswCanMsg_RT1_10 vBswTest_CanMsg_RT_01_10ms;
uint8 vBswTest_CanMsg_RT_01_10ms_RxNew;
uint8 vBswTest_CanMsg_RT_01_10ms_Dlc;
uint8 vBswTest_CanMsg_RT_01_10ms_Timeout;

typBswCanMsg_RT1_20 vBswTest_CanMsg_RT_01_20ms;
uint8 vBswTest_CanMsg_RT_01_20ms_RxNew;
uint8 vBswTest_CanMsg_RT_01_20ms_Dlc;
uint8 vBswTest_CanMsg_RT_01_20ms_Timeout;

typBswCanMsg_RT1_200 vBswTest_CanMsg_RT_01_200ms;
uint8 vBswTest_CanMsg_RT_01_200ms_RxNew;
uint8 vBswTest_CanMsg_RT_01_200ms_Dlc;
uint8 vBswTest_CanMsg_RT_01_200ms_Timeout;

//Tx Msg
typBswCanMsg_ARS1 vBswTest_CanMsg_ARS_dev_01_1ms;
typBswCanMsg_MEAS vBswTest_CanMsg_MEAS_01_1ms;
typBswCanMsg_MEAS vBswTest_CanMsg_MEAS_01_5ms;
typBswCanMsg_MEAS vBswTest_CanMsg_MEAS_02_5ms;
typBswCanMsg_MEAS vBswTest_CanMsg_MEAS_01_10ms;
typBswCanMsg_MEAS vBswTest_CanMsg_MEAS_02_10ms;

uint8 vBswTest_Can0BusOffState; // 1 : Bus_off, 0 : not in Bus_off
uint8 vBswTest_Can1BusOffState; // 1 : Bus_off, 0 : not in Bus_off

extern uint8 Ch0CanDisable = 0;

/* CH0 CAN Tx Enable/Disable Test - Set Ch0CanDisable via CAL/XCP */
void BswTest_CanTx_Ch0Ctrl(void)
{
    /* 0: Tx ON, 1: Tx OFF (Set by customer CAL) */
	ShrHWIA_BswCan_SetCh0CanDisable(Ch0CanDisable);
}

void BswTest_CanRx_1ms_Task(void)
{
	vBswTest_CanMsg_MVPC_ARS_01_1ms_Timeout = ShrHWIA_BswCan_GetState_Timeout(BSWCAN_MSG_RX_INDEX_MVPC_ARS_01_1ms);
	vBswTest_CanMsg_MVPC_ARS_01_1ms_RxNew = ShrHWIA_BswCan_GetMsg(BSWCAN_MSG_RX_INDEX_MVPC_ARS_01_1ms, &vBswTest_CanMsg_MVPC_ARS_01_1ms_Dlc, &vBswTest_CanMsg_MVPC_ARS_01_1ms.byte[0]);
}

void BswTest_CanTx_1ms_Task(void)
{
	vBswTest_Can0BusOffState = ShrHWIA_BswCan_GetState_Busoff(BSWCAN_CAN_CH0);
	vBswTest_Can1BusOffState = ShrHWIA_BswCan_GetState_Busoff(BSWCAN_CAN_CH1);

	if(vBswTest_Can1BusOffState == FALSE){
		ShrHWIA_BswCan_SetMsg(BSWCAN_MSG_TX_INDEX_ARS_dev_01_1ms, BSWCAN_MSG_DLC_ARS_dev_01_1ms, &vBswTest_CanMsg_ARS_dev_01_1ms.byte[0]);
	}

	if(vBswTest_Can0BusOffState == FALSE){
		ShrHWIA_BswCan_SetMsg(BSWCAN_MSG_TX_INDEX_MEAS_01_1ms, BSWCAN_MSG_DLC_MEAS, &vBswTest_CanMsg_MEAS_01_1ms.byte[0]);
	}
}

void BswTest_CanTx_5ms_Task(void)
{
	if(vBswTest_Can0BusOffState == FALSE){
		ShrHWIA_BswCan_SetMsg(BSWCAN_MSG_TX_INDEX_MEAS_01_5ms, BSWCAN_MSG_DLC_MEAS, &vBswTest_CanMsg_MEAS_01_5ms.byte[0]);
		ShrHWIA_BswCan_SetMsg(BSWCAN_MSG_TX_INDEX_MEAS_02_5ms, BSWCAN_MSG_DLC_MEAS, &vBswTest_CanMsg_MEAS_02_5ms.byte[0]);
	}
}

void BswTest_CanTx_10ms_Task(void)
{
	if(vBswTest_Can0BusOffState == FALSE){
		ShrHWIA_BswCan_SetMsg(BSWCAN_MSG_TX_INDEX_MEAS_01_10ms, BSWCAN_MSG_DLC_MEAS, &vBswTest_CanMsg_MEAS_01_10ms.byte[0]);
		ShrHWIA_BswCan_SetMsg(BSWCAN_MSG_TX_INDEX_MEAS_02_10ms, BSWCAN_MSG_DLC_MEAS, &vBswTest_CanMsg_MEAS_02_10ms.byte[0]);
	}
}

void BswTest_CanRx_10ms_Task(void)
{
	vBswTest_CanMsg_RT_01_10ms_Timeout = ShrHWIA_BswCan_GetState_Timeout(BSWCAN_MSG_RX_INDEX_ROUTING_01_10ms);
	vBswTest_CanMsg_RT_01_10ms_RxNew = ShrHWIA_BswCan_GetMsg(BSWCAN_MSG_RX_INDEX_ROUTING_01_10ms, &vBswTest_CanMsg_RT_01_10ms_Dlc, &vBswTest_CanMsg_RT_01_10ms.byte[0]);
}

void BswTest_CanRx_20ms_Task(void)
{
	vBswTest_CanMsg_RT_01_20ms_Timeout = ShrHWIA_BswCan_GetState_Timeout(BSWCAN_MSG_RX_INDEX_ROUTING_01_20ms);
	vBswTest_CanMsg_RT_01_20ms_RxNew = ShrHWIA_BswCan_GetMsg(BSWCAN_MSG_RX_INDEX_ROUTING_01_20ms, &vBswTest_CanMsg_RT_01_20ms_Dlc, &vBswTest_CanMsg_RT_01_20ms.byte[0]);
}

void BswTest_CanRx_200ms_Task(void)
{
	vBswTest_CanMsg_RT_01_200ms_Timeout = ShrHWIA_BswCan_GetState_Timeout(BSWCAN_MSG_RX_INDEX_ROUTING_01_200ms);
	vBswTest_CanMsg_RT_01_200ms_RxNew = ShrHWIA_BswCan_GetMsg(BSWCAN_MSG_RX_INDEX_ROUTING_01_200ms, &vBswTest_CanMsg_RT_01_200ms_Dlc, &vBswTest_CanMsg_RT_01_200ms.byte[0]);
}

uint8 vBswTest_Dio_Testcase=0xFF;

//uint16 vBswTest_Dio_LedOnTimeMs = 1000; // 1sec on
//uint16 vBswTest_Dio_LedOffTimeMs = 2000; // 2sec off
uint16 vBswTest_Dio_LedOnTimeMs = 0; // 1sec on
uint16 vBswTest_Dio_LedOffTimeMs = 0; // 2sec off

void BswTest_Dio_100ms_Task(void)
{
	ShrHWIA_BswDio_Set_LED_Indicate(vBswTest_Dio_LedOnTimeMs, vBswTest_Dio_LedOffTimeMs);

	switch(vBswTest_Dio_Testcase){
	case 0: // OFF
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP158, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP29, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP31, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP48, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP52, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP2, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP4, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP20, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP50, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP51, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP62, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP65, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP76, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP77, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP78, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP98, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP100, BSWDIO_FLAG_OFF);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP53, BSWDIO_FLAG_OFF);
	    vBswTest_Dio_Testcase = 0xFF;
	    break;
	case 1: // ON
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP158, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP29, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP31, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP48, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP52, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP2, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP4, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP20, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP50, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP51, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP62, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP65, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP76, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP77, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP78, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP98, BSWDIO_FLAG_ON);
	    ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP100, BSWDIO_FLAG_ON);
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

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP52) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP52, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP52, BSWDIO_FLAG_ON);
	    }

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP2) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP2, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP2, BSWDIO_FLAG_ON);
	    }

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP4) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP4, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP4, BSWDIO_FLAG_ON);
	    }

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP20) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP20, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP20, BSWDIO_FLAG_ON);
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

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP62) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP62, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP62, BSWDIO_FLAG_ON);
	    }

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP65) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP65, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP65, BSWDIO_FLAG_ON);
	    }

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP76) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP76, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP76, BSWDIO_FLAG_ON);
	    }

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP77) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP77, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP77, BSWDIO_FLAG_ON);
	    }

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP78) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP78, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP78, BSWDIO_FLAG_ON);
	    }

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP98) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP98, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP98, BSWDIO_FLAG_ON);
	    }

	    if(ShrHWIA_BswDio_GetPin(BSWDIO_CH_TP100) == BSWDIO_FLAG_ON){
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP100, BSWDIO_FLAG_OFF);
	    }
	    else{
	        ShrHWIA_BswDio_SetPin(BSWDIO_CH_TP100, BSWDIO_FLAG_ON);
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

/*
 * Read/Write NVM block data by index.
 * Return: BSWNVM_STATUS_OK (0) if request is accepted,
 *         BSWNVM_STATUS_NOT_OK (1) if index is invalid or request failed to start.
 * Note: data array size should be 64 bytes.
 */
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

#define BSWTEST_IG_ON_THRESHOLD      (0.8f)
#define BSWTEST_IS_IG_ON()           (vBswTest_AdcValue.IG >= BSWTEST_IG_ON_THRESHOLD ? 1 : 0)	// PMIC IG falling threshold (logic OFF) = 0.8V

typBswSys_Mcu_Reset vBswTest_ResetReason;
uint32 vBswTest_ResetStatus;
uint8 vBswTest_ReproStatusFlag;
uint8 vBswTest_SetTargetAxle = 0;//OnlyTSW_SetTargetAxle
uint8 vBswTest_McuReset = 0;
uint8 vBswTest_ShutdownRequest = 0;
float32 vBswTest_GetCpuLoad = 0;

void BswTest_Sys_100ms_Task(void)
{
	vBswTest_ResetReason = ShrHWIA_BswSys_GetResetReason();
	vBswTest_ResetStatus = ShrHWIA_BswSys_GetResetStatus();
	vBswTest_ReproStatusFlag = ShrHWIA_BswSys_GetReproStatusFlag();
	vBswTest_GetCpuLoad = ShrHWIA_BswSys_GetCpuLoad();

	//OnlyTSW_SetTargetAxle
	if(vBswTest_SetTargetAxle == BSWSYS_TARGET_AXLE_UNDEFINED){
		// do nothing
	}
	else if(vBswTest_SetTargetAxle == BSWSYS_TARGET_AXLE_FRONT){
		ShrHWIA_BswSys_SetTargetAxle(BSWSYS_TARGET_AXLE_FRONT);
	}
	else if(vBswTest_SetTargetAxle == BSWSYS_TARGET_AXLE_REAR){
		ShrHWIA_BswSys_SetTargetAxle(BSWSYS_TARGET_AXLE_REAR);
	}
	else{
		// do nothing
	}

	if(vBswTest_McuReset == 1){
		ShrHWIA_BswSys_McuReset();
	}


	// Behavior depends on IG state:
	// - IG ON  : No action (safe to call anytime)
	// - IG OFF : Shutdown immediately (skips normal 10s delay)
	if (vBswTest_ShutdownRequest == 1){
		if (BSWTEST_IS_IG_ON() == 0){
			ShrHWIA_BswSys_ShutdownRequest();
		}
		else{
			//no action
		}

		vBswTest_ShutdownRequest = 0;
	}
}

#define BSWTEST_SENT_MAX_LOG_COUNT 10

typBswSent_StateType vBswTest_SentStateArray[BSWTEST_SENT_MAX_LOG_COUNT];
uint16 vBswTest_SentDataArray1[BSWTEST_SENT_MAX_LOG_COUNT];
uint8 vBswTest_SentDataArray2[BSWTEST_SENT_MAX_LOG_COUNT];
static uint32 vBswTest_SentCounter = 0;

typBswSent_StateType vBswTest_State;
uint16 vBswTest_SentPositionData;
uint8 vBswTest_SentTemperatureData;

void BswTest_Sent_1ms_Task(void)
{
    typBswSent_StateType tempstate;
    uint16 tempdata1;
    uint8 tempdata2;

    tempstate = ShrHWIA_BswSent_GetGearPosition(&tempdata1, &tempdata2);

    if (vBswTest_SentCounter < BSWTEST_SENT_MAX_LOG_COUNT)
    {
    	vBswTest_SentStateArray[vBswTest_SentCounter] = tempstate;
        vBswTest_SentDataArray1[vBswTest_SentCounter] = tempdata1;
        vBswTest_SentDataArray2[vBswTest_SentCounter] = tempdata2;
    }
    else
    {
        vBswTest_State = tempstate;
        vBswTest_SentPositionData = tempdata1;
        vBswTest_SentTemperatureData = tempdata2;
    }

    vBswTest_SentCounter++;
}


void BswTest_GetIcuPinStatus_1ms_Task(void)
{
	vBswTest_IcuStatus.INTERLOCK_Sens		= ShrHWIA_BswDio_GetPin(BSWDIO_CH_SENS_INTERLOCK);
	vBswTest_IcuStatus.DRV_FLT_Sens			= ShrHWIA_BswDio_GetPin(BSWDIO_CH_DRV_FAULT);
	vBswTest_IcuStatus.CURR_FLT_U_Sens		= ShrHWIA_BswDio_GetPin(BSWDIO_CH_CURR_FLT_SENS_U);
	vBswTest_IcuStatus.CURR_FLT_W_Sens		= ShrHWIA_BswDio_GetPin(BSWDIO_CH_CURR_FLT_SENS_W);
	vBswTest_IcuStatus.CURR_FLT_HVB_Sens	= ShrHWIA_BswDio_GetPin(BSWDIO_CH_CURR_FLT_SENS_HVB);
	vBswTest_IcuStatus.HV_OV_Sens			= ShrHWIA_BswDio_GetPin(BSWDIO_CH_HV_OV_SENS);
}

#define SLOWCHANNEL_TOTAL_IDS (22u)

typedef struct {
    uint8            msgId;   /* original message ID            */
    Std_ReturnType   ret;     /* API return value               */
    uint16           data;    /* received data                  */
    uint32           ts;      /* received timestamp)     */
}typBswSlowCh_Entry;

static typBswSlowCh_Entry vBswTest_SlowCh[SLOWCHANNEL_TOTAL_IDS] = {
    { .msgId = 0x01 }, { .msgId = 0x03 }, { .msgId = 0x05 }, { .msgId = 0x06 },
    { .msgId = 0x07 }, { .msgId = 0x08 }, { .msgId = 0x09 }, { .msgId = 0x0A },
    { .msgId = 0x23 }, { .msgId = 0x24 },
    { .msgId = 0x29 }, { .msgId = 0x2A }, { .msgId = 0x2B }, { .msgId = 0x2C },
    { .msgId = 0x90 }, { .msgId = 0x91 }, { .msgId = 0x92 }, { .msgId = 0x93 },
    { .msgId = 0x94 }, { .msgId = 0x95 }, { .msgId = 0x96 }, { .msgId = 0x97 }
};

void BswTest_SlowCh_1ms_Task(void)
{
    uint16 tmpdata;
    uint32 tmpts;

    /* ID 0x01 */
    vBswTest_SlowCh[0].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[0].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[0].ret) {
        vBswTest_SlowCh[0].data = tmpdata;  /* store data */
        vBswTest_SlowCh[0].ts   = tmpts;   /* store time stamp */
    }
    else {
        /* no action */
    }

    /* ID 0x03 */
    vBswTest_SlowCh[1].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[1].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[1].ret) {
        vBswTest_SlowCh[1].data = tmpdata;
        vBswTest_SlowCh[1].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x05 */
    vBswTest_SlowCh[2].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[2].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[2].ret) {
        vBswTest_SlowCh[2].data = tmpdata;
        vBswTest_SlowCh[2].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x06 */
    vBswTest_SlowCh[3].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[3].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[3].ret) {
        vBswTest_SlowCh[3].data = tmpdata;
        vBswTest_SlowCh[3].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x07 */
    vBswTest_SlowCh[4].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[4].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[4].ret) {
        vBswTest_SlowCh[4].data = tmpdata;
        vBswTest_SlowCh[4].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x08 */
    vBswTest_SlowCh[5].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[5].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[5].ret) {
        vBswTest_SlowCh[5].data = tmpdata;
        vBswTest_SlowCh[5].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x09 */
    vBswTest_SlowCh[6].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[6].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[6].ret) {
        vBswTest_SlowCh[6].data = tmpdata;
        vBswTest_SlowCh[6].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x0A */
    vBswTest_SlowCh[7].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[7].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[7].ret) {
        vBswTest_SlowCh[7].data = tmpdata;
        vBswTest_SlowCh[7].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x23 */
    vBswTest_SlowCh[8].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[8].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[8].ret) {
        vBswTest_SlowCh[8].data = tmpdata;
        vBswTest_SlowCh[8].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x24 */
    vBswTest_SlowCh[9].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[9].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[9].ret) {
        vBswTest_SlowCh[9].data = tmpdata;
        vBswTest_SlowCh[9].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x29 */
    vBswTest_SlowCh[10].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[10].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[10].ret) {
        vBswTest_SlowCh[10].data = tmpdata;
        vBswTest_SlowCh[10].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x2A */
    vBswTest_SlowCh[11].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[11].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[11].ret) {
        vBswTest_SlowCh[11].data = tmpdata;
        vBswTest_SlowCh[11].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x2B */
    vBswTest_SlowCh[12].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[12].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[12].ret) {
        vBswTest_SlowCh[12].data = tmpdata;
        vBswTest_SlowCh[12].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x2C */
    vBswTest_SlowCh[13].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[13].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[13].ret) {
        vBswTest_SlowCh[13].data = tmpdata;
        vBswTest_SlowCh[13].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x90 */
    vBswTest_SlowCh[14].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[14].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[14].ret) {
        vBswTest_SlowCh[14].data = tmpdata;
        vBswTest_SlowCh[14].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x91 */
    vBswTest_SlowCh[15].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[15].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[15].ret) {
        vBswTest_SlowCh[15].data = tmpdata;
        vBswTest_SlowCh[15].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x92 */
    vBswTest_SlowCh[16].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[16].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[16].ret) {
        vBswTest_SlowCh[16].data = tmpdata;
        vBswTest_SlowCh[16].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x93 */
    vBswTest_SlowCh[17].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[17].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[17].ret) {
        vBswTest_SlowCh[17].data = tmpdata;
        vBswTest_SlowCh[17].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x94 */
    vBswTest_SlowCh[18].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[18].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[18].ret) {
        vBswTest_SlowCh[18].data = tmpdata;
        vBswTest_SlowCh[18].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x95 */
    vBswTest_SlowCh[19].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[19].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[19].ret) {
        vBswTest_SlowCh[19].data = tmpdata;
        vBswTest_SlowCh[19].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x96 */
    vBswTest_SlowCh[20].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[20].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[20].ret) {
        vBswTest_SlowCh[20].data = tmpdata;
        vBswTest_SlowCh[20].ts   = tmpts;
    }
    else {
        /* no action */
    }

    /* ID 0x97 */
    vBswTest_SlowCh[21].ret = ShrHWIA_BswSent_GetSlowChannel(vBswTest_SlowCh[21].msgId, &tmpdata, &tmpts);
    if (E_OK == vBswTest_SlowCh[21].ret) {
        vBswTest_SlowCh[21].data = tmpdata;
        vBswTest_SlowCh[21].ts   = tmpts;
    }
    else {
        /* no action */
    }
}
