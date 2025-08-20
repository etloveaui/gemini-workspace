/*
 * VectorTest.h
 *
 *  Created on: 2024. 12. 19.
 *      Author: jaegalrang
 */

#ifndef CDRV_CDRVIFC_VECTORTEST_H_
#define CDRV_CDRVIFC_VECTORTEST_H_

#include "Platform_Types.h"
//FEATURE
#define TEST_VECTORCONTROL_ON
//#define TEST_CAN_ON

#define	HVEOP_MOTOR						(1)
#define	ARS_MOTOR						(2)
#define	TAGET_MOTOR						ARS_MOTOR

#define	NO_1_MOTOR						(1)			//PPR_1024_INIT_POSITION_106.436_FOR_DYNAMO_CHA
#define	NO_2_MOTOR						(2)			//PPR_2048_INIT_POSITION_117.598_FOR_GEAR_CHA
#define	NO_4_MOTOR						(4)			//PPR_1024_INIT_POSITION_126.299_FOR_GEAR_CHA_REMOVE
#define	NO_5_MOTOR						(5)			//PPR_2048_INIT_POSITION_123.311_FOR_GEAR_CHA_REMOVE
#define	MOTOR_SAMPLE_NO					NO_2_MOTOR

#define	VOLTAGE_VECTOR_TEST				(1)
#define	CURRENT_VECTOR_TEST				(2)
#define	ENCODER_VECTOR_TEST				(3)
#define	TAGET_CONTROL					ENCODER_VECTOR_TEST

#define MT_2PAI 						(6.28316538f)
#define MT_1_OVR_SQ3 					(0.57735027f)
#define MT_SQ3_OVR_2					(0.8660254046f)

/* MOTOR_PARAMETER */
#if(TAGET_MOTOR == HVEOP_MOTOR)
#define MOTOR_PP						(5.0)
#define MOTOR_RS						(0.250)			//ECOMP-800V
#define MOTOR_LD						(0.000166)		//CC_ANTI_CHECK_OVER_SPEED
#define MOTOR_LQ						(0.000252)		//CC_ANTI_CHECK_OVER_SPEED
#define MOTOR_KE						(0.054289074)
#define MOTOR_KT						(POWER_CONSTANT * MOTOR_PP * MOTOR_KE)
#define MOTOR_J							(0.0000675)				//kg-m2
#elif(TAGET_MOTOR == ARS_MOTOR)
#define MOTOR_PP						(5.0)
#define MOTOR_RS						(2.8835)
#define MOTOR_LD						(0.003615)				//0.003615
#define MOTOR_LQ						(0.003615)
#define MOTOR_KE						(0.054289)
#define MOTOR_KT						(POWER_CONSTANT * MOTOR_PP * MOTOR_KE)
#define MOTOR_J							(0.00001)				//kg-m2
#endif

#define RPM2WE							(1.0/60.0*MT_2PAI*MOTOR_PP)
#define MT_DEGREE 						(360.0f)
#define TR_DEG2RAD						(1.0/MT_DEGREE*MT_2PAI)
#define WE2RPM							(1.0/RPM2WE)
#define POWER_CONSTANT					(1.5)
#define TIME_COMP_CONSTANT				(1.5)

/* FEATURE_DEFINE */
#define MOTOR_DIR_CCW					//MOTOR_DIR_CCW or MOTOR_DIR_CW

#if(TAGET_MOTOR == HVEOP_MOTOR)
#define A1333_MIN_DUTY					(5.0)
#define A1333_MAX_DUTY					(95.0)
#define ENCODER_DIR_CCW					(0)
#define ENCODER_DIR_CW					(1)
#define ENCPULSE						(1024)
#define ENCODER_MAX_VALUE				(65535)
#define ENCMULTIPLIER					(4)
#define ENCZPOSITION_RATIO				(0.002777778)
#define ENCPULSEPERPOLE					(ENCPULSE * ENCMULTIPLIER / MOTOR_PP)
#define ENCTHETA_SCALE					(MT_2PAI * MOTOR_PP / (ENCPULSE * ENCMULTIPLIER))
#define ENCZPULSE_ANGLE					(150.0)

//#ifdef	MOTOR_DIR_CCW
//#define ENCZPULSE_ANGLE					(150.0)		//150.0
//#elif defined MOTOR_DIR_CW
//#define ENCZPULSE_ANGLE					(330.0)
//#endif

