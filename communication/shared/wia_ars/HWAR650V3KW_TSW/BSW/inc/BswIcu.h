/*
 * BswIcu.h
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#ifndef BSWICU_H_
#define BSWICU_H_

#include "Platform_Types.h"

#define BSWICU_CH_SENS1_PWM		(0U)
#define BSWICU_CH_SENS2_PWM		(1U)

extern uint32 ShrHWIA_BswIcu_GetFrequency(uint8 ch);
extern uint16 ShrHWIA_BswIcu_GetDuty(uint8 ch);

#endif /* BSWICU_H_ */
