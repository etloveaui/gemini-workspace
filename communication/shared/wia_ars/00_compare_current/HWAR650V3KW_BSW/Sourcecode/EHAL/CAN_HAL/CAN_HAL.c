/*
 * CAN_HAL.c
 *
 *  Created on: 2017. 4. 19.
 *      Author:
 */

#include "CDrv/CDrvIfc/Flashing_PFlash.h"
#include "EHAL/CAN_HAL/CAN_HAL.h"
#include "EHAL/EhalAdc/EhalAdc.h"
#include "EHAL/TLF35584_HAL/TLF35584.h"
#include "TSW/Tsw.h"
#include "EhalPwm.h"
#include "IswHandler.h"
#include "CanSM.h"
#include "EhalSys.h"
#include "CanIf_Cbk.h"

//FBL
typCanMsg_VCU6_FRAME vCanMsg_VCU6_FRAME;
typCanMsg_SCU6 vCanMsg_SCU6;
// Rx
typCanMsg_MVPC1_FRAME vCanMsg_MVPC1_FRAME;
typCanMsg_RT1_10_FRAME vCanMsg_RT1_10_FRAME;
typCanMsg_RT1_20_FRAME vCanMsg_RT1_20_FRAME;
typCanMsg_RT1_200_FRAME vCanMsg_RT1_200_FRAME;
typCanMsg_RMT_CMD_FRAME vCanMsg_RMT_CMD_FRAME;
// Tx
typCanMsg_ARS1 vCanMsg_ARS1;
// 2025. 6. 13. etkim - removed
//typCanMsg_ARS2 vCanMsg_ARS2;
//typCanMsg_ARS3 vCanMsg_ARS3;
//typCanMsg_ARS4 vCanMsg_ARS4;
typCanMsg_RMT_RES vCanMsg_RMT_RES;
typCanMsg_MEAS32 vCanMsg_MEAS_1MS;
typCanMsg_MEAS32 vCanMsg_MEAS_5MS_A;
typCanMsg_MEAS32 vCanMsg_MEAS_5MS_B;
typCanMsg_MEAS32 vCanMsg_MEAS_10MS_A;
typCanMsg_MEAS32 vCanMsg_MEAS_10MS_B;

/*
 * CH0 MEAS CANTx Enable Flag
 * 1U = Tx ON (DEFAULT), 0U = Tx OFF
 */
static volatile uint8 vEhalCan_Can0MeasTxEnable = 1U;
uint8 vEhalCan1_BusoffCtrl;


//uint8 vEhalCan_Can0_BusOffState; // Bus Off Recovery
//uint8 vEhalCan_Can1_BusOffState; // Bus Off Recovery

#define CANIF_ID_FD_MASK				(uint32)(0x40000000U)
#define CANIF_ID_EXTENDED_MASK			(uint32)(0x80000000U)

// Define CAN Controller IDs
#define CAN_0	(Can_17_McmCanConf_CanController_Can_Network_CANNODE_0)
#define CAN_1	(Can_17_McmCanConf_CanController_Can_Network_CANNODE_1)

typedef enum {
	CAN0_MSG_TX_INDEX_MEAS_1MS = 0U,
	CAN0_MSG_TX_INDEX_MEAS_5MS_A,
	CAN0_MSG_TX_INDEX_MEAS_5MS_B,
	CAN0_MSG_TX_INDEX_MEAS_10MS_A,
	CAN0_MSG_TX_INDEX_MEAS_10MS_B,
	CAN1_MSG_TX_INDEX_ARS1,
	CAN1_MSG_TX_INDEX_RMT_RES,
	CAN_MSG_TX_INDEX_MAX
} typCanMsg_TX_Index;


