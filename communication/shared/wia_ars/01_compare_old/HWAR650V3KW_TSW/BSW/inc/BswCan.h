/*
 * BswCan.h
 *
 *  Created on: 2024. 12. 2.
 *      Author: dell
 */

#ifndef BSWCAN_H_
#define BSWCAN_H_

#include "Platform_Types.h"

#define BSWCAN_CAN_CH0			(0U)

#define BSWCAN_MSG_RX_INDEX_VPC_ARS_01_10ms		(0U) //Rx // 0x51C
#define BSWCAN_MSG_RX_INDEX_SEA_ARS_01_1ms		(1U) //Rx // 0x51A
#define BSWCAN_MSG_RX_INDEX_SEA_ARS_02_1ms		(2U) //Rx // 0x51B

#define BSWCAN_MSG_TX_INDEX_ARS_dev_01_10ms		(0U) //Tx // 0x514 ->0x515 2025.04.01
#define BSWCAN_MSG_TX_INDEX_ARS_dev_02_1ms		(1U) //Tx // 0x515 ->0x514 2025.04.01
#define BSWCAN_MSG_TX_INDEX_ARS_dev_03_10ms		(2U) //Tx // 0x516
#define BSWCAN_MSG_TX_INDEX_ARS_dev_04_10ms		(3U) //Tx // 0x517

#define BSWCAN_MSG_DLC_VPC_ARS_01_10ms			(8U)
#define BSWCAN_MSG_DLC_SEA_ARS_01_1ms			(16U) //Rx
#define BSWCAN_MSG_DLC_SEA_ARS_02_1ms			(24U) //Rx

#define BSWCAN_MSG_DLC_ARS_dev_01_10ms			(32U) //Tx
#define BSWCAN_MSG_DLC_ARS_dev_02_1ms			(8U) //Tx
#define BSWCAN_MSG_DLC_ARS_dev_03_10ms			(8U) //Tx
#define BSWCAN_MSG_DLC_ARS_dev_04_10ms			(24U) //Tx

typedef union{
	uint8 byte[32];
	struct __packed__{
		uint32 VPC1_ARSOperationModeCommand	: 4;
		uint32 Reserved4					: 4;
		sint16 VPC1_ARSTargetTorque;
		uint8 Reserved8;
		uint32 Reserved32;
	}signal;
}typBswCanMsg_VPC1;

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
}typBswCanMsg_SEA1;

typedef union{
	uint8 byte[32];
	struct __packed__{
		float32 SEACtrl_SEA_deformation;
		float32 SEACtrl_SEA_measured_torque;
		float32 SEACtrl_SEA_Position_1;
		float32 SEACtrl_SEA_Position_2;
		float32 SEACtrl_SEA_Position_2_offset;
		float32 SEACtrl_Motor_Position;
		uint32 Reserved2;
		uint32 Reserved1;
	}signal;
}typBswCanMsg_SEA2;

typedef union{
	uint8 byte[32];
	struct __packed__{
		uint32 DiagErrorFlags     : 32;
		sint32 MotorActualRPM     : 16;
		sint8 PCBTemperature      : 8;
		uint8 OperationMode      : 8;
		sint8 MotorTemperature     : 8;
		sint16 TargetTorque      : 12;
		sint16 reserved1      : 4;
		sint8 IGBTTemperature     : 8;
		sint16 ActualTorque      : 12;
		sint16 reserved2      : 4;
		sint16 MotorTargetTq      : 12;
		sint16 reserved3      : 4;
		uint16 MotorSensorValue    : 12;
		uint16 reserved4      : 4;
		sint16 MotorIsRef       : 9;
		sint16 reserved5      : 7;
		sint16 MotorVq         : 12;
		sint16 reserved6      : 4;
		uint16 SEASensorValue     : 12;
		uint16 reserved7      : 4;
		sint16 MotorIs         : 9;
		sint16 reserved8      : 7;
		sint16 MotorBeta        : 12;
		sint16 reserved9      : 4;
		sint16 MotorVd         : 12;
		sint16 reserved10      : 4;
		sint16 reserved11;

	}signal;
}typBswCanMsg_ARS1;

typedef union{
	uint8 byte[32];
	struct __packed__{
		uint16 SEASensorValue_for_SEACtrl   : 16;
		uint16 MotorSensorValue_for_SEACtrl  : 16;
	}signal;
}typBswCanMsg_ARS2;

typedef union{
	uint8 byte[32];
	struct{
		sint16 MotorActualTq      : 12;
		sint16 reserved1      : 4;
		uint8 InterlockStatus     : 2;
		uint8 reserved2      : 6;
		uint8 InputLVoltage      : 8;
		uint16 InputHVoltage      : 10;
		uint16 reserved3      : 6;
		sint16 reserved4;
	}signal;
}typBswCanMsg_ARS3;

typedef union{
	uint8 byte[32];
	struct{
		float32 ARS_SEA_Position_1;
		float32 ARS_SEA_Position_2;
		float32 ARS_SEA_Position_2_offset;
		float32 ARS_SEADeformation;
		float32 ARS_MotorPosition;
		uint32 unused4;
		uint32 unused3;
		uint32 unused2;
		uint32 unused1;
	}signal;
}typBswCanMsg_ARS4;

extern uint8 ShrHWIA_BswCan_GetMsg(uint8 msg_index, uint8 *dlc, uint8 *data);
extern uint8 ShrHWIA_BswCan_SetMsg(uint8 msg_index, uint8 dlc, uint8 *data);
extern uint8 ShrHWIA_BswCan_GetState_Busoff(uint8 can_ch);
extern uint8 ShrHWIA_BswCan_GetState_Timeout(uint8 msg_index);


#endif /* BSWCAN_H_ */
