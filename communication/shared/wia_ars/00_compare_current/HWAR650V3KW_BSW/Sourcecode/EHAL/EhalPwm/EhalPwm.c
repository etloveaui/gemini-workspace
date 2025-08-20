/*
 * PwmHal.c

 *
 *  Created on: 2022. 2. 16.
 *      Author: dell
 */
//#include "Icu_17_GtmCcu6.h"
#include "BswPwm_Cbk.h"
#include "EhalPwm.h"
#include "EHAL/EhalDio/EhalDio.h"
//#include "EhalSys.h"

//Icu_17_GtmCcu6_DutyCycleType vEhalPwm_IcuDutyCycleType[7];
//typEhalPwm_IcuMonitor vEhalPwm_IcuMonitor[7];
typEhalPwm_TestConfig vEhalPwm_TestConfig;

uint32 vEhalPwm_TimerTestTick_001us;
uint32 vEhalPwm_TimerTestTick_001us_Prev;
uint32 vEhalPwm_TimerTestTick_001us_Delta;

uint16 vEhalPwm_FrequencyValue		= PWM_SWITCHING_FREQUENCY_16K;
uint16 vEhalPwm_MaxDutyTickValue	= PWM_MAX_DUTY_VALUE_16K;
uint16 vEhalPwm_HalfDutyTickValue	= PWM_HALF_DUTY_VALUE_16K;
float vEhalPwm_SamplingTime			= PWM_SAMPLING_TIME_VALUE;

uint16 vEhalPwm_DeadTimeValue = PWM_DEAD_TIME_VALUE; //200~1000

/* Debug */
typedef struct{
	uint32 LS_U;
	uint32 HS_U;
	uint32 LS_V;
	uint32 HS_V;
	uint32 LS_W;
	uint32 HS_W;
}typEhalPwm_TestDuty;


/////////////////////////////////////////// PWM ///////////////////////////////////////////////////////////////////
void EhalPwm_Channel_Output_Enable(void)
{
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT1 = EHALPWM_CHANNEL_OUTPUT_ENABLE;
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT2 = EHALPWM_CHANNEL_OUTPUT_ENABLE;
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT3 = EHALPWM_CHANNEL_OUTPUT_ENABLE;
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT4 = EHALPWM_CHANNEL_OUTPUT_ENABLE;
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT5 = EHALPWM_CHANNEL_OUTPUT_ENABLE;
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT6 = EHALPWM_CHANNEL_OUTPUT_ENABLE;
}

void EhalPwm_Channel_Output_Disable(void)
{
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT1 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT2 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT3 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT4 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT5 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
	GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT6 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
}

void EhalPwm_SR_Update_Enable(void)
{
	/* EhalPwm_Init(void)
	 * TOM channel x enable update of register CM0, CM1 and CLK_SRC from SR0, SR1 and CLK_SRC_SR
	 * Write / Read
	 * 00B Don't care / update disabled
	 * 01B Disable update / --
	 * 10B Enable update / --
	 * 11B Don�셳 care / update enabled */
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL1 = EHALPWM_WRITE_UPDATE_ENABLE;		// EHAL_PWM_TOM_1_1_PORT_0_1_DRV_HS_W
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL2 = EHALPWM_WRITE_UPDATE_ENABLE;		// EHAL_PWM_TOM_1_2_PORT_0_3_DRV_HS_U
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL3 = EHALPWM_WRITE_UPDATE_ENABLE;		// EHAL_PWM_TOM_1_3_PORT_0_4_DRV_LS_U
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL4 = EHALPWM_WRITE_UPDATE_ENABLE;		// EHAL_PWM_TOM_1_4_PORT_0_5_DRV_HS_V
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL5 = EHALPWM_WRITE_UPDATE_ENABLE;		// EHAL_PWM_TOM_1_5_PORT_0_6_DRV_LS_V
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL6 = EHALPWM_WRITE_UPDATE_ENABLE;		// EHAL_PWM_TOM_1_6_PORT_0_2_DRV_LS_W
}

