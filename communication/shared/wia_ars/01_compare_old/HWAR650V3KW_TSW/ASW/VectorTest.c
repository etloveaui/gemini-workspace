/*
 * VectorTest.c
 *
 *  Created on: 2024. 12. 19.
 *      Author: jaegalrang
 */

#include "VectorTest.h"
#include "math.h"
#include "BswPwm.h"
#include "Global_Config.h"
#include "BswTest.h"
#include "BswCan.h"
#include "BswTest.h"

appFaultStatus_t		permFaults;			// Permanent faults to be indicated inhere
pmsmDrive_t				drvFOC;        		// Field Oriented Control Variables
Debug_t					JJM_CNT;			// Debug

typBswCanMsg_RMT_CMD vBswTest_CanMsg_RMT_CMD;
uint8 vBswTest_CanMsg_RMT_CMD_RxNew;
uint8 vBswTest_CanMsg_RMT_CMD_Dlc;

typBswCanMsg_RMT_RES vBswCanMsg_RMT_RES;

#define DAC8803              (0)
#define TLV5614              (1)

extern uint8 vEhalDac_DacModule;
extern uint16 vEhalPwm_HalfDutyTickValue;
extern float vEhalPwm_SamplingTime;
extern uint16 vEhalPwm_FrequencyValue;
extern uint16 vEhalPwm_MaxDutyTickValue;
extern measModule_t		meas;				// Measure Module
extern typEhalIcu_IcuMonitor vEhalIcu_IcuMonitor[5];

extern void EhalGpt12_InitEncoder(uint8 CLRT3EN);

///////////////////////////////////////////////////////////////////////////////////////////////////////////
float DoRampRef_LPF(float tFTarget, RAMP_FILTER_T *xpRamp)
{
	float tFTempInc;
	float tFTempDec;
	float tFTempState;
	float tFResult;

	if (xpRamp->tFInteg != tFTarget)
	{
		tFTempInc = (xpRamp->tFInteg + xpRamp->tFSlopeInc);
		tFTempDec = (xpRamp->tFInteg - xpRamp->tFSlopeDec);
		tFTempState = (xpRamp->tFInteg <= tFTarget)? tFTempInc : tFTempDec;
		xpRamp->tFInteg = (((tFTempState >= tFTarget) && (xpRamp->tFInteg <= tFTarget)) || ((tFTempState <= tFTarget) && (xpRamp->tFInteg > tFTarget))) ? tFTarget : tFTempState;
	}
	if (xpRamp->FilterEnable == 0)
	{
		xpRamp->tFIntegFlt = xpRamp->tFInteg;
		tFResult = xpRamp->tFInteg;
	}
	else
	{
		tFTempState = (xpRamp->tFKx * (xpRamp->tFInteg - xpRamp->tFIntegFlt));
		xpRamp->tFIntegFlt = (xpRamp->tFIntegFlt + tFTempState);
		tFResult = xpRamp->tFIntegFlt;
	}
	return (tFResult);
}

float DoCtrlPIAS(CtrlPIAS_t *xpParamPI, float tFErr)
{
	float tFRef;
	float tFOut;
	float tFInteg;

	tFInteg = (xpParamPI->tFInteg + (tFErr * xpParamPI->tFKiT));
	tFInteg = LIMIT(tFInteg, xpParamPI->tFUpperLimit, xpParamPI->tFLowerLimit);

	tFRef = tFInteg;
	tFRef = (tFRef + (tFErr * xpParamPI->tFKp));
	tFOut = LIMIT(tFRef, xpParamPI->tFUpperLimit, xpParamPI->tFLowerLimit);

	xpParamPI->tFInteg = (tFInteg - ((tFRef - tFOut) * xpParamPI->tFKcT));

	return tFOut;
}

float DoCtrlPIA(CtrlPIA_t *xpParamPI, float xf16Err)
{
	float tFRef;
	float tFOut;
	float tFInteg;

	// tqdInteg = xpParamPI->qdInteg + xqErr * xpParamPI->qKiT
	tFInteg = (xpParamPI->tFInteg + (xf16Err * xpParamPI->tFKiT));

	// tqRef = xpParamPI->qVff + (tFrac16)tqdInteg + (xqErr * xpParamPI->qKp) >> SCALE_PIA1_KP
	tFRef = tFInteg;
	tFRef = (tFRef + (xf16Err * xpParamPI->tFKp));
	tFRef = (tFRef + xpParamPI->tFVff);
	tFOut = LIMIT(tFRef, xpParamPI->tFUpperLimit, xpParamPI->tFLowerLimit);
	xpParamPI->tFVref = tFRef;
	xpParamPI->tFInteg = (tFInteg - ((tFRef - tFOut) * xpParamPI->tFKcT));

	return tFOut;
}

