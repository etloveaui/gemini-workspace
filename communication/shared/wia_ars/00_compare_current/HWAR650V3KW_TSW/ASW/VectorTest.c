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
#include "BswDio.h"
#include "BswGpt_Cbk.h"
#include "BswIcu_Cbk.h"
#include "BswAdc_Cbk.h"
//#include "BswSent.h"

appFaultStatus_t		permFaults;			// Permanent faults to be indicated inhere
pmsmDrive_t				drvFOC;        		// Field Oriented Control Variables
MotControl_t			MotControl;
Debug_t					JJM_CNT;			// Debug

uint32 JJM_EncA_Pulse_I_Time = 0;

long int Diff_I_Pulse_Diff_Cnt = 0, Diff_I_Pulse_Diff_Cnt_Old = 0, JJM_MAX_CNT = 0, JJM_MIN_CNT = 0;
float JJM_Compensation_E_Angle = 0.0;
float IPulse_Angle = 0.0;
uint8 fault_Log = 0;
IIR2_Filter stage1, stage2;
FIRFilter fir_d, fir_q;
float fir_coeffs[FIR_TAP_NUM] = {
    -0.0012, -0.0024, -0.0031, -0.0027, -0.0008,
     0.0029,  0.0078,  0.0131,  0.0176,  0.0198,
     0.0184,  0.0127,  0.0027, -0.0109, -0.0260,
    -0.0404, -0.0518, -0.0581, -0.0577, -0.0501,
    -0.0361, -0.0173,  0.0033,  0.0225,  0.0378,
     0.0474,  0.0504,  0.0466,  0.0369,  0.0227,
     0.0059
};

typBswCanMsg_RMT_CMD vBswTest_CanMsg_RMT_CMD;
uint8 vBswTest_CanMsg_RMT_CMD_RxNew;
uint8 vBswTest_CanMsg_RMT_CMD_Dlc;

typBswCanMsg_RMT_RES vBswCanMsg_RMT_RES;

extern uint8 vEhalDac_DacModule;
extern uint16 vEhalPwm_HalfDutyTickValue;
extern float vEhalPwm_SamplingTime;
extern uint16 vEhalPwm_FrequencyValue;
extern uint16 vEhalPwm_MaxDutyTickValue;
extern measModule_t	meas;
extern typEhalIcu_IcuMonitor vEhalIcu_IcuMonitor[5];

extern boolean HVDCvolt_fault_F;
extern boolean IPM_fault_F;
extern boolean Interlock_fault_F;
extern boolean Ucurr_fault_F;
extern boolean Wcurr_fault_F;
extern boolean DCcurr_fault_F;

extern void EhalGpt12_InitEncoder(uint8 CLRT3EN);

///////////////////////////////////////////////////////////////////////////////////////////////////////////
void iir2_filter_setup(IIR2_Filter *filt,
                       float b0, float b1, float b2,
                       float a1, float a2)
{
    filt->b0 = b0;
    filt->b1 = b1;
    filt->b2 = b2;
    filt->a1 = a1;
    filt->a2 = a2;
    filt->x1 = filt->x2 = 0.0f;
    filt->y1 = filt->y2 = 0.0f;
}

float iir2_filter_process(IIR2_Filter *filt, float input)
{
    float output = filt->b0 * input
                 + filt->b1 * filt->x1
                 + filt->b2 * filt->x2
                 - filt->a1 * filt->y1
                 - filt->a2 * filt->y2;

    filt->x2 = filt->x1;
    filt->x1 = input;
    filt->y2 = filt->y1;
    filt->y1 = output;

    return output;
}

void FIR_Init(FIRFilter *filt, const float *coeffs)
{
    for (int i = 0; i < FIR_TAP_NUM; i++) {
        filt->coeffs[i] = coeffs[i];
        filt->buffer[i] = 0.0f;
    }
    filt->index = 0;
}

float FIR_Apply(FIRFilter *filt, float input)
{
    filt->buffer[filt->index] = input;

    float output = 0.0f;
    int idx = filt->index;

    for (int i = 0; i < FIR_TAP_NUM; i++) {
        output += filt->coeffs[i] * filt->buffer[idx];
        idx = (idx == 0) ? FIR_TAP_NUM - 1 : idx - 1;
    }

    filt->index = (filt->index + 1) % FIR_TAP_NUM;

    return output;
}


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