void EhalPwm_SR_Update_Disable(void)
{
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL1 = EHALPWM_WRITE_UPDATE_DISABLE;		// EHAL_PWM_TOM_1_1_PORT_0_1_DRV_HS_W
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL2 = EHALPWM_WRITE_UPDATE_DISABLE;		// EHAL_PWM_TOM_1_2_PORT_0_3_DRV_HS_U
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL3 = EHALPWM_WRITE_UPDATE_DISABLE;		// EHAL_PWM_TOM_1_3_PORT_0_4_DRV_LS_U
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL4 = EHALPWM_WRITE_UPDATE_DISABLE;		// EHAL_PWM_TOM_1_4_PORT_0_5_DRV_HS_V
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL5 = EHALPWM_WRITE_UPDATE_DISABLE;		// EHAL_PWM_TOM_1_5_PORT_0_6_DRV_LS_V
	GTM_TOM1_TGC0_GLB_CTRL.B.UPEN_CTRL6 = EHALPWM_WRITE_UPDATE_DISABLE;		// EHAL_PWM_TOM_1_6_PORT_0_2_DRV_LS_W
}

void EhalPwm_Init(void)
{
	Pwm_17_GtmCcu6_SetPeriodAndDuty(EHALPWM_TOM_1_0_PORT_0_0_DRV_PWM_REF,vEhalPwm_MaxDutyTickValue,vEhalPwm_HalfDutyTickValue);
	/* Notification will be called when a rising edge occurs on the PWM Output signal.
	 * #define PWM_17_GTMCCU6_RISING_EDGE     ((Pwm_17_GtmCcu6_EdgeNotificationType)(1))
	 */

	/* Notification will be called when a falling edge occurs on the PWM output signal
	 * #define PWM_17_GTMCCU6_FALLING_EDGE    ((Pwm_17_GtmCcu6_EdgeNotificationType)(2))
	 */

	/* Notification will be called when both a rising edge or falling edge
	 * (means any edge) occurs on the PWM output signal
	 * #define PWM_17_GTMCCU6_BOTH_EDGES      ((Pwm_17_GtmCcu6_EdgeNotificationType)(3))
	 */
	Pwm_17_GtmCcu6_EnableNotification(EHALPWM_TOM_1_0_PORT_0_0_DRV_PWM_REF, PWM_17_GTMCCU6_RISING_EDGE);
	EhalPwm_SR_Update_Enable();
}

void EhalPwm_Module_All_Disable(void)
{
	EhalPwm_Channel_Output_Disable();
	EhalPwm_SR_Update_Disable();
}

void EhalPwm_Module_All_Enable(void)
{
	EhalPwm_SR_Update_Enable();
	EhalPwm_Channel_Output_Enable();
}

inline void EhalPwm_MotorDrive(Pwm_17_GtmCcu6_ChannelType ChannelNumber, uint32 DutyCycle)
{
	uint16 CenterAlign = 0, ComparePeriod = 0, CompareDuty = 0, set_Duty = 0;

	CenterAlign		= (uint16)(DutyCycle * MT_1_OVR_2);
	set_Duty		= PwmBound(CenterAlign, ((int)vEhalPwm_HalfDutyTickValue - vEhalPwm_DeadTimeValue - CONS_1), (vEhalPwm_DeadTimeValue + CONS_1));
	ComparePeriod	= (int)vEhalPwm_HalfDutyTickValue + set_Duty;
	CompareDuty		= (int)vEhalPwm_HalfDutyTickValue - set_Duty;

	switch(ChannelNumber)
	{
		case EHALPWM_TOM_1_2_PORT_0_3_DRV_HS_U:
			GTM_TOM1_CH2_SR0.U	= CompareDuty;
			GTM_TOM1_CH2_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			break;
		case EHALPWM_TOM_1_3_PORT_0_4_DRV_LS_U:
			GTM_TOM1_CH3_SR0.U	= ComparePeriod;
			GTM_TOM1_CH3_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;

		case EHALPWM_TOM_1_4_PORT_0_5_DRV_HS_V:
			GTM_TOM1_CH4_SR0.U	= CompareDuty;
			GTM_TOM1_CH4_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			break;
		case EHALPWM_TOM_1_5_PORT_0_6_DRV_LS_V:
			GTM_TOM1_CH5_SR0.U	= ComparePeriod;
			GTM_TOM1_CH5_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;

		case EHALPWM_TOM_1_1_PORT_0_1_DRV_HS_W:
			GTM_TOM1_CH1_SR0.U	= CompareDuty;
			GTM_TOM1_CH1_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			break;
		case EHALPWM_TOM_1_6_PORT_0_2_DRV_LS_W:
			GTM_TOM1_CH6_SR0.U	= ComparePeriod;
			GTM_TOM1_CH6_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;

		default: break;
	}
}

