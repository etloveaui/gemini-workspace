/*
 * EhalAdc.c
 *
 *  Created on: 2022. 3. 7.
 *      Author: dell
 */
#include "BswAdc_Cbk.h"
#include "Adc_Cfg.h"
#include "Dio.h"
#include "EHAL/EhalAdc/EhalAdc.h"
#include "EHAL/EhalDio/EhalDio.h"
#include "EHAL/EhalPwm/EhalPwm.h"
#include "IfxSrc_reg.h"
//#include "EhalSys.h"

typEhalAdc_BufferStatus			vEhalAdc_ResultBufferStatus;
typEhalAdc_NotificationCount	vEhalAdc_NotificationCount;
typEhalAdc_Status				vEhalAdc_GroupConversionStatus;
uint8 vEhalAdc_Test2;

/**
 * @brief Result Buffer Declaration
 *
 * @section Hardware_Groups Hardware Groups
 * | Group Name                      | Channel Count | Channels                         | Access Mode  | Samples      |
 * |---------------------------------|---------------|----------------------------------|--------------|--------------|
 * | AdcConf_AdcGroup_AdcGroup0_Hw   | 1             | SENS_CURR_U, (SENS_CURR_U_REF)   | Single       | 1            |
 * | AdcConf_AdcGroup_AdcGroup1_Hw   | 1             | SENS_CURR_W, (SENS_CURR_W_REF)   | Single   	   | 1            |
 * | AdcConf_AdcGroup_AdcGroup2_Hw   | 1             | SENS_HV   						| Single       | 1            |
 * | AdcConf_AdcGroup_AdcGroup3_Hw   | 1             | SENS_CURR_DC, (SENS_CURR_DC_REF) | Single       | 1            |
 *
 * @section Software_Groups Software Groups
 * | Group Name                      | Channel Count | Channels                               			| Access Mode  | Samples      |
 * |---------------------------------|---------------|--------------------------------------------------|--------------|--------------|
 * | AdcConf_AdcGroup_AdcGroup0_Sw   | 2             | SENS_VDD_15V, SENS_VDD_5V0             			| Single       | 1            |
 * | AdcConf_AdcGroup_AdcGroup1_Sw   | 3             | SENS_TEMP1, SENS_PCB_TEMP, SENS_IPM_TEMP			| Single       | 1            |
 * | AdcConf_AdcGroup_AdcGroup2_Sw   | 2             | SENS_LV, SENS_IG                       			| Single       | 1            |
 * | AdcConf_AdcGroup_AdcGroup4_Sw   | 5             | VUC_5V0, VCOM_5V0, VT1_5V0, VT2_5V0, VREF_5V0    | Single       | 1            |
 */

//ADC Result Buffers
Adc_ValueGroupType vEhalAdc_AdcGroup0_Hw_Result[ADC_BUFFER_SIZE_ADC0_HW] = {0};
Adc_ValueGroupType vEhalAdc_AdcGroup1_Hw_Result[ADC_BUFFER_SIZE_ADC1_HW] = {0};
Adc_ValueGroupType vEhalAdc_AdcGroup2_Hw_Result[ADC_BUFFER_SIZE_ADC2_HW] = {0};
Adc_ValueGroupType vEhalAdc_AdcGroup3_Hw_Result[ADC_BUFFER_SIZE_ADC3_HW] = {0};
Adc_ValueGroupType vEhalAdc_AdcGroup0_Sw_Result[ADC_BUFFER_SIZE_ADC0_SW] = {0};
Adc_ValueGroupType vEhalAdc_AdcGroup1_Sw_Result[ADC_BUFFER_SIZE_ADC1_SW] = {0};
Adc_ValueGroupType vEhalAdc_AdcGroup2_Sw_Result[ADC_BUFFER_SIZE_ADC2_SW] = {0};
//Adc_ValueGroupType vEhalAdc_AdcGroup3_Sw_Result[ADC_BUFFER_SIZE_ADC3_SW] = {0};
Adc_ValueGroupType vEhalAdc_AdcGroup4_Sw_Result[ADC_BUFFER_SIZE_ADC4_SW] = {0};

// Global variables for storing ADC group converted voltages
float vEhalAdc_HwGroupVoltages[4] = {0.0, 0.0, 0.0, 0.0};  // For HW Triggered groups 0, 1, 2, 3
float vEhalAdc_SwGroupVoltages[12] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};  // For SW Triggered groups 0, 1, 2, 3, 4