#elif(TAGET_MOTOR == ARS_MOTOR)
#define A1333_MIN_DUTY					(5.0)									//AAS33001
#define A1333_MAX_DUTY					(95.0)									//AAS33001
#define ENCODER_DIR_CCW					(0)
#define ENCODER_DIR_CW					(1)

#if(MOTOR_SAMPLE_NO == NO_1_MOTOR)
#define ENCPULSE						(1024)
#elif(MOTOR_SAMPLE_NO == NO_2_MOTOR)
#define ENCPULSE						(1024)
#elif(MOTOR_SAMPLE_NO == NO_4_MOTOR)
#define ENCPULSE						(1024)
#elif(MOTOR_SAMPLE_NO == NO_5_MOTOR)
#define ENCPULSE						(2048)
#endif

#define ENCODER_MAX_VALUE				(65535)									//AAS33001
#define ENCMULTIPLIER					(4)										//AAS33001
#define ENCZPOSITION_RATIO				(0.002777778)							//AAS33001
#define ENCPULSEPERPOLE					(ENCPULSE * ENCMULTIPLIER / MOTOR_PP)	//AAS33001
#define ENCTHETA_SCALE					(MT_2PAI * MOTOR_PP / (ENCPULSE * ENCMULTIPLIER))
#if(MOTOR_SAMPLE_NO == NO_1_MOTOR)
#define ENCZPULSE_ANGLE					(106.436)
#elif(MOTOR_SAMPLE_NO == NO_2_MOTOR)
#define ENCZPULSE_ANGLE					(117.598)
#elif(MOTOR_SAMPLE_NO == NO_4_MOTOR)
#define ENCZPULSE_ANGLE					(126.299)
#elif(MOTOR_SAMPLE_NO == NO_5_MOTOR)
#define ENCZPULSE_ANGLE					(123.311)
#endif
#endif

#define SPEED_REF_MAX					(7000.0)
#define SPEED_REF_MIN					(-7000.0)

/* GAIN */
// CC
#define CLOOP_LIMIT                     (0.90)				//16KHz & Dead_2us
#define CC_ZETA                     	(1.0)
#define CC_F_CUT                     	(600.0)				//7000rpm
// SC
#define SPEED_LOOP_CNTR                 (5)
#define SC_MAX_SPEED					(7000.0)
#define SC_WCC							(SC_MAX_SPEED * RPM2WE)
#define SC_WSC_GAIN						(10.0)
#define SC_WPI_GAIN                     (10.0)

#define VPHSET_CUTOFF					(5.0)						//Hz, PWM_FREQUENCY
#define ENCWE_CUTOFF					(500.0)						//Hz, PWM_FREQUENCY
#define SPD_CUTOFF						(100.0)						//Hz, PWM_FREQUENCY

//CURRENT
#define	OCP_PERIOD						(3)
#define I_PH_OVER                       (13.0)							//ARS

/* CL_PARAMETER */
#define CL_CURRENT_LIMIT				(I_PH_OVER - 3.0)

typedef union
{
    uint16 R;
    struct
    {
    	uint16 OverPhaseCCurrent    : 1;   /* OverCurrent fault flag */				//1
    	uint16 OverPhaseBCurrent    : 1;   /* OverCurrent fault flag */				//2
    	uint16 OverPhaseACurrent    : 1;   /* OverCurrent fault flag */				//3
    	uint16						: 13;  /* RESERVED */
    }B;
}motorFaultStatus_t;

typedef struct
{
	motorFaultStatus_t 		motor;
}appFaultStatus_t;    /* Application fault status user type*/

typedef struct
{
	float			tFArg1;
	float			tFArg2;
	float			tFArg3;
} SWLIBS_3Syst_tFloat;

typedef struct
{
	float			tFArg1;
	float			tFArg2;
} SWLIBS_2Syst_tFloat;

// PI + FF + AW
typedef struct
{
	float			tFKp;
	float			tFKiT;
	float			tFKcT;
	float			tFVff;
	float			tFVref;
	float			tFInteg;
	float			tFUpperLimit;
	float			tFLowerLimit;
} CtrlPIA_t;

typedef struct
{
	float			tFKp;
	float			tFKiT;
	float			tFKcT;
	float			tFInteg;
	float			tFUpperLimit;
	float			tFLowerLimit;
} CtrlPIAS_t;

typedef struct
{
	float			tFSlopeInc;
	float			tFSlopeDec;
	float			tFInteg;
	uint16 			FilterEnable;
	float 			tFKx;
	float 			tFIntegFlt;
} RAMP_FILTER_T;