void EhalPwm_Module_Ch_Control(uint8 mode, uint16 OutValue)
{
	typPwm_Output_Mode Pwm_Output_Mode = U_POLE_LOW;
	uint16 CenterAlign = 0, ComparePeriod = 0, CompareDuty = 0, set_Duty = 0;

	CenterAlign		= (uint16)(OutValue * MT_1_OVR_2);
	set_Duty		= PwmBound(CenterAlign, ((int)vEhalPwm_HalfDutyTickValue - vEhalPwm_DeadTimeValue - CONS_1), (vEhalPwm_DeadTimeValue + CONS_1));
	ComparePeriod	= (int)vEhalPwm_HalfDutyTickValue + set_Duty;
	CompareDuty		= (int)vEhalPwm_HalfDutyTickValue - set_Duty;

	Pwm_Output_Mode	= mode;

	switch(Pwm_Output_Mode)
	{
		case U_POLE_LOW:
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT2 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT3 = EHALPWM_CHANNEL_OUTPUT_ENABLE;

			GTM_TOM1_CH2_SR0.U	= CompareDuty;
			GTM_TOM1_CH2_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			GTM_TOM1_CH3_SR0.U	= ComparePeriod;
			GTM_TOM1_CH3_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;
		case U_POLE_HIGH:
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT2 = EHALPWM_CHANNEL_OUTPUT_ENABLE;
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT3 = EHALPWM_CHANNEL_OUTPUT_ENABLE;

			GTM_TOM1_CH2_SR0.U	= CompareDuty;
			GTM_TOM1_CH2_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			GTM_TOM1_CH3_SR0.U	= ComparePeriod;
			GTM_TOM1_CH3_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;
		case U_POLE_OPEN:
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT2 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT3 = EHALPWM_CHANNEL_OUTPUT_DISABLE;

			GTM_TOM1_CH2_SR0.U	= CompareDuty;
			GTM_TOM1_CH2_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			GTM_TOM1_CH3_SR0.U	= ComparePeriod;
			GTM_TOM1_CH3_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;

		case V_POLE_LOW:
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT4 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT5 = EHALPWM_CHANNEL_OUTPUT_ENABLE;

			GTM_TOM1_CH4_SR0.U	= CompareDuty;
			GTM_TOM1_CH4_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			GTM_TOM1_CH5_SR0.U	= ComparePeriod;
			GTM_TOM1_CH5_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;
		case V_POLE_HIGH:
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT4 = EHALPWM_CHANNEL_OUTPUT_ENABLE;
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT5 = EHALPWM_CHANNEL_OUTPUT_ENABLE;

			GTM_TOM1_CH4_SR0.U	= CompareDuty;
			GTM_TOM1_CH4_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			GTM_TOM1_CH5_SR0.U	= ComparePeriod;
			GTM_TOM1_CH5_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;
		case V_POLE_OPEN:
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT4 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT5 = EHALPWM_CHANNEL_OUTPUT_DISABLE;

			GTM_TOM1_CH4_SR0.U	= CompareDuty;
			GTM_TOM1_CH4_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			GTM_TOM1_CH5_SR0.U	= ComparePeriod;
			GTM_TOM1_CH5_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;

		case W_POLE_LOW:
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT1 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT6 = EHALPWM_CHANNEL_OUTPUT_ENABLE;

			GTM_TOM1_CH1_SR0.U	= CompareDuty;
			GTM_TOM1_CH1_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			GTM_TOM1_CH6_SR0.U	= ComparePeriod;
			GTM_TOM1_CH6_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;
		case W_POLE_HIGH:
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT1 = EHALPWM_CHANNEL_OUTPUT_ENABLE;
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT6 = EHALPWM_CHANNEL_OUTPUT_ENABLE;

			GTM_TOM1_CH1_SR0.U	= CompareDuty;
			GTM_TOM1_CH1_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			GTM_TOM1_CH6_SR0.U	= ComparePeriod;
			GTM_TOM1_CH6_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;
		case W_POLE_OPEN:
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT1 = EHALPWM_CHANNEL_OUTPUT_DISABLE;
			GTM_TOM1_TGC0_OUTEN_STAT.B.OUTEN_STAT6 = EHALPWM_CHANNEL_OUTPUT_DISABLE;

			GTM_TOM1_CH1_SR0.U	= CompareDuty;
			GTM_TOM1_CH1_SR1.U	= ComparePeriod - vEhalPwm_DeadTimeValue;
			GTM_TOM1_CH6_SR0.U	= ComparePeriod;
			GTM_TOM1_CH6_SR1.U	= CompareDuty - vEhalPwm_DeadTimeValue;
			break;
		default:
			break;
	}
}