uint8 fault_Log = 0;
static char faultDetection()
{
	char faultDetectiontEvent;

    faultDetectiontEvent = FALSE;

	// Fault:   Phase A over-current detected
	permFaults.motor.B.OverPhaseACurrent   = (fabs(drvFOC.iAbcFbck.tFArg1) > I_PH_OVER) ? TRUE : FALSE;
	permFaults.motor.B.OverPhaseBCurrent   = (fabs(drvFOC.iAbcFbck.tFArg2) > I_PH_OVER) ? TRUE : FALSE;
	permFaults.motor.B.OverPhaseCCurrent   = (fabs(drvFOC.iAbcFbck.tFArg3) > I_PH_OVER) ? TRUE : FALSE;

	faultDetectiontEvent = (permFaults.motor.B.OverPhaseACurrent || permFaults.motor.B.OverPhaseBCurrent || permFaults.motor.B.OverPhaseCCurrent) ? TRUE : FALSE;

	if(faultDetectiontEvent == TRUE)		fault_Log ++;
	else{}

    return faultDetectiontEvent;
}

inline void Clark_Park_Transform(void)
{
	drvFOC.ThetaCurTimeComp = drvFOC.pospeControl.thRotEl;

	if(drvFOC.ThetaCurTimeComp > MT_2PAI) 				drvFOC.ThetaCurTimeComp -= MT_2PAI;
	else if(drvFOC.ThetaCurTimeComp < 0.0f)				drvFOC.ThetaCurTimeComp += MT_2PAI;
	else{}

	drvFOC.thClarkTransform.tFArg1 = sin(drvFOC.ThetaCurTimeComp);
	drvFOC.thClarkTransform.tFArg2 = cos(drvFOC.ThetaCurTimeComp);

	drvFOC.iAlBeFbck.tFArg2	= drvFOC.iAbcFbck.tFArg1;
	drvFOC.iAlBeFbck.tFArg1	= MT_1_OVR_SQ3 * (drvFOC.iAbcFbck.tFArg3 - drvFOC.iAbcFbck.tFArg2);

	drvFOC.iDQFbck.tFArg2	= (drvFOC.iAlBeFbck.tFArg2*drvFOC.thClarkTransform.tFArg2 - drvFOC.iAlBeFbck.tFArg1*drvFOC.thClarkTransform.tFArg1);
	drvFOC.iDQFbck.tFArg1	= (drvFOC.iAlBeFbck.tFArg2*drvFOC.thClarkTransform.tFArg1 + drvFOC.iAlBeFbck.tFArg1*drvFOC.thClarkTransform.tFArg2);
}

inline void get_Voltage_Limit(void)
{
	drvFOC.Vph_Set = sqrt(drvFOC.uDQReq.tFArg1 * drvFOC.uDQReq.tFArg1 + drvFOC.uDQReq.tFArg2 * drvFOC.uDQReq.tFArg2);
	LPF(drvFOC.Vph_Set_Fil, drvFOC.Vph_Set, drvFOC.lpf_gain.VphSetLpfFct);
	drvFOC.Vqe_Limit = sqrt((drvFOC.Vph_Max * drvFOC.Vph_Max)-(drvFOC.uDQReq.tFArg1 * drvFOC.uDQReq.tFArg1));
}

inline void Inverse_Park_Transform(void)
{
	if(meas.flag.B.angle_calibDone == TRUE)		drvFOC.ThetaVoltTimeComp = drvFOC.pospeControl.thRotEl + (float)(vEhalPwm_SamplingTime * TIME_COMP_CONSTANT * drvFOC.Encoder.EncWeFil);
	else										drvFOC.ThetaVoltTimeComp = drvFOC.pospeControl.thRotEl;

	if(drvFOC.ThetaVoltTimeComp > MT_2PAI) 		drvFOC.ThetaVoltTimeComp -= MT_2PAI;
	else if(drvFOC.ThetaVoltTimeComp < 0.) 		drvFOC.ThetaVoltTimeComp += MT_2PAI;
	else{}

	drvFOC.thParkTransform.tFArg1 = sin(drvFOC.ThetaVoltTimeComp);
	drvFOC.thParkTransform.tFArg2 = cos(drvFOC.ThetaVoltTimeComp);

	drvFOC.uAlBeReq.tFArg2 =  (drvFOC.uDQReq.tFArg2 * drvFOC.thParkTransform.tFArg2) + (drvFOC.uDQReq.tFArg1 * drvFOC.thParkTransform.tFArg1);
	drvFOC.uAlBeReq.tFArg1 = -(drvFOC.uDQReq.tFArg2 * drvFOC.thParkTransform.tFArg1) + (drvFOC.uDQReq.tFArg1 * drvFOC.thParkTransform.tFArg2);

	drvFOC.uAbcReq.tFArg1 =  drvFOC.uAlBeReq.tFArg2;
	drvFOC.uAbcReq.tFArg2 = -(MT_1_OVR_2 * drvFOC.uAlBeReq.tFArg2) - (MT_SQ3_OVR_2 * drvFOC.uAlBeReq.tFArg1);
	drvFOC.uAbcReq.tFArg3 = -(MT_1_OVR_2 * drvFOC.uAlBeReq.tFArg2) + (MT_SQ3_OVR_2 * drvFOC.uAlBeReq.tFArg1);
}

