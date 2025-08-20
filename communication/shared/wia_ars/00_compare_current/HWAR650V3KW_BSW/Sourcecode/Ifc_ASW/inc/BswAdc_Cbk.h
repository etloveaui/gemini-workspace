/*
 * BswAdc_Cbk.h
 *
 *  Created on: 2024. 12. 19.
 *      Author: jaegalrang
 */

#ifndef BSWADC_CBK_H_
#define BSWADC_CBK_H_

#include "Platform_Types.h"

extern boolean vBswAdc_DIR;
extern float vBswAdc_gDACTest;
extern float vBswAdc_DAC_TEST_MAX;

extern uint16 vBswAdc_CbkIsrCount;

extern void ShrHWIA_BswAdc_Cbk_ISR(void);

#endif /* BSWADC_CBK_H_ */
