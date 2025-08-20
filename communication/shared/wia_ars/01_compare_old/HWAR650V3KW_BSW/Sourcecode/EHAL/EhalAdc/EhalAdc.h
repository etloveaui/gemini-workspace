/*
 * EhalAdc.h
 *
 *  Created on: 2022. 3. 7.
 *      Author: dell
 */

#ifndef BSW_EHAL_EHALADC_EHALADC_H_
#define BSW_EHAL_EHALADC_EHALADC_H_

#include "Platform_Types.h"
#include "Adc.h"
#include "EHAL/EhalGpt12/EhalGpt12.h"

/* FEATURE_DEFINE */

//#define TEMP_MATH			// TEMP_ARRAY or TEMP_MATH

//ADC_DATA_BUFFER
#define NUM_OF_CHANNEL_ADC0_HW		1	//SENS_CURR_U														AdcConf_AdcGroup_AdcGroup0_Hw
#define NUM_OF_CHANNEL_ADC1_HW		1	//SENS_CURR_W														AdcConf_AdcGroup_AdcGroup1_Hw
#define NUM_OF_CHANNEL_ADC2_HW		1	//SENS_HV															AdcConf_AdcGroup_AdcGroup2_Hw
#define NUM_OF_CHANNEL_ADC0_SW		2	//SENS_VDD_15V, SENS_VDD_5V0										AdcConf_AdcGroup_AdcGroup0_Sw
#define NUM_OF_CHANNEL_ADC1_SW		1	//SENS_TEMP1														AdcConf_AdcGroup_AdcGroup1_Sw
#define NUM_OF_CHANNEL_ADC2_SW		2	//SENS_LV,		SENS_IG												AdcConf_AdcGroup_AdcGroup2_Sw
#define NUM_OF_CHANNEL_ADC3_SW		2	//SENS_IPM_TEMP,SENS_PCB_TEMP										AdcConf_AdcGroup_AdcGroup3_Sw
#define NUM_OF_CHANNEL_ADC4_SW		5	//VUC_3V3, 		VCOM_5V0, 	VREF_5V0, 	VT1_5V0, 	VT2_5V0			AdcConf_AdcGroup_AdcGroup4_Sw

#define ADC_RESOLUTION				4095  			// 12-bit resolution max value (2^12 - 1)
#define V_REF						5.0            // Reference voltage (0-5V range)

/* SENSING */
// ADC_SCALE
#define ADC_SCALE						(0.001221001)							// (=Dig/V)

// PHASE_CURRENT
#define CURRENT_ZERO_OFFSET				(2048)									//Remove_after_applying_offset_logic
#define AMP_GAIN						(0.03075)								// V/A
#define CURRENT_GAIN					(ADC_SCALE/AMP_GAIN)					// A/dig

// HVDC_GAIN_DEFINE
#define HVDC_DIV_R1						(12.000)															//MOhm
#define HVDC_DIV_R2						(0.02)																//MOhm
#define HVDC_DIV_R3						(0.0)																//MOhm
#define HVDC_ISOL_IMP					(1000)																//MOhm
#define HVDC_ISOL_AMP_OFFSET			(1.44)																//V
#define HVDC_ISOL_AMP_GAIN				(1.00)
#define HVDC_AMP_R1						(10.00)																//KOhm
#define HVDC_AMP_R2						(10.00)																//KOhm
#define HVDC_AMP_R3						(27.00)																//KOhm
#define HVDC_AMP_R4						(27.00)																//KOhm
#define HVDC_AMP_OFFSET					(0.00)

#define HVDC_DIV_RA						(HVDC_DIV_R3+HVDC_ISOL_IMP)											//MOhm
#define HVDC_DIV_RB						(HVDC_DIV_R2*HVDC_DIV_RA)/(HVDC_DIV_R2+HVDC_DIV_RA)
#define HVDC_DIV_GAIN					(HVDC_DIV_RA*HVDC_DIV_RB-HVDC_DIV_RB*HVDC_DIV_R3)/((HVDC_DIV_R1+HVDC_DIV_RB)*HVDC_DIV_RA)
#define HVDC_T_GAIN						(0.5f*HVDC_ISOL_AMP_GAIN*HVDC_DIV_GAIN)
#define HVDC_A_GAIN						(HVDC_AMP_R3/(HVDC_AMP_R1+HVDC_AMP_R3))
#define HVDC_B_GAIN						(HVDC_AMP_R4/HVDC_AMP_R2)
#define HVDC_OFFSET_ISOL_OP				(HVDC_ISOL_AMP_OFFSET-HVDC_AMP_OFFSET)

