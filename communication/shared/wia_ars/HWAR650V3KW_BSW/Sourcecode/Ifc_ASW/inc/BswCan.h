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
#define BSWCAN_CAN_CH1			(1U)

#define BSWCAN_MSG_RX_INDEX_MVPC_ARS_01_1ms		(0U) //Rx // 0x20
#define BSWCAN_MSG_RX_INDEX_ROUTING_01_10ms		(1U) //Rx // 0x27
#define BSWCAN_MSG_RX_INDEX_ROUTING_01_20ms		(2U) //Rx // 0x26
#define BSWCAN_MSG_RX_INDEX_ROUTING_01_200ms	(3U) //Rx // 0x25

#define BSWCAN_MSG_TX_INDEX_MEAS_01_1ms			(0U) //Tx 0x401
#define BSWCAN_MSG_TX_INDEX_MEAS_01_5ms			(1U) //Tx 0x402
#define BSWCAN_MSG_TX_INDEX_MEAS_02_5ms			(2U) //Tx 0x403
#define BSWCAN_MSG_TX_INDEX_MEAS_01_10ms		(3U) //Tx 0x404
#define BSWCAN_MSG_TX_INDEX_MEAS_02_10ms		(4U) //Tx 0x405
#define BSWCAN_MSG_TX_INDEX_ARS_dev_01_1ms		(5U) //Tx  Front: 0x21, Rear: 0x22  2025.06.16

#define BSWCAN_MSG_DLC_ARS_dev_01_1ms			(16U) //Tx
#define BSWCAN_MSG_DLC_MEAS						(32U) //Tx

typedef union{
	uint8 byte[32];
	struct __packed__ {
		uint32 unused8;
		uint32 unused7;
		uint32 unused6;
		uint32 unused5;
		uint32 unused4;
		uint32 unused3;
		uint32 unused2;
		uint32 unused1;
	}signal;
}typBswCanMsg_MEAS;

typedef union {
    uint8 byte[16];
    struct __packed__ {
        uint8 MVPC_ArsFrntOpMdCmd;
        uint8 MVPC_ArsReOpMdCmd;
        sint16 MVPC_ArsFrntTgTq    : 12;
        uint16 reserved1          : 4;
        sint16 MVPC_ArsReTgTq     : 12;
        uint16 reserved2          : 4;
        uint8  MVPC_ArsFltLvl     : 2;
        uint8  reserved3          : 6;
        uint8  MVPC_ArsAlvCnt1Val;
        uint8  MVPC_ArsManMdCmd;
        sint16 MVPC_ArsMotRpmCmd;
        uint16 reserved4;
        uint16 reserved5;
        uint8 reserved6;
    } signal;
} typBswCanMsg_MVPC1;

typedef union {
    uint8 byte[24];
    struct __packed__ {
        uint8 ESC_CylPrsrSta     : 2;
        uint8 IMU_LatAccelSigSta : 4;
        uint8 WHL_DirFLVal       : 2;
        uint16 ESC_CylPrsrVal    : 12;
        uint8 IMU_LongAccelSigSta : 4;
        uint8 IMU_RollSigSta     : 4;
        uint8 IMU_VerAccelSigSta : 4;
        uint16 IMU_LatAccelVal;
        uint16 IMU_LongAccelVal;
        uint16 IMU_RollRtVal;
        uint16 IMU_VerAccelVal;
        uint16 IMU_YawRtVal;
        uint8 IMU_YawSigSta : 4;
        uint8 WHL_DirFRVal  : 2;
        uint8 WHL_DirRLVal  : 2;
        uint8 WHL_DirRRVal  : 2;
        uint8 reserved1     : 6;
        uint16 WHL_SpdFLVal : 14;
        uint16 reserved2    : 2;
        uint16 WHL_SpdFRVal : 14;
        uint16 reserved3    : 2;
        uint16 WHL_SpdRLVal : 14;
        uint16 reserved4    : 2;
        uint16 WHL_SpdRRVal : 14;
        uint16 reserved5    : 2;
    } signal;
} typBswCanMsg_RT1_10;

typedef union {
    uint8 byte[8];
    struct __packed__ {
        uint16 ESC_VehAccelVal : 11;
        uint16 ESC_PrkBrkActvSta : 2;
        uint16 ESC_DrvBrkActvSta : 2;
        uint16 reserved1 : 1;
        uint8  SAS_SpdVal;
        sint16 SAS_AnglVal;
        uint8  VCU_AccPedDepVal;
        uint8  VCU_DrvModOpSta : 4;
        uint8  VCU_EvDrvRdySta : 2;
        uint8  reserved2 : 2;
        uint8  reserved3;
    } signal;
} typBswCanMsg_RT1_20;

typedef union {
    uint8 byte[8];
    struct __packed__ {
        uint8 DATC_OutTempSnsrVal;
        uint8 BCM_Ign2InSta   : 2;
        uint8 BCM_AccInSta    : 2;
        uint8 BCM_Ign1InSta   : 2;
        uint8 reserved1       : 2;
        uint8 CLU_DrvngModSwSta : 4;
        uint8 reserved2       : 4;
        uint8 CLU_OutTempCSta;
        sint16 xEV_BattCurrVal;
        uint16 reserved3;
    } signal;
} typBswCanMsg_RT1_200;

typedef union{
	uint8 byte[16];
	struct __packed__{
		uint8 AlvCnt2Val;
		uint32 DiagErrorFlags;
		sint16 target_torque      : 12;
		uint16 reserved1      	  : 4;
		sint8 Temperature;
		uint16 InputHVoltage     : 10;
		uint16 reserved2      	 : 6;
		sint16 SEA_Angle      	 : 12;
		uint16 reserved3      	 : 4;
		sint16 estTorque      	 : 12;
		uint16 reserved4      	 : 4;
		uint16 reserved5;
	}signal;
}typBswCanMsg_ARS1;

extern uint8 ShrHWIA_BswCan_GetMsg(uint8 msg_index, uint8 *dlc, uint8 *data);
extern uint8 ShrHWIA_BswCan_SetMsg(uint8 msg_index, uint8 dlc, uint8 *data);
extern uint8 ShrHWIA_BswCan_GetState_Busoff(uint8 can_ch);
extern uint8 ShrHWIA_BswCan_GetState_Timeout(uint8 msg_index);
extern void ShrHWIA_BswCan_SetTimeoutMax(uint8 msg_index,uint32 timeout_max);
extern void ShrHWIA_BswCan_SetCh0CanDisable(uint8 disable);


#endif /* BSWCAN_H_ */
