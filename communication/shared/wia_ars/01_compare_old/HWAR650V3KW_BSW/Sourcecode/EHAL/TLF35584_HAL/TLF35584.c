/*
 * TLF35584.c
 *
 *  Created on: 2022. 6. 30.
 *      Author: eunta
 */

/*******************************************************************************
 **                      Includes                                              **
 *******************************************************************************/
#include "TLF35584.h"
#include "Spi.h"
#include "Dio.h"
#include "EHAL/EhalDio/EhalDio.h"
#include "EHAL/EhalAdc/EhalAdc.h"
#include "IfxGtm_reg.h"
#include "Std_Types.h"

/*******************************************************************************
 **                      Global Variable Definitions                           **
 *******************************************************************************/

//Process Variables
typTLF35584Panels vTLF35584_Panels;
typTLF35584Panels vTLF35584_Panels_bak;
Ifx_GTM_OCDS_OCS vGTM_OCDS_OCS;
uint32 vTLF35584_WdErrCnt;

//Functional Watchdog response definition
const uint8 vTLF35584_FwdResp0Table[16]=
{      /* QUEST, RESP0*/
		/* 0 */  0x00,
		/* 1 */  0x4F,
		/* 2 */  0x16,
		/* 3 */  0x59,
		/* 4 */  0x8A,
		/* 5 */  0xC5,
		/* 6 */  0x9C,
		/* 7 */  0xD3,
		/* 8 */  0x2D,
		/* 9 */  0x62,
		/* 10 */ 0x3B,
		/* 11 */ 0x74,
		/* 12 */ 0xA7,
		/* 13 */ 0xE8,
		/* 14 */ 0xB1,
		/* 15 */ 0xFE,
};

//Spi Variables
uint16	vTLF35584_SpiTxMsg;
uint16	vTLF35584_SpiRxMsg;
uint8	vTLF35584_SpiRxData;
uint32	vTLF35584_job_count;
uint32	vTLF35584_seq_count;
uint32 vTLF35584_SpiReadCounter = 0;

//******************************************************************************
// @Function	 	void TLF35584_ConfigureSpi(void)
// @Description		TLF35584 SPI Setup
// @Return Value	None
// @Parameters    	None
//******************************************************************************

void TLF35584_ConfigureSpi(void)
{
	Std_ReturnType spi_return;

	spi_return = Spi_SetupEB(SpiConf_SpiChannel_SpiChannel_0,
			(Spi_DataBufferType *)&vTLF35584_SpiTxMsg,
			(Spi_DataBufferType *)&vTLF35584_SpiRxMsg,
			1);

	if (spi_return != E_OK) {

	}
	else{

	}

}/*End of TLF35584_ConfigureSpi(void)*/

//******************************************************************************
// @Function	 	uint16 TLF35584_ParityGeneration(uint16 Data)
// @Description   	To Calculate Data Frame Parity bit
// @Return Value	n (ParityBit)
// @Parameters    	uint16 Data
//******************************************************************************
//uint16 TLF35584_ParityGeneration(uint16 Data)
//{
//	uint16 n = 0;
//	while (Data)
//	{
//		Data &= Data-1;
//		++n;
//	}
//	while (n > 1)
//	{
//		n = n-2;
//	}
//	return (n);
//} /*End of TLF35584_ParityGeneration()*/

uint16 TLF35584_ParityGeneration(uint16 Data)
{
	Data ^= Data >> 8;
	Data ^= Data >> 4;
	Data ^= Data >> 2;
	Data ^= Data >> 1;
	return Data & 1;
}

//**********************************************************************************************
// @Function	 	void TLF35584_Communication(uint16 Mode, uint8 Address, uint8 Data)
// @Description   	For communication with TLF35584 , User can read and write Data to TLF by API
// @Return Value	None
// @Parameters    	Mode (0-Read,1-Write), TLF Address , Data
//**********************************************************************************************
void TLF35584_Communication(uint16 Mode, uint8 Address, uint8 Data)
{
	uint32 spi_try_count = 0;
	Spi_SeqResultType spi_seq_result;
	vTLF35584_SpiTxMsg = (  (Mode<<15) |          /* Write command */
			(Address << 9) |        /* Address */
			(Data << 1) );          /* Data */
	vTLF35584_SpiTxMsg |= TLF35584_ParityGeneration(vTLF35584_SpiTxMsg); /* Parity */
	Spi_AsyncTransmit(SpiConf_SpiSequence_SpiSequence_0);				//Improvement
	while(spi_try_count < TLF35584_SPI_TIMEOUT_CNT){
		spi_seq_result = Spi_GetSequenceResult(SpiConf_SpiSequence_SpiSequence_0);
		if(spi_seq_result == SPI_SEQ_OK){
			vTLF35584_SpiRxData = (vTLF35584_SpiRxMsg >> 1) & 0x00FF;
			//			break;
			return;
		}
		else{
			spi_try_count++;
		}
	}

	//	vTLF35584_SpiRxData = (vTLF35584_SpiRxMsg >> 1) & 0x00FF;
} /*End of TLF35584_Communication()*/

//******************************************************************************
// @Function	 	void TLF35584_UnlockProtectedRegister(void)
// @Description   	Unlock Protected register
// @Return Value	None
// @Parameters    	None
//******************************************************************************
void TLF35584_UnlockProtectedRegister(void)
{	/* UNLOCK - Send password sequence */
	TLF35584_Communication(PMIC_WRITE,PROTCFG, PROTECTION_UNLOCK_KEY1);
	TLF35584_Communication(PMIC_WRITE,PROTCFG, PROTECTION_UNLOCK_KEY2);
	TLF35584_Communication(PMIC_WRITE,PROTCFG, PROTECTION_UNLOCK_KEY3);
	TLF35584_Communication(PMIC_WRITE,PROTCFG, PROTECTION_UNLOCK_KEY4);
} /*End of TLF35584_UnlockProtectedRegister()*/

//******************************************************************************
// @Function	 	void TLF35584_LockProtectedRegister(void)
// @Description   	Lock Protected register
// @Return Value	None
// @Parameters    	None
//******************************************************************************
void TLF35584_LockProtectedRegister(void)
{	/* LOCK - Send password sequence */
	TLF35584_Communication(PMIC_WRITE,PROTCFG, PROTECTION_LOCK_KEY1);
	TLF35584_Communication(PMIC_WRITE,PROTCFG, PROTECTION_LOCK_KEY2);
	TLF35584_Communication(PMIC_WRITE,PROTCFG, PROTECTION_LOCK_KEY3);
	TLF35584_Communication(PMIC_WRITE,PROTCFG, PROTECTION_LOCK_KEY4);
} /*End of TLF35584_LockProtectedRegister()*/

//****************************************************************************
// Notification function for TLF35584 communication
//****************************************************************************
void SpiJob_0_EndNotification(void)
{
	vTLF35584_job_count++;
}

void SpiSeq_0_EndNotification(void)
{
	vTLF35584_seq_count++;
}

//******************************************************************************
// @Function	 	Spi Communication Read function for TLF35584 communication
// @Description
// @Return Value
// @Parameters
//******************************************************************************

//static inline uint8 TLF35584_ReadRegister(uint8 address) {
//    TLF35584_Communication(PMIC_READ, address, 0x0);
//    return vTLF35584_SpiRxData;
//}
//
//static inline void TLF35584_WriteRegister(uint8 address, uint8 data) {
//    TLF35584_Communication(PMIC_WRITE, address, data);
//}