#define HVDC_SYSTEM_GAIN_A				( (HVDC_A_GAIN*HVDC_B_GAIN*HVDC_T_GAIN)*(CONS_1+((HVDC_A_GAIN+HVDC_B_GAIN)/(HVDC_A_GAIN*HVDC_B_GAIN))) )
#define T_HVDC_SYSTEM_GAIN_A			(CONS_1/HVDC_SYSTEM_GAIN_A)
#define HVDC_SYSTEM_GAIN_B				( (HVDC_OFFSET_ISOL_OP*(HVDC_A_GAIN*HVDC_B_GAIN+(HVDC_A_GAIN-HVDC_B_GAIN)))+HVDC_AMP_OFFSET )
#define HVDC_VOLTAGE_GAIN				(ADC_SCALE / HVDC_SYSTEM_GAIN_A)			//Rsolution_CHECK : Offset_NO_affect

// SMPS_GAIN_DEFINE
#define SMPS_DIV_R1						(10.0)																//kOhm
#define SMPS_DIV_R2						(3.3)																//kOhm
#define SMPS_DIV_R3						(0.0)																//kOhm
#define SMPS_ISOL_IMP					(1250)																//kOhm
#define SMPS_ISOL_AMP_OFFSET			(1.44)																//V
#define SMPS_ISOL_AMP_GAIN				(0.40)
#define SMPS_AMP_R1						(10.00)																//KOhm
#define SMPS_AMP_R2						(10.00)																//KOhm
#define SMPS_AMP_R3						(23.00)																//KOhm
#define SMPS_AMP_R4						(23.00)																//KOhm
#define SMPS_AMP_OFFSET					(0.00)

#define SMPS_DIV_RA						(SMPS_DIV_R3+SMPS_ISOL_IMP)											//kOhm
#define SMPS_DIV_RB						(SMPS_DIV_R2*SMPS_DIV_RA)/(SMPS_DIV_R2+SMPS_DIV_RA)
#define SMPS_DIV_GAIN					(SMPS_DIV_RA*SMPS_DIV_RB-SMPS_DIV_RB*SMPS_DIV_R3)/((SMPS_DIV_R1+SMPS_DIV_RB)*SMPS_DIV_RA)
#define SMPS_T_GAIN						(0.5f*SMPS_ISOL_AMP_GAIN*SMPS_DIV_GAIN)
#define SMPS_A_GAIN						(SMPS_AMP_R3/(SMPS_AMP_R1+SMPS_AMP_R3))
#define SMPS_B_GAIN						(SMPS_AMP_R4/SMPS_AMP_R2)
#define SMPS_OFFSET_ISOL_OP				(SMPS_ISOL_AMP_OFFSET-SMPS_AMP_OFFSET)

#define SMPS_SYSTEM_GAIN_A				( (SMPS_A_GAIN*SMPS_B_GAIN*SMPS_T_GAIN)*(CONS_1+((SMPS_A_GAIN+SMPS_B_GAIN)/(SMPS_A_GAIN*SMPS_B_GAIN))) )
#define T_SMPS_SYSTEM_GAIN_A			(CONS_1/SMPS_SYSTEM_GAIN_A)
#define SMPS_SYSTEM_GAIN_B				( (SMPS_OFFSET_ISOL_OP *(SMPS_A_GAIN*SMPS_B_GAIN+(SMPS_A_GAIN-SMPS_B_GAIN)))+SMPS_AMP_OFFSET )
#define SMPS_VOLTAGE_GAIN				(ADC_SCALE / SMPS_SYSTEM_GAIN_A)			//Rsolution_CHECK : Offset_NO_affect

