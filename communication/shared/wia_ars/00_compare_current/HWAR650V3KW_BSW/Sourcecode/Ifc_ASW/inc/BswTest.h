/*
 * BswTest.h
 *
 *  Created on: 2024. 12. 19.
 *      Author: jaegalrang
 */

#ifndef IFC_ASW_BSWTEST_H_
#define IFC_ASW_BSWTEST_H_

#include "Platform_Types.h"

#define DAC_USAGE_CH_NUM		(4U)

typedef struct{
	float 				PhaseU_Raw;
	float 				PhaseW_Raw;
	float 				IDC_Raw;
	float				HVDC;
	float 				VDD15V;
	float 				VDD5V;
	float 				LVDC;
	float 				IG;
	float 				Vmcu;
	float 				Vcom;
	float 				Vtr1;
	float 				Vtr2;
	float 				Vref;
	float 				Tpcb;
	float 				Tigbt;
	float 				Tmot;
}DebugADC_t;

typedef struct{
	uint32				EncA_Pulse;
	uint32				EncB_Pulse;
	boolean				EncA_Dir;
	boolean				EncB_Dir;
	uint32				EncA_Frequency;
	uint32				EncA_Duty;
}DebugENC_t;

typedef struct{
	uint8				INTERLOCK_Sens;
	uint8				DRV_FLT_Sens;
	uint8				CURR_FLT_U_Sens;
	uint8				CURR_FLT_W_Sens;
	uint8				CURR_FLT_HVB_Sens;
	uint8				HV_OV_Sens;
}DebugIcuStatus_t;

typedef enum
{
	PWM_3PH_DISABLE,
	PWM_3PH_SYNC_ENABLE,
	PWM_CH_ENABLE
}Pwm_Enable_mode;

extern uint16 vBswTest_Pwm_DutyCycle_U;
extern uint16 vBswTest_Pwm_DutyCycle_V;
extern uint16 vBswTest_Pwm_DutyCycle_W;

extern Pwm_Enable_mode vBswTest_Pwm_Enable_Mode;
extern DebugENC_t vBswTest_EncValue;

extern DebugADC_t vBswTest_AdcValue;
extern uint32 vBswTest_Pwm_Period_SetValue;
extern uint16 vBswTest_Pwm_Deadtime_SetValue;

extern void BswTest_Adc_10ms_Task(void);
extern void BswTest_Adc_ISR(void);
extern void BswTest_ENC_A_ISR(void);
extern void BswTest_ICU_ENC_ISR(void);
extern void BswTest_PWM_ISR(void);
extern void BswTest_GetSysTime(void);
extern void BswTest_McuReset(void);
extern void BswTest_DAC_Idle_Task(void);
extern void BswTest_CanTx_Ch0Ctrl(void);
extern void BswTest_CanRx_1ms_Task(void);
extern void BswTest_CanTx_1ms_Task(void);
extern void BswTest_CanTx_5ms_Task(void);
extern void BswTest_CanRx_10ms_Task(void);
extern void BswTest_CanRx_20ms_Task(void);
extern void BswTest_CanRx_200ms_Task(void);
extern void BswTest_CanTx_10ms_Task(void);
extern void BswTest_Pwm_Idle_Task(void);
extern void BswTest_Dio_100ms_Task(void);
extern void BswTest_Nvm_100ms_Task(void);
extern void BswTest_StopWatch_Start(uint8 Task_Id);
extern void BswTest_StopWatch_Stop(uint8 Task_Id);
extern void BswTest_Wdt_100ms_Task(void);
extern void BswTest_Sys_100ms_Task(void);
extern void BswTest_Sent_1ms_Task(void);
extern void BswTest_SlowCh_1ms_Task(void);
extern void BswTest_GetIcuPinStatus_1ms_Task(void);

#endif /* IFC_ASW_BSWTEST_H_ */