static char focSlowLoop()
{
	drvFOC.pospeControl.speedLoopCntr    = 0;

	drvFOC.iDQReq.tFArg1 = 0;
	drvFOC.pospeControl.wRotElReqRamp = DoRampRef_LPF(drvFOC.pospeControl.wRotElReq, &drvFOC.speedRamp);
	drvFOC.pospeControl.wRotElErr = (drvFOC.pospeControl.wRotElReqRamp - drvFOC.pospeControl.wRotEl);
	drvFOC.iDQReq.tFArg2 = DoCtrlPIAS(&drvFOC.CtrlPIA_S, drvFOC.pospeControl.wRotElErr);

    return TRUE;
}

void focFastLoop(void)
{
	drvFOC.CtrlPIAD.tFUpperLimit	= drvFOC.Vph_Max;
	drvFOC.CtrlPIAD.tFLowerLimit	= (CONS_1_M * drvFOC.CtrlPIAD.tFUpperLimit);

    drvFOC.iDQErr.tFArg1 = drvFOC.iDQReq.tFArg1 - drvFOC.iDQFbck.tFArg1;
    drvFOC.uDQReq.tFArg1 = DoCtrlPIA(&drvFOC.CtrlPIAD, drvFOC.iDQErr.tFArg1);

    get_Voltage_Limit();

	drvFOC.CtrlPIAQ.tFUpperLimit	= drvFOC.Vqe_Limit;
	drvFOC.CtrlPIAQ.tFLowerLimit	= (CONS_1_M * drvFOC.CtrlPIAQ.tFUpperLimit);

    drvFOC.iDQErr.tFArg2 = drvFOC.iDQReq.tFArg2 - drvFOC.iDQFbck.tFArg2;
    drvFOC.uDQReq.tFArg2 = DoCtrlPIA(&drvFOC.CtrlPIAQ, drvFOC.iDQErr.tFArg2);

	Inverse_Park_Transform();
}

inline void MIN_MAX_PWM(void)
{
	float PwmScale=0.,MinMaxTmp=0.,MidTmp=0.;
	sint16 PwmUCompareTmp=0,PwmVCompareTmp=0,PwmWCompareTmp=0;

	MidTmp = (drvFOC.uAbcReq.tFArg1 - drvFOC.uAbcReq.tFArg2) * (drvFOC.uAbcReq.tFArg3 - drvFOC.uAbcReq.tFArg1) > 0.0 ? drvFOC.uAbcReq.tFArg1 : (drvFOC.uAbcReq.tFArg2 - drvFOC.uAbcReq.tFArg3) * (drvFOC.uAbcReq.tFArg3 - drvFOC.uAbcReq.tFArg1) >= 0.0 ? drvFOC.uAbcReq.tFArg3 : drvFOC.uAbcReq.tFArg2;
	PwmScale = (float)vEhalPwm_MaxDutyTickValue / meas.measured.tFHVdcb.filt;

	MinMaxTmp = (MidTmp * MT_1_OVR_2);

	drvFOC.uNAbcReq.tFArg1 = drvFOC.uAbcReq.tFArg1 + MinMaxTmp;
	drvFOC.uNAbcReq.tFArg2 = drvFOC.uAbcReq.tFArg2 + MinMaxTmp;
	drvFOC.uNAbcReq.tFArg3 = drvFOC.uAbcReq.tFArg3 + MinMaxTmp;
	drvFOC.uNAbcReq.tFArg1 = SAT(drvFOC.uNAbcReq.tFArg1, drvFOC.Vpl_Max);
	drvFOC.uNAbcReq.tFArg2 = SAT(drvFOC.uNAbcReq.tFArg2, drvFOC.Vpl_Max);
	drvFOC.uNAbcReq.tFArg3 = SAT(drvFOC.uNAbcReq.tFArg3, drvFOC.Vpl_Max);

	PwmUCompareTmp = (sint16)(drvFOC.uNAbcReq.tFArg1 * PwmScale);
	PwmVCompareTmp = (sint16)(drvFOC.uNAbcReq.tFArg2 * PwmScale);
	PwmWCompareTmp = (sint16)(drvFOC.uNAbcReq.tFArg3 * PwmScale);
	PwmUCompareTmp = (sint16)SAT(PwmUCompareTmp,(sint16)vEhalPwm_HalfDutyTickValue);
	PwmVCompareTmp = (sint16)SAT(PwmVCompareTmp,(sint16)vEhalPwm_HalfDutyTickValue);
	PwmWCompareTmp = (sint16)SAT(PwmWCompareTmp,(sint16)vEhalPwm_HalfDutyTickValue);

	drvFOC.pwmcompare.tU16Arg1 = (sint16)PwmUCompareTmp + (sint16)vEhalPwm_HalfDutyTickValue;
	drvFOC.pwmcompare.tU16Arg2 = (sint16)PwmVCompareTmp + (sint16)vEhalPwm_HalfDutyTickValue;
	drvFOC.pwmcompare.tU16Arg3 = (sint16)PwmWCompareTmp + (sint16)vEhalPwm_HalfDutyTickValue;
}

