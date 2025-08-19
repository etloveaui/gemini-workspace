/*
 * BswIcu.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#include "BswIcu.h"
#include "EHAL/EhalIcu/EhalIcu.h"

uint32 ShrHWIA_BswIcu_GetFrequency(uint8 ch)
{
	uint32 result = 0U;

    switch(ch)
    {
        case BSWICU_CH_SENS1_PWM:
        	result = vEhalIcu_IcuMonitor[EHALICU_TIM_0_0_PORT_2_5_SENS1_PWM].frequency_001hz;
            break;
        case BSWICU_CH_SENS2_PWM:
        	result = vEhalIcu_IcuMonitor[EHALICU_TIM_2_7_PORT_11_12_SENS2_SENT_PWM].frequency_001hz;
            break;
        default:
            // Handle unknown channel case
            break;
    }

	return result; // Default return value
}

uint16 ShrHWIA_BswIcu_GetDuty(uint8 ch)
{
	uint16 result = 0U;

    switch(ch)
    {
        case BSWICU_CH_SENS1_PWM:
        	result = vEhalIcu_IcuMonitor[EHALICU_TIM_0_0_PORT_2_5_SENS1_PWM].duty_001per;
            break;
        case BSWICU_CH_SENS2_PWM:
        	result = vEhalIcu_IcuMonitor[EHALICU_TIM_2_7_PORT_11_12_SENS2_SENT_PWM].duty_001per;
            break;
        default:
            // Handle unknown channel case
            break;
    }

	return result; // Default return value
}
