/*
 * CAN_HAL.c
 *
 *  Created on: 2017. 4. 19.
 *      Author:
 */

//#include "BSW_System.h"
//#include <EHAL/A1333_HAL/A1333.h>
#include "CDrv/CDrvIfc/Flashing_PFlash.h"
#include "EHAL/CAN_HAL/CAN_HAL.h"
#include "EHAL/EhalAdc/EhalAdc.h"
#include "EHAL/TLF35584_HAL/TLF35584.h"
//#include "EHAL/A4918_HAL/A4918_HAL_spi.h"
#include "TSW/Tsw.h"
#include "EhalPwm.h"
#include "IswHandler.h"
#include "CanSM.h"

//#include "integration/MCAL/api/Can_GeneralTypes.h"
//#include "mcal/MCAL_Gen/inc/Can_17_MCanP_Cfg.h"
//#include "mcal/MCAL_Modules/Can/inc/Can_17_MCanP.h"


//typCanMsg_FAULTS_Infor SCU2;
//typCanMsg_MOT_Infor SCU3;


typCanMsg_VCU6_FRAME vCanMsg_VCU6_FRAME;
typCanMsg_SCU6 vCanMsg_SCU6;

typCanMsg_VPC1_FRAME vCanMsg_VPC1_FRAME; // Rx
typCanMsg_SEA1_FRAME vCanMsg_SEA1_FRAME; // Rx
typCanMsg_SEA2_FRAME vCanMsg_SEA2_FRAME; // Rx
typCanMsg_RMT_CMD_FRAME vCanMsg_RMT_CMD_FRAME;

typCanMsg_ARS1 vCanMsg_ARS1; // Tx
typCanMsg_ARS2 vCanMsg_ARS2; // Tx
typCanMsg_ARS3 vCanMsg_ARS3; // Tx
typCanMsg_ARS4 vCanMsg_ARS4; // Tx
typCanMsg_RMT_RES vCanMsg_RMT_RES;

uint8 vEhalCan_Can0_BusOffState; // Bus Off Recovery

//typedef union{
//	uint8 byte[8];
//	struct{
//		sint16 WheelAngleEncoder; // 0.01[deg]
//		uint16 unused3;
//		uint16 unused2;
//		uint16 unused1;
//	}signal;
//}typCanMsg_ADT_WHEEL_ANGLE;
//typCanMsg_ADT_WHEEL_ANGLE vCanMsg_ADT_WHEEL_ANGLE;


#define CANIF_ID_FD_MASK				(uint32)(0x40000000U)
#define CANIF_ID_EXTENDED_MASK			(uint32)(0x80000000U)


// Define CAN Controller IDs
#define CAN_0	(Can_17_McmCanConf_CanController_Can_Network_CANNODE_0)
#define CAN_1	(Can_17_McmCanConf_CanController_Can_Network_CANNODE_1)
//#define CAN_2	(2)
//#define CAN_3	(3)


typedef enum {
	CAN0_MSG_RX_INDEX_VPC1 = 0U,
	CAN0_MSG_RX_INDEX_SEA1,
	CAN0_MSG_RX_INDEX_SEA2,
	CAN0_MSG_RX_INDEX_RMT_CMD,
	CAN0_MSG_RX_INDEX_MAILBOX15,
	CAN1_MSG_RX_INDEX_MAILBOX1,
	CAN1_MSG_RX_INDEX_MAILBOX2,
	CAN1_MSG_RX_INDEX_MAILBOX14,
	CAN1_MSG_RX_INDEX_MAILBOX15,
	CAN_MSG_RX_INDEX_MAX
} typCanMsg_RX_Index;

typedef enum {
	CAN0_MSG_TX_INDEX_ARS1 = 0U,
	CAN0_MSG_TX_INDEX_ARS2,
	CAN0_MSG_TX_INDEX_ARS3,
	CAN0_MSG_TX_INDEX_ARS4,
	CAN0_MSG_TX_INDEX_RMT_RES,
	CAN0_MSG_TX_INDEX_MAILBOX14,
	CAN0_MSG_TX_INDEX_MAILBOX15,
	CAN1_MSG_TX_INDEX_MAILBOX1,
	CAN1_MSG_TX_INDEX_MAILBOX2,
	CAN1_MSG_TX_INDEX_MAILBOX14,
	CAN1_MSG_TX_INDEX_MAILBOX15,
	CAN_MSG_TX_INDEX_MAX
} typCanMsg_TX_Index;