char Meas_GetSpeed(void)
{
	drvFOC.Encoder.EncValue		= vBswTest_EncValue.EncA_Pulse;
	drvFOC.Encoder.EncDirection	= vBswTest_EncValue.EncA_Dir;

	if(drvFOC.Encoder.EncValue != drvFOC.Encoder.EncValue_Old)
	{
		drvFOC.Encoder.Diff_Pulse = (((drvFOC.Encoder.EncValue - drvFOC.Encoder.EncValue_Old) << 16) >> 16);
		drvFOC.Encoder.pulseSum += drvFOC.Encoder.Diff_Pulse;

		if(drvFOC.Encoder.pulseSum > ENCPULSEPERPOLE)			drvFOC.Encoder.pulseSum -= ENCPULSEPERPOLE;
		else if(drvFOC.Encoder.pulseSum < 0)					drvFOC.Encoder.pulseSum += ENCPULSEPERPOLE;
		else{}
	}
	else{}

//	if(drvFOC.Encoder.EncDirection == ENCODER_DIR_CCW)
//	{
//		if((drvFOC.Encoder.Z_Pulse_Old == FALSE) && (drvFOC.Encoder.Z_Pulse == TRUE))
//		{
//			drvFOC.Encoder.pulseSum = (ENCPULSEPERPOLE * ENCZPULSE_ANGLE * ENCZPOSITION_RATIO);
//			drvFOC.Encoder.Z_Pulse_Set = TRUE;
//		}
//		else
//		{
//			drvFOC.Encoder.Z_Pulse_Set = FALSE;
//		}
//	}
//	else
//	{
//		if((drvFOC.Encoder.Z_Pulse_Old == TRUE) && (drvFOC.Encoder.Z_Pulse == FALSE))
//		{
//			drvFOC.Encoder.pulseSum = (ENCPULSEPERPOLE * ENCZPULSE_ANGLE * ENCZPOSITION_RATIO);
//			drvFOC.Encoder.Z_Pulse_Set = TRUE;
//		}
//		else
//		{
//			drvFOC.Encoder.Z_Pulse_Set = FALSE;
//		}
//	}

	drvFOC.Encoder.Ftheta = drvFOC.Encoder.pulseSum * ENCTHETA_SCALE;

	if(drvFOC.Encoder.Ftheta > MT_2PAI)			drvFOC.Encoder.Ftheta = (drvFOC.Encoder.Ftheta - MT_2PAI);
	else if(drvFOC.Encoder.Ftheta < 0.0f)			drvFOC.Encoder.Ftheta = (drvFOC.Encoder.Ftheta + MT_2PAI);
	else{}

	drvFOC.Encoder.ThetaFdbComp = drvFOC.Encoder.Ftheta;

	if(drvFOC.Encoder.ThetaFdbComp > MT_2PAI)				JJM_CNT.tfE = drvFOC.Encoder.ThetaFdbComp;
	else if(drvFOC.Encoder.ThetaFdbComp < 0.0f)			JJM_CNT.tfE = drvFOC.Encoder.ThetaFdbComp;
	else{}

//	if(drvFOC.Encoder.Z_Pulse_Set == FALSE)
//	{
//		drvFOC.Encoder.Diff_Ftheta		= (drvFOC.Encoder.Ftheta - drvFOC.Encoder.Ftheta_Old);
//		drvFOC.Encoder.Diff_Ftheta_Old	= drvFOC.Encoder.Diff_Ftheta;
//	}
//	else
//	{
//		drvFOC.Encoder.Diff_Ftheta = drvFOC.Encoder.Diff_Ftheta_Old;
//	}

	drvFOC.Encoder.Diff_Ftheta		= (drvFOC.Encoder.Ftheta - drvFOC.Encoder.Ftheta_Old);

	if(drvFOC.Encoder.EncDirection == ENCODER_DIR_CCW)
	{
		if(drvFOC.Encoder.Diff_Ftheta < 0 )					drvFOC.Encoder.Diff_Ftheta = (drvFOC.Encoder.Diff_Ftheta + MT_2PAI);
		else{}
	}
	else
	{
		if(drvFOC.Encoder.Diff_Ftheta > 0)					drvFOC.Encoder.Diff_Ftheta = (drvFOC.Encoder.Diff_Ftheta - MT_2PAI);
		else{}
	}

	drvFOC.Encoder.Diff_Ftheta	= fabs(drvFOC.Encoder.Diff_Ftheta);

	drvFOC.Encoder.EncWe		= (drvFOC.Encoder.Diff_Ftheta * vEhalPwm_FrequencyValue);

#ifdef	MOTOR_DIR_CCW
	if(drvFOC.Encoder.EncDirection == ENCODER_DIR_CW)		drvFOC.Encoder.EncWe = drvFOC.Encoder.EncWe * CONS_1_M;
	else{}
#elif defined MOTOR_DIR_CW
	if(drvFOC.Encoder.EncDirection == ENCODER_DIR_CCW)		drvFOC.Encoder.EncWe = drvFOC.Encoder.EncWe * CONS_1_M;
	else{}
#endif

	LPF(drvFOC.Encoder.EncWeFil, drvFOC.Encoder.EncWe, drvFOC.lpf_gain.EncWeLpfFct);

	drvFOC.Encoder.EncSpeed = (drvFOC.Encoder.EncWeFil * WE2RPM);

	drvFOC.Encoder.EncValue_Old	= drvFOC.Encoder.EncValue;
	drvFOC.Encoder.Z_Pulse_Old	= drvFOC.Encoder.Z_Pulse;
	drvFOC.Encoder.Ftheta_Old		= drvFOC.Encoder.Ftheta;

    return(1);
}