#define CAN0_ID_MEAS_1MS			(CANIF_ID_FD_MASK|0x401)		//TX
#define CAN0_ID_MEAS_5MS_A			(CANIF_ID_FD_MASK|0x402)		//TX
#define CAN0_ID_MEAS_5MS_B			(CANIF_ID_FD_MASK|0x403)		//TX
#define CAN0_ID_MEAS_10MS_A			(CANIF_ID_FD_MASK|0x404)		//TX
#define CAN0_ID_MEAS_10MS_B			(CANIF_ID_FD_MASK|0x405)		//TX

//2025.01.22
//#define CAN1_ID_VPC1			(CANIF_ID_FD_MASK|0x51C)	//RX
//#define CAN1_ID_SEA1			(CANIF_ID_FD_MASK|0x51A)	//RX
//#define CAN1_ID_SEA2			(CANIF_ID_FD_MASK|0x51B)	//RX

#define CAN1_ID_MVPC1			(CANIF_ID_FD_MASK|0x20)		//RX
#define CAN1_ID_RT1_10			(CANIF_ID_FD_MASK|0x27)		//RX
#define CAN1_ID_RT1_20			(CANIF_ID_FD_MASK|0x26)		//RX
#define CAN1_ID_RT1_200			(CANIF_ID_FD_MASK|0x25)		//RX

//#define CAN1_RX_TIMEOUT_MAX_VPC1		(100U) // 10ms * 100 = 1000ms
//#define CAN1_RX_TIMEOUT_MAX_SEA1		(100U) // 1ms * 100 = 100ms
//#define CAN1_RX_TIMEOUT_MAX_SEA2		(100U) // 1ms * 100 = 100ms

#define CAN1_ID_ARS1_F			(CANIF_ID_FD_MASK|0x21) // 0x514 -> 0x515 -> 0x21 / 2025.04.01, Front 2025.06.06, 2025.06.16

// 2025. 6. 13. etkim - removed
//#define CAN1_ID_ARS2_F			(CANIF_ID_FD_MASK|0x514) // 0x515 ->0x514 2025.04.01, Front 2025.06.06
//#define CAN1_ID_ARS3_F			(CANIF_ID_FD_MASK|0x516) // Front 2025.06.06
//#define CAN1_ID_ARS4_F			(CANIF_ID_FD_MASK|0x517) // Front 2025.06.06

#define CAN1_ID_ARS1_R			(CANIF_ID_FD_MASK|0x22) // 0x511 -> 0x22 / Rear 2025.06.06, 2025.06.16

// 2025. 6. 13. etkim - removed
//#define CAN1_ID_ARS2_R			(CANIF_ID_FD_MASK|0x510) // Rear 2025.06.06
//#define CAN1_ID_ARS3_R			(CANIF_ID_FD_MASK|0x512) // Rear 2025.06.06
//#define CAN1_ID_ARS4_R			(CANIF_ID_FD_MASK|0x513) // Rear 2025.06.06

//GINT internal test
#define CAN1_ID_RMT_CMD			(CANIF_ID_FD_MASK|0x7A1)	//RX
#define CAN1_ID_RMT_RES			(CANIF_ID_FD_MASK|0x7A4)	//TX
#define CAN0_ID_REPROGRAM_CMD	(CANIF_ID_FD_MASK|0x0F0)	//RX

//Can_MsgObjCanId_t Can_MsgObj_CanId[] =
//{// MCAL_CanObjectId(HthIdx) / CanCtrlId / CanId / SW Ordered Number(PDU ID) / Can Data Length
//		{ARS1_CAN1_TX, 		CAN_1, 		CAN1_ID_ARS1, 			ARS1_CAN1_TX,			32},   	// TX : CAN_ID_ARS1 0x514
//		{ARS2_CAN1_TX, 		CAN_1, 		CAN1_ID_ARS2, 			ARS2_CAN1_TX,			8},   	// TX : CAN_ID_ARS2 0x515
//		{ARS3_CAN1_TX, 		CAN_1, 		CAN1_ID_ARS3, 			ARS3_CAN1_TX,			8},   	// TX : CAN_ID_ARS3 0x516
//		{ARS4_CAN1_TX, 		CAN_1, 		CAN1_ID_ARS4, 			ARS4_CAN1_TX,			24},  	// TX : CAN_ID_ARS4 0x517
//		{RMT_RES_CAN1_TX, 	CAN_1, 		CAN1_ID_RMT_RES, 		RMT_RES_CAN1_TX,		8},		// TX : CAN_ID_RMT_RES 0x7A4
//};