//#define CAN0_MSG_RX_INDEX_VPC1		(0U)
//#define CAN0_MSG_RX_INDEX_SEA1		(1U)
//#define CAN0_MSG_RX_INDEX_RMT_CMD	(2U)
//#define DUMMY_CAN0_RX_MAILBOX15		(3U)
//#define CAN1_MSG_RX_INDEX_MAILBOX1	(4U)
//#define CAN1_MSG_RX_INDEX_MAILBOX2	(5U)
//#define CAN_MSG_RX_INDEX_MAX		(6U)
//
//#define CAN0_MSG_TX_INDEX_ARS1		(0U)
//#define CAN0_MSG_TX_INDEX_ARS2		(1U)
//#define CAN0_MSG_TX_INDEX_ARS3		(2U)
//#define CAN0_MSG_TX_INDEX_RMT_RES	(3U)
//#define CAN1_MSG_TX_INDEX_TEST1		(4U)
//#define CAN1_MSG_TX_INDEX_TEST2		(5U)
//#define CAN_MSG_TX_INDEX_MAX		(6U)

//2025.01.22
#define CAN0_ID_VPC1			(CANIF_ID_FD_MASK|0x51C)
#define CAN0_ID_SEA1			(CANIF_ID_FD_MASK|0x51A)
#define CAN0_ID_SEA2			(CANIF_ID_FD_MASK|0x51B)
#define CAN0_ID_ARS1			(CANIF_ID_FD_MASK|0x515) // 0x514 ->0x515 2025.04.01
#define CAN0_ID_ARS2			(CANIF_ID_FD_MASK|0x514) // 0x515 ->0x514 2025.04.01
#define CAN0_ID_ARS3			(CANIF_ID_FD_MASK|0x516)
#define CAN0_ID_ARS4			(CANIF_ID_FD_MASK|0x517)

//GINT internal test
#define CAN0_ID_RMT_CMD			(CANIF_ID_FD_MASK|0x7A1)
#define CAN0_ID_RMT_RES			(CANIF_ID_FD_MASK|0x7A4)
#define CAN0_ID_REPROGRAM_CMD	(CANIF_ID_FD_MASK|0x0F0)

// RX TEST
#define CAN0_ID_RX_MAILBOX15	(CANIF_ID_FD_MASK|0x10F)
#define CAN1_ID_RX_MAILBOX1		(CANIF_ID_FD_MASK|0x201)
#define CAN1_ID_RX_MAILBOX2		(CANIF_ID_FD_MASK|0x202)
#define CAN1_ID_RX_MAILBOX14	(CANIF_ID_FD_MASK|0x20E)
#define CAN1_ID_RX_MAILBOX15	(CANIF_ID_FD_MASK|0x20F)

// TX TEST
#define CAN0_ID_TX_MAILBOX14	(CANIF_ID_FD_MASK|0x11E)
#define CAN0_ID_TX_MAILBOX15	(CANIF_ID_FD_MASK|0x11F)
#define CAN1_ID_TX_MAILBOX1		(CANIF_ID_FD_MASK|0x211)
#define CAN1_ID_TX_MAILBOX2		(CANIF_ID_FD_MASK|0x212)
#define CAN1_ID_TX_MAILBOX14	(CANIF_ID_FD_MASK|0x21E)
#define CAN1_ID_TX_MAILBOX15	(CANIF_ID_FD_MASK|0x21F)

typCanMsg_RX_TEST1_FRAME vCanMsg_CAN1_RX_MAILBOX1;		//8byte
typCanMsg_RX_TEST2_FRAME vCanMsg_CAN1_RX_MAILBOX2;		//32byte
typCanMsg_RX_TEST1_FRAME vCanMsg_CAN0_RX_MAILBOX15;		//8byte
typCanMsg_RX_TEST2_FRAME vCanMsg_CAN1_RX_MAILBOX14;		//32byte
typCanMsg_RX_TEST1_FRAME vCanMsg_CAN1_RX_MAILBOX15;		//8byte