void Test_CAN_10ms(void)
{
//	vBswTest_RMT_CMD_10ms_RxNew = ShrHWIA_BswCan_GetMsg(2, &vBswTest_RMT_CMD_10ms_Dlc, &vBswTest_RMT_CMD_10ms.byte[0]);
//	vBswTest_RMT_CMD_10ms.signal.Pwm_Enable_F = vBswTest_Pwm_Enable_Mode;
//	vBswTest_RMT_CMD_10ms.signal.can_spd_cmd
	vBswTest_CanMsg_RMT_CMD_RxNew = ShrHWIA_BswCan_GetMsg(4, &vBswTest_CanMsg_RMT_CMD_Dlc, &vBswTest_CanMsg_RMT_CMD.byte[0]);

	if(vBswTest_CanMsg_RMT_CMD.signal.TEST_EN == 1)
	{
		vBswTest_Pwm_Enable_Mode = vBswTest_CanMsg_RMT_CMD.signal.Pwm_Enable_F;
		MotControl.Speed_SpeedCMD = vBswTest_CanMsg_RMT_CMD.signal.can_spd_cmd;
//		JJM_CNT.tfA = (float)(vBswTest_CanMsg_RMT_CMD.signal.JJM_CNT_tfA);
//		vBswTest_Pwm_Period_SetValue = vBswTest_CanMsg_RMT_CMD.signal.FrequencyValue;
//		vBswTest_Pwm_Deadtime_SetValue = vBswTest_CanMsg_RMT_CMD.signal.DeadTimeValue;

//		vBswCanMsg_RMT_RES.signal.wRotElFilt = (sint16)(drvFOC.pospeControl.wRotElFilt);
//		vBswCanMsg_RMT_RES.signal.AdcValue_HVDC = (uint16)(vBswTest_AdcValue.HVDC);
		vBswCanMsg_RMT_RES.signal.AdcValue_Tigbt = (sint16)(vBswTest_AdcValue.Tigbt);
		vBswCanMsg_RMT_RES.signal.AdcValue_Tpcb = (sint16)(vBswTest_AdcValue.Tpcb);
		ShrHWIA_BswCan_SetMsg(CAN_MSG_TX_INDEX_RMT_RES, 16, &vBswCanMsg_RMT_RES.byte[0]);

//		vBswCanMsg_RMT_RES.signal.Sent_State = (uint16)(vBswTest_State);
//		vBswCanMsg_RMT_RES.signal.Sent_Data = vBswTest_SentData;
//		vBswCanMsg_RMT_RES.signal.ThetaFdbComp = drvFOC.Encoder.ThetaFdbComp;
//		ShrHWIA_BswCan_SetMsg(CAN_MSG_TX_INDEX_RMT_RES, 16, &vBswCanMsg_RMT_RES.byte[0]);
	}
	else{}
}

static char faultDetection()
{
	char faultDetectiontEvent;
	static uint16 OVP_Cnt,UVP_Cnt,OVP_Recovery_Cnt,UVP_Recovery_Cnt;

    if(meas.flag.Current_Cal == PASS)
    {
		permFaults.motor.B.SW_OCP_U		= (fabs(drvFOC.iAbcFbck.tFArg1) > I_PH_OVER) ? TRUE : FALSE;
		permFaults.motor.B.SW_OCP_V		= (fabs(drvFOC.iAbcFbck.tFArg2) > I_PH_OVER) ? TRUE : FALSE;
		permFaults.motor.B.SW_OCP_W		= (fabs(drvFOC.iAbcFbck.tFArg3) > I_PH_OVER) ? TRUE : FALSE;
		permFaults.motor.B.SW_OCP_DC	= (fabs(drvFOC.Idc_Measure) > I_DC_OVER) ? TRUE : FALSE;
    }
    else{}

////////////////////////////* TEMP_CODE *//////////////////////////////////
    if(permFaults.motor.B.SW_UVP_LVDC == FALSE)
    {
    	if(meas.measured.tFLVdcb.filt <= (8.5 - 0.8))
    	{
    		if(UVP_Cnt ++ > 16000)
    		{
    			permFaults.motor.B.SW_UVP_LVDC	= TRUE;
    			UVP_Cnt							= 0;
    		}
    		else{}
    	}
    	else
    	{
    		UVP_Cnt = 0;
    	}
    }
    else
    {
		if(meas.measured.tFLVdcb.filt >= (9.0 - 0.8))
		{
			if(UVP_Recovery_Cnt ++ > 16000)
			{
				permFaults.motor.B.SW_UVP_LVDC = FALSE;
				UVP_Recovery_Cnt = 0;
			}
			else{}
		}
		else
		{
			UVP_Recovery_Cnt = 0;
		}
    }

	if(permFaults.motor.B.SW_OVP_LVDC == FALSE)
	{
		if(meas.measured.tFLVdcb.filt >= (16.5 - 0.8))
		{
			if(OVP_Cnt ++ > 16000)
			{
				permFaults.motor.B.SW_OVP_LVDC = TRUE;
				OVP_Cnt = 0;
			}
			else{}
		}
		else
		{
			OVP_Cnt = 0;
		}
	}
	else
	{
		if(meas.measured.tFLVdcb.filt <= (16.0 - 0.8))
		{
			if(OVP_Recovery_Cnt ++ > 16000)
			{
				permFaults.motor.B.SW_OVP_LVDC = FALSE;
				OVP_Recovery_Cnt = 0;
			}
			else{}
		}
		else
		{
			OVP_Recovery_Cnt = 0;
		}
	}
////////////////////////////////////////////////////////////////////////////////////

    permFaults.motor.B.HW_OCP_U			= Ucurr_fault_F;
    permFaults.motor.B.HW_OCP_W			= Wcurr_fault_F;
    permFaults.motor.B.HW_OCP_DC		= DCcurr_fault_F;

    permFaults.motor.B.HW_OVP_HVDC		= HVDCvolt_fault_F;

    permFaults.motor.B.IPM_FAULT		= IPM_fault_F;
    permFaults.motor.B.INTERLOCK_FAULT	= Interlock_fault_F;

	faultDetectiontEvent = (permFaults.motor.R) ? TRUE : FALSE;

    return faultDetectiontEvent;
}