typedef struct
{
	sint16			f16Arg1;
	sint16			f16Arg2;
	sint16			f16Arg3;
} SWLIBS_3Syst_F16;

typedef struct
{
	uint16			tU16Arg1;
	uint16			tU16Arg2;
	uint16			tU16Arg3;
} SWLIBS_3Syst_tU16;

typedef struct
{
	float					thRotEl;		// El. position entering to the control loop
	float					wRotEl;			// El. speed entering to the control loop
	float					wRotElFilt;		// Filtered El. speed entering to the control loop
	float					wRotElReq;		// Required el. speed
	float					wRotElReqRamp;	// Required el. speed converted to the ramp shape
	float					wRotElErr;		// Error of the el. speed entering to speed controller
	sint16					speedLoopCntr;	// rate between speed and current loop
} pospeControl_t;

typedef struct
{
	char				Z_Pulse;
    char				Z_Pulse_Old;
    char				Z_Pulse_Set;
    char				EncDirection;
    char				SpeedMeas_Start_F;
    long int			EncValue;
    long int			EncValue_Old;
    long int			Diff_Pulse;
    float				Ftheta;
    float				Ftheta_Old;
    float				pulseSum;
    float				Diff_Ftheta;
    float				Diff_Ftheta_Old;
    float				ThetaFdbComp;
    float				EncWe;
    float				EncWeFil;
    float				EncSpeed;
    uint16				Pulse_Start_Cnt;
}w_meas_t;


typedef struct
{
	//asw
	float 	VphSetLpfFct;
	float 	EncWeLpfFct;
	float 	SpeedLpfFct;
} lpf_gain_t;

typedef struct{
	char							LOW_Temp_Operating_F;
	char							Idc_Est_F;
	char 							Restart_F;
	char							TLF35584_Err_F;

	sint16 							can_spd_cmd;
	uint16							Align_Sector;
	uint16        		            alignVoltage;	// Alignment voltage
	uint16		                    svmSector;      // Space Vector Modulation sector
	float							Init_Position_Deg_E;
	float							Vph_Max;
	float							Vpl_Max;
	float							Vph_Set;
	float							Vqe_Limit;

	float							Idc_Est;
	float							wRotEl_Fil;
	float							Vph_Set_Fil;

	//PERIOD,CNT
	uint16 							FaultClear_Period;
	uint16 							Restart_Cnt;
	uint16 							FaultClear_Cnt;
	uint16							Metal_Temp_CNT;
	float							ThetaCurTimeComp;
	float							ThetaVoltTimeComp;

	SWLIBS_2Syst_tFloat				iDQReq;         // dq - axis required currents, given by speed PI
	SWLIBS_2Syst_tFloat				iDQFbck;        // dq - axis current feedback
	SWLIBS_2Syst_tFloat				iAlBeFbck;      // Alpha/Beta - axis current feedback
	SWLIBS_3Syst_tFloat				iAbcFbck;       // Three phases current feedback

	SWLIBS_2Syst_tFloat             iDQErr;         // Error between the reference and feedback signal
	CtrlPIA_t						CtrlPIAD;        // Predefined structure related to d-axis current PI controller
	CtrlPIA_t						CtrlPIAQ;        // Predefined structure related to q-axis current PI controller

    SWLIBS_2Syst_tFloat				uDQReq;         // dq - axis required voltages given by current PIs
    SWLIBS_2Syst_tFloat             uAlBeReq;       // Alpha/Beta required voltages
    SWLIBS_3Syst_tFloat				uAbcReq;        // Three phases required voltages
    SWLIBS_3Syst_tFloat				uNAbcReq;       // Three phases required voltages
    SWLIBS_2Syst_tFloat				thClarkTransform;// Transformation angle - enters to Park transformation
    SWLIBS_2Syst_tFloat				thParkTransform;// Transformation angle - enters to Park transformation

    SWLIBS_3Syst_F16                pwm16;          // Three phase 16bit Duty-Cycles estimated from uAlBeReqDCB
    SWLIBS_3Syst_tU16				pwmcompare;
    float							iCLoop_Limit;	// Current loop limit

    CtrlPIAS_t						CtrlPIA_S;        // Predefined structure related to Speed PI controller
    RAMP_FILTER_T					speedRamp;      // Reference speed ramp generation + LPF

    pospeControl_t                  pospeControl;   // Position/Speed variables needed for control

    w_meas_t			Encoder;			// Encoder
    lpf_gain_t			lpf_gain;
    uint16 angle_calibDone			;
}pmsmDrive_t;

