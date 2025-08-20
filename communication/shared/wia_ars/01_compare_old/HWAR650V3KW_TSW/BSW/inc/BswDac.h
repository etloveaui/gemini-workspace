/*
 * BswDac.h
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#ifndef BSWDAC_H_
#define BSWDAC_H_

#include "Platform_Types.h"

#define BSWDAC_CH_1    (0U)
#define BSWDAC_CH_2    (1U)
#define BSWDAC_CH_3    (2U)
#define BSWDAC_CH_4    (3U)

extern void ShrHWIA_BswDac_SetValue(uint8 ch, float value, float max, float min);


#endif /* IFC_ASW_BSWDAC_H_ */
