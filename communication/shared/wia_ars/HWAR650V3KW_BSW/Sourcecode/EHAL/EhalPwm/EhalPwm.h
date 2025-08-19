/*
 * PwmHal.h
 *
 *  Created on: 2022. 2. 16.
 *      Author: dell
 */

#ifndef BSW_EHAL_EHALPWM_EHALPWM_H_
#define BSW_EHAL_EHALPWM_EHALPWM_H_

#include "Platform_Types.h"
#include "IfxGtm_reg.h"
#include "Pwm_17_GtmCcu6_Cfg.h"
#include "Pwm_17_GtmCcu6.h"
#include "Pwm_17_GtmCcu6_Cbk.h"
#include "_Conf/Global_Config.h"

/* PWM_DEFINE */
#define PWM_SWITCHING_FREQUENCY_16K			(16000)
#define PWM_MAX_DUTY_VALUE_16K				(6250)
#define PWM_HALF_DUTY_VALUE_16K				(3125)
#define PWM_SAMPLING_TIME_VALUE				(0.0000625f)
#define PWM_DEAD_TIME_VALUE					(200)					//2.0us

#define PWM_UPDATE_DELAY_CONDITION_MAX		(8500)

#define EHALPWM_TOM_1_0_PORT_0_0_DRV_PWM_REF					(Pwm_17_GtmCcu6Conf_PwmChannel_PwmChannel_0)
#define EHALPWM_TOM_1_7_PORT_0_8_ADC_SYNC						(Pwm_17_GtmCcu6Conf_PwmChannel_PwmChannel_1)
#define EHALPWM_TOM_1_1_PORT_0_1_DRV_HS_W						(Pwm_17_GtmCcu6Conf_PwmChannel_PwmChannel_2)
#define EHALPWM_TOM_1_2_PORT_0_3_DRV_HS_U						(Pwm_17_GtmCcu6Conf_PwmChannel_PwmChannel_3)
#define EHALPWM_TOM_1_3_PORT_0_4_DRV_LS_U						(Pwm_17_GtmCcu6Conf_PwmChannel_PwmChannel_4)
#define EHALPWM_TOM_1_4_PORT_0_5_DRV_HS_V						(Pwm_17_GtmCcu6Conf_PwmChannel_PwmChannel_5)
#define EHALPWM_TOM_1_5_PORT_0_6_DRV_LS_V						(Pwm_17_GtmCcu6Conf_PwmChannel_PwmChannel_6)
#define EHALPWM_TOM_1_6_PORT_0_2_DRV_LS_W						(Pwm_17_GtmCcu6Conf_PwmChannel_PwmChannel_7)
#define EHALPWM_ATOM_3_4_PORT_33_12_LED_STATUS					(Pwm_17_GtmCcu6Conf_PwmChannel_PwmChannel_8)

#ifndef EHALPWM_WRITE_UPDATE_ENABLE
#define EHALPWM_WRITE_UPDATE_ENABLE			(0x2)
#endif
#ifndef EHALPWM_WRITE_UPDATE_DISABLE
#define EHALPWM_WRITE_UPDATE_DISABLE		(0x1)
#endif
#ifndef EHALPWM_READ_UPDATE_ENABLE
#define EHALPWM_READ_UPDATE_ENABLE			(0x3)
#endif
#ifndef EHALPWM_READ_UPDATE_DISABLE
#define EHALPWM_READ_UPDATE_DISABLE			(0x0)
#endif

#ifndef EHALPWM_CHANNEL_OUTPUT_ENABLE
#define EHALPWM_CHANNEL_OUTPUT_ENABLE		(0x2)
#endif

#ifndef EHALPWM_CHANNEL_OUTPUT_DISABLE
#define EHALPWM_CHANNEL_OUTPUT_DISABLE		(0x1)
#endif

#define ICU_T_10MS						(0.01f)
// ICU

#define EHAL_PWM_IN						0
#define EHAL_MOT_HALL_W					1
#define EHAL_MOT_HALL_V					2
#define EHAL_MOT_HALL_U					3
#define EHAL_MOT_PMIC_ERR				4
#define EHAL_DIG_BTS3800				5
#define EHAL_POS_SEN_INPUT				6