/* Temperature */
#define MetalPCB_PTC_Hor	(2)
#define MetalPCB_PTC_Ver	(39)
const sint16 MetalPCB_PTC[MetalPCB_PTC_Hor][MetalPCB_PTC_Ver] ={
{6656,	6871,	7094,	7324,	7563,	7809,	8063,	8325,	8594,	8871,	9155,	9447,	9747,	10054,	10369,	10692,	11022,	11360,	11706,	12059,	12421,	12791,	13169,	13555,	13950,	14353,	14765,	15185,	15615,	16053,	16501,	16959,	17426,	17903,	18391,	18888,	19396,	19915,	20446},
{-40,	-35,	-30,	-25,	-20,	-15,	-10,	-5,		0,		5,		10,		15,		20,		25,		30,		35,		40,		45,		50,		55,		60,		65,		70,		75,		80,		85,		90,		95,		100,	105,	110,	115,	120,	125,	130,	135,	140,	145,	150}};

#define Motor_NTC_Hor	(2)
#define Motor_NTC_Ver	(22)
const float Motor_NTC[Motor_NTC_Hor][Motor_NTC_Ver] ={
{394.70,	122.00,		44.09,	27.86,	18.13,	10.00,	5.806,	4.144,	3.011,	1.668,	1.451,	0.9754,	0.5920,	0.3679,	0.2365,	0.1568,	0.1068,	0.07467,	0.05345,	0.03907,	0.02912,	0.02209},
{-50.0,		-30.0,		-10.0,	0.0,	10.0,	25.0,	40.0,	50.0,	60.0,	80.0,	85.0,	100.0,	120.0,	140.0,	160.0,	180.0,	200.0,	220.0,		240.0,		260.0,		280.0,		300.0}};

#define IGBT_NTC_Hor	(2)
#define IGBT_NTC_Ver	(39)
const float IGBT_NTC[IGBT_NTC_Hor][IGBT_NTC_Ver] ={
{1607642,	1160765,	847302,	624853,	465271,	349617,	264992,	202507,	155973,	121033,	94593,	74438,	58963,	47000,	37692,	30404,	24664,	20116,	16492,	13589,	11252,	9360,	7822,	6565,	5534,	4684,	3980,	3394,	2906,	2497,	2153,	1862,	1617,	1408,	1229,	1077,	946,	833,	736},
{	-40,	-35,		-30,	-25,	-20,	-15,	-10,	-5,		0,		5,		10,		15,		20,		25,		30,		35,		40,		45,		50,		55,		60,		65,		70,		75,		80,		85,		90,		95,		100,	105,	110,	115,	120,	125,	130,	135,	140,	145,	150}};

/* Variables Definition */
measModule_t		meas;				// Measure Module

///////////////////////////////////// ALGORITHM /////////////////////////////////////////////////
void sort(float *arr, int size)
{
    for (int i = 0; i < size-1; i++)
    {
        for (int j = i+1; j < size; j++)
        {
            if (arr[i] > arr[j])
            {
            	float tmp = arr[i];
                arr[i] = arr[j];
                arr[j] = tmp;
            }
            else{}
        }
    }
}

float trimmed_mean_filter(uint16 *samples, int size)
{
	float temp[5];
    for (int i = 0; i < size; i++)
        temp[i] = samples[i];

    sort(temp, size);

    float sum = (temp[1] + temp[2] + temp[3]);
    return (sum / 3);
}

char Meas_Clear(measModule_t *ptr)
{
    ptr->measured.tFPhA.filt			= 0.0;
    ptr->measured.tFPhB.filt			= 0.0;
    ptr->measured.tFPhC.filt			= 0.0;
    ptr->measured.tFIdcb.filt			= 0.0;

    ptr->offset.tFPhA.tFOffset			= 0.0;
	ptr->offset.tFPhB.tFOffset			= 0.0;
	ptr->offset.tFPhC.tFOffset			= 0.0;
	ptr->offset.tFIdcb.tFOffset			= 0.0;

    ptr->flag.Current_CalInitDone		= FALSE;
    ptr->flag.Current_Cal				= IN_PROGRESS;

    return 1;
}