// VDD_GAIN_DEFINE
#define VDD_DIV_R1						(0.00001)															//kOhm
#define VDD_DIV_R2						(100000)															//kOhm
#define VDD_DIV_R3						(0.0)																//kOhm
#define VDD_ISOL_IMP					(1250)																//kOhm
#define VDD_ISOL_AMP_OFFSET				(1.44)																//V
#define VDD_ISOL_AMP_GAIN				(0.40)
#define VDD_AMP_R1						(10.00)																//KOhm
#define VDD_AMP_R2						(10.00)																//KOhm
#define VDD_AMP_R3						(19.00)																//KOhm
#define VDD_AMP_R4						(19.00)																//KOhm
#define VDD_AMP_OFFSET					(0.00)

#define VDD_DIV_RA						(VDD_DIV_R3+VDD_ISOL_IMP)											//kOhm
#define VDD_DIV_RB						(VDD_DIV_R2*VDD_DIV_RA)/(VDD_DIV_R2+VDD_DIV_RA)
#define VDD_DIV_GAIN					(VDD_DIV_RA*VDD_DIV_RB-VDD_DIV_RB*VDD_DIV_R3)/((VDD_DIV_R1+VDD_DIV_RB)*VDD_DIV_RA)
#define VDD_T_GAIN						(0.5f*VDD_ISOL_AMP_GAIN*VDD_DIV_GAIN)
#define VDD_A_GAIN						(VDD_AMP_R3/(VDD_AMP_R1+VDD_AMP_R3))
#define VDD_B_GAIN						(VDD_AMP_R4/VDD_AMP_R2)
#define VDD_OFFSET_ISOL_OP				(VDD_ISOL_AMP_OFFSET-VDD_AMP_OFFSET)

#define VDD_SYSTEM_GAIN_A				( (VDD_A_GAIN*VDD_B_GAIN*VDD_T_GAIN)*(CONS_1+((VDD_A_GAIN+VDD_B_GAIN)/(VDD_A_GAIN*VDD_B_GAIN))) )
#define T_VDD_SYSTEM_GAIN_A				(CONS_1/VDD_SYSTEM_GAIN_A)
#define VDD_SYSTEM_GAIN_B				( (VDD_OFFSET_ISOL_OP *(VDD_A_GAIN*VDD_B_GAIN+(VDD_A_GAIN-VDD_B_GAIN)))+VDD_AMP_OFFSET )
#define VDD_VOLTAGE_GAIN				(ADC_SCALE / VDD_SYSTEM_GAIN_A)			//Rsolution_CHECK : Offset_NO_affect

// LVDC_GAIN_DEFINE
#define LVDC_DIVIDE_R1					(1000000.0)								//1MOhm
#define LVDC_DIVIDE_R2					(230000.0)								//230kOhm
#define LVDC_DIVIDE_GAIN				(LVDC_DIVIDE_R2 / (LVDC_DIVIDE_R1 + LVDC_DIVIDE_R2))
#define LVDC_VOLTAGE_GAIN				(ADC_SCALE / LVDC_DIVIDE_GAIN)

//IG_GAIN_DEFINE
#define IGDC_DIODE_DROP					(0.15)									//DIODE_SPEC
#define IGDC_DIVIDE_R1					(10000.0)								//10kOhm
#define IGDC_DIVIDE_TLF_R1				(10000.0)								//10kOhm
#define IGDC_DIVIDE_TLF_R2				(31000.0)								//31kOhm
#define IGDC_DIVIDE_ADC_R1				(47000.0)								//47kOhm
#define IGDC_DIVIDE_ADC_R2				(18000.0)								//18kOhm
#define IGDC_DIVIDE_TLF_RT				(IGDC_DIVIDE_TLF_R1 + IGDC_DIVIDE_TLF_R2)
#define IGDC_DIVIDE_ADC_RT				(IGDC_DIVIDE_ADC_R1 + IGDC_DIVIDE_ADC_R2)
#define IGDC_DIVIDE_EQR_TOTAL			(IGDC_DIVIDE_R1 + (IGDC_DIVIDE_TLF_RT * IGDC_DIVIDE_ADC_RT) / (IGDC_DIVIDE_TLF_RT + IGDC_DIVIDE_ADC_RT))
#define IGDC_DIVIDE_GAIN				((CONS_1 - (IGDC_DIVIDE_R1/IGDC_DIVIDE_EQR_TOTAL))*IGDC_DIVIDE_ADC_R2/IGDC_DIVIDE_ADC_RT)
#define IGDC_VOLTAGE_GAIN				(ADC_SCALE / IGDC_DIVIDE_GAIN)