inline void Clark_Park_Transform(void)
{
	drvFOC.ThetaCurTimeComp = drvFOC.pospeControl.thRotEl;

	if(drvFOC.ThetaCurTimeComp > MT_2PAI) 		drvFOC.ThetaCurTimeComp -= MT_2PAI;
	else if(drvFOC.ThetaCurTimeComp < 0.0f)		drvFOC.ThetaCurTimeComp += MT_2PAI;
	else{}

	drvFOC.thClarkTransform.tFArg1 = sin(drvFOC.ThetaCurTimeComp);
	drvFOC.thClarkTransform.tFArg2 = cos(drvFOC.ThetaCurTimeComp);

	drvFOC.iAlBeFbck.tFArg2	= drvFOC.iAbcFbck.tFArg1;
	drvFOC.iAlBeFbck.tFArg1	= MT_1_OVR_SQ3 * (drvFOC.iAbcFbck.tFArg3 - drvFOC.iAbcFbck.tFArg2);

	drvFOC.iDQFbck.tFArg2	= (drvFOC.iAlBeFbck.tFArg2*drvFOC.thClarkTransform.tFArg2 - drvFOC.iAlBeFbck.tFArg1*drvFOC.thClarkTransform.tFArg1);
	drvFOC.iDQFbck.tFArg1	= (drvFOC.iAlBeFbck.tFArg2*drvFOC.thClarkTransform.tFArg1 + drvFOC.iAlBeFbck.tFArg1*drvFOC.thClarkTransform.tFArg2);

//	drvFOC.iDQFbck.tFArg1_filt = iir2_filter_process(&stage2, iir2_filter_process(&stage1, drvFOC.iDQFbck.tFArg1));
//	drvFOC.iDQFbck.tFArg2_filt = iir2_filter_process(&stage2, iir2_filter_process(&stage1, drvFOC.iDQFbck.tFArg2));

//	LPF(drvFOC.iDQFbck.tFArg1_filt, drvFOC.iDQFbck.tFArg1, drvFOC.lpf_gain.IdqeLpfFct);
//	LPF(drvFOC.iDQFbck.tFArg2_filt, drvFOC.iDQFbck.tFArg2, drvFOC.lpf_gain.IdqeLpfFct);

	drvFOC.iDQFbck.tFArg1_filt = drvFOC.iDQFbck.tFArg1;
	drvFOC.iDQFbck.tFArg2_filt = drvFOC.iDQFbck.tFArg2;
}

inline void get_Voltage_Limit(void)
{
	drvFOC.Vph_Set = sqrt(drvFOC.uDQReq.tFArg1 * drvFOC.uDQReq.tFArg1 + drvFOC.uDQReq.tFArg2 * drvFOC.uDQReq.tFArg2);
	LPF(drvFOC.Vph_Set_Fil, drvFOC.Vph_Set, drvFOC.lpf_gain.VphSetLpfFct);
	drvFOC.Vqe_Limit = sqrt((drvFOC.Vph_Max * drvFOC.Vph_Max)-(drvFOC.uDQReq.tFArg1 * drvFOC.uDQReq.tFArg1));
}

inline void Inverse_Park_Transform(void)
{
	if(meas.flag.Angle_Cal == PASS)				drvFOC.ThetaVoltTimeComp = (drvFOC.pospeControl.thRotEl + (float)(vEhalPwm_SamplingTime * TIME_COMP_CONSTANT * drvFOC.Encoder.EncWeFil));
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
	drvFOC.pospeControl.speedLoopCntr	= 0;

	drvFOC.iDQReq.tFArg1				= 0.0f;
	drvFOC.pospeControl.wRotElReqRamp	= DoRampRef_LPF(drvFOC.pospeControl.wRotElReq, &drvFOC.speedRamp);
	drvFOC.pospeControl.wRotElErr		= (drvFOC.pospeControl.wRotElReqRamp - drvFOC.pospeControl.wRotEl);
	drvFOC.iDQReq.tFArg2				= DoCtrlPIAS(&drvFOC.CtrlPIA_S, drvFOC.pospeControl.wRotElErr);

	return TRUE;
}

