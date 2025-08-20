/*
 * BswDac.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#include "BswDac.h"
#include "EHAL/EhalDac/EhalDac.h"

void ShrHWIA_BswDac_SetValue(uint8 ch, float value, float max, float min)
{
	Qspi2_DAC_Communication(ch, value, max, min);
}