// PCB_Temperature
#define PCB_TEMP_NTC_MAX_VOLTAGE		(4.5)			//V
#define PCB_TEMP_DIV_R					(10000.0)		//Ohm

// MOTOR_Temperature
#define MOTOR_TEMP_NTC_MAX_VOLTAGE		(4.5)			//V
#define MOTOR_TEMP_PULLUP_R				(0.47)			//kOhm
#define MOTOR_TEMP_PULLDOWN_R			(4.7)			//kOhm

// IGBT_Temperature
#define IGBT_TEMP_NTC_MAX_VOLTAGE		(4.572)								//V
#define IGBT_TEMP_NTC_MIN_VOLTAGE		(0.315)								//V
#define IGBT_TEMP_PULLUP_R				(10000.0)							//Ohm
#define IGBT_DIV_R1						(0.00001)							//kOhm
#define IGBT_DIV_R2						(100000)							//kOhm
#define IGBT_DIV_R3						(0.0)								//kOhm
#define IGBT_ISOL_IMP					(1250)								//kOhm
#define IGBT_ISOL_AMP_OFFSET			(1.44)								//V
#define IGBT_ISOL_AMP_GAIN				(0.40)
#define IGBT_AMP_R1						(10.00)								//KOhm
#define IGBT_AMP_R2						(10.00)								//KOhm
#define IGBT_AMP_R3						(23.00)								//KOhm
#define IGBT_AMP_R4						(23.00)								//KOhm
#define IGBT_AMP_OFFSET					(0.00)

#define IGBT_DIV_RA						(IGBT_DIV_R3+IGBT_ISOL_IMP)
#define IGBT_DIV_RB						(IGBT_DIV_R2*IGBT_DIV_RA)/(IGBT_DIV_R2+IGBT_DIV_RA)
#define IGBT_DIV_GAIN					(IGBT_DIV_RA*IGBT_DIV_RB-IGBT_DIV_RB*IGBT_DIV_R3)/((IGBT_DIV_R1+IGBT_DIV_RB)*IGBT_DIV_RA)
#define IGBT_T_GAIN						(0.5f*IGBT_ISOL_AMP_GAIN*IGBT_DIV_GAIN)
#define IGBT_A_GAIN						(IGBT_AMP_R3/(IGBT_AMP_R1+IGBT_AMP_R3))
#define IGBT_B_GAIN						(IGBT_AMP_R4/IGBT_AMP_R2)
#define IGBT_OFFSET_ISOL_OP				(IGBT_ISOL_AMP_OFFSET-IGBT_AMP_OFFSET)

#define IGBT_SYSTEM_GAIN_A				( (IGBT_A_GAIN*IGBT_B_GAIN*IGBT_T_GAIN)*(CONS_1+((IGBT_A_GAIN+IGBT_B_GAIN)/(IGBT_A_GAIN*IGBT_B_GAIN))) )
#define IGBT_SYSTEM_GAIN_B				( (IGBT_OFFSET_ISOL_OP *(IGBT_A_GAIN*IGBT_B_GAIN+(IGBT_A_GAIN-IGBT_B_GAIN)))+IGBT_AMP_OFFSET )
#define IGBT_VOLTAGE_GAIN				(ADC_SCALE / IGBT_SYSTEM_GAIN_A)			//Rsolution_CHECK : Offset_NO_affect
/* SENSOR_FAIL_PROTECTION */
// Phase_Current_OFFSET
#define CURRENT_SENSOR_LOW				(409.5)								//0.5V
#define CURRENT_SENSOR_HIGH				(3685.5)							//4.5V
#define CURRENT_OFFSET_ERR_MIN			(2014)								//TO_BE_UPDATED
#define CURRENT_OFFSET_ERR_MAX			(2080)								//TO_BE_UPDATED
#define MEAS_CALIB_PERIOD				(1.0/T_CC)
#define MEAS_OFFSET_CHECK_PERIOD		(5)

