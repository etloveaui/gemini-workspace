/*
 * EhalGpt12.c
 *
 *  Created on: 2024. 11. 19.
 *      Author: eunta
 */

#include "EhalGpt12.h"
#include "EHAL/EhalAdc/EhalAdc.h"
#include "BswGpt.h"

typEhalGpt12_ReadRegister vEhalGpt12_ReadRegister;
typEhalGpt12_ReadValue vEhalGpt12_ReadData;

void EhalGpt12_T4_InterruptHandler(void)
{
	vEhalGpt12_ReadData.noti_count++;
	vEhalGpt12_ReadData.enc_i_pulse = TRUE;
	ShrHWIA_BswGpt_GetEnc_I_ISR(BSWGPT_ENC_CH_SENS1);
	SRC_GPT120T4.B.CLRR = 1U;
}

// Encoder 1 Initialization Function
void EhalGpt12_InitEncoder(uint8 CLRT3EN)
{
    // Configure T3
    GPT120_T3CON.B.T3I      = 3U;    // Timer T3 Input Parameter Selection - 3U (Any transition on any Tx input - TxIN or TxEUD)
    GPT120_T3CON.B.T3M      = 7U;    // Timer T3 Mode Control - 111B (Incremental Interface Mode - Edge Detection Mode)
//    GPT120_T3CON.B.T3R      = 0U;    // Timer T3 Run Bit - 1 (Timer T3 runs)
    GPT120_T3CON.B.T3UD     = 0U;    // Timer T3 Up/Down Control - 0 (Counts Up)
    GPT120_T3CON.B.T3UDE    = 1U;    // Timer T3 External Up/Down Enable - 1 (Controlled by T3EUD)
    GPT120_T3CON.B.T3OE     = 0U;    // Timer T3 Overflow/Underflow Output Enable - 0 (Disabled)
    GPT120_T3CON.B.T3OTL    = 0U;    // Timer T3 Overflow Toggle Latch - 0 (Not toggled)
    GPT120_T3CON.B.BPS1     = 0U;    // GPT1 Block Prescaler Control - 00B (Prescaler value)
    GPT120_T3CON.B.T3EDGE   = 0U;    // Timer T3 Edge Detection Flag - 0 (No edge detected)
    GPT120_T3CON.B.T3CHDIR  = 0U;    // Timer T3 Count Direction Change Flag - 0 (No change)
    GPT120_T3CON.B.T3RDIR   = 0U;    // Timer T3 Rotation Direction Flag - 0 (Counts Up)

    // Configure T4
    GPT120_T4CON.B.T4I      = 1U;    // Timer T4 Input Parameter Selection
    GPT120_T4CON.B.T4M      = 5U;    // Timer T4 Mode Control - 101B (Capture Mode)
//    GPT120_T4CON.B.T4R      = 0U;    // Timer T4 Run Bit - 1 (Timer T4 runs)
    GPT120_T4CON.B.T4UD     = 0U;    // Timer T4 Up/Down Control - 0 (Counts Up)
    GPT120_T4CON.B.T4UDE    = 0U;    // Timer T4 External Up/Down Disable - 0
    GPT120_T4CON.B.T4RC     = 0U;    // Timer T4 Remote Control - 0 (Controlled by T4R)
    GPT120_T4CON.B.CLRT2EN  = 0U;    // Clear Timer T2 Enable - 0 (Disabled)
    GPT120_T4CON.B.CLRT3EN  = CLRT3EN;    // Clear Timer T3 Enable - 1 (Enable)
    GPT120_T4CON.B.T4IRDIS  = 0U;    // Timer T4 Interrupt Disable - 0 (Enabled)
    GPT120_T4CON.B.T4EDGE   = 0U;    // Timer T4 Edge Detection Flag - 0 (No edge detected)
    GPT120_T4CON.B.T4CHDIR  = 0U;    // Timer T4 Count Direction Change Flag - 0 (No change)
    GPT120_T4CON.B.T4RDIR   = 0U;    // Timer T4 Rotation Direction Flag - 0 (Counts Up)

    // Initialize and start Encoder 1 timers
    Encoder_ClearTimer3();
    Encoder_ClearTimer4();
    Encoder_StartTimer3();
    Encoder_StartTimer4();

    vEhalGpt12_ReadData.encvalue = 0U;
    vEhalGpt12_ReadData.enccnt = 0U;
    vEhalGpt12_ReadData.encdir = 0U;
    vEhalGpt12_ReadData.enc_i_pulse = FALSE;
}

