/*
 * EhalDio.c
 *
 *  Created on: 2022. 3. 7.
 *      Author: dell
 */
#include "EhalDio.h"
#include "Dio.h"
#include "IfxPort_reg.h"

typedef struct{
	uint8 A;
}typEhalDio_ReadTest;

typedef struct{
	uint8 A;
}typEhalDio_WriteTest;

typEhalDio_ReadTest vEhalDio_ReadTest;
typEhalDio_WriteTest vEhalDio_WriteTest;

#include "Dio.h"

typedef struct{
	uint8 Testcase;
	Dio_LevelType ChannelLevel;
	Std_VersionInfoType VersionInfo;
	Dio_PortLevelType GroupLevel;
	uint8 Flip;
	uint32 Testcount;
}typEhalDio_Test;
typEhalDio_Test vEhalDio_Test;

void EhalDio_Test_10ms(void) {
	vEhalDio_Test.Testcount++;
	switch(vEhalDio_Test.Testcase) {
	case 0:

		vEhalDio_Test.Testcase = 0;
		break;
	case 1:
		// Flip channel state
		if(vEhalDio_Test.Testcount % 50 == 0){
			vEhalDio_Test.ChannelLevel = Dio_FlipChannel(EHAL_DIO_PMIC_WDI);

		}
		else{

		}
		vEhalDio_Test.Testcase = 1;
		break;

	case 2:
		// Get version info
		//            Dio_GetVersionInfo(&vEhalDio_VersionInfo);
		vEhalDio_Test.Testcase = 0;
		break;

	case 3:
		// Write to port with mask
		//            Dio_MaskedWritePort(DIO_PORT_2, 0x0F, 0xF0);
		vEhalDio_Test.Testcase = 0;
		break;

	case 4:
		// Read channel state
		vEhalDio_Test.ChannelLevel = Dio_ReadChannel(EHAL_DIO_TRANS_EN);
		vEhalDio_Test.Testcase = 0;
		break;

	case 5:
		// Read group of channels
		//		vEhalDio_GroupLevel = Dio_ReadChannelGroup(DioConf_DioChannelGroup_DioChannelGroup_LED);
		vEhalDio_Test.Testcase = 0;
		break;

	case 6:
		// Read full port state
		vEhalDio_Test.GroupLevel = Dio_ReadPort(DioConf_DioPort_DioPort_11);
		vEhalDio_Test.Testcase = 0;
		break;

	case 7:
		// Write value to channel
		//            Dio_WriteChannel(DioConf_DioChannel_TRB_LED, STD_HIGH);
		vEhalDio_Test.Flip ^= 1;
		Dio_WriteChannel(EHAL_DIO_TRANS_EN, vEhalDio_Test.Flip);
		vEhalDio_Test.ChannelLevel = Dio_ReadChannel(EHAL_DIO_TRANS_EN);
		vEhalDio_Test.Testcase = 0;
		break;

	case 8:
		Dio_WriteChannel(EHAL_DIO_TRANS_EN, 1);
		vEhalDio_Test.ChannelLevel = Dio_ReadChannel(EHAL_DIO_TRANS_EN);
		vEhalDio_Test.Testcase = 0;
		break;
	case 9:
		Dio_WriteChannel(EHAL_DIO_TRANS_EN, 0);
		vEhalDio_Test.ChannelLevel = Dio_ReadChannel(EHAL_DIO_TRANS_EN);
		vEhalDio_Test.Testcase = 0;
		break;
		break;

	default:
		vEhalDio_Test.Testcase = 0;
		break;
	}
}