void focFastLoop(void)
{
	drvFOC.CtrlPIAD.tFUpperLimit	= drvFOC.Vph_Max;
	drvFOC.CtrlPIAD.tFLowerLimit	= (CONS_1_M * drvFOC.CtrlPIAD.tFUpperLimit);

	drvFOC.iDQErr.tFArg1 = drvFOC.iDQReq.tFArg1 - drvFOC.iDQFbck.tFArg1_filt;
	drvFOC.iDQErr.tFArg2 = drvFOC.iDQReq.tFArg2 - drvFOC.iDQFbck.tFArg2_filt;

	drvFOC.uDQReq.tFArg1 = DoCtrlPIA(&drvFOC.CtrlPIAD, drvFOC.iDQErr.tFArg1);

	get_Voltage_Limit();

	drvFOC.CtrlPIAQ.tFUpperLimit	= drvFOC.Vqe_Limit;
	drvFOC.CtrlPIAQ.tFLowerLimit	= (CONS_1_M * drvFOC.CtrlPIAQ.tFUpperLimit);

	drvFOC.uDQReq.tFArg2 = DoCtrlPIA(&drvFOC.CtrlPIAQ, drvFOC.iDQErr.tFArg2);

	Inverse_Park_Transform();
}

inline void MIN_MAX_PWM(void)
{
	float PwmScale=0.,MinMaxTmp=0.,MidTmp=0.;
	sint16 PwmUCompareTmp=0,PwmVCompareTmp=0,PwmWCompareTmp=0;

	MidTmp = ((drvFOC.uAbcReq.tFArg1 - drvFOC.uAbcReq.tFArg2) * (drvFOC.uAbcReq.tFArg3 - drvFOC.uAbcReq.tFArg1)) > 0.0 ? drvFOC.uAbcReq.tFArg1 : ((drvFOC.uAbcReq.tFArg2 - drvFOC.uAbcReq.tFArg3) * (drvFOC.uAbcReq.tFArg3 - drvFOC.uAbcReq.tFArg1)) >= 0.0 ? drvFOC.uAbcReq.tFArg3 : drvFOC.uAbcReq.tFArg2;
	PwmScale = ((float)vEhalPwm_MaxDutyTickValue / meas.measured.tFHVdcb.filt);

	MinMaxTmp = (MidTmp * MT_1_OVR_2);

	drvFOC.uNAbcReq.tFArg1 = (drvFOC.uAbcReq.tFArg1 + MinMaxTmp);
	drvFOC.uNAbcReq.tFArg2 = (drvFOC.uAbcReq.tFArg2 + MinMaxTmp);
	drvFOC.uNAbcReq.tFArg3 = (drvFOC.uAbcReq.tFArg3 + MinMaxTmp);
	drvFOC.uNAbcReq.tFArg1 = SAT(drvFOC.uNAbcReq.tFArg1, drvFOC.Vpl_Max);
	drvFOC.uNAbcReq.tFArg2 = SAT(drvFOC.uNAbcReq.tFArg2, drvFOC.Vpl_Max);
	drvFOC.uNAbcReq.tFArg3 = SAT(drvFOC.uNAbcReq.tFArg3, drvFOC.Vpl_Max);

	PwmUCompareTmp = (sint16)(drvFOC.uNAbcReq.tFArg1 * PwmScale);
	PwmVCompareTmp = (sint16)(drvFOC.uNAbcReq.tFArg2 * PwmScale);
	PwmWCompareTmp = (sint16)(drvFOC.uNAbcReq.tFArg3 * PwmScale);
	PwmUCompareTmp = (sint16)SAT(PwmUCompareTmp,(sint16)vEhalPwm_HalfDutyTickValue);
	PwmVCompareTmp = (sint16)SAT(PwmVCompareTmp,(sint16)vEhalPwm_HalfDutyTickValue);
	PwmWCompareTmp = (sint16)SAT(PwmWCompareTmp,(sint16)vEhalPwm_HalfDutyTickValue);

	drvFOC.pwmcompare.tU16Arg1 = ((sint16)PwmUCompareTmp + (sint16)vEhalPwm_HalfDutyTickValue);
	drvFOC.pwmcompare.tU16Arg2 = ((sint16)PwmVCompareTmp + (sint16)vEhalPwm_HalfDutyTickValue);
	drvFOC.pwmcompare.tU16Arg3 = ((sint16)PwmWCompareTmp + (sint16)vEhalPwm_HalfDutyTickValue);
}