void EhalPwm_SetPwm(uint8 pwm_out_ch, uint16 duty_001per)
{
	uint16 duty_tick;

	duty_tick = (uint16)((uint32)vEhalPwm_MaxDutyTickValue * duty_001per / EHALPWM_MOT_PERIOD);

	switch(pwm_out_ch)
	{
	case EHALPWM_TOM_1_2_PORT_0_3_DRV_HS_U:
		Pwm_17_GtmCcu6_SetPeriodAndDuty(EHALPWM_TOM_1_2_PORT_0_3_DRV_HS_U, EHALPWM_POSITION_PERIOD, duty_tick);
		break;
	case EHALPWM_TOM_1_4_PORT_0_5_DRV_HS_V:
		Pwm_17_GtmCcu6_SetPeriodAndDuty(EHALPWM_TOM_1_4_PORT_0_5_DRV_HS_V, EHALPWM_MOT_PERIOD, duty_tick);
		break;
	case EHALPWM_TOM_1_1_PORT_0_1_DRV_HS_W:
		Pwm_17_GtmCcu6_SetPeriodAndDuty(EHALPWM_TOM_1_1_PORT_0_1_DRV_HS_W, EHALPWM_MOT_PERIOD, duty_tick);
		break;
	case EHALPWM_TOM_1_3_PORT_0_4_DRV_LS_U:
		Pwm_17_GtmCcu6_SetPeriodAndDuty(EHALPWM_TOM_1_3_PORT_0_4_DRV_LS_U, EHALPWM_MOT_PERIOD, duty_tick);
		break;
	case EHALPWM_TOM_1_5_PORT_0_6_DRV_LS_V:
		Pwm_17_GtmCcu6_SetPeriodAndDuty(EHALPWM_TOM_1_5_PORT_0_6_DRV_LS_V, EHALPWM_MOT_PERIOD, duty_tick);
		break;
	case EHALPWM_TOM_1_6_PORT_0_2_DRV_LS_W:
		Pwm_17_GtmCcu6_SetPeriodAndDuty(EHALPWM_TOM_1_6_PORT_0_2_DRV_LS_W, EHALPWM_MOT_PERIOD, duty_tick);
		break;
//	case EHAL_PWM_OUT:
//		Pwm_17_Gtm_SetPeriodAndDuty(EHAL_PWM_OUT, EHALPWM_MOT_PERIOD, duty_tick);
//		break;
	default:
		break;
	}
}

inline void EhalPwm_Half_Output(void)
{
	EhalPwm_MotorDrive(PwmChannel_U_H,(uint16)vEhalPwm_HalfDutyTickValue);
	EhalPwm_MotorDrive(PwmChannel_U_L,(uint16)vEhalPwm_HalfDutyTickValue);
	EhalPwm_MotorDrive(PwmChannel_V_H,(uint16)vEhalPwm_HalfDutyTickValue);
	EhalPwm_MotorDrive(PwmChannel_V_L,(uint16)vEhalPwm_HalfDutyTickValue);
	EhalPwm_MotorDrive(PwmChannel_W_H,(uint16)vEhalPwm_HalfDutyTickValue);
	EhalPwm_MotorDrive(PwmChannel_W_L,(uint16)vEhalPwm_HalfDutyTickValue);
}

inline void EhalPwm_Idle_Output(void)
{
	Pwm_17_GtmCcu6_SetOutputToIdle(PwmChannel_U_H);
	Pwm_17_GtmCcu6_SetOutputToIdle(PwmChannel_U_L);
	Pwm_17_GtmCcu6_SetOutputToIdle(PwmChannel_V_H);
	Pwm_17_GtmCcu6_SetOutputToIdle(PwmChannel_V_L);
	Pwm_17_GtmCcu6_SetOutputToIdle(PwmChannel_W_H);
	Pwm_17_GtmCcu6_SetOutputToIdle(PwmChannel_W_L);
}