#define ICU_A1333_NOT_UPDATE_PERIOD		(0.1f/ICU_T_10MS)							//0.1s

//PWM
#define PwmChannel_U_H					(EHALPWM_TOM_1_2_PORT_0_3_DRV_HS_U)
#define PwmChannel_U_L					(EHALPWM_TOM_1_3_PORT_0_4_DRV_LS_U)
#define PwmChannel_V_H					(EHALPWM_TOM_1_4_PORT_0_5_DRV_HS_V)
#define PwmChannel_V_L					(EHALPWM_TOM_1_5_PORT_0_6_DRV_LS_V)
#define PwmChannel_W_H					(EHALPWM_TOM_1_1_PORT_0_1_DRV_HS_W)
#define PwmChannel_W_L					(EHALPWM_TOM_1_6_PORT_0_2_DRV_LS_W)

#define SEC_TO_US						(1000000U)
#define EHALPWM_MOT_PERIOD				(10000U)	// 0.1ms, 10kHz, GTM Fixed clock_0 @100Mhz,  0.01us/1tick
#define EHALPWM_POSITION_PERIOD			(62500U)	// 10ms, 100Hz, GTM Fixed clock_1 @6.25Mhz,  0.16us/1tick

#define MODE_GAIN						(3)
#define PWM_OUTMODE_MAX					(8)

typedef struct{
	uint32 test_case;
	Pwm_17_GtmCcu6_ChannelType ch_num;
	uint32 duty_tick;
	Pwm_17_GtmCcu6_PeriodType period_tick;
	Pwm_17_GtmCcu6_OutputStateType output_state;
	Pwm_17_GtmCcu6_EdgeNotificationType edge_type;
	uint32 noti_count;
}typEhalPwm_TestConfig;

typedef enum{
	U_POLE_LOW,
	U_POLE_HIGH,
	U_POLE_OPEN,
	V_POLE_LOW,
	V_POLE_HIGH,
	V_POLE_OPEN,
	W_POLE_LOW,
	W_POLE_HIGH,
	W_POLE_OPEN
}typPwm_Output_Mode;

//typedef struct{
//	uint8 state;
//	uint16 duty_001per;
//	uint32 peoriod_us;
//}typEhalPwm_IcuMonitor;

//extern typEhalPwm_IcuMonitor vEhalPwm_IcuMonitor[7];

/////////////////// Debug ///////////////////////////////////////////
extern uint16 vEhalPwm_DeadTimeValue;
extern uint16 vEhalPwm_FrequencyValue;
extern uint16 vEhalPwm_MaxDutyTickValue, vEhalPwm_HalfDutyTickValue;
extern float vEhalPwm_SamplingTime;
/////////////////////////////////////////////////////////////////////


//extern void EhalIcu_Start(void);
//extern void EhalIcu_Task_1ms(void);

extern void EhalPwm_Init(void);

extern void EhalPwm_SetPwm(uint8 pwm_out_ch, uint16 duty_001per);
//extern uint8 EhalPwm_GetDuty(uint8 pwm_ch_in, uint16* duty_001per, uint16* frequency);
extern void EhalPwm_Test_10ms(void);
extern inline void EhalPwm_MotorDrive(Pwm_17_GtmCcu6_ChannelType ChannelNumber, uint32 DutyCycle);

extern inline void EhalPwm_Half_Output(void);
extern inline void EhalPwm_Idle_Output(void);

extern void EhalPwm_Module_All_Disable(void);
extern void EhalPwm_Module_All_Enable(void);

extern void EhalPwm_Channel_Output_Enable(void);
extern void EhalPwm_Channel_Output_Disable(void);

extern void EhalPwm_SR_Update_Enable(void);
extern void EhalPwm_SR_Update_Disable(void);

extern void EhalPwm_Module_Ch_Control(uint8 mode, uint16 OutValue);

#endif /* BSW_EHAL_EHALPWM_EHALPWM_H_ */
