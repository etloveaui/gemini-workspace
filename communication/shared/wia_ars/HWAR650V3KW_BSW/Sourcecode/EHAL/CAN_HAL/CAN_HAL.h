/*
 * CAN_HAL.h
 *
 *  Created on: 2017. 4. 19.
 *      Author:
 */

#ifndef CAN_HAL_H_
#define CAN_HAL_H_

#include "Platform_Types.h"

typedef union{
	uint8 byte[16];
	struct __packed__{
		uint8 MVPC_ARS_byte1     ;
		uint8 MVPC_ARS_byte2     ;
		uint8 MVPC_ARS_byte3     ;
		uint8 MVPC_ARS_byte4     ;
		uint8 MVPC_ARS_byte5     ;
		uint8 MVPC_ARS_byte6     ;
		uint8 MVPC_ARS_byte7     ;
		uint8 MVPC_ARS_byte8     ;
		uint8 MVPC_ARS_byte9     ;
		uint8 MVPC_ARS_byte10     ;
		uint8 MVPC_ARS_byte11    ;
		uint8 MVPC_ARS_byte12     ;
		uint8 MVPC_ARS_byte13     ;
		uint8 MVPC_ARS_byte14     ;
		uint8 MVPC_ARS_byte15     ;
		uint8 MVPC_ARS_byte16     ;
	}signal;
}typCanMsg_MVPC1;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	uint32 count_prev;
	uint8 timeout_flag;
	uint32 timeout_cnt;
	uint32 timeout_max;
	typCanMsg_MVPC1 Msg;
}typCanMsg_MVPC1_FRAME;

typedef union{
	uint8 byte[24];
	struct __packed__{
		uint8 RT1_10_byte1     ;
		uint8 RT1_10_byte2     ;
		uint8 RT1_10_byte3     ;
		uint8 RT1_10_byte4     ;
		uint8 RT1_10_byte5     ;
		uint8 RT1_10_byte6     ;
		uint8 RT1_10_byte7     ;
		uint8 RT1_10_byte8     ;
		uint8 RT1_10_byte9     ;
		uint8 RT1_10_byte10     ;
		uint8 RT1_10_byte11    ;
		uint8 RT1_10_byte12     ;
		uint8 RT1_10_byte13     ;
		uint8 RT1_10_byte14     ;
		uint8 RT1_10_byte15     ;
		uint8 RT1_10_byte16     ;
		uint8 RT1_10_byte17     ;
		uint8 RT1_10_byte18     ;
		uint8 RT1_10_byte19     ;
		uint8 RT1_10_byte20     ;
		uint8 RT1_10_byte21     ;
		uint8 RT1_10_byte22     ;
		uint8 RT1_10_byte23     ;
		uint8 RT1_10_byte24     ;
	}signal;
}typCanMsg_RT1_10;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	uint32 count_prev;
	uint8 timeout_flag;
	uint32 timeout_cnt;
	uint32 timeout_max;
	typCanMsg_RT1_10 Msg;
}typCanMsg_RT1_10_FRAME;

typedef union{
	uint8 byte[8];
	struct __packed__{
		uint8 RT1_20_byte1     ;
		uint8 RT1_20_byte2     ;
		uint8 RT1_20_byte3     ;
		uint8 RT1_20_byte4     ;
		uint8 RT1_20_byte5     ;
		uint8 RT1_20_byte6     ;
		uint8 RT1_20_byte7     ;
		uint8 RT1_20_byte8     ;
	}signal;
}typCanMsg_RT1_20;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	uint32 count_prev;
	uint8 timeout_flag;
	uint32 timeout_cnt;
	uint32 timeout_max;
	typCanMsg_RT1_20 Msg;
}typCanMsg_RT1_20_FRAME;

typedef union{
	uint8 byte[8];
	struct __packed__{
		uint8 RT1_200_byte1     ;
		uint8 RT1_200_byte2     ;
		uint8 RT1_200_byte3     ;
		uint8 RT1_200_byte4     ;
		uint8 RT1_200_byte5     ;
		uint8 RT1_200_byte6     ;
		uint8 RT1_200_byte7     ;
		uint8 RT1_200_byte8     ;
	}signal;
}typCanMsg_RT1_200;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	uint32 count_prev;
	uint8 timeout_flag;
	uint32 timeout_cnt;
	uint32 timeout_max;
	typCanMsg_RT1_200 Msg;
}typCanMsg_RT1_200_FRAME;


typedef union{
	uint8 byte[8];
	struct{
		uint32 unused1;
		uint32 unused0;
	}signal;
}typCanMsg_VCU6;