Can_MsgObjCanId_t Can_MsgObj_CanIdFront[] =
{// MCAL_CanObjectId(HthIdx, Mailbox) / CanCtrlId / CanId / Can Data Length / pSdu
		{MEAS_1MS_CAN0_TX,				CAN_0, 		CAN0_ID_MEAS_1MS,		32,		vCanMsg_MEAS_1MS.byte},   	// TX : MEAS_1MS_CAN0_TX 0x401
		{MEAS_5MS_A_CAN0_TX,			CAN_0, 		CAN0_ID_MEAS_5MS_A,		32,		vCanMsg_MEAS_5MS_A.byte},   	// TX : MEAS_5MS_A_CAN0_TX 0x402
		{MEAS_5MS_B_CAN0_TX,			CAN_0, 		CAN0_ID_MEAS_5MS_B,		32,		vCanMsg_MEAS_5MS_B.byte},   	// TX : MEAS_5MS_B_CAN0_TX 0x403
		{MEAS_10MS_A_CAN0_TX,			CAN_0, 		CAN0_ID_MEAS_10MS_A,	32,		vCanMsg_MEAS_10MS_A.byte},   	// TX : MEAS_10MS_A_CAN0_TX 0x404
		{MEAS_10MS_B_CAN0_TX,			CAN_0, 		CAN0_ID_MEAS_10MS_B,	32,		vCanMsg_MEAS_10MS_B.byte},   	// TX : MEAS_10MS_B_CAN0_TX 0x405
		{ARS1_CAN1_TX,					CAN_1, 		CAN1_ID_ARS1_F,			16,		vCanMsg_ARS1.byte},   	// TX : CAN_ID_ARS1 0x514
		{RMT_RES_CAN1_TX,				CAN_1,		CAN1_ID_RMT_RES,		8,		vCanMsg_RMT_RES.byte},	// TX : CAN_ID_RMT_RES 0x7A4
};

Can_MsgObjCanId_t Can_MsgObj_CanIdRear[] =
{// MCAL_CanObjectId(HthIdx, Mailbox) / CanCtrlId / CanId / Can Data Length / pSdu
		{MEAS_1MS_CAN0_TX,				CAN_0, 		CAN0_ID_MEAS_1MS,		32,		vCanMsg_MEAS_1MS.byte},   	// TX : MEAS_1MS_CAN0_TX 0x401
		{MEAS_5MS_A_CAN0_TX,			CAN_0, 		CAN0_ID_MEAS_5MS_A,		32,		vCanMsg_MEAS_5MS_A.byte},   	// TX : MEAS_5MS_A_CAN0_TX 0x402
		{MEAS_5MS_B_CAN0_TX,			CAN_0, 		CAN0_ID_MEAS_5MS_B,		32,		vCanMsg_MEAS_5MS_B.byte},   	// TX : MEAS_5MS_B_CAN0_TX 0x403
		{MEAS_10MS_A_CAN0_TX,			CAN_0, 		CAN0_ID_MEAS_10MS_A,	32,		vCanMsg_MEAS_10MS_A.byte},   	// TX : MEAS_10MS_A_CAN0_TX 0x404
		{MEAS_10MS_B_CAN0_TX,			CAN_0, 		CAN0_ID_MEAS_10MS_B,	32,		vCanMsg_MEAS_10MS_B.byte},   	// TX : MEAS_10MS_B_CAN0_TX 0x405
		{ARS1_CAN1_TX,					CAN_1, 		CAN1_ID_ARS1_R,			16,		vCanMsg_ARS1.byte},   	// TX : CAN_ID_ARS1 0x514
		{RMT_RES_CAN1_TX,				CAN_1,		CAN1_ID_RMT_RES,		8,		vCanMsg_RMT_RES.byte},	// TX : CAN_ID_RMT_RES 0x7A4
};