//LPF_CUTOFF_FREQUENCY
#define HVDC_CUTOFF						(500.0)						//Hz, PWM_FREQUENCY
#define LVDC_CUTOFF						(50.0)						//Hz, 100HZ
#define IOFFSET_CUTOFF					(100.0)						//Hz, PWM_FREQUENCY
#define TEMPERATURE_CUTOFF				(9.0)						//Hz, 10Hz

/*Function declaration for Notification Function of AdcGroup0_Hw*/
extern void AdcGroup0_Hw_Notification(void);
/*Function declaration for Notification Function of AdcGroup0_Sw*/
extern void AdcGroup0_Sw_Notification(void);
/*Function declaration for Notification Function of AdcGroup1_Hw*/
extern void AdcGroup1_Hw_Notification(void);
/*Function declaration for Notification Function of AdcGroup1_Sw*/
extern void AdcGroup1_Sw_Notification(void);
/*Function declaration for Notification Function of AdcGroup2_Hw*/
extern void AdcGroup2_Hw_Notification(void);
/*Function declaration for Notification Function of AdcGroup2_Sw*/
extern void AdcGroup2_Sw_Notification(void);
/*Function declaration for Notification Function of AdcGroup3_Sw*/
extern void AdcGroup3_Sw_Notification(void);
/*Function declaration for Notification Function of AdcGroup4_Sw*/
extern void AdcGroup4_Sw_Notification(void);

typedef struct
{
	float    raw;   /*! raw value */
    float    filt;  /*! filtered value */
}meas_t;

typedef struct
{
	uint32	AdcGroup0_Hw;
	uint32	AdcGroup1_Hw;
	uint32	AdcGroup2_Hw;
	uint32	AdcGroup0_Sw;
	uint32	AdcGroup1_Sw;
	uint32	AdcGroup2_Sw;
	uint32	AdcGroup3_Sw;
	uint32	AdcGroup4_Sw;
} typEhalAdc_NotificationCount;

typedef struct
{
	Std_ReturnType	AdcGroup0_Hw;
	Std_ReturnType	AdcGroup1_Hw;
	Std_ReturnType	AdcGroup2_Hw;
	Std_ReturnType	AdcGroup0_Sw;
	Std_ReturnType	AdcGroup1_Sw;
	Std_ReturnType	AdcGroup2_Sw;
	Std_ReturnType	AdcGroup3_Sw;
	Std_ReturnType	AdcGroup4_Sw;
} typEhalAdc_BufferStatus;

typedef struct
{
	Adc_StatusType	AdcGroup0_Hw;
	Adc_StatusType	AdcGroup1_Hw;
	Adc_StatusType	AdcGroup2_Hw;
	Adc_StatusType	AdcGroup0_Sw;
	Adc_StatusType	AdcGroup1_Sw;
	Adc_StatusType	AdcGroup2_Sw;
	Adc_StatusType	AdcGroup3_Sw;
	Adc_StatusType	AdcGroup4_Sw;
} typEhalAdc_Status;

typedef struct
{
	sint16 	f16X1;
	sint16 	f16Kx;
	sint32 	f32Integ;
} LPF_t;

typedef struct
{
	//bsw
	float 	HVdcFdbLpfFct;
	float 	IphAdcOfstLpfFct;
	float	LVdcFdbLpfFct;
	float 	TemperatureLpfFct;

	//asw
//	float 	VphSetLpfFct;
//	float 	EncWeLpfFct;
//	float 	SpeedLpfFct;
} lpf_gain_t;

