/*
 * EhalIcu.h
 *
 *  Created on: 2024. 11. 4.
 *      Author: eunta
 */

#ifndef EHAL_EHALICU_EHALICU_H_
#define EHAL_EHALICU_EHALICU_H_

#include "Icu_17_TimerIp.h"
#include "Icu_17_TimerIp_Cfg.h"
#include "_Conf/Global_Config.h"

#define EHALPWM_TIM_0_0_PORT_2_5_SENS1_PWM				(IcuConf_IcuChannel_IcuChannel_0)
#define EHALPWM_TOM_2_6_PORT_15_3_SENS_INTERLOCK		(IcuConf_IcuChannel_IcuChannel_1)
#define EHALPWM_TOM_2_3_PORT_15_0_DRV_FAULT				(IcuConf_IcuChannel_IcuChannel_2)
#define EHALPWM_TIM_2_4_PORT_20_3_HV_OV_SENS			(IcuConf_IcuChannel_IcuChannel_3)
#define EHALPWM_TIM_2_7_PORT_11_12_SENS2_SENT_PWM		(IcuConf_IcuChannel_IcuChannel_4)

typedef struct{
//	uint32 test_case;
//	Icu_17_TimerIp_ChannelType ch_num;
	Icu_17_TimerIp_DutyCycleType ticks;
	Icu_17_TimerIp_DutyCycleType time;
	Icu_17_TimerIp_InputStateType status;
	uint32 frequency_001hz;
	uint16 duty_001per;
//	Icu_17_TimerIp_EdgeNotificationType
//	Icu_17_TimerIp_DutyCycleType
//	Pwm_17_GtmCcu6_OutputStateType output_state;
//	Pwm_17_GtmCcu6_EdgeNotificationType edge_type;
	uint32 noti_count;
	uint32 err_count;
}typEhalIcu_IcuMonitor;

extern void EhalIcu_Init(void);
extern void EhalIcu_Test_10ms(void);
extern void EhalIcu_Task_10ms(void);

extern typEhalIcu_IcuMonitor vEhalIcu_IcuMonitor[5];

#endif /* EHAL_EHALICU_EHALICU_H_ */