uint8 vRead_Idlelevel[6];
uint8 vWrite_Idlelevel[6];
void EhalPwm_Test_10ms(void)
{

	switch(vEhalPwm_TestConfig.test_case)
	{
		case 0:
			vEhalPwm_TestConfig.test_case=0;
			break;
		case 1:
			Pwm_17_GtmCcu6_Init(&Pwm_17_GtmCcu6_Config);
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 2:
			Pwm_17_GtmCcu6_DeInit();
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 3:
			EhalPwm_MotorDrive(vEhalPwm_TestConfig.ch_num, vEhalPwm_TestConfig.duty_tick);
//			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 4:
			Pwm_17_GtmCcu6_SetDutyCycle(vEhalPwm_TestConfig.ch_num, vEhalPwm_TestConfig.duty_tick);
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 5:
			Pwm_17_GtmCcu6_SetPeriodAndDuty(vEhalPwm_TestConfig.ch_num, vEhalPwm_TestConfig.period_tick, vEhalPwm_TestConfig.duty_tick);
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 6:
			EhalPwm_Init();
//			Pwm_17_GtmCcu6_SetOutputToIdle(vEhalPwm_TestConfig.ch_num);
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 7:
			// PWM_MODULE_CHANNEL_OFF
			EhalPwm_Module_All_Disable();
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 8:
			// PWM_MODULE_CHANNEL_ON
			EhalPwm_Module_All_Enable();
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 9:
			/* PWM_17_GTMCCU6_RISING_EDGE     ((Pwm_17_GtmCcu6_EdgeNotificationType)(1))
			 * PWM_17_GTMCCU6_FALLING_EDGE    ((Pwm_17_GtmCcu6_EdgeNotificationType)(2))
			 * PWM_17_GTMCCU6_BOTH_EDGES      ((Pwm_17_GtmCcu6_EdgeNotificationType)(3))
			 */
			Pwm_17_GtmCcu6_EnableNotification(vEhalPwm_TestConfig.ch_num, vEhalPwm_TestConfig.edge_type);
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 10:
			Pwm_17_GtmCcu6_DisableNotification(vEhalPwm_TestConfig.ch_num);
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 11:
			vRead_Idlelevel[0] = GTM_TOM1_CH2_STAT.B.OL;	//DRV_HS_U
			vRead_Idlelevel[1] = GTM_TOM1_CH3_STAT.B.OL;	//DRV_LS_U
			vRead_Idlelevel[2] = GTM_TOM1_CH4_STAT.B.OL;	//DRV_HS_V
			vRead_Idlelevel[3] = GTM_TOM1_CH5_STAT.B.OL;	//DRV_LS_V
			vRead_Idlelevel[4] = GTM_TOM1_CH1_STAT.B.OL;	//DRV_HS_W
			vRead_Idlelevel[5] = GTM_TOM1_CH6_STAT.B.OL;	//DRV_LS_W
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 12:
			GTM_TOM1_CH2_CTRL.B.SL = vWrite_Idlelevel[0];	//DRV_HS_U
			GTM_TOM1_CH3_CTRL.B.SL = vWrite_Idlelevel[1];	//DRV_LS_U
			GTM_TOM1_CH4_CTRL.B.SL = vWrite_Idlelevel[2];	//DRV_HS_V
			GTM_TOM1_CH5_CTRL.B.SL = vWrite_Idlelevel[3];	//DRV_LS_V
			GTM_TOM1_CH1_CTRL.B.SL = vWrite_Idlelevel[4];	//DRV_HS_W
			GTM_TOM1_CH6_CTRL.B.SL = vWrite_Idlelevel[5];	//DRV_LS_W
			vEhalPwm_TestConfig.test_case = 0;
			break;
		case 13:
			GTM_TOM1_TGC0_GLB_CTRL.B.RST_CH1 = 1;			// 0B No action, 1B Reset channel
			GTM_TOM1_TGC0_GLB_CTRL.B.RST_CH2 = 1;			// 0B No action, 1B Reset channel
			GTM_TOM1_TGC0_GLB_CTRL.B.RST_CH3 = 1;			// 0B No action, 1B Reset channel
			GTM_TOM1_TGC0_GLB_CTRL.B.RST_CH4 = 1;			// 0B No action, 1B Reset channel
			GTM_TOM1_TGC0_GLB_CTRL.B.RST_CH5 = 1;			// 0B No action, 1B Reset channel
			GTM_TOM1_TGC0_GLB_CTRL.B.RST_CH6 = 1;			// 0B No action, 1B Reset channel
			vEhalPwm_TestConfig.test_case = 0;
			break;
		default:
			break;
	}
}

void PwmChannel_0_Cbk_Notification (void) // For Double Sampling
{
//	uint32 sys_time_start;
//	uint32 sys_time_finish;
//	sys_time_start = BswSys_GetSysTime();

	vEhalPwm_TestConfig.noti_count++;
	ShrHWIA_BswPwm_Cbk_ISR();
//	sys_time_finish = BswSys_GetSysTime();
//	vBswSys_ISR_ElapsedTime = vBswSys_ISR_ElapsedTime + sys_time_finish - sys_time_start;
}
//////////////////////////////////////////////////////////////////////////////////////////////////////////////
