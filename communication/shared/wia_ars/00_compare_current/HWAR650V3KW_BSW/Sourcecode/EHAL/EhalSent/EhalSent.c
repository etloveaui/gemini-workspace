/*
 * EhalSent.c
 *
 *  Created on: 2025. 2. 6.
 *      Author: eunta
 */

#include "IfxStm_reg.h"
#include "EhalDio.h"
#include "Dio.h"
#include "_Conf/Global_Config.h"
#include "EhalSent.h"
#include "IfxStm_reg.h"

uint8 vEhalSent_Testcase;
uint8 vEhalSent_ChanFrameLen;

//uint8 vEhalSent_SerialID;
//uint16 vEhalSent_Serialout_data;
//uint32 vEhalSent_Serialout_timestamp;
//Std_ReturnType vEhalSent_Return;

//Sent_ChanStatusType vEhalSent_Stat;
//typEhalSent_INTSTAT vHar3930_Intstat;
//uint16 vHar3930_PosData;
//Std_ReturnType vReadGlitchFilterStatus;

//#define SERIAL_DATA_COUNT 100
//
//typEhalSent_Data vEhalSent_DataTest;
//uint32 vEhalSent_ReceivedTest;
//uint32 vEhalSent_ReceivedTestSerial[SERIAL_DATA_COUNT];
//uint8 vEhalSent_SerialIndex;
//uint8 vEhalSent_SerialMode;
//boolean vEhalSent_SerialDone = FALSE;
//
//uint16 vEhalSent_SerialData[SERIAL_DATA_COUNT];
//uint16 vEhalSent_SerialMsgId[SERIAL_DATA_COUNT];
//uint16 vEhalSent_SerialCrc[SERIAL_DATA_COUNT];
//uint16 vEhalSent_SerialConfiguration[SERIAL_DATA_COUNT];
//static uint8 vEhalSent_prevMsgId = 0xFF;

static typEhalSent_SlowCh vEhalSent_SlowChDb[SLOW_ID_MAX];

static inline sint8 EhalSent_MapId(uint8 id)
{
	switch(id)
	{
	case 0x01: return IDX_01; case 0x03: return IDX_03; case 0x05: return IDX_05; case 0x06: return IDX_06;
	case 0x07: return IDX_07; case 0x08: return IDX_08; case 0x09: return IDX_09; case 0x0A: return IDX_0A;
	case 0x23: return IDX_23; case 0x24: return IDX_24;
	case 0x29: return IDX_29; case 0x2A: return IDX_2A; case 0x2B: return IDX_2B; case 0x2C: return IDX_2C;
	case 0x90: return IDX_90; case 0x91: return IDX_91; case 0x92: return IDX_92; case 0x93: return IDX_93;
	case 0x94: return IDX_94; case 0x95: return IDX_95; case 0x96: return IDX_96; case 0x97: return IDX_97;
	default:   return -1;
	}
}

void EhalSent_StoreDb(uint8 id, uint16 data, uint32 tick)
{
	sint8 idx = EhalSent_MapId(id);
	if(idx < 0) {
		return;
	}
	else{
		vEhalSent_SlowChDb[idx].id      = id;
		vEhalSent_SlowChDb[idx].data    = data;
		vEhalSent_SlowChDb[idx].rxtimestamp = tick;
		vEhalSent_SlowChDb[idx].valid   = 1U;
	}
}

void EhalSent_ReadSerialData(void)
{
	Sent_RxSerialDataType serialdata;
	uint32 cur_tick;

	Sent_ReadSerialData(SENT_CHANNEL_NUM,&serialdata);
	cur_tick = STM0_TIM0.U;

	switch (serialdata.MsgId) {
	case 0x06:
		serialdata.Data &= 0x000F;   /* keep only lower 4 bits (REV[3:0]) */
		break;
	case 0x24:
		serialdata.Data &= 0x00FF;   /* keep only lower 8 bits (SSI[7:0]) */
		break;
	default:
		/* no masking needed */
		break;
	}

	EhalSent_StoreDb(serialdata.MsgId, serialdata.Data, cur_tick);

	//	if(serialdata.MsgId != vEhalSent_prevMsgId){
	//		vEhalSent_prevMsgId = serialdata.MsgId;
	//		vEhalSent_SerialData[vEhalSent_SerialIndex] = serialdata.Data;
	//		vEhalSent_SerialMsgId[vEhalSent_SerialIndex] = serialdata.MsgId;
	//		vEhalSent_SerialCrc[vEhalSent_SerialIndex] = serialdata.Crc;
	//		vEhalSent_SerialConfiguration[vEhalSent_SerialIndex] = serialdata.Configuration;
	//		vEhalSent_SerialIndex = (vEhalSent_SerialIndex + 1) % SERIAL_DATA_COUNT;
	//	}
	//	else{
	//		//no action
	//	}
}