typedef struct{
	uint8 new_flag;
	uint32 CanId;
	uint16 Hrh;
	uint8 CanDlc;
	uint32 count;
	uint32 count_prev;
	uint32 timeout_cnt;
	uint8 timeout_flag;
	typCanMsg_VCU6 Msg;
}typCanMsg_VCU6_FRAME;

typedef union{
	uint8 byte[8];
	struct{
		uint16 unused4;
		uint16 unused3;
		uint16 unused2;
		uint16 unused1;
	}signal;
}typCanMsg_SCU6;

typedef union{
	uint8 byte[16];
	struct __packed__{
		uint8 ARS1_byte1     ;
		uint8 ARS1_byte2     ;
		uint8 ARS1_byte3     ;
		uint8 ARS1_byte4     ;
		uint8 ARS1_byte5     ;
		uint8 ARS1_byte6     ;
		uint8 ARS1_byte7     ;
		uint8 ARS1_byte8     ;
		uint8 ARS1_byte9     ;
		uint8 ARS1_byte10     ;
		uint8 ARS1_byte11    ;
		uint8 ARS1_byte12     ;
		uint8 ARS1_byte13     ;
		uint8 ARS1_byte14     ;
		uint8 ARS1_byte15     ;
		uint8 ARS1_byte16     ;
	}signal;
}typCanMsg_ARS1;

typedef union{
	uint8 byte[32];
	struct __packed__{
		sint16 ARS2_MotorPosition;
		sint16 ARS2_SEAPosition;
		sint16 ARS2_SEADeformation;
		sint16 Reserved16;
		uint32 unused6;
		uint32 unused5;
		uint32 unused4;
		uint32 unused3;
		uint32 unused2;
		uint32 unused1;
	}signal;
}typCanMsg_ARS2;

typedef union{
	uint8 byte[32];
	struct{
		uint16 ARS3_SEASensorValue;
		uint16 ARS3_MotorSensorValue;
		uint32 unused7;
		uint32 unused6;
		uint32 unused5;
		uint32 unused4;
		uint32 unused3;
		uint32 unused2;
		uint32 unused1;
	}signal;
}typCanMsg_ARS3;

typedef union{
	uint8 byte[32];
	struct{
		uint32 unused8;
		uint32 unused7;
		uint32 unused6;
		uint32 unused5;
		uint32 unused4;
		uint32 unused3;
		uint32 unused2;
		uint32 unused1;
	}signal;
}typCanMsg_ARS4;

typedef union {
	uint8 byte[32];
	struct __packed__ {
		uint8 MEAS_byte1;
		uint8 MEAS_byte2;
		uint8 MEAS_byte3;
		uint8 MEAS_byte4;
		uint8 MEAS_byte5;
		uint8 MEAS_byte6;
		uint8 MEAS_byte7;
		uint8 MEAS_byte8;
		uint8 MEAS_byte9;
		uint8 MEAS_byte10;
		uint8 MEAS_byte11;
		uint8 MEAS_byte12;
		uint8 MEAS_byte13;
		uint8 MEAS_byte14;
		uint8 MEAS_byte15;
		uint8 MEAS_byte16;
		uint8 MEAS_byte17;
		uint8 MEAS_byte18;
		uint8 MEAS_byte19;
		uint8 MEAS_byte20;
		uint8 MEAS_byte21;
		uint8 MEAS_byte22;
		uint8 MEAS_byte23;
		uint8 MEAS_byte24;
		uint8 MEAS_byte25;
		uint8 MEAS_byte26;
		uint8 MEAS_byte27;
		uint8 MEAS_byte28;
		uint8 MEAS_byte29;
		uint8 MEAS_byte30;
		uint8 MEAS_byte31;
		uint8 MEAS_byte32;
	} signal;
} typCanMsg_MEAS32;


typedef union{
	uint8 byte[8];
	struct __packed__ {
		sint16 wRotElFilt;
		uint16 AdcValue_HVDC;
		sint16 AdcValue_Tigbt;
		uint16 unused1;
	}signal;
}typCanMsg_RMT_RES;

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
}typCanMsg_RMT_CMD;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	typCanMsg_RMT_CMD Msg;
}typCanMsg_RMT_CMD_FRAME;

typedef struct
{
	uint8 HthIdx;
	uint8 CanCtrlId;
	uint32 CanId;
	//	uint8 CanTxPduId;
	uint8 CanDlc;
	uint8 *pSdu;
}Can_MsgObjCanId_t;