void Meas_Voltage_Current(void)
{
#if(TAGET_MOTOR == HVEOP_MOTOR)
	drvFOC.iAbcFbck.tFArg1	= meas.measured.tFPhU.raw;
	drvFOC.iAbcFbck.tFArg2	= meas.measured.tFPhV.raw;
	drvFOC.iAbcFbck.tFArg3	= meas.measured.tFPhW.raw;
#elif(TAGET_MOTOR == ARS_MOTOR)
	drvFOC.iAbcFbck.tFArg1	= meas.measured.tFPhW.raw;
	drvFOC.iAbcFbck.tFArg2	= meas.measured.tFPhV.raw;
	drvFOC.iAbcFbck.tFArg3	= meas.measured.tFPhU.raw;

	LPF(meas.measured.tFIdcb.filt, meas.measured.tFIdcb.raw, drvFOC.lpf_gain.IdcLpfFct);
	drvFOC.Idc_Measure		= meas.measured.tFIdcb.filt;
#endif
	drvFOC.Vph_Max		= MT_1_OVR_SQ3 * meas.measured.tFHVdcb.filt * drvFOC.iCLoop_Limit;
	drvFOC.Vpl_Max		= MT_1_OVR_2 * meas.measured.tFHVdcb.filt * drvFOC.iCLoop_Limit;
}

char Meas_GetSpeed_Pll(void)
{
	float tmp0 = 0;

	drvFOC.Encoder.EncValue		= vBswTest_EncValue.EncA_Pulse;
	drvFOC.Encoder.EncDirection	= vBswTest_EncValue.EncA_Dir;

	if(drvFOC.Encoder.Z_Pulse == TRUE)
	{
		drvFOC.Encoder.Z_Pulse	= FALSE;

		if(drvFOC.Encoder.EncDirection == ENCODER_DIR_CCW)
		{
			if(drvFOC.Encoder.EncValue >= JJM_EncA_Pulse_I_Time)		Diff_I_Pulse_Diff_Cnt = drvFOC.Encoder.EncValue	- JJM_EncA_Pulse_I_Time;
			else														Diff_I_Pulse_Diff_Cnt = ((drvFOC.Encoder.EncValue - JJM_EncA_Pulse_I_Time) + 65535);
		}
		else
		{
			if(drvFOC.Encoder.EncValue <= JJM_EncA_Pulse_I_Time)		Diff_I_Pulse_Diff_Cnt = drvFOC.Encoder.EncValue	- JJM_EncA_Pulse_I_Time;
			else														Diff_I_Pulse_Diff_Cnt = ((drvFOC.Encoder.EncValue - JJM_EncA_Pulse_I_Time) - 65535);
		}

		drvFOC.Encoder.Z_Pulse	= FALSE;
		drvFOC.Encoder.pulseSum	= (ENCPULSEPERPOLE * ENCZPULSE_ANGLE * ENCZPOSITION_RATIO);
		drvFOC.Encoder.pulseSum = drvFOC.Encoder.pulseSum + Diff_I_Pulse_Diff_Cnt;
	}
	else
	{
		if(drvFOC.Encoder.EncValue != drvFOC.Encoder.EncValue_Old)
		{
			drvFOC.Encoder.Diff_Pulse = (((drvFOC.Encoder.EncValue - drvFOC.Encoder.EncValue_Old) << 16) >> 16);
			drvFOC.Encoder.pulseSum += drvFOC.Encoder.Diff_Pulse;
		}
		else{}
	}

	if(drvFOC.Encoder.pulseSum > ENCPULSEPERPOLE)			drvFOC.Encoder.pulseSum -= ENCPULSEPERPOLE;
	else if(drvFOC.Encoder.pulseSum < 0)					drvFOC.Encoder.pulseSum += ENCPULSEPERPOLE;
	else{}

	drvFOC.Encoder.Ftheta = drvFOC.Encoder.pulseSum * ENCTHETA_SCALE;

	if(drvFOC.Encoder.Ftheta > MT_2PAI)			drvFOC.Encoder.Ftheta = (drvFOC.Encoder.Ftheta - MT_2PAI);
	else if(drvFOC.Encoder.Ftheta < 0.0f)		drvFOC.Encoder.Ftheta = (drvFOC.Encoder.Ftheta + MT_2PAI);
	else{}

	drvFOC.Encoder.ThetaFdbComp = drvFOC.Encoder.Ftheta;

	drvFOC.Encoder.Pll.phase_error = sin(drvFOC.Encoder.ThetaFdbComp - drvFOC.Encoder.ThetaFdbComp_est);

	tmp0 = (drvFOC.Encoder.Pll.phase_error * drvFOC.Encoder.Pll.kp);
	drvFOC.Encoder.Pll.integ += (drvFOC.Encoder.Pll.phase_error * drvFOC.Encoder.Pll.ki * vEhalPwm_SamplingTime);

	drvFOC.Encoder.EncWe_est = (tmp0 + drvFOC.Encoder.Pll.integ);
//	LPF(drvFOC.Encoder.EncWeFil, drvFOC.Encoder.EncWe_est, drvFOC.lpf_gain.EncWeLpfFct);

	drvFOC.Encoder.ThetaFdbComp_est += (drvFOC.Encoder.EncWe_est * vEhalPwm_SamplingTime);

	if(drvFOC.Encoder.ThetaFdbComp_est > MT_2PAI)		drvFOC.Encoder.ThetaFdbComp_est = (drvFOC.Encoder.ThetaFdbComp_est - MT_2PAI);
	else if(drvFOC.Encoder.ThetaFdbComp_est < 0.0f)		drvFOC.Encoder.ThetaFdbComp_est = (drvFOC.Encoder.ThetaFdbComp_est + MT_2PAI);
	else{}

	drvFOC.Encoder.ThetaFdbComp_obs = drvFOC.Encoder.ThetaFdbComp_est + drvFOC.Encoder.Pll.phase_error;

	if(drvFOC.Encoder.ThetaFdbComp_obs > MT_2PAI)		drvFOC.Encoder.ThetaFdbComp_obs = (drvFOC.Encoder.ThetaFdbComp_obs - MT_2PAI);
	else if(drvFOC.Encoder.ThetaFdbComp_obs < 0.0f)		drvFOC.Encoder.ThetaFdbComp_obs = (drvFOC.Encoder.ThetaFdbComp_obs + MT_2PAI);
	else{}

	drvFOC.Encoder.EncSpeed = (drvFOC.Encoder.EncWe_est * WE2RPM);

	drvFOC.Encoder.EncValue_Old	= drvFOC.Encoder.EncValue;
	drvFOC.Encoder.Z_Pulse_Old	= drvFOC.Encoder.Z_Pulse;
	drvFOC.Encoder.Ftheta_Old		= drvFOC.Encoder.Ftheta;

	return(1);
}