//2025.01.22 before
//#define CAN_ID_VPC1		(CANIF_ID_FD_MASK|0x211)
//#define CAN_ID_SEA1		(CANIF_ID_FD_MASK|0x321)
//#define CAN_ID_ARS1		(CANIF_ID_FD_MASK|0x431)
//#define CAN_ID_ARS2		(CANIF_ID_FD_MASK|0x432)
//#define CAN_ID_ARS3		(CANIF_ID_FD_MASK|0x433)

extern CanSM_BusOffRecoveryStateType_ten CanSM_currBOR_State_en[1];
static uint8 vEhalCan_Can1BusOffState = 0U;

uint8 EhalCan_IsBusoff(uint8 can_ch)
{
	uint8 flag = 0;

	switch(can_ch){
	case 0:
		if(CanSM_currBOR_State_en[0]==CANSM_S_NO_BUS_OFF){
			flag = 0;
		}
		else{
			flag = 1;
		}
		break;
	case 1:
		//		flag = MODULE_CAN1.N[0].PSR.B.BO;
		//		if(flag == 1){
		//			MODULE_CAN1.N[0].CCCR.B.INIT = 0;
		//		}
		//		else{
		//			//no action
		//		}
		flag = vEhalCan_Can1BusOffState;
		break;
	default:
		flag = 0;
		break;
	}
	return flag;
}
uint32 vteste;
void EhalCan1_BusOffRecovery_Task(void)
{
	vEhalCan_Can1BusOffState = MODULE_CAN1.N[0].PSR.B.BO ;
	if (MODULE_CAN1.N[0].PSR.B.BO == 1){
		Can_17_McmCan_SetControllerMode (CAN_1, CAN_T_START);
	}
	else{
		//no action
	}
}

static inline boolean EhalCan_IsCh0MeasIndex(uint8 idx)
{
	return ( (idx >= CAN0_MSG_TX_INDEX_MEAS_1MS) &&
			(idx <= CAN0_MSG_TX_INDEX_MEAS_10MS_B) );
}

void EhalCan_Init(void)
{
	Can_17_McmCan_SetControllerMode (CAN_1, CAN_T_START);
	Can_17_McmCan_EnableControllerInterrupts(CAN_1);

	vCanMsg_MVPC1_FRAME.timeout_max = 100;
	vCanMsg_RT1_10_FRAME.timeout_max = 1000;
	vCanMsg_RT1_20_FRAME.timeout_max = 1000;
	vCanMsg_RT1_200_FRAME.timeout_max = 50;
}

static void CAN_HAL_CheckSingleTimeout(uint32* count, uint32* count_prev,
		uint8* timeout_flag, uint32* timeout_cnt,
		uint32* timeout_max)
{
	if(*count == *count_prev){
		// No Rx msg
		if(*timeout_flag == 0U){
			(*timeout_cnt)++;
			if(*timeout_cnt >= *timeout_max){
				*timeout_flag = 1U;
			}
			else{
				// no action
			}
		}
		else{
			// no action
		}
	}
	else{
		*count_prev = *count;
		*timeout_flag = 0U;
		*timeout_cnt = 0U;
	}
}

void CAN_HAL_TimeoutCheck_1ms_Task(void)
{
	CAN_HAL_CheckSingleTimeout(&vCanMsg_MVPC1_FRAME.count,
			&vCanMsg_MVPC1_FRAME.count_prev,
			&vCanMsg_MVPC1_FRAME.timeout_flag,
			&vCanMsg_MVPC1_FRAME.timeout_cnt,
			&vCanMsg_MVPC1_FRAME.timeout_max);
}

