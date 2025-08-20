/*
 * BswGpt.h
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#ifndef BSWGPT_H_
#define BSWGPT_H_

#include "Platform_Types.h"

#define BSWGPT_ENC_CH_SENS1		(0U)


extern uint32 ShrHWIA_BswGpt_GetEncPulseCnt(uint8 enc_ch);
extern boolean ShrHWIA_BswGpt_GetEncDirection(uint8 enc_ch);


#endif /* BSWGPT_H_ */