char Meas_GetSpeed(void)
{
	drvFOC.Encoder.EncValue		= vBswTest_EncValue.EncA_Pulse;
	drvFOC.Encoder.EncDirection	= vBswTest_EncValue.EncA_Dir;

	if(drvFOC.Encoder.Z_Pulse == TRUE)
	{
		drvFOC.Encoder.Z_Pulse	= FALSE;

		if(drvFOC.Encoder.EncDirection == ENCODER_DIR_CCW)
		{
			if(drvFOC.Encoder.EncValue >= JJM_EncA_Pulse_I_Time)		Diff_I_Pulse_Diff_Cnt = drvFOC.Encoder.EncValue	- JJM_EncA_Pulse_I_Time;
			else														Diff_I_Pulse_Diff_Cnt = ((drvFOC.Encoder.EncValue - JJM_EncA_Pulse_I_Time) + 65535);
		}
		else
		{
			if(drvFOC.Encoder.EncValue <= JJM_EncA_Pulse_I_Time)		Diff_I_Pulse_Diff_Cnt = drvFOC.Encoder.EncValue	- JJM_EncA_Pulse_I_Time;
			else														Diff_I_Pulse_Diff_Cnt = ((drvFOC.Encoder.EncValue - JJM_EncA_Pulse_I_Time) - 65535);
		}

		drvFOC.Encoder.Z_Pulse	= FALSE;
		drvFOC.Encoder.pulseSum	= (ENCPULSEPERPOLE * ENCZPULSE_ANGLE * ENCZPOSITION_RATIO);
		drvFOC.Encoder.pulseSum = drvFOC.Encoder.pulseSum + Diff_I_Pulse_Diff_Cnt;
	}
	else
	{
		if(drvFOC.Encoder.EncValue != drvFOC.Encoder.EncValue_Old)
		{
			drvFOC.Encoder.Diff_Pulse = (((drvFOC.Encoder.EncValue - drvFOC.Encoder.EncValue_Old) << 16) >> 16);
			drvFOC.Encoder.pulseSum += drvFOC.Encoder.Diff_Pulse;
		}
		else{}
	}

	if(drvFOC.Encoder.pulseSum > ENCPULSEPERPOLE)			drvFOC.Encoder.pulseSum -= ENCPULSEPERPOLE;
	else if(drvFOC.Encoder.pulseSum < 0)					drvFOC.Encoder.pulseSum += ENCPULSEPERPOLE;
	else{}

	drvFOC.Encoder.Ftheta = drvFOC.Encoder.pulseSum * ENCTHETA_SCALE;

	if(drvFOC.Encoder.Ftheta > MT_2PAI)			drvFOC.Encoder.Ftheta = (drvFOC.Encoder.Ftheta - MT_2PAI);
	else if(drvFOC.Encoder.Ftheta < 0.0f)			drvFOC.Encoder.Ftheta = (drvFOC.Encoder.Ftheta + MT_2PAI);
	else{}

	drvFOC.Encoder.ThetaFdbComp = drvFOC.Encoder.Ftheta;

	if(drvFOC.Encoder.ThetaFdbComp > MT_2PAI)				JJM_CNT.tfE = drvFOC.Encoder.ThetaFdbComp;
	else if(drvFOC.Encoder.ThetaFdbComp < 0.0f)			JJM_CNT.tfE = drvFOC.Encoder.ThetaFdbComp;
	else{}

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
	drvFOC.Encoder.Ftheta_Old	= drvFOC.Encoder.Ftheta;

	return(1);
}