void stateCalib(void)
{
	float TMP0=0.0f,TMP1=0.0f;

	if((meas.flag.B.angle_calibDone == FALSE) && (meas.flag.B.current_calibDone == TRUE))
	{
		/* Encoder_Init */
		EhalGpt12_InitEncoder(0);
		drvFOC.Encoder.EncValue		= 0;
		drvFOC.Encoder.EncValue_Old	= 0;
		drvFOC.Encoder.Ftheta		= 0.;
		drvFOC.Encoder.Ftheta_Old	= 0.;
		drvFOC.Encoder.ThetaFdbComp	= 0.;
		drvFOC.Encoder.EncWe		= 0.;
		drvFOC.Encoder.EncWeFil		= 0.;
		drvFOC.Encoder.EncSpeed		= 0.;
		drvFOC.Encoder.pulseSum		= 0.;
		drvFOC.Encoder.Diff_Pulse	= 0.;
		drvFOC.Encoder.Diff_Ftheta	= 0.;

		TMP0						= ((float)(vEhalIcu_IcuMonitor[0].duty_001per)/100.0f);
		drvFOC.Init_Position_Deg_E	= fmod(((MT_DEGREE - ((TMP0 - A1333_MIN_DUTY)/(A1333_MAX_DUTY - A1333_MIN_DUTY) * MT_DEGREE)) * MOTOR_PP) + ENCZPULSE_ANGLE,MT_DEGREE);
		TMP1						= (drvFOC.Init_Position_Deg_E * TR_DEG2RAD);
		drvFOC.Encoder.pulseSum		= (TMP1 / MT_2PAI) * ENCPULSEPERPOLE;

		meas.flag.B.angle_calibDone	= TRUE;
	}
	else{}
}

