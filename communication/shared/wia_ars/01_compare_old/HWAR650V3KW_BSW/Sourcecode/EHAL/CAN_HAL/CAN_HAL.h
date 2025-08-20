/*
 * CAN_HAL.h
 *
 *  Created on: 2017. 4. 19.
 *      Author:
 */

#ifndef CAN_HAL_H_
#define CAN_HAL_H_

#include "Platform_Types.h"

#define CAN_TEMPERATURE_OFFSET			(40.0f)
#define CAN_GEAR_SPEED_SCALE			(100.0f)



typedef union{
	uint8 byte[32];
	struct __packed__{
		uint32 VPC1_ARSOperationModeCommand	: 4;
		uint32 Reserved4					: 4;
		sint16 VPC1_ARSTargetTorque;
		uint8 Reserved8;
		uint32 Reserved32;
	}signal;
}typCanMsg_VPC1;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	typCanMsg_VPC1 Msg;
}typCanMsg_VPC1_FRAME;

typedef union{
	uint8 byte[32];
	struct __packed__{
		uint32 SEA1_SEAControlModeCommand	: 4;
		uint32 Reserved4					: 4;
		sint16 SEA1_MotorTargetTorque;
		sint16 SEA1_MotorRPMCmd;
		uint16 SEA1_MotorFreqCmd;
		sint16 SEA1_MotorBetaCmd;
		uint16 SEA1_MotorVltCmd;
		sint16 SEA1_MotorTqCmd;
		uint32 Reserved24					: 24;
	}signal;
}typCanMsg_SEA1;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	typCanMsg_SEA1 Msg;
}typCanMsg_SEA1_FRAME;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	typCanMsg_SEA1 Msg;
}typCanMsg_SEA2_FRAME;


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
	typCanMsg_VCU6 Msg;
}typCanMsg_VCU6_FRAME;

typedef union{
	uint8 byte[8];
	struct{
		/* A4918 */
		uint8 A4918_ALU				: 1;
		uint8 A4918_AHU				: 1;
		uint8 A4918_BLU				: 1;
		uint8 A4918_BHU				: 1;
		uint8 A4918_CLU				: 1;
		uint8 A4918_CHU				: 1;
		uint8 A4918_VSU				: 1;
		uint8 A4918_VSO				: 1;

		uint8 A4918_ALO				: 1;
		uint8 A4918_BLO				: 1;
		uint8 A4918_CLO				: 1;
		uint8 A4918_VBR				: 1;
		uint8 A4918_VRU				: 1;
		uint8 A4918_VRO				: 1;
		uint8 A4918_OC1				: 1;
		uint8 A4918_OL				: 1;

		uint8 A4918_VA				: 1;
		uint8 A4918_VB				: 1;
		uint8 A4918_VC				: 1;
		uint8 A4918_TW				: 1;
		uint8 A4918_OT				: 1;
		uint8 A4918_EE				: 1;
		uint8 A4918_SE				: 1;
		uint8 A4918_POR				: 1;

		/* A4918 & TLF35584 */
		uint8 A4918_LAD				: 1;
		uint8 A4918_LBD				: 1;
		uint8 A4918_LCD				: 1;
		uint8 TLF_INITF				: 1;
		uint8 TLF_ABISTERR			: 1;
		uint8 TLF_VMONF_A			: 1;
		uint8 TLF_OTF_A				: 1;
		uint8 TLF_VOLTSELERR		: 1;

		uint8 TLF_HARDRES			: 1;
		uint8 TLF_SOFTRES			: 1;
		uint8 TLF_ERRF				: 1;
		uint8 TLF_FWDF				: 1;
		uint8 TLF_WWDF				: 1;
		uint8 TLF_VMONF_B			: 1;
		uint8 HALL_SENSOR_FAULTS	: 1;
		uint8 LOGIC_VOLT_FAULTS		: 1;

		uint8 TLF_INTMISS			: 1;
		uint8 TLF_ABIST				: 1;
		uint8 TLF_OTF_C				: 1;
		uint8 TLF_OTW				: 1;
		uint8 TLF_MON				: 1;
		uint8 TLF_SPI				: 1;
		uint8 TLF_WK				: 1;
		uint8 TLF_SYS				: 1;

		/* A1333 */
		uint8 A1333_RST				: 1;
		uint8 A1333_MSL				: 1;
		uint8 A1333_UVA				: 1;
		uint8 A1333_UVD				: 1;
		uint8 A1333_OFE				: 1;
		uint8 A1333_EUE				: 1;
		uint8 A1333_ZIE				: 1;
		uint8 A1333_PLK				: 1;

		uint8 A1333_AVG				: 1;
		uint8 A1333_STF				: 1;
		uint8 A1333_WAR				: 1;
		uint8 A1333_MSH				: 1;
		uint8 A1333_SAT				: 1;
		uint8 A1333_ESE				: 1;
		uint8 A1333_TR				: 1;
		uint8 unused4				: 1;
	}signal;
}typCanMsg_FAULTS_Infor;