char Meas_CalibCurrentSense(measModule_t *ptr)
{
    if(ptr->flag.Current_CalInitDone == FALSE)
    {
		ptr->calibCntr						= vEhalPwm_FrequencyValue;

		ptr->offset.tFPhA.tF_raw			= 0.0;
		ptr->offset.tFPhB.tF_raw			= 0.0;
		ptr->offset.tFPhC.tF_raw			= 0.0;
		ptr->offset.tFIdcb.tF_raw			= 0.0;

		ptr->offset.tFPhA.tFOffset			= 0.0;
		ptr->offset.tFPhB.tFOffset			= 0.0;
		ptr->offset.tFPhC.tFOffset			= 0.0;
		ptr->offset.tFIdcb.tFOffset			= 0.0;

		ptr->flag.Current_Cal				= IN_PROGRESS;
		ptr->flag.Current_CalInitDone		= TRUE;
    }
    else{}

    if (ptr->flag.Current_Cal == IN_PROGRESS)
    {
        if ((--ptr->calibCntr)<=0)
        {
        	if((ptr->offset.tFPhA.tF_raw <= CURRENT_SENSOR_LOW) || (ptr->offset.tFPhA.tF_raw >= CURRENT_SENSOR_HIGH))			ptr->Current_Sensor_Error_F = TRUE;
        	else if((ptr->offset.tFPhC.tF_raw <= CURRENT_SENSOR_LOW) || (ptr->offset.tFPhC.tF_raw >= CURRENT_SENSOR_HIGH))		ptr->Current_Sensor_Error_F = TRUE;
        	else if((ptr->offset.tFIdcb.tF_raw <= CURRENT_SENSOR_LOW) || (ptr->offset.tFIdcb.tF_raw >= CURRENT_SENSOR_HIGH))	ptr->Current_Sensor_Error_F = TRUE;
        	else{}

        	if(ptr->Current_Sensor_Error_F == FALSE)
        	{
        		ptr->offset_check_Cnt ++;
				if((ptr->offset.tFPhA.tF_raw <= CURRENT_OFFSET_ERR_MIN) || (ptr->offset.tFPhA.tF_raw >= CURRENT_OFFSET_ERR_MAX) ||
				(ptr->offset.tFPhC.tF_raw <= CURRENT_OFFSET_ERR_MIN) || (ptr->offset.tFPhC.tF_raw >= CURRENT_OFFSET_ERR_MAX) ||
				(ptr->offset.tFIdcb.tF_raw <= CURRENT_OFFSET_ERR_MIN) || (ptr->offset.tFIdcb.tF_raw >= CURRENT_OFFSET_ERR_MAX))
				{
					if(ptr->offset_check_Cnt >= MEAS_OFFSET_CHECK_PERIOD)
					{
						ptr->flag.Current_Cal			= FAIL;
						ptr->flag.Current_CalInitDone	= FALSE;
					}
					else
					{
						ptr->flag.Current_Cal 			= IN_PROGRESS;
						ptr->flag.Current_CalInitDone	= FALSE;
					}
				}
				else
				{
					ptr->flag.Current_Cal			= PASS;
					ptr->flag.Current_CalInitDone	= FALSE;
					ptr->offset.tFPhA.tFOffset		= ptr->offset.tFPhA.tF_raw;
					ptr->offset.tFPhC.tFOffset		= ptr->offset.tFPhC.tF_raw;
					ptr->offset.tFIdcb.tFOffset		= ptr->offset.tFIdcb.tF_raw;
				}
        	}
        	else
        	{
        		ptr->flag.Current_Cal			= FAIL;
        		ptr->flag.Current_CalInitDone	= FALSE;
        	}
        }
        else
        {
        	LPF(ptr->offset.tFPhA.tF_raw,	ptr->measured.tFPhA.raw,	meas.lpf_gain.IphAdcOfstLpfFct);
        	LPF(ptr->offset.tFPhC.tF_raw,	ptr->measured.tFPhC.raw,	meas.lpf_gain.IphAdcOfstLpfFct);
        	LPF(ptr->offset.tFIdcb.tF_raw,	ptr->measured.tFIdcb.raw,	meas.lpf_gain.IphAdcOfstLpfFct);
        }
    }
    else{}

    return (ptr->flag.Current_Cal);
}

char Meas_Get3PhCurrent(measModule_t *ptr)
{
	float tmp0,tmp1,tmp2;
//	tmp0 = trimmed_mean_filter(vEhalAdc_AdcGroup0_Hw_Result, 5);
//	tmp1 = trimmed_mean_filter(vEhalAdc_AdcGroup1_Hw_Result, 5);
	tmp0 = vEhalAdc_AdcGroup0_Hw_Result[0];
	tmp1 = vEhalAdc_AdcGroup1_Hw_Result[0];
	tmp2 = vEhalAdc_AdcGroup3_Hw_Result[0];

	ptr->measured.tFPhA.raw		= tmp0;
	ptr->measured.tFPhC.raw		= tmp1;
	ptr->measured.tFIdcb.raw	= tmp2;

	if(meas.flag.Current_Cal == PASS)
	{
		ptr->measured.tFPhA.raw 	= (ptr->measured.tFPhA.raw - ptr->offset.tFPhA.tFOffset);					//Current_Direction_Check
		ptr->measured.tFPhC.raw		= ((ptr->measured.tFPhC.raw - ptr->offset.tFPhC.tFOffset) * CONS_1_M);		//Current_Direction_Check

		ptr->measured.tFIdcb.raw	= (ptr->measured.tFIdcb.raw - ptr->offset.tFIdcb.tFOffset);

		ptr->measured.tFPhU.raw		= (ptr->measured.tFPhA.raw * CURRENT_GAIN);
		ptr->measured.tFPhW.raw		= (ptr->measured.tFPhC.raw * CURRENT_GAIN);
		ptr->measured.tFPhV.raw		= (CONS_1_M * ptr->measured.tFPhU.raw + CONS_1_M * ptr->measured.tFPhW.raw);

		ptr->measured.tFIdcb.raw	= (ptr->measured.tFIdcb.raw * CURRENT_GAIN);
	}
	else{}

    return(1);
}