typedef struct
{
	float    raw;   /*! raw value */
    float    filt;  /*! filtered value */
}meas_t;

typedef struct
{
	sint16 	f16X1;
	sint16 	f16Kx;
	sint32 	f32Integ;
} LPF_t;

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

//Debug
typedef struct{
	char							tbF_A;
	char							tbF_B;
	char							tbF_C;
	char							tbF_D;
	char							tbF_E;

	sint16 							tsA;
	sint16 							tsB;
	sint16 							tsC;
	sint16 							tsD;
	sint16 							tsE;
	sint16 							tsF;
	sint16 							tsG;
	sint16 							tsH;
	sint16 							tsI;
	sint16 							tsJ;

	uint16 							tuA;
	uint16 							tuB;
	uint16 							tuC;
	uint16 							tuD;
	uint16 							tuE;
	uint16 							tuF;
	uint16 							tuG;
	uint16 							tuH;
	uint16 							tuI;
	uint16 							tuJ;

	float 							tfA;
	float 							tfB;
	float 							tfC;
	float 							tfD;
	float 							tfE;
	float 							tfF;
	float 							tfG;
	float 							tfH;
	float 							tfI;
	float 							tfJ;
}Debug_t;



typedef union{
	uint8 byte[8];
	struct __packed__ {
		sint16 wRotElFilt;
		uint16 AdcValue_HVDC;
		sint16 AdcValue_Tigbt;
		uint16 unused1;
	}signal;
}typBswCanMsg_RMT_RES;

typedef union{
	uint8 byte[32];
	struct __packed__ {
		uint16 TEST_EN			: 1;
		uint16 Pwm_Enable_F 	: 1;
		uint16 unused4			: 14;
		sint16 can_spd_cmd;
		uint16 JJM_CNT_tfA;
		uint16 FrequencyValue ;
		uint16 DeadTimeValue  ;
		uint16 unused3;
		uint16 unused2;
		uint16 unused1;
	}signal;
}typBswCanMsg_RMT_CMD;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	typBswCanMsg_RMT_CMD Msg;
}typBswCanMsg_RMT_CMD_FRAME;

typedef uint32 Icu_17_TimerIp_ValueType;

typedef struct
{
  /* To store ActiveTime for GetDutyCycles API.*/
  Icu_17_TimerIp_ValueType  ActiveTime;
  /* To store PeriodTime for GetDutyCycles API.*/
  Icu_17_TimerIp_ValueType  PeriodTime;
} Icu_17_TimerIp_DutyCycleType;

typedef enum
{
  /* No activation edge has been detected since the last call of
  Icu_17_TimerIp_GetInputState() or Icu_17_TimerIp_Init().*/
  ICU_17_TIMERIP_IDLE = 0U,
  /* An activation edge has been detected by an ICU*/
  ICU_17_TIMERIP_ACTIVE = 1U
} Icu_17_TimerIp_InputStateType;

typedef struct{
//	uint32 test_case;
//	Icu_17_TimerIp_ChannelType ch_num;
	Icu_17_TimerIp_DutyCycleType ticks;
	Icu_17_TimerIp_DutyCycleType time;
	Icu_17_TimerIp_InputStateType status;
	uint32 frequency_001hz;
	uint16 duty_001per;
//	Icu_17_TimerIp_EdgeNotificationType
//	Icu_17_TimerIp_DutyCycleType
//	Pwm_17_GtmCcu6_OutputStateType output_state;
//	Pwm_17_GtmCcu6_EdgeNotificationType edge_type;
	uint32 noti_count;
}typEhalIcu_IcuMonitor;

extern	pmsmDrive_t			drvFOC;        		// Field Oriented Control Variables
extern	Debug_t				JJM_CNT;			//Debug

extern typBswCanMsg_RMT_CMD_FRAME vCanMsg_RMT_CMD_FRAME;
extern typBswCanMsg_RMT_RES vCanMsg_RMT_RES;

#define CAN_MSG_RX_INDEX_RMT_CMD		(2U)
#define CAN_MSG_TX_INDEX_RMT_RES		(3U)

extern void Voltage_Vector(void);
extern void Simply_MotorContorl(void);
extern void VectorTest_Task_10ms(void);
#endif /* CDRV_CDRVIFC_VECTORTEST_H_ */