typedef struct
{
	float		PTC_Temperature;	// METAL_PTC_TEMP
	meas_t		tFPhA;				// phase A current_raw
	meas_t		tFPhB;				// phase B current_raw
	meas_t		tFPhC;				// phase C current_raw

	meas_t		tFPhU;				// phase U Current (After_Offset)
	meas_t		tFPhV;				// phase V Current (After_Offset)
	meas_t		tFPhW;				// phase W Current (After_Offset)

	meas_t		tFIdcb;				// DC offset measured on DC bus current
	meas_t		tFHVdcb;			// DC offset measured on DC bus voltage
	meas_t		tFSmps;				// SMPS_Voltage_masurement
	meas_t		tFVdd;				// Vdd_Voltage_masurement

	meas_t		tFLVdcb;			// Low_Voltage_masurement
	meas_t		tFIGdcb;			// IG_Voltage_masurement
	meas_t		tFVmcudcb;
	meas_t		tFVcomdcb;
	meas_t		tFVtr1dcb;
	meas_t		tFVtr2dcb;
	meas_t		tFVrefdcb;

	meas_t		tFPcbTemp;
	meas_t		tFMotorTemp;
	meas_t		tFIgbtTemp;

	LPF_t		Offset_LPF_A;
	LPF_t		Offset_LPF_B;
	LPF_t		Offset_LPF_C;
	LPF_t		Offset_TEMP_LPF;
}measResult_t;

typedef struct
{
	float    				    tFOffset;   /*! raw value */
    float						tF_raw;
}offsetBasic_t;

typedef struct
{
    offsetBasic_t    	tFPhA;         	// DC offset measured on phase A current
    offsetBasic_t    	tFPhB;			// DC offset measured on phase B current
    offsetBasic_t    	tFPhC;			// DC offset measured on phase C current
    offsetBasic_t    	tFHVdcb;		// DC offset measured on DC bus voltage
}offset_t;

typedef struct
{
	uint16     u16CalibSamples; // Number of samples taken for calibration
}calibParam_t;

typedef union
{
	uint16 R;
    struct {
    	uint16							:14;// RESERVED
        uint16 current_calibDone		:1; // DC offset calibration done
        uint16 current_calibInitDone	:1; // initial setup for DC offset calibration done
        uint16 angle_calibDone			:1;
    } B;
}calibFlags_t;

//typedef struct
//{
//	char				Z_Pulse;
//    char				Z_Pulse_Old;
//    char				Z_Pulse_Set;
//    char				EncDirection;
//    char				SpeedMeas_Start_F;
//    long int			EncValue;
//    long int			EncValue_Old;
//    long int			Diff_Pulse;
//    float				Ftheta;
//    float				Ftheta_Old;
//    float				pulseSum;
//    float				Diff_Ftheta;
//    float				Diff_Ftheta_Old;
//    float				ThetaFdbComp;
//    float				EncWe;
//    float				EncWeFil;
//    float				EncSpeed;
//    uint16				Pulse_Start_Cnt;
//}w_meas_t;

typedef struct
{
	char 				Current_Sensor_Error_F;
	char 				PTC_Sensor_Error_F;
    measResult_t  		measured;
//	w_meas_t			Encoder;			// Encoder
    offset_t     		offset;
    calibParam_t      	param;
    calibFlags_t      	flag;
    lpf_gain_t			lpf_gain;
    uint16 				calibCntr;
	uint16				offset_check_Cnt;
	float				HVDC_Calibration_Value;
}measModule_t;

/******************************************************************************
| Exported Variables
-----------------------------------------------------------------------------*/
extern   measModule_t		meas;
/******************************************************************************
| Exported function prototypes
-----------------------------------------------------------------------------*/
extern void EhalAdc_Init(void);
extern void EhalAdc_Task_10ms_3(void);
extern void EhalAdc_Task_10ms_5(void);
extern void EhalAdc_Task_10ms_7(void);
extern void EhalAdc_Task_100ms(void);
extern char Meas_Clear(measModule_t *ptr);
extern char Meas_CalibCurrentSense(measModule_t *ptr);
extern char Meas_Get3PhCurrent(measModule_t *ptr);
extern char Meas_GetHVdcVoltage(measModule_t *ptr);
extern char Meas_GetSmpsVoltage(measModule_t *ptr);
extern char Meas_GetVddVoltage(measModule_t *ptr);
extern char Meas_GetLVVoltage(measModule_t *ptr);
extern char Meas_GetIGVoltage(measModule_t *ptr);
extern char Meas_GetVmcu_ref_com_tr1_tr2Voltage(measModule_t *ptr);
extern void EhalAdc_LogicInit(void);
extern void EhalAdc_LPF_Init(void);
#endif /* BSW_EHAL_EHALADC_EHALADC_H_ */