char Meas_GetHVdcVoltage(measModule_t *ptr)
{
	ptr->measured.tFHVdcb.raw = (((float)vEhalAdc_AdcGroup2_Hw_Result[0]*ADC_SCALE)-HVDC_SYSTEM_GAIN_B)*T_HVDC_SYSTEM_GAIN_A;
	ptr->measured.tFHVdcb.raw = (ptr->measured.tFHVdcb.raw - meas.HVDC_Calibration_Value);
	LPF(ptr->measured.tFHVdcb.filt, ptr->measured.tFHVdcb.raw, meas.lpf_gain.HVdcFdbLpfFct);

    return(1);
}

char Meas_GetSmpsVoltage(measModule_t *ptr)
{
	ptr->measured.tFSmps.raw = (((float)vEhalAdc_AdcGroup0_Sw_Result[0]*ADC_SCALE)-SMPS_SYSTEM_GAIN_B)*T_SMPS_SYSTEM_GAIN_A;
	LPF(ptr->measured.tFSmps.filt, ptr->measured.tFSmps.raw, meas.lpf_gain.LVdcFdbLpfFct);

    return(1);
}

char Meas_GetVddVoltage(measModule_t *ptr)
{
	ptr->measured.tFVdd.raw = (((float)vEhalAdc_AdcGroup0_Sw_Result[1]*ADC_SCALE)-VDD_SYSTEM_GAIN_B)*T_VDD_SYSTEM_GAIN_A;
	LPF(ptr->measured.tFVdd.filt, ptr->measured.tFVdd.raw, meas.lpf_gain.LVdcFdbLpfFct);

    return(1);
}

char Meas_GetLVVoltage(measModule_t *ptr)
{
	ptr->measured.tFLVdcb.raw = ((float)vEhalAdc_AdcGroup2_Sw_Result[0]*LVDC_VOLTAGE_GAIN);
	LPF(ptr->measured.tFLVdcb.filt, ptr->measured.tFLVdcb.raw, meas.lpf_gain.LVdcFdbLpfFct);

    return(1);
}

char Meas_GetIGVoltage(measModule_t *ptr)
{
	ptr->measured.tFIGdcb.raw = (((float)vEhalAdc_AdcGroup2_Sw_Result[1]*IGDC_VOLTAGE_GAIN)+IGDC_DIODE_DROP);
	LPF(ptr->measured.tFIGdcb.filt, ptr->measured.tFIGdcb.raw, meas.lpf_gain.LVdcFdbLpfFct);

    return(1);
}

char Meas_GetVmcu_ref_com_tr1_tr2Voltage(measModule_t *ptr)
{
	ptr->measured.tFVmcudcb.raw = ((float)vEhalAdc_AdcGroup4_Sw_Result[0]*VUC_VOLTAGE_GAIN);
	ptr->measured.tFVcomdcb.raw = ((float)vEhalAdc_AdcGroup4_Sw_Result[1]*VUC_VOLTAGE_GAIN);
	ptr->measured.tFVtr1dcb.raw = ((float)vEhalAdc_AdcGroup4_Sw_Result[2]*VUC_VOLTAGE_GAIN);
	ptr->measured.tFVtr2dcb.raw = ((float)vEhalAdc_AdcGroup4_Sw_Result[3]*VUC_VOLTAGE_GAIN);
	ptr->measured.tFVrefdcb.raw = ((float)vEhalAdc_AdcGroup4_Sw_Result[4]*VUC_VOLTAGE_GAIN);

	LPF(ptr->measured.tFVmcudcb.filt, ptr->measured.tFVmcudcb.raw, meas.lpf_gain.LVdcFdbLpfFct);
	LPF(ptr->measured.tFVcomdcb.filt, ptr->measured.tFVcomdcb.raw, meas.lpf_gain.LVdcFdbLpfFct);
	LPF(ptr->measured.tFVtr1dcb.filt, ptr->measured.tFVtr1dcb.raw, meas.lpf_gain.LVdcFdbLpfFct);
	LPF(ptr->measured.tFVtr2dcb.filt, ptr->measured.tFVtr2dcb.raw, meas.lpf_gain.LVdcFdbLpfFct);
	LPF(ptr->measured.tFVrefdcb.filt, ptr->measured.tFVrefdcb.raw, meas.lpf_gain.LVdcFdbLpfFct);

    return(1);
}

