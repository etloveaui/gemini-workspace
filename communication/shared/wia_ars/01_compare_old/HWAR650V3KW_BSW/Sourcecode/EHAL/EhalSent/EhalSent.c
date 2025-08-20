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

#define HAR3930 	(0)

typEhalSent_Count vEhalSent_Count;
uint8 vEhalSent_Testcase;
typEhalSent_ChanStatusType vHar3930_Stat;
typEhalSent_INTSTAT vHar3930_Intstat;
uint16 vHar3930_PosData;
Std_ReturnType vReadGlitchFilterStatus;

uint16 Har3930_ReadData(void)
{
	uint32 receiveddata = 0;
	uint16 convertdata = 0;

	/* SENT DATA Receive */
	receiveddata = Sent_ReadData(HAR3930);

	convertdata = (uint16)(((receiveddata & 0xF00) >> 8)
						  | (receiveddata & 0x0F0)
						  | ((receiveddata & 0x00F) << 8));

	return convertdata;
}

void Har3930_Init(void)
{
	Sent_SetChannel(HAR3930, SENT_ENABLE);
}

void Har3930_Task_1ms(void)
{
	vEhalSent_Count.taskcnt++;
//	Sent_ReadChannelStatus(HAR3930, &vHar3930_Stat);
//	vHar3930_Intstat.reg = vHar3930_Stat.IntStat;
}

void Har3930_Task_10ms(void)
{
	;
}

void Har3930_Test_10ms(void)
{
	vEhalSent_Count.testcnt++;

	switch(vEhalSent_Testcase) {
	case 0:
//		Sent_ReadChannelStatus(HAR3930, &vHar3930_Stat);
//		vHar3930_Intstat.reg = vHar3930_Stat.IntStat;
		vEhalSent_Testcase = 0;
		break;
	case 1:
		Sent_Init(&Sent_Config);
		vEhalSent_Testcase = 0;
		break;
	case 2:
		Sent_SetChannel(0, SENT_ENABLE);//
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
		Dio_WriteChannel(EHAL_DIO_PORT_14_0, 1);
		vEhalSent_Testcase = 0;
		break;
	case 8:
//		Sent_ReadChannelStatus(HAR3930, &vHar3930_Stat);
//		vHar3930_Intstat.reg = vHar3930_Stat.IntStat;
		vEhalSent_Testcase = 0;
		break;
	default:
		vEhalSent_Testcase = 0;
		break;
	}

}