void Simply_MotorContorl_Init(void)
{
	if(JJM_CNT.tbF_A == FALSE)
	{
		JJM_CNT.tbF_A = TRUE;
		// ACCELATION
		drvFOC.speedRamp.tFSlopeInc			= (2000.0 * (SPEED_LOOP_CNTR * vEhalPwm_SamplingTime));
		drvFOC.speedRamp.tFSlopeDec			= (2000.0 * (SPEED_LOOP_CNTR * vEhalPwm_SamplingTime));
//		drvFOC.speedRamp.tFSlopeInc			= (20000.0 * (5.0f*vEhalPwm_SamplingTime));
//		drvFOC.speedRamp.tFSlopeDec			= (20000.0 * (5.0f*vEhalPwm_SamplingTime));

		// Speed PI controllers
//		drvFOC.CtrlPIA_S.tFKp				= ((SC_WCC / SC_WSC_GAIN) * (MOTOR_J / MOTOR_KT));
//		drvFOC.CtrlPIA_S.tFKiT				= (drvFOC.CtrlPIA_S.tFKp * ((SC_WCC / SC_WSC_GAIN) / SC_WPI_GAIN) * (SPEED_LOOP_CNTR * vEhalPwm_SamplingTime));
		drvFOC.CtrlPIA_S.tFKp				= 0.004f;
		drvFOC.CtrlPIA_S.tFKiT				= 0.00001f;
		drvFOC.CtrlPIA_S.tFKcT				= (CONS_1 / drvFOC.CtrlPIA_S.tFKp);
		drvFOC.CtrlPIA_S.tFUpperLimit		= CL_CURRENT_LIMIT;
		drvFOC.CtrlPIA_S.tFLowerLimit		= (CONS_1_M * drvFOC.CtrlPIA_S.tFUpperLimit);

		// Current PI controllers
		drvFOC.iCLoop_Limit					= CLOOP_LIMIT;
		drvFOC.CtrlPIAD.tFKp				= (CC_ZETA * (CC_F_CUT * MT_2PAI) * MOTOR_LD);
		drvFOC.CtrlPIAD.tFKiT				= (CC_ZETA * (CC_F_CUT * MT_2PAI) * MOTOR_RS * vEhalPwm_SamplingTime);
		drvFOC.CtrlPIAD.tFKcT				= (CONS_1 / drvFOC.CtrlPIAD.tFKp);

		drvFOC.CtrlPIAQ.tFKp				= (CC_ZETA * (CC_F_CUT * MT_2PAI) * MOTOR_LQ);
		drvFOC.CtrlPIAQ.tFKiT				= (CC_ZETA * (CC_F_CUT * MT_2PAI) * MOTOR_RS * vEhalPwm_SamplingTime);
		drvFOC.CtrlPIAQ.tFKcT				= (CONS_1 / drvFOC.CtrlPIAQ.tFKp);

		//Filter_Gain
		FILFCT(VPHSET_CUTOFF,			drvFOC.lpf_gain.VphSetLpfFct,			vEhalPwm_FrequencyValue);
		FILFCT(ENCWE_CUTOFF,			drvFOC.lpf_gain.EncWeLpfFct,			vEhalPwm_FrequencyValue);
		FILFCT(SPD_CUTOFF,				drvFOC.lpf_gain.SpeedLpfFct,			vEhalPwm_FrequencyValue);
	}
	else{}

	/* Speed */
	drvFOC.pospeControl.wRotElReq		= 0.;
	drvFOC.pospeControl.wRotElReqRamp	= 0.;
	drvFOC.pospeControl.wRotEl			= 0.;
	drvFOC.pospeControl.wRotElFilt		= 0.;

	drvFOC.speedRamp.tFInteg			= 0;
	drvFOC.speedRamp.FilterEnable		= 0;
	drvFOC.speedRamp.tFKx				= 0;
	drvFOC.speedRamp.tFIntegFlt			= 0;

	drvFOC.pospeControl.speedLoopCntr	= 0.;
	drvFOC.pospeControl.wRotElErr		= 0.;
	drvFOC.CtrlPIA_S.tFInteg			= 0.;

	/* Current */
	drvFOC.iDQReq.tFArg1				= 0.;
	drvFOC.iDQReq.tFArg2				= 0.;

	drvFOC.CtrlPIAD.tFInteg				= 0.;
	drvFOC.CtrlPIAD.tFVff				= 0.;
	drvFOC.CtrlPIAQ.tFInteg				= 0.;
	drvFOC.CtrlPIAQ.tFVff				= 0.;

	/* Voltages */
	drvFOC.Vph_Set						= 0.;
	drvFOC.Vph_Set_Fil					= 0.;
	drvFOC.uDQReq.tFArg1				= 0.;
	drvFOC.uDQReq.tFArg2				= 0.;
	drvFOC.uAlBeReq.tFArg1				= 0.;
	drvFOC.uAlBeReq.tFArg2				= 0.;
	drvFOC.uAbcReq.tFArg1				= 0.;
	drvFOC.uAbcReq.tFArg2				= 0.;
	drvFOC.uAbcReq.tFArg3				= 0.;
	drvFOC.uNAbcReq.tFArg1				= 0.;
	drvFOC.uNAbcReq.tFArg2				= 0.;
	drvFOC.uNAbcReq.tFArg3				= 0.;
	drvFOC.pwmcompare.tU16Arg1			= vEhalPwm_HalfDutyTickValue;
	drvFOC.pwmcompare.tU16Arg2			= vEhalPwm_HalfDutyTickValue;
	drvFOC.pwmcompare.tU16Arg3			= vEhalPwm_HalfDutyTickValue;



	/* Speed/Position */
	drvFOC.ThetaVoltTimeComp			= 0.;
	drvFOC.thClarkTransform.tFArg1		= 0.;
	drvFOC.thClarkTransform.tFArg2		= 0.;
	drvFOC.thParkTransform.tFArg1		= 0.;
	drvFOC.thParkTransform.tFArg2		= 0.;

	/* Encoder */
	drvFOC.Encoder.EncWe					= 0.;
	drvFOC.Encoder.EncWeFil				= 0.;
	drvFOC.Encoder.EncSpeed				= 0.;


	//VOLTAGE&CURRENT_VECTOR_TEST
	JJM_CNT.tfA					= 0.0;
	JJM_CNT.tfB					= 0.0;
#if((TAGET_CONTROL == VOLTAGE_VECTOR_TEST) || (TAGET_CONTROL == CURRENT_VECTOR_TEST))
    drvFOC.pospeControl.thRotEl = 0.0;
#endif
    if(meas.flag.B.angle_calibDone == FALSE)		stateCalib();
    else{}
}