char Meas_PCB_Temperature(measModule_t *ptr)
{
	int i=0,X1=0,X2=0,Y1=0,Y2=0;
	float tmp_Voltage = 0.0;
	static uint32 tmp_Resistance = 0;

	tmp_Voltage = ((float)vEhalAdc_AdcGroup1_Sw_Result[1] * ADC_SCALE);

	if(tmp_Voltage >= PCB_TEMP_NTC_MAX_VOLTAGE)		tmp_Resistance = MetalPCB_PTC[0][MetalPCB_PTC_Ver-1];
	else											tmp_Resistance	= (((tmp_Voltage * PCB_TEMP_DIV_R)/(V_REF - tmp_Voltage)) <= MetalPCB_PTC[0][0]) ? MetalPCB_PTC[0][0]:((tmp_Voltage * PCB_TEMP_DIV_R)/(V_REF - tmp_Voltage));

	for (i=0; i < MetalPCB_PTC_Ver; ++i)
	{
		if(MetalPCB_PTC[0][i] >= tmp_Resistance)
		{
			X1 = MetalPCB_PTC[0][i-1];
			X2 = MetalPCB_PTC[0][i];
			Y1 = MetalPCB_PTC[1][i-1];
			Y2 = MetalPCB_PTC[1][i];

			ptr->measured.tFPcbTemp.raw = (float)Y1 + ((float)(tmp_Resistance - X1) / (float)(X2 - X1)) * (float)(Y2 -Y1);

			break;
		}
		else{}
	}

	LPF(ptr->measured.tFPcbTemp.filt, ptr->measured.tFPcbTemp.raw, meas.lpf_gain.TemperatureLpfFct);

    return(1);
}

char Meas_MOTOR_Temperature(measModule_t *ptr)
{
	int i=0;
	float X1=0.0,X2=0.0,Y1=0.0,Y2=0.0;
	float tmp_Voltage=0.0,tmp_Resistance=0.0;

	tmp_Voltage = ((float)vEhalAdc_AdcGroup1_Sw_Result[0] * ADC_SCALE);

	if(tmp_Voltage < MOTOR_TEMP_FAULT_LOW)
	{
		ptr->measured.tFMotorTemp.raw	= -50.0f;
		ptr->measured.tFMotorTemp.filt	= -50.0f;
		ptr->MTR_NTC_Sensor_Error_F		= TRUE;
	}
	else if(tmp_Voltage > MOTOR_TEMP_FAULT_HIGH)
	{
		ptr->measured.tFMotorTemp.raw	= 300.0f;
		ptr->measured.tFMotorTemp.filt	= 300.0f;
		ptr->MTR_NTC_Sensor_Error_F		= TRUE;
	}
	else
	{
		ptr->MTR_NTC_Sensor_Error_F		= FALSE;

		tmp_Resistance	= ((V_REF * MOTOR_TEMP_PULLDOWN_R)/tmp_Voltage - (MOTOR_TEMP_PULLUP_R + MOTOR_TEMP_PULLDOWN_R));

		if(tmp_Resistance <= Motor_NTC[0][Motor_NTC_Ver-1])		tmp_Resistance = Motor_NTC[0][Motor_NTC_Ver-1];
		else if(tmp_Resistance >= Motor_NTC[0][0])				tmp_Resistance = Motor_NTC[0][0];
		else{}

		for (i=0; i < Motor_NTC_Ver; ++i)
		{
			if(Motor_NTC[0][i] <= tmp_Resistance)
			{
				X1 = Motor_NTC[0][i-1];
				X2 = Motor_NTC[0][i];
				Y1 = Motor_NTC[1][i-1];
				Y2 = Motor_NTC[1][i];

				ptr->measured.tFMotorTemp.raw = Y1 + (((tmp_Resistance - X1) / (X2 - X1)) * (Y2 -Y1));

				break;
			}
			else{}
		}
	}

	LPF(ptr->measured.tFMotorTemp.filt, ptr->measured.tFMotorTemp.raw, meas.lpf_gain.TemperatureLpfFct);

    return(1);
}