typedef union{
	uint8 byte[8];
	struct{
//		uint16 SCU_CHIP_TERERATURE	: 8;
//		uint32 DURABILITY_CNT		: 24;
//		uint16 mot_speed_rpm_ref	: 16;
//		uint16 mot_speed_rpm		: 16;

		uint32 SCU_CHIP_TERERATURE	: 8;

		uint32 DURABILITY_CNT		: 20;
		uint32 mot_speed_rpm_ref	: 13;
		uint32 mot_speed_rpm		: 13;
		uint32 mot_current			: 10;
	}signal;
}typCanMsg_MOT_Infor;

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
	uint8 byte[32];
	struct __packed__{
		uint32 ARS1_OperationMode     :3;
		uint32 Reserved5              :5;
		sint16 ARS1_TargetTorque      ;
		sint16 ARS1_ActualTorque      ;
		uint32 ARS1_InputHVoltage     :10;
		uint32 ARS1_MotorVd           :10;
		uint32 ARS1_MotorVq           :10;
		uint32 ARS1_InterlockStatus   :1;
		uint32 Reserved1              :1;
		sint16 ARS1_MotorTargetTq     ;
		sint16 ARS1_MotorActualTq     ;
		uint32 ARS1_MotorIsRef        :10 ;
		uint32 ARS1_MotorIs           :10;
		uint32 ARS1_MotorBeta         :12;
		uint8  ARS1_IGBTTemperature   ;
		uint8  ARS1_MotorTemperature  ;
		uint8  ARS1_PCBTemperature    ;
		uint8  ARS1_InputLVoltage     ;
		uint32 ARS1_DiagErrorFlags    ;
		sint16 ARS1_MotorActualRPM    ;
		uint32 ARS1_SEASensorValue    :12;
		uint32 ARS1_MotorSensorValue  :12;
		uint16 Reserved16             ;
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

typedef union{
	uint8 byte[8];
	struct __packed__{
		uint8 data1;
		uint8 data2;
		uint8 data3;
		uint8 data4;
		uint8 data5;
		uint8 data6;
		uint8 data7;
		uint8 data8;
	}signal;
}typCanMsg_TEST1;

typedef union{
	uint8 byte[32];
	struct __packed__{
		uint8 data1;
		uint8 data2;
		uint8 data3;
		uint8 data4;
		uint8 data5;
		uint8 data6;
		uint8 data7;
		uint8 data8;
		uint8 data9;
		uint8 data10;
		uint8 data11;
		uint8 data12;
		uint8 data13;
		uint8 data14;
		uint8 data15;
		uint8 data16;
		uint8 data17;
		uint8 data18;
		uint8 data19;
		uint8 data20;
		uint8 data21;
		uint8 data22;
		uint8 data23;
		uint8 data24;
		uint8 data25;
		uint8 data26;
		uint8 data27;
		uint8 data28;
		uint8 data29;
		uint8 data30;
		uint8 data31;
		uint8 data32;
	}signal;
}typCanMsg_TEST2;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	typCanMsg_TEST1 Msg;
}typCanMsg_RX_TEST1_FRAME;

typedef struct{
	uint8 new_flag;
	uint8 CanDlc;
	uint16 Hrh;
	uint32 CanId;
	uint32 count;
	typCanMsg_TEST2 Msg;
}typCanMsg_RX_TEST2_FRAME;

