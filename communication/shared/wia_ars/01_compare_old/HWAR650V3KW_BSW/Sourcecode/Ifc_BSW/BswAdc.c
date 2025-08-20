/*
 * BswAdc.c
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#include "BswAdc.h"
#include "EhalAdc.h"

uint8 vBswAdc_PrebuildTest;

float ShrHWIA_BswAdc_GetPhyValue(uint8 ch)
{
	float result = 0.0f;

    switch(ch)
    {
        case BSWADC_CH_SENS_CURR_U:
        	result = (float)meas.measured.tFPhU.raw;
            break;
        case BSWADC_CH_SENS_CURR_V:
        	result = (float)meas.measured.tFPhV.raw;
            break;
        case BSWADC_CH_SENS_CURR_W:
        	result = (float)meas.measured.tFPhW.raw;
            break;
        case BSWADC_CH_SENS_HV:
        	result = (float)meas.measured.tFHVdcb.filt;
            break;
        case BSWADC_CH_SENS_VDD_15V:
        	result = (float)meas.measured.tFSmps.filt;
            break;
        case BSWADC_CH_SENS_VDD_5V0:
        	result = (float)meas.measured.tFVdd.filt;
            break;
        case BSWADC_CH_SENS_LV:
        	result = (float)meas.measured.tFLVdcb.filt;
            break;
        case BSWADC_CH_SENS_IG:
        	result = (float)meas.measured.tFIGdcb.filt;
            break;
        case BSWADC_CH_VUC_3V3:
        	result = (float)meas.measured.tFVmcudcb.filt;
            break;
        case BSWADC_CH_VCOM_5V0:
        	result = (float)meas.measured.tFVcomdcb.filt;
            break;
        case BSWADC_CH_VT1_5V0:
        	result = (float)meas.measured.tFVtr1dcb.filt;
            break;
        case BSWADC_CH_VT2_5V0:
        	result = (float)meas.measured.tFVtr2dcb.filt;
            break;
        case BSWADC_CH_VREF_5V0:
        	result = (float)meas.measured.tFVrefdcb.filt;
            break;
        case BSWADC_CH_SENS_PCB_TEMP:
        	result = (float)meas.measured.tFPcbTemp.filt;
            break;
        case BSWADC_CH_SENS_IPM_TEMP:
        	result = (float)meas.measured.tFIgbtTemp.filt;
            break;
        case BSWADC_CH_SENS_MOT_TEMP:
        	result = (float)meas.measured.tFMotorTemp.filt;
            break;
        default:
        	result = 0.0f;
            // Handle unknown channel case
            break;
    }

    return result; // Default return value
}