char Meas_IGBT_Temperature(measModule_t *ptr)
{
	int i=0;
	float X1=0.0,X2=0.0,Y1=0.0,Y2=0.0;
	float tmp_Voltage=0.0,tmp_Resistance=0.0;

	tmp_Voltage		= ((float)vEhalAdc_AdcGroup1_Sw_Result[2]*ADC_SCALE);
	tmp_Voltage		= (tmp_Voltage>=IGBT_TEMP_NTC_MAX_VOLTAGE)? IGBT_TEMP_NTC_MAX_VOLTAGE:(tmp_Voltage<=IGBT_TEMP_NTC_MIN_VOLTAGE)?IGBT_TEMP_NTC_MIN_VOLTAGE:tmp_Voltage;
	tmp_Voltage		= ((tmp_Voltage-IGBT_SYSTEM_GAIN_B)/IGBT_SYSTEM_GAIN_A);

	tmp_Resistance	= ((IGBT_TEMP_PULLUP_R*tmp_Voltage)/(V_REF-tmp_Voltage));
	tmp_Resistance	= ((tmp_Resistance >= IGBT_NTC[0][0])?IGBT_NTC[0][0]:(tmp_Resistance <= IGBT_NTC[0][IGBT_NTC_Ver-1])?IGBT_NTC[0][IGBT_NTC_Ver-1]:tmp_Resistance);

	for (i=0; i < IGBT_NTC_Ver; ++i)
	{
		if(IGBT_NTC[0][i] <= tmp_Resistance)
		{
			X1 = IGBT_NTC[0][i-1];
			X2 = IGBT_NTC[0][i];
			Y1 = IGBT_NTC[1][i-1];
			Y2 = IGBT_NTC[1][i];

			ptr->measured.tFIgbtTemp.raw = Y1 + (((tmp_Resistance - X1) / (X2 - X1)) * (Y2 -Y1));

			break;
		}
		else{}
	}

	LPF(ptr->measured.tFIgbtTemp.filt, ptr->measured.tFIgbtTemp.raw, meas.lpf_gain.TemperatureLpfFct);

    return(1);
}
//////////////////////////////////////////////////////////////////////////////////////////////////////

///////////////////////////////////// INIT_&_SETTING /////////////////////////////////////////////////////
void EhalAdc_ConfigureHwAdcGroup(Adc_GroupType group, Adc_ValueGroupType* resultBuffer, Std_ReturnType* bufferStatus)
{
	*bufferStatus = (Std_ReturnType)(Adc_SetupResultBuffer(group, resultBuffer));
	if (*bufferStatus != E_NOT_OK) {
		Adc_EnableHardwareTrigger(group);
		Adc_EnableGroupNotification(group);
	}
	else{
		/*Could not setup result buffer*/
	}
}

void EhalAdc_ConfigureSwAdcGroup(Adc_GroupType group, Adc_ValueGroupType* resultBuffer, Std_ReturnType* bufferStatus)
{
	*bufferStatus = (Std_ReturnType)(Adc_SetupResultBuffer(group, resultBuffer));
	if (*bufferStatus != E_NOT_OK) {
		Adc_EnableGroupNotification(group);
	}
	else{
		/*Could not setup result buffer*/
	}
}

void EhalAdc_StartGroupConversion(Adc_GroupType group)
{
    if (Adc_GetGroupStatus(group) != ADC_BUSY) {
        Adc_StartGroupConversion(group);
    }
    else{

    }
}

void EhalAdc_Init(void)
{
	EhalAdc_ConfigureHwAdcGroup(AdcConf_AdcGroup_AdcGroup0_Hw, vEhalAdc_AdcGroup0_Hw_Result, &vEhalAdc_ResultBufferStatus.AdcGroup0_Hw);
	EhalAdc_ConfigureHwAdcGroup(AdcConf_AdcGroup_AdcGroup1_Hw, vEhalAdc_AdcGroup1_Hw_Result, &vEhalAdc_ResultBufferStatus.AdcGroup1_Hw);
	EhalAdc_ConfigureHwAdcGroup(AdcConf_AdcGroup_AdcGroup2_Hw, vEhalAdc_AdcGroup2_Hw_Result, &vEhalAdc_ResultBufferStatus.AdcGroup2_Hw);
	EhalAdc_ConfigureHwAdcGroup(AdcConf_AdcGroup_AdcGroup3_Hw, vEhalAdc_AdcGroup3_Hw_Result, &vEhalAdc_ResultBufferStatus.AdcGroup3_Hw);

	EhalAdc_ConfigureSwAdcGroup(AdcConf_AdcGroup_AdcGroup0_Sw, vEhalAdc_AdcGroup0_Sw_Result, &vEhalAdc_ResultBufferStatus.AdcGroup0_Sw);
	EhalAdc_ConfigureSwAdcGroup(AdcConf_AdcGroup_AdcGroup1_Sw, vEhalAdc_AdcGroup1_Sw_Result, &vEhalAdc_ResultBufferStatus.AdcGroup1_Sw);
	EhalAdc_ConfigureSwAdcGroup(AdcConf_AdcGroup_AdcGroup2_Sw, vEhalAdc_AdcGroup2_Sw_Result, &vEhalAdc_ResultBufferStatus.AdcGroup2_Sw);
//	EhalAdc_ConfigureSwAdcGroup(AdcConf_AdcGroup_AdcGroup3_Sw, vEhalAdc_AdcGroup3_Sw_Result, &vEhalAdc_ResultBufferStatus.AdcGroup3_Sw);
	EhalAdc_ConfigureSwAdcGroup(AdcConf_AdcGroup_AdcGroup4_Sw, vEhalAdc_AdcGroup4_Sw_Result, &vEhalAdc_ResultBufferStatus.AdcGroup4_Sw);
}

