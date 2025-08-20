/*
 * EhalIcu.c
 *
 *  Created on: 2024. 11. 4.
 *      Author: eunta
 */

#include "EhalIcu.h"
#include "BswIcu_Cbk.h"

typEhalIcu_IcuMonitor vEhalIcu_IcuMonitor[5] = {
		{{0}}, {{0}}, {{0}}, {{0}}, {{0}}
};

void EhalIcu_Init(void)
{
	Icu_17_TimerIp_EnableEdgeDetection(EHALPWM_TOM_2_6_PORT_15_3_SENS_INTERLOCK);
	Icu_17_TimerIp_EnableEdgeDetection(EHALPWM_TOM_2_3_PORT_15_0_DRV_FAULT);
	Icu_17_TimerIp_EnableEdgeDetection(EHALPWM_TIM_2_4_PORT_20_3_HV_OV_SENS);

	Icu_17_TimerIp_EnableNotification(EHALPWM_TOM_2_6_PORT_15_3_SENS_INTERLOCK);
	Icu_17_TimerIp_EnableNotification(EHALPWM_TOM_2_3_PORT_15_0_DRV_FAULT);
	Icu_17_TimerIp_EnableNotification(EHALPWM_TIM_2_4_PORT_20_3_HV_OV_SENS);

	Icu_17_TimerIp_StartSignalMeasurement(EHALPWM_TIM_0_0_PORT_2_5_SENS1_PWM);
	Icu_17_TimerIp_StartSignalMeasurement(EHALPWM_TIM_2_7_PORT_11_12_SENS2_SENT_PWM);
}

//void EhalIcu_UpdateValues(Icu_17_TimerIp_ChannelType ch_num)
//{
//	vEhalIcu_IcuMonitor[ch_num].status = Icu_17_TimerIp_GetInputState(ch_num);
//	Icu_17_TimerIp_GetDutyCycleValues(ch_num,&vEhalIcu_IcuMonitor[ch_num].ticks);
//
//	if(vEhalIcu_IcuMonitor[ch_num].ticks.PeriodTime != 0){
//		if((vEhalIcu_IcuMonitor[ch_num].ticks.PeriodTime >= ICU_MIN_PERIOD_TICKS) &&
//				(vEhalIcu_IcuMonitor[ch_num].ticks.PeriodTime <= ICU_MAX_PERIOD_TICKS))
//		{
//			vEhalIcu_IcuMonitor[ch_num].duty_001per = (uint16)((uint64)vEhalIcu_IcuMonitor[ch_num].ticks.ActiveTime * CONVERT_DUTY_001PER / (uint64)vEhalIcu_IcuMonitor[ch_num].ticks.PeriodTime);
//			vEhalIcu_IcuMonitor[ch_num].frequency_001hz = (uint32)(CONVERT_FREQUENCY_001HZ/(vEhalIcu_IcuMonitor[ch_num].ticks.PeriodTime * TICKCNT_TO_US));
//		}
//		else{
//			vEhalIcu_IcuMonitor[ch_num].frequency_001hz = 0xffffffffU;
//			vEhalIcu_IcuMonitor[ch_num].duty_001per = 0xffffU;
//		}
//	}
//	else{
//
//	}
//}

void EhalIcu_UpdateValues(Icu_17_TimerIp_ChannelType ch_num)
{
	vEhalIcu_IcuMonitor[ch_num].status = Icu_17_TimerIp_GetInputState(ch_num);
	Icu_17_TimerIp_GetDutyCycleValues(ch_num, &vEhalIcu_IcuMonitor[ch_num].ticks);

	if (vEhalIcu_IcuMonitor[ch_num].ticks.PeriodTime != 0) {
		if ((vEhalIcu_IcuMonitor[ch_num].ticks.PeriodTime >= ICU_MIN_PERIOD_TICKS) &&
				(vEhalIcu_IcuMonitor[ch_num].ticks.PeriodTime <= ICU_MAX_PERIOD_TICKS)){
			vEhalIcu_IcuMonitor[ch_num].err_count = 0;
			vEhalIcu_IcuMonitor[ch_num].duty_001per =
					(uint16)((uint64)vEhalIcu_IcuMonitor[ch_num].ticks.ActiveTime * CONVERT_DUTY_001PER /
							(uint64)vEhalIcu_IcuMonitor[ch_num].ticks.PeriodTime);
			vEhalIcu_IcuMonitor[ch_num].frequency_001hz =
					(uint32)(CONVERT_FREQUENCY_001HZ / (vEhalIcu_IcuMonitor[ch_num].ticks.PeriodTime * TICKCNT_TO_US));
		}
		else {
			vEhalIcu_IcuMonitor[ch_num].err_count++;

			if (vEhalIcu_IcuMonitor[ch_num].err_count >= ICU_ERROR_THRESHOLD){
				vEhalIcu_IcuMonitor[ch_num].frequency_001hz = 0xffffffffU;
				vEhalIcu_IcuMonitor[ch_num].duty_001per = 0xffffU;
			}
			else{
				// no action, keep previous values
			}
		}
	}
	else{
		// zero PeriodTime
	}
}


void EhalIcu_Test_10ms(void)
{
	EhalIcu_UpdateValues(EHALPWM_TIM_0_0_PORT_2_5_SENS1_PWM);
	EhalIcu_UpdateValues(EHALPWM_TIM_2_7_PORT_11_12_SENS2_SENT_PWM);
}

//void EhalIcu_Task_1ms(void)
//{
//	EhalPwm_UpdateDuty(EHAL_PWM_IN);
//	EhalPwm_UpdateDuty(EHAL_MOT_PMIC_ERR);
//	EhalPwm_UpdateDuty(EHAL_DIG_BTS3800);
//	EhalPwm_UpdateDuty(EHAL_POS_SEN_INPUT);
//}

void EhalIcu_Task_10ms(void)
{
	EhalIcu_UpdateValues(EHALPWM_TIM_0_0_PORT_2_5_SENS1_PWM);
	EhalIcu_UpdateValues(EHALPWM_TIM_2_7_PORT_11_12_SENS2_SENT_PWM);
}

void IcuChannel_1_Cbk_Notification(void)
{
	vEhalIcu_IcuMonitor[EHALPWM_TOM_2_6_PORT_15_3_SENS_INTERLOCK].status = Icu_17_TimerIp_GetInputState(EHALPWM_TOM_2_6_PORT_15_3_SENS_INTERLOCK);
	vEhalIcu_IcuMonitor[1].noti_count++;
	ShrHWIA_BswIcu_Cbk_Fault(BSWICU_FAULT_INTERLOCK);
}

void IcuChannel_2_Cbk_Notification(void)
{
	vEhalIcu_IcuMonitor[EHALPWM_TOM_2_3_PORT_15_0_DRV_FAULT].status = Icu_17_TimerIp_GetInputState(EHALPWM_TOM_2_3_PORT_15_0_DRV_FAULT);
	vEhalIcu_IcuMonitor[2].noti_count++;
	ShrHWIA_BswIcu_Cbk_Fault(BSWICU_FAULT_IPM);
}

void IcuChannel_3_Cbk_Notification(void)
{
	vEhalIcu_IcuMonitor[EHALPWM_TIM_2_4_PORT_20_3_HV_OV_SENS].status = Icu_17_TimerIp_GetInputState(EHALPWM_TIM_2_4_PORT_20_3_HV_OV_SENS);
	vEhalIcu_IcuMonitor[3].noti_count++;
	ShrHWIA_BswIcu_Cbk_Fault(BSWICU_FAULT_HVOV);
}