//RX
//CAN0
#define CANICOM_CAN0_RX			 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_1) //0x7A0 CanIcom(MCAL)
#define DUMMY_CAN0_RX_MAILBOX2 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_2) //DUMMY 0x102
#define DUMMY_CAN0_RX_MAILBOX3		 		(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_3) //DUMMY 0x103
#define DCM_FUNC_CAN0_RX		 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_4) //0x7DF DCM_FUNC(CAN_TP)
#define REPROGRAM_CMD_CAN0_RX				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_5) //0xF0  REPROGRAM_CMD
#define DCM_PHYREQ_CAN0_RX					(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_6) //0x7EA DCM_PHYREQ(CAN_TP)
#define DUMMY_CAN0_RX_MAILBOX7	 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_7) //DUMMY 0x107
#define DUMMY_CAN0_RX_MAILBOX8 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_8) //DUMMY 0x108
#define CTO_XCP_CAN0_RX			 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_9) //0x660 CTO_XCP
#define DUMMY_CAN0_RX_MAILBOX10				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_10) //DUMMY 0x10A
#define DUMMY_CAN0_RX_MAILBOX11				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_11) //DUMMY 0x10B
#define DUMMY_CAN0_RX_MAILBOX12				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_12) //DUMMY 0x10C
#define DUMMY_CAN0_RX_MAILBOX13				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_13) //DUMMY 0x10D
#define DUMMY_CAN0_RX_MAILBOX14				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_14) //DUMMY 0x10E
#define DUMMY_CAN0_RX_MAILBOX15				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_15) //DUMMY 0x10F

//CAN1
//#define SEA_ARS_01_CAN1_RX					(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_1) //SEA_ARS_01 0x51A
//#define SEA_ARS_02_CAN1_RX					(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_2) //SEA_ARS_02 0x51B
//#define VPC_ARS_01_CAN1_RX 					(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_3) //VPC_ARS_01 0x51C
#define MVPC_ARS_01_CAN1_RX					(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_1) //MVPC_Ars_01_1ms 0x20
#define ROUTING_01_10MS_CAN1_RX				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_2) //Routing_01_10ms 0x27
#define ROUTING_01_2000MS_CAN1_RX 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_3) //Routing_01_200ms 0x25
#define ROUTING_01_20MS_CAN1_RX				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_4) //Routing_01_20ms 0x26
#define DUMMY_CAN1_RX_MAILBOX5 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_5) //DUMMY 0x205
#define DUMMY_CAN1_RX_MAILBOX6 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_6) //DUMMY 0x206
#define DUMMY_CAN1_RX_MAILBOX7 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_7) //DUMMY 0x207
#define DUMMY_CAN1_RX_MAILBOX8 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_8) //DUMMY 0x208
#define DUMMY_CAN1_RX_MAILBOX9 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_9) //DUMMY 0x209
#define DUMMY_CAN1_RX_MAILBOX10				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_10) //DUMMY 0x20A
#define DUMMY_CAN1_RX_MAILBOX11				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_11) //DUMMY 0x20B
#define DUMMY_CAN1_RX_MAILBOX12				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_12) //DUMMY 0x20C
#define DUMMY_CAN1_RX_MAILBOX13				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_13) //DUMMY 0x20D
#define DUMMY_CAN1_RX_MAILBOX14				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_14) //DUMMY 0x20E
#define RMT_CMD_CAN1_RX						(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_15) //RMT_CMD 0x7A1

//TX
//CAN0
#define DUMMY_CAN0_TX_MAILBOX1 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_1) //DUMMY 0x7A5
#define MEAS_1MS_CAN0_TX					(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_2) //0x401 CAN0_ID_MEAS_1MS
#define MEAS_5MS_A_CAN0_TX					(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_3) //0x402 CAN0_ID_MEAS_5MS_A
#define DCM_PHYRES_CAN0_TX			 		(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_4) //0x7E2 DCM_PHYRES(CAN_TP)
#define MEAS_5MS_B_CAN0_TX	 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_5) //0x403 CAN0_ID_MEAS_5MS_B
#define MEAS_10MS_A_CAN0_TX 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_6) //0x404 CAN0_ID_MEAS_10MS_A
#define REPROGRAM_RES_CAN0_TX		 		(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_7) //0xF1  REPROGRAM_RES
#define DTO_XCP_CAN0_TX						(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_8) //0x661 DTO_XCP
#define MEAS_10MS_B_CAN0_TX					(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_9) //0x405 CAN0_ID_MEAS_10MS_B
#define DUMMY_CAN0_TX_MAILBOX10				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_10) //DUMMY
#define DUMMY_CAN0_TX_MAILBOX11				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_11) //DUMMY
#define DUMMY_CAN0_TX_MAILBOX12				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_12) //DUMMY
#define DUMMY_CAN0_TX_MAILBOX13				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_13) //DUMMY
#define DUMMY_CAN0_TX_MAILBOX14				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_14) //DUMMY
#define DUMMY_CAN0_TX_MAILBOX15				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_15) //DUMMY

