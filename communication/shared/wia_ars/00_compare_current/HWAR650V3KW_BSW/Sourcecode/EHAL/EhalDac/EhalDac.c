/*
 * EhalDac.c
 *
 *  Created on: 2022. 9. 22.
 *      Author: dell
 */

#include "EHAL/EhalDac/EhalDac.h"
#include "Spi.h"
#include "EHAL/EhalAdc/EhalAdc.h"
#include "Global_Config.h"

typEhalDac_Buffer vEhalDac_TxBuf;
typEhalDac_Buffer vEhalDac_RxBuf;

uint32 vEhalDac_job_count;
uint32 vEhalDac_seq_count;
uint8 vEhalDac_DacModule = DAC8803;
/*******************************************************************************
**                      Private Variable Declarations                         **
*******************************************************************************/

/*******************************************************************************
**                      Private Function Declarations                           **
*******************************************************************************/

/*******************************************************************************
**                      Global Function Definitions                           **
*******************************************************************************/
void SpiSeq_2_EndNotification(void){
	vEhalDac_seq_count++;
}


void SpiJob_2_EndNotification(void){
	vEhalDac_job_count++;
}

void EhalDac_ConfigureSpi(void)
{
	Std_ReturnType spi_return;

	spi_return = Spi_SetupEB(SpiConf_SpiChannel_SpiChannel_2,
							 (Spi_DataBufferType*) &vEhalDac_TxBuf.halfword,
							 (Spi_DataBufferType*) &vEhalDac_RxBuf.halfword,
							 1U);
}

void EhalDac_SpiAsyncTransmit(uint8 ch, uint16 txdata)
{
//    Spi_SeqResultType spi_seq_result;
//    uint32 spi_try_count = 0;

    if(vEhalDac_DacModule == DAC8803){
    	// Construct data specifically for DAC8803
    	// A1 (bit 15) and A0 (bit 14) for channel selection, D13-D0 for data
    	vEhalDac_TxBuf.halfword = ((ch & 0x3) << 14) | (txdata & 0x3FFF);
    }
    else{
    	vEhalDac_TxBuf.halfword = ((ch&0x3)<<14) | ((TLV5614_SPD&0x1)<<13) | ((TLV5614_PWR&0x1)<<12) | (txdata&0xFFF);
    }

    Spi_AsyncTransmit(SpiConf_SpiSequence_SpiSequence_2);

//    // Start SPI async transmission
//    if (Spi_AsyncTransmit(SpiConf_SpiSequence_SpiSequence_2) != E_OK) {
//        return;
//    }
//
//    // Wait for the sequence to complete or timeout
//    while (spi_try_count < EHALDAC_SPI_TIMEOUT_CNT) {
//        spi_seq_result = Spi_GetSequenceResult(SpiConf_SpiSequence_SpiSequence_2);
//        if (spi_seq_result == SPI_SEQ_OK) {
//            return; // Success
//        }
//        spi_try_count++;
//    }
}

void EhalDac_Init(void)
{
    // Reset job and sequence counters
    vEhalDac_job_count = 0;
    vEhalDac_seq_count = 0;

    // Optionally, initialize other hardware or DAC-specific settings
    if(vEhalDac_DacModule == DAC8803){
    	// Additional DAC8803-specific initialization (if needed)
    }
    else{
    	// Additional TLV5614-specific initialization (if needed)
    }


    // Configure SPI for DAC communication
    EhalDac_ConfigureSpi();
}

inline void Qspi2_DAC_Communication(uint8 gucch, float gfdacData, float gfdacMax, float gfdacMin)
{
	uint16 txData = 0;

	if(vEhalDac_DacModule == DAC8803){
		txData = (uint16)((sint16)(((gfdacData - gfdacMin) / (gfdacMax - gfdacMin)) * 0x3FFF));
	}
	else{
		txData = (uint16)((sint16)(((gfdacData - gfdacMin) / (gfdacMax - gfdacMin)) * 0xFFF));
	}

	EhalDac_SpiAsyncTransmit(gucch,txData);

//	if(gucch == 0)			EhalDac_SpiAsyncTransmit(DAC_CHANNEL_A,txData);
//	else if(gucch == 1)		EhalDac_SpiAsyncTransmit(DAC_CHANNEL_B,txData);
//	else if(gucch == 2)		EhalDac_SpiAsyncTransmit(DAC_CHANNEL_C,txData);
//	else if(gucch == 3)		EhalDac_SpiAsyncTransmit(DAC_CHANNEL_D,txData);
//	else{}
}
