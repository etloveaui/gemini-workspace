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
        case BSWADC_CH_SENS_CURR_U_RAW:
        	if(meas.flag.Current_Cal == PASS)				result = (float)meas.measured.tFPhA.raw;
        	else											result = (float)0.0f;
            break;
        case BSWADC_CH_SENS_CURR_W_RAW:
        	if(meas.flag.Current_Cal == PASS)				result = (float)meas.measured.tFPhC.raw;
        	else											result = (float)0.0f;
            break;
        case BSWADC_CH_SENS_CURR_DC_RAW:
        	if(meas.flag.Current_Cal == PASS)				result = (float)meas.measured.tFIdcb.raw;
        	else											result = (float)0.0f;
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
        case BSWADC_CH_VUC_5V0:
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

uint8 ShrHWIA_BswAdc_GetCurrentCalibStatus(void)
{
    uint8 result;

    switch(meas.flag.Current_Cal)
    {
        case IN_PROGRESS:
            result = BSWADC_CALIB_IN_PROGRESS;
            break;
        case PASS:
            result = BSWADC_CALIB_PASS;
            break;
        case FAIL:
            result = BSWADC_CALIB_FAIL;
            break;
        default:
            result = BSWADC_CALIB_IN_PROGRESS;
            break;
    }

    return result;
}

uint8 ShrHWIA_BswAdc_GetMotorTempErrStatus(void)
{
    uint8 result;

    result = meas.MTR_NTC_Sensor_Error_F;

    return result;
}