void stateCalib(void)
{
	float TMP0=0.0f,TMP1=0.0f;

	if((meas.flag.Angle_Cal == IN_PROGRESS) && (meas.flag.Current_Cal == PASS))
	{
		/* Encoder_Init */
		EhalGpt12_InitEncoder(0);
		drvFOC.Encoder.EncValue			= 0;
		drvFOC.Encoder.EncValue_Old		= 0;
		drvFOC.Encoder.Ftheta			= 0.;
		drvFOC.Encoder.Ftheta_Old		= 0.;
		drvFOC.Encoder.ThetaFdbComp		= 0.;
		drvFOC.Encoder.ThetaFdbComp_est	= 0.;
		drvFOC.Encoder.ThetaFdbComp_obs	= 0.;
		drvFOC.Encoder.EncWe			= 0.;
		drvFOC.Encoder.EncWe_est		= 0.;
		drvFOC.Encoder.EncWeFil			= 0.;
		drvFOC.Encoder.EncSpeed			= 0.;
		drvFOC.Encoder.pulseSum			= 0.;
		drvFOC.Encoder.Diff_Pulse		= 0.;
		drvFOC.Encoder.Diff_Ftheta		= 0.;

		TMP0						= ((float)(vBswTest_EncValue.EncA_Duty)/MT_DUTY_MAX);
//		drvFOC.Init_Position_Deg_E	= fmod(((MT_DEGREE - ((TMP0 - A1333_MIN_DUTY)/(A1333_MAX_DUTY - A1333_MIN_DUTY) * MT_DEGREE)) * MOTOR_PP) + ENCZPULSE_ANGLE,MT_DEGREE);
		drvFOC.Init_Position_Deg_E	= fmod(((MT_DEGREE - ((TMP0 - A1333_MIN_DUTY)/(A1333_MAX_DUTY - A1333_MIN_DUTY) * MT_DEGREE)) * MOTOR_PP) + 140.0f,MT_DEGREE);
		TMP1						= (drvFOC.Init_Position_Deg_E * TR_DEG2RAD);
		drvFOC.Encoder.pulseSum		= (TMP1 / MT_2PAI) * ENCPULSEPERPOLE;
		meas.flag.Angle_Cal			= PASS;
	}
	else{}
}

void Operating_SPEE_REF(void)
{
	if(MotControl.Speed_SpeedCMD != 0)
	{
		drvFOC.pospeControl.wRotElReq = (float)(MotControl.Speed_SpeedCMD);

		if(drvFOC.pospeControl.wRotElReq >= SPEED_REF_MAX)						drvFOC.pospeControl.wRotElReq = SPEED_REF_MAX;
		else if(drvFOC.pospeControl.wRotElReq <= SPEED_REF_MIN)					drvFOC.pospeControl.wRotElReq = SPEED_REF_MIN;
		else{}
	}
	else
	{
		drvFOC.pospeControl.wRotElReq = 0;
	}
}

void Vector_Control(void)
{
	if(MotControl.ContorlSensorMode == FORCED)
	{
		drvFOC.pospeControl.wRotEl	= (MotControl.Forced_SpeedCMD * RPM2WE);
		drvFOC.pospeControl.thRotEl += (drvFOC.pospeControl.wRotEl * vEhalPwm_SamplingTime);

		if(drvFOC.pospeControl.thRotEl > MT_2PAI) 			drvFOC.pospeControl.thRotEl -= MT_2PAI;
		else if(drvFOC.pospeControl.thRotEl < 0.) 			drvFOC.pospeControl.thRotEl += MT_2PAI;
		else{}
	}
	else if(MotControl.ContorlSensorMode == ENCODER)
	{
#ifdef SPEED_PLL
		drvFOC.pospeControl.thRotEl	= drvFOC.Encoder.ThetaFdbComp_obs;
#else
		drvFOC.pospeControl.thRotEl	= drvFOC.Encoder.ThetaFdbComp;
#endif
		drvFOC.pospeControl.wRotEl	= drvFOC.Encoder.EncSpeed;
		LPF(drvFOC.pospeControl.wRotElFilt, drvFOC.pospeControl.wRotEl, drvFOC.lpf_gain.SpeedLpfFct);

		/* Init */
		MotControl.Forced_SpeedCMD = 0.0;
	}
	else
	{
		MotControl.Forced_SpeedCMD		= 0.0;
		drvFOC.pospeControl.thRotEl		= 0.0;
		drvFOC.pospeControl.wRotEl		= 0.0;
		drvFOC.pospeControl.wRotElFilt	= 0.0;
	}

	if(MotControl.ControlMode == VECTOR_VOLTAGE)
	{
		drvFOC.uDQReq.tFArg1	= MotControl.Voltage_VdeCMD;
		drvFOC.uDQReq.tFArg2	= MotControl.Voltage_VqeCMD;

		Clark_Park_Transform();
		Inverse_Park_Transform();
	}
	else if(MotControl.ControlMode == VECTOR_CURRENT)
	{
		drvFOC.iDQReq.tFArg1	= MotControl.Current_IdeCMD;
		drvFOC.iDQReq.tFArg2	= MotControl.Current_IqeCMD;

		if(drvFOC.iDQReq.tFArg2 > 15.0)		drvFOC.iDQReq.tFArg2 = 15.0;
		else{}

		Clark_Park_Transform();
		focFastLoop();
	}
	else if(MotControl.ControlMode == VECTOR_SPEED)
	{
		if(MotControl.Speed_SpeedCMD != 0)
		{
			if (drvFOC.pospeControl.speedLoopCntr++ >= SPEED_LOOP_CNTR)			focSlowLoop();
			else{}

			Clark_Park_Transform();
			focFastLoop();
		}
		else
		{
			drvFOC.uAbcReq.tFArg1 = 0.0;
			drvFOC.uAbcReq.tFArg2 = 0.0;
			drvFOC.uAbcReq.tFArg3 = 0.0;
		}
	}
	else{}

	MIN_MAX_PWM();
}