typedef struct
{
	uint8 HthIdx;
	uint8 CanCtrlId;
	uint32 CanId;
	uint8 CanTxPduId;
}Can_MsgObjCanId_t;


#define CANICOM_CAN0_RX_MAILBOX1 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_1) //0x7A0 CanIcom(MCAL)
#define SEA_ARS_01_CAN0_RX_MAILBOX2 		(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_2) //0x51A SEA_ARS_01
#define VPC_ARS_01_CAN0_RX_MAILBOX3 		(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_3) //0x51B VPC_ARS_01
#define DCM_FUNC_CAN0_RX_MAILBOX4 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_4) //0x7DF DCM_FUNC(CAN_TP)
#define REPROGRAM_CMD_CAN0_RX_MAILBOX5		(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_5) //0xF0  REPROGRAM_CMD
#define DCM_PHYREQ_CAN0_RX_MAILBOX6 		(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_6) //0x7EA DCM_PHYREQ(CAN_TP)
#define RMT_CMD_CAN0_RX_MAILBOX7 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_7) //0x7A1 RMT_CMD
#define DUMMY_CAN0_RX_MAILBOX8 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_8) //DUMMY 0x108
#define CTO_XCP_CAN0_RX_MAILBOX9 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_9) //0x660 CTO_XCP
#define SEA_ARS_02_CAN0_RX_MAILBOX10		(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_10) //DUMMY 0x10A
#define DUMMY_CAN0_RX_MAILBOX11				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_11) //DUMMY 0x10B
#define DUMMY_CAN0_RX_MAILBOX12				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_12) //DUMMY 0x10C
#define DUMMY_CAN0_RX_MAILBOX13				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_13) //DUMMY 0x10D
#define DUMMY_CAN0_RX_MAILBOX14				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_14) //DUMMY 0x10E
#define DUMMY_CAN0_RX_MAILBOX15				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Rx_Std_MailBox_15) //DUMMY 0x10F for Test

#define DUMMY_CAN0_TX_MAILBOX1 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_1) //DUMMY 0x7A5
#define ARS3_CAN0_TX_MAILBOX2 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_2) //0x516 ARS_dev_03
#define ARS1_CAN0_TX_MAILBOX3 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_3) //0x514 ARS_dev_01
#define DCM_PHYRES_CAN0_TX_MAILBOX4 		(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_4) //0x7E2 DCM_PHYRES(CAN_TP)
#define RMT_RES_CAN0_TX_MAILBOX5 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_5) //0x7A4 RMT_RES
#define ARS2_CAN0_TX_MAILBOX6 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_6) //0x515 ARS_dev_02
#define REPROGRAM_RES_CAN0_TX_MAILBOX7 		(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_7) //0xF1  REPROGRAM_RES
#define DTO_XCP_CAN0_TX_MAILBOX8 			(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_8) //0x661 DTO_XCP
#define ARS4_CAN0_TX_MAILBOX9 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_9) //DUMMY
#define DUMMY_CAN0_TX_MAILBOX10				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_10) //DUMMY
#define DUMMY_CAN0_TX_MAILBOX11				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_11) //DUMMY
#define DUMMY_CAN0_TX_MAILBOX12				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_12) //DUMMY
#define DUMMY_CAN0_TX_MAILBOX13				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_13) //DUMMY
#define DUMMY_CAN0_TX_MAILBOX14				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_14) //DUMMY 0x11E for Test
#define DUMMY_CAN0_TX_MAILBOX15				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_0_Tx_Std_MailBox_15) //DUMMY 0x11F for Test

