/*
 * BswAdc.h
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#ifndef BSWADC_H_
#define BSWADC_H_

#include "Platform_Types.h"

#define BSWADC_CH_SENS_CURR_U_RAW	(0U)
#define BSWADC_CH_SENS_CURR_W_RAW	(1U)
#define BSWADC_CH_SENS_CURR_DC_RAW	(2U)
#define BSWADC_CH_SENS_HV			(3U)

#define BSWADC_CH_SENS_VDD_15V		(4U)
#define BSWADC_CH_SENS_VDD_5V0		(5U)
#define BSWADC_CH_SENS_LV			(6U)
#define BSWADC_CH_SENS_IG			(7U)
#define BSWADC_CH_VUC_5V0			(8U)
#define BSWADC_CH_VCOM_5V0			(9U)
#define BSWADC_CH_VT1_5V0			(10U)
#define BSWADC_CH_VT2_5V0			(11U)
#define BSWADC_CH_VREF_5V0			(12U)

#define BSWADC_CH_SENS_PCB_TEMP		(13U)
#define BSWADC_CH_SENS_IPM_TEMP		(14U)
#define BSWADC_CH_SENS_MOT_TEMP		(15U)

// Current Calibration Status Definitions
#define BSWADC_CALIB_IN_PROGRESS    (0U)
#define BSWADC_CALIB_PASS           (1U)
#define BSWADC_CALIB_FAIL           (2U)

// Motor Temperature Sensor Error Status Definitions
#define BSWADC_MOTOR_TEMP_VALID     (0U)
#define BSWADC_MOTOR_TEMP_INVALID   (1U)

extern float ShrHWIA_BswAdc_GetPhyValue(uint8 ch);
extern uint8 ShrHWIA_BswAdc_GetCurrentCalibStatus(void);
extern uint8 ShrHWIA_BswAdc_GetMotorTempErrStatus(void);

#endif /* BSWADC_H_ */