/*----------------------------------------------------------------------------*
 *  Retrieve latest value by ID                                               *
 *  out_data    : raw data value                                              *
 *  out_ts_tick : STM0 tick timestamp					                      *
 *----------------------------------------------------------------------------*/
Std_ReturnType EhalSent_GetSerialData(uint8 id, uint16* out_data, uint32* out_timestamp)
{
	sint8 idx = EhalSent_MapId(id);
	if(idx < 0 || vEhalSent_SlowChDb[idx].valid == 0U){
		return E_NOT_OK;
	}
	else{
		*out_data    = vEhalSent_SlowChDb[idx].data;
		*out_timestamp = vEhalSent_SlowChDb[idx].rxtimestamp;

		/* Consume�릓nce: clear valid flag */
		vEhalSent_SlowChDb[idx].valid = 0U;

		return E_OK;
	}
}


typEhalSent_Data EhalSent_ReadData(void)
{
	uint32 receiveddata = 0;
	typEhalSent_Data result = {0};

	/* Receive SENT DATA */
	receiveddata = Sent_ReadData(SENT_CHANNEL_NUM);
	result.flamelen = vEhalSent_ChanFrameLen;

	/* Process based on frame length */
	if (vEhalSent_ChanFrameLen == FRAME_LEN_HAL3930_H2) {
		/* Process 3-nibble (12-bit) legacy data */
		result.h2data = (uint16)(
				((receiveddata & 0xF00) >> 8) |
				(receiveddata & 0x0F0) |
				((receiveddata & 0x00F) << 8)
		);
	}
	else if (vEhalSent_ChanFrameLen == FRAME_LEN_MLX90513_H7) {
		/* Process 6-nibble H.7 mode data */
		/* Convert 16-bit CH1 data (4 nibbles) */
		result.h7data.channel1 = (uint16)(
				((receiveddata & 0xFFFF0000) >> 16)   // CH1 MSN (bits 20-23) -> bits 0-3
		);

		/* Convert 8-bit CH2 data (2 nibbles) */
		/* T[�꼦]=T[K]�닋273.15=(raw_code+220)�닋273.15=raw_code�닋53.15 */
		result.h7data.channel2 = (uint8)(
				//				((receiveddata & 0x0000FF00) >> 8)
				((receiveddata & 0x0000F000) >> 12) |
				((receiveddata & 0x00000F00) >> 4)
		);
	}
	else{
		//no action
	}

	return result;
}

void EhalSent_Init(void)
{
	Sent_SetChannel(SENT_CHANNEL_NUM, SENT_ENABLE);
	vEhalSent_ChanFrameLen = Sent_Config.SentCorePtr[0]->Sent_ChannelConfig->ChanFrameLen;

	/* init DB */
	for (int i = 0; i < SLOW_ID_MAX; ++i) {
		vEhalSent_SlowChDb[i].valid = 0U;
	}
}

void EhalSent_Test_1ms(void)
{
	switch(vEhalSent_Testcase) {
	case 0:
		//		Sent_ReadSerialData(SENT_CHANNEL_NUM,&vHar3930_RxSerialData);
		//		vEhalSent_DataTest = EhalSent_ReadData();
		//		Sent_ReadChannelStatus(SENT_CHANNEL_NUM, &vEhalSent_Stat);
		//		vEhalSent_ReceivedTestSerial = SENT_CHANNEL[6].SDS.B;
//		EhalSent_ReadSerialData();
//		vEhalSent_Return = EhalSent_GetSerialData(vEhalSent_SerialID, &vEhalSent_Serialout_data, &vEhalSent_Serialout_timestamp);
		vEhalSent_Testcase = 0;
		break;
	case 1:
		Sent_Init(&Sent_Config);
		vEhalSent_Testcase = 0;
		break;
	case 2:
		Sent_SetChannel(SENT_CHANNEL_NUM, SENT_ENABLE);//
		vEhalSent_Testcase = 0;
		break;
	case 3:
		SENT_CH0_INTCLR.B.RBI = 1;
		SENT_CH0_INTCLR.B.FRI = 1;
		SENT_CH6_INTCLR.B.RBI = 1;
		SENT_CH6_INTCLR.B.FRI = 1;
		vEhalSent_Testcase = 0;
		break;
	case 4:
		//		vReadGlitchFilterStatus = Sent_ReadGlitchFilterStatus(0);
		vEhalSent_Testcase = 0;
		break;
	case 5:
		//		Sent_ReadChannelStatus(0, &vHar3930_Stat);
		vEhalSent_Testcase = 0;
		break;
	case 6:
		//		vHar3930_PosData = Har3930_ReadData();
		vEhalSent_Testcase = 0;
		break;
	case 7:
//		Dio_WriteChannel(EHAL_DIO_PORT_14_0, 1);
		vEhalSent_Testcase = 0;
		break;
	case 8:

		vEhalSent_Testcase = 0;
		break;
	default:
		vEhalSent_Testcase = 0;
		break;
	}

}