void TLF35584_Spi_Read_DEVCFG0_0x00()
{
	TLF35584_Communication(PMIC_READ,DEVCFG0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_DEVCFG0_0x00.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_DEVCFG1_0x01()
{
	TLF35584_Communication(PMIC_READ,DEVCFG1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_DEVCFG1_0x01.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_DEVCFG2_0x02()
{
	TLF35584_Communication(PMIC_READ,DEVCFG2,0x0);
	vTLF35584_Panels.read_reg.TLF35584_DEVCFG2_0x02.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_PROTCFG_0x03()
{
	TLF35584_Communication(PMIC_READ,PROTCFG,0x0);
	vTLF35584_Panels.read_reg.TLF35584_PROTCFG_0x03.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_SYSPCFG0_0x04()
{
	TLF35584_Communication(PMIC_READ,SYSPCFG0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_SYSPCFG0_0x04.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_SYSPCFG1_0x05()
{
	TLF35584_Communication(PMIC_READ,SYSPCFG1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_SYSPCFG1_0x05.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_WDCFG0_0x06()
{
	TLF35584_Communication(PMIC_READ,WDCFG0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_WDCFG0_0x06.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_WDCFG1_0x07()
{
	TLF35584_Communication(PMIC_READ,WDCFG1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_WDCFG1_0x07.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_FWDCFG_0x08()
{
	TLF35584_Communication(PMIC_READ,FWDCFG,0x0);
	vTLF35584_Panels.read_reg.TLF35584_FWDCFG_0x08.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_WWDCFG0_0x09()
{
	TLF35584_Communication(PMIC_READ,WWDCFG0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_WWDCFG0_0x09.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_WWDCFG1_0x0A()
{
	TLF35584_Communication(PMIC_READ,WWDCFG1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_WWDCFG1_0x0A.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_RSYSPCFG0_0x0B()
{
	TLF35584_Communication(PMIC_READ,RSYSPCFG0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_RSYSPCFG0_0x0B.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_RSYSPCFG1_0x0C()
{
	TLF35584_Communication(PMIC_READ,RSYSPCFG1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_RSYSPCFG1_0x0C.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_RWDCFG0_0x0D()
{
	TLF35584_Communication(PMIC_READ,RWDCFG0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_RWDCFG0_0x0D.byte = vTLF35584_SpiRxData;

	vTLF35584_Panels.watchdogs.WdTime.WdCyc = vTLF35584_Panels.read_reg.TLF35584_RWDCFG0_0x0D.signal.WDCYC;
	vTLF35584_Panels.watchdogs.Wwd.TrigSelect = vTLF35584_Panels.read_reg.TLF35584_RWDCFG0_0x0D.signal.WWDTSEL;
	vTLF35584_Panels.watchdogs.Wwd.Enable = vTLF35584_Panels.read_reg.TLF35584_RWDCFG0_0x0D.signal.WWDEN;
	vTLF35584_Panels.watchdogs.Wwd.Treshold = vTLF35584_Panels.read_reg.TLF35584_RWDCFG0_0x0D.signal.WWDETHR;
	vTLF35584_Panels.watchdogs.Fwd.Enable = vTLF35584_Panels.read_reg.TLF35584_RWDCFG0_0x0D.signal.FWDEN;
}

void TLF35584_Spi_Read_RWDCFG1_0x0E()
{
	TLF35584_Communication(PMIC_READ,RWDCFG1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_RWDCFG1_0x0E.byte = vTLF35584_SpiRxData;
	vTLF35584_Panels.watchdogs.Fwd.Treshold = vTLF35584_Panels.read_reg.TLF35584_RWDCFG1_0x0E.signal.FWDETHR;
}

void TLF35584_Spi_Read_RFWDCFG_0x0F()
{
	TLF35584_Communication(PMIC_READ,RFWDCFG,0x0);
	vTLF35584_Panels.read_reg.TLF35584_RFWDCFG_0x0F.byte = vTLF35584_SpiRxData;
	vTLF35584_Panels.watchdogs.WdTime.FwdHb = vTLF35584_Panels.read_reg.TLF35584_RFWDCFG_0x0F.signal.WDHBTP;
}

void TLF35584_Spi_Read_RWWDCFG0_0x10()
{
	TLF35584_Communication(PMIC_READ,RWWDCFG0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_RWWDCFG0_0x10.byte = vTLF35584_SpiRxData;
	vTLF35584_Panels.watchdogs.WdTime.WwdCw = vTLF35584_Panels.read_reg.TLF35584_RWWDCFG0_0x10.signal.CW;
}

void TLF35584_Spi_Read_RWWDCFG1_0x11()
{
	TLF35584_Communication(PMIC_READ,RWWDCFG1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_RWWDCFG1_0x11.byte = vTLF35584_SpiRxData;
	vTLF35584_Panels.watchdogs.WdTime.WwdOw = vTLF35584_Panels.read_reg.TLF35584_RWWDCFG1_0x11.signal.OW;
}

void TLF35584_Spi_Read_WKTIMCFG0_0x12()
{
	TLF35584_Communication(PMIC_READ,WKTIMCFG0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_WKTIMCFG0_0x12.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_WKTIMCFG1_0x13()
{
	TLF35584_Communication(PMIC_READ,WKTIMCFG1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_WKTIMCFG1_0x13.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_WKTIMCFG2_0x14()
{
	TLF35584_Communication(PMIC_READ,WKTIMCFG2,0x0);
	vTLF35584_Panels.read_reg.TLF35584_WKTIMCFG2_0x14.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_DEVCTRL_0x15()
{
	TLF35584_Communication(PMIC_READ,DEVCTRL,0x0);
	vTLF35584_Panels.read_reg.TLF35584_DEVCTRL_0x15.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_DEVCTRLN_0x16()
{
	TLF35584_Communication(PMIC_READ,DEVCTRLN,0x0);
	vTLF35584_Panels.read_reg.TLF35584_DEVCTRLN_0x16.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_WWDSCMD_0x17()
{
	TLF35584_Communication(PMIC_READ,WWDSCMD,0x0);
	vTLF35584_Panels.read_reg.TLF35584_WWDSCMD_0x17.byte = vTLF35584_SpiRxData;
	vTLF35584_Panels.watchdogs.Wwd.TrigState = vTLF35584_Panels.read_reg.TLF35584_WWDSCMD_0x17.signal.TRIG_STATUS;
}

void TLF35584_Spi_Read_FWDRSP_0x18()
{
	TLF35584_Communication(PMIC_READ,FWDRSP,0x0);
	vTLF35584_Panels.read_reg.TLF35584_FWDRSP_0x18.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_FWDRSPSYNC_0x19()
{
	TLF35584_Communication(PMIC_READ,FWDRSPSYNC,0x0);
	vTLF35584_Panels.read_reg.TLF35584_FWDRSPSYNC_0x19.byte = vTLF35584_SpiRxData;
}

uint8 TLF35584_Spi_Read_SYSFAIL_0x1A()
{
	TLF35584_Communication(PMIC_READ,SYSFAIL,0x0);
	vTLF35584_Panels.read_reg.TLF35584_SYSFAIL_0x1A.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_SYSFAIL_0x1A.byte;
}

uint8 TLF35584_Spi_Read_INITERR_0x1B()
{
	TLF35584_Communication(PMIC_READ,INITERR,0x0);
	vTLF35584_Panels.read_reg.TLF35584_INITERR_0x1B.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_INITERR_0x1B.byte;
}

uint8 TLF35584_Spi_Read_IF_0x1C()
{
	TLF35584_Communication(PMIC_READ,IF,0x0);
	vTLF35584_Panels.read_reg.TLF35584_IF_0x1C.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_IF_0x1C.byte;
}

uint8 TLF35584_Spi_Read_SYSSF_0x1D()
{
	TLF35584_Communication(PMIC_READ,SYSSF,0x0);
	vTLF35584_Panels.read_reg.TLF35584_SYSSF_0x1D.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_SYSSF_0x1D.byte;
}

uint8 TLF35584_Spi_Read_WKSF_0x1E()
{
	TLF35584_Communication(PMIC_READ,WKSF,0x0);
	vTLF35584_Panels.read_reg.TLF35584_WKSF_0x1E.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_WKSF_0x1E.byte;
}

uint8 TLF35584_Spi_Read_SPISF_0x1F()
{
	TLF35584_Communication(PMIC_READ,SPISF,0x0);
	vTLF35584_Panels.read_reg.TLF35584_SPISF_0x1F.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_SPISF_0x1F.byte;
}

uint8 TLF35584_Spi_Read_MONSF0_0x20()
{
	TLF35584_Communication(PMIC_READ,MONSF0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_MONSF0_0x20.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_MONSF0_0x20.byte;
}

uint8 TLF35584_Spi_Read_MONSF1_0x21()
{
	TLF35584_Communication(PMIC_READ,MONSF1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_MONSF1_0x21.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_MONSF1_0x21.byte;
}

uint8 TLF35584_Spi_Read_MONSF2_0x22()
{
	TLF35584_Communication(PMIC_READ,MONSF2,0x0);
	vTLF35584_Panels.read_reg.TLF35584_MONSF2_0x22.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_MONSF2_0x22.byte;
}

uint8 TLF35584_Spi_Read_MONSF3_0x23()
{
	TLF35584_Communication(PMIC_READ,MONSF3,0x0);
	vTLF35584_Panels.read_reg.TLF35584_MONSF3_0x23.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_MONSF3_0x23.byte;
}

uint8 TLF35584_Spi_Read_OTFAIL_0x24()
{
	TLF35584_Communication(PMIC_READ,OTFAIL,0x0);
	vTLF35584_Panels.read_reg.TLF35584_OTFAIL_0x24.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_OTFAIL_0x24.byte;
}

uint8 TLF35584_Spi_Read_OTWRNSF_0x25()
{
	TLF35584_Communication(PMIC_READ,OTWRNSF,0x0);
	vTLF35584_Panels.read_reg.TLF35584_OTWRNSF_0x25.byte = vTLF35584_SpiRxData;
	return vTLF35584_Panels.read_reg.TLF35584_OTWRNSF_0x25.byte;
}

void TLF35584_Spi_Read_VMONSTAT_0x26()
{
	TLF35584_Communication(PMIC_READ,VMONSTAT,0x0);
	vTLF35584_Panels.read_reg.TLF35584_VMONSTAT_0x26.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_DEVSTAT_0x27()
{
	TLF35584_Communication(PMIC_READ,DEVSTAT,0x0);
	vTLF35584_Panels.read_reg.TLF35584_DEVSTAT_0x27.byte = vTLF35584_SpiRxData;
	//	vTLF35584_Panels.state_machine.CurrState = vTLF35584_Panels.read_reg.TLF35584_DEVSTAT_0x27.signal.STATE;
}

void TLF35584_Spi_Read_PROTSTAT_0x28()
{
	TLF35584_Communication(PMIC_READ,PROTSTAT,0x0);
	vTLF35584_Panels.read_reg.TLF35584_PROTSTAT_0x28.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_WWDSTAT_0x29()
{
	TLF35584_Communication(PMIC_READ,WWDSTAT,0x0);
	vTLF35584_Panels.read_reg.TLF35584_WWDSTAT_0x29.byte = vTLF35584_SpiRxData;
	vTLF35584_Panels.watchdogs.Wwd.ErrCnt = vTLF35584_Panels.read_reg.TLF35584_WWDSTAT_0x29.signal.WWDECNT;
}

void TLF35584_Spi_Read_FWDSTAT0_0x2A()
{
	TLF35584_Communication(PMIC_READ,FWDSTAT0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_FWDSTAT0_0x2A.byte = vTLF35584_SpiRxData;
	vTLF35584_Panels.watchdogs.Fwd.Quest = vTLF35584_Panels.read_reg.TLF35584_FWDSTAT0_0x2A.signal.FWDQUEST;
	vTLF35584_Panels.watchdogs.Fwd.MsgOk = vTLF35584_Panels.read_reg.TLF35584_FWDSTAT0_0x2A.signal.FWDRSPOK;
	vTLF35584_Panels.watchdogs.Fwd.RespCnt = vTLF35584_Panels.read_reg.TLF35584_FWDSTAT0_0x2A.signal.FWDRSPC;
}

void TLF35584_Spi_Read_FWDSTAT1_0x2B()
{
	TLF35584_Communication(PMIC_READ,FWDSTAT1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_FWDSTAT1_0x2B.byte = vTLF35584_SpiRxData;
	vTLF35584_Panels.watchdogs.Fwd.ErrCnt = vTLF35584_Panels.read_reg.TLF35584_FWDSTAT1_0x2B.signal.FWDECNT;
}

void TLF35584_Spi_Read_ABIST_CTRL0_0x2C()
{
	TLF35584_Communication(PMIC_READ,ABIST_CTRL0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_ABIST_CTRL0_0x2C.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_ABIST_CTRL1_0x2D()
{
	TLF35584_Communication(PMIC_READ,ABIST_CTRL1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_ABIST_CTRL1_0x2D.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_ABIST_SELECT0_0x2E()
{
	TLF35584_Communication(PMIC_READ,ABIST_SELECT0,0x0);
	vTLF35584_Panels.read_reg.TLF35584_ABIST_SELECT0_0x2E.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_ABIST_SELECT1_0x2F()
{
	TLF35584_Communication(PMIC_READ,ABIST_SELECT1,0x0);
	vTLF35584_Panels.read_reg.TLF35584_ABIST_SELECT1_0x2F.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_ABIST_SELECT2_0x30()
{
	TLF35584_Communication(PMIC_READ,ABIST_SELECT2,0x0);
	vTLF35584_Panels.read_reg.TLF35584_ABIST_SELECT2_0x30.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_BCK_FREQ_CHANGE_0x31()
{
	TLF35584_Communication(PMIC_READ,BCK_FREQ_CHANGE,0x0);
	vTLF35584_Panels.read_reg.TLF35584_BCK_FREQ_CHANGE_0x31.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_BCK_FRE_SPREAD_0x32()
{
	TLF35584_Communication(PMIC_READ,BCK_FRE_SPREAD,0x0);
	vTLF35584_Panels.read_reg.TLF35584_BCK_FRE_SPREAD_0x32.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_BCK_MAIN_CTRL_0x33()
{
	TLF35584_Communication(PMIC_READ,BCK_MAIN_CTRL,0x0);
	vTLF35584_Panels.read_reg.TLF35584_BCK_MAIN_CTRL_0x33.byte = vTLF35584_SpiRxData;
}

void TLF35584_Spi_Read_GTM_0x3F()
{
	TLF35584_Communication(PMIC_READ,GTM_TEST,0x0);
	vTLF35584_Panels.read_reg.TLF35584_GTM_0x3F.byte = vTLF35584_SpiRxData;
}

//******************************************************************************
// @Function	 	Spi Communication Write function for TLF35584 communication
// @Description
// @Return Value
// @Parameters
//******************************************************************************

void TLF35584_Spi_Write_DEVCFG0_0x00()
{
	TLF35584_Communication(PMIC_WRITE,DEVCFG0,vTLF35584_Panels.write_reg.TLF35584_DEVCFG0_0x00.byte);
}

void TLF35584_Spi_Write_DEVCFG1_0x01()
{
	TLF35584_Communication(PMIC_WRITE,DEVCFG1,vTLF35584_Panels.write_reg.TLF35584_DEVCFG1_0x01.byte);
}

void TLF35584_Spi_Write_DEVCFG2_0x02()
{
	TLF35584_Communication(PMIC_WRITE,DEVCFG2,vTLF35584_Panels.write_reg.TLF35584_DEVCFG2_0x02.byte);
}

void TLF35584_Spi_Write_SYSPCFG0_0x04()//Protection Register, Protected System configuration request 0
{
	TLF35584_Communication(PMIC_WRITE,SYSPCFG0,vTLF35584_Panels.write_reg.TLF35584_SYSPCFG0_0x04.byte);
}

void TLF35584_Spi_Write_SYSPCFG1_0x05()//Protection Register, Protected System configuration request 1
{
	TLF35584_Communication(PMIC_WRITE,SYSPCFG1,vTLF35584_Panels.write_reg.TLF35584_SYSPCFG1_0x05.byte);
}

void TLF35584_Spi_Write_WDCFG0_0x06()//Protection Register, Protected Watchdog configuration request 0
{
	TLF35584_Communication(PMIC_WRITE,WDCFG0,vTLF35584_Panels.write_reg.TLF35584_WDCFG0_0x06.byte);
}

void TLF35584_Spi_Write_WDCFG1_0x07()//Protection Register, Protected Watchdog configuration request 1
{
	TLF35584_Communication(PMIC_WRITE,WDCFG1,vTLF35584_Panels.write_reg.TLF35584_WDCFG1_0x07.byte);
}

void TLF35584_Spi_Write_FWDCFG_0x08()//Protection Register, Protected Functional watchdog configuration request
{
	TLF35584_Communication(PMIC_WRITE,FWDCFG,vTLF35584_Panels.write_reg.TLF35584_FWDCFG_0x08.byte);
}

void TLF35584_Spi_Write_WWDCFG0_0x09()//Protection Register, Protected Window watchdog configuration request 0
{
	TLF35584_Communication(PMIC_WRITE,WWDCFG0,vTLF35584_Panels.write_reg.TLF35584_WWDCFG0_0x09.byte);
}

void TLF35584_Spi_Write_WWDCFG1_0x0A()//Protection Register, Protected Window watchdog configuration request 1
{
	TLF35584_Communication(PMIC_WRITE,WWDCFG1,vTLF35584_Panels.write_reg.TLF35584_WWDCFG1_0x0A.byte);
}

void TLF35584_Spi_Write_WKTIMCFG0_0x12()
{
	TLF35584_Communication(PMIC_WRITE,WKTIMCFG0,vTLF35584_Panels.write_reg.TLF35584_WKTIMCFG0_0x12.byte);
}

void TLF35584_Spi_Write_WKTIMCFG1_0x13()
{
	TLF35584_Communication(PMIC_WRITE,WKTIMCFG1,vTLF35584_Panels.write_reg.TLF35584_WKTIMCFG1_0x13.byte);
}

void TLF35584_Spi_Write_WKTIMCFG2_0x14()
{
	TLF35584_Communication(PMIC_WRITE,WKTIMCFG2,vTLF35584_Panels.write_reg.TLF35584_WKTIMCFG2_0x14.byte);
}

void TLF35584_Spi_Write_DEVCTRL_0x15(uint8 data) //Request for device state transition, 1: INIT, 2: NORMAL, 3: SLEEP, 4: STANDBY, 5: WAKE
{
	vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.STATEREQ = data;
	vTLF35584_Panels.write_reg.TLF35584_DEVCTRLN_0x16.byte = ~vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.byte;
	TLF35584_Communication(PMIC_WRITE,DEVCTRL, vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.byte);
	TLF35584_Communication(PMIC_WRITE,DEVCTRLN, vTLF35584_Panels.write_reg.TLF35584_DEVCTRLN_0x16.byte);
}

void TLF35584_Spi_Write_WWDSCMD_0x17(uint8 data)
{
	vTLF35584_Panels.write_reg.TLF35584_WWDSCMD_0x17.byte = data;
	TLF35584_Communication(PMIC_WRITE,WWDSCMD,vTLF35584_Panels.write_reg.TLF35584_WWDSCMD_0x17.byte);
}

void TLF35584_Spi_Write_FWDRSP_0x18(uint8 data)
{
	vTLF35584_Panels.write_reg.TLF35584_FWDRSP_0x18.byte = data;
	TLF35584_Communication(PMIC_WRITE,FWDRSP,vTLF35584_Panels.write_reg.TLF35584_FWDRSP_0x18.byte);
}

void TLF35584_Spi_Write_FWDRSPSYNC_0x19(uint8 data)
{
	vTLF35584_Panels.write_reg.TLF35584_FWDRSPSYNC_0x19.byte = data;
	TLF35584_Communication(PMIC_WRITE,FWDRSPSYNC,vTLF35584_Panels.write_reg.TLF35584_FWDRSPSYNC_0x19.byte);
}

void TLF35584_Spi_Write_SYSFAIL_0x1A(uint8 data)//Failure status flags
{
	vTLF35584_Panels.write_reg.TLF35584_SYSFAIL_0x1A.signal.ABISTERR = data; //ABIST operation interrupted flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags
	vTLF35584_Panels.write_reg.TLF35584_SYSFAIL_0x1A.signal.INITF = data; //INIT failure flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags
	vTLF35584_Panels.write_reg.TLF35584_SYSFAIL_0x1A.signal.OTF = data; //Over temperature failure flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags, read OTFAIL for details
	vTLF35584_Panels.write_reg.TLF35584_SYSFAIL_0x1A.signal.VMONF = data; //Voltage monitor failure flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags, read MONSF0, MONSF1 and MONSF3 for details
	vTLF35584_Panels.write_reg.TLF35584_SYSFAIL_0x1A.signal.VOLTSELERR = data; //Double Bit error on voltage selection flag: 0=No fault, write 0 - no action, 1=Fault occurred, write 1 to clear the flags
	TLF35584_Communication(PMIC_WRITE,SYSFAIL,vTLF35584_Panels.write_reg.TLF35584_SYSFAIL_0x1A.byte);
}

void TLF35584_Spi_Write_INITERR_0x1B(uint8 data)//Init error status flags
{
	vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.signal.HARDRES = data; //Hard reset flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.signal.SOFTRES = data; //Soft reset flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.signal.ERRF = data; //MCU error monitor failure flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.signal.FWDF = data; //Functional watchdog error counter overflow failure flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.signal.WWDF = data; //Window watchdog error counter overflow failure flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.signal.VMONF = data; //Voltage monitor failure flag, 1:clear the flags
	TLF35584_Communication(PMIC_WRITE,INITERR,vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.byte);
}

void TLF35584_Spi_Write_IF_0x1C(uint8 data)//Interrupt flags
{
	vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.signal.INTMISS = 0; //READ ONLY, Interrupt not serviced in time flag, cleared by hardware when all other flags in IF are cleared.
	vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.signal.ABIST = data; //Requested ABIST operation performed flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.signal.OTF = data; //Over temperature failure interrupt flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.signal.OTW = data; //Over temperature warning interrupt flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.signal.MON = data; //Monitor interrupt flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.signal.SPI = data; //SPI interrupt flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.signal.WK = data; //Wake interrupt flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.signal.SYS = data; //System interrupt flag, 1:clear the flags
	TLF35584_Communication(PMIC_WRITE,IF,vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.byte);
}

void TLF35584_Spi_Write_SYSSF_0x1D(uint8 data)//System status flags
{
	vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.signal.NO_OP = data; //State transition request failure flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.signal.TRFAIL = data; //Transition to low power failed flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.signal.ERRMISS = data; //MCU error miss status flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.signal.FWDE = data; //Functional watchdog error interrupt flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.signal.WWDE = data; //Window watchdog error interrupt flag, 1:clear the flags
	vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.signal.CFGE = data; //Protected configuration double bit error flag, 1:clear the flags
	TLF35584_Communication(PMIC_WRITE,SYSSF,vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.byte);
}

void TLF35584_Spi_Write_WKSF_0x1E(uint8 data)//Wake up status flags
{
	vTLF35584_Panels.write_reg.TLF35584_WKSF_0x1E.signal.CMON = data;
	vTLF35584_Panels.write_reg.TLF35584_WKSF_0x1E.signal.ENA = data;
	vTLF35584_Panels.write_reg.TLF35584_WKSF_0x1E.signal.WAK = data;
	vTLF35584_Panels.write_reg.TLF35584_WKSF_0x1E.signal.WKSPI = data;
	vTLF35584_Panels.write_reg.TLF35584_WKSF_0x1E.signal.WKTIM = data;
	TLF35584_Communication(PMIC_WRITE,WKSF,vTLF35584_Panels.write_reg.TLF35584_WKSF_0x1E.byte);
}
void TLF35584_Spi_Write_SPISF_0x1F(uint8 data)//SPI status flags
{
	vTLF35584_Panels.write_reg.TLF35584_SPISF_0x1F.signal.ADDRE = data;
	vTLF35584_Panels.write_reg.TLF35584_SPISF_0x1F.signal.DURE = data;
	vTLF35584_Panels.write_reg.TLF35584_SPISF_0x1F.signal.LENE = data;
	vTLF35584_Panels.write_reg.TLF35584_SPISF_0x1F.signal.LOCK = data;
	vTLF35584_Panels.write_reg.TLF35584_SPISF_0x1F.signal.PARE = data;
	TLF35584_Communication(PMIC_WRITE,SPISF,vTLF35584_Panels.write_reg.TLF35584_SPISF_0x1F.byte);
}

void TLF35584_Spi_Write_MONSF0_0x20(uint8 data)//Monitor status flags 0(short to ground status)
{
	vTLF35584_Panels.write_reg.TLF35584_MONSF0_0x20.signal.PREGSG = data; //Pre-regulator voltage short to ground status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF0_0x20.signal.UCSG = data; //uC LDO short to ground status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF0_0x20.signal.STBYSG = data; //Standby LDO short to ground status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF0_0x20.signal.VCORESG = data; //Core voltage short to ground status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF0_0x20.signal.COMSG = data; //Communication LDO short to ground status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF0_0x20.signal.VREFSG = data; //Voltage reference short to ground status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF0_0x20.signal.TRK1SG = data; //Tracker1 short to ground status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF0_0x20.signal.TRK2SG = data; //Tracker2 short to ground status flag
	TLF35584_Communication(PMIC_WRITE,MONSF0,vTLF35584_Panels.write_reg.TLF35584_MONSF0_0x20.byte);
}

void TLF35584_Spi_Write_MONSF1_0x21(uint8 data)//Monitor status flags 1(over voltage status)
{
	vTLF35584_Panels.write_reg.TLF35584_MONSF1_0x21.signal.PREGOV = data; //Pre-regulator voltage over voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF1_0x21.signal.UCOV = data; //uC LDO over voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF1_0x21.signal.STBYOV = data; //Standby LDO over voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF1_0x21.signal.VCOREOV = data; //Core voltage over voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF1_0x21.signal.COMOV = data; //Communication LDO over voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF1_0x21.signal.VREFOV = data; //Voltage reference over voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF1_0x21.signal.TRK1OV = data; //Tracker1 over voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF1_0x21.signal.TRK2OV	 = data; //Tracker2 over voltage status flag
	TLF35584_Communication(PMIC_WRITE,MONSF1,vTLF35584_Panels.write_reg.TLF35584_MONSF1_0x21.byte);
}

void TLF35584_Spi_Write_MONSF2_0x22(uint8 data)//Monitor status flags 2(under voltage status)
{
	vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.signal.PREGUV = data;//Pre-regulator voltage under voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.signal.UCUV = data;//uC LDO under voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.signal.STBYUV = data;//Standby LDO under voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.signal.VCOREUV = data;//Core voltage under voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.signal.COMUV = data;//Communication LDO under voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.signal.VREFUV = data;//Voltage reference under voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.signal.TRK1UV = data;//Tracker1 under voltage status flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.signal.TRK2UV = data;//Tracker2 under voltage status flag
	TLF35584_Communication(PMIC_WRITE,MONSF2,vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.byte);
}

void TLF35584_Spi_Write_MONSF3_0x23(uint8 data)//Monitor status flags 3
{
	vTLF35584_Panels.write_reg.TLF35584_MONSF3_0x23.signal.VBATOV = data;//Supply voltage VSx over voltage flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF3_0x23.signal.BG12UV = data;//Bandgap comparator under voltage condition flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF3_0x23.signal.BG12OV = data;//Bandgap comparator over voltage condition flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF3_0x23.signal.BIASLOW = data;//Bias current too low flag
	vTLF35584_Panels.write_reg.TLF35584_MONSF3_0x23.signal.BIASHI	 = data;//Bias current too high flag
	TLF35584_Communication(PMIC_WRITE,MONSF3,vTLF35584_Panels.write_reg.TLF35584_MONSF3_0x23.byte);
}

void TLF35584_Spi_Write_OTFAIL_0x24(uint8 data)//Over temperature failure status flags
{
	vTLF35584_Panels.write_reg.TLF35584_OTFAIL_0x24.signal.COM = data;
	vTLF35584_Panels.write_reg.TLF35584_OTFAIL_0x24.signal.MON = data;
	vTLF35584_Panels.write_reg.TLF35584_OTFAIL_0x24.signal.PREG = data;
	vTLF35584_Panels.write_reg.TLF35584_OTFAIL_0x24.signal.UC	 = data;
	TLF35584_Communication(PMIC_WRITE,OTFAIL,vTLF35584_Panels.write_reg.TLF35584_OTFAIL_0x24.byte);
}

void TLF35584_Spi_Write_OTWRNSF_0x25(uint8 data)//Over temperature warning status flags
{
	vTLF35584_Panels.write_reg.TLF35584_OTWRNSF_0x25.signal.COM = data;
	vTLF35584_Panels.write_reg.TLF35584_OTWRNSF_0x25.signal.PREG = data;
	vTLF35584_Panels.write_reg.TLF35584_OTWRNSF_0x25.signal.STDBY = data;
	vTLF35584_Panels.write_reg.TLF35584_OTWRNSF_0x25.signal.UC = data;
	vTLF35584_Panels.write_reg.TLF35584_OTWRNSF_0x25.signal.VREF = data;
	TLF35584_Communication(PMIC_WRITE,OTWRNSF,vTLF35584_Panels.write_reg.TLF35584_OTWRNSF_0x25.byte);
}

void TLF35584_Spi_Write_ABIST_CTRL0_0x2C()
{
	TLF35584_Communication(PMIC_WRITE,ABIST_CTRL0,vTLF35584_Panels.write_reg.TLF35584_ABIST_CTRL0_0x2C.byte);
}

void TLF35584_Spi_Write_ABIST_CTRL1_0x2D()
{
	TLF35584_Communication(PMIC_WRITE,ABIST_CTRL1,vTLF35584_Panels.write_reg.TLF35584_ABIST_CTRL1_0x2D.byte);
}

void TLF35584_Spi_Write_ABIST_SELECT0_0x2E()
{
	TLF35584_Communication(PMIC_WRITE,ABIST_SELECT0,vTLF35584_Panels.write_reg.TLF35584_ABIST_SELECT0_0x2E.byte);
}

void TLF35584_Spi_Write_ABIST_SELECT1_0x2F()
{
	TLF35584_Communication(PMIC_WRITE,ABIST_SELECT1,vTLF35584_Panels.write_reg.TLF35584_ABIST_SELECT1_0x2F.byte);
}

void TLF35584_Spi_Write_ABIST_SELECT2_0x30()
{
	TLF35584_Communication(PMIC_WRITE,ABIST_SELECT2,vTLF35584_Panels.write_reg.TLF35584_ABIST_SELECT2_0x30.byte);
}

void TLF35584_Spi_Write_BCK_FREQ_CHANGE_0x31()
{
	TLF35584_Communication(PMIC_WRITE,BCK_FREQ_CHANGE,vTLF35584_Panels.write_reg.TLF35584_BCK_FREQ_CHANGE_0x31.byte);
}

void TLF35584_Spi_Write_BCK_FRE_SPREAD_0x32()
{
	TLF35584_Communication(PMIC_WRITE,BCK_FRE_SPREAD,vTLF35584_Panels.write_reg.TLF35584_BCK_FRE_SPREAD_0x32.byte);
}

void TLF35584_Spi_Write_BCK_MAIN_CTRL_0x33()
{
	TLF35584_Communication(PMIC_WRITE,BCK_MAIN_CTRL,vTLF35584_Panels.write_reg.TLF35584_BCK_MAIN_CTRL_0x33.byte);
}

/**
 * @brief Toggle the WDI output pin.
 *
 * This function toggles the state of the WDI output.
 * In a real implementation, this would control a GPIO pin.
 */
static void TLF35584_ToggleWDIOutput(void)
{
	static Dio_LevelType wdi_state = STD_LOW;

	wdi_state = (wdi_state == STD_LOW) ? STD_HIGH : STD_LOW;

	Dio_WriteChannel(EHAL_DIO_PMIC_WDI, wdi_state);
}

//******************************************************************************
// @Function	 	void TLF35584_ServiceWWD(void)
// @Description   	To Service WWD by SPI communication
// @Return Value	None
// @Parameters    	None
//******************************************************************************
void TLF35584_ServiceWWD(void)
{
#if (WWD_TRIG_SELECTION == WWD_TRIG_SPI)
	uint8 SpiTxData;

	/* read Window watchdog command */
	TLF35584_Spi_Read_WWDSCMD_0x17();

	/* invert Window watchdog trigger bit value */
	//	SpiTxData = ~((SpiRxMsg >> 1)) & 0x1;
	SpiTxData = ~(vTLF35584_Panels.read_reg.TLF35584_WWDSCMD_0x17.signal.TRIG);

	/* service Window watchdog */
	TLF35584_Spi_Write_WWDSCMD_0x17(SpiTxData);
	vTLF35584_Panels.watchdogs.WdTrigCnt.WwdTrig++;
#elif (WWD_TRIG_SELECTION == WWD_TRIG_WDI)
	//    if(vTLF35584_Panels.read_pins.WDI == FALSE) {
	TLF35584_ToggleWDIOutput();
	vTLF35584_Panels.watchdogs.WdTrigCnt.WwdTrig++;
	//    }
#endif
} /*End of TLF35584Demo_TriggerWWD()*/

//------------------------------------------------------------------------------
// Function: TLF35584_ManageWWD
// Description: Unified function to handle both WWD trigger via WDI pin or SPI register.
//
// If WWD_TRIG_SELECTION == WWD_TRIG_SPI:
//   - Use SPI to service the Window Watchdog (just do a periodic SPI trigger).
//
// If WWD_TRIG_SELECTION == WWD_TRIG_WDI:
//   - Use a state machine controlling the WDI pin:
//       * LONGOPEN -> CLOSED -> OPEN states
//       * CLOSED window keeps WDI HIGH
//       * OPEN window drives WDI LOW, then returns HIGH at the end
//------------------------------------------------------------------------------

//void TLF35584_ManageWWD()
//{
//	uint32 LowTrigTime = LONG_OPEN_WINDOW_TIME/2;
////	uint32 LowTrigTime = 3;
////	uint32 LowTrigTime = OPEN_WINDOW_TIME/2;
//	uint32 OwTrigTime = CLOSE_WINDOW_TIME + (OPEN_WINDOW_TIME/2);
//
//	vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime++;
//	/* Long Open Window Trigger, Windows Watch dog First Trigger */
//	//	if(vTLF35584_Panels.watchdogs.WdTrigCnt.WwdLow == 0)
//	if(vTLF35584_Panels.watchdogs.WdTrigCnt.WwdLow == 0)
//	{
//		if(vTLF35584_Panels.state_machine.CurrState == TLF35584_STATE_INIT){
//			if(vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime >= LowTrigTime)
//			{
//				vTLF35584_Panels.watchdogs.WwdTrigTime.LowTrigTime = vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime;
//				TLF35584_ServiceWWD();
//				vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime = 0;
////				vTLF35584_Panels.watchdogs.WdTrigCnt.WwdLow++;
//			}
//			else{
//				//no action
//			}
//		}
//		else if(vTLF35584_Panels.state_machine.CurrState == TLF35584_STATE_NORMAL){
//			if(vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime >= LowTrigTime)
//			{
//				vTLF35584_Panels.watchdogs.WwdTrigTime.LowTrigTime = vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime;
//				TLF35584_ServiceWWD();
//				vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime = 0;
//				vTLF35584_Panels.watchdogs.WdTrigCnt.WwdLow++;
//			}
//			else{
//				//no action
//			}
//		}
//		else{
//			//no action
//		}
//
//	}
//	/* Open Window Trigger */
//	else{
//#if (WWD_TRIG_SELECTION == WWD_TRIG_SPI) //SPI Open Window Trigger
//		if(vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime >= OwTrigTime){
//			vTLF35584_Panels.watchdogs.WwdTrigTime.TrigLastTime = vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime;
//			TLF35584_ServiceWWD();
//			vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime=0;
//		}
//		else{
//			//do nothing
//		}
//#elif (WWD_TRIG_SELECTION == WWD_TRIG_WDI) //WDI Open Window Trigger
//		//Preparing for Trigger
//		if((vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime >= WDI_HIGH_TIME)
//				&&(vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime < OwTrigTime)){
//			if(vTLF35584_Panels.read_pins.WDI == STD_LOW)
//			{
//				TLF35584_ToggleWDIOutput();  // LOW → HIGH
//				vTLF35584_Panels.watchdogs.WdTrigCnt.WwdTrig++;
//			}
//			else{
//				//no action
//			}
//		}
//		else if(vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime >= OwTrigTime){
//			if(vTLF35584_Panels.read_pins.WDI == STD_HIGH)
//			{
//				TLF35584_ToggleWDIOutput();  // HIGH → LOW (falling edge)
//				vTLF35584_Panels.watchdogs.WdTrigCnt.WwdTrig++;
//				vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime = 0;
//			}
//			else{
//				//no action
//			}
//		}
//		else{
//			//no action
//		}
//#endif
//	}
//}

void TLF35584_ManageWWD(void)
{
    uint32 LowTrigTime = LONG_OPEN_WINDOW_TIME / 2;
    uint32 OwTrigTime  = CLOSE_WINDOW_TIME + (OPEN_WINDOW_TIME / 2);

    vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime++;

    if(vTLF35584_Panels.watchdogs.WdTrigCnt.WwdLow == 0) {
        if( (vTLF35584_Panels.state_machine.CurrState == TLF35584_STATE_INIT) ||
            (vTLF35584_Panels.state_machine.CurrState == TLF35584_STATE_NORMAL) )
        {
            if(vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime >= LowTrigTime) {
                if(vTLF35584_Panels.read_pins.WDI == STD_LOW) {
                    TLF35584_ToggleWDIOutput();
                    vTLF35584_Panels.watchdogs.WdTrigCnt.WwdLow = 1;
                    vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime = 0;
                }
            }
        }
    }
    else {
        if((vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime >= WDI_HIGH_TIME) &&
           (vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime < OwTrigTime))
        {
            if(vTLF35584_Panels.read_pins.WDI == STD_LOW) {
                TLF35584_ToggleWDIOutput(); // LOW -> HIGH
                vTLF35584_Panels.watchdogs.WdTrigCnt.WwdTrig++;
            }
        }
        else if(vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime >= OwTrigTime) {
            if(vTLF35584_Panels.read_pins.WDI == STD_HIGH) {
                TLF35584_ToggleWDIOutput(); // HIGH -> LOW
                vTLF35584_Panels.watchdogs.WdTrigCnt.WwdTrig++;
                vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime = 0;
            }
        }
    }
}


//******************************************************************************
// @Function	 	TLF35584_ManageFWD(void)
// @Description   	Functional Watchdog Process
// @Return Value	None
// @Parameters    	None
//******************************************************************************
void TLF35584_ManageFWD(void)
{
	uint8 FwdQuestNum, UpperBit, LowerBit,
	InvertUpperBit, InvertLowerBit,
	Rasp0Data, Rasp3Data, Rasp2Data, Rasp1Data;

	uint32 Timeout = TLF35584_SPI_TIMEOUT_CNT;

	/* read Functional watchdog question */
	TLF35584_Communication(PMIC_READ,FWDSTAT0,0);
	vTLF35584_Panels.read_reg.TLF35584_FWDSTAT0_0x2A.byte = vTLF35584_SpiRxData;
	FwdQuestNum = vTLF35584_Panels.read_reg.TLF35584_FWDSTAT0_0x2A.signal.FWDQUEST;

	/* calculate Functional watchdog response: RESP 3, 2, 1 and 1 */
	Rasp0Data = vTLF35584_FwdResp0Table[FwdQuestNum];
	UpperBit = Rasp0Data&0xF0;
	LowerBit = Rasp0Data&0x0F;
	InvertUpperBit = (~UpperBit)&0xF0;
	InvertLowerBit = (~LowerBit)&0x0F;

	Rasp3Data = ~Rasp0Data;
	Rasp2Data = UpperBit + InvertLowerBit;
	Rasp1Data = InvertUpperBit + LowerBit;

	/* send Functional watchdog response: RESP 3, 2, 1 and 1 */
	vTLF35584_Panels.write_reg.TLF35584_FWDRSP_0x18.byte = Rasp3Data;
	TLF35584_Communication(PMIC_WRITE,FWDRSP, vTLF35584_Panels.write_reg.TLF35584_FWDRSP_0x18.byte);
	vTLF35584_Panels.write_reg.TLF35584_FWDRSP_0x18.byte = Rasp2Data;
	TLF35584_Communication(PMIC_WRITE,FWDRSP, vTLF35584_Panels.write_reg.TLF35584_FWDRSP_0x18.byte);
	vTLF35584_Panels.write_reg.TLF35584_FWDRSP_0x18.byte = Rasp1Data;
	TLF35584_Communication(PMIC_WRITE,FWDRSP, vTLF35584_Panels.write_reg.TLF35584_FWDRSP_0x18.byte);
	vTLF35584_Panels.write_reg.TLF35584_FWDRSPSYNC_0x19.byte = Rasp0Data;
	TLF35584_Communication(PMIC_WRITE,FWDRSPSYNC, vTLF35584_Panels.write_reg.TLF35584_FWDRSPSYNC_0x19.byte);

	/* read and check Functional watchdog response check status */
	//	TLF35584_Communication(PMIC_READ,FWDSTAT0,0);
	//	vTLF35584_Panels.read_reg.TLF35584_FWDSTAT0_0x2A.byte = vTLF35584_SpiRxData;

	while ( Timeout > 0 ) {
		TLF35584_Communication(PMIC_READ, FWDSTAT0, 0);
		vTLF35584_Panels.read_reg.TLF35584_FWDSTAT0_0x2A.byte = vTLF35584_SpiRxData;

		if ( vTLF35584_Panels.read_reg.TLF35584_FWDSTAT0_0x2A.signal.FWDRSPOK ) {
			break;
		}
		Timeout--;
	}

	if(Timeout == 0){
		//vTLF35584_Panels.error_control.error_flag = TRUE;
	}
	else{
		vTLF35584_Panels.watchdogs.WdTrigCnt.FwdTrig++;
	}
}

/**
 * @brief Check for debug error reset condition without clearing the global init counter.
 *
 * This function checks, at every 1ms tick (called from the 1ms task), whether
 * the elapsed time since the last error reset (based on the global init counter)
 * exceeds DEBUG_INIT_TIMEOUT. If so, and if either the WWDF or FWDF flag is set in
 * the INITERR register, then, if the GTM_OCDS_OCS.B.SUS field indicates debug soft suspend mode,
 * an error reset is triggered. The last reset timestamp is then updated so that the condition
 * will wait for the specified timeout period before being checked again.
 */
static void TLF35584_DebugErrorResetCheck(void)
{
	// Static variable to hold the last time an error reset was performed.
	static uint32 lastInitResetTime = 0;

	// Update the GTM_OCDS_OCS register value from hardware
	vGTM_OCDS_OCS.U = GTM_OCDS_OCS.U;

	// Use the continuously increasing init counter (in ms, for example)
	uint32 currentTime = vTLF35584_Panels.state_machine.Cnt.init;

	// Check if the elapsed time since last reset exceeds DEBUG_INIT_TIMEOUT
	if ((currentTime - lastInitResetTime) > DEBUG_INIT_TIMEOUT) {
		// Check if either the WWDF or the FWDF flag is set in the INITERR register
		if ((vTLF35584_Panels.read_reg.TLF35584_INITERR_0x1B.signal.WWDF == 1) ||
				(vTLF35584_Panels.read_reg.TLF35584_INITERR_0x1B.signal.FWDF == 1)) {
			// If the GTM_OCDS_OCS.B.SUS field indicates soft suspend mode (debug mode)
			if (vGTM_OCDS_OCS.B.SUS == OCDS_SOFT_SUSPEND_CH0) {
				//                TLF35584_ResetErrors();	// Perform error reset
				TLF35584_Spi_Write_INITERR_0x1B(1);	//Init error status flags, WWD & FWD & ERR Flag Clear
				// Update the last reset time to the current time for future checks
				lastInitResetTime = currentTime;
			}
			else {
				TLF35584_ResetErrors();
				// Optionally handle other SUS values if needed
			}
		}
		else {
			// Optionally handle the case when neither WWDF nor FWDF is set
		}
	}
}

//******************************************************************************
// @Function	 	void TLF35584_DetectErrors()
// @Description   	Read diagnosis registers and check for errors.
//******************************************************************************
void TLF35584_DetectErrors(void)
{
	uint8 iflags, initerr, sysfail;

	TLF35584_Spi_Read_SYSFAIL_0x1A();		// Failure status flags
	TLF35584_Spi_Read_INITERR_0x1B(); 		// Init error status flags
	TLF35584_Spi_Read_IF_0x1C();			// Interrupt flags

	vTLF35584_Panels.read_reg.TLF35584_IF_0x1C.byte = (vTLF35584_Panels.read_reg.TLF35584_IF_0x1C.byte & 0x7C);

	sysfail = vTLF35584_Panels.read_reg.TLF35584_SYSFAIL_0x1A.byte;  /* OTF, VMONF */
	initerr = vTLF35584_Panels.read_reg.TLF35584_INITERR_0x1B.byte;  /* WWDF, FWDF */
	iflags  = vTLF35584_Panels.read_reg.TLF35584_IF_0x1C.byte;       /* OTW, MON */

	vTLF35584_Panels.error_control.error_flag = (vTLF35584_Panels.read_reg.TLF35584_SYSFAIL_0x1A.byte || \
			vTLF35584_Panels.read_reg.TLF35584_INITERR_0x1B.byte || \
			vTLF35584_Panels.read_reg.TLF35584_IF_0x1C.byte);

	/* Additionally, set a specific error_type */
	/* Since multiple bits might be set at the same time, you can decide the priority as needed */
	if ( (sysfail & (1<<1)) != 0 ) {
		/* SYSFAIL_0x1A.bit1 = OTF (Over Temperature Failure) */
		vTLF35584_Panels.error_control.error_type = TLF35584_TEMPERATURE_ERROR;
	}
	else if ( (sysfail & (1<<2)) != 0 ) {
		/* SYSFAIL_0x1A.bit2 = VMONF (Voltage Monitor Failure) */
		vTLF35584_Panels.error_control.error_type = TLF35584_VOLTAGE_ERROR;
	}
	else if ( (initerr & (1<<3)) != 0 ) {
		/* INITERR_0x1B.bit3 = WWDF (Window Watchdog Overflow) */
		vTLF35584_Panels.error_control.error_type = TLF35584_WWD_TRIGGER_ERROR;
		vTLF35584_WdErrCnt++;
		if(vTLF35584_WdErrCnt < 10){
			vTLF35584_Panels.error_control.error_clear = 1;
		}
		else{

		}
	}
	else if ( (initerr & (1<<4)) != 0 ) {
		/* INITERR_0x1B.bit4 = FWDF (Functional Watchdog Overflow) */
		vTLF35584_Panels.error_control.error_type = TLF35584_FWD_TRIGGER_ERROR;
	}
	else if (iflags != 0) {
		/* Handles other Interrupt Flags or unknown errors */
		vTLF35584_Panels.error_control.error_type = TLF35584_UNKNOWN_ERROR;
	}
	else {
		/* No errors detected, set to NO_ERROR */
		vTLF35584_Panels.error_control.error_type = TLF35584_NO_ERROR;
	}
} /*End of TLF35584_DetectErrors()*/

//******************************************************************************
// @Function	 	void TLF35584_ResetErrors()
// @Description   	Read diagnosis registers and clear the error.
//******************************************************************************
void TLF35584_ResetErrors(void)
{
	TLF35584_Spi_Write_SYSFAIL_0x1A(1);	//Failure status flags Clear
	TLF35584_Spi_Write_INITERR_0x1B(1);	//Init error status flags, WWD & FWD & ERR Flag Clear
	TLF35584_Spi_Write_IF_0x1C(1);	//Interrupt flags, Flag All Clear
	TLF35584_Spi_Write_SYSSF_0x1D(1);//System status flags
	TLF35584_Spi_Write_WKSF_0x1E(1);//Wake up status flags
	TLF35584_Spi_Write_SPISF_0x1F(1);//SPI status flags
	TLF35584_Spi_Write_MONSF0_0x20(1);//Monitor status flags 0(short to ground status)
	TLF35584_Spi_Write_MONSF1_0x21(1);//Monitor status flags 1(over voltage status)
	TLF35584_Spi_Write_MONSF2_0x22(1);//Monitor status flags 2(under voltage status)
	TLF35584_Spi_Write_MONSF3_0x23(1);//Monitor status flags 3
	TLF35584_Spi_Write_OTFAIL_0x24(1);//Over temperature failure status flags
	TLF35584_Spi_Write_OTWRNSF_0x25(1);//Over temperature warning status flags
} /*End of TLF35584_ResetErrors()*/

void TLF35584_SetOutputState(uint8 data)
{
	switch(data)
	{
	case TLF35584_STATE_INIT :
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.COMEN	= TRUE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.VREFEN	= TRUE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.TRK1EN	= TRUE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.TRK2EN	= TRUE;
		break;
	case TLF35584_STATE_NORMAL :
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.COMEN	= TRUE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.VREFEN	= TRUE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.TRK1EN	= TRUE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.TRK2EN	= TRUE;
		break;
	case TLF35584_STATE_SLEEP :
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.COMEN	= FALSE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.VREFEN	= FALSE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.TRK1EN	= FALSE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.TRK2EN	= FALSE;
		break;
	case TLF35584_STATE_STANDBY :
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.COMEN	= FALSE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.VREFEN	= FALSE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.TRK1EN	= FALSE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.TRK2EN	= FALSE;
		break;
	case TLF35584_STATE_WAKE :
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.COMEN	= TRUE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.VREFEN	= TRUE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.TRK1EN	= TRUE;
		vTLF35584_Panels.write_reg.TLF35584_DEVCTRL_0x15.signal.TRK2EN	= TRUE;
		break;
	default:
		break;
	}
}

void TLF35584_UpdatePins(void)
{
	vTLF35584_Panels.read_pins.ENA = (meas.measured.tFIGdcb.filt >= IGNITION_DETECT_12V_THRESHOLD) ? TRUE : FALSE;
	//	vTLF35584_Panels.ReadPins.WAK = (drvBLDC.meas_IG3.tFfilt >= INPUT_12V_HIGH_THRES_LEVEL) ? TRUE : FALSE;
	vTLF35584_Panels.read_pins.SS1 = Dio_ReadChannel(EHAL_DIO_PMIC_SS1); // Safe state signal
	vTLF35584_Panels.read_pins.SS2 = Dio_ReadChannel(EHAL_DIO_PMIC_SS2); // Safe state signal2
	vTLF35584_Panels.read_pins.INT = Dio_ReadChannel(EHAL_DIO_PMIC_INT); // Fault interrupt signal
	vTLF35584_Panels.read_pins.WDI = Dio_ReadChannel(EHAL_DIO_PMIC_WDI); //NOT_USED : Watchdog input, trigger signal
	if(vTLF35584_Panels.read_pins.SS1 == TRUE){
		vTLF35584_Panels.state_machine.CurrState = TLF35584_STATE_NORMAL;
	}
	else{
		vTLF35584_Panels.state_machine.CurrState = TLF35584_STATE_INIT;
	}
}


//******************************************************************************
// @Function	 	void TLF35584_HandleState()
// @Description   	Manage the state machine and state transition of TLF35584
// @Return Value	None
// @Parameters    	None
//******************************************************************************
void TLF35584_HandleState()
{

	switch(vTLF35584_Panels.state_machine.CurrState)
	{
	case TLF35584_STATE_NONE :
		break;

	case TLF35584_STATE_INIT:
		vTLF35584_Panels.state_machine.Cnt.init++;
		TLF35584_DetectErrors();

		if(vTLF35584_Panels.state_machine.PrevState != vTLF35584_Panels.state_machine.CurrState){
			TLF35584_SetOutputState(TLF35584_STATE_INIT);
			TLF35584_Spi_Write_DEVCTRL_0x15(TLF35584_STATE_INIT);
		}
		else{
		}

		if(!vTLF35584_Panels.error_control.error_flag &&
				vTLF35584_Panels.state_machine.Cnt.init > INIT_TO_NORMAL_DELAY){
			TLF35584_SetOutputState(TLF35584_STATE_NORMAL);
			TLF35584_Spi_Write_DEVCTRL_0x15(TLF35584_STATE_NORMAL);
			vTLF35584_Panels.next_state_request = STATE_REQ_NONE;
		}
		else{
		}

		break;

	case TLF35584_STATE_NORMAL:
		vTLF35584_Panels.state_machine.Cnt.normal++;

		/* ERROR_DETECTION */
		if(!vTLF35584_Panels.read_pins.SS1 || !vTLF35584_Panels.read_pins.SS2){
			vTLF35584_Panels.error_control.error_flag = TRUE;
		}
		else{
			vTLF35584_Panels.error_control.error_flag = FALSE;
		}

		if(!vTLF35584_Panels.error_control.error_flag) {
			if(!vTLF35584_Panels.read_pins.ENA && !vTLF35584_Panels.read_pins.WAK)
			{
				if(vTLF35584_Panels.sleep_count > IG_OFF_SLEEP_DELAY)
				{
					vTLF35584_Panels.sleep_count = 0;

					if (LOW_POWER_MODE_SELECTION == LOW_POWER_STANDBY_MODE){
						TLF35584_SetOutputState(TLF35584_STATE_STANDBY);
						TLF35584_Spi_Write_DEVCTRL_0x15(TLF35584_STATE_STANDBY);
					}
					else{ //LOW_POWER_MODE_SELECTION == LOW_POWER_SLEEP_MODE
						TLF35584_SetOutputState(TLF35584_STATE_SLEEP);
						TLF35584_Spi_Write_DEVCTRL_0x15(TLF35584_STATE_SLEEP);
					}
				}
				else
				{
					vTLF35584_Panels.sleep_count++;
				}
			}
			else
			{
				vTLF35584_Panels.sleep_count = 0;
			}
		}
		else{
			//no action
		}
		break;

	case TLF35584_STATE_SLEEP:
		vTLF35584_Panels.state_machine.Cnt.sleep++;
		TLF35584_DetectErrors();

		if(vTLF35584_Panels.next_state_request == STATE_REQ_WAKE) {
			vTLF35584_Panels.next_state_request = STATE_REQ_NONE;
			TLF35584_SetOutputState(TLF35584_STATE_WAKE);
			TLF35584_Spi_Write_DEVCTRL_0x15(TLF35584_STATE_WAKE);
		}
		else{
			//no action
		}
		break;

	case TLF35584_STATE_STANDBY:

		break;

	case TLF35584_STATE_WAKE:
		vTLF35584_Panels.state_machine.Cnt.wake++;
		TLF35584_DetectErrors();

		if(!vTLF35584_Panels.error_control.error_flag)
		{
			if(vTLF35584_Panels.next_state_request == STATE_REQ_NORMAL)
			{
				vTLF35584_Panels.next_state_request = STATE_REQ_NONE;
				TLF35584_SetOutputState(TLF35584_STATE_NORMAL);
				TLF35584_Spi_Write_DEVCTRL_0x15(TLF35584_STATE_NORMAL);
			}
			else if(!vTLF35584_Panels.read_pins.ENA && !vTLF35584_Panels.read_pins.WAK)
			{
				if(vTLF35584_Panels.next_state_request == STATE_REQ_SLEEP)
				{
					vTLF35584_Panels.next_state_request = STATE_REQ_NONE;
					TLF35584_SetOutputState(TLF35584_STATE_SLEEP);
					TLF35584_Spi_Write_DEVCTRL_0x15(TLF35584_STATE_SLEEP);
				}
				else{
					//no action
				}
			}
			else{
				//no action
			}
		}
		else{
			//no action
		}
		break;
	case TLF35584_STATE_RESERVED1:
		break;

	case TLF35584_STATE_RESERVED2:
		break;

	default:
		break;
	}
	vTLF35584_Panels.state_machine.PrevState = vTLF35584_Panels.state_machine.CurrState;
}

void TLF35584_GetWatchdogStatus()
{
	TLF35584_Spi_Read_WWDSTAT_0x29();		//READ WWD CNT
#if FUNCTION_WATCHDOG_ENABLE == 1
	TLF35584_Spi_Read_FWDSTAT0_0x2A();		//READ FWD Status
	TLF35584_Spi_Read_FWDSTAT1_0x2B();		//READ FWD CNT
#endif
}

void TLF35584_GetABISTStatus() //Read ABIST status
{
	TLF35584_Spi_Read_ABIST_CTRL0_0x2C();
	TLF35584_Spi_Read_ABIST_CTRL1_0x2D();
	TLF35584_Spi_Read_ABIST_SELECT0_0x2E();
	TLF35584_Spi_Read_ABIST_SELECT1_0x2F();
	TLF35584_Spi_Read_ABIST_SELECT2_0x30();
}

void TLF35584_GetProtectionRegisters() //Read Protection
{
	TLF35584_Spi_Read_RSYSPCFG0_0x0B();
	TLF35584_Spi_Read_RSYSPCFG1_0x0C();
	TLF35584_Spi_Read_RWDCFG0_0x0D();
	TLF35584_Spi_Read_RWDCFG1_0x0E();
	TLF35584_Spi_Read_RFWDCFG_0x0F();
	TLF35584_Spi_Read_RWWDCFG0_0x10();
	TLF35584_Spi_Read_RWWDCFG1_0x11();
}

void TLF35584_WriteRegisters(void)
{
	switch(vTLF35584_Panels.ctrl_reg.write_num)
	{
	case 0 :
		//no action
		vTLF35584_Panels.ctrl_reg.write_num = 0;
		break;
	case 1 :
		TLF35584_Spi_Write_SYSFAIL_0x1A(1);
		TLF35584_Spi_Write_INITERR_0x1B(1);
		TLF35584_Spi_Write_IF_0x1C(1);
		vTLF35584_Panels.ctrl_reg.write_num = 2;
		break;
	case 2:
		TLF35584_Spi_Write_SYSSF_0x1D(1);
		TLF35584_Spi_Write_WKSF_0x1E(1);
		TLF35584_Spi_Write_SPISF_0x1F(1);
		vTLF35584_Panels.ctrl_reg.write_num = 3;
		break;
	case 3:
		TLF35584_Spi_Write_MONSF0_0x20(1);
		TLF35584_Spi_Write_MONSF1_0x21(1);
		TLF35584_Spi_Write_MONSF2_0x22(1);
		vTLF35584_Panels.ctrl_reg.write_num = 4;
		break;
	case 4:
		TLF35584_Spi_Write_MONSF3_0x23(1);
		TLF35584_Spi_Write_OTFAIL_0x24(1);
		TLF35584_Spi_Write_OTWRNSF_0x25(1);
		vTLF35584_Panels.ctrl_reg.write_num = 0;
		break;
	default:
		break;
	}
}

void TLF35584_ReadRegisters(void)
{
	switch(vTLF35584_Panels.ctrl_reg.read_num)
	{
	case 0 :
		//		TLF35584_Spi_Read_DEVCFG0_0x00();				// 0x00 to 0x02 Read Device configuration
		//		TLF35584_Spi_Read_DEVCFG1_0x01();
		//		TLF35584_Spi_Read_DEVCFG2_0x02();
		vTLF35584_Panels.ctrl_reg.read_num = 0;
		break;
	case 1 :
		TLF35584_Spi_Read_DEVCFG0_0x00();				// 0x00 to 0x02 Read Device configuration
		TLF35584_Spi_Read_DEVCFG1_0x01();
		TLF35584_Spi_Read_DEVCFG2_0x02();
		vTLF35584_Panels.ctrl_reg.read_num = 2;
		break;
	case 2 :
		TLF35584_Spi_Read_RSYSPCFG0_0x0B();				//0x0B to 0x11 Read Protection Register(System configuration, Watchdog configuration)
		TLF35584_Spi_Read_RSYSPCFG1_0x0C();
		TLF35584_Spi_Read_RWDCFG0_0x0D();
		vTLF35584_Panels.ctrl_reg.read_num = 3;
		break;
	case 3 :
		TLF35584_Spi_Read_RWDCFG1_0x0E();
		TLF35584_Spi_Read_RFWDCFG_0x0F();
		TLF35584_Spi_Read_RWWDCFG0_0x10();
		vTLF35584_Panels.ctrl_reg.read_num = 4;
		break;
	case 4 :
		TLF35584_Spi_Read_RWWDCFG1_0x11();
		TLF35584_Spi_Read_WKTIMCFG0_0x12();				//0x12 to 0x14 Read Wake timer configuration
		TLF35584_Spi_Read_WKTIMCFG1_0x13();
		vTLF35584_Panels.ctrl_reg.read_num = 5;
		break;
	case 5 :
		TLF35584_Spi_Read_WKTIMCFG2_0x14();
		TLF35584_Spi_Read_SYSSF_0x1D();					//0x1D to 0x25 Read_Diag_Register
		TLF35584_Spi_Read_WKSF_0x1E();
		vTLF35584_Panels.ctrl_reg.read_num = 6;
		break;
	case 6 :
		TLF35584_Spi_Read_SPISF_0x1F();
		TLF35584_Spi_Read_MONSF0_0x20();
		TLF35584_Spi_Read_MONSF1_0x21();
		vTLF35584_Panels.ctrl_reg.read_num = 7;
		break;
	case 7 :
		TLF35584_Spi_Read_MONSF2_0x22();
		TLF35584_Spi_Read_MONSF3_0x23();
		TLF35584_Spi_Read_OTFAIL_0x24();
		TLF35584_Spi_Read_OTWRNSF_0x25();
		vTLF35584_Panels.ctrl_reg.read_num = 8;
		break;
	case 8 :
		TLF35584_Spi_Read_VMONSTAT_0x26();				//0x26 Voltage monitor status
		TLF35584_Spi_Read_PROTSTAT_0x28();				//0x28 Protection status
		TLF35584_Spi_Read_ABIST_CTRL0_0x2C();			//0x2C to 0x30 Read_ABIST_Status
		vTLF35584_Panels.ctrl_reg.read_num = 9;
		break;
	case 9 :
		TLF35584_Spi_Read_ABIST_CTRL1_0x2D();
		TLF35584_Spi_Read_ABIST_SELECT0_0x2E();
		TLF35584_Spi_Read_ABIST_SELECT1_0x2F();
		TLF35584_Spi_Read_ABIST_SELECT2_0x30();
		vTLF35584_Panels.ctrl_reg.read_num = 10;
		break;
	case 10 :
		TLF35584_Spi_Read_BCK_FREQ_CHANGE_0x31();		//0x31 to 0x33 Read Buck Register
		TLF35584_Spi_Read_BCK_FRE_SPREAD_0x32();
		TLF35584_Spi_Read_BCK_MAIN_CTRL_0x33();
		vTLF35584_Panels.ctrl_reg.read_num = 0;
		break;
	default:
		break;
	}
}

//******************************************************************************
// @Function	 	void TLF35584_ClearInitErrors(void)
// @Description   	Read diagnosis registers and clear the error.
//******************************************************************************
void TLF35584_ClearInitErrors(void)
{
	//	/*Clear WWD Err Register Variables*/
	//	vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.signal.WWDF			= 1;			//Clear = 1
	//	vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.signal.WWDE			= 1;			//Clear = 1
	//
	//	/*Clear FWD Err Register Variables*/
	//	vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.signal.FWDF			= 1;			//Clear = 1
	//	vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.signal.FWDE			= 1;			//Clear = 1
	//
	//	/* Clear SPI Communication Error Flag */
	//	vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.signal.SPI				= 1;			//Clear = 1
	//
	//	/*Clear Pre-regulator Err Register Variables*/
	////	vTLF35584_Panels.WriteReg.TLF35584_IF_0x1C.signal.MON				= 1;			//Clear = 1
	////	vTLF35584_Panels.WriteReg.TLF35584_MONSF2_0x22.signal.PREGUV		= 1;			//Clear = 1
	//
	//	/*SET Clear WWD(Window WatchDogs) Error Counter & PREGUV(Pre-regulator Under voltage) Error Register*/
	//	TLF35584_Communication(PMIC_WRITE,INITERR,vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.byte);
	//	TLF35584_Communication(PMIC_WRITE,IF,vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.byte);
	//	TLF35584_Communication(PMIC_WRITE,SYSSF,vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.byte);
	//	TLF35584_Communication(PMIC_WRITE,MONSF2,vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.byte);
	TLF35584_ResetErrors();
}

//************************************************************************************************************
// @Function	 	void TLF35584_InitializeData(void)
//************************************************************************************************************
void TLF35584_InitializeData(void)
{	//Init Variables
	vTLF35584_Panels.state_machine.CurrState				= TLF35584_STATE_NONE;
	vTLF35584_Panels.next_state_request 					= STATE_REQ_NONE;

	vTLF35584_Panels.watchdogs.Wwd.ErrCnt					= 0;
	vTLF35584_Panels.watchdogs.Fwd.ErrCnt					= 0;
	vTLF35584_Panels.watchdogs.WdTrigCnt.WwdLow				= 0;
	vTLF35584_Panels.watchdogs.WwdTrigTime.TrigTime			= 0;

	vTLF35584_Panels.error_control.error_flag				= 0;
	vTLF35584_Panels.error_control.error_clear				= 0;

	vTLF35584_Panels.ctrl_reg.write_num						= 0;
	vTLF35584_Panels.ctrl_reg.read_num						= 0;

	vTLF35584_Panels.sleep_count							= 0;

	//Init Register Variables
	vTLF35584_Panels.write_reg.TLF35584_SYSPCFG0_0x04.byte	= 0;
	vTLF35584_Panels.write_reg.TLF35584_SYSPCFG1_0x05.byte	= 0;
	vTLF35584_Panels.write_reg.TLF35584_WDCFG0_0x06.byte	= 0;
	vTLF35584_Panels.write_reg.TLF35584_WDCFG1_0x07.byte	= 0;
	vTLF35584_Panels.write_reg.TLF35584_FWDCFG_0x08.byte	= 0;
	vTLF35584_Panels.write_reg.TLF35584_WWDCFG0_0x09.byte	= 0;
	vTLF35584_Panels.write_reg.TLF35584_WWDCFG1_0x0A.byte	= 0;

	/*INIT WWD Err Register Variables*/
	vTLF35584_Panels.write_reg.TLF35584_INITERR_0x1B.byte	= 0;
	vTLF35584_Panels.write_reg.TLF35584_IF_0x1C.byte		= 0;
	vTLF35584_Panels.write_reg.TLF35584_SYSSF_0x1D.byte		= 0;
	vTLF35584_Panels.write_reg.TLF35584_MONSF2_0x22.byte	= 0;

	vTLF35584_Panels.write_reg.TLF35584_DEVCFG0_0x00.byte	= 0;
	vTLF35584_Panels.write_reg.TLF35584_DEVCFG1_0x01.byte	= 0;
	vTLF35584_Panels.write_reg.TLF35584_DEVCFG2_0x02.byte	= 0;
} /*End of TLF35584_InitializeData()*/

//************************************************************************************************************
// @Function	 	void TLF35584_ConfigureRegisters(void)
//************************************************************************************************************
void TLF35584_ConfigureRegisters(void)
{
	//Set Register Variables
	vTLF35584_Panels.write_reg.TLF35584_SYSPCFG0_0x04.signal.STBYEN		= PMIC_DISABLE;	//0:Disable 1:Enable, (Stand-By LDO Not USED)Request standby regulator QST enable. Valid for all device states except FAILSAFE.

	vTLF35584_Panels.write_reg.TLF35584_SYSPCFG1_0x05.signal.ERRREC		= 0;			//(MCU_TO_PMIC_Generate_PWM_NOT_USED) Request ERR pin monitor recovery time, 0:1ms 1:2.5ms 2:5ms 3:10ms
	vTLF35584_Panels.write_reg.TLF35584_SYSPCFG1_0x05.signal.ERRRECEN	= PMIC_DISABLE;	//(MCU_TO_PMIC_Generate_PWM_NOT_USED) Request ERR pin monitor recovery enable, 0:Disable 1:Enable
	vTLF35584_Panels.write_reg.TLF35584_SYSPCFG1_0x05.signal.ERREN		= PMIC_DISABLE; 	//(MCU_TO_PMIC_Generate_PWM_NOT_USED) Request ERR pin monitor enable, 0:Disable 1:Enable
	vTLF35584_Panels.write_reg.TLF35584_SYSPCFG1_0x05.signal.ERRSLPEN	= PMIC_DISABLE;	//(MCU_TO_PMIC_Generate_PWM_NOT_USED) Request ERR pin monitor functionality enable while the system is in SLEEP, 0:Disable 1:Active
	vTLF35584_Panels.write_reg.TLF35584_SYSPCFG1_0x05.signal.SS2DEL		= 3;			//(Between delay Time SS1 & SS2) Request safe state 2 delay, 0:no delay 1:10ms 2:50ms 3:100ms 4:250ms

	vTLF35584_Panels.write_reg.TLF35584_WDCFG0_0x06.signal.FWDEN		= FUNCTION_WATCHDOG_ENABLE;	//0:Disable, 1:Enabled (FWD)
	vTLF35584_Panels.write_reg.TLF35584_WDCFG0_0x06.signal.WDCYC		= WATCHDOG_CYCLE_TIME;		//0:0.1 ms per 1 tick (LONG OPEN LOW=60ms), 1: 1 ms per 1 tick (LONG OPEN LOW=600ms)
	vTLF35584_Panels.write_reg.TLF35584_WDCFG0_0x06.signal.WWDEN		= WINDOW_WATCHDOG_ENABLE;	//0:Disable, 1:Enabled (WWD)
	vTLF35584_Panels.write_reg.TLF35584_WDCFG0_0x06.signal.WWDETHR		= WWD_ERROR_THRESHOLD;		//(5 : 5cnt) WWD error threshold to generate reset and enter into INIT state. Reset: 0x9
	vTLF35584_Panels.write_reg.TLF35584_WDCFG0_0x06.signal.WWDTSEL		= WWD_TRIG_SELECTION;	//0:WDI Pin MODE, 1:SPI MODE

	vTLF35584_Panels.write_reg.TLF35584_WDCFG1_0x07.signal.FWDETHR		= FWD_ERROR_THRESHOLD;		//(5 : 5cnt) FWD error threshold to generate reset and enter into INIT state. Reset: 0x9
	vTLF35584_Panels.write_reg.TLF35584_WDCFG1_0x07.signal.WDSLPEN		= PMIC_DISABLE;	//Watchdog function in sleep mode: 0=Disabled, 1=Enabled

	vTLF35584_Panels.write_reg.TLF35584_FWDCFG_0x08.signal.WDHBTP		= FWD_HEARTBEAT_TIME;		//FWD heart beat time set: WDCYC(0.1ms or 1ms)* wd cycles, Factor: 50, Offset: 50, 0wd cycles = 50, 1wd cycles = 100

	vTLF35584_Panels.write_reg.TLF35584_WWDCFG0_0x09.signal.CW			= WWD_CLOSE_WINDOW_TIME;		//WWD Close Window Time: WDCYC(0.1ms or 1ms)* wd cycles, Factor: 50, Offset: 50, 0wd cycles = 50, 1wd cycles = 100
	vTLF35584_Panels.write_reg.TLF35584_WWDCFG1_0x0A.signal.OW			= WWD_OPEN_WINDOW_TIME;		//WWD Open Window Time: WDCYC(0.1ms or 1ms)* wd cycles, Factor: 50, Offset: 50, 0wd cycles = 50, 1wd cycles = 100

	vTLF35584_Panels.write_reg.TLF35584_DEVCFG0_0x00.signal.TRDEL		= 15;			//Transition delay into low power(Stand-by,sleep) states: 0=100us, 1=200us, 2=300us ........ 15=1600us
	vTLF35584_Panels.write_reg.TLF35584_DEVCFG0_0x00.signal.WKTIMCYC	= 1;			//Wake timer cycle period: 0=10us, 1=10ms
	vTLF35584_Panels.write_reg.TLF35584_DEVCFG0_0x00.signal.WKTIMEN		= PMIC_DISABLE;	//Wake timer enable: 0=Disabled 1=Enable

	vTLF35584_Panels.write_reg.TLF35584_DEVCFG1_0x01.signal.RESDEL		= 6;			//Reset release delay time: 0=200us 1=400us 2=800us 3=1ms 4=2ms 5=4ms 6=10ms 7=15ms

	vTLF35584_Panels.write_reg.TLF35584_DEVCFG2_0x02.signal.ESYNEN		= PMIC_DISABLE;	//Synchronization output for external switchmode regulator enable: 0=Disabled 1=Enable
	vTLF35584_Panels.write_reg.TLF35584_DEVCFG2_0x02.signal.ESYNPHA		= 0;			//External synchronization output phase: 0=No phase shift, 1=180 phase shift
	vTLF35584_Panels.write_reg.TLF35584_DEVCFG2_0x02.signal.CTHR		= 3;			//(On Sleep Mode Current Threshold) QUC current monitoring threshold value: 0=10mA 1=30mA 2=60mA 3=100mA
	vTLF35584_Panels.write_reg.TLF35584_DEVCFG2_0x02.signal.CMONEN		= PMIC_DISABLE;	//(On Standby Mode Current Monitor Enable)QUC current monitor enable for transition to a low power state: 0=Disabled 1=Enable

	TLF35584_UnlockProtectedRegister();
	/* Set System configuration */
	TLF35584_Spi_Write_SYSPCFG0_0x04();	 	//disable LDO_Stby
	TLF35584_Spi_Write_SYSPCFG1_0x05(); 	//ERR Pin & SS2 delay Set, Protected System configuration request 1

	/* Set Watchdog configuration */
	TLF35584_Spi_Write_WDCFG0_0x06();		//Protected Watchdog configuration request 0
	TLF35584_Spi_Write_WDCFG1_0x07();		//Protected Watchdog configuration request 1
	TLF35584_Spi_Write_FWDCFG_0x08();		//Protected Functional watchdog configuration request
	TLF35584_Spi_Write_WWDCFG0_0x09();		//Protected Window watchdog configuration request 0
	TLF35584_Spi_Write_WWDCFG1_0x0A();		//Protected Window watchdog configuration request 1
	TLF35584_LockProtectedRegister();

	//Init Register
	TLF35584_Spi_Write_DEVCFG0_0x00();
	TLF35584_Spi_Write_DEVCFG1_0x01();
	TLF35584_Spi_Write_DEVCFG2_0x02();
} /*End of TLF35584_ConfigureRegisters()*/


//************************************************************************************************************
// @Function	 	void TLF35584_Init(void)
//************************************************************************************************************
void TLF35584_Init(void)
{
	TLF35584_ConfigureSpi();			//Init_SPI
	TLF35584_InitializeData();			//InitializeData
	TLF35584_ConfigureRegisters();		//Init_Setup
	TLF35584_ClearInitErrors();			//INIT_Clear_Flags
	//	TLF35584_ResetErrors();
}

//************************************************************************************************************
// @Function	 	void TLF35584_Task_1ms(void)
//************************************************************************************************************
void TLF35584_Task_1ms(void)
{	/* Required_WWD_Cycle_Below10ms_Enable */
#if (WATCHDOG_CYCLE_TIME == 0) & (WINDOW_WATCHDOG_ENABLE == 1)
	TLF35584_ManageWWD(); //Window Watchdogs
#endif
	TLF35584_UpdatePins();
	TLF35584_DebugErrorResetCheck();
}

//************************************************************************************************************
// @Function	 	void TLF35584_Task_10ms(void)
//************************************************************************************************************
void TLF35584_Task_10ms_7(void)
{	/* Required_WWD_Cycle_Below100ms_Enable */
#if (WATCHDOG_CYCLE_TIME == 1) & (WINDOW_WATCHDOG_ENABLE == 1)
	TLF35584_ManageWWD();							//Window Watchdogs Process
#endif
#if FUNCTION_WATCHDOG_ENABLE == 1
	TLF35584_ManageFWD(); 						//Functional Watchdogs Process
#endif
}
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////// NOT_USED //////////////////////////////////////////////////////
//************************************************************************************************************
// @Function	 	void TLF35584_Task_100ms(void)
//************************************************************************************************************
void TLF35584_Task_100ms(void)
{
	//	TLF35584_GetWatchdogStatus(); 				//Read Watchdog Status
	//	TLF35584_Spi_Read_DEVSTAT_0x27(); 			//Read Current State
	TLF35584_HandleState();
	TLF35584_UpdatePins();
	TLF35584_DebugErrorResetCheck();

	//	TLF35584_ReadRegisters();
	//	TLF35584_WriteRegisters();

	/* If the error_clear flag is TRUE, clear errors through software */
	if(vTLF35584_Panels.error_control.error_clear == TRUE)
	{
		TLF35584_ResetErrors();  /* Clear all register flags */
		/* Reset internal flags as well */
		vTLF35584_Panels.error_control.error_flag = FALSE;
		vTLF35584_Panels.error_control.error_type = TLF35584_NO_ERROR;
		vTLF35584_Panels.error_control.error_clear = FALSE;
	}
	else{

	}
}

//************************************************************************************************************
// @Function	 	void TLF35584_Task_1000ms(void)
//************************************************************************************************************
void TLF35584_Task_1000ms(void)
{
	// do nothing
}

void TLF35584_Test_10ms(void)
{
	switch(vTLF35584_Panels.test_config.test_case)
	{
	case 0 :
		//do nothing
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	case 1:
		TLF35584_ServiceWWD();
		TLF35584_ServiceWWD();
		TLF35584_ServiceWWD();
		TLF35584_ServiceWWD();
		TLF35584_ServiceWWD();
		TLF35584_ServiceWWD();
		TLF35584_ServiceWWD();
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	case 2:
		Dio_WriteChannel(EHAL_DIO_PMIC_WDI, ~vTLF35584_Panels.read_pins.WDI);
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	case 3:
		Dio_WriteChannel(EHAL_DIO_PMIC_WDI, 1);
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	case 4:
		Dio_WriteChannel(EHAL_DIO_PMIC_WDI, 0);
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	case 5:
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	case 6:
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	case 7:
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	case 8:
		//Mcu_SetMode(McuConf_McuModeSettingConf_McuModeSettingConf_2);// MCU Standby Mode
		//Mcu_SetMode(McuConf_McuModeSettingConf_McuModeSettingConf_1);// MCU Sleep Mode
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	case 9:
		TLF35584_Spi_Write_ABIST_CTRL0_0x2C();
		TLF35584_Spi_Write_ABIST_CTRL1_0x2D();
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	case 10:
		TLF35584_Spi_Write_ABIST_SELECT0_0x2E();
		TLF35584_Spi_Write_ABIST_SELECT1_0x2F();
		TLF35584_Spi_Write_ABIST_SELECT2_0x30();
		vTLF35584_Panels.test_config.test_case = 0;
		break;
	default:
		break;
	}
}