void Voltage_Vector(void)
{
#if(TAGET_CONTROL == VOLTAGE_VECTOR_TEST)
	drvFOC.uDQReq.tFArg1		= 0.0;
    drvFOC.uDQReq.tFArg2		= JJM_CNT.tfA;

	drvFOC.pospeControl.wRotEl	= (JJM_CNT.tfB * RPM2WE);
	drvFOC.pospeControl.thRotEl += (drvFOC.pospeControl.wRotEl * vEhalPwm_SamplingTime);

	if(drvFOC.pospeControl.thRotEl > MT_2PAI) 			drvFOC.pospeControl.thRotEl -= MT_2PAI;
	else if(drvFOC.pospeControl.thRotEl < 0.) 			drvFOC.pospeControl.thRotEl += MT_2PAI;
	else{}

	Inverse_Park_Transform();
#elif(TAGET_CONTROL == CURRENT_VECTOR_TEST)
	drvFOC.iDQReq.tFArg1	= 0.0;
	drvFOC.iDQReq.tFArg2	= JJM_CNT.tfA;

	if(drvFOC.iDQReq.tFArg2 > 10.0)		drvFOC.iDQReq.tFArg2 = 10.0;
	else{}

	drvFOC.pospeControl.wRotEl	= (JJM_CNT.tfB * RPM2WE);
	drvFOC.pospeControl.thRotEl += (drvFOC.pospeControl.wRotEl * vEhalPwm_SamplingTime);

	if(drvFOC.pospeControl.thRotEl > MT_2PAI) 			drvFOC.pospeControl.thRotEl -= MT_2PAI;
	else if(drvFOC.pospeControl.thRotEl < 0.) 			drvFOC.pospeControl.thRotEl += MT_2PAI;
	else{}

	focFastLoop();
#elif(TAGET_CONTROL == ENCODER_VECTOR_TEST)
	if (drvFOC.pospeControl.speedLoopCntr++ >= SPEED_LOOP_CNTR)			focSlowLoop();
	else{}

	focFastLoop();
#endif
	MIN_MAX_PWM();
}

void Operating_SPEE_REF(void)
{
	if(drvFOC.can_spd_cmd != 0)
	{
		drvFOC.pospeControl.wRotElReq = drvFOC.can_spd_cmd;

		if(drvFOC.pospeControl.wRotElReq >= SPEED_REF_MAX)						drvFOC.pospeControl.wRotElReq = SPEED_REF_MAX;
		else if(drvFOC.pospeControl.wRotElReq <= SPEED_REF_MIN)					drvFOC.pospeControl.wRotElReq = SPEED_REF_MIN;
		else{}
	}
	else
	{
		drvFOC.pospeControl.wRotElReq = 0;
	}
}