void EhalGpt12_Init(void)
{
	volatile uint32 dummy;

    // Retrieve Safety Watchdog Password
//    unsigned short safetyPw = Ifx_Ssw_getSafetyWatchdogPassword();
    uint16 passwd = Ifx_Ssw_getCpuWatchdogPasswordInline(&MODULE_SCU.WDTCPU[0]);

    // Clear ENDINIT bit
//    Ifx_Ssw_clearSafetyEndinit(safetyPw);
    Ifx_Ssw_clearCpuEndinitInline(&MODULE_SCU.WDTCPU[0], passwd);

	GPT120_CLC.U = 0;		// Clock Control Register: Turn on GPT120 module.
	dummy = GPT120_CLC.U ;

    // Set ENDINIT bit
//    Ifx_Ssw_setSafetyEndinit(safetyPw);
    Ifx_Ssw_setCpuEndinitInline(&MODULE_SCU.WDTCPU[0], passwd);

    // ---------------------------------------------------------
    // Configure PISEL(Port Input Select) Register for Encoders
    // ---------------------------------------------------------

    // Encoder1: T3 (Phase A/B) and T4 (Index)
    GPT120_PISEL.B.IST3IN  = T3INA_SELECTED;		// Select T3INA (P02.6)	Input Select for T3IN - IST3IN (rw)
    GPT120_PISEL.B.IST3EUD = T3EUDA_SELECTED;		// Select T3EUDA (P02.6)	Input Select for T3EUD - IST3EUD (rw)
    GPT120_PISEL.B.IST4IN  = T4INA_SELECTED;    	// Select T4INA (P02.8)	Input Select for T4IN - IST4IN (rw)

    // Unused Pins
    GPT120_PISEL.B.IST2IN	= NOT_USED;          	//NOT USED, Input Select for T2IN - IST2IN (rw)
	GPT120_PISEL.B.IST2EUD	= NOT_USED;         	//NOT USED, Input Select for T2EUD - IST2EUD (rw)
    GPT120_PISEL.B.IST4EUD	= NOT_USED;    			//NOT USED, Input Select for T4EUD - IST4EUD (rw)
    GPT120_PISEL.B.IST6EUD  = NOT_USED;   			//NOT USED, Input Select for T6EUD - IST6EUD (rw)
    GPT120_PISEL.B.ISCAPIN	= NOT_USED;   			//NOT USED, Input Select for CAPIN - ISCAPIN (rw)
    GPT120_PISEL.B.IST5IN   = NOT_USED;   			//NOT USED, Input Select for T5IN - IST5IN (rw)
    GPT120_PISEL.B.IST5EUD  = NOT_USED;   			//NOT USED, Input Select for T5EUD - IST5EUD (rw)
    GPT120_PISEL.B.IST6IN   = NOT_USED;   			//NOT USED, Input Select for T6IN - IST6IN (rw)

    // Initialize Encoders
    EhalGpt12_InitEncoder(0); // Clear Timer T3 Enable - 0 (Disable)
} /* Gpt12_Initialization */

void EhalGpt12_ReadRegister()
{
	vEhalGpt12_ReadRegister.clc.U =	GPT120_CLC.U;
	vEhalGpt12_ReadRegister.pisel.U  = GPT120_PISEL.U;
	vEhalGpt12_ReadRegister.t3con.U  = GPT120_T3CON.U;
	vEhalGpt12_ReadRegister.t4con.U  = GPT120_T4CON.U;
//	vEhalGpt12_ReadRegister.t5con.U  = GPT120_T5CON.U;
//	vEhalGpt12_ReadRegister.t6con.U  = GPT120_T6CON.U;
	vEhalGpt12_ReadRegister.srcr.U  = SRC_GPT120T4.U;

}

void EhalGpt12_Test_10ms(void)
{
	vEhalGpt12_ReadData.encvalue = Encoder_ReadTimer3();
	vEhalGpt12_ReadData.encdir = Encoder_GetCountDirection3();
//	vEhalGpt12_ReadData.enc_i_pulse = vEhalGpt12_EncoderData.Z_Pulse;
	if((vEhalGpt12_ReadData.encdir == 1)&&(vEhalGpt12_ReadData.enccnt<ENCODER_COUNT_LIMIT)){
		vEhalGpt12_ReadData.enccnt++;
	}
	else{
		vEhalGpt12_ReadData.enccnt=0;
	}

	if(vEhalGpt12_ReadData.enc_i_pulse == TRUE){
		if(SRC_GPT120T4.B.CLRR == 0){
			vEhalGpt12_ReadData.enc_i_pulse = FALSE;
			vEhalGpt12_ReadData.clear_count++;
		}
	}
	else{

	}

	EhalGpt12_ReadRegister();
}
