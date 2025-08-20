/*
 * BswSys_Cbk.c
 *
 *  Created on: 2024. 12. 23.
 *      Author: dell
 */


#include "BswSys_Cbk.h"

uint16 vBswSysCbk_FlsReprogramCount = 0;
void ShrHWIA_Mod_FlsReprogram_Cbk(void)
{
	vBswSysCbk_FlsReprogramCount++;
}
