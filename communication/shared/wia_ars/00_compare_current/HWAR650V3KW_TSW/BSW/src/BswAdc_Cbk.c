/*
 * BswAdc_Cbk.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#include "Platform_Types.h"
#include "BswAdc.h"
#include "BswTest.h"

#include "BswDio.h"				//TEST
#include "IswHandler.h"			//TEST
#include "VectorTest.h"			//TEST

uint16 vBswAdc_CbkIsrCount;

boolean vBswAdc_DIR = 0;
float vBswAdc_gDACTest = 0.0;
float vBswAdc_DAC_TEST_MAX = 20.0;
void ShrHWIA_BswAdc_Cbk_ISR(void)
{
	vBswAdc_CbkIsrCount++;

	if (vBswAdc_DIR == TRUE){
		vBswAdc_gDACTest++;
	}
	else{
		vBswAdc_gDACTest--;
	}

	if (vBswAdc_gDACTest >= vBswAdc_DAC_TEST_MAX) {
		vBswAdc_DIR = FALSE;
	}
	else if (vBswAdc_gDACTest <= -vBswAdc_DAC_TEST_MAX) {
		vBswAdc_DIR = TRUE;
	}
	else{
		//do nothing
	}


	BswTest_Adc_ISR(); 		// Test example
	BswTest_ENC_A_ISR();	// Test example
	BswTest_ICU_ENC_ISR();	// Test example
#ifdef TEST_VECTORCONTROL_ON
	Simply_MotorContorl();			// Remove_after_a_test. //20250110_mjkim
#endif
}