typCanMsg_TEST1 vCanMsg_CAN1_TX_MAILBOX1;				//8byte
typCanMsg_TEST2 vCanMsg_CAN1_TX_MAILBOX2;				//32byte
typCanMsg_TEST1 vCanMsg_CAN0_TX_MAILBOX14;				//8byte
typCanMsg_TEST2 vCanMsg_CAN0_TX_MAILBOX15;				//32byte
typCanMsg_TEST1 vCanMsg_CAN1_TX_MAILBOX14;				//8byte
typCanMsg_TEST2 vCanMsg_CAN1_TX_MAILBOX15;				//32byte

Can_MsgObjCanId_t Can_MsgObj_CanId[] =
{// MCAL_CanObjectId(HthIdx) / CanCtrlId / CanId / SW Ordered Number(PDU ID)
		{ARS1_CAN0_TX_MAILBOX3, 		CAN_0, 		CAN0_ID_ARS1, 			ARS1_CAN0_TX_MAILBOX3},   	// TX : CAN_ID_ARS1 0x514
		{ARS2_CAN0_TX_MAILBOX6, 		CAN_0, 		CAN0_ID_ARS2, 			ARS2_CAN0_TX_MAILBOX6},   	// TX : CAN_ID_ARS2 0x515
		{ARS3_CAN0_TX_MAILBOX2, 		CAN_0, 		CAN0_ID_ARS3, 			ARS3_CAN0_TX_MAILBOX2},   	// TX : CAN_ID_ARS3 0x516
		{ARS4_CAN0_TX_MAILBOX9, 		CAN_0, 		CAN0_ID_ARS4, 			ARS4_CAN0_TX_MAILBOX9},  	// TX : CAN0_ID_TX_MAILBOX14 0x11E
		{RMT_RES_CAN0_TX_MAILBOX5, 		CAN_0, 		CAN0_ID_RMT_RES, 		RMT_RES_CAN0_TX_MAILBOX5},	// TX : CAN_ID_RMT_RES 0x7A4
		{DUMMY_CAN0_TX_MAILBOX15, 		CAN_0, 		CAN0_ID_TX_MAILBOX15, 	DUMMY_CAN0_TX_MAILBOX15},  	// TX : CAN0_ID_TX_MAILBOX15 0x11F
		{DUMMY_CAN1_TX_MAILBOX1, 		CAN_1, 		CAN1_ID_TX_MAILBOX1, 	DUMMY_CAN1_TX_MAILBOX1},  	// TX : CAN1_ID_TX_MAILBOX1 0x211
		{DUMMY_CAN1_TX_MAILBOX2, 		CAN_1, 		CAN1_ID_TX_MAILBOX2, 	DUMMY_CAN1_TX_MAILBOX2},  	// TX : CAN1_ID_TX_MAILBOX2 0x212
		{DUMMY_CAN1_TX_MAILBOX14, 		CAN_1, 		CAN1_ID_TX_MAILBOX14, 	DUMMY_CAN1_TX_MAILBOX14},  	// TX : CAN1_ID_TX_MAILBOX14 0x21E
		{DUMMY_CAN1_TX_MAILBOX15, 		CAN_1, 		CAN1_ID_TX_MAILBOX15, 	DUMMY_CAN1_TX_MAILBOX15},  	// TX : CAN1_ID_TX_MAILBOX15 0x21F
};

//2025.01.22 before
//#define CAN_ID_VPC1		(CANIF_ID_FD_MASK|0x211)
//#define CAN_ID_SEA1		(CANIF_ID_FD_MASK|0x321)
//#define CAN_ID_ARS1		(CANIF_ID_FD_MASK|0x431)
//#define CAN_ID_ARS2		(CANIF_ID_FD_MASK|0x432)
//#define CAN_ID_ARS3		(CANIF_ID_FD_MASK|0x433)

uint8 EhalCan_IsBusoff(uint8 can_ch)
{
	uint8 bus_off_state;

	switch(can_ch){
	case 0:
		//		bus_off_state = MODULE_CAN0.N[0].PSR.B.BO;
		bus_off_state = vEhalCan_Can0_BusOffState;
		break;
	default:
		bus_off_state = 0;
		break;
	}
	return bus_off_state;
}

void EhalCan_Init(void)
{
	Can_17_McmCan_SetControllerMode (CAN_1, CAN_T_START);
}