void Vector_Control_Init(void)
{
	static uint8 tmp_F = FALSE;

	if(tmp_F == FALSE)
	{
		tmp_F = TRUE;

		vEhalDac_DacModule = TLV5614;

		// DEFINE_MODE_SET
		MotControl.ContorlSensorMode		= ENCODER;
		MotControl.ControlMode				= VECTOR_SPEED;

		// ACCELATION
		drvFOC.speedRamp.tFSlopeInc			= (2000.0 * (SPEED_LOOP_CNTR * vEhalPwm_SamplingTime));
		drvFOC.speedRamp.tFSlopeDec			= (2000.0 * (SPEED_LOOP_CNTR * vEhalPwm_SamplingTime));

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

		// PLL Observer
		drvFOC.Encoder.Pll.kp				= (CONS_2 * PLL_ZETA * MT_2PAI * PLL_Fcut);
		drvFOC.Encoder.Pll.ki				= (((MT_2PAI * PLL_Fcut) * (MT_2PAI * PLL_Fcut)) / CONS_2);

		//Filter_Gain
		FILFCT(VPHSET_CUTOFF,	drvFOC.lpf_gain.VphSetLpfFct,	vEhalPwm_FrequencyValue);
		FILFCT(ENCWE_CUTOFF,	drvFOC.lpf_gain.EncWeLpfFct,	vEhalPwm_FrequencyValue);
		FILFCT(SPD_CUTOFF,		drvFOC.lpf_gain.SpeedLpfFct,	vEhalPwm_FrequencyValue);
		FILFCT(IDC_CUTOFF,		drvFOC.lpf_gain.IdcLpfFct,		vEhalPwm_FrequencyValue);
	}
	else{}

	MotControl.Speed_SpeedCMD			= 0;
	MotControl.Forced_SpeedCMD			= 0.0;
	MotControl.Voltage_VdeCMD 			= 0.0;
	MotControl.Voltage_VqeCMD			= 0.0;
	MotControl.Current_IdeCMD			= 0.0;
	MotControl.Current_IqeCMD			= 0.0;

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
	drvFOC.Encoder.EncWe				= 0.;
	drvFOC.Encoder.EncWeFil				= 0.;
	drvFOC.Encoder.EncSpeed				= 0.;
	drvFOC.Encoder.Pll.phase_error		= 0.0f;
	drvFOC.Encoder.Pll.integ			= 0.0f;

	//5kHz
//	iir2_filter_setup(&stage1,0.19050441f, 0.38100882f, 0.19050441f,0.4129187f, 0.07900857f);
//	iir2_filter_setup(&stage2,1.0f, 2.0f, 1.0f,0.56545007f, 0.47759225f);

	if(meas.flag.Angle_Cal == IN_PROGRESS)		stateCalib();
	else{}
}

void Simply_MotorContorl(void)
{
	static char getFcnStatus;

	if((meas.flag.Current_Cal == PASS) && (meas.flag.Angle_Cal == PASS))
	{
		Meas_Voltage_Current();
#ifdef SPEED_PLL
		Meas_GetSpeed_Pll();
#else
		Meas_GetSpeed();
#endif

		getFcnStatus = faultDetection();

		if(getFcnStatus == TRUE)
		{
			fault_Log ++;
			vBswTest_Pwm_Enable_Mode	= PWM_3PH_DISABLE;
			MotControl.Speed_SpeedCMD	= 0;
			Vector_Control_Init();
		}
		else
		{
			Operating_SPEE_REF();

			if(vBswTest_Pwm_Enable_Mode == PWM_3PH_DISABLE)
			{
				MotControl.Speed_SpeedCMD = 0;
				Vector_Control_Init();
			}
			else
			{
				Vector_Control();
			}
		}
	}
	else
	{
		Vector_Control_Init();
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