void CAN_HAL_TimeoutCheck_10ms_Task(void)
{
	CAN_HAL_CheckSingleTimeout(&vCanMsg_RT1_10_FRAME.count,
			&vCanMsg_RT1_10_FRAME.count_prev,
			&vCanMsg_RT1_10_FRAME.timeout_flag,
			&vCanMsg_RT1_10_FRAME.timeout_cnt,
			&vCanMsg_RT1_10_FRAME.timeout_max);
}

void CAN_HAL_TimeoutCheck_20ms_Task(void)
{
	CAN_HAL_CheckSingleTimeout(&vCanMsg_RT1_20_FRAME.count,
			&vCanMsg_RT1_20_FRAME.count_prev,
			&vCanMsg_RT1_20_FRAME.timeout_flag,
			&vCanMsg_RT1_20_FRAME.timeout_cnt,
			&vCanMsg_RT1_20_FRAME.timeout_max);
}

void CAN_HAL_TimeoutCheck_200ms_Task(void)
{
	CAN_HAL_CheckSingleTimeout(&vCanMsg_RT1_200_FRAME.count,
			&vCanMsg_RT1_200_FRAME.count_prev,
			&vCanMsg_RT1_200_FRAME.timeout_flag,
			&vCanMsg_RT1_200_FRAME.timeout_cnt,
			&vCanMsg_RT1_200_FRAME.timeout_max);
}

void CAN_HAL_RxIndication(uint16 Hrh, uint32 CanId, uint8 CanDlc, const uint8 *CanSduPtr)
{
	uint8 i;

	if(CanId == CAN1_ID_MVPC1){
		vCanMsg_MVPC1_FRAME.count++;
		vCanMsg_MVPC1_FRAME.new_flag = TRUE;
		vCanMsg_MVPC1_FRAME.CanId = CanId;
		vCanMsg_MVPC1_FRAME.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_MVPC1_FRAME.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN1_ID_RT1_10){
		vCanMsg_RT1_10_FRAME.count++;
		vCanMsg_RT1_10_FRAME.new_flag = TRUE;
		vCanMsg_RT1_10_FRAME.CanId = CanId;
		vCanMsg_RT1_10_FRAME.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_RT1_10_FRAME.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN1_ID_RT1_20){
		vCanMsg_RT1_20_FRAME.count++;
		vCanMsg_RT1_20_FRAME.new_flag = TRUE;
		vCanMsg_RT1_20_FRAME.CanId = CanId;
		vCanMsg_RT1_20_FRAME.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_RT1_20_FRAME.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN1_ID_RT1_200){
		vCanMsg_RT1_200_FRAME.count++;
		vCanMsg_RT1_200_FRAME.new_flag = TRUE;
		vCanMsg_RT1_200_FRAME.CanId = CanId;
		vCanMsg_RT1_200_FRAME.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_RT1_200_FRAME.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN1_ID_RMT_CMD){

		vCanMsg_RMT_CMD_FRAME.count++;
		vCanMsg_RMT_CMD_FRAME.new_flag = TRUE;
		vCanMsg_RMT_CMD_FRAME.CanId = CanId;
		vCanMsg_RMT_CMD_FRAME.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_RMT_CMD_FRAME.Msg.byte[i] = CanSduPtr[i];
		}
	}
	//	FBL
	else if(CanId == CAN0_ID_REPROGRAM_CMD){
		//Repro_CAN_0xF0_Isr(CanSduPtr);
		vCanMsg_VCU6_FRAME.count++;
		vCanMsg_VCU6_FRAME.new_flag = TRUE;
		vCanMsg_VCU6_FRAME.CanId = CanId;
		vCanMsg_VCU6_FRAME.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_VCU6_FRAME.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else{
		//do nothing
	}
}