void EhalAdc_LogicInit(void)
{
	meas.flag.Current_CalInitDone	= FALSE;
	meas.flag.Current_Cal			= IN_PROGRESS;
}

void EhalAdc_LPF_Init(void)
{
	FILFCT(HVDC_CUTOFF,				meas.lpf_gain.HVdcFdbLpfFct,		vEhalPwm_FrequencyValue);
	FILFCT(IOFFSET_CUTOFF,			meas.lpf_gain.IphAdcOfstLpfFct,		vEhalPwm_FrequencyValue);
	FILFCT(LVDC_CUTOFF,				meas.lpf_gain.LVdcFdbLpfFct,		FREQUENCY_100HZ);
	FILFCT(TEMPERATURE_CUTOFF,		meas.lpf_gain.TemperatureLpfFct,	FREQUENCY_10HZ);
}

//////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////// Measure_Function ////////////////////////////////////////////////
void EhalAdc_HW_Trigger_Measure(void)
{   // Read and convert ADC results for each hardware-triggered ADC group
	if(meas.flag.Current_Cal == IN_PROGRESS)		Meas_CalibCurrentSense(&meas);
	else{}

	Meas_Get3PhCurrent(&meas);
	Meas_GetHVdcVoltage(&meas);
}
/////////////////////////////////////////////////////////////////////////////////////////////

///////////////////////////////////// TASK //////////////////////////////////////////////////
void EhalAdc_Task_10ms_3(void)
{	// Read and convert ADC results for each software-triggered ADC group
	EhalAdc_StartGroupConversion(AdcConf_AdcGroup_AdcGroup2_Sw);
	Meas_GetLVVoltage(&meas);
	Meas_GetIGVoltage(&meas);
}

void EhalAdc_Task_10ms_5(void)
{	// Read and convert ADC results for each software-triggered ADC group
	EhalAdc_StartGroupConversion(AdcConf_AdcGroup_AdcGroup0_Sw);
	Meas_GetSmpsVoltage(&meas);
	Meas_GetVddVoltage(&meas);
}

void EhalAdc_Task_10ms_7(void)
{	// Read and convert ADC results for each software-triggered ADC group
	EhalAdc_StartGroupConversion(AdcConf_AdcGroup_AdcGroup4_Sw);
	Meas_GetVmcu_ref_com_tr1_tr2Voltage(&meas);
}

void EhalAdc_Task_100ms(void)
{	// Read and convert ADC results for each software-triggered ADC group
	EhalAdc_StartGroupConversion(AdcConf_AdcGroup_AdcGroup1_Sw);
//	EhalAdc_StartGroupConversion(AdcConf_AdcGroup_AdcGroup3_Sw);
	Meas_MOTOR_Temperature(&meas);
	Meas_PCB_Temperature(&meas);
	Meas_IGBT_Temperature(&meas);
}
////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////// NOTI ///////////////////////////////////
void AdcGroup0_Hw_Notification(void)
{
//	Dio_WriteChannel(EHAL_DIO_PORT_33_11, HIGH);
	vEhalAdc_NotificationCount.AdcGroup0_Hw++;
}

void AdcGroup1_Hw_Notification(void)
{
	vEhalAdc_NotificationCount.AdcGroup1_Hw++;
}

void AdcGroup2_Hw_Notification(void)
{
	vEhalAdc_NotificationCount.AdcGroup2_Hw++;
}



void AdcGroup3_Hw_Notification(void)
{
//	uint32 sys_time_start;
//	uint32 sys_time_finish;
//	sys_time_start = BswSys_GetSysTime();
	vEhalAdc_NotificationCount.AdcGroup3_Hw++;
	EhalAdc_HW_Trigger_Measure();
	ShrHWIA_BswAdc_Cbk_ISR();
//	Dio_WriteChannel(EHAL_DIO_PORT_33_11, LOW);
//	sys_time_finish = BswSys_GetSysTime();
//	vBswSys_ISR_ElapsedTime = vBswSys_ISR_ElapsedTime + sys_time_finish - sys_time_start;
}