#define DUMMY_CAN1_RX_MAILBOX1 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_1) //DUMMY 0x201 for Test
#define DUMMY_CAN1_RX_MAILBOX2 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_2) //DUMMY 0x202 for Test
#define DUMMY_CAN1_RX_MAILBOX3 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_3) //DUMMY 0x203
#define DUMMY_CAN1_RX_MAILBOX4 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_4) //DUMMY 0x204
#define DUMMY_CAN1_RX_MAILBOX5 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_5) //DUMMY 0x205
#define DUMMY_CAN1_RX_MAILBOX6 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_6) //DUMMY 0x206
#define DUMMY_CAN1_RX_MAILBOX7 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_7) //DUMMY 0x207
#define DUMMY_CAN1_RX_MAILBOX8 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_8) //DUMMY 0x208
#define DUMMY_CAN1_RX_MAILBOX9 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_9) //DUMMY 0x209
#define DUMMY_CAN1_RX_MAILBOX10				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_10) //DUMMY 0x20A
#define DUMMY_CAN1_RX_MAILBOX11				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_11) //DUMMY 0x20B
#define DUMMY_CAN1_RX_MAILBOX12				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_12) //DUMMY 0x20C
#define DUMMY_CAN1_RX_MAILBOX13				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_13) //DUMMY 0x20D
#define DUMMY_CAN1_RX_MAILBOX14				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_14) //DUMMY 0x20E for Test
#define DUMMY_CAN1_RX_MAILBOX15				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Rx_Std_MailBox_15) //DUMMY 0x20F for Test

#define DUMMY_CAN1_TX_MAILBOX1 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_1) //DUMMY 0x211 for Test
#define DUMMY_CAN1_TX_MAILBOX2 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_2) //DUMMY 0x212 for Test
#define DUMMY_CAN1_TX_MAILBOX3 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_3)
#define DUMMY_CAN1_TX_MAILBOX4 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_4)
#define DUMMY_CAN1_TX_MAILBOX5 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_5)
#define DUMMY_CAN1_TX_MAILBOX6 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_6)
#define DUMMY_CAN1_TX_MAILBOX7 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_7)
#define DUMMY_CAN1_TX_MAILBOX8 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_8)
#define DUMMY_CAN1_TX_MAILBOX9 				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_9)
#define DUMMY_CAN1_TX_MAILBOX10				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_10)
#define DUMMY_CAN1_TX_MAILBOX11				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_11)
#define DUMMY_CAN1_TX_MAILBOX12				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_12)
#define DUMMY_CAN1_TX_MAILBOX13				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_13)
#define DUMMY_CAN1_TX_MAILBOX14				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_14) //DUMMY 0x21E for Test
#define DUMMY_CAN1_TX_MAILBOX15				(Can_17_McmCanConf_CanHardwareObject_Can_Network_CANNODE_1_Tx_Std_MailBox_15) //DUMMY 0x21F for Test


extern typCanMsg_FAULTS_Infor SCU2;
extern typCanMsg_MOT_Infor SCU3;
extern typCanMsg_VCU6_FRAME vCanMsg_VCU6_FRAME;
extern typCanMsg_SCU6 vCanMsg_SCU6;


extern typCanMsg_VPC1_FRAME vCanMsg_VPC1_FRAME; // Rx
extern typCanMsg_SEA1_FRAME vCanMsg_SEA1_FRAME; // Rx
extern typCanMsg_SEA2_FRAME vCanMsg_SEA2_FRAME; // Rx
extern typCanMsg_RMT_CMD_FRAME vCanMsg_RMT_CMD_FRAME;// Rx

extern typCanMsg_ARS1 vCanMsg_ARS1; // Tx
extern typCanMsg_ARS2 vCanMsg_ARS2; // Tx
extern typCanMsg_ARS3 vCanMsg_ARS3; // Tx
extern typCanMsg_ARS4 vCanMsg_ARS4; // Tx
extern typCanMsg_RMT_RES vCanMsg_RMT_RES;// Tx

extern void CAN_HAL_RxIndication(uint16 Hrh, uint32 CanId, uint8 CanDlc, const uint8 *CanSduPtr);
extern void EhalCan_Task_1ms(void);
extern void EhalCan_Task_10ms_3(void);
extern void EhalCan_Task_10ms_5(void);
extern void EhalCan_Task_10ms_7(void);
extern void EhalCan_Task_100ms(void);
extern uint8 EhalCan_IsBusoff(uint8 can_ch);
extern void EhalCan_SendRmtResImmediate(uint8 value);
extern void EhalCan_Init(void);

//FBL
extern uint8 CanIf_TxMsg(uint8 MsgHandler, uint32 MsgId, uint8 MsgDlc, uint8 *MsgData);
#endif /* CAN_HAL_H_ */