void CAN_HAL_RxIndication(uint16 Hrh, uint32 CanId, uint8 CanDlc, const uint8 *CanSduPtr)
{
	uint8 i;

	if(CanId == CAN0_ID_VPC1){
		vCanMsg_VPC1_FRAME.count++;
		vCanMsg_VPC1_FRAME.new_flag = TRUE;
		vCanMsg_VPC1_FRAME.CanId = CanId;
		vCanMsg_VPC1_FRAME.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_VPC1_FRAME.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN0_ID_SEA1){
		vCanMsg_SEA1_FRAME.count++;
		vCanMsg_SEA1_FRAME.new_flag = TRUE;
		vCanMsg_SEA1_FRAME.CanId = CanId;
		vCanMsg_SEA1_FRAME.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_SEA1_FRAME.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN0_ID_SEA2){
		vCanMsg_SEA2_FRAME.count++;
		vCanMsg_SEA2_FRAME.new_flag = TRUE;
		vCanMsg_SEA2_FRAME.CanId = CanId;
		vCanMsg_SEA2_FRAME.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_SEA2_FRAME.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN0_ID_RMT_CMD){

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
	else if(CanId == CAN1_ID_RX_MAILBOX1){

		vCanMsg_CAN1_RX_MAILBOX1.count++;
		vCanMsg_CAN1_RX_MAILBOX1.new_flag = TRUE;
		vCanMsg_CAN1_RX_MAILBOX1.CanId = CanId;
		vCanMsg_CAN1_RX_MAILBOX1.CanDlc = CanDlc;

		if(CanDlc>8){
			CanDlc = 8;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_CAN1_RX_MAILBOX1.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN1_ID_RX_MAILBOX2){

		vCanMsg_CAN1_RX_MAILBOX2.count++;
		vCanMsg_CAN1_RX_MAILBOX2.new_flag = TRUE;
		vCanMsg_CAN1_RX_MAILBOX2.CanId = CanId;
		vCanMsg_CAN1_RX_MAILBOX2.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_CAN1_RX_MAILBOX2.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN0_ID_RX_MAILBOX15){

		vCanMsg_CAN0_RX_MAILBOX15.count++;
		vCanMsg_CAN0_RX_MAILBOX15.new_flag = TRUE;
		vCanMsg_CAN0_RX_MAILBOX15.CanId = CanId;
		vCanMsg_CAN0_RX_MAILBOX15.CanDlc = CanDlc;

		if(CanDlc>8){
			CanDlc = 8;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_CAN0_RX_MAILBOX15.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN1_ID_RX_MAILBOX14){

		vCanMsg_CAN1_RX_MAILBOX14.count++;
		vCanMsg_CAN1_RX_MAILBOX14.new_flag = TRUE;
		vCanMsg_CAN1_RX_MAILBOX14.CanId = CanId;
		vCanMsg_CAN1_RX_MAILBOX14.CanDlc = CanDlc;

		if(CanDlc>32){
			CanDlc = 32;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_CAN1_RX_MAILBOX14.Msg.byte[i] = CanSduPtr[i];
		}
	}
	else if(CanId == CAN1_ID_RX_MAILBOX15){

		vCanMsg_CAN1_RX_MAILBOX15.count++;
		vCanMsg_CAN1_RX_MAILBOX15.new_flag = TRUE;
		vCanMsg_CAN1_RX_MAILBOX15.CanId = CanId;
		vCanMsg_CAN1_RX_MAILBOX15.CanDlc = CanDlc;

		if(CanDlc>8){
			CanDlc = 8;
		}
		else{
			//do nothing
		}

		for (i=0; i < CanDlc ; i++){
			vCanMsg_CAN1_RX_MAILBOX15.Msg.byte[i] = CanSduPtr[i];
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

void CAN_HAL_TxMsg(uint8 msg_index, uint8 dlc, uint8 *data)
{
	Can_PduType Can_pdu;
	Can_ReturnType RetVal = CAN_NOT_OK;

	if(msg_index<CAN_MSG_TX_INDEX_MAX){
		Can_pdu.swPduHandle = Can_MsgObj_CanId[msg_index].CanTxPduId;
		Can_pdu.id = Can_MsgObj_CanId[msg_index].CanId;
		Can_pdu.length = dlc;
		Can_pdu.sdu = &data[0];

		RetVal = Can_17_McmCan_Write(Can_MsgObj_CanId[msg_index].HthIdx, &Can_pdu) ;
	}
	else{
		//do nothing
	}
}


#define BUS_OFF_ARRAY_MAX		(64U)
uint8 vEhalCan_Can0_BusOffState_10ms[BUS_OFF_ARRAY_MAX];
uint8 vEhalCan_Can0_BusOffState_10ms_count;

extern CanSM_BusOffRecoveryStateType_ten CanSM_currBOR_State_en[1];

void EhalCan_Task_1ms(void)
{
	if(CanSM_currBOR_State_en[0]==CANSM_S_NO_BUS_OFF){
		CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_ARS2, 8, &vCanMsg_ARS2.byte[0]);
	}
}

void EhalCan_Task_10ms_3(void)
{
	if(CanSM_currBOR_State_en[0]==CANSM_S_NO_BUS_OFF){
		vEhalCan_Can0_BusOffState = 0;
		CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_ARS1, 32, &vCanMsg_ARS1.byte[0]);
	}
	else{
		vEhalCan_Can0_BusOffState = 1;
	}
}

void EhalCan_Task_10ms_5(void)
{
	if(CanSM_currBOR_State_en[0]==CANSM_S_NO_BUS_OFF){
		vEhalCan_Can0_BusOffState = 0;

		CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_ARS3, 8, &vCanMsg_ARS3.byte[0]);


		if(vCanMsg_RMT_CMD_FRAME.Msg.signal.TEST_EN == 1){
			CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_RMT_RES, 8, &vCanMsg_RMT_RES.byte[0]);
//			CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_MAILBOX14, 8, &vCanMsg_CAN0_TX_MAILBOX14.byte[0]);
//			CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_MAILBOX15, 32, &vCanMsg_CAN0_TX_MAILBOX15.byte[0]);
//			CAN_HAL_TxMsg(CAN1_MSG_TX_INDEX_MAILBOX1, 8, &vCanMsg_CAN1_TX_MAILBOX1.byte[0]);
//			CAN_HAL_TxMsg(CAN1_MSG_TX_INDEX_MAILBOX2, 32, &vCanMsg_CAN1_TX_MAILBOX2.byte[0]);
//			CAN_HAL_TxMsg(CAN1_MSG_TX_INDEX_MAILBOX14, 8, &vCanMsg_CAN1_TX_MAILBOX14.byte[0]);
//			CAN_HAL_TxMsg(CAN1_MSG_TX_INDEX_MAILBOX15, 32, &vCanMsg_CAN1_TX_MAILBOX15.byte[0]);
		}

	}
	else{
		vEhalCan_Can0_BusOffState = 1;
	}
}

void EhalCan_Task_10ms_7(void)
{
	if(CanSM_currBOR_State_en[0]==CANSM_S_NO_BUS_OFF){
		vEhalCan_Can0_BusOffState = 0;
		CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_ARS4, 24, &vCanMsg_ARS4.byte[0]);
	}
	else{
		vEhalCan_Can0_BusOffState = 1;
	}
}

void EhalCan_SendRmtResImmediate(uint8 value)
{
	vCanMsg_RMT_RES.byte[0] = value;
	CAN_HAL_TxMsg(CAN0_MSG_TX_INDEX_RMT_RES, 8, &vCanMsg_RMT_RES.byte[0]);
}

void EhalCan_Task_100ms(void)
{
	//	vEhalCan_Can0_BusOffState = EhalCan_IsBusoff(0);
	//	if(vEhalCan_Can0_BusOffState == 1){
	//		CanIf_SetControllerMode(0,CANIF_CS_STARTED);
	//		vEhalCan_Can0_BusOffState =0;
	//	}
}

//FBL
//uint8 CanIf_TxMsg(uint8 MsgHandler, uint32 MsgId, uint8 MsgDlc, uint8 *MsgData)
//{
//	Can_PduType Can_pdu;
//	Can_ReturnType RetVal = CAN_NOT_OK;
//
//	if(MsgDlc > 8)
//	{
//
//	}
//	else
//	{
//		Can_pdu.swPduHandle = MsgHandler;
//		Can_pdu.id = MsgId;
//		Can_pdu.length = MsgDlc;
//		Can_pdu.sdu = &MsgData[0];
//
////		RetVal = Can_17_MCanP_Write(Can_17_MCanPConf_CanHardwareObject_CanHardwareObject_BSL_TX, &Can_pdu); //20220607 G.W.Ham : Autosar first build
//	}
//
//	return RetVal;
//}