void AdcGroup0_Sw_Notification(void)
{
	vEhalAdc_NotificationCount.AdcGroup0_Sw++;
    Adc_ReadGroup(AdcConf_AdcGroup_AdcGroup0_Sw, vEhalAdc_AdcGroup0_Sw_Result);

}

void AdcGroup1_Sw_Notification(void)
{
	vEhalAdc_NotificationCount.AdcGroup1_Sw++;
    Adc_ReadGroup(AdcConf_AdcGroup_AdcGroup1_Sw, vEhalAdc_AdcGroup1_Sw_Result);
}

void AdcGroup2_Sw_Notification(void)
{
	vEhalAdc_NotificationCount.AdcGroup2_Sw++;
    Adc_ReadGroup(AdcConf_AdcGroup_AdcGroup2_Sw, vEhalAdc_AdcGroup2_Sw_Result);
}

//void AdcGroup3_Sw_Notification(void)
//{
//	vEhalAdc_NotificationCount.AdcGroup3_Sw++;
//    Adc_ReadGroup(AdcConf_AdcGroup_AdcGroup3_Sw, vEhalAdc_AdcGroup3_Sw_Result);
//}

void AdcGroup4_Sw_Notification(void)
{
	vEhalAdc_NotificationCount.AdcGroup4_Sw++;
    Adc_ReadGroup(AdcConf_AdcGroup_AdcGroup4_Sw, vEhalAdc_AdcGroup4_Sw_Result);
}
//////////////////////////////////// TEST ///////////////////////////////////////
// Converts ADC value to voltage (0-5V range)
float EhalAdc_ConvertAdcToVoltage(int adcValue) {
    return ((float)adcValue / ADC_RESOLUTION) * V_REF;
}

// Measure function for Hardware-triggered ADC groups
void EhalAdc_HW_Trigger_Measure_Test(void)
{   // Read and convert ADC results for each hardware-triggered ADC group
    vEhalAdc_HwGroupVoltages[0] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup0_Hw_Result[0]);
    vEhalAdc_HwGroupVoltages[1] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup1_Hw_Result[0]);
    vEhalAdc_HwGroupVoltages[2] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup2_Hw_Result[0]);
    vEhalAdc_HwGroupVoltages[3] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup3_Hw_Result[0]);
}

// Measure function for Software-triggered ADC groups
void EhalAdc_SW_Trigger_Measure_Test(void)
{   // Read and convert ADC results for each software-triggered ADC group
    vEhalAdc_SwGroupVoltages[0] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup0_Sw_Result[0]);
    vEhalAdc_SwGroupVoltages[1] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup0_Sw_Result[1]);
    vEhalAdc_SwGroupVoltages[2] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup1_Sw_Result[0]);
    vEhalAdc_SwGroupVoltages[3] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup2_Sw_Result[0]);
    vEhalAdc_SwGroupVoltages[4] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup2_Sw_Result[1]);
    vEhalAdc_SwGroupVoltages[5] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup1_Sw_Result[1]);
    vEhalAdc_SwGroupVoltages[6] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup1_Sw_Result[2]);
    vEhalAdc_SwGroupVoltages[7] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup4_Sw_Result[0]);
    vEhalAdc_SwGroupVoltages[8] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup4_Sw_Result[1]);
    vEhalAdc_SwGroupVoltages[9] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup4_Sw_Result[2]);
    vEhalAdc_SwGroupVoltages[10] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup4_Sw_Result[3]);
    vEhalAdc_SwGroupVoltages[11] = EhalAdc_ConvertAdcToVoltage(vEhalAdc_AdcGroup4_Sw_Result[4]);
}

void EhalAdc_Test_10ms(void) {

	EhalAdc_HW_Trigger_Measure_Test();
	EhalAdc_SW_Trigger_Measure_Test();

	switch(vEhalAdc_Test2) {
	case 0:
		vEhalAdc_Test2 = 0;
		break;
	case 1:
		vEhalAdc_Test2 = 0;
		break;
	case 2:
		vEhalAdc_Test2 = 0;
		break;
	case 3:
		vEhalAdc_Test2 = 0;
		break;
	case 4:
		vEhalAdc_Test2 = 0;
		break;
	case 5:
		vEhalAdc_Test2 = 0;
		break;
	default:
		vEhalAdc_Test2 = 0;
		break;
	}
}
//////////////////////////////////// NOT_USED ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////