void CAN_HAL_TxMsg(uint8 msg_index)
{
	Can_PduType Can_pdu;
	Can_MsgObjCanId_t *obj;

	if((EhalCan_IsCh0MeasIndex(msg_index) != FALSE) && (vEhalCan_Can0MeasTxEnable == 0U) ){
		return;
	}
	else{
		//no action
	}

	if(vBswSys_TargetAxle == BSWSYS_TARGET_AXLE_FRONT){
		obj = &Can_MsgObj_CanIdFront[msg_index];
		if(msg_index<CAN_MSG_TX_INDEX_MAX){
			if (EhalCan_IsBusoff(obj->CanCtrlId)) {
				return;
			}
			Can_pdu.swPduHandle = (PduIdType)obj->HthIdx;
			Can_pdu.id = obj->CanId;
			Can_pdu.length = obj->CanDlc;
			Can_pdu.sdu = obj->pSdu;
			(void)Can_17_McmCan_Write(Can_MsgObj_CanIdFront[msg_index].HthIdx, &Can_pdu) ;
		}
		else{
			return;
		}
	}
	else if(vBswSys_TargetAxle == BSWSYS_TARGET_AXLE_REAR){
		obj = &Can_MsgObj_CanIdRear[msg_index];
		if(msg_index<CAN_MSG_TX_INDEX_MAX){
			if (EhalCan_IsBusoff(obj->CanCtrlId)) {
				return;
			}
			Can_pdu.swPduHandle = (PduIdType)obj->HthIdx;
			Can_pdu.id = obj->CanId;
			Can_pdu.length = obj->CanDlc;
			Can_pdu.sdu = obj->pSdu;
			(void)Can_17_McmCan_Write(Can_MsgObj_CanIdRear[msg_index].HthIdx, &Can_pdu) ;
		}
		else{
			return;
		}
	}
	else{ //undefined
		//do nothing
	}
}

void EhalCan_SetCh0TxEnable(uint8 enable)
{
	vEhalCan_Can0MeasTxEnable = enable;
}

void EhalCan_Task_1ms(void)
{
	CAN_HAL_TxMsg(CAN1_MSG_TX_INDEX_ARS1);
	CAN_HAL_TimeoutCheck_1ms_Task();

	CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_MEAS_1MS);
}

void EhalCan_Task_5ms(void)
{
	CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_MEAS_5MS_A);
	CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_MEAS_5MS_B);
}

void EhalCan_Task_10ms_3(void)
{
	;
}

void EhalCan_Task_10ms_5(void)
{
	//	CAN_HAL_TxMsg(CAN1_MSG_TX_INDEX_ARS3);	// 2025. 6. 13. etkim - removed
	if(vCanMsg_RMT_CMD_FRAME.Msg.signal.TEST_EN == 1){
		//			CAN_HAL_TxMsg(CAN1_MSG_TX_INDEX_RMT_RES, &vCanMsg_RMT_RES.byte[0]);
		CAN_HAL_TxMsg(CAN1_MSG_TX_INDEX_RMT_RES);
	}
	else{
		//no action
	}

	CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_MEAS_10MS_A);
	CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_MEAS_10MS_B);
}

void EhalCan_Task_10ms_7(void)
{
	//	CAN_HAL_TxMsg(CAN1_MSG_TX_INDEX_ARS4);	// 2025. 6. 13. etkim - removed
	CAN_HAL_TimeoutCheck_10ms_Task();
}

void EhalCan_Task_20ms(void)
{
	CAN_HAL_TimeoutCheck_20ms_Task();
}

void EhalCan_Task_100ms(void)
{
	EhalCan1_BusOffRecovery_Task();
}

void EhalCan_Task_200ms(void)
{
	CAN_HAL_TimeoutCheck_200ms_Task();
	//	EhalCan1_BusOffRecovery_Task();
}

void EhalCan_Task_500ms(void)
{
	;
}

void EhalCan_Task_1000ms(void)
{
	//	EhalCan1_BusOffRecovery_Task();
}