//CAN1
#define ARS1_CAN1_TX 						(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_1) //0x515 ARS_dev_01
#define DUMMY_CAN1_TX_MAILBOX2				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_2) // 2025. 6. 13. etkim - removed //0x514 ARS_dev_02
#define DUMMY_CAN1_TX_MAILBOX3				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_3) // 2025. 6. 13. etkim - removed //0x516 ARS_dev_03
#define DUMMY_CAN1_TX_MAILBOX4				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_4) // 2025. 6. 13. etkim - removed //0x517 ARS_dev_04
#define DUMMY_CAN1_TX_MAILBOX5 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_5)
#define DUMMY_CAN1_TX_MAILBOX6 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_6)
#define DUMMY_CAN1_TX_MAILBOX7 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_7)
#define DUMMY_CAN1_TX_MAILBOX8 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_8)
#define DUMMY_CAN1_TX_MAILBOX9 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_9)
#define DUMMY_CAN1_TX_MAILBOX10				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_10)
#define DUMMY_CAN1_TX_MAILBOX11				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_11)
#define DUMMY_CAN1_TX_MAILBOX12				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_12)
#define DUMMY_CAN1_TX_MAILBOX13				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_13)
#define DUMMY_CAN1_TX_MAILBOX14				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_14) //DUMMY 0x21E
#define RMT_RES_CAN1_TX						(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_15) //0x7A4 RMT_RES


//extern typCanMsg_FAULTS_Infor SCU2;
//extern typCanMsg_MOT_Infor SCU3;
extern typCanMsg_VCU6_FRAME vCanMsg_VCU6_FRAME;
extern typCanMsg_SCU6 vCanMsg_SCU6;

extern typCanMsg_MVPC1_FRAME vCanMsg_MVPC1_FRAME; // Rx
extern typCanMsg_RT1_10_FRAME vCanMsg_RT1_10_FRAME; // Rx
extern typCanMsg_RT1_20_FRAME vCanMsg_RT1_20_FRAME; // Rx
extern typCanMsg_RT1_200_FRAME vCanMsg_RT1_200_FRAME; // Rx
extern typCanMsg_RMT_CMD_FRAME vCanMsg_RMT_CMD_FRAME;// Rx

extern typCanMsg_ARS1 vCanMsg_ARS1; // Tx
//extern typCanMsg_ARS2 vCanMsg_ARS2; // Tx
//extern typCanMsg_ARS3 vCanMsg_ARS3; // Tx
//extern typCanMsg_ARS4 vCanMsg_ARS4; // Tx
extern typCanMsg_RMT_RES vCanMsg_RMT_RES;		// Tx
extern typCanMsg_MEAS32 vCanMsg_MEAS_1MS;		// Tx
extern typCanMsg_MEAS32 vCanMsg_MEAS_5MS_A;		// Tx
extern typCanMsg_MEAS32 vCanMsg_MEAS_5MS_B;		// Tx
extern typCanMsg_MEAS32 vCanMsg_MEAS_10MS_A;	// Tx
extern typCanMsg_MEAS32 vCanMsg_MEAS_10MS_B;	// Tx

extern void CAN_HAL_RxIndication(uint16 Hrh, uint32 CanId, uint8 CanDlc, const uint8 *CanSduPtr);
extern void EhalCan_Task_1ms(void);
extern void EhalCan_Task_5ms(void);
extern void EhalCan_Task_10ms_3(void);
extern void EhalCan_Task_10ms_5(void);
extern void EhalCan_Task_10ms_7(void);
extern void EhalCan_Task_20ms(void);
extern void EhalCan_Task_100ms(void);
extern void EhalCan_Task_200ms(void);
extern void EhalCan_Task_500ms(void);
extern void EhalCan_Task_1000ms(void);
extern uint8 EhalCan_IsBusoff(uint8 can_ch);
extern void EhalCan1_BusOffRecovery_Task(void);
//extern void EhalCan_SendRmtResImmediate(uint8 value);
extern void EhalCan_Init(void);
extern void EhalCan_SetCh0TxEnable(uint8 enable);

//FBL
extern uint8 CanIf_TxMsg(uint8 MsgHandler, uint32 MsgId, uint8 MsgDlc, uint8 *MsgData);
#endif /* CAN_HAL_H_ */