void Simply_MotorContorl(void)
{
	static char getFcnStatus;

	getFcnStatus = faultDetection();

	if(getFcnStatus)			vBswTest_Pwm_Enable_F = FALSE;
	else{}

	drvFOC.iCLoop_Limit = CLOOP_LIMIT;
	drvFOC.Vph_Max = MT_1_OVR_SQ3 * meas.measured.tFHVdcb.filt * drvFOC.iCLoop_Limit;
	drvFOC.Vpl_Max = MT_1_OVR_2 * meas.measured.tFHVdcb.filt * drvFOC.iCLoop_Limit;

	if(vBswTest_Pwm_Enable_F == FALSE)		drvFOC.can_spd_cmd = 0;
	else{}

	if((meas.flag.B.current_calibDone == TRUE) && (meas.flag.B.angle_calibDone == TRUE))
	{
#if(TAGET_MOTOR == HVEOP_MOTOR)
		drvFOC.iAbcFbck.tFArg1 = meas.measured.tFPhU.raw;
		drvFOC.iAbcFbck.tFArg2 = meas.measured.tFPhV.raw;
		drvFOC.iAbcFbck.tFArg3 = meas.measured.tFPhW.raw;
#elif(TAGET_MOTOR == ARS_MOTOR)
		drvFOC.iAbcFbck.tFArg1 = meas.measured.tFPhW.raw;
		drvFOC.iAbcFbck.tFArg2 = meas.measured.tFPhV.raw;
		drvFOC.iAbcFbck.tFArg3 = meas.measured.tFPhU.raw;
#endif
		Clark_Park_Transform();
		Meas_GetSpeed();

#if(TAGET_CONTROL == ENCODER_VECTOR_TEST)
		Operating_SPEE_REF();

		drvFOC.pospeControl.thRotEl	= drvFOC.Encoder.ThetaFdbComp;
		drvFOC.pospeControl.wRotEl	= drvFOC.Encoder.EncSpeed;
		LPF(drvFOC.pospeControl.wRotElFilt, drvFOC.pospeControl.wRotEl, drvFOC.lpf_gain.SpeedLpfFct);
#endif

		if(drvFOC.can_spd_cmd != 0)		Voltage_Vector();
		else							Simply_MotorContorl_Init();
	}
	else
	{
		Simply_MotorContorl_Init();
	}

#if(TAGET_MOTOR == HVEOP_MOTOR)
	vBswTest_Pwm_DutyCycle_U = drvFOC.pwmcompare.tU16Arg1;
	vBswTest_Pwm_DutyCycle_V = drvFOC.pwmcompare.tU16Arg2;
	vBswTest_Pwm_DutyCycle_W = drvFOC.pwmcompare.tU16Arg3;
#elif(TAGET_MOTOR == ARS_MOTOR)
	vBswTest_Pwm_DutyCycle_U = drvFOC.pwmcompare.tU16Arg3;
	vBswTest_Pwm_DutyCycle_V = drvFOC.pwmcompare.tU16Arg2;
	vBswTest_Pwm_DutyCycle_W = drvFOC.pwmcompare.tU16Arg1;
#endif
}





void VectorTest_Task_10ms(void)
{
	vEhalDac_DacModule = TLV5614;
//	vBswTest_RMT_CMD_10ms_RxNew = ShrHWIA_BswCan_GetMsg(2, &vBswTest_RMT_CMD_10ms_Dlc, &vBswTest_RMT_CMD_10ms.byte[0]);
//	vBswTest_RMT_CMD_10ms.signal.Pwm_Enable_F = vBswTest_Pwm_Enable_F;
//	vBswTest_RMT_CMD_10ms.signal.can_spd_cmd
	vBswTest_CanMsg_RMT_CMD_RxNew = ShrHWIA_BswCan_GetMsg(3, &vBswTest_CanMsg_RMT_CMD_Dlc, &vBswTest_CanMsg_RMT_CMD.byte[0]);

	if(vBswTest_CanMsg_RMT_CMD.signal.TEST_EN == 1){
		vBswTest_Pwm_Enable_F = vBswTest_CanMsg_RMT_CMD.signal.Pwm_Enable_F;
		drvFOC.can_spd_cmd = vBswTest_CanMsg_RMT_CMD.signal.can_spd_cmd;
//		JJM_CNT.tfA = (float)(vBswTest_CanMsg_RMT_CMD.signal.JJM_CNT_tfA);
//		vBswTest_Pwm_Period_SetValue = vBswTest_CanMsg_RMT_CMD.signal.FrequencyValue;
//		vBswTest_Pwm_Deadtime_SetValue = vBswTest_CanMsg_RMT_CMD.signal.DeadTimeValue;

//		vEhalDac_DacModule = TLV5614;
//		vBswCanMsg_RMT_RES.signal.wRotElFilt = (sint16)(drvFOC.pospeControl.wRotElFilt);
//		vBswCanMsg_RMT_RES.signal.AdcValue_HVDC = (uint16)(vBswTest_AdcValue.HVDC);
//		vBswCanMsg_RMT_RES.signal.AdcValue_Tigbt = (sint16)(vBswTest_AdcValue.Tigbt);
//		ShrHWIA_BswCan_SetMsg(CAN_MSG_TX_INDEX_RMT_RES, 16, &vBswCanMsg_RMT_RES.byte[0]);
	}


}
